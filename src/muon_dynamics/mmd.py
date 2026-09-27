"""Smoothed energy-distance MMD for weighted particle measures.

The kernel is -sqrt(|x-y|**2 + epsilon**2). Pairwise storage is quadratic
in the particle counts; this intentionally small implementation is not batched.
"""

import numpy as np

from .spectral import _matrix, _weights


def _inputs(x, y, weights, target_weights, epsilon):
    x, y = _matrix(x, "x"), _matrix(y, "y")
    if x.shape[1] != y.shape[1]:
        raise ValueError("point clouds must have the same ambient dimension")
    if not np.isfinite(epsilon) or epsilon <= 0:
        raise ValueError("epsilon must be positive and finite")
    return x, y, _weights(weights, len(x)), _weights(target_weights, len(y))


def _distances(x, y, epsilon):
    return np.sqrt(np.sum((x[:, None] - y[None, :]) ** 2, axis=-1) + epsilon**2)


def mmd_energy(x, y, *, weights=None, target_weights=None, epsilon=0.01):
    """Squared MMD, including the constant target-target term."""
    x, y, a, b = _inputs(x, y, weights, target_weights, epsilon)
    return float(2 * a @ _distances(x, y, epsilon) @ b
                 - a @ _distances(x, x, epsilon) @ a
                 - b @ _distances(y, y, epsilon) @ b)


def mmd_force(x, y, *, weights=None, target_weights=None, epsilon=0.01):
    """Spatial first-variation gradient g(x_i), so dF/dx_i = w_i*g(x_i)."""
    x, y, a, b = _inputs(x, y, weights, target_weights, epsilon)
    cross = (x[:, None] - y[None, :]) / _distances(x, y, epsilon)[..., None]
    own = (x[:, None] - x[None, :]) / _distances(x, x, epsilon)[..., None]
    return 2 * (np.einsum("ijd,j->id", cross, b) - np.einsum("ijd,j->id", own, a))
