"""Spectral Wasserstein numerical primitives; see docs/toolbox.md for conventions."""

from .spectral import (
    block_lmo, particle_lmo, schatten_gauge, schatten_lmo, schatten_norm,
    second_moment, velocity_norm,
)
from .mmd import mmd_energy, mmd_force
from .gaussians import affine_covariance_rhs, gaussian_kl, gaussian_kl_rhs
from .transport import TransportResult, solve_transport

__all__ = [
    "block_lmo", "particle_lmo", "schatten_gauge", "schatten_lmo",
    "schatten_norm", "second_moment", "velocity_norm", "mmd_energy",
    "mmd_force", "affine_covariance_rhs", "gaussian_kl", "gaussian_kl_rhs",
    "TransportResult", "solve_transport",
]
