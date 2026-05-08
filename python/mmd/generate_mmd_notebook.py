from pathlib import Path
from textwrap import dedent

import nbformat as nbf


ROOT = Path(__file__).resolve().parent
NOTEBOOK = ROOT / "mmd_flow.ipynb"
FIG_DIR_TARGET = "../../neurips/figures/fig-mmd"


def md(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip() + "\n")


def code(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip() + "\n")


cells = [
    md(
        r"""
        # MMD Spectral Flows (`p=1` vs `p=\infty`)

        We minimize
        $$
        f(\mu)=\operatorname{MMD}(\mu,\nu)^2
        $$
        for the energy-distance kernel $k(x,y)=-\|x-y\|_2$, and compare the particle flows associated with Schatten selectors for `p=1` and `p=\infty`.
        """
    ),
    code(
        r"""
        from pathlib import Path
        import random

        import matplotlib.pyplot as plt
        import numpy as np
        import torch

        torch.set_default_dtype(torch.float64)

        SEED = 1234
        random.seed(SEED)
        np.random.seed(SEED)
        torch.manual_seed(SEED)

        FIG_DIR = Path("__FIG_DIR__")
        FIG_DIR.mkdir(parents=True, exist_ok=True)

        plt.rcParams.update(
            {
                "figure.dpi": 140,
                "font.size": 11,
                "axes.grid": True,
                "grid.alpha": 0.22,
                "axes.spines.top": False,
                "axes.spines.right": False,
            }
        )
        """.replace("__FIG_DIR__", FIG_DIR_TARGET)
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
            if p == float("inf"):
                U, S, Vh = torch.linalg.svd(grad, full_matrices=False)
                return -S.sum() * (U @ Vh)
            raise ValueError("Only p=1 and p=inf are supported in this notebook.")


        def run_flow(X0: torch.Tensor, Y: torch.Tensor, p, step_size: float, steps: int, eps: float = 1e-2):
            X = X0.clone().detach()
            history = [X.clone().cpu()]
            losses = []
            for _ in range(steps):
                X = X.detach().requires_grad_(True)
                loss = mmd_energy_squared(X, Y, eps)
                loss.backward()
                G = X.grad.detach()
                V = schatten_direction(G, p)
                with torch.no_grad():
                    X = X + step_size * V
                history.append(X.clone().cpu())
                losses.append(float(loss.detach().cpu()))
            return {"history": torch.stack(history), "losses": np.asarray(losses)}
        """
    ),
    code(
        r"""
        n = 200
        m = 200
        steps = 6000
        eps = 1e-2

        # 2x larger step sizes, yielding a 2x larger effective final integration time.
        step_sizes = {1: 5.0, float("inf"): 3.2}
        names = {1: "Schatten $p=1$", float("inf"): "Schatten $p=\\infty$"}

        Y = sample_target(m)
        X0 = sample_source(n)

        results = {p: run_flow(X0, Y, p, step_sizes[p], steps, eps) for p in [1, float("inf")]}
        for p in [1, float("inf")]:
            print(names[p], "final loss =", f"{results[p]['losses'][-1]:.6f}")
        """
    ),
    code(
        r"""
        def plot_trajectories_for_p(p, save_path: Path):
            history = results[p]["history"]

            all_points = np.concatenate([Y.numpy(), X0.numpy(), history[-1].numpy()], axis=0)
            x_min, y_min = all_points.min(axis=0) - 0.7
            x_max, y_max = all_points.max(axis=0) + 0.7

            fig, ax = plt.subplots(figsize=(6.6, 6.2), constrained_layout=True)
            ax.scatter(Y[:, 0], Y[:, 1], s=16, c="royalblue", alpha=0.22, label="target")

            for idx in range(history.shape[1]):
                curve = history[:, idx].numpy()
                ax.plot(curve[:, 0], curve[:, 1], color="black", lw=0.9, alpha=0.26)

            ax.scatter(history[0, :, 0], history[0, :, 1], s=14, c="crimson", alpha=0.75, label="source")
            ax.scatter(history[-1, :, 0], history[-1, :, 1], s=14, c="royalblue", alpha=0.82, label="final")

            ax.set_aspect("equal")
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_axis_off()
            fig.savefig(save_path, bbox_inches="tight")
            plt.show()


        pdf_p1 = FIG_DIR / "mmd_trajectories_p1.pdf"
        pdf_pinf = FIG_DIR / "mmd_trajectories_pinf.pdf"
        plot_trajectories_for_p(1, pdf_p1)
        plot_trajectories_for_p(float("inf"), pdf_pinf)

        print("Saved:")
        print(pdf_p1.resolve())
        print(pdf_pinf.resolve())
        """
    ),
    code(
        r"""
        # Error-decay comparison for f(mu_t)=MMD(mu_t,nu)^2
        fig, ax = plt.subplots(figsize=(6.6, 4.6), constrained_layout=True)
        t_p1 = np.linspace(0, 1, len(results[1]["losses"]))
        t_pinf = np.linspace(0, 1, len(results[float("inf")]["losses"]))
        ax.semilogy(t_p1, results[1]["losses"], color=(0.05, 0.20, 0.95), lw=2.0, label=r"$p=1$")
        ax.semilogy(
            t_pinf,
            results[float("inf")]["losses"],
            color=(0.95, 0.05, 0.05),
            lw=2.0,
            label=r"$p=\infty$",
        )
        ax.set_xlabel("normalized optimization time")
        ax.set_ylabel(r"$f(\mu_t)=\mathrm{MMD}(\mu_t,\nu)^2$")
        ax.legend(frameon=True)

        pdf_decay = FIG_DIR / "mmd_error_decay_p1_vs_pinf.pdf"
        fig.savefig(pdf_decay, bbox_inches="tight")
        plt.show()
        print(pdf_decay.resolve())
        """
    ),
    code(
        r"""
        # Combined paper figure: two trajectory panels and one rectangular energy-decay panel.
        fig = plt.figure(figsize=(13.8, 3.8), constrained_layout=True)
        gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 1.35])
        axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[0, 2])]
        all_points = np.concatenate([Y.numpy(), X0.numpy(), results[1]["history"][-1].numpy(), results[float("inf")]["history"][-1].numpy()], axis=0)
        x_min, y_min = all_points.min(axis=0) - 0.7
        x_max, y_max = all_points.max(axis=0) + 0.7

        for ax, p in zip(axes[:2], [1, float("inf")]):
            history = results[p]["history"]
            ax.scatter(Y[:, 0], Y[:, 1], s=12, c="royalblue", alpha=0.22)
            for idx in range(history.shape[1]):
                curve = history[:, idx].numpy()
                ax.plot(curve[:, 0], curve[:, 1], color="black", lw=0.75, alpha=0.22)
            ax.scatter(history[0, :, 0], history[0, :, 1], s=10, c="crimson", alpha=0.70)
            ax.scatter(history[-1, :, 0], history[-1, :, 1], s=10, c="royalblue", alpha=0.80)
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_aspect("equal")
            ax.set_axis_off()

        axes[2].semilogy(t_p1, results[1]["losses"], color=(0.05, 0.20, 0.95), lw=2.0, label=r"$p=1$")
        axes[2].semilogy(t_pinf, results[float("inf")]["losses"], color=(0.95, 0.05, 0.05), lw=2.0, label=r"$p=\infty$")
        axes[2].set_xlabel("normalized optimization time")
        axes[2].set_ylabel(r"$\mathrm{MMD}^2$")
        axes[2].legend(frameon=True)
        for spine in ["left", "right", "top", "bottom"]:
            axes[2].spines[spine].set_visible(True)
            axes[2].spines[spine].set_linewidth(1.0)

        combined = FIG_DIR / "mmd_combined_p1_pinf_decay.pdf"
        fig.savefig(combined, bbox_inches="tight")
        plt.show()
        print(combined.resolve())
        """
    ),
]


nb = nbf.v4.new_notebook()
nb["metadata"] = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11"},
}
nb["cells"] = cells

with NOTEBOOK.open("w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Wrote {NOTEBOOK}")
