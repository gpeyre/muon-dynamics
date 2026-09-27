"""Discrete static spectral transport, with full couplings rather than matchings."""

from dataclasses import dataclass

import numpy as np
from scipy import sparse
from scipy.optimize import linear_sum_assignment, linprog

from .spectral import _matrix, _weights, schatten_gauge


@dataclass(frozen=True)
class TransportResult:
    """Numerical optimum; solver status/residuals are not exact certificates."""

    plan: np.ndarray
    squared_cost: float
    moment: np.ndarray
    marginal_error: float
    status: str
    solver: str


def solve_transport(x, y, p=1, *, weights=None, target_weights=None,
                    solver=None, solver_options=None, feasibility_tolerance=1e-5):
    """Minimize gamma_p(sum_ij pi_ij (x_i-y_j)(x_i-y_j)^T).

    p=1: exact assignment for equal uniform clouds, otherwise a HiGHS LP.
    p=2 or inf: convex conic problem using the optional CVXPY dependency.
    Other p are deliberately unsupported; no heuristic substitution occurs.
    The returned cost is W_gamma**2. Conic solutions are only numerical,
    with status and marginal feasibility checks (not a certified dual gap).
    The full n*m coupling and pairwise displacements are stored in memory.
    """
    x, y = _matrix(x, "x"), _matrix(y, "y")
    if x.shape[1] != y.shape[1]:
        raise ValueError("point clouds must have the same dimension")
    if p not in (1, 2, np.inf):
        raise ValueError("static solver supports only p=1, p=2, and p=inf")
    if not np.isfinite(feasibility_tolerance) or feasibility_tolerance <= 0:
        raise ValueError("feasibility_tolerance must be positive and finite")
    a, b = _weights(weights, len(x)), _weights(target_weights, len(y))
    n, m, d = len(x), len(y), x.shape[1]
    delta = x[:, None, :] - y[None, :, :]
    cost = np.sum(delta**2, axis=-1)
    if p == 1:
        if solver is not None or solver_options:
            raise ValueError("solver options apply only to conic problems (p=2 or inf)")
        if n == m and np.all(a == 1 / n) and np.all(b == 1 / m):
            rows, cols = linear_sum_assignment(cost)
            plan = np.zeros((n, m))
            plan[rows, cols] = 1 / n
            name = "scipy.linear_sum_assignment"
        else:
            constraints = sparse.vstack([
                sparse.kron(sparse.eye(n), np.ones((1, m))),
                sparse.kron(np.ones((1, n)), sparse.eye(m)),
            ], format="csr")
            result = linprog(cost.ravel(), A_eq=constraints, b_eq=np.r_[a, b],
                             bounds=(0, None), method="highs")
            if not result.success:
                raise RuntimeError(f"Transport LP failed: {result.message}")
            plan = result.x.reshape(n, m)
            name = "scipy.highs"
        status = "optimal"
    else:
        try:
            import cvxpy as cp
        except ImportError as error:
            raise ImportError('Install muon-dynamics[transport] for p=2 or p=inf') from error
        coupling = cp.Variable((n, m), nonneg=True)
        moment = cp.bmat([
            [cp.sum(cp.multiply(delta[..., i] * delta[..., j], coupling))
             for j in range(d)] for i in range(d)
        ])
        objective = cp.norm(moment, "fro") if p == 2 else cp.lambda_max(moment)
        problem = cp.Problem(cp.Minimize(objective),
                             [cp.sum(coupling, axis=1) == a, cp.sum(coupling, axis=0) == b])
        problem.solve(solver=solver, **dict(solver_options or {}))
        if problem.status != cp.OPTIMAL or coupling.value is None:
            raise RuntimeError(f"Conic transport solve did not reach optimal status: {problem.status}")
        plan = np.asarray(coupling.value)
        status, name = problem.status, problem.solver_stats.solver_name
    residual = float(max(np.max(np.abs(plan.sum(axis=1) - a)),
                         np.max(np.abs(plan.sum(axis=0) - b))))
    if (not np.isfinite(plan).all() or plan.min() < -feasibility_tolerance
            or residual > feasibility_tolerance):
        raise RuntimeError(f"Transport solve failed feasibility checks (marginal error {residual:g})")
    moment = np.einsum("ij,ijk,ijl->kl", plan, delta, delta)
    return TransportResult(plan, schatten_gauge(moment, p), moment, residual, status, name)
