"""Generate the small, deterministic slide experiment with the Python toolbox.

No article experiment is changed or rerun. Runtime playback only interpolates
these trajectories; it never solves an optimization problem in the browser.
"""

import argparse
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from muon_dynamics import mmd_force  # noqa: E402

COUNTS = (8, 16, 32, 64, 128, 256)
MIXTURE = (
    {"weight": .5, "mean": [-1.25, 1.0], "covariance": [[.32, .13], [.13, .27]]},
    {"weight": .5, "mean": [1.45, .45], "covariance": [[.28, -.11], [-.11, .42]]},
)


def mean_distance(x, y, epsilon):
    total = 0.0
    for block in np.array_split(x, max(1, len(x) // 128)):
        total += np.sqrt(((block[:, None] - y[None, :]) ** 2).sum(-1) + epsilon**2).sum()
    return float(total / (len(x) * len(y)))


def generate(target_count=2048, steps=400):
    if steps < 100 or steps % 100:
        raise ValueError("steps must be a positive multiple of 100")
    if target_count < 2 or target_count % 2:
        raise ValueError("target_count must be positive and even")
    rng = np.random.default_rng(20261026)
    target = np.concatenate([
        rng.multivariate_normal(component["mean"], component["covariance"], target_count // 2)
        for component in MIXTURE
    ])
    initial = rng.normal(size=(max(COUNTS), 2)) * [.53, .43] + [-1.8, -1.65]
    epsilon, horizon = 1e-3, 16.0
    target_constant = mean_distance(target, target, epsilon)
    experiments = []
    for count in COUNTS:
        x = initial[:count].copy()
        frames, energies = [], []
        for step in range(steps + 1):
            if step % (steps // 100) == 0:
                frames.append(x.round(6).ravel().tolist())
                energy = 2 * mean_distance(x, target, epsilon) - mean_distance(x, x, epsilon) - target_constant
                energies.append(round(energy, 9))
            if step < steps:
                x -= (horizon / steps) * mmd_force(x, target, epsilon=epsilon)
        if not np.isfinite(x).all() or np.max(np.diff(energies)) > 1e-7:
            raise RuntimeError(f"Unstable or non-descending trajectory for n={count}")
        experiments.append({"count": count, "frames": frames, "energies": energies})
        print(f"n={count}: energy {energies[0]:.6f} -> {energies[-1]:.6f}", flush=True)
    return {
        "version": 1, "seed": 20261026, "epsilon": epsilon,
        "horizon": horizon, "stepSize": horizon / steps, "frameCount": 101,
        "targetCount": target_count, "targetSamples": target.round(6).ravel().tolist(),
        "mixture": MIXTURE, "experiments": experiments,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-count", type=int, default=2048)
    parser.add_argument("--steps", type=int, default=400)
    parser.add_argument("--output", type=Path, default=ROOT / "slides/public/data/measures.json")
    args = parser.parse_args()
    result = generate(args.target_count, args.steps)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Saved {args.output} ({args.output.stat().st_size:,} bytes)")
