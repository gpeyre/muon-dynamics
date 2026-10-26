# Interactive slides

A Reveal.js presentation with locally bundled KaTeX, Canvas graphics and D3
contours. It currently contains a title slide and one interactive slide,
**Optimization over measures**. No external font, CDN or Python service is
needed to view the deployed deck.

Publication address: [www.gpeyre.com/muon-dynamics](https://www.gpeyre.com/muon-dynamics/).
GitHub Pages uses the account's existing custom domain for this project.

## Local preview

With Node.js 24 or later:

```sh
cd slides
npm ci
npm run dev
```

Open the local URL printed by Vite. Use the arrow buttons or arrow keys to
change slides; the particle and time sliders remain independent of navigation.
The play button animates the flow, the circular arrow resets time, and the
trajectory button toggles paths. Full screen and Reveal.js speaker notes
(`S`) are available. On narrow screens, the content slide scrolls vertically.

## Numerical experiment

The target is an equal mixture of two two-dimensional Gaussians. The blue
level sets show its analytic density. The optimization uses 2,048 fixed
target samples, with 1,024 samples from each component, and equal-weight
particle measures with `n = 8, 16, 32, 64, 128, 256`.

Each particle count has its own interacting-particle flow, computed with the
repository's `muon_dynamics.mmd_force`. Initial clouds share nested samples,
but changing the slider does not merely hide particles from a larger flow.
This opening experiment uses **W2 descent**, not spectral/Muon descent.

The energy is squared MMD for the energy-distance kernel `-|x-y|`, smoothed
numerically to `-sqrt(|x-y|^2 + epsilon^2)` with `epsilon = 0.001`. Explicit
Euler uses `dt = 0.04` up to `T = 16`; the browser interpolates 101 saved
frames. The displayed energy includes the constant target-target term.
All six saved energy sequences decrease. Colors interpolate from blue at
time zero to red at time `T`; target contours remain blue.

Regenerate only this small slide experiment from the repository root, in a
Python environment with the numerical toolbox dependencies installed:

```sh
python slides/scripts/generate_experiment.py
```

The saved data are versioned in `public/data/measures.json`; viewing or
building the slides never reruns a simulation.

## Scientific context

The cell example is deliberately high-level: infer a Waddington landscape
and trajectories between cell fates from population snapshots. See
[Huizing, Samaran et al., STORIES, Nature Methods 23, 522-531 (2026)](https://doi.org/10.1038/s41592-025-02855-4).
Modeling qualifications and experiment details are also in the speaker notes.

## Tests and publication

```sh
npm test
npx playwright install chromium
npm run test:browser
npm run build
npm run preview
```

On a machine with Chrome installed, `PLAYWRIGHT_CHANNEL=chrome npm run
test:browser` can use it instead. Browser tests cover desktop and phone
layouts, nonblank canvas pixels, color changes, controls and download errors.

The `Interactive slides` workflow builds and tests the deck, then publishes
only `slides/dist/` to GitHub Pages on pushes to `main`. Enable **GitHub
Actions** as the Pages source in the repository settings before deploying.
The default `https://gpeyre.github.io/muon-dynamics/` address redirects to
the existing custom domain. The workflow reports the publication URL. Private
drafts, review responses and paper source files are not part of the artifact.

To extend the deck, add a section to `index.html`; navigation counts it
automatically. Plotting and interpolation are separated into `src/plot.js`
and `src/experiment.js`; the simulation generator remains in Python.

Framework documentation: [Reveal.js](https://revealjs.com/),
[Vite deployment](https://vite.dev/guide/static-deploy), and
[GitHub Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
