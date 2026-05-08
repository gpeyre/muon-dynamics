from pathlib import Path
from textwrap import dedent
import os
import random
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = ROOT / "python"
FIG_DIR = ROOT / "paper" / "figures"

os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="mplconfig_"))
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import matplotlib.pyplot as plt
import nbformat as nbf
import numpy as np
import torch
import cvxpy as cp
from scipy.optimize import linear_sum_assignment

torch.set_default_dtype(torch.float64)
SEED = 1234
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)


def sample_mmd_pair(num_points: int = 200):
    torch.manual_seed(SEED)
    y = sample_target(num_points)
    x = sample_source(num_points)
    return x, y


def sample_target(num_points: int) -> torch.Tensor:
    weights = torch.tensor([0.40, 0.35, 0.25], dtype=torch.float64)
    counts = (weights * num_points).long()
    counts[-1] = num_points - counts[:-1].sum()
    centers = torch.tensor(
        [[-3.4, -1.1], [-0.6, 3.0], [3.8, -2.5]],
        dtype=torch.float64,
    )
    scales = torch.tensor(
        [[0.55, 0.30], [0.35, 0.65], [0.45, 0.35]],
        dtype=torch.float64,
    )
    chunks = []
    for center, scale, count in zip(centers, scales, counts):
        z = torch.randn(int(count), 2, dtype=torch.float64)
        chunks.append(center + z * scale)
    y = torch.cat(chunks, dim=0)
    return y[torch.randperm(y.shape[0])]


def sample_source(num_points: int) -> torch.Tensor:
    z = torch.randn(num_points, 2, dtype=torch.float64)
    a = torch.tensor([[1.4, 0.8], [-0.3, 0.6]], dtype=torch.float64)
    x = z @ a.T
    x += torch.tensor([2.8, 2.4], dtype=torch.float64)
    return x

def sample_static_pair(num_points: int = 200):
    x, y = sample_mmd_pair(num_points)
    return x.numpy(), y.numpy()


def smooth_cdist(x: torch.Tensor, y: torch.Tensor, eps: float = 1e-2) -> torch.Tensor:
    diff = x[:, None, :] - y[None, :, :]
    return torch.sqrt((diff * diff).sum(dim=-1) + eps**2)


def mmd_energy_squared(x: torch.Tensor, y: torch.Tensor, eps: float = 1e-2) -> torch.Tensor:
    d_xx = smooth_cdist(x, x, eps)
    d_yy = smooth_cdist(y, y, eps)
    d_xy = smooth_cdist(x, y, eps)
    return 2.0 * d_xy.mean() - d_xx.mean() - d_yy.mean()


def schatten_direction(grad: torch.Tensor, p):
    if p == 1:
        return -grad
    u, s, vh = torch.linalg.svd(grad, full_matrices=False)
    if p == float("inf"):
        return -s.sum() * (u @ vh)
    r = 2.0 * p
    q = r / (r - 1.0)
    norm_q = (s.pow(q).sum()).pow(1.0 / q)
    if float(norm_q) < 1e-14:
        return torch.zeros_like(grad)
    weights = s.pow(q - 1.0)
    return -(norm_q.pow(2.0 - q)) * ((u * weights.unsqueeze(0)) @ vh)


def run_flow(x0: torch.Tensor, y: torch.Tensor, p, step_size: float, steps: int, eps: float):
    x = x0.clone().detach()
    history = [x.clone()]
    losses = []
    for _ in range(steps):
        x = x.detach().requires_grad_(True)
        loss = mmd_energy_squared(x, y, eps)
        loss.backward()
        grad = x.grad.detach()
        vel = schatten_direction(grad, p)
        with torch.no_grad():
            x = x + step_size * vel
        history.append(x.clone())
        losses.append(float(loss.detach()))
    return {"history": torch.stack(history), "losses": np.array(losses, dtype=float)}


def blended_color(step_id: int, total_steps: int):
    t = step_id / total_steps
    red = np.array([220, 20, 60], dtype=float) / 255.0
    blue = np.array([65, 105, 225], dtype=float) / 255.0
    return tuple((1.0 - t) * red + t * blue)


def cost_perm(x: np.ndarray, y: np.ndarray, perm: np.ndarray, p) -> float:
    d = y[perm] - x
    if p == 1:
        return float((d * d).sum() / len(x))
    s = np.linalg.svd(d, compute_uv=False, full_matrices=False)
    if p == np.inf:
        return float((s[0] ** 2) / len(x))
    return float((np.sum(s ** (2 * p)) ** (1.0 / p)) / len(x))


def local_swap_descent(x: np.ndarray, y: np.ndarray, perm0: np.ndarray, p, max_sweeps: int = 6):
    cur = perm0.copy()
    cur_cost = cost_perm(x, y, cur, p)
    n = len(cur)
    improved = True
    sweep = 0
    while improved and sweep < max_sweeps:
        improved = False
        sweep += 1
        for i in range(n - 1):
            for j in range(i + 1, n):
                test = cur.copy()
                test[i], test[j] = test[j], test[i]
                c = cost_perm(x, y, test, p)
                if c + 1e-12 < cur_cost:
                    cur = test
                    cur_cost = c
                    improved = True
    return cur, cur_cost


def solve_static_coupling_cvxpy(x: np.ndarray, y: np.ndarray, p, solver: str = "SCS"):
    n, m = len(x), len(y)
    a = np.full(n, 1.0 / n)
    b = np.full(m, 1.0 / m)
    dx = y[None, :, 0] - x[:, None, 0]
    dy = y[None, :, 1] - x[:, None, 1]
    a11 = dx * dx
    a12 = dx * dy
    a22 = dy * dy

    if p == 1:
        cost = a11 + a22
        rows, cols = linear_sum_assignment(cost)
        perm = np.empty(n, dtype=int)
        perm[rows] = cols
        P = np.zeros((n, m), dtype=float)
        P[np.arange(n), perm] = 1.0 / n
        return P, float(cost_perm(x, y, perm, 1))

    P = cp.Variable((n, m), nonneg=True)
    constraints = [cp.sum(P, axis=1) == a, cp.sum(P, axis=0) == b]
    s11 = cp.sum(cp.multiply(a11, P))
    s12 = cp.sum(cp.multiply(a12, P))
    s22 = cp.sum(cp.multiply(a22, P))
    S = cp.bmat([[s11, s12], [s12, s22]])

    if p == 2:
        objective = cp.Minimize(cp.norm(S, "fro"))
    elif p == np.inf:
        objective = cp.Minimize(cp.lambda_max(S))
    else:
        raise ValueError(f"unsupported p={p}")

    problem = cp.Problem(objective, constraints)
    kwargs = {"verbose": False}
    if solver == "SCS":
        kwargs.update({"eps": 1e-5, "max_iters": 12000})
    problem.solve(solver=solver, **kwargs)
    if P.value is None:
        raise RuntimeError(f"CVXPY failed for p={p} with status {problem.status}")
    return np.asarray(P.value, dtype=float), float(problem.value)


def extract_permutation_from_plan(P: np.ndarray) -> np.ndarray:
    rows, cols = linear_sum_assignment(-P)
    perm = np.empty(len(rows), dtype=int)
    perm[rows] = cols
    return perm


def md(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip() + "\n")


def code(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip() + "\n")


def notebook_preamble_cells():
    return [
        code(
            r"""
            import os
            import random
            import tempfile

            import numpy as np
            import torch
            import matplotlib.pyplot as plt

            os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
            os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="mplconfig_"))

            ip = get_ipython()
            if ip is not None:
                ip.run_line_magic("matplotlib", "inline")

            torch.set_default_dtype(torch.float64)
            SEED = 1234
            random.seed(SEED)
            np.random.seed(SEED)
            torch.manual_seed(SEED)

            plt.rcParams["figure.figsize"] = (7, 6)
            plt.rcParams["axes.grid"] = True
            plt.rcParams["grid.alpha"] = 0.2
            plt.rcParams["axes.spines.top"] = False
            plt.rcParams["axes.spines.right"] = False
            """
        ),
        code(
            r"""
            def sample_target(num_points: int) -> torch.Tensor:
                weights = torch.tensor([0.40, 0.35, 0.25], dtype=torch.float64)
                counts = (weights * num_points).long()
                counts[-1] = num_points - counts[:-1].sum()
                centers = torch.tensor([[-3.4, -1.1], [-0.6, 3.0], [3.8, -2.5]], dtype=torch.float64)
                scales = torch.tensor([[0.55, 0.30], [0.35, 0.65], [0.45, 0.35]], dtype=torch.float64)
                chunks = []
                for center, scale, count in zip(centers, scales, counts):
                    z = torch.randn(int(count), 2, dtype=torch.float64)
                    chunks.append(center + z * scale)
                Y = torch.cat(chunks, dim=0)
                return Y[torch.randperm(Y.shape[0])]

            def sample_source(num_points: int) -> torch.Tensor:
                z = torch.randn(num_points, 2, dtype=torch.float64)
                A = torch.tensor([[1.4, 0.8], [-0.3, 0.6]], dtype=torch.float64)
                X = z @ A.T
                X += torch.tensor([2.8, 2.4], dtype=torch.float64)
                return X

            def sample_mmd_pair(num_points: int = 200):
                torch.manual_seed(SEED)
                Y = sample_target(num_points)
                X = sample_source(num_points)
                return X, Y

            def sample_static_pair(num_points: int = 200):
                X, Y = sample_mmd_pair(num_points)
                return X.numpy(), Y.numpy()
            """
        ),
    ]


def build_mmd_notebook():
    nb = nbf.v4.new_notebook()
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
    }
    cells = [
        md(
            r"""
            # MMD Flows for Schatten $p=1,2,\infty$

            This notebook compares three particle flows for the same objective
            $$
            f(\mu)=\operatorname{MMD}(\mu,\nu)^2,
            $$
            where the kernel is the energy-distance kernel
            $$
            k(x,y)=-\|x-y\|_2.
            $$

            The transport geometry is indexed by a norm $\gamma$ on positive semidefinite matrices. For the Schatten family
            $$
            \gamma_p(S)=\|S\|_{S_p},
            $$
            the three cases displayed here are:

            - $p=1$: the trace norm, which recovers the classical $W_2$ / Euclidean flow;
            - $p=2$: the Frobenius-intermediate geometry;
            - $p=\infty$: the operator norm, which gives the Muon-type flow.
            """
        ),
        *notebook_preamble_cells(),
        code(
            r"""
            def smooth_cdist(X: torch.Tensor, Y: torch.Tensor, eps: float = 1e-2) -> torch.Tensor:
                diff = X[:, None, :] - Y[None, :, :]
                return torch.sqrt((diff * diff).sum(dim=-1) + eps**2)

            def mmd_energy_squared(X: torch.Tensor, Y: torch.Tensor, eps: float = 1e-2) -> torch.Tensor:
                D_xx = smooth_cdist(X, X, eps)
                D_yy = smooth_cdist(Y, Y, eps)
                D_xy = smooth_cdist(X, Y, eps)
                return 2.0 * D_xy.mean() - D_xx.mean() - D_yy.mean()

            def schatten_direction(grad: torch.Tensor, p):
                if p == 1:
                    return -grad
                U, S, Vh = torch.linalg.svd(grad, full_matrices=False)
                if p == float("inf"):
                    return -S.sum() * (U @ Vh)
                r = 2.0 * p
                q = r / (r - 1.0)
                norm_q = (S.pow(q).sum()).pow(1.0 / q)
                if float(norm_q) < 1e-14:
                    return torch.zeros_like(grad)
                weights = S.pow(q - 1.0)
                return -(norm_q.pow(2.0 - q)) * ((U * weights.unsqueeze(0)) @ Vh)

            def run_flow(x0: torch.Tensor, y: torch.Tensor, p, step_size: float, steps: int, eps: float):
                x = x0.clone().detach()
                history = [x.clone()]
                losses = []
                for _ in range(steps):
                    x = x.detach().requires_grad_(True)
                    loss = mmd_energy_squared(x, y, eps)
                    loss.backward()
                    grad = x.grad.detach()
                    vel = schatten_direction(grad, p)
                    with torch.no_grad():
                        x = x + step_size * vel
                    history.append(x.clone())
                    losses.append(float(loss.detach()))
                return {"history": torch.stack(history), "losses": np.array(losses, dtype=float)}

            def blended_color(step_id: int, total_steps: int):
                t = step_id / total_steps
                red = np.array([220, 20, 60], dtype=float) / 255.0
                blue = np.array([65, 105, 225], dtype=float) / 255.0
                return tuple((1.0 - t) * red + t * blue)
            """
        ),
        md(
            r"""
            ## Setup

            We use the same source-target pair for all three flows.

            - `n = m = 200` particles,
            - a farther-away Gaussian-mixture target,
            - a long integration horizon,
            - logarithmically spaced displayed times to emphasize the early regime.
            """
        ),
        code(
            r"""
            import ipywidgets as widgets

            n = 200
            m = 200
            steps = 6000
            eps = 1e-2
            step_sizes = {1: 2.5, 2: 1.8, float("inf"): 1.6}
            names = {1: "Schatten $p=1$ / $W_2$", 2: "Schatten $p=2$", float("inf"): "Schatten $p=\\infty$ / Muon"}

            Y = sample_target(m)
            X0 = sample_source(n)

            fig, ax = plt.subplots(figsize=(6.4, 6.4))
            ax.scatter(Y[:, 0], Y[:, 1], s=20, c="royalblue", alpha=0.85, label="target $\\nu$")
            ax.scatter(X0[:, 0], X0[:, 1], s=20, c="crimson", alpha=0.78, label="initial $\\mu_0$")
            ax.set_title("Initial source and target clouds")
            ax.set_aspect("equal")
            ax.legend()
            plt.show()
            """
        ),
        code(
            r"""
            results = {p: run_flow(X0, Y, p, step_sizes[p], steps, eps) for p in [1, 2, float("inf")]}
            for p in [1, 2, float("inf")]:
                print(names[p], "final loss =", f"{results[p]['losses'][-1]:.6f}")
            """
        ),
        code(
            r"""
            all_points = [Y.numpy(), X0.numpy()] + [out["history"][-1].numpy() for out in results.values()]
            stacked = np.concatenate(all_points, axis=0)
            x_min, y_min = stacked.min(axis=0) - 0.7
            x_max, y_max = stacked.max(axis=0) + 0.7

            fig, axes = plt.subplots(1, 3, figsize=(18, 5.8), constrained_layout=True)
            for ax, p in zip(axes, [1, 2, float("inf")]):
                history = results[p]["history"]
                ax.scatter(Y[:, 0], Y[:, 1], s=14, c="royalblue", alpha=0.24)
                for idx in range(n):
                    curve = history[:, idx].numpy()
                    ax.plot(curve[:, 0], curve[:, 1], color="black", lw=0.45, alpha=0.18)
                ax.scatter(history[0, :, 0], history[0, :, 1], s=14, c="crimson", alpha=0.75)
                ax.scatter(history[-1, :, 0], history[-1, :, 1], s=14, c="royalblue", alpha=0.82)
                ax.set_title(f"{names[p]}\nfinal loss = {results[p]['losses'][-1]:.4f}")
                ax.set_aspect("equal")
                ax.set_xlim(x_min, x_max)
                ax.set_ylim(y_min, y_max)
            plt.show()
            """
        ),
        code(
            r"""
            snapshot_ids = np.round(np.geomspace(1.0, steps + 1.0, 8) - 1.0).astype(int)
            snapshot_ids[0] = 0
            snapshot_ids[-1] = steps

            fig, axes = plt.subplots(3, 8, figsize=(18.5, 7.8), constrained_layout=True)
            for row, p in enumerate([1, 2, float("inf")]):
                history = results[p]["history"]
                for ax, step_id in zip(axes[row], snapshot_ids):
                    ax.scatter(Y[:, 0], Y[:, 1], s=8, c="royalblue", alpha=0.18)
                    ax.scatter(
                        history[step_id, :, 0],
                        history[step_id, :, 1],
                        s=10,
                        c=[blended_color(step_id, steps)],
                        alpha=0.88,
                    )
                    ax.set_title(f"p={'inf' if p == float('inf') else p}\n$k={step_id}$", fontsize=9)
                    ax.set_aspect("equal")
                    ax.set_xlim(x_min, x_max)
                    ax.set_ylim(y_min, y_max)
                    ax.set_xticks([])
                    ax.set_yticks([])
            plt.show()
            """
        ),
        code(
            r"""
            fig, ax = plt.subplots(figsize=(7.2, 4.8))
            for p in [1, 2, float("inf")]:
                ax.plot(results[p]["losses"], lw=2.1, label=f"{names[p]} ({results[p]['losses'][-1]:.4f})")
            ax.set_xlabel("iteration")
            ax.set_ylabel("$f(\\mu_k)$")
            ax.set_title("MMD decay for the three generalized Wasserstein flows")
            ax.legend(fontsize=9)
            plt.show()
            """
        ),
        md(
            r"""
            ## Interactive Comparison

            The slider displays the three evolving clouds at the same iteration. Red means early time, blue means late time.
            """
        ),
        code(
            r"""
            def show_frame(step_id: int):
                fig, axes = plt.subplots(1, 3, figsize=(18, 5.6), constrained_layout=True)
                for ax, p in zip(axes, [1, 2, float("inf")]):
                    history = results[p]["history"]
                    ax.scatter(Y[:, 0], Y[:, 1], s=14, c="royalblue", alpha=0.22)
                    ax.scatter(history[step_id, :, 0], history[step_id, :, 1], s=16, c=[blended_color(step_id, steps)], alpha=0.9)
                    ax.set_title(f"{names[p]}\n$k={step_id}$")
                    ax.set_aspect("equal")
                    ax.set_xlim(x_min, x_max)
                    ax.set_ylim(y_min, y_max)
                plt.show()

            slider = widgets.IntSlider(value=0, min=0, max=steps, step=max(1, steps // 150), description="step")
            widgets.interact(show_frame, step_id=slider)
            """
        ),
    ]
    nb["cells"] = cells
    return nb


def build_static_notebook():
    nb = nbf.v4.new_notebook()
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
    }
    cells = [
        md(
            r"""
            # Static Generalized Optimal Matchings for Schatten $p=1,2,\infty$

            This notebook studies the discrete static Spectral Wasserstein problem for two empirical measures.

            For
            $$
            \mu = \sum_{i=1}^n a_i \delta_{x_i},
            \qquad
            \nu = \sum_{j=1}^m b_j \delta_{y_j},
            $$
            a coupling is represented by a transport matrix $P \in \mathbb{R}_+^{n\times m}$ with
            $$
            P \mathbf{1}_m = a,
            \qquad
            P^\top \mathbf{1}_n = b.
            $$
            The discrete static problem is
            $$
            \min_{P \ge 0,\; P \mathbf{1}_m = a,\; P^\top \mathbf{1}_n = b}
            \gamma_p\!\left(
            \sum_{i=1}^n \sum_{j=1}^m P_{ij} (y_j-x_i)(y_j-x_i)^\top
            \right).
            $$

            - For $p=1$, this is the usual quadratic optimal-transport problem.
            - For $p=2$, the objective is a convex second-order-cone expression.
            - For $p=\infty$, the objective is the maximal eigenvalue of a PSD matrix, hence an SDP-representable convex objective.

            We solve the $p=2$ and $p=\infty$ cases with CVXPY, and in the equal-weight case we extract a permutation from the optimal plan for visualization.

            To keep the static and dynamic experiments directly comparable, we use exactly the same source and target clouds as in the MMD-flow notebook.
            """
        ),
        *notebook_preamble_cells(),
        code(
            r"""
            import cvxpy as cp
            from scipy.optimize import linear_sum_assignment

            def solve_static_coupling_cvxpy(X: np.ndarray, Y: np.ndarray, p, solver: str = "SCS"):
                n, m = len(X), len(Y)
                a = np.full(n, 1.0 / n)
                b = np.full(m, 1.0 / m)
                dx = Y[None, :, 0] - X[:, None, 0]
                dy = Y[None, :, 1] - X[:, None, 1]
                A11 = dx * dx
                A12 = dx * dy
                A22 = dy * dy

                if p == 1:
                    C = A11 + A22
                    rows, cols = linear_sum_assignment(C)
                    perm = np.empty(n, dtype=int)
                    perm[rows] = cols
                    P = np.zeros((n, m), dtype=float)
                    P[np.arange(n), perm] = 1.0 / n
                    return P, float(C[np.arange(n), perm].sum() / n)

                P = cp.Variable((n, m), nonneg=True)
                constraints = [cp.sum(P, axis=1) == a, cp.sum(P, axis=0) == b]
                S11 = cp.sum(cp.multiply(A11, P))
                S12 = cp.sum(cp.multiply(A12, P))
                S22 = cp.sum(cp.multiply(A22, P))
                S = cp.bmat([[S11, S12], [S12, S22]])

                if p == 2:
                    objective = cp.Minimize(cp.norm(S, "fro"))
                elif p == np.inf:
                    objective = cp.Minimize(cp.lambda_max(S))
                else:
                    raise ValueError(p)

                problem = cp.Problem(objective, constraints)
                problem.solve(solver=solver, verbose=False, eps=1e-5, max_iters=12000)
                if P.value is None:
                    raise RuntimeError(f"solver failed with status {problem.status}")
                return np.asarray(P.value, dtype=float), float(problem.value)

            def extract_permutation_from_plan(P: np.ndarray) -> np.ndarray:
                rows, cols = linear_sum_assignment(-P)
                perm = np.empty(len(rows), dtype=int)
                perm[rows] = cols
                return perm
            """
        ),
        code(
            r"""
            X, Y = sample_static_pair(num_points=200)
            n = len(X)

            couplings = {}
            for p in [1, 2, np.inf]:
                P_opt, cost = solve_static_coupling_cvxpy(X, Y, p)
                couplings[p] = {"P": P_opt, "cost": cost, "perm": extract_permutation_from_plan(P_opt)}

            for p in [1, 2, np.inf]:
                print("p =", p, "cost =", couplings[p]["cost"], "plan mass on extracted permutation =", couplings[p]["P"][np.arange(n), couplings[p]["perm"]].sum())
            """
        ),
        code(
            r"""
            all_pts = np.concatenate([X, Y], axis=0)
            x_min, y_min = all_pts.min(axis=0) - 0.7
            x_max, y_max = all_pts.max(axis=0) + 0.7

            fig, axes = plt.subplots(1, 3, figsize=(18, 5.6), constrained_layout=True)
            for ax, p in zip(axes, [1, 2, np.inf]):
                perm = couplings[p]["perm"]
                cost = couplings[p]["cost"]
                ax.scatter(X[:, 0], X[:, 1], s=26, c="crimson", alpha=0.82, label="source")
                ax.scatter(Y[:, 0], Y[:, 1], s=26, c="royalblue", alpha=0.82, label="target")
                for i in range(n):
                    seg = np.vstack([X[i], Y[perm[i]]])
                    ax.plot(seg[:, 0], seg[:, 1], color="black", lw=0.85, alpha=0.5)
                ax.set_title(f"Schatten p={'inf' if p is np.inf else p}\ncost = {cost:.3f}")
                ax.set_aspect("equal")
                ax.set_xlim(x_min, x_max)
                ax.set_ylim(y_min, y_max)
            axes[0].legend(loc="upper right")
            plt.show()
            """
        ),
        code(
            r"""
            fig, ax = plt.subplots(figsize=(7.0, 4.8))
            for p, color in zip([1, 2, np.inf], ["crimson", "darkorange", "royalblue"]):
                perm = couplings[p]["perm"]
                s = np.linalg.svd(Y[perm] - X, compute_uv=False, full_matrices=False)
                ax.plot(s, marker="o", lw=2, color=color, label=f"p={'inf' if p is np.inf else p}")
            ax.set_title("Singular values of the displacement matrix")
            ax.set_xlabel("index")
            ax.set_ylabel("singular value")
            ax.legend()
            plt.show()
            """
        ),
    ]
    nb["cells"] = cells
    return nb


def generate_figures():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams["figure.figsize"] = (7, 6)
    plt.rcParams["axes.grid"] = True
    plt.rcParams["grid.alpha"] = 0.2
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.spines.right"] = False

    x_static, y_static = sample_static_pair(num_points=200)
    n_static = len(x_static)
    couplings = {}
    for p in [1, 2, np.inf]:
        P_opt, cost = solve_static_coupling_cvxpy(x_static, y_static, p)
        couplings[p] = {"P": P_opt, "cost": cost, "perm": extract_permutation_from_plan(P_opt)}

    all_static = np.concatenate([x_static, y_static], axis=0)
    sx_min, sy_min = all_static.min(axis=0) - 0.7
    sx_max, sy_max = all_static.max(axis=0) + 0.7

    fig, axes = plt.subplots(1, 3, figsize=(18, 5.6), constrained_layout=True)
    for ax, p in zip(axes, [1, 2, np.inf]):
        perm = couplings[p]["perm"]
        cost = couplings[p]["cost"]
        ax.scatter(x_static[:, 0], x_static[:, 1], s=26, c="crimson", alpha=0.82, label="source")
        ax.scatter(y_static[:, 0], y_static[:, 1], s=26, c="royalblue", alpha=0.82, label="target")
        for i in range(n_static):
            seg = np.vstack([x_static[i], y_static[perm[i]]])
            ax.plot(seg[:, 0], seg[:, 1], color="black", lw=0.85, alpha=0.5)
        ax.set_title(f"Schatten p={'inf' if p is np.inf else p}\ncost = {cost:.3f}")
        ax.set_aspect("equal")
        ax.set_xlim(sx_min, sx_max)
        ax.set_ylim(sy_min, sy_max)
    axes[0].legend(loc="upper right", fontsize=9)
    fig.savefig(FIG_DIR / "static_matchings_three.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    n = 200
    m = 200
    steps = 6000
    eps = 1e-2
    step_sizes = {1: 2.5, 2: 1.8, float("inf"): 1.6}
    labels = {
        1: "Schatten $p=1$ / $W_2$",
        2: "Schatten $p=2$",
        float("inf"): "Schatten $p=\\infty$ / Muon",
    }

    x0, y = sample_mmd_pair(n)
    results = {p: run_flow(x0, y, p, step_sizes[p], steps, eps) for p in [1, 2, float("inf")]}

    all_points = [y.numpy(), x0.numpy()] + [out["history"][-1].numpy() for out in results.values()]
    stacked = np.concatenate(all_points, axis=0)
    x_min, y_min = stacked.min(axis=0) - 0.7
    x_max, y_max = stacked.max(axis=0) + 0.7
    snapshot_ids = np.round(np.geomspace(1.0, steps + 1.0, 8) - 1.0).astype(int)
    snapshot_ids[0] = 0
    snapshot_ids[-1] = steps

    fig, axes = plt.subplots(1, 3, figsize=(18, 5.6), constrained_layout=True)
    for ax, p in zip(axes, [1, 2, float("inf")]):
        history = results[p]["history"]
        ax.scatter(y[:, 0], y[:, 1], s=14, c="royalblue", alpha=0.24, label="target")
        for idx in range(n):
            curve = history[:, idx].numpy()
            ax.plot(curve[:, 0], curve[:, 1], color="black", lw=0.45, alpha=0.18)
        ax.scatter(history[0, :, 0], history[0, :, 1], s=14, c="crimson", alpha=0.75, label="start")
        ax.scatter(history[-1, :, 0], history[-1, :, 1], s=14, c="royalblue", alpha=0.80, label="end")
        ax.set_title(f"{labels[p]}\nfinal loss = {results[p]['losses'][-1]:.4f}")
        ax.set_aspect("equal")
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
    axes[0].legend(loc="upper right", fontsize=9)
    fig.savefig(FIG_DIR / "mmd_trajectories_three.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(3, 8, figsize=(18.5, 7.5), constrained_layout=True)
    for row, p in enumerate([1, 2, float("inf")]):
        history = results[p]["history"]
        for ax, step_id in zip(axes[row], snapshot_ids):
            ax.scatter(y[:, 0], y[:, 1], s=8, c="royalblue", alpha=0.18)
            ax.scatter(
                history[step_id, :, 0],
                history[step_id, :, 1],
                s=10,
                c=[blended_color(step_id, steps)],
                alpha=0.88,
            )
            ax.set_title(f"p={'inf' if p == float('inf') else p}\n$k={step_id}$", fontsize=9)
            ax.set_aspect("equal")
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_xticks([])
            ax.set_yticks([])
    fig.savefig(FIG_DIR / "mmd_snapshots_three.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.0, 4.8))
    for p in [1, 2, float("inf")]:
        ax.plot(results[p]["losses"], lw=2.2, label=f"{labels[p]} ({results[p]['losses'][-1]:.4f})")
    ax.set_xlabel("iteration")
    ax.set_ylabel("$f(\\mu_k)$")
    ax.set_title("MMD decay for three generalized Wasserstein flows")
    ax.legend(fontsize=9)
    fig.savefig(FIG_DIR / "mmd_losses_three.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    return labels, results


def main():
    PYTHON_DIR.mkdir(exist_ok=True)
    labels, results = generate_figures()

    with open(PYTHON_DIR / "mmd_flow.ipynb", "w", encoding="utf-8") as f:
        nbf.write(build_mmd_notebook(), f)
    with open(PYTHON_DIR / "static.ipynb", "w", encoding="utf-8") as f:
        nbf.write(build_static_notebook(), f)

    print("wrote notebooks and figures")
    for p in [1, 2, float("inf")]:
        print(labels[p], "final loss =", results[p]["losses"][-1])


if __name__ == "__main__":
    main()
