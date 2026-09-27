"""Centered Gaussian closures; numerical integration is left to the caller."""

import numpy as np

from .spectral import _matrix, _psd, schatten_lmo


def affine_covariance_rhs(covariance, force_matrix, p=1):
    """Return dSigma/dt for g(x)=H x and the canonical spectral selector.

    Uses a covariance square root, not an inverse force covariance, and
    accepts singular Sigma. No existence/uniqueness assertion at rank loss
    is implicit in this pointwise evaluation of the vector field.
    """
    covariance, values, vectors = _psd(covariance, "covariance")
    force_matrix = _matrix(force_matrix, "force_matrix")
    if force_matrix.shape != covariance.shape:
        raise ValueError("force_matrix and covariance must have the same shape")
    root = (vectors * np.sqrt(values)) @ vectors.T
    velocity_factor = schatten_lmo(force_matrix @ root, p)
    derivative = velocity_factor @ root.T
    return derivative + derivative.T


def gaussian_kl(covariance, target):
    """KL(N(0,Sigma) | N(0,target)); both covariances must be SPD."""
    covariance, _, _ = _psd(covariance, "covariance", positive=True)
    target, _, _ = _psd(target, "target", positive=True)
    if covariance.shape != target.shape:
        raise ValueError("covariances must have the same shape")
    return float((np.trace(np.linalg.solve(target, covariance)) - len(target)
                  + np.linalg.slogdet(target)[1] - np.linalg.slogdet(covariance)[1]) / 2)


def gaussian_kl_rhs(covariance, target, p=1):
    """Spectral KL covariance ODE on the positive definite cone.

    A caller integrating this ODE must monitor positive definiteness;
    this function rejects invalid states rather than projecting silently.
    """
    covariance, _, _ = _psd(covariance, "covariance", positive=True)
    target, _, _ = _psd(target, "target", positive=True)
    if covariance.shape != target.shape:
        raise ValueError("covariances must have the same shape")
    eye = np.eye(len(target))
    hessian = np.linalg.solve(target, eye) - np.linalg.solve(covariance, eye)
    return affine_covariance_rhs(covariance, hessian, p)
