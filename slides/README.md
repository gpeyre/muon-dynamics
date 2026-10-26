# Interactive lecture

A 27-slide Reveal.js lecture on **Muon Dynamics as a Spectral Wasserstein
Flow**, with 25 interactive numerical illustrations, locally bundled KaTeX,
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

1. **Algorithm to geometry:** practical Muon, removing momentum, the small-step
   limit, the state-dependent clock change, norm steepest descent, and Schatten
   exponents.
2. **Particles to measures to transport:** empirical scaling, the finite
   measure-LMO, MMD flows, static and robust transport, the Benamou-Brenier
   formula, geodesics, and Gaussian transport.
3. **Applications and consequences:** conditional gradient-flow identification,
   ReLU training, attention heads, Gaussian linear networks, block gauges,
   failure of geodesic convexity, P-L and Poincare inequalities.
4. **Extensions and limits:** root-norm gauges, finite Newton-Schulz iterations,
   and noise before normalization.

Allow approximately 45-60 minutes with demonstrations. Technical slides can
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
animate the experiments; space toggles playback when available. Full screen
and Reveal.js speaker notes (`S`) are available. On narrow screens, slides
scroll vertically without shrinking the entire lecture to an unreadable size.

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
  target samples, `epsilon=0.03`, `dt=0.02`, `T=8`, and 101 frames. Different
  particle counts are separately interacting systems with nested initial
  samples. Every run has decreasing saved energy. Comparisons use the same
  metric clock, without matching initial rates.
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
gives the velocity. Euler uses `dt=0.025`, `T=15`, and saves 101 frames.
Saved losses decrease. The lower plot projects neurons onto their two inner
coordinates; it does not show their outer weights.

The attention illustration averages scalar-head softmax weights for eight
tokens, 4/16/64 heads, and varying query/key scale. It is a parameterization
demo, not a training run. Effective token counts are averaged per head and
query, not computed from the averaged heatmap.

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
duality gaps, energy descent, positive covariances, attention normalization
and color convention. Browser tests visit every slide at desktop and phone
sizes, check equation bounds and nonblank canvases, exercise sliders,
playback, navigation and deep links, and capture screenshots. The commuting
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
- `src/plot.js`, `src/experiment.js`: opening particle experiment.
- `scripts/`: reproducible dataset generators.

The title and opening slide remain in `index.html`. The other sections are
generated before Reveal.js initializes, so navigation and deep links count
them automatically.

Framework documentation: [Reveal.js](https://revealjs.com/),
[Vite deployment](https://vite.dev/guide/static-deploy), and
[GitHub Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
