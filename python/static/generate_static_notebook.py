from pathlib import Path
from textwrap import dedent

import nbformat as nbf


ROOT = Path(__file__).resolve().parent
NOTEBOOK = ROOT / "static_couplings.ipynb"
FIG_DIR_STATIC = "../../neurips/figures/fig-static"
FIG_DIR_DYN = "../../neurips/figures/fig-dynamics"
DATA_DIR = "../data"


def md(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip() + "\n")


def code(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip() + "\n")


cells = [
    md(
        r"""
        # Static Spectral Couplings (`p=1` vs `p=\infty`)

        This notebook builds Figure 1 panels from independent PDFs:
        - pairing plots (`p=1`, `p=\infty`),
        - five interpolation snapshots per `p` (`t=0,0.25,0.5,0.75,1`) rendered as quantized Parzen level sets.

        The trace assignment is optimal. The operator matching below is a
        permutation heuristic, not a certified spectral transport optimizer;
        an optimal spectral coupling can split mass. For a convex solve over
        all couplings, use `muon_dynamics.solve_transport` on a small cloud.
        """
    ),
    code(
        r"""
        from pathlib import Path
        import random

        import matplotlib.pyplot as plt
        import numpy as np
        from scipy.optimize import linear_sum_assignment

        SEED = 1234
        random.seed(SEED)
        np.random.seed(SEED)

        FIG_DIR_STATIC = Path("__FIG_DIR_STATIC__")
        FIG_DIR_DYN = Path("__FIG_DIR_DYN__")
        DATA_DIR = Path("__DATA_DIR__")
        FIG_DIR_STATIC.mkdir(parents=True, exist_ok=True)
        FIG_DIR_DYN.mkdir(parents=True, exist_ok=True)

        plt.rcParams.update(
            {
                "figure.dpi": 150,
                "font.size": 10,
                "axes.grid": True,
                "grid.alpha": 0.18,
                "axes.spines.top": True,
                "axes.spines.right": True,
            }
        )
        """.replace("__FIG_DIR_STATIC__", FIG_DIR_STATIC).replace("__FIG_DIR_DYN__", FIG_DIR_DYN).replace("__DATA_DIR__", DATA_DIR)
    ),
    code(
        r"""
        def sample_uniform_annulus(num_points: int, r_min: float = 1.15, r_max: float = 1.55):
            theta = 2.0 * np.pi * np.random.rand(num_points)
            rad = np.sqrt(np.random.rand(num_points) * (r_max * r_max - r_min * r_min) + r_min * r_min)
            x = rad * np.cos(theta)
            y = rad * np.sin(theta)
            return np.stack([x, y], axis=1)


        def sample_uniform_disk(num_points: int, center, radius: float):
            theta = 2.0 * np.pi * np.random.rand(num_points)
            rad = radius * np.sqrt(np.random.rand(num_points))
            x = center[0] + rad * np.cos(theta)
            y = center[1] + rad * np.sin(theta)
            return np.stack([x, y], axis=1)


        def sample_union_two_disks(num_points: int):
            n1 = num_points // 2
            n2 = num_points - n1
            d1 = sample_uniform_disk(n1, center=(4.30, 1.15), radius=0.68)
            d2 = sample_uniform_disk(n2, center=(5.00, -1.18), radius=0.66)
            Y = np.concatenate([d1, d2], axis=0)
            idx = np.random.permutation(num_points)
            return Y[idx]


        def sample_static_pair(num_points: int = 400):
            X = sample_uniform_annulus(num_points)
            Y = sample_union_two_disks(num_points)
            return X, Y


        def _grayscale01(img):
            if img.ndim == 2:
                gray = img.astype(float)
            else:
                rgb = img[:, :, :3].astype(float)
                gray = 0.2989 * rgb[:, :, 0] + 0.5870 * rgb[:, :, 1] + 0.1140 * rgb[:, :, 2]
            if gray.max() > 1.0 + 1e-8:
                gray = gray / 255.0
            return np.clip(gray, 0.0, 1.0)


        def _foreground_mask(img, occ_min=0.25, occ_max=0.50, occ_target=0.35):
            gray = _grayscale01(img)
            if img.ndim == 3 and img.shape[2] == 4:
                alpha = img[:, :, 3].astype(float)
                if alpha.max() > 1.0 + 1e-8:
                    alpha = alpha / 255.0
            else:
                alpha = np.ones_like(gray)
            valid = alpha > 1e-3
            g = gray[valid]
            # Foreground is dark. We choose threshold by controlling occupied area
            # instead of a fixed quantile (median can saturate to full square on
            # binary-like images when black area is below 50%).
            thresholds = np.linspace(0.0, 1.0, 513)
            cover = np.array([np.mean(g <= t) for t in thresholds])
            in_band = (cover >= occ_min) & (cover <= occ_max)
            if np.any(in_band):
                cand = np.where(in_band)[0]
                idx = cand[np.argmin(np.abs(cover[cand] - occ_target))]
            else:
                # If no threshold achieves the target band (e.g. heavy JPEG
                # compression), pick the closest achievable occupancy.
                if cover.min() > occ_max:
                    idx = int(np.argmin(cover))
                elif cover.max() < occ_min:
                    idx = int(np.argmax(cover))
                else:
                    # Nearest point to the interval [occ_min, occ_max].
                    dist = np.minimum(np.abs(cover - occ_min), np.abs(cover - occ_max))
                    idx = int(np.argmin(dist))
            thr = thresholds[idx]
            mask = (gray <= thr) & valid
            if mask.sum() < 50:
                # Last-resort safety fallback.
                mask = (gray <= 0.5) & valid
            return mask


        def _farthest_point_sampling(points: np.ndarray, k: int) -> np.ndarray:
            n = points.shape[0]
            if k >= n:
                return points.copy()
            chosen = np.empty(k, dtype=int)
            chosen[0] = np.random.randint(n)
            d2 = np.sum((points - points[chosen[0]]) ** 2, axis=1)
            for i in range(1, k):
                idx = int(np.argmax(d2))
                chosen[i] = idx
                d2 = np.minimum(d2, np.sum((points - points[idx]) ** 2, axis=1))
            return points[chosen]


        def sample_image_shape(filename: str, num_points: int, scale: float = 1.0, shift=(0.0, 0.0)):
            img = plt.imread(DATA_DIR / filename)
            mask = _foreground_mask(img, occ_min=0.25, occ_max=0.50, occ_target=0.35)
            iy, ix = np.nonzero(mask)
            if len(ix) == 0:
                raise RuntimeError(f"No foreground detected in {filename}")
            # Jittered pixel samples inside black foreground.
            candidates = np.stack(
                [ix + np.random.rand(len(ix)), -(iy + np.random.rand(len(iy)))],
                axis=1,
            )
            # Oversample then FPS to obtain quasi-uniform cloud without grid artifacts.
            over = min(max(6 * num_points, num_points), candidates.shape[0])
            perm = np.random.permutation(candidates.shape[0])[:over]
            sampled = candidates[perm]
            pts = _farthest_point_sampling(sampled, num_points)
            pts -= pts.mean(axis=0, keepdims=True)
            pts /= np.max(np.linalg.norm(pts, axis=1)) + 1e-15
            pts = scale * pts + np.asarray(shift)[None, :]
            return pts


        SETTINGS = {
            "annulus-twodisks": ("annulus.png", "twodisks.png", 1.55, 1.55),
            "bunny-trefle": ("bunny.png", "trefle.jpg", 1.55, 1.55),
            "cross-heart": ("cross.jpg", "heart.jpg", 1.45, 1.45),
            "cat-annulus": ("cat.png", "annulus.png", 1.55, 1.55),
        }


        def sample_static_pair(num_points: int = 400, setting_name: str = "annulus-twodisks"):
            src, tgt, sx, sy = SETTINGS[setting_name]
            X = sample_image_shape(src, num_points, scale=sx, shift=(0.0, 0.0))
            Y = sample_image_shape(tgt, num_points, scale=sy, shift=(4.2, 0.0))
            return X, Y


        def solve_assignment_with_Q(X: np.ndarray, Y: np.ndarray, Q: np.ndarray):
            D = Y[None, :, :] - X[:, None, :]
            C = (
                Q[0, 0] * D[:, :, 0] * D[:, :, 0]
                + 2.0 * Q[0, 1] * D[:, :, 0] * D[:, :, 1]
                + Q[1, 1] * D[:, :, 1] * D[:, :, 1]
            )
            rows, cols = linear_sum_assignment(C)
            perm = np.empty(X.shape[0], dtype=int)
            perm[rows] = cols
            return perm, float(C[np.arange(X.shape[0]), perm].mean())


        def solve_static_coupling(X: np.ndarray, Y: np.ndarray, p):
            n = X.shape[0]

            if p == 1:
                Q = np.eye(2)
                perm, _ = solve_assignment_with_Q(X, Y, Q)
                D = Y[perm] - X
                S = (D.T @ D) / n
                cost = float(np.trace(S))
                return perm, cost

            if p == np.inf:
                # Heuristic restricted to permutations and rank-one cost matrices.
                q = np.array([1.0, 0.0], dtype=float)
                best_perm = None
                best_cost = np.inf
                for _ in range(40):
                    Q = np.outer(q, q)  # PSD, tr=1 rank-1
                    perm, _ = solve_assignment_with_Q(X, Y, Q)
                    D = Y[perm] - X
                    S = (D.T @ D) / n
                    vals, vecs = np.linalg.eigh(S)
                    q_new = vecs[:, np.argmax(vals)]
                    q_new /= np.linalg.norm(q_new) + 1e-15
                    cost = float(np.max(vals))
                    if cost < best_cost:
                        best_cost = cost
                        best_perm = perm.copy()
                    if np.linalg.norm(q_new - q) < 1e-10 or np.linalg.norm(q_new + q) < 1e-10:
                        break
                    q = q_new
                return best_perm, best_cost

            raise ValueError("Only p=1 and p=inf are supported.")


        def blue_red_color(t):
            t = float(np.clip(t, 0.0, 1.0))
            return (t, 0.0, 1.0 - t)


        def kde_density(points: np.ndarray, grid_x: np.ndarray, grid_y: np.ndarray, bandwidth: float = 0.15):
            gx = grid_x[:, None, None]
            gy = grid_y[None, :, None]
            px = points[:, 0][None, None, :]
            py = points[:, 1][None, None, :]
            d2 = (gx - px) ** 2 + (gy - py) ** 2
            K = np.exp(-0.5 * d2 / (bandwidth**2))
            dens = K.mean(axis=2) / (2.0 * np.pi * bandwidth**2)
            return dens


        def plot_quantized_density(ax, points: np.ndarray, color, extent, num_levels: int = 7):
            x_min, x_max, y_min, y_max = extent
            gx = np.linspace(x_min, x_max, 190)
            gy = np.linspace(y_min, y_max, 190)
            dens = kde_density(points, gx, gy)
            dens = dens / (dens.max() + 1e-15)
            levels = np.linspace(0.0, 1.0, num_levels + 1)
            cols = []
            for k in range(num_levels):
                # Flat quantized bands from white (lowest level) to pure target color (highest level).
                a = k / max(num_levels - 1, 1)
                cols.append(
                    (
                        (1.0 - a) + a * color[0],
                        (1.0 - a) + a * color[1],
                        (1.0 - a) + a * color[2],
                    )
                )
            ax.contourf(gx, gy, dens.T, levels=levels, colors=cols, antialiased=False)
            ax.contour(gx, gy, dens.T, levels=levels[1:-1], colors=[color], linewidths=0.50)
        """
    ),
    code(
        r"""
        tau = np.linspace(0.0, 1.0, 5)
        SETTING_NAME = "annulus-twodisks"

        X_pair, Y_pair = sample_static_pair(num_points=700, setting_name=SETTING_NAME)
        X_interp, Y_interp = sample_static_pair(num_points=1500, setting_name=SETTING_NAME)
        n_pair = len(X_pair)

        results_pair = {}
        results_interp = {}
        for p in [1, np.inf]:
            perm_pair, cost_pair = solve_static_coupling(X_pair, Y_pair, p)
            perm_interp, cost_interp = solve_static_coupling(X_interp, Y_interp, p)
            results_pair[p] = {"perm": perm_pair, "cost": cost_pair}
            results_interp[p] = {"perm": perm_interp, "cost": cost_interp}
            print(f"{SETTING_NAME} pair   p={p} cost={cost_pair:.6f}")
            print(f"{SETTING_NAME} interp p={p} cost={cost_interp:.6f}")
        """
    ),
    code(
        r"""
        all_pts_pair = np.concatenate([X_pair, Y_pair], axis=0)
        q_lo = np.quantile(all_pts_pair, 0.01, axis=0)
        q_hi = np.quantile(all_pts_pair, 0.99, axis=0)
        pad = 0.18
        x_min, y_min = q_lo - pad
        x_max, y_max = q_hi + pad
        extent_pair = (x_min, x_max, y_min, y_max)


        def save_pairing_panel(p, prefix=""):
            perm = results_pair[p]["perm"]
            cost = results_pair[p]["cost"]
            fig, ax = plt.subplots(figsize=(4.8, 4.8), constrained_layout=True)
            # Color convention aligned with interpolation panels: source blue, target red.
            ax.scatter(X_pair[:, 0], X_pair[:, 1], s=12, c="royalblue", alpha=0.78)
            ax.scatter(Y_pair[:, 0], Y_pair[:, 1], s=12, c="crimson", alpha=0.78)
            # Display only a sub-sampled set of matched pairs for readability.
            idx = np.linspace(0, n_pair - 1, 180).round().astype(int)
            for i in idx:
                seg = np.vstack([X_pair[i], Y_pair[perm[i]]])
                ax.plot(seg[:, 0], seg[:, 1], color="black", lw=0.55, alpha=0.45)
            tag = "inf" if p is np.inf else "1"
            ax.set_xlim(extent_pair[0], extent_pair[1])
            ax.set_ylim(extent_pair[2], extent_pair[3])
            ax.set_aspect("equal")
            ax.set_axis_off()
            out = FIG_DIR_STATIC / f"{prefix}static_pairing_p{tag}.pdf"
            fig.savefig(out, bbox_inches="tight", pad_inches=0.01)
            plt.show()
            print("Saved:", out.resolve())


        def horizontal_extent_single(points, y_extent, pad_x=0.30, q=0.9999):
            # Horizontal-only crop, shared vertical extent across all panels.
            c = points.mean(axis=0)
            rx = np.quantile(np.abs(points[:, 0] - c[0]), q) + pad_x
            return (c[0] - rx, c[0] + rx, y_extent[0], y_extent[1])


        def save_interp_panels(p, prefix=""):
            perm = results_interp[p]["perm"]
            tag = "inf" if p is np.inf else "1"
            # Shared vertical extent so panel heights preserve density geometry.
            all_pts = np.concatenate([X_interp, Y_interp], axis=0)
            cy = float(np.mean(all_pts[:, 1]))
            ry = float(np.quantile(np.abs(all_pts[:, 1] - cy), 0.9995) + 0.14)
            y_extent = (cy - ry, cy + ry)
            for k, t in enumerate(tau):
                Xt = (1.0 - t) * X_interp + t * Y_interp[perm]
                color = blue_red_color(float(t))
                ext = horizontal_extent_single(Xt, y_extent, pad_x=0.30, q=0.9997)
                fig, ax = plt.subplots(figsize=(2.0, 2.0), constrained_layout=True)
                plot_quantized_density(ax, Xt, color, ext, num_levels=7)
                ax.set_xlim(ext[0], ext[1])
                ax.set_ylim(ext[2], ext[3])
                ax.set_aspect("equal")
                ax.set_axis_off()
                out = FIG_DIR_DYN / f"{prefix}static_interp_p{tag}_t{k}.pdf"
                fig.savefig(out, bbox_inches="tight", pad_inches=0.0)
                plt.show()
                print("Saved:", out.resolve())


        for p in [1, np.inf]:
            save_pairing_panel(p)
            save_interp_panels(p)
        """
    ),
    code(
        r"""
        # Appendix variants: same code path, different image-defined shapes.
        for setting_name in ["bunny-trefle", "cross-heart", "cat-annulus"]:
            X_pair, Y_pair = sample_static_pair(num_points=600, setting_name=setting_name)
            X_interp, Y_interp = sample_static_pair(num_points=1200, setting_name=setting_name)
            n_pair = len(X_pair)
            results_pair = {}
            results_interp = {}
            for p in [1, np.inf]:
                perm_pair, cost_pair = solve_static_coupling(X_pair, Y_pair, p)
                perm_interp, cost_interp = solve_static_coupling(X_interp, Y_interp, p)
                results_pair[p] = {"perm": perm_pair, "cost": cost_pair}
                results_interp[p] = {"perm": perm_interp, "cost": cost_interp}
                print(f"{setting_name} pair p={p} cost={cost_pair:.6f}")
                save_pairing_panel(p, prefix=f"{setting_name}_")
                save_interp_panels(p, prefix=f"{setting_name}_")
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
