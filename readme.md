# Muon Dynamics as a Spectral Wasserstein Flow

Author: Gabriel Peyré

This repository accompanies the article

> Muon Dynamics as a Spectral Wasserstein Flow, Gabriel Peyré, [arXiv:2604.04891](http://arxiv.org/abs/2604.04891), 2026.

The project studies matrix-normalized optimization rules, with Muon as the motivating example, through a mean-field transport viewpoint. The core object is a family of Spectral Wasserstein distances indexed by a norm $\gamma$ on positive semidefinite matrices:

```math
\mathsf W_{\gamma}(\mu,\nu)^2
=
\inf_{\pi\in\Pi(\mu,\nu)}
\gamma\!\left(
\int (y-x)(y-x)^\top\,d\pi(x,y)
\right).
```

Two benchmark choices are:

- $\gamma(S)=\mathrm{tr}(S)$, which recovers the classical $W_2^2$ geometry.
- $\gamma(S)=\lambda_{\max}(S)$, which gives the Muon or operator-norm geometry.

Intermediate Schatten norms, such as the Frobenius case $p=2$, interpolate between these two extremes.

This repository contains:

- the paper source in `neurips/` and the generated figures used by the manuscript;
- reproducible notebooks for static spectral transport couplings and MMD gradient flows;
- additional notebooks for Gaussian reductions, two-layer ReLU training, and shallow attention;
- helper scripts that regenerate the notebooks from plain Python sources.

The figure below illustrates MMD gradient flows under different spectral geometries. They optimize the same objective, but move the particle cloud through different collective directions.

![Three Schatten flows](./assets/mmd_trajectories_three.png)

## Notebooks

All notebooks are in [`python/`](./python/README.md). Each one can be opened directly on GitHub or launched in Colab.

### Static Spectral Couplings

[![Static spectral couplings](./assets/static_matchings_three.png)](https://github.com/gpeyre/muon-dynamics/blob/main/python/static/static_couplings.ipynb)

[![Open on GitHub](https://img.shields.io/badge/Open_on-GitHub-24292f?logo=github)](https://github.com/gpeyre/muon-dynamics/blob/main/python/static/static_couplings.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/gpeyre/muon-dynamics/blob/main/python/static/static_couplings.ipynb)

Static transport couplings between planar point clouds for the trace geometry and the operator-norm geometry.

### MMD Gradient Flow

[![MMD gradient flow](./assets/mmd_trajectories_three.png)](https://github.com/gpeyre/muon-dynamics/blob/main/python/mmd/mmd_flow.ipynb)

[![Open on GitHub](https://img.shields.io/badge/Open_on-GitHub-24292f?logo=github)](https://github.com/gpeyre/muon-dynamics/blob/main/python/mmd/mmd_flow.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/gpeyre/muon-dynamics/blob/main/python/mmd/mmd_flow.ipynb)

Particle flows minimizing an MMD loss under different Spectral Wasserstein geometries.

### Gaussian Closed-Form Reductions

[![Gaussian closed-form reductions](./assets/gaussian_closed_form.png)](https://github.com/gpeyre/muon-dynamics/blob/main/python/gaussians/gaussian_closed_form.ipynb)

[![Open on GitHub](https://img.shields.io/badge/Open_on-GitHub-24292f?logo=github)](https://github.com/gpeyre/muon-dynamics/blob/main/python/gaussians/gaussian_closed_form.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/gpeyre/muon-dynamics/blob/main/python/gaussians/gaussian_closed_form.ipynb)

Closed-form Gaussian dynamics, conserved leaves, and rank-one/rank-two covariance trajectories.

### Gaussian KL Flow

[![Gaussian KL flow](./assets/gaussian_kl_flow.png)](https://github.com/gpeyre/muon-dynamics/blob/main/python/gaussians-kl-flow/gaussian-kl-flow.ipynb)

[![Open on GitHub](https://img.shields.io/badge/Open_on-GitHub-24292f?logo=github)](https://github.com/gpeyre/muon-dynamics/blob/main/python/gaussians-kl-flow/gaussian-kl-flow.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/gpeyre/muon-dynamics/blob/main/python/gaussians-kl-flow/gaussian-kl-flow.ipynb)

Centered Gaussian covariance flows for the KL functional, sampled by covariance arclength.

### Two-Layer ReLU Training

[![Two-layer ReLU training](./assets/mlp_spectral_flow_relu.png)](https://github.com/gpeyre/muon-dynamics/blob/main/python/mlp/mlp_spectral_flow_relu.ipynb)

[![Open on GitHub](https://img.shields.io/badge/Open_on-GitHub-24292f?logo=github)](https://github.com/gpeyre/muon-dynamics/blob/main/python/mlp/mlp_spectral_flow_relu.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/gpeyre/muon-dynamics/blob/main/python/mlp/mlp_spectral_flow_relu.ipynb)

Mean-field training of a two-layer ReLU network in two dimensions under trace and Muon-type flows.

### Shallow Attention

[![Shallow attention spectral flow](./assets/attention_spectral_flow.png)](https://github.com/gpeyre/muon-dynamics/blob/main/python/attention/attention_spectral_flow.ipynb)

[![Open on GitHub](https://img.shields.io/badge/Open_on-GitHub-24292f?logo=github)](https://github.com/gpeyre/muon-dynamics/blob/main/python/attention/attention_spectral_flow.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/gpeyre/muon-dynamics/blob/main/python/attention/attention_spectral_flow.ipynb)

Mean-field shallow multi-head attention trained against a random teacher across dense and sparse attention regimes.

## Reproducing the Numerics

The notebooks use standard scientific Python packages listed in `requirements.txt`. From the repository root, a typical setup and run is:

```bash
python -m pip install -r requirements.txt
cd python/mmd
python generate_mmd_notebook.py
jupyter nbconvert --to notebook --execute --inplace mmd_flow.ipynb
```

The generated PDF figures are written under `neurips/figures/fig-*`, where the LaTeX source includes them.

## Building the Paper

The active LaTeX source is in `neurips/`. From that directory, run:

```bash
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex
```

The `arxiv/` directory is treated as a generated export bundle and is ignored by git.
