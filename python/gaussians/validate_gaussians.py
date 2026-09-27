"""Validate actual Gaussian notebook functions without plotting or training.

Run with the notebook's numpy environment. --trajectories additionally checks
all published Gaussian runs at their configured step size and horizon.
The default checks also compare the modal covariance equation with a full
matrix LMO and test Gaussian entropy dissipation through affine transports.
"""

import argparse
import ast
import json
from pathlib import Path

import numpy as np


def load_functions(path):
    notebook = json.loads(path.read_text())
    names = {"TARGET", "initial_points", "p_values", "beta_list", "r_init_2d", "s_init_2d"}
    statements = []
    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        for node in ast.parse("".join(cell["source"])).body:
            if isinstance(node, ast.FunctionDef):
                statements.append(node)
            elif isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id in names for target in node.targets
            ):
                statements.append(node)
    scope = {"np": np}
    exec(compile(ast.Module(body=statements, type_ignores=[]), str(path), "exec"), scope)
    return scope


def analytical_rs(a, b, p, beta):
    q = 1.0 if np.isinf(p) else 2.0 * p / (2.0 * p - 1.0)
    error = (a - b) / 2 - beta
    N = np.linalg.norm(np.concatenate((np.abs(error) * np.sqrt(a),
                                       np.abs(error) * np.sqrt(b))), ord=q)
    if N == 0:
        return np.zeros_like(a), np.zeros_like(b)
    psi = np.zeros_like(error)
    active = error != 0
    psi[active] = error[active] * np.abs(error[active]) ** (q - 2)
    rate = -(N ** (2 - q)) * psi
    return rate * (a ** (q / 2) + b ** (q / 2)), rate * (a ** (q / 2) - b ** (q / 2))


def check_identities(ns):
    worst_rhs = worst_leaf = worst_derivative = 0.0
    for p in ns["p_values"]:
        for a, b, beta in [
            (np.array([0.1, 10.0]), np.array([0.1, 10.0]), np.array([-1.25, -0.65])),
            (np.array([0.7, 2.4]), np.array([1.6, 0.8]), np.array([0.3, -0.2])),
            (np.array([0.7, 2.4]), np.array([1.6, 0.8]), np.array([-0.45, 0.8])),
            (np.array([0.0, 2.4]), np.array([1.6, 0.0]), np.array([0.3, -0.2])),
        ]:
            da, db = ns["rhs_ab_2d"](a, b, p, beta)
            expected = analytical_rs(a, b, p, beta)
            actual = ((da - db) / 2, (da + db) / 2)
            np.testing.assert_allclose(actual, expected, rtol=2e-14, atol=2e-14)
            worst_rhs = max(worst_rhs, float(np.max(np.abs(np.array(actual) - expected))))
            assert np.all(da[a == 0] == 0) and np.all(db[b == 0] == 0)
            for ai, bi, target in zip(a, b, beta):
                one = ns["rhs_ab_1d"](ai, bi, p, target)
                two = ns["rhs_ab_2d"](np.array([ai]), np.array([bi]), p, np.array([target]))
                np.testing.assert_allclose(one, np.array(two).ravel(), rtol=2e-14, atol=2e-14)
            if np.all(a > 0) and np.all(b > 0):
                if p == 1:
                    derivative = b * da + a * db
                else:
                    exponent = 0.5 if np.isinf(p) else (p - 1) / (2 * p - 1)
                    derivative = exponent * (a ** (exponent - 1) * da + b ** (exponent - 1) * db)
                worst_derivative = max(worst_derivative, float(np.max(np.abs(derivative))))
                np.testing.assert_allclose(derivative, 0, atol=2e-13)
        stationary = ns["rhs_ab_2d"](np.ones(2), np.ones(2), p, np.zeros(2))
        np.testing.assert_array_equal(stationary, np.zeros((2, 2)))
        level = ns["invariant_level"](0.2, 1.5, p)
        for r in [-0.8, -0.2, 0.0, 0.4, 0.8]:
            s = ns["solve_s_on_invariant"](r, level, p)
            assert np.isfinite(s) and s > abs(r)
            residual = abs(ns["invariant_level"](r, s, p) - level)
            worst_leaf = max(worst_leaf, residual)
            assert residual < 2e-13
        if p != 1:
            assert np.isnan(ns["solve_s_on_invariant"](10, ns["invariant_level"](0, 0.1, p), p))
    return {"max_rhs_absolute_error": worst_rhs, "max_leaf_residual": worst_leaf,
            "max_invariant_time_derivative": worst_derivative}


def trajectory_checks(ns, published):
    results = []
    options = {} if published else {"T": 0.02, "dt": 2e-4}
    for p in ns["p_values"]:
        cases = [(f"one-mode-{i}", ns["integrate_flow_1d"](*point, p, **options))
                 for i, point in enumerate(ns["initial_points"])]
        cases += [(f"two-mode-{i}", ns["integrate_flow_2d"](beta, p, **options))
                  for i, beta in enumerate(ns["beta_list"])]
        for name, (r, s) in cases:
            r, s = np.asarray(r).reshape(len(r), -1), np.asarray(s).reshape(len(s), -1)
            assert np.isfinite(r).all() and np.isfinite(s).all()
            assert np.min(s - np.abs(r)) >= -1e-14
            drift = 0.0
            for mode in range(r.shape[1]):
                # Only test the initial connected interior segment, before rank loss.
                boundary = np.flatnonzero(s[:, mode] - np.abs(r[:, mode]) <= 1e-3)
                stop = int(boundary[0]) if len(boundary) else len(r)
                levels = ns["invariant_level"](r[:stop, mode], s[:stop, mode], p)
                relative = np.max(np.abs(levels - levels[0])) / max(1.0, abs(levels[0]))
                drift = max(drift, float(relative))
            assert drift < (2e-5 if published else 1e-9), (name, p, drift)
            results.append({"case": name, "p": "inf" if np.isinf(p) else p,
                            "max_relative_interior_leaf_drift": drift, "final_r": r[-1].tolist()})
    return results


def check_matrix_covariance(ns):
    worst_rhs = worst_action = 0.0
    identity = np.eye(2)
    basis = np.block([[identity, identity], [identity, -identity]]) / np.sqrt(2)
    cases = [
        (np.array([0.7, 2.4]), np.array([1.6, 0.8])),
        (np.array([0.0, 2.4]), np.array([1.6, 0.0])),
        (np.zeros(2), np.zeros(2)),
    ]
    for p in ns["p_values"]:
        q = 1.0 if np.isinf(p) else 2 * p / (2 * p - 1)
        for a, b in cases:
            error = (a - b) / 2 - np.array([0.3, -0.2])
            root = basis @ np.diag(np.sqrt(np.concatenate((a, b)))) @ basis.T
            force = basis @ np.diag(np.concatenate((error, -error))) @ basis.T
            k = force @ root
            u, singular, vt = np.linalg.svd(k)
            # Compact SVD: remove roundoff in the exactly null singular subspaces.
            active = singular > 1e-13 * max(1.0, singular[0])
            norm = np.linalg.norm(singular[active], ord=q)
            if norm == 0:
                velocity = np.zeros_like(k)
            else:
                velocity = -(norm ** (2 - q)) * (
                    (u[:, active] * singular[active] ** (q - 1)) @ vt[active]
                )
            covariance_rhs = velocity @ root + root @ velocity.T
            da, db = ns["rhs_ab_2d"](a, b, p, np.array([0.3, -0.2]))
            expected = basis @ np.diag(np.concatenate((da, db))) @ basis.T
            np.testing.assert_allclose(covariance_rhs, expected, atol=2e-13, rtol=2e-13)
            action = np.linalg.norm(np.linalg.svd(velocity, compute_uv=False), ord=2 * p) ** 2
            dissipation = -np.sum(k * velocity)
            np.testing.assert_allclose([action, dissipation], norm ** 2, atol=2e-13, rtol=2e-13)
            worst_rhs = max(worst_rhs, float(np.max(np.abs(covariance_rhs - expected))))
            worst_action = max(worst_action, abs(action - norm ** 2), abs(dissipation - norm ** 2))
    return {"max_covariance_rhs_error": worst_rhs, "max_action_identity_error": worst_action}


def check_gaussian_entropy():
    rng = np.random.default_rng(8)
    raw = rng.normal(size=(3, 3))
    covariance = raw @ raw.T + np.eye(3)
    raw = rng.normal(size=(3, 3))
    target = raw @ raw.T + 2 * np.eye(3)
    mean = np.array([0.2, -0.4, 0.7])
    precision = np.linalg.inv(target)
    hessian = precision - np.linalg.inv(covariance)
    offset = precision @ mean
    force_covariance = hessian @ covariance @ hessian + np.outer(offset, offset)
    eigenvalues, eigenvectors = np.linalg.eigh(force_covariance)
    eig_cov, vec_cov = np.linalg.eigh(covariance)
    root = (vec_cov * np.sqrt(eig_cov)) @ vec_cov.T

    def entropy(m, s):
        return 0.5 * (np.trace(precision @ s) + m @ precision @ m - 3
                      + np.linalg.slogdet(target)[1] - np.linalg.slogdet(s)[1])

    worst_action = worst_derivative = 0.0
    for p in (0.5, 0.75, 1.0, 2.0, np.inf):
        if p == 0.5:
            multiplier = np.outer(eigenvectors[:, -1], eigenvectors[:, -1])
            expected = eigenvalues[-1]
        else:
            q = 1.0 if np.isinf(p) else 2 * p / (2 * p - 1)
            norm = np.linalg.norm(np.sqrt(eigenvalues), ord=q)
            multiplier = (norm ** (2 - q)) * (
                (eigenvectors * eigenvalues ** (q / 2 - 1)) @ eigenvectors.T
            )
            expected = norm ** 2
        velocity_operator = -multiplier @ np.column_stack((hessian @ root, offset))
        action = np.linalg.norm(np.linalg.svd(velocity_operator, compute_uv=False), ord=2 * p) ** 2
        np.testing.assert_allclose(action, expected, atol=2e-12, rtol=2e-12)
        step = 1e-6 / max(1.0, np.linalg.norm(multiplier @ hessian, ord=2))
        energies = []
        for sign in (1, -1):
            transport = np.eye(3) - sign * step * multiplier @ hessian
            energies.append(entropy(mean - sign * step * multiplier @ offset,
                                    transport @ covariance @ transport.T))
        derivative = (energies[0] - energies[1]) / (2 * step)
        np.testing.assert_allclose(derivative, -expected, atol=2e-7, rtol=2e-7)
        worst_action = max(worst_action, abs(action - expected))
        worst_derivative = max(worst_derivative, abs(derivative + expected))
    return {"max_action_identity_error": worst_action,
            "max_entropy_derivative_error": worst_derivative}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notebook", type=Path, default=Path(__file__).with_name("gaussian_closed_form.ipynb"))
    parser.add_argument("--trajectories", action="store_true")
    args = parser.parse_args()
    ns = load_functions(args.notebook)
    report = check_identities(ns)
    report["matrix_covariance_checks"] = check_matrix_covariance(ns)
    report["gaussian_entropy_checks"] = check_gaussian_entropy()
    report["published_horizon"] = args.trajectories
    report["integration_parameters"] = {
        "one_mode_T_dt": list(ns["integrate_flow_1d"].__defaults__) if args.trajectories else [0.02, 2e-4],
        "two_mode_T_dt": list(ns["integrate_flow_2d"].__defaults__) if args.trajectories else [0.02, 2e-4],
        "interior_eigenvalue_threshold": 1e-3,
    }
    report["trajectories"] = trajectory_checks(ns, args.trajectories)
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
