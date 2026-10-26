"""Small covariance and radial examples, with independent numerical checks."""

import json
from pathlib import Path

import cvxpy as cp
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import gamma

ROOT = Path(__file__).resolve().parents[2]


def array(x):
    return np.asarray(x).round(10).tolist()


def root(s):
    values, vectors = np.linalg.eigh(s)
    return (vectors * np.sqrt(np.maximum(values, 0))) @ vectors.T


def quadratic():
    times = np.linspace(0, 2, 201)
    experiments = []
    for condition in (1, 4, 16, 32):
        for p, label in ((1, "1"), (1.5, "1.5"), (2, "2"), (4, "4"), (np.inf, "inf")):
            if p == 1:
                factors = np.exp(-times[:, None] * np.array([1, condition]))
            elif np.isinf(p):
                factors = np.repeat(np.exp(-(1 + condition) * times[:, None]), 2, axis=1)
            else:
                q = 2 * p / (2 * p - 1)
                rates = np.array([1, condition**(q - 1)])

                def factors_at(tau):
                    return np.maximum(1 - rates * tau, 0)**(1 / (2 - q))

                def rhs(_time, tau):
                    singular = np.array([1, condition]) * factors_at(tau[0])
                    return [(2 - q) * np.linalg.norm(singular, q)**(2 - q)]

                solution = solve_ivp(rhs, (0, times[-1]), [0.], t_eval=times,
                                     rtol=1e-10, atol=1e-12, max_step=.005)
                if not solution.success:
                    raise RuntimeError(solution.message)
                factors = np.stack([factors_at(tau) for tau in solution.y[0]])
            energy = .5 * (factors[:, 0]**2 + condition * factors[:, 1]**2)
            if not np.isfinite(factors).all() or np.max(np.diff(energy)) > 1e-10:
                raise RuntimeError("Invalid quadratic flow")
            experiments.append(dict(condition=condition, p=label, factors=array(factors), energies=array(energy)))
    rng = np.random.default_rng(823)
    points = rng.normal(size=(256, 2))
    samples = []
    for n in (16, 64, 256):
        x = points[:n] - points[:n].mean(axis=0)
        x = x @ np.linalg.inv(root(x.T @ x / n))
        if not np.allclose(x.T @ x / n, np.eye(2), atol=1e-12):
            raise RuntimeError("Sample whitening failed")
        samples.append(dict(n=n, x=array(x)))
    return dict(horizon=2, times=array(times), experiments=experiments, samples=samples)


def gaussian_transport():
    a = np.diag([2.0**2, .55**2])
    rng = np.random.default_rng(245)
    normals = rng.normal(size=(96, 4))
    output = []
    for angle in range(0, 91, 15):
        theta = np.deg2rad(angle)
        r = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
        b = r @ np.diag([.7**2, 1.6**2]) @ r.T
        for p, label in ((1, "1"), (2, "2"), (np.inf, "inf")):
            k = cp.Variable((2, 2))
            joint = cp.bmat([[a, k], [k.T, b]])
            moment = a + b - k - k.T
            objective = cp.trace(moment) if p == 1 else cp.norm(moment, "fro") if p == 2 else cp.lambda_max(moment)
            problem = cp.Problem(cp.Minimize(objective), [joint >> 0])
            options = dict(solver="CLARABEL", tol_gap_abs=1e-8, tol_feas=1e-8, tol_gap_rel=1e-8)
            problem.solve(**options)
            if problem.status != cp.OPTIMAL:
                raise RuntimeError(f"Gaussian primal: {problem.status}")
            q = cp.Variable((2, 2), symmetric=True)
            constraints = [q >> 0]
            constraints += [q == np.eye(2)] if p == 1 else [cp.norm(q, "fro") <= 1] if p == 2 else [cp.trace(q) <= 1]
            lower = cp.Problem(cp.Maximize(cp.trace(q @ (a + b)) - 2 * cp.norm(root(a) @ q @ root(b), "nuc")), constraints)
            lower.solve(**options)
            if lower.status != cp.OPTIMAL:
                raise RuntimeError(f"Gaussian dual: {lower.status}")
            gap = float(problem.value - lower.value)
            block = np.block([[a, k.value], [k.value.T, b]])
            mineig = float(np.linalg.eigvalsh(block).min())
            if abs(gap) > 5e-7 or mineig < -1e-7:
                raise RuntimeError(f"Gaussian certificate: gap={gap}, min eigenvalue={mineig}")
            samples = normals @ root(block).T
            output.append(dict(angle=angle, p=label, source=array(a), target=array(b), cross=array(k.value),
                               samples=array(samples),
                               cost=float(problem.value), lower=float(lower.value), gap=gap,
                               minimumJointEigenvalue=mineig))
    print(f"Gaussian transport: {len(output)} SDP pairs; max gap {max(abs(e['gap']) for e in output):.2g}", flush=True)
    bound = max(np.abs(e["samples"]).max() for e in output) + .3
    return dict(experiments=output, bound=float(bound))


def radial():
    output = []
    radius = np.linspace(0, 5, 251)
    for q, label in ((1.25, "1.25"), (1.5, "1.5"), (2, "2"), (3, "3"), (4, "4"), (8, "8"), (np.inf, "inf")):
        raw = np.array([2 / (j + 2) if np.isinf(q) else gamma((j + 2) / q) / gamma(2 / q)
                        for j in (2, 4, 6)])
        scale = np.sqrt(2 / raw[0])
        moments = raw * scale**np.array([2, 4, 6])
        if np.isinf(q):
            density = np.where(radius <= scale, 1 / (np.pi * scale**2), 0)
        else:
            density = np.exp(-(radius / scale)**q) * q / (2 * np.pi * scale**2 * gamma(2 / q))
        output.append(dict(q=label, scale=float(scale), moments=array(moments), density=array(density)))
    return dict(radius=array(radius), experiments=output)


if __name__ == "__main__":
    result = dict(version=1, quadratic=quadratic(), gaussianTransport=gaussian_transport(), radial=radial())
    path = ROOT / "slides/public/data/extensions.json"
    path.write_text(json.dumps(result, separators=(",", ":"), allow_nan=False) + "\n")
    print(f"Saved {path.name}: {path.stat().st_size:,} bytes", flush=True)
