"""Small reproducible experiments for the lecture, independent of paper outputs."""

import json
from pathlib import Path
import sys

import cvxpy as cp
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import linear_sum_assignment

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from muon_dynamics import mmd_force, particle_lmo, schatten_lmo, solve_transport  # noqa: E402
from generate_experiment import mean_distance  # noqa: E402

P = (1, 1.5, 2, 4, np.inf)
LABELS = ("1", "1.5", "2", "4", "inf")


def array(value):
    return np.asarray(value).round(9).tolist()


def flows():
    original = json.loads((ROOT / "slides/public/data/measures.json").read_text())
    target = np.array(original["targetSamples"]).reshape(-1, 2)[::2]
    initial = np.array(original["experiments"][-1]["frames"][0]).reshape(-1, 2)
    eps, horizon, steps = .03, 8.0, 400
    constant = mean_distance(target, target, eps)
    output, fields = [], []
    for n in (16, 32, 64, 128):
        for p, label in zip(P, LABELS):
            x = initial[:n].copy()
            g0 = mmd_force(x, target, epsilon=eps)
            v0 = particle_lmo(g0, p)
            fields.append(dict(n=n, p=label, x=array(x), g=array(g0), v=array(v0),
                               forceMoment=array(g0.T @ g0 / n), velocityMoment=array(v0.T @ v0 / n)))
            frames, energies = [], []
            for k in range(steps + 1):
                if k % 4 == 0:
                    frames.append(array(x.ravel()))
                    energies.append(float(2 * mean_distance(x, target, eps) - mean_distance(x, x, eps) - constant))
                if k < steps:
                    x += horizon / steps * particle_lmo(mmd_force(x, target, epsilon=eps), p)
            if not np.isfinite(x).all() or max(np.diff(energies)) > 1e-7:
                raise RuntimeError(f"Non-descending slide experiment: n={n}, p={label}")
            output.append(dict(count=n, p=label, frames=frames, energies=array(energies)))
            print(f"MMD n={n}, p={label}: {energies[0]:.5f} -> {energies[-1]:.5f}", flush=True)
    return dict(horizon=horizon, epsilon=eps, dt=horizon / steps, targetCount=len(target),
                mixture=original["mixture"], experiments=output, fields=fields)


def dual_transport(x, y, p):
    n = len(x)
    delta = x[:, None] - y[None, :]
    u, v = cp.Variable(n), cp.Variable(n)
    q = cp.Variable((2, 2), symmetric=True)
    costs = sum(q[i, j] * (delta[:, :, i] * delta[:, :, j]) for i in range(2) for j in range(2))
    constraints = [q >> 0, cp.reshape(u, (n, 1), order="C") + cp.reshape(v, (1, n), order="C") <= costs]
    if p == 1:
        constraints += [q == np.eye(2)]
    elif p == 2:
        constraints += [cp.norm(q, "fro") <= 1]
    else:
        constraints += [cp.trace(q) <= 1]
    problem = cp.Problem(cp.Maximize((cp.sum(u) + cp.sum(v)) / n), constraints)
    problem.solve(solver="CLARABEL", tol_gap_abs=1e-8, tol_feas=1e-8)
    if problem.status != cp.OPTIMAL:
        raise RuntimeError(f"Transport dual: {problem.status}")
    return float(problem.value), q.value


def transport():
    rng = np.random.default_rng(35)
    sources = rng.normal(size=(16, 2)) * [.85, .48] + [-.6, 0]
    targets = rng.normal(size=(16, 2)) * [.5, .9]
    output = []
    for n in (8, 16):
        for angle in (0, 30, 60):
            theta = np.deg2rad(angle)
            rotation = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
            x, y = sources[:n], targets[:n] @ rotation.T + [.6, 0]
            for p, label in ((1, "1"), (2, "2"), (np.inf, "inf")):
                options = {} if p == 1 else dict(solver="CLARABEL", solver_options=dict(tol_gap_abs=1e-8, tol_feas=1e-8))
                result = solve_transport(x, y, p, **options)
                lower, q = dual_transport(x, y, p)
                gap = result.squared_cost - lower
                if abs(gap) > 2e-6 or result.marginal_error > 1e-7:
                    raise RuntimeError(f"Unresolved transport gap: {gap:g}")
                output.append(dict(n=n, p=label, angle=angle, x=array(x), y=array(y),
                                   plan=array(result.plan), moment=array(result.moment), Q=array(q),
                                   cost=result.squared_cost, dualCost=lower, gap=gap,
                                   marginalError=result.marginal_error))
    base = next(e for e in output if e["n"] == 16 and e["p"] == "inf" and e["angle"] == 30)
    x, y = np.array(base["x"]), np.array(base["y"])
    delta = x[:, None] - y[None, :]
    robust = []
    for w in np.linspace(0, 1, 21):
        for theta in np.linspace(0, np.pi, 73):
            r = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
            q = r @ np.diag([w, 1 - w]) @ r.T
            cost = np.einsum("ijk,kl,ijl->ij", delta, q, delta)
            rows, cols = linear_sum_assignment(cost)
            value = float(cost[rows, cols].mean())
            if value > base["cost"] + 1e-6:
                raise RuntimeError("Quadratic cost exceeds robust optimum")
            robust.append(dict(cost=value, assignment=cols.tolist()))
    print(f"Transport: {len(output)} convex solves, maximum gap {max(abs(e['gap']) for e in output):.2g}", flush=True)
    return dict(experiments=output, robust=robust)


def gaussian_network():
    output = []
    times = np.linspace(0, 4, 101)
    for variance in (.6, 1., 1.8):
        for p, label in zip(P, LABELS):
            def rhs(_t, flat):
                factor = flat.reshape(2, 2)
                covariance = factor @ factor.T
                e = covariance[0, 1] - 1
                force = np.array([[0., e], [e, 0.]])
                return schatten_lmo(force @ factor, p).ravel()
            solution = solve_ivp(rhs, (0, times[-1]), (np.eye(2) * np.sqrt(variance)).ravel(),
                                 t_eval=times, rtol=2e-9, atol=1e-11, max_step=.025)
            if not solution.success:
                raise RuntimeError(solution.message)
            factors = solution.y.T.reshape(-1, 2, 2)
            covariances = factors @ factors.transpose(0, 2, 1)
            losses = .5 * (covariances[:, 0, 1] - 1) ** 2
            if np.linalg.eigvalsh(covariances).min() <= 1e-5 or max(np.diff(losses)) > 1e-8:
                raise RuntimeError("Gaussian closure left the verified regime")
            output.append(dict(variance=variance, p=label, covariance=array(covariances), losses=array(losses)))
    print("Gaussian network: 15 positive-definite, descending trajectories", flush=True)
    return dict(horizon=4, experiments=output)


def blocks():
    output = []
    for scale in np.linspace(.25, 3, 12):
        g = np.array([[1, 0, .5 * scale, 0], [0, .25, 0, .8 * scale], [.3, .1, .2 * scale, .1 * scale]])
        parts = np.split(g, 2, axis=1)
        nuclear = [np.linalg.svd(a, compute_uv=False).sum() for a in parts]
        polar = []
        for a in parts:
            u, _, vh = np.linalg.svd(a, full_matrices=False)
            polar.append(u @ vh)
        velocities = dict(full=schatten_lmo(g, np.inf),
                          sum=np.concatenate([schatten_lmo(a, np.inf) for a in parts], axis=1),
                          max=np.concatenate([-sum(nuclear) * a for a in polar], axis=1))
        output.append(dict(scale=scale, force=[array(np.linalg.svd(a, compute_uv=False)) for a in parts],
                           velocity={mode: [array(np.linalg.svd(a, compute_uv=False)) for a in np.split(v, 2, axis=1)]
                                     for mode, v in velocities.items()}))
    return output


if __name__ == "__main__":
    result = dict(version=1, flow=flows(), transport=transport(), gaussian=gaussian_network(), blocks=blocks())
    path = ROOT / "slides/public/data/lecture.json"
    path.write_text(json.dumps(result, separators=(",", ":"), allow_nan=False) + "\n")
    print(f"Saved {path.name}: {path.stat().st_size:,} bytes", flush=True)
