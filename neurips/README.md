# Manuscript

`paper.tex` is the full, non-anonymous preprint, including all appendices.
`paper.pdf` is its compiled rendering. The NeurIPS style is in `preprint`
mode, suitable for public circulation without implying conference acceptance.

## Build

From this directory, run `make` with a standard TeX installation providing
`latexmk`, pdfLaTeX, BibTeX, and `plainnat`. No shell escape is required.

Run `make arxiv` to create `arxiv-source.tar.gz`. This includes the actual
local inputs recorded during compilation, the generated bibliography
`paper.bbl`, and `references.bib`. The main source is `paper.tex`; no draft,
review, rebuttal, notebook, or compiled manuscript PDF is included.
The packaging script requires Python 3.9 or newer.

The archive is a source bundle, not an arXiv submission. Author metadata,
abstract, subject categories, and license must still be selected at upload.

## Revision and Verification

- `../modifications.md` records the changes and checks for the finalization pass.
- `bibliography-audit.md` documents the primary-source check of every reference.
- Appendix G records the experimental protocols and limitations. The Gaussian
  modal figures were regenerated after correcting their ODE implementation;
  the neural-network experiments were not rerun for this editorial pass.
- `../python/mlp/validate_initialization.py` independently reproduces the
  initialization and clipping diagnostics from the MLP notebook.
- `../python/gaussians/validate_gaussians.py` checks the modal vector fields,
  invariant leaves, and short integrations; `--trajectories` checks all
  published Gaussian trajectories at their full horizon.

The mathematical scope remains explicit: the flow theorem verifies regular
solutions, not global PDE existence or particle-limit convergence. Finite
Newton--Schulz steps have a convex-dissipation interpretation on a controlled
spectral region, not the homogeneous fixed-metric interpretation of exact
Muon. Numerical time-normalized plots are not runtime comparisons.
