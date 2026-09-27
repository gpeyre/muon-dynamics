"""Exercise notebook-only numerical helpers without plotting or training."""

import ast
import json
from pathlib import Path
import unittest

import numpy as np
from scipy.integrate import trapezoid


class NumpyWithoutTrapz:
    """Reproduce the NumPy 2.4 removal even when testing with older NumPy."""

    def __getattr__(self, name):
        if name == "trapz":
            raise AttributeError("np.trapz is unavailable in NumPy >= 2.4")
        return getattr(np, name)


class NotebookHelperTests(unittest.TestCase):
    def test_mlp_angular_density_without_numpy_trapz(self):
        path = Path(__file__).resolve().parents[1] / "python/mlp/mlp_spectral_flow_relu.ipynb"
        notebook = json.loads(path.read_text())
        functions = []
        for cell in notebook["cells"]:
            if cell["cell_type"] == "code":
                source = cell["source"]
                source = source if isinstance(source, str) else "".join(source)
                functions.extend(node for node in ast.parse(source).body
                                 if isinstance(node, ast.FunctionDef)
                                 and node.name == "circular_parzen_density_from_X")
        self.assertEqual(len(functions), 1)
        scope = {"np": NumpyWithoutTrapz()}
        exec(compile(ast.Module(body=functions, type_ignores=[]), str(path), "exec"), scope)
        density = scope["circular_parzen_density_from_X"]
        grid = np.linspace(0, 2*np.pi, 256)
        particles = np.array([[1., 1., 0.], [-2., 0., 1.], [0.5, 0., -1.]])
        values = density(particles, grid)
        self.assertTrue(np.isfinite(values).all())
        self.assertTrue((values >= 0).all())
        self.assertAlmostEqual(trapezoid(values, grid), 1, places=12)
        np.testing.assert_array_equal(density(np.zeros((3, 3)), grid), np.zeros_like(grid))


if __name__ == "__main__":
    unittest.main()
