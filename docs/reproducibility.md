# Reproducing the Figures

Install the experiment environment from the repository root:

```bash
python -m pip install -r requirements.txt
python scripts/reproduce.py --list
python scripts/reproduce.py --check
```

Run a fast pipeline check, then a full experiment:

```bash
python scripts/reproduce.py mmd --smoke --output outputs/mmd-smoke
python scripts/reproduce.py mmd --output outputs/mmd-full
```

`--all` selects all six paper experiments; `--examples` selects the four small
teaching notebooks. Full attention and MLP training can be expensive.
`--timeout` specifies the per-cell timeout in seconds (default 3600).
Smoke runs reduce counts or horizons and **do not reproduce the paper's
scientific results**. Changed parameters are listed in `run.json` and the
executed notebook is prominently marked as a smoke test.

## Outputs and Provenance

The runner copies the selected notebook, generator, and required image data
into a fresh output directory. It uses a private Jupyter kernel running the
same Python interpreter as the runner. This needs local loopback ports, but
does not start a public server or download data. It executes code with
[NBClient](https://nbclient.readthedocs.io/en/latest/client.html).

For example, an MMD run produces:

```text
outputs/mmd-full/mmd/
  run.json
  python/mmd/mmd_flow.ipynb
  python/mmd/generate_mmd_notebook.py
  neurips/figures/fig-mmd/*.pdf
```

The executed notebook includes plots and outputs. `run.json` records package
versions, interpreter version, Git revision and dirty state, source/generator
and toolbox hashes, input-image hashes, smoke overrides, elapsed time, status,
and PDF artifacts. The kernel sets OpenMP/MKL thread counts to one.
Errors propagate; the partial notebook and failure report are retained.
The runner refuses to overwrite an existing run directory.
Seeds are fixed in each experiment. BLAS, hardware, solver, and PyTorch version
differences can affect results; this is not a bitwise reproducibility claim.

The tracked manuscript figures are **never overwritten by the runner**.
After reviewing a full run, its PDF files can be promoted to the corresponding
`neurips/figures/` subdirectory. Opening and executing a paper notebook directly
from its original directory retains the legacy behavior of writing there.

## Experiment Map

| Name | Notebook | Generated assets |
| --- | --- | --- |
| `static` | `python/static/static_couplings.ipynb` | 48 matching/interpolation PDFs in `fig-static` and `fig-dynamics` |
| `mmd` | `python/mmd/mmd_flow.ipynb` | 4 trajectory/decay PDFs in `fig-mmd` |
| `gaussians` | `python/gaussians/gaussian_closed_form.ipynb` | 6 covariance/leaf PDFs in `fig-gaussians` |
| `gaussian-kl` | `python/gaussians-kl-flow/gaussian-kl-flow.ipynb` | 4 covariance-gallery PDFs beside the notebook |
| `mlp` | `python/mlp/mlp_spectral_flow_relu.ipynb` | 4 regression/trajectory PDFs in `fig-mlp` |
| `attention` | `python/attention/attention_spectral_flow.ipynb` | 4 attention PDFs and a statistics JSON in `fig-attention` |

The Gaussian KL notebook is an additional illustration, not a main-body paper
figure. The other experiments have plain-Python notebook generators.
`--check` validates their agreement with the checked-in notebooks (and also
checks the teaching-notebook generator), ignoring
execution outputs and cell IDs. Regenerate a notebook after editing its
generator; do not edit the two sources independently.

`python/_generate_repo_assets.py` is a legacy preview generator for the README's
three-geometry illustrations. Those previews are not the two-geometry paper
panels. It no longer writes obsolete notebooks or a nonexistent `paper/` tree.

## Numerical Qualifications

- The operator matching illustration alternates assignments and rank-one cost
  matrices; it is a heuristic with no optimality certificate. Its interpolants
  need not be spectral Wasserstein geodesics. Use the toolbox's full-coupling
  conic solver for small examples.
- The MMD loss uses smoothed distance with `epsilon=0.01`.
- MLP and attention use full-matrix step caps and coordinate guards. Their
  displayed normalized times are not intrinsic flow times or runtime comparisons.
- The neural-network/MMD notebooks differentiate the empirical objective in
  particle coordinates and apply a matrix LMO. The mean-field clock carries
  the particle-count factor explained in `toolbox.md`.
- Current neural-network selectors use the tested canonical rank-support
  selector and fail on invalid forces/SVD errors. Earlier archived figures
  used notebook-local selectors with different singular-value cutoffs and,
  for the MLP, silent fallback rules. Full reruns may therefore differ near
  degeneracy; the stored figures are not silently replaced by this code pass.
- Gaussian modal RK4 clips negative numerical variances to zero and keeps
  extinct modes at zero. Interior invariants stop applying after rank loss.
- The legacy Gaussian KL gallery uses regularized spectral inverses, SPD
  projection, and operator-flow time reparametrization. Its galleries sample
  covariance arclength, not equal elapsed time. The new small Gaussian example
  instead uses the toolbox's unregularized force-factor formula on SPD states.

Additional checks from the repository root:

```bash
python python/mlp/validate_initialization.py
python python/gaussians/validate_gaussians.py
python python/gaussians/validate_rank_events.py
```

The rank-event validator performs local refinement near events, not a certified
global trajectory error bound. The mathematical audit is in `audit-maths.md`.
