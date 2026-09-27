"""Mathematical contracts, degeneracies, and optional backend consistency."""

import importlib.util
import unittest

import numpy as np
from numpy.testing import assert_allclose

from muon_dynamics import (
    affine_covariance_rhs, block_lmo, gaussian_kl, gaussian_kl_rhs,
    mmd_energy, mmd_force, particle_lmo, schatten_gauge, schatten_lmo,
    schatten_norm, second_moment, solve_transport, velocity_norm,
)

P_VALUES = (0.5, 0.75, 1, 2, 4, np.inf)


class SpectralTests(unittest.TestCase):
    def test_fenchel_equality_and_random_competitors(self):
        rng = np.random.default_rng(14)
        for shape in ((7, 3), (2, 5), (1, 1)):
            for g in (rng.normal(size=shape), np.zeros(shape)):
                for p in P_VALUES:
                    with self.subTest(shape=shape, p=p):
                        v = schatten_lmo(g, p)
                        q = np.inf if p == 0.5 else (1 if np.isinf(p) else 2*p/(2*p-1))
                        dual = schatten_norm(g, q)
                        action = schatten_norm(v, 2*p)**2
                        assert_allclose(action, dual**2, rtol=2e-12, atol=1e-12)
                        assert_allclose(np.sum(g*v), -action, rtol=2e-12, atol=1e-12)
                        for _ in range(3):
                            w = rng.normal(size=shape)
                            self.assertGreaterEqual(np.sum(g*w) + schatten_norm(w, 2*p)**2/2,
                                                    -dual**2/2 - 1e-12)

    def test_rank_support_and_tied_endpoint(self):
        g = np.diag([3., 0., 0.])
        assert_allclose(schatten_lmo(g, np.inf), -g)
        assert_allclose(schatten_lmo(np.diag([3., 3., 1.]), 0.5), np.diag([-1.5, -1.5, 0]))
        for p in P_VALUES:
            assert_allclose(schatten_lmo(1e-150*g, p), 1e-150*schatten_lmo(g, p), atol=1e-162)

    def test_orthogonal_equivariance_and_large_p(self):
        rng = np.random.default_rng(9)
        left, _ = np.linalg.qr(rng.normal(size=(4, 4)))
        right, _ = np.linalg.qr(rng.normal(size=(3, 3)))
        g = np.r_[np.diag([4., 2., 0.]), np.zeros((1, 3))]
        for p in P_VALUES:
            assert_allclose(schatten_lmo(left@g@right, p),
                            left@schatten_lmo(g, p)@right, atol=2e-12)
        assert_allclose(schatten_lmo(g, 1e308), schatten_lmo(g, np.inf), atol=1e-12)

    def test_core_import_does_not_load_optional_backends(self):
        import subprocess
        import sys
        result = subprocess.run([sys.executable, "-c",
                                 "import muon_dynamics,sys; "
                                 "assert 'torch' not in sys.modules; "
                                 "assert 'cvxpy' not in sys.modules"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_particle_weights_and_replication(self):
        g = np.array([[2., 1.], [0., -1.], [3., 2.]])
        w = np.array([0.2, 0.3, 0.5])
        for p in P_VALUES:
            v = particle_lmo(g, p, w)
            assert_allclose(np.sum(w[:, None]*g*v), -velocity_norm(v, p, w)**2, atol=1e-12)
            assert_allclose(schatten_gauge(second_moment(v, w), p), velocity_norm(v, p, w)**2,
                            # Forming V^T V squares the condition number; its
                            # tiny eigenvalue errors are amplified for p<1.
                            rtol=3e-8 if p < 1 else 1e-12, atol=1e-12)
            repeated = particle_lmo(np.repeat(g, 2, axis=0), p)
            assert_allclose(repeated[::2], particle_lmo(g, p), atol=1e-12)
        assert_allclose(block_lmo(g, [1, 1], np.inf), -g)

    def test_validation(self):
        for g in ([1, 2], [[np.nan]], [[1j]], np.empty((0, 2))):
            with self.assertRaises(ValueError):
                schatten_lmo(g)
        for p in (0.49, -np.inf, np.nan):
            with self.assertRaises(ValueError):
                schatten_lmo([[1]], p)
        for w in ([0., 1.], [-1., 2.], [1., 1.]):
            with self.assertRaises(ValueError):
                particle_lmo(np.ones((2, 2)), weights=w)
        with self.assertRaises(ValueError):
            schatten_gauge(np.diag([1, -0.1]))
        with self.assertRaises(ValueError):
            block_lmo(np.eye(2), [3])

    @unittest.skipUnless(importlib.util.find_spec("torch"), "optional torch extra")
    def test_torch_matches_numpy(self):
        import torch
        from muon_dynamics.torch import schatten_lmo as torch_lmo
        for dtype in (torch.float32, torch.float64):
            for g in (np.diag([3., 0., 0.]), np.arange(12.).reshape(4, 3), np.zeros((2, 3))):
                tensor = torch.tensor(g, dtype=dtype)
                for p in P_VALUES:
                    actual = torch_lmo(tensor, p)
                    self.assertEqual(actual.dtype, dtype)
                    assert_allclose(actual.numpy(), schatten_lmo(g, p), atol=3e-5, rtol=3e-5)


class DynamicsTests(unittest.TestCase):
    def test_weighted_mmd_derivative(self):
        rng = np.random.default_rng(42)
        x, y = rng.normal(size=(5, 2)), rng.normal(size=(4, 2))
        w = np.arange(1, 6) / 15
        direction = rng.normal(size=x.shape)
        eps = 1e-6
        derivative = (mmd_energy(x+eps*direction, y, weights=w)
                      - mmd_energy(x-eps*direction, y, weights=w))/(2*eps)
        force = mmd_force(x, y, weights=w)
        assert_allclose(derivative, np.sum(w[:, None]*force*direction), atol=1e-8)
        assert_allclose(mmd_force(x, x, weights=w, target_weights=w), 0, atol=1e-14)
        self.assertAlmostEqual(mmd_energy(x, x, weights=w, target_weights=w), 0)
        for p in P_VALUES:
            self.assertLess(np.sum(w[:, None]*force*particle_lmo(force, p, w)), 0)

    def test_gaussian_dissipation(self):
        sigma = np.array([[2., 0.4], [0.4, 1.]])
        target = np.array([[0.8, -0.2], [-0.2, 1.5]])
        h = np.linalg.inv(target) - np.linalg.inv(sigma)
        vals, vecs = np.linalg.eigh(sigma)
        root = (vecs*np.sqrt(vals)) @ vecs.T
        for p in P_VALUES:
            rhs = gaussian_kl_rhs(sigma, target, p)
            v = schatten_lmo(h@root, p)
            assert_allclose(np.sum(h*rhs)/2, -schatten_norm(v, 2*p)**2, atol=1e-12)
            eps = 1e-6
            derivative = (gaussian_kl(sigma+eps*rhs, target)-gaussian_kl(sigma-eps*rhs, target))/(2*eps)
            assert_allclose(derivative, np.sum(h*rhs)/2, atol=2e-8)
            assert_allclose(gaussian_kl_rhs(target, target, p), 0, atol=1e-14)
        assert_allclose(gaussian_kl_rhs(sigma, target), -h@sigma-sigma@h)
        assert_allclose(affine_covariance_rhs(np.diag([1., 0.]), np.eye(2), np.inf), np.diag([-2., 0.]))
        with self.assertRaises(ValueError):
            gaussian_kl_rhs(np.diag([1., 0.]), target)


class TransportTests(unittest.TestCase):
    def test_trace_assignment_and_weighted_lp(self):
        result = solve_transport([[0.], [2.]], [[3.], [1.]])
        assert_allclose(result.plan, [[0, .5], [.5, 0]])
        self.assertAlmostEqual(result.squared_cost, 1)
        result = solve_transport([[0.]], [[1.], [3.]], target_weights=[.25, .75])
        assert_allclose(result.plan, [[.25, .75]])
        self.assertAlmostEqual(result.squared_cost, 7)
        with self.assertRaises(ValueError):
            solve_transport([[0]], [[1]], p=.75)

    @unittest.skipUnless(importlib.util.find_spec("cvxpy"), "optional transport extra")
    def test_conic_plan_splitting(self):
        # Both permutations have operator cost 2; their mixture has cost 1.
        x, y = [[-1., 0.], [1., 0.]], [[0., -1.], [0., 1.]]
        for p, optimum in ((1, 2), (2, np.sqrt(2)), (np.inf, 1)):
            result = solve_transport(x, y, p)
            self.assertAlmostEqual(result.squared_cost, optimum, places=5)
            self.assertLess(result.marginal_error, 1e-6)
            if p != 1:
                assert_allclose(result.plan, .25, atol=1e-5)


if __name__ == "__main__":
    unittest.main()
