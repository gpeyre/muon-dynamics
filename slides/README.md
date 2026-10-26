# Interactive lecture

A 35-slide, four-part Reveal.js lecture on **Muon Dynamics as a Spectral Wasserstein
Flow**, with 29 interactive numerical illustrations and four animated roadmaps, locally bundled KaTeX,
Canvas graphics and D3 contours. No external font, CDN or Python service is
needed to view the deployed deck.

**[Open the slides](https://www.gpeyre.com/muon-dynamics/)** |
[Paper](https://arxiv.org/abs/2604.04891) | [Storyboard](STORYBOARD.md)

GitHub Pages uses the account's existing custom domain for this project.
Individual slides have stable links, for example
[the two clocks](https://www.gpeyre.com/muon-dynamics/#/clocks) and
[spectral transport](https://www.gpeyre.com/muon-dynamics/#/static).

## Narrative

The storyboard records the alternatives considered before implementation,
the teaching objective of each slide, and mathematical safeguards.

1. **[From Muon to measures](https://www.gpeyre.com/muon-dynamics/#/part-1)**
   (slides 2-12): measure optimization, practical Muon, small momentum and step
   limits, the clock change, Schatten descent, empirical scaling, the finite
   measure-LMO, and MMD/quadratic flows.
2. **[Spectral transport](https://www.gpeyre.com/muon-dynamics/#/part-2)**
   (slides 13-20): static and robust transport, exact mass splitting,
   Benamou-Brenier, geodesics, and Gaussian covariance transport.
3. **[Learning dynamics](https://www.gpeyre.com/muon-dynamics/#/part-3)**
   (slides 21-26): conditional gradient-flow identification, ReLU training,
   attention heads, Gaussian linear networks, and block gauges.
4. **[Convergence and limits](https://www.gpeyre.com/muon-dynamics/#/part-4)**
   (slides 27-35): geodesic convexity, P-L, Gaussian and radial Poincare
   comparisons, root-norm gauges, finite Newton-Schulz, and stochastic forces.

Each part opens with the same four-preview roadmap. The current part is fully
opaque, with the other three at 26% opacity. Its previews show a varying
Schatten norm ball, optimal joint-Gaussian interpolation, a saved ReLU fit,
and theoretical P-L envelopes. Each preview links to its part's roadmap.
The title uses a dark, full-bleed canvas with luminous particle heads and
short trails from the saved 256-particle W2 experiment. Blue contours show
the analytic target. No new simulation is needed for these animations.

Forward replays fade before restarting, rather than running the dynamics
backwards. The title loops every 20 seconds; roadmap loops take 14-18 seconds.
Only the visible slide animates. Pause/play buttons and the space key control
ambient playback, and reduced-motion preferences pause it by default.

Allow approximately 50-65 minutes with demonstrations. Technical slides can
be skipped using the slide index. Each slide includes source pointers and
speaker notes with assumptions, proof ideas and numerical qualifications.

Throughout, **initial measures are red, targets are blue, and moving particles
interpolate red to blue**. Paths are translucent gray. Other plots use gray
for a baseline and green for the selected response. Larger local dissipation
is not presented as a universal training or runtime advantage.

## Local preview

With Node.js 24 or later:

```sh
cd slides
npm ci
npm run dev
```

Open the local URL printed by Vite. Arrow buttons and arrow keys change slides;
the index button jumps directly to a topic. Time sliders and play buttons
animate the experiments; reset returns time to zero, and space toggles
playback when available. Full screen
and Reveal.js speaker notes (`S`) are available. On narrow screens, slides
scroll vertically without shrinking the entire lecture to an unreadable size.
The index groups the lecture into four parts. Major numerical experiments use
full-width layouts. At 1280-by-720, main prose is at least 22 pixels and display
equations at least 23 pixels; chart labels are at least 14 pixels. Essential
qualifications remain on screen, with longer arguments in speaker notes.

## Numerical provenance

Small datasets are versioned in `public/data/`. Building or viewing the deck
never reruns simulations. Generators reuse the repository's numerical toolbox;
they do not modify or rerun the article's full experiments.

### Opening measure experiment

`measures.json` contains W2 MMD descent toward an equal mixture of two 2D
Gaussians, with 2,048 fixed target samples and particle counts 8-256. Blue
contours show the analytic target density. The smoothed energy-distance
kernel is `-sqrt(|x-y|^2 + epsilon^2)`, with `epsilon=0.001`. Euler uses
`dt=0.04`, `T=16`, and saves 101 frames. Energy includes the target-target
constant. The six saved energy sequences decrease.

### Spectral dynamics and transport

`lecture.json` contains:

- Twenty MMD runs: `n=16,32,64,128`, `p=1,1.5,2,4,infinity`, 1,024 stratified
  target samples, `epsilon=0.03`, `T=8`, and 101 frames. Adaptive RK45 uses
  `rtol=2e-6`, `atol=2e-8`, and maximum step `0.08`. Different
  particle counts are separately interacting systems with nested initial
  samples. Every run has decreasing saved energy. Comparisons use the same
  metric clock, without matching initial rates. At `n=32`, the trace and
  operator runs were repeated at 100-times tighter tolerances and half the
  maximum step. Maximum coordinate RMS differences were `3.8e-6` and `1.7e-5`;
  relative final-energy differences were below `7e-6`. These are refinement
  checks, not rigorous error bounds for every run.
- Eighteen spectral transport solves: 8 or 16 atoms, `p=1,2,infinity`, and
  target rotations 0, 30 or 60 degrees. The full coupling polytope is used;
  splitting is allowed. SciPy solves the trace case and the toolbox uses
  CVXPY/CLARABEL for the other cases. Independent robust dual solves agree
  within `4e-8`; marginal residuals are below `1e-7`.
- A grid of 1,533 trace-one PSD cost matrices for the robust-cost experiment.
  Each inner quadratic transport problem is solved by assignment. Its
  continuous robust optimum is computed separately, not estimated from the grid.
- Fifteen centered Gaussian linear-network runs with an affine force,
  integrated through a covariance factor with SciPy. Saved covariances remain
  positive definite and losses decrease. Full, sum-block and max-block
  selectors are also compared on a fixed small force matrix.

### Neural-network illustrations

`networks.json` contains nine small ReLU teacher-fitting runs with 16, 32 or
64 neurons and `p=1,2,infinity`. The scalar input is augmented by a bias
coordinate. PyTorch differentiates the loss on 97 fixed inputs; multiplying
by the neuron count gives the measure force, and the toolbox's Schatten LMO
gives the velocity. Heun's method uses `dt=0.025`, `T=40`, and saves 101 frames.
Saved losses decrease. At `n=32`, halving the step for the trace and operator
runs changes predictions by at most `3.8e-5` in RMS across the input grid and
final losses by less than `8e-6` relatively. ReLU nonsmoothness still requires
care in interpreting a continuous-time limit. The parameter plot projects
neurons onto their two inner coordinates; marker radius also reflects the
absolute outer weight. A dashed trace-flow predictor supplies a baseline.

The attention illustration averages scalar-head softmax weights for eight
tokens, 4/16/64 heads, and varying query/key scale. It is a parameterization
demo, not a training run. Effective token counts are averaged per head and
query, not computed from the averaged heatmap. A query-row slider connects
the heatmap to its individual weight profile; the square-root color scale is
explicitly identified.

### Additional analytic and covariance experiments

`extensions.json` contains three small, reproducible datasets:

- **Anisotropic quadratic descent:** 20 closed covariance evolutions for
  curvature ratios `1,4,16,32` and five exponents. Trace and operator endpoints
  use exact exponentials. Intermediate exponents reduce to a scalar clock ODE
  with positive-part powers, so extinction cannot produce negative standard
  deviations. Empirical clouds of 16, 64 and 256 points are centered and
  whitened separately; the covariance closure is exact for each cloud.
- **Rotated Gaussian transport:** 21 primal/dual semidefinite pairs for seven
  rotations and `p=1,2,infinity`. Independent dual values agree within `5e-8`.
  Every interpolated ellipse uses the analytic covariance of the optimal
  joint Gaussian, not a fit to its 96 displayed samples. Numerical negative
  eigenvalues at solver tolerance are clipped only when sampling. The joint
  Gaussian is not asserted to be induced by a deterministic map.
- **Radial Poincare tests:** exact second, fourth and sixth moments for seven
  targets, from `exp(-|x|^1.25)` to the uniform disk, rescaled to covariance
  identity. Browser formulas evaluate linear-plus-cubic test quotients.
  These are upper bounds on sharp constants, not computed sharp constants
  or numerical proofs of the strict-gap theorem.

An exact two-atom transport example needs no data file: its feasible
couplings have displacement eigenvalues `2 theta` and `2(1-theta)`. For
`p>1`, equal splitting uniquely minimizes the cost at `2^(1/p)`, whereas
every deterministic transport costs 2. The interface distinguishes optimal
from nonoptimal interpolations.

Other experiments use explicit formulas evaluated in the browser: diagonal
LMOs, clock changes, EMA response, norm balls, commuting Gaussian transport,
entropy collapse, P-L envelopes, Gaussian test-function quotients, classical
cubic Newton-Schulz iterations, and a two-outcome noisy-force model.

To regenerate the data from the repository root, use a Python environment
with the toolbox, SciPy, CVXPY and PyTorch installed:

```sh
python slides/scripts/generate_experiment.py
python slides/scripts/generate_lecture.py
python slides/scripts/generate_networks.py
python slides/scripts/generate_extensions.py
```

The cell example remains deliberately high-level: infer a Waddington
landscape and trajectories between cell fates from population snapshots.
See [Huizing, Samaran et al., STORIES (2026)](https://doi.org/10.1038/s41592-025-02855-4).

## Tests and publication

```sh
npm test
npx playwright install chromium
npm run test:browser
npm run build
npm run preview
```

On a machine with Chrome installed, `PLAYWRIGHT_CHANNEL=chrome npm run
test:browser` uses it instead. Unit tests check the formulas, feasibility,
duality gaps, energy descent, refinement checks, positive covariances, attention normalization
and color convention. Browser tests visit every slide at desktop and phone
sizes, check readable font floors, equation bounds and nonblank canvases,
exercise sliders, playback, reset, navigation and deep links, and capture
screenshots. The commuting
Gaussian example explicitly checks that changing p changes its distance but
not its interpolation.

The `Interactive slides` workflow builds and tests the deck, then publishes
only `slides/dist/` on pushes to `main`. Pages is configured to use GitHub
Actions. The default `https://gpeyre.github.io/muon-dynamics/` address redirects
to the existing custom domain. Private drafts, review responses and paper
source files are not included in the publication artifact.

## Extending the deck

- `src/content.js`: slide order, visible equations, controls, sources and notes.
- `src/demos.js`: interactive charts and per-slide playback.
- `src/lecture-math.js`: pure mathematical functions, independently tested.
- `src/main.js`: navigation, mathematical rendering, loading and animation.
- `src/ambient.js`: looping title scene and the four roadmap previews.
- `src/plot.js`, `src/experiment.js`: opening particle experiment.
- `scripts/`: reproducible dataset generators.

The title and opening slide remain in `index.html`. The other sections are
generated before Reveal.js initializes, so navigation and deep links count
them automatically.

Framework documentation: [Reveal.js](https://revealjs.com/),
[Vite deployment](https://vite.dev/guide/static-deploy), and
[GitHub Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
