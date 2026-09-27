"""Optional PyTorch selectors, preserving device and floating-point dtype.

These are optimizer directions, not differentiable-through-SVD optimizers.
"""

import math
import torch

from .spectral import _exponent


@torch.no_grad()
def schatten_lmo(gradient, p=1, *, rtol=None):
    """Torch counterpart of muon_dynamics.schatten_lmo; see its conventions."""
    p = _exponent(p)
    if (gradient.ndim != 2 or min(gradient.shape) == 0 or gradient.is_complex()
            or gradient.dtype not in (torch.float32, torch.float64)
            or not torch.isfinite(gradient).all()):
        raise ValueError("gradient must be a nonempty finite float32/float64 matrix")
    if rtol is None:
        rtol = torch.finfo(gradient.dtype).eps * max(gradient.shape)
    if not math.isfinite(rtol) or not 0 <= rtol < 1:
        raise ValueError("rtol must lie in [0, 1)")
    if p == 1:
        return -gradient.clone()
    u, s, vh = torch.linalg.svd(gradient, full_matrices=False)
    if s[0] == 0:
        return torch.zeros_like(gradient)
    s = torch.where(s > rtol * s[0], s, 0)
    if p == 0.5:
        active = s >= (1 - rtol) * s[0]
        response = s[0] * active / active.sum()
    elif math.isinf(p):
        active = s > rtol * s[0]
        response = s[active].sum() * active
    else:
        q = 1 + 1 / (2 * p - 1)
        normalized = s / s[0]
        norm = normalized.pow(q).sum().pow(1 / q)
        response = s[0] * norm * (normalized / norm).pow(q - 1)
        response = torch.where(s > 0, response, 0)
    return -(u * response) @ vh
