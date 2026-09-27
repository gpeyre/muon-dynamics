# Finalization After Review: 2026-09-27

This pass prepares `neurips/` as a complete, non-anonymous preprint. It uses
the submitted `reviews/original.pdf`, all three reviews, the final rebuttal,
and the subsequent mathematical discussions. The historical polishing log
below is retained; its old page count and verification statements describe
that earlier version, not this release.

## Review Integration

| Reviewer concern | Change in the manuscript |
| --- | --- |
| awfw: finite-width Muon versus the measure theorem | The start of Section 5 distinguishes the exact empirical ODE/PDE identity from the conditional maximal-slope theorem. The introduction explains the three construction steps and the scope of the idealized model. |
| awfw: what the measure view adds | Explains the width-independent formulation, Gaussian moment closure, and possible convergence criteria, without claiming a proved particle limit or global PDE well-posedness. |
| awfw / CQiK: flattened versus independently normalized blocks | States the actual particle-matrix layouts in the examples. Proves separation of the action/LMO under the block gauge and distinguishes it from independence of the measure's marginals. |
| CQiK: LMO terminology | Acknowledges the terminology convention at first use and derives the squared-norm oracle from a classical unit-ball LMO followed by scalar optimization. Distinguishes trace-scaled and unscaled polar clocks. |
| CQiK: opaque measure-LMO proof | Supplies a complete compact operator-projection proof in the main text, with existence by coercivity and explicit treatment of a zero force covariance. |
| CQiK: rotation and figure interpretation | Explains simultaneous orthogonal invariance of Schatten transport. Adds a modest covariance-whitening explanation of the MMD transient and qualifies the numerical operator couplings as heuristic. |
| CQiK: hand-picked time scales; follow-up on smoothness | Replaces the asserted small-time calibration by the actual nominal horizons and clipping rules. Adds a precise primal/dual Lipschitz-gradient constant, a descent bound, and the fixed-dimension rank comparison. |
| CQiK: dense Gaussian discussion | Moves the modal details and Gaussian figure to Appendix F; retains only the Gaussian-closure motivation in the main text. |
| CQiK: Kantorovich dual | Adds the potential formulation after the robust-cost theorem, with proof and allowance for singular quadratic costs. |
| JwJP: explicit regularity assumptions | Replaces “sufficiently smooth/regular” by a finite-interval verification theorem with a uniform quadratic transport remainder. Proves both slope bounds, the characteristic chain rule, metric speed, and the energy identity. Gives a concrete moment-functional class. |
| JwJP: singular inverse-trace selectors | Retains the singular-safe finite-dimensional LMO as the primary construction. States Borel measurability and gives a rank-change discontinuity example. Corrects the suggestion that the inverse-trace optimizer is necessarily singular at the operator endpoint. |
| JwJP: practical optimizer variants | Appendix B now separates fixed-scale Newton--Schulz dissipation, phase-space momentum, minibatch bias, independent Brownian-noise surrogates, and exact blockwise normalization. |

## Mathematical Corrections and Boundaries

- The flow theorem needs no density or invertible force covariance. Its
  transport expansion controls all sufficiently small couplings, including
  nondeterministic perturbations of atomic measures. It verifies an existing
  regular solution; it is not an existence/uniqueness theorem. Smooth features
  alone, or a finite dataset, do not imply its global growth bounds.
- Fixed-scale finite Newton--Schulz is **not** an exact LMO for a fixed
  squared-norm metric, even on its stable region. This corrects an overstatement
  in the historical rebuttal. Added a positive replacement result: convexity
  of the dual spectral dissipation on the stable force ball and a global
  convex extension, with its Fenchel-conjugate velocity dissipation. The
  force-side polynomial must not be substituted for the primal gauge.
- The full-rank operator inverse-trace minimizer is
  `Q = sqrt(S_g) / tr(sqrt(S_g))`, not a rank-one matrix. Rank-one static
  cost certificates and infinitesimal dual selectors are different objects.
- The two smoothness constants obey `L_1 <= L_infinity <= min(n,d) L_1`
  under the same unscaled normalization and on the same region. Thus there
  is still a factor bounded by `d` at infinite width when particle dimension
  is fixed. This is not an ordering of iteration complexity or observed loss
  curves, and does not assert Lipschitz continuity of the Muon velocity.
- The averaged noisy-force closure has expectation outside the nonlinear
  LMO and no automatic Laplacian at fixed-variance fast resampling. Separate
  Brownian noise after normalization gives a Laplacian, but generally not the
  same entropy-penalized spectral gradient flow. No impossibility claim for
  every conceivable alternative energy is made.
- Strengthened the P-L convergence hypotheses with finite initial energy
  and absolute continuity. The transfer proof now uses metric comparison
  directly and does not silently assume smoothness of the functional.
- Specified the weighted Sobolev domain for spectral Poincare inequalities.
  Distinguished the rigorous dual-norm perturbation expansion from an
  additional identification with the nonlinear entropy metric slope.
- Added the scalar exception to the root-norm Schatten threshold: the
  threshold `p >= 1/2` is substantive only in dimension at least two.
- Made the Gaussian ansatz and Gaussian KL statements conditional on the
  selected moment dynamics, without asserting uniqueness through rank
  changes. Kept the canonical selector explicit.
- Standardized the linear-network layer dimension as `m` and total particle
  dimension as `d = 2m`; allowed balanced diagonal, not only isotropic,
  initialization in the modal reduction. Updated the notation tables.
- Clarified that the energy-distance kernel is conditionally positive
  definite on zero-mass measures; anchoring gives the equivalent RKHS form.
- Removed the unverified attribution of the exact spherical WFR action to
  Chizat--Bach and cited the primary unbalanced-transport formulations.

## Numerical Corrections and Transparency

- Added `python/mlp/validate_initialization.py`, which extracts initialization
  and update arithmetic from the actual notebook using JSON/AST and never
  runs training. Verified the ideal initial dissipation ratio `2.55765` and
  the fact that **both initial updates are clipped**. The clipped linearized
  per-display-step decrease ratio is `0.92334`. Neither number is used to
  relabel the archived trajectories as calibrated continuum times.
- Corrected the Gaussian simulation's missing `psi_q(error)` exponent and
  extra factors of two, as well as variable shadowing in the finite-p
  invariant helper. Regenerated its notebook and figure outputs; checks are
  recorded in the verification subsection below.
- Corrected the MLP teacher-angle description and the attention notebook's
  misleading factor-two timing description, preserving their configured
  experiments. The attention runs redraw both teacher and student.
- Added an experimental-protocol table, parameter guards, the attention
  histogram truncation, and the distinction between nominal and effective
  clocks. MLP, attention, MMD, and static experiments were not rerun.
- Explicitly identifies the operator static solver as a rank-one alternating
  heuristic without a primal-dual certificate. Its interpolations are not
  claimed to be certified optimal geodesics.

## Bibliography and Release Preparation

- Audited all 36 pre-existing bibliography entries, including uncited ones,
  against primary publisher, proceedings, arXiv, or author records. None was
  found to be a fabricated work. `neurips/bibliography-audit.md` records each
  source, metadata correction, and distinction between a factual error and
  a version/name update.
- Added verified references for signSGD failure examples and classical
  diffusion/Poincare/log-Sobolev theory. Corrected publication metadata and
  added verified persistent links.
- Switched the manuscript from anonymous submission mode to `preprint`,
  restored the existing author acknowledgments/funding, and enabled PDF
  hyperlinks and metadata. This does not imply conference acceptance.
- Added `neurips/Makefile`, `neurips/README.md`, and
  `neurips/prepare_arxiv.py` for reproducible compilation and a source-only
  archive of the actual local LaTeX dependencies, including `paper.bbl`.
  The archive excludes review/rebuttal material and working drafts. Generated
  verification files and the submission archive are ignored by Git; the
  sources, build instructions, and audit remain available for versioning.
- Historical review responses and unrelated drafts were not rewritten;
  where a rebuttal promise was mathematically too strong, the manuscript
  and this log state the corrected scope explicitly.

## Final Verification

- Built the final `neurips/paper.pdf`: **55 pages**, non-anonymous preprint
  mode, live hyperlinks and author metadata. The final LaTeX log has no
  warnings, unresolved citations/references, duplicate destinations, or
  overfull/underfull boxes. `git diff --check` passes.
- Rendered all 55 pages at 105 dpi and inspected all contact sheets, with
  detailed checks of the main flow theorem, Newton--Schulz proposition,
  Gaussian figure, protocol table, and notation tables. No clipping or
  overlapping elements were found.
- `make arxiv` produced `neurips/arxiv-source.tar.gz` with **65 files**:
  manuscript/notation sources, local style, `.bib`, `.bbl`, and 60 used
  figure PDFs. Verified that every archive member matches the current file
  and that no review, draft, or compiled manuscript PDF is present.
- Extracted the archive into a clean directory and built it independently
  with shell escape disabled. It produced 55 pages with identical extracted
  text and a clean final log. This verifies the local source bundle, not
  acceptance by or submission to arXiv.
- BibTeX processed all **38** entries with `plainnat` without warnings. The
  manuscript has 33 cited keys and no missing entry; the five uncited entries
  were also audited. Every entry has a verified URL, and 23 have verified
  DOI fields. The audit explicitly records access limits and the withheld,
  unverified optional Sion DOI.
- Re-ran the MLP initialization validator after the metadata correction:
  ideal dissipation ratio `2.55764654765836`, clipped linearized per-step
  ratio `0.92333571858905`, both coordinate guards initially inactive.
- The Gaussian validator matches the analytical RHS to less than
  `3.6e-15`; root residuals and invariant derivatives are below `9e-16`.
  All 24 full-horizon trajectories passed finite-value and PSD checks,
  with maximum scaled interior invariant drift below `7.8e-6`.
  These checks use float64 RK4, `T=18`, `dt=0.0002`, and stop each invariant
  check before its mode approaches the boundary (`s_i-|r_i| <= 0.001`).
  All six Gaussian PDFs were regenerated and visually checked.
- Python compilation checks pass for the archive builder and both new
  validators. No neural-network retraining, timing benchmark, particle-limit
  test, remote submission, commit, or push was performed.

Final PDF SHA-256:
`2ad450d5d461c30d4fca620f1750a7012fe4f6a8c0b654772e8f157fba277eed`.

---

# Historical Global Manuscript Polishing Pass

This file records the global mathematical, notational, editorial, and layout review of the NeurIPS manuscript in `neurips/`.

## Mathematical corrections and clarifications

- Corrected both proofs of the static/dynamic equivalence. The Eulerian velocity induced by a coupling is the conditional mean displacement, and the reverse estimate now follows explicitly from conditional Jensen and monotonicity of the gauge.
- Defined the tangent norm as a quotient over velocity representatives. The Measure-LMO selector is now proved to be minimal in its tangent class, and the steepest-descent statement follows from norm duality rather than an informal Riesz argument.
- Clarified the relation between the finite-dimensional matrix LMO, the Measure-LMO, and the Muon update. In particular, the rank-one static certificate at the operator-norm endpoint is no longer conflated with the infinitesimal Muon selector.
- Completed the Schatten endpoint conventions and separated the two conjugate exponents used in the paper: `p'` for matrix-gauge support representations and `q=(2p)'` for tangent/Dirichlet duality.
- Strengthened the norm-extension and PSD support-representation arguments, including the nondegeneracy proof and the passage from the ambient symmetric space to the PSD cone.
- Repaired the Gaussian modal formulas and endpoint conventions, distinguished the closed covariance cone from its positive-definite interior, and stated Gaussian preservation for the canonical affine Measure-LMO selection.
- Corrected the Gaussian relative-entropy flow. The exact intrinsic covariance ODE is now stated first; its simpler symmetrized form is restricted to the commuting case. Singular force covariances use an explicit pseudoinverse/range convention.
- Made the large-mean asymptotics quantitative enough to identify the limiting rank-one optimizer and proved the needed continuity of the projected transport correction.
- Corrected the Monge-map discussion. The nonmonotone weighted entrywise example is now justified by explicit PSD matrices, and the conditional Brenier argument uses the saddle inequalities to show that every primal optimizer is optimal for the selected quadratic cost.
- Supplied a pinching argument for the commuting-Gaussian reduction and made the common-eigenbasis and `p=\infty` conventions explicit.
- Distinguished full geodesic convexity from convexity along static displacement geodesics. A branching constant-speed geodesic for the Muon/operator metric shows that convex potentials need not be convex along every spectral geodesic. The linear, interaction, and entropy results are now scoped accordingly.
- Strengthened the uniformly elliptic entropy result by proving that equality in the positive-definite Jensen step forces every constant-speed geodesic to be a displacement geodesic. The degenerate case is stated only as a selected-geodesic result.
- Corrected the finite Newton--Schulz discussion: truncated polynomial maps are no longer presented as exact LMOs or as automatically defining Spectral Wasserstein metrics.
- Recast momentum directly through the phase-space Measure-LMO, which remains meaningful at `p=\infty`; the inverse-trace formula is now only an optional representation when its attainment and invertibility assumptions hold.
- Clarified the root-norm characterization as a compatible family over Hilbert targets and repaired the Benamou--Brenier proof using conditional-expectation contraction.
- Corrected the positively two-homogeneous projection at the origin and expanded the weak derivation of the projected continuity--reaction equation.
- Checked and polished the P-L and Poincare appendix: scaling under gauge normalization, transfer from `W_2`, the robust anisotropic representation, the Gaussian equality result, and the strict generalized-Gaussian comparison are now stated with consistent constants and exponents.

## Notation and model consistency

- Standardized two-layer-network parameters as `x=(u,v)`, with `u` the outer weight and `v` the inner weight, throughout the main text and appendices.
- Consequently standardized the linear-network predictor, covariance blocks, error matrix, and gradient formulas to use `M_\mu=\int uv^\top\,d\mu=\Sigma_{UV}` and the corresponding `(Ev,E^\top u)` force.
- Removed the path notation `\gamma_t`, which collided with the matrix gauge `\gamma`, and used `\omega` for individual trajectories.
- Standardized the force covariance, root norm, representing set, metric slope, spectral Dirichlet form, Poincare constants, KL divergence, and block-gauge notation.
- Updated `neurips/notation_section.tex` to include the new symbols and their first-use locations, and to distinguish notation that had previously shared the same letter.
- Removed an obsolete disabled block and normalized source typography to ASCII-compatible LaTeX commands.

## Writing and presentation

- Reworked the abstract and introduction for a tighter statement of the paper's contribution and a clearer progression from static transport to gradient-flow applications.
- Polished theorem statements, proofs, transitions, captions, and appendix introductions throughout, removing ambiguous claims and tightening assumptions where the proofs require them.
- Clarified which results hold for convex monotone gauges, root-norm gauges, Schatten endpoints, positive-definite covariances, or canonical choices in a nonunique LMO.
- Resized the MLP figure to the text width and corrected the ordering and placement of the additional coupling/interpolation figures. The bunny, cross, and cat rows now match their labels, and the section introduction precedes its floats.

## Verification

- Built `neurips/paper.pdf` with two final `pdflatex` passes.
- Verified a 51-page letter-size PDF with no undefined references, undefined citations, duplicate labels, or overfull boxes.
- Rendered all 51 pages at 120 dpi and inspected them for clipping, overlap, float ordering, formula overflow, and figure-label alignment.
- The remaining log messages are benign: the NeurIPS draft-mode `hyperref` warning and underfull vertical boxes on float-heavy pages.
- Ran source whitespace and non-ASCII checks on the edited manuscript and notation files.

## Files changed

- `neurips/paper.tex`
- `neurips/notation_section.tex`
- `neurips/paper.pdf`
- `modifications.md`
