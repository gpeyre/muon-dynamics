"""Tiny CPU-only ReLU fits and scalar-head attention illustrations for slides."""

import json
from pathlib import Path
import sys

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from muon_dynamics.torch import schatten_lmo  # noqa: E402

torch.set_num_threads(1)
torch.set_default_dtype(torch.float64)


def relu_fits():
    rng = np.random.default_rng(720)
    grid = torch.linspace(-1, 1, 97)
    inputs = torch.stack([grid, torch.ones_like(grid)], dim=1)
    teacher = torch.tensor([[2.5, 1, .6], [-4., 1, .05], [3., 1, -.5]])

    def predict(x):
        return torch.relu(inputs @ x[:, 1:].T) @ x[:, 0] / len(x)

    target = predict(teacher)
    initial = np.column_stack([rng.normal(0, .5, 64), rng.normal(0, 1, (64, 2))])
    output = []
    for n in (16, 32, 64):
        for p, label in ((1, "1"), (2, "2"), (np.inf, "inf")):
            x = torch.tensor(initial[:n], requires_grad=True)
            frames, predictions, losses = [], [], []
            for k in range(601):
                prediction = predict(x)
                loss = .5 * ((prediction - target) ** 2).mean()
                if k % 6 == 0:
                    frames.append(x.detach().numpy().round(8).tolist())
                    predictions.append(prediction.detach().numpy().round(8).tolist())
                    losses.append(float(loss.detach()))
                if k < 600:
                    force = n * torch.autograd.grad(loss, x)[0]
                    with torch.no_grad():
                        x += .025 * schatten_lmo(force, p)
            if max(np.diff(losses)) > 1e-7:
                raise RuntimeError(f"Non-descending ReLU example n={n}, p={label}")
            output.append(dict(n=n, p=label, frames=frames, predictions=predictions, losses=losses))
            print(f"ReLU n={n}, p={label}: {losses[0]:.5f} -> {losses[-1]:.5f}", flush=True)
    return dict(grid=grid.numpy().tolist(), target=target.numpy().tolist(), horizon=15, dt=.025, experiments=output)


def attention():
    rng = np.random.default_rng(841)
    heads = rng.normal(size=(64, 2))
    tokens = np.linspace(-1.5, 1.5, 8)
    output = []
    for n in (4, 16, 64):
        for scale in np.linspace(0, 3, 31):
            logits = (scale**2 * heads[:n, 0] * heads[:n, 1])[:, None, None] * tokens[None, :, None] * tokens[None, None, :]
            weights = np.exp(logits - logits.max(axis=-1, keepdims=True))
            weights /= weights.sum(axis=-1, keepdims=True)
            output.append(dict(n=n, scale=round(float(scale), 2), weights=weights.mean(axis=0).round(9).tolist(),
                               effectiveTokens=float((1 / (weights**2).sum(axis=-1)).mean())))
    return dict(tokens=tokens.tolist(), experiments=output)


if __name__ == "__main__":
    path = ROOT / "slides/public/data/networks.json"
    path.write_text(json.dumps(dict(version=1, relu=relu_fits(), attention=attention()), separators=(",", ":"), allow_nan=False) + "\n")
    print(f"Saved {path.name}: {path.stat().st_size:,} bytes")
