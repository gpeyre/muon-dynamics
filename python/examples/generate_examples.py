"""Generate short, deterministic notebooks using the installed toolbox."""

from pathlib import Path
from textwrap import dedent

import nbformat as nbf

ROOT = Path(__file__).resolve().parent
SETUP = """
import numpy as np
import matplotlib.pyplot as plt
import muon_dynamics as md

plt.rcParams.update({"figure.dpi": 120, "axes.spines.top": False,
                     "axes.spines.right": False, "font.size": 11})
"""
INSTALL = """
Run from an environment with `pip install -e '.[notebooks,transport]'` from
the repository root. In Colab, first run
`%pip install 'muon-dynamics[notebooks,transport] @ git+https://github.com/gpeyre/muon-dynamics.git'`.
All particle arrays have particles in rows. No training data are downloaded.
"""

NOTEBOOKS = {
    "01_spectral_directions": [
        ("markdown", r"""
        # Spectral descent in a few lines

        The penalized LMO minimizes $\langle G,V\rangle+\|V\|_{S_{2p}}^2/2$.
        At $p=1$ it is $-G$; at $p=\infty$ it is the negative polar factor
        multiplied by $\|G\|_*$, not just the polar factor.
        """ + INSTALL),
        ("code", SETUP),
        ("code", """
        G = np.diag([4., 1., .2])
        ps = [0.5, 1, 2, np.inf]
        velocities = [md.schatten_lmo(G, p) for p in ps]
        for p, V in zip(ps, velocities):
            action = md.schatten_norm(V, 2*p)**2
            np.testing.assert_allclose(np.sum(G*V), -action)
            print(f"p={p:g}: dissipation = {action:.4f}")
        """),
        ("code", """
        fig, ax = plt.subplots(figsize=(7, 3.5), constrained_layout=True)
        for j, (p, V) in enumerate(zip(ps, velocities)):
            ax.bar(np.arange(3) + .18*j, -np.diag(V), width=.17, label=f"p={p:g}")
        ax.set(xticks=np.arange(3)+.27, xticklabels=["4", "1", "0.2"],
               xlabel="Force singular value", ylabel="Descent singular value")
        ax.set_ylim(0, 6.5)
        ax.legend(ncol=4)
        fig.savefig("01_spectral_directions.png", dpi=130)
        plt.show()
        """),
        ("markdown", r"""
        ## From matrices to measures

        `particle_lmo(g, p, weights)` takes the spatial force $g(x_i)$.
        If automatic differentiation returns $\nabla_{x_i}F$, divide it by
        the particle weight first. For uniform weights this is a factor $n$.
        `block_lmo(G, [d1, d2], p)` instead normalizes two parameter blocks
        independently, with one dual-norm scale per block.
        """),
        ("code", """
        weights = np.array([.2, .3, .5])
        V = md.particle_lmo(G, np.inf, weights)
        np.testing.assert_allclose(np.sum(weights[:, None]*G*V),
                                   -md.velocity_norm(V, np.inf, weights)**2)
        print("Weighted dissipation identity verified.")
        """),
    ],
    "02_particle_mmd": [
        ("markdown", r"""
        # A small MMD particle flow

        Compare three geometries for the same smoothed energy-distance
        objective. `mmd_force` returns the mean-field force, already scaled
        for use with `particle_lmo`. These are small explicit Euler examples,
        not calibrated speed comparisons or the paper's full experiments.
        Blue points are the target, red points the final particles, and gray
        lines their trajectories. The three spatial panels share axis limits.
        """ + INSTALL),
        ("code", SETUP),
        ("code", """
        rng = np.random.default_rng(7)
        source = rng.normal(size=(32, 2)) * [.7, .3] + [1.8, 1.]
        target = np.r_[rng.normal(size=(24, 2))*.25 + [-1, .7],
                       rng.normal(size=(24, 2))*.3 + [1, -.7]]
        dt, steps = .025, 160
        histories, energies = {}, {}
        for p in [1, 2, np.inf]:
            x = source.copy()
            history, energy = [x.copy()], [md.mmd_energy(x, target)]
            for _ in range(steps):
                velocity = md.particle_lmo(md.mmd_force(x, target), p)
                x = x + dt*velocity
                history.append(x.copy())
                energy.append(md.mmd_energy(x, target))
            histories[p], energies[p] = np.array(history), np.array(energy)
            assert energy[-1] < energy[0]
        """),
        ("code", """
        fig, axes = plt.subplots(1, 4, figsize=(12, 3), constrained_layout=True)
        all_points = np.concatenate([target] + [h.reshape(-1, 2) for h in histories.values()])
        lower, upper = all_points.min(axis=0)-.2, all_points.max(axis=0)+.2
        for ax, p in zip(axes, histories):
            h = histories[p]
            ax.scatter(*target.T, s=12, color="royalblue", alpha=.3)
            ax.plot(h[:, :, 0], h[:, :, 1], color="black", lw=.6, alpha=.35)
            ax.scatter(*h[-1].T, s=12, color="crimson")
            ax.set(title=f"p={p:g}", aspect="equal",
                   xlim=(lower[0], upper[0]), ylim=(lower[1], upper[1]))
            axes[-1].semilogy(np.arange(steps+1)*dt, energies[p], label=f"p={p:g}")
        axes[-1].set(xlabel="Euler time", ylabel="Squared MMD")
        axes[-1].legend()
        fig.savefig("02_particle_mmd.png", dpi=130)
        plt.show()
        """),
    ],
    "03_static_transport": [
        ("markdown", r"""
        # Spectral transport can split mass

        Two horizontal source points are transported to two vertical target
        points. Every matching has operator cost $2$; the uniform coupling
        has displacement moment $I$ and operator cost $1$. This illustrates
        why permutation heuristics need not solve spectral OT.

        `solve_transport` solves the full convex coupling problem for
        $p\in\{1,2,\infty\}$. Its cost is the **squared** distance. Conic
        results are numerical optima, not exact primal-dual certificates.
        """ + INSTALL),
        ("code", SETUP),
        ("code", """
        x = np.array([[-1., 0.], [1., 0.]])
        y = np.array([[0., -1.], [0., 1.]])
        results = [md.solve_transport(x, y, p) for p in [1, 2, np.inf]]
        np.testing.assert_allclose([r.squared_cost for r in results], [2, np.sqrt(2), 1], atol=1e-5)
        for p, result in zip([1, 2, np.inf], results):
            print(f"p={p:g}: cost={result.squared_cost:.6f}, "
                  f"marginal error={result.marginal_error:.2e}, solver={result.solver}")
        """),
        ("code", """
        fig, axes = plt.subplots(1, 3, figsize=(8, 3), constrained_layout=True)
        for ax, p, result in zip(axes, [1, 2, np.inf], results):
            for i in range(2):
                for j in range(2):
                    ax.plot([x[i, 0], y[j, 0]], [x[i, 1], y[j, 1]],
                            color="gray", lw=8*max(result.plan[i, j], 0))
            ax.scatter(*x.T, s=55, color="crimson", label="Source")
            ax.scatter(*y.T, s=55, color="royalblue", label="Target")
            ax.set(title=f"p={p:g}; cost={result.squared_cost:.3f}", aspect="equal",
                   xlim=(-1.3, 1.3), ylim=(-1.3, 1.3))
        axes[0].legend(fontsize=8)
        fig.savefig("03_static_transport.png", dpi=130)
        plt.show()
        """),
    ],
    "04_gaussian_kl": [
        ("markdown", r"""
        # Gaussian KL flows on covariance matrices

        For centered Gaussians, the entropy force is affine:
        $g(x)=(\bar\Sigma^{-1}-\Sigma^{-1})x$. The toolbox evaluates the
        covariance ODE with a square-root factor, without inverting the
        force covariance. The state covariance must remain positive definite.

        We use SciPy's adaptive ODE solver for a short interval and check
        positivity and decay at sampled times. These checks do not certify
        global existence or positivity between samples.

        This first example uses isotropic covariances, avoiding nonsmooth
        force-rank changes. Here $\Sigma_t=s(t)I$ and the exact equation is
        $s'=-2d^{1-1/p}(s-1)$. Different rates along this particular path
        do not imply different optimal Gaussian Poincare constants.
        """ + INSTALL),
        ("code", SETUP + "\nfrom scipy.integrate import solve_ivp\n"),
        ("code", """
        initial = 2*np.eye(2)
        target = np.eye(2)
        times = np.linspace(0, 1.5, 90)
        solutions = {}
        for p in [1, 2, np.inf]:
            def rhs(t, flat):
                S = flat.reshape(2, 2)
                return md.gaussian_kl_rhs((S+S.T)/2, target, p).ravel()
            sol = solve_ivp(rhs, (0, times[-1]), initial.ravel(), t_eval=times,
                            rtol=1e-7, atol=1e-9, max_step=.02)
            assert sol.success, sol.message
            covariances = sol.y.T.reshape(-1, 2, 2)
            assert np.linalg.eigvalsh(covariances).min() > 0
            energy = np.array([md.gaussian_kl(S, target) for S in covariances])
            assert np.max(np.diff(energy)) < 1e-7
            rate = 2 * 2**(1 - (0 if np.isinf(p) else 1/p))
            np.testing.assert_allclose(covariances[:, 0, 0], 1+np.exp(-rate*times), atol=2e-7)
            solutions[p] = covariances, energy
        """),
        ("code", """
        fig, axes = plt.subplots(1, 2, figsize=(8, 3.2), constrained_layout=True)
        for p, (covariances, energy) in solutions.items():
            axes[0].plot(times, covariances[:, 0, 0], label=f"p={p:g}")
            axes[1].semilogy(times, energy, label=f"p={p:g}")
        axes[0].axhline(1, linestyle=":", color="black", label="Target")
        axes[0].set(xlabel="ODE time", ylabel="Isotropic covariance")
        axes[1].set(xlabel="ODE time", ylabel="Gaussian KL")
        axes[0].legend()
        axes[1].legend()
        fig.savefig("04_gaussian_kl.png", dpi=130)
        plt.show()
        """),
    ],
}


def main():
    for name, definitions in NOTEBOOKS.items():
        cells = []
        for index, (kind, source) in enumerate(definitions):
            factory = nbf.v4.new_code_cell if kind == "code" else nbf.v4.new_markdown_cell
            if source.endswith(INSTALL):
                source = dedent(source[:-len(INSTALL)]) + INSTALL
            cells.append(factory(dedent(source).strip() + "\n", id=f"cell-{index:02}"))
        nb = nbf.v4.new_notebook(cells=cells, metadata={
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        })
        nbf.validate(nb)
        nbf.write(nb, ROOT / f"{name}.ipynb")
        print(f"Wrote {name}.ipynb")


if __name__ == "__main__":
    main()
