# Notebooks and Numerical Experiments

This directory contains the Jupyter notebooks used to generate the numerical
figures for the Spectral Wasserstein paper. Each experiment is organized in its
own subdirectory and, when relevant, has a small generator script that writes the
notebook in a reproducible form.

The reusable computational toolbox is in [`../src/muon_dynamics/`](../src/muon_dynamics/),
separate from these experiments. See the [API and conventions](../docs/toolbox.md)
and the [figure-reproduction guide](../docs/reproducibility.md).

## Small Examples

Start with [`examples/`](examples/) for short notebooks using the public API:

1. [Spectral directions](examples/01_spectral_directions.ipynb): norms, LMOs, weights, and endpoint behavior.
2. [Particle MMD](examples/02_particle_mmd.ipynb): a small deterministic particle flow.
3. [Static transport](examples/03_static_transport.ipynb): full convex couplings and mass splitting.
4. [Gaussian KL](examples/04_gaussian_kl.ipynb): covariance ODEs and dissipation checks.

Execute all four with `python scripts/reproduce.py --examples` from the repository
root after installing `pip install -e '.[notebooks,transport]'`.

## `static/`

Static Spectral Wasserstein couplings between two planar point clouds. The
notebook compares the trace endpoint `p=1`, which recovers the usual quadratic
optimal transport assignment, and the operator endpoint `p=inf`, which uses a
spectral cost on the displacement second moment. The operator matching is a
permutation heuristic, not a certified optimum. It generates the pairing figures
and displacement-interpolation density snapshots.

Main files:

- `static_couplings.ipynb`
- `generate_static_notebook.py`

## `mmd/`

Particle gradient flows minimizing an MMD loss with the energy-distance kernel.
The same objective is evolved under the trace geometry and the operator
geometry, making visible how the metric changes the collective trajectories of
the particles.

Main files:

- `mmd_flow.ipynb`
- `generate_mmd_notebook.py`

## `mlp/`

Mean-field training of a two-layer ReLU network in two input dimensions. The
experiment compares the trace flow and the Muon-type operator flow on a
teacher-student regression problem. It visualizes energy decay, angular
redistribution of neurons, and reduced parameter-space trajectories.

Main files:

- `mlp_spectral_flow_relu.ipynb`
- `generate_mlp_spectral_flow_relu_notebook.py`

## `gaussians/`

Closed-form Gaussian reductions for linear two-layer models. These notebooks
visualize the reduced ODEs in covariance coordinates, interior conserved leaves
for different Schatten geometries, and rank-one/rank-two target dynamics.
After covariance rank loss, the numerical continuation keeps extinct
eigenvalues at zero; the interior invariants no longer apply.

Main files:

- `gaussian_closed_form.ipynb`
- `generate_gaussians_notebook.py`
- `validate_gaussians.py`: checks the notebook vector field, interior invariants,
  full-matrix covariance LMOs (including singular states), and Gaussian entropy
  dissipation identities.
- `validate_rank_events.py`: independent event-aware reference integration and
  local step-size refinement across rank-loss and zero-error events.

Run the validators from the repository root with
`python python/gaussians/validate_gaussians.py` and
`python python/gaussians/validate_rank_events.py`. Neither command regenerates
plots or runs neural-network training. Event-window checks are not certified
global discretization error bounds.

## `gaussians-kl-flow/`

Centered Gaussian covariance flows for the KL functional under spectral
Wasserstein geometries. The notebook visualizes covariance ellipses sampled by
arclength along the covariance trajectory.

Main files:

- `gaussian-kl-flow.ipynb`

## `attention/`

Mean-field shallow multi-head attention. A head is a particle
`x=(Q,K,V,O)`, and the empirical measure over heads implements a multi-head
attention block. The notebook compares `p=1` and `p=inf` flows for fitting a
random five-head teacher with a 200-head student across two query/key
temperatures (`very_dense` and `very_sparse`).

The implementation is vectorized in PyTorch over data, heads, query tokens, and
key tokens using batched tensor contractions. The exported PDFs include separate
energy-decay plots for dense and sparse attention, together with stacked
histograms of the teacher attention values.

Each setting uses 5 paired trials that redraw both teacher and student, and curves are shown
without summary overlays (no median curve).

Main files:

- `attention_spectral_flow.ipynb`
- `generate_attention_notebook.py`

## Re-running

Install the numerical dependencies from the repository root with:

```bash
python -m pip install -r requirements.txt
```

The recommended runner regenerates and executes notebooks in isolated output
directories, with version and source-hash records. For example:

```bash
python scripts/reproduce.py --check
python scripts/reproduce.py mmd --smoke --output outputs/mmd-check
python scripts/reproduce.py mmd --output outputs/mmd-full
```

Smoke outputs are pipeline checks, not the published experiments. Full MLP and
attention runs are substantially more expensive. The runner writes a mirrored
`neurips/figures/fig-*` tree under the selected output directory; it never
overwrites tracked manuscript figures. Direct execution of an original paper
notebook still writes to its legacy figure paths.
