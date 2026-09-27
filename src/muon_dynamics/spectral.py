"""Schatten root norms and quadratic-penalty LMOs for real matrices."""

import numpy as np


def _matrix(value, name="matrix"):
    raw = np.asarray(value)
    if np.iscomplexobj(raw):
        raise ValueError(f"{name} must be real")
    value = np.asarray(raw, dtype=float)
    if value.ndim != 2 or min(value.shape) == 0 or not np.isfinite(value).all():
        raise ValueError(f"{name} must be a nonempty finite matrix")
    return value


def _exponent(p, minimum=0.5):
    p = float(p)
    if np.isnan(p) or p < minimum:
        raise ValueError(f"p must be at least {minimum} (infinity is allowed)")
    return p


def _weights(weights, n):
    if weights is not None and np.iscomplexobj(weights):
        raise ValueError("weights must be real")
    weights = np.full(n, 1 / n) if weights is None else np.asarray(weights, dtype=float)
    if (weights.shape != (n,) or not np.isfinite(weights).all()
            or np.any(weights <= 0) or not np.isclose(weights.sum(), 1, rtol=1e-10, atol=1e-12)):
        raise ValueError("weights must be positive and sum to one; remove zero-mass atoms")
    return weights


def _psd(value, name="matrix", positive=False):
    value = _matrix(value, name)
    if value.shape[0] != value.shape[1]:
        raise ValueError(f"{name} must be square")
    tol = 1e-12 * max(float(np.linalg.norm(value, 2)), np.finfo(float).tiny)
    if np.max(np.abs(value - value.T)) > tol:
        raise ValueError(f"{name} must be symmetric")
    value = (value + value.T) / 2
    eigenvalues, vectors = np.linalg.eigh(value)
    if eigenvalues[0] < -tol or (positive and eigenvalues[0] <= 0):
        raise ValueError(f"{name} must be positive {'definite' if positive else 'semidefinite'}")
    return value, np.maximum(eigenvalues, 0), vectors


def _power_norm(values, order):
    largest = float(np.max(values))
    if largest == 0 or np.isinf(order):
        return largest
    return largest * float(np.sum((values / largest) ** order) ** (1 / order))


def schatten_norm(matrix, order=2):
    """Return the Schatten norm (order >= 1) of a real rectangular matrix."""
    order = _exponent(order, minimum=1)
    return _power_norm(np.linalg.svd(_matrix(matrix), compute_uv=False), order)


def schatten_gauge(moment, p=1):
    """Return gamma_p(S) = (tr S**p)**(1/p), or lambda_max for p=inf.

    S must be PSD. For 1/2 <= p < 1 this is a root-norm gauge, not a
    convex function of S. No matrix inverse is used.
    """
    p = _exponent(p)
    _, values, _ = _psd(moment)
    return _power_norm(values, p)


def schatten_lmo(gradient, p=1, *, rtol=None):
    """Minimize <G,V> + ||V||_{S_{2p}}**2 / 2 over V.

    The returned direction includes the negative sign and the dual-norm
    scale; it is not the unit-polar Muon direction. Except at p=1, singular
    values <= rtol*s_max are treated as zero (default: eps*max(shape)).
    At p=1/2, average equally over numerically tied top singular values.
    These choices fix valid canonical selectors at the exact endpoints;
    a nonzero tolerance introduces the corresponding rank approximation.
    """
    gradient = _matrix(gradient, "gradient")
    p = _exponent(p)
    if rtol is None:
        rtol = np.finfo(float).eps * max(gradient.shape)
    if not np.isfinite(rtol) or not 0 <= rtol < 1:
        raise ValueError("rtol must lie in [0, 1)")
    if p == 1:
        return -gradient.copy()
    u, s, vh = np.linalg.svd(gradient, full_matrices=False)
    if s[0] == 0:
        return np.zeros_like(gradient)
    s = np.where(s > rtol * s[0], s, 0)
    if p == 0.5:
        active = s >= (1 - rtol) * s[0]
        response = s[0] * active / active.sum()
    elif np.isinf(p):
        active = s > rtol * s[0]
        response = s[active].sum() * active
    else:
        q = 1 + 1 / (2 * p - 1)
        normalized = s / s[0]
        norm = np.sum(normalized**q) ** (1 / q)
        response = s[0] * norm * (normalized / norm) ** (q - 1)
        # When q rounds to 1, NumPy evaluates 0**0 as 1; null directions
        # must still stay zero in the canonical operator-limit selector.
        response = np.where(s > 0, response, 0)
    return -(u * response) @ vh


def second_moment(vectors, weights=None):
    """Uncentered second moment sum_i w_i v_i v_i^T (particles are rows)."""
    vectors = _matrix(vectors, "vectors")
    weights = _weights(weights, len(vectors))
    return vectors.T @ (weights[:, None] * vectors)


def velocity_norm(velocity, p=1, weights=None):
    """Return N_mu,p(v) = ||diag(sqrt(w)) V||_{S_{2p}}."""
    velocity = _matrix(velocity, "velocity")
    p = _exponent(p)
    weights = _weights(weights, len(velocity))
    return schatten_norm(np.sqrt(weights)[:, None] * velocity, 2 * p)


def particle_lmo(force, p=1, weights=None, *, rtol=None):
    """Measure LMO for force samples g(x_i), NOT weighted parameter gradients.

    Minimize sum_i w_i <g_i,v_i> + gamma(sum_i w_i v_i v_i^T)/2.
    For an empirical energy differentiated in particle coordinates, first
    divide each row of its Euclidean gradient by the corresponding weight.
    """
    force = _matrix(force, "force")
    root = np.sqrt(_weights(weights, len(force)))[:, None]
    return schatten_lmo(root * force, p, rtol=rtol) / root


def block_lmo(gradient, block_sizes, p=1):
    """Independent column-block LMOs for gamma(S)=sum_b gamma_p(S_bb).

    Each block has its own dual-norm scale. This is not a single common
    time rescaling of independently *unscaled* polar updates.
    """
    gradient = _matrix(gradient, "gradient")
    sizes = tuple(block_sizes)
    if (not sizes or any(not isinstance(s, (int, np.integer)) or s <= 0 for s in sizes)
            or sum(sizes) != gradient.shape[1]):
        raise ValueError("block_sizes must be positive integers summing to the column count")
    blocks = np.split(gradient, np.cumsum(sizes)[:-1], axis=1)
    return np.concatenate([schatten_lmo(block, p) for block in blocks], axis=1)
