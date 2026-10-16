# Manuscript

`paper.tex` is the NeurIPS 2026 camera-ready working version, including all
appendices and the mandatory paper checklist. `paper.pdf` is its compiled
rendering. It uses the official `neurips_2026` style with `[main,final]`.
The content ends on page 10; acknowledgements and funding begin on page 11.

The manuscript includes funding and competing-interests disclosures and a
completed checklist. The original toolbox code is MIT-licensed; the checklist
records unverified permissions for some legacy illustrations and missing
historical compute records. Building or packaging the manuscript does not
submit it to a publication service.

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
It packages the selected manuscript style, now the accepted-paper `final`
version. The historical `../arxiv/` copy is not modified by this build.

## Official Style Provenance

The style was checked byte-for-byte against the official NeurIPS 2026 kit
downloaded on 2026-10-16:
https://media.neurips.cc/Conferences/NeurIPS2026/Formatting_Instructions_For_NeurIPS_2026.zip
The checklist retains that kit's questions and guidelines, with the initial
instruction block removed and manuscript-specific answers supplied.
Requirements: https://neurips.cc/Conferences/2026/MainTrackHandbook

## Reproducibility and Scope

- Appendix G records the experimental protocols and limitations. The Gaussian
  modal figures were regenerated after correcting their ODE implementation;
  the neural-network experiments were not rerun for this editorial pass.
- Main figures retain trajectory panels, with compact single-row loss,
  histogram, and Gaussian diagnostics in the appendix. The archived numerical
  results are unchanged; one legacy PDF legend is corrected by a tested helper.
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
