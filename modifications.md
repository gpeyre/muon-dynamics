# GitHub Actions Compatibility Fix: 2026-09-27

- Investigated failed run `36314997903`: both core jobs, all numerical tests,
  notebook-source checks, and the four teaching examples passed. The paper
  smoke run stopped in the MLP angular-density plot because NumPy 2.4 and
  later no longer provide `np.trapz`; local NumPy 2.3.5 still provided it.
- Replaced this call with `scipy.integrate.trapezoid` in the notebook and
  its generator, preserving the existing NumPy/SciPy minimum versions and
  the numerical quadrature rule.
- Added a regression test that extracts the actual notebook helper, hides
  `np.trapz` even on older NumPy, and checks unit-integral normalization,
  nonnegativity, and the zero-weight case. It reproduced the original error
  before the fix; all 12 tests pass after the fix.
- Notebook/generator checks pass, and the corrected MLP smoke run and the
  subsequent attention smoke run both complete locally with all eight PDFs.
- Updated checkout, Python setup, and artifact upload to the verified
  official v7 actions using Node.js 24. Pinned CI runners to `ubuntu-24.04`
  to avoid the upcoming `ubuntu-latest` OS migration. These warnings were
  separate from the NumPy error that caused the job failure.

---

# Computational Toolbox and Reproducibility Pass: 2026-09-27

## Organization and API

- Added an installable `muon_dynamics` package with a NumPy/SciPy core and
  separate PyTorch, convex-transport, notebook, and full-experiment extras.
- Added Schatten gauges/root norms, matrix and weighted-particle LMOs for
  `p >= 1/2`, blockwise LMOs, uncentered second moments, smoothed MMD energies
  and forces, centered Gaussian KL/covariance vector fields, and full-coupling
  static transport for `p=1,2,infinity`.
- Made signs, particle-weight versus parameter-gradient scaling, endpoint
  choices, numerical rank tolerance, and squared transport costs explicit.
  Singular force covariances do not require inverse regularization.
- Centralized the MMD, MLP, and attention spectral selectors in the tested
  PyTorch implementation. Removed silent random perturbation, zero-update,
  and gradient-descent fallbacks on MLP selector failures. Null singular
  directions are suppressed with an explicit relative tolerance; very large
  finite exponents also preserve this support when the dual exponent rounds
  to one. Archived figures were not silently replaced.

## Examples and Figure Reproduction

- Added four short generated Jupyter notebooks in `python/examples/`, with
  executed plots: spectral directions, particle MMD, convex static transport,
  and Gaussian KL. The last uses an isotropic case with an exact covariance
  solution, avoiding nonsmooth force-rank events in a first teaching example.
- Added an isolated `scripts/reproduce.py` runner for all six paper notebooks
  and the teaching examples. It supports reduced smoke runs, validates
  generator/notebook agreement, saves executed notebooks, checks figure export,
  and records package versions, source hashes, Git state, overrides, and errors.
  It refuses to overwrite existing run directories or tracked paper figures.
- Clearly labeled the paper's operator matching routine as a heuristic, not a
  full spectral OT solve. Added a two-point example where splitting mass
  strictly beats every matching, with a convex-solver regression check.
- Corrected the legacy README-preview generator's obsolete `paper/figures`
  output path and stopped it from producing outdated top-level notebooks.
- Expanded the root README and `python/README.md`, added API/reproduction
  guides, and added preview figures and GitHub links for the new notebooks.
  Clarified that attention trials redraw both teacher and student, and that
  legacy Gaussian KL galleries use numerical regularization and arclength.
- Added GitHub Actions configuration for core tests on Python 3.10/3.12 and
  optional-backend tests plus all notebook smoke runs on Python 3.12.
- Verified the GitHub URL in the main-body Contributions paragraph and
  expanded its sentence to mention the toolbox and illustrative notebooks.
  Rebuilt the manuscript PDF and arXiv source bundle, and visually checked
  the Contributions page.

## Verification and Limits

- Editable installation and wheel build succeeded locally on Python 3.14.
- All 11 numerical tests pass, covering LMO optimality identities, rank-deficient endpoints,
  extreme exponents, rotation equivariance, weighted/replicated particles,
  NumPy/PyTorch agreement, optional-dependency isolation, finite-difference
  MMD derivatives, Gaussian dissipation, and exact small transport examples.
- All four teaching notebooks executed successfully. All six paper notebooks
  executed with reduced smoke settings and produced the expected 70 PDFs.
  All notebook/generator consistency checks pass. Example plots were inspected.
- The full-size MLP initialization validator retains the manuscript's
  dissipation ratio `2.5576465` and clipped-decrease ratio `0.9233357`.
- Full-length MLP, attention, MMD, and static experiments were not rerun in
  this code pass. Smoke runs check plumbing and export, not scientific
  reproducibility or convergence. No new benchmark or general integrator
  accuracy guarantee is claimed. GitHub Actions is configured but has not
  been run remotely. No commit or push was performed.
- No license was previously present. A code-license choice was requested;
  no license is imposed without the author's decision.

---

# Post-Correction Mathematical Recheck: 2026-09-27

Rechecked the corrected proofs and nearby dependencies, and recorded the
details in the new opening section of `audit-maths.md`.

- Corrected the Gaussian boundary proof's remainder from an ambiguous
  `O(W_2^2)` to the cost of the **chosen coupling**, exactly as required by
  the main transport--Taylor hypothesis. The boundary flow conclusion is
  unchanged. Made its finite action and almost-everywhere identities explicit.
- Added the necessary factor `T` when bounding the spherical endpoint
  distance by an action computed on `[0,T]`, with the time-rescaling proof.
- Restricted the Gaussian-preservation hypothesis to states in the energy
  domain, excluded singular Gaussians from the entropy example, and required
  smooth dependence for the general moment-functional example.
- Made root-norm comparison constants independent of the Hilbert target
  explicitly, and justified the entropy perturbation expansion under its
  changing reference measure using two-sided velocity-norm bounds.
- Qualified the rank-invariant and nonlocality wording where stationary
  modes or dimension-one geometries are exceptions.
- Extended `python/gaussians/validate_gaussians.py` with independent matrix
  LMO/covariance checks and Gaussian entropy directional derivatives, including
  the nonconvex root-norm range. Maximum errors were `5.33e-15` for covariance
  dynamics, `8.89e-15` for matrix action/dissipation, and `5.75e-10` for the
  entropy finite difference. Reran the 24-case rank-event validation.
- Rebuilt and visually checked the updated 58-page PDF and refreshed the
  arXiv bundle. No undefined references/citations or overfull boxes remain;
  the existing underfull notice on a figure page is unchanged.

The recheck found no further error in the corrected central results after
these repairs. Global PDE well-posedness, converse spherical lifting, and
uniform local entropy P-L theory remain outside the proved statements.

# Mathematical Audit Corrections: 2026-09-27

Implemented the repair plan in `audit-maths.md` in `neurips/paper.tex` and
`neurips/notation_section.tex`. The original audit and the earlier release
log below are retained as historical records.

## Corrections by Finding

| Finding | Implemented correction |
| --- | --- |
| A1: homogeneous selection | Appendix J now fixes the projected matrix selector as a function of the force second moment. The spherical PDE assumes a one-homogeneous Borel velocity, zero at the origin, finite action, and Wasserstein continuity. The proof justifies the quadratic-growth test by cutoffs. Smoothness of the feature/energy is explicit; ReLU requires a separate nonsmooth argument. |
| A2: block normalization | Appendix B distinguishes the sum gauge, which gives separately scaled squared-norm LMOs, from the maximum of block operator norms. The latter gives raw blockwise polar directions with a single common multiplier. Added fixed block learning-rate weights and aligned the main-text summaries. |
| A3: velocity versus speed | Removed the unrestricted identification of velocity norm and metric speed. Stated the representative minimization formally and retained the proved speed equality for descent flows. Replaced the entropy-convexity proof's unsupported minimal-velocity step by a fixed optimal quadratic-cost argument along the given geodesic. |
| A4: entropy slope | Added `prop:entropy-slope`, identifying the ambient entropy slope under positive C1 densities and a log-density ratio with bounded Hessian. Its proof uses a one-sided entropy inequality and compact smooth transports. Gaussian KL flows now have a separate metric verification, and smooth entropy perturbations explicitly satisfy the lemma. |
| A5: covariance rank loss | Restricted the inverse-covariance formula to positive-definite intervals. Proved the general modal invariant and finite-time extinction criterion. Added `app-prop:gaussian-boundary`, verifying the canonical zero-eigenvalue continuation directly from Gaussian random variables and the metric energy identity, conditionally on the modal solution. Explained which plotted targets require it, and added independent event/refinement checks. |
| A6: spherical geometry | Specified the admissible unbalanced paths, distinguished equality of projected actions from equality of endpoint distances, and supplied a counterexample to an isometry of fixed lifts. Proved the spherical metric property by comparison with WFR and action concatenation. No converse lifting theorem is claimed. |
| A7: attention domain | A finite sixth parameter moment is given as a sufficient force-integrability condition for bounded data and targets. Moment preservation and selector regularity remain separate requirements. |
| A8: radial powers | Supplied the local form-bound argument for the singular effective potential when the radial exponent lies between one and two, followed by tail control and compact embedding. Clarified elliptic regularity in the ridge-eigenfunction obstruction. |
| A9: local dissipation | Replaced bilinear “Dirichlet form” language by “Dirichlet energy.” Explained that the leading small-amplitude spectral PDE is generally nonlinear, gave its formal dissipation identity, and distinguished the variational local constant from a uniform local or global P-L theorem. |
| A10: consistency | Fixed the missing divergence command, separated SVD notation from the Schatten exponent, made the operator endpoint convention explicit, declared uncentered second-moment terminology, and corrected the attention clock description. The definition of a flow now includes absolute continuity and the integrated energy identity. |

## Additional Safeguards

- Restricted the commuting Gaussian formula explicitly to `p >= 1` and
  included the `p = 1/2` counterexample from the audit.
- Strengthened the root-norm characterization: it is enough to test the
  norm property on square `d x d` matrices. The proof derives Loewner
  monotonicity and extends the triangle inequality to arbitrary Hilbert
  targets by compression.
- None of these repairs asserts global existence or uniqueness for the
  general nonlinear PDE. The new boundary proposition verifies a specified
  modal continuation; the entropy proposition verifies an existing
  positive-definite Gaussian moment curve. The finite Newton--Schulz
  dissipation statement remains distinct from a fixed-metric flow.

## Verification

- The Gaussian algebra validator passes: maximum tested vector-field error
  `3.55e-15`, interior-invariant derivative error `8.88e-16`.
- New `python/gaussians/validate_rank_events.py` independently integrates
  transformed variances with rank-loss and zero-error events for all 24
  published parameter cases over `[0,18]`. It also checks nonnegativity,
  energy decay, and persistence of extinct eigenvalues.
- It detects 11 rank-loss events and 12 target events. Comparing reference
  tolerances gives maximum sampled eigenvalue discrepancy `1.34e-7`,
  rank-event time discrepancy `4.83e-8`, and target-event time discrepancy
  `2.49e-5`. Finite-p target events are nontransverse and less accurately
  localized than rank loss; the last remaining residual approaches zero
  asymptotically and is not counted as a finite target event.
- Local notebook-RK4 refinement across every detected event reduces the
  maximum eigenvalue error from `3.42e-4` at step `2e-4` to `8.53e-5` at
  step `5e-5`. These checks are not a certified full-trajectory error bound
  and do not assume fourth-order convergence at nonsmooth events. Existing
  figures are retained; full neural-network training was not rerun.
- Rebuilt the 58-page `neurips/paper.pdf` and the 65-file arXiv source
  bundle. The final LaTeX log has no undefined references/citations or
  overfull boxes; one underfull vertical-box notice remains on an existing
  figure page. Inspected rendered pages covering the changed definitions,
  proofs, block gauges, Gaussian continuation, Poincare discussion, spherical
  reduction, and notation table. `git diff --check` passes.
- Independently checked the two-block scaling and nonconvex commuting
  counterexample numerically. The numerical README now documents the new
  validator and the distinction between interior invariants and boundary
  continuation. No bibliography or historical rebuttal was changed in this pass.

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
