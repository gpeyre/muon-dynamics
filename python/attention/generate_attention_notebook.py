from pathlib import Path
from textwrap import dedent

import nbformat as nbf


ROOT = Path(__file__).resolve().parent
NOTEBOOK = ROOT / "attention_spectral_flow.ipynb"
FIG_DIR_TARGET = "../../neurips/figures/fig-attention"


def md(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip() + "\n")


def code(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip() + "\n")


cells = [
    md(
        r"""
        # Spectral Flows for a Mean-Field Shallow Attention Layer

        This notebook compares the trace geometry $p=1$ and the operator geometry
        $p=\infty$ for training a shallow mean-field multi-head attention model.

        A head is a particle $x=(Q,K,V,O)$, with
        $$Q,K,V\in\mathbb{R}^{d_H\times d_T}, \qquad
        O\in\mathbb{R}^{d_H\times d_T}.$$

        For tokens $z=(z_1,\ldots,z_m)$, one head computes
        $$
        \phi(z,x)_j =
        O^\top \sum_i
        \frac{\exp(\langle Qz_j,Kz_i\rangle/\sqrt{d_H})}
        {\sum_\ell \exp(\langle Qz_j,Kz_\ell\rangle/\sqrt{d_H})}
        Vz_i.
        $$

        The mean-field predictor is $H_\mu(z)=\int\phi(z,x)d\mu(x)$.
        For $\mu_X=n^{-1}\sum_i\delta_{x_i}$, this is a standard multi-head
        attention layer with $n$ heads, averaged instead of concatenated.
        """
    ),
    md(
        r"""
        ## Numerical experiment

        We train a student with $n$ heads to match a random teacher with $k=5$
        heads. We compare two teacher temperatures, very dense and very sparse,
        by varying the query-key scale.

        The effective number of attended tokens is measured by the participation
        ratio $1/\sum_i w_i^2$ of each attention row.

        At very high temperature, softmax approaches a linearized regime around
        a nearly uniform attention matrix; this makes the attention map a smooth
        low-order polynomial function of the input tokens (cubic at first
        non-trivial order in this setup).
        """
    ),
    code(
        r"""
        from pathlib import Path
        import json
        import math
        import random

        import matplotlib.pyplot as plt
        import numpy as np
        import torch

        torch.set_default_dtype(torch.float32)

        SEED = 123
        random.seed(SEED)
        np.random.seed(SEED)
        torch.manual_seed(SEED)

        FIG_DIR = Path("__FIG_DIR__")
        FIG_DIR.mkdir(parents=True, exist_ok=True)

        plt.rcParams.update(
            {
                "figure.dpi": 150,
                "font.size": 11,
                "axes.grid": True,
                "grid.alpha": 0.22,
                "axes.spines.top": True,
                "axes.spines.right": True,
            }
        )
        """.replace("__FIG_DIR__", FIG_DIR_TARGET)
    ),
    code(
        r"""
        # Dimensions kept deliberately small, but with enough tokens to see
        # dense-vs-sparse attention effects.
        d_T = 4
        d_H = 3
        m = 16
        N = 32
        k_teacher = 5
        n_student = 200

        # Flattened parameter dimension: Q,K,V,O all have shape d_H x d_T.
        D = 4 * d_H * d_T

        def unpack_heads(X: torch.Tensor):
            n = X.shape[0]
            block = d_H * d_T
            Q = X[:, 0:block].reshape(n, d_H, d_T)
            K = X[:, block:2 * block].reshape(n, d_H, d_T)
            V = X[:, 2 * block:3 * block].reshape(n, d_H, d_T)
            O = X[:, 3 * block:4 * block].reshape(n, d_H, d_T)
            return Q, K, V, O

        def attention_components(X: torch.Tensor, Z: torch.Tensor):
            # Fully vectorized over data, heads, query tokens, and key tokens.
            Q, K, V, O = unpack_heads(X)
            queries = torch.einsum("hab,njb->nhja", Q, Z)
            keys = torch.einsum("hab,nib->nhia", K, Z)
            values = torch.einsum("hab,nib->nhia", V, Z)
            scores = torch.einsum("nhja,nhia->nhji", queries, keys) / math.sqrt(d_H)
            weights = torch.softmax(scores, dim=-1)
            hidden = torch.einsum("nhji,nhia->nhja", weights, values)
            out = torch.einsum("hab,nhja->nhjb", O, hidden)
            return out.mean(dim=1), weights

        def attention_predict(X: torch.Tensor, Z: torch.Tensor) -> torch.Tensor:
            pred, _ = attention_components(X, Z)
            return pred

        def effective_tokens(X: torch.Tensor, Z: torch.Tensor) -> float:
            _, weights = attention_components(X, Z)
            participation = 1.0 / (weights.square().sum(dim=-1) + 1e-12)
            return float(participation.mean())

        def attention_weight_values(X: torch.Tensor, Z: torch.Tensor) -> np.ndarray:
            _, weights = attention_components(X, Z)
            return weights.detach().cpu().numpy().ravel()

        def empirical_loss(X: torch.Tensor, Z: torch.Tensor, Y: torch.Tensor) -> torch.Tensor:
            pred = attention_predict(X, Z)
            return 0.5 * ((pred - Y) ** 2).mean()

        print(f"Token count m={m}, sqrt(m)={math.sqrt(m):.2f}")
        print(f"Parameter dimension per head D={D}")
        """
    ),
    code(
        r"""
        def random_teacher_heads(
            num_heads: int,
            qk_scale: float,
            vo_scale: float,
            generator: torch.Generator,
        ) -> torch.Tensor:
            block = d_H * d_T
            Q = qk_scale * torch.randn(num_heads, block, generator=generator)
            K = qk_scale * torch.randn(num_heads, block, generator=generator)
            V = vo_scale * torch.randn(num_heads, block, generator=generator)
            O = vo_scale * torch.randn(num_heads, block, generator=generator)
            return torch.cat([Q, K, V, O], dim=1)

        Z_train = torch.randn(N, m, d_T)
        Z_test = torch.randn(96, m, d_T)

        regime_order = ["very_dense", "very_sparse"]
        regimes = {
            "very_dense": {
                "title": "Very dense",
                "qk_scale": 0.08,
                "vo_scale": 0.65,
            },
            "very_sparse": {
                "title": "Very sparse",
                "qk_scale": 1.45,
                "vo_scale": 0.65,
            },
        }
        """
    ),
    md(
        r"""
        ## Spectral selectors and Euler flow

        We train the flattened particle matrix $X\in\mathbb{R}^{n\times D}$.
        The $p=1$ selector gives ordinary gradient flow, while $p=\infty$ uses
        the Muon-type polar selector. The same implementation is used for all
        temperature regimes.
        """
    ),
    code(
        r"""
        def spectral_selector(G: torch.Tensor, p):
            if p == 1:
                return -G
            if p == float("inf"):
                U, S, Vh = torch.linalg.svd(G, full_matrices=False)
                nuclear = S.sum()
                if float(nuclear) < 1e-12:
                    return torch.zeros_like(G)
                return -nuclear * (U @ Vh)
            raise ValueError("Only p=1 and p=inf are implemented.")

        def run_flow(
            X0: torch.Tensor,
            Z: torch.Tensor,
            Y: torch.Tensor,
            p,
            step_size: float,
            steps: int,
            max_step_norm: float,
        ):
            X = X0.clone().detach()
            losses = []
            for it in range(steps):
                X = X.detach().requires_grad_(True)
                loss = empirical_loss(X, Z, Y)
                loss.backward()
                G = X.grad.detach()
                Vdir = spectral_selector(G, p)
                with torch.no_grad():
                    dX = step_size * Vdir
                    norm_dX = float(torch.linalg.norm(dX))
                    if norm_dX > max_step_norm:
                        dX = dX * (max_step_norm / (norm_dX + 1e-12))
                    X = torch.clamp(torch.nan_to_num(X + dX), -10.0, 10.0)
                    losses.append(float(loss.detach()))
            return {"X": X.detach(), "losses": np.asarray(losses)}
        """
    ),
    md(
        r"""
        ## Run five random initializations in the two temperature regimes

        The nominal Euler horizons are $960\times100=96000$ for the trace flow
        and $480\times180=86400$ for the operator flow, a ratio of $10/9$.
        Each display axis is normalized by its own nominal horizon. Global
        step clipping and coordinate guards mean these are not exact
        continuous-flow clocks or wall-clock times.
        """
    ),
    code(
        r"""
        n_runs = 5
        # Twice as many trace steps; unequal step sizes give a 10/9 horizon ratio.
        steps_base = 480
        steps_map = {1: 2 * steps_base, float("inf"): steps_base}
        max_step_norm = 0.45
        step_size = {1: 1.0e2, float("inf"): 1.8e2}

        initializations = []
        for run in range(n_runs):
            gen = torch.Generator().manual_seed(1000 + run)
            X0 = 0.16 * torch.randn(n_student, D, generator=gen)
            initializations.append(X0)

        teacher_runs = {name: [] for name in regime_order}
        all_results = {}
        for ridx, regime_name in enumerate(regime_order):
            cfg = regimes[regime_name]
            print(f"\n=== {regime_name.upper()} ===")
            all_results[regime_name] = {1: [], float("inf"): []}
            for run, X0 in enumerate(initializations):
                teacher_gen = torch.Generator().manual_seed(7000 + 100 * ridx + run)
                X_teacher = random_teacher_heads(
                    k_teacher,
                    cfg["qk_scale"],
                    cfg["vo_scale"],
                    teacher_gen,
                )
                with torch.no_grad():
                    Y_train = attention_predict(X_teacher, Z_train)
                    Y_test = attention_predict(X_teacher, Z_test)
                    eff = effective_tokens(X_teacher, Z_train)
                    weight_values = attention_weight_values(X_teacher, Z_train)
                teacher_runs[regime_name].append(
                    {
                        "teacher": X_teacher,
                        "Y_train": Y_train,
                        "Y_test": Y_test,
                        "effective_tokens": eff,
                        "attention_values": weight_values,
                    }
                )
                print(
                    f"{regime_name}, run={run}, qk_scale={cfg['qk_scale']}, "
                    f"effective tokens={eff:.2f}"
                )
                for p in [1, float("inf")]:
                    result = run_flow(
                        X0,
                        Z_train,
                        Y_train,
                        p=p,
                        step_size=step_size[p],
                        steps=steps_map[p],
                        max_step_norm=max_step_norm,
                    )
                    all_results[regime_name][p].append(result)
                    print(
                        f"{regime_name}, p={p}, run={run}, "
                        f"initial={result['losses'][0]:.4e}, final={result['losses'][-1]:.4e}"
                    )
        """
    ),
    code(
        r"""
        from matplotlib.lines import Line2D

        colors = {1: (0.05, 0.20, 0.95), float("inf"): (0.95, 0.05, 0.05)}
        labels = {1: r"$p=1$", float("inf"): r"$p=\infty$"}

        stats = {}
        for regime_name in regime_order:
            cfg = regimes[regime_name]
            eff_tokens = np.array([r["effective_tokens"] for r in teacher_runs[regime_name]])
            stats[regime_name] = {
                "effective_tokens_mean": float(eff_tokens.mean()),
                "effective_tokens_std": float(eff_tokens.std()),
            }

        hist_bins = np.linspace(0.0, 0.1, 45)
        histograms = {}
        global_hist_max = 0.0
        for regime_name in regime_order:
            all_vals = np.concatenate(
                [r["attention_values"] for r in teacher_runs[regime_name]],
                axis=0,
            )
            hist, edges = np.histogram(all_vals, bins=hist_bins, density=True)
            histograms[regime_name] = (hist, edges)
            global_hist_max = max(global_hist_max, float(hist.max()))

        def plot_histogram_panel(ax, regime_name):
            hist, edges = histograms[regime_name]
            centers = 0.5 * (edges[:-1] + edges[1:])
            width = edges[1] - edges[0]
            ax.bar(centers, hist, width=width, color="0.25", edgecolor="0.25")
            ax.set_xlim(0, 0.1)
            ax.set_ylim(0, 1.05 * global_hist_max)
            ax.set_ylabel("Dense" if regime_name == "very_dense" else "Sparse")
            ax.grid(False)

        fig_overall = plt.figure(figsize=(13.8, 3.8), constrained_layout=True)
        outer = fig_overall.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 1.0])
        axes = [fig_overall.add_subplot(outer[0, 0]), fig_overall.add_subplot(outer[0, 1])]
        hist_grid = outer[0, 2].subgridspec(2, 1, hspace=0.18)
        hist_axes = [fig_overall.add_subplot(hist_grid[0, 0]), fig_overall.add_subplot(hist_grid[1, 0])]
        for idx, regime_name in enumerate(regime_order):
            ax = axes[idx]
            cfg = regimes[regime_name]
            for p in [1, float("inf")]:
                curves = np.stack([r["losses"] for r in all_results[regime_name][p]], axis=0)
                t = np.linspace(0, 1, curves.shape[1])
                for c in curves:
                    ax.semilogy(t, c, color=colors[p], alpha=0.5, linewidth=1.1)
            ax.set_xlabel("normalized optimization time")
            ax.set_ylabel("training energy")
            legend_handles = [
                Line2D([0], [0], color=colors[1], lw=2.0, label=labels[1]),
                Line2D([0], [0], color=colors[float("inf")], lw=2.0, label=labels[float("inf")]),
            ]
            ax.legend(handles=legend_handles, frameon=True)
            plot_histogram_panel(hist_axes[idx], regime_name)
        hist_axes[0].set_xticklabels([])
        hist_axes[1].set_xlabel("teacher attention value")
        fig_path = FIG_DIR / "attention_energy_decay.pdf"
        fig_overall.savefig(fig_path, bbox_inches="tight")
        plt.show()

        fig_hist, hist_axes_single = plt.subplots(2, 1, figsize=(4.6, 3.4), constrained_layout=True)
        for ax, regime_name in zip(hist_axes_single, regime_order):
            plot_histogram_panel(ax, regime_name)
        hist_axes_single[0].set_xticklabels([])
        hist_axes_single[1].set_xlabel("teacher attention value")
        hist_path = FIG_DIR / "attention_teacher_histograms.pdf"
        fig_hist.savefig(hist_path, bbox_inches="tight")
        plt.close(fig_hist)

        for regime_name in regime_order:
            fig_single, ax = plt.subplots(figsize=(4.6, 3.4), constrained_layout=True)
            for p in [1, float("inf")]:
                curves = np.stack([r["losses"] for r in all_results[regime_name][p]], axis=0)
                t = np.linspace(0, 1, curves.shape[1])
                for c in curves:
                    ax.semilogy(t, c, color=colors[p], alpha=0.5, linewidth=1.1)
            ax.set_xlabel("normalized optimization time")
            ax.set_ylabel("training energy")
            legend_handles = [
                Line2D([0], [0], color=colors[1], lw=2.0, label=labels[1]),
                Line2D([0], [0], color=colors[float("inf")], lw=2.0, label=labels[float("inf")]),
            ]
            ax.legend(handles=legend_handles, frameon=True)
            if regime_name == "very_dense":
                panel_path = FIG_DIR / "attention_energy_decay_dense.pdf"
            else:
                panel_path = FIG_DIR / "attention_energy_decay_sparse.pdf"
            fig_single.savefig(panel_path, bbox_inches="tight")
            plt.close(fig_single)

        stats_path = FIG_DIR / "attention_energy_stats.json"
        stats_path.write_text(json.dumps(stats, indent=2))
        print(f"Saved {fig_path}")
        print(json.dumps(stats, indent=2))
        """
    ),
]


nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "py314",
    },
    "language_info": {
        "name": "python",
        "pygments_lexer": "ipython3",
    },
}

NOTEBOOK.write_text(nbf.writes(nb))
print(f"Wrote {NOTEBOOK}")
