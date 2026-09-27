# Computational Toolbox

The installable `muon_dynamics` package lives in `src/muon_dynamics/`.
The core requires only NumPy and SciPy; PyTorch and CVXPY are optional.
Python 3.10 or later is required.

```bash
python -m pip install -e .
python -m pip install -e '.[transport,notebooks]'  # teaching examples
python -m pip install -e '.[experiments]'         # all paper experiments
```

## Conventions

All matrices and particles are real. A particle array has shape `(n, d)`:
particles are rows, coordinates are columns. Probability weights are strictly
positive and sum to one; remove zero-mass atoms before calling these routines.
`second_moment` does not subtract the mean.

The Schatten gauge is `gamma_p(S) = (tr(S**p))**(1/p)` on PSD matrices,
with `gamma_inf(S) = lambda_max(S)`. Its velocity norm is the Schatten
`2*p` norm of the weighted particle matrix. Root norms are supported for
`p >= 1/2`, including the nonconvex-gauge range `1/2 <= p < 1`.
The static convex solver supports only `p = 1, 2, inf`.

`schatten_lmo(G, p)` returns the **descent direction** minimizing
`<G,V> + ||V||_(2p)**2 / 2`, including its dual-norm scale.
For `G = U diag(s) V.T`, at `p=inf` this is
`-sum(s) * U_active @ V_active.T`, not the unscaled polar update.
No momentum, Newton--Schulz iteration, stochastic gradients, learning-rate
schedule, or claim of practical optimizer equivalence is implicit in this API.

For `p != 1`, singular values below `rtol * s_max` are discarded;
the default is machine epsilon times the larger matrix dimension.
This is a numerical rank convention, not a mathematical regularization theorem.
At `p=1/2`, numerically tied top singular directions are averaged.
Set `rtol=0` to use all strictly positive computed singular values.
Fractional matrix powers amplify roundoff near zero: prefer `velocity_norm(V)`
to forming `V.T @ V` and then taking its small eigenvalues to fractional powers.

## Matrix and Particle APIs

| Function | Meaning |
| --- | --- |
| `schatten_gauge(S, p)` | Gauge of a PSD matrix; validates symmetry and positivity |
| `schatten_norm(A, order)` | Schatten matrix norm, `order >= 1` |
| `schatten_lmo(G, p)` | Matrix LMO, arbitrary rectangular shape |
| `particle_lmo(g, p, weights)` | Measure LMO evaluated on force samples |
| `second_moment(v, weights)` | Weighted uncentered second moment |
| `velocity_norm(v, p, weights)` | Square root of the gauge action |
| `block_lmo(G, block_sizes, p)` | Independent column blocks for a sum block gauge |

The distinction between forces and parameter gradients matters. If
`F(X) = F(sum_i w_i delta_(x_i))`, then `grad_X[i] = w_i * g(x_i)`.
Use `particle_lmo(grad_X / weights[:, None], p, weights)` for the mean-field
clock. With uniform weights, `particle_lmo(g,p) = schatten_lmo(g,p)`;
using an autodifferentiated parameter gradient directly therefore changes
the clock by a factor of the particle count.

```python
import numpy as np
from muon_dynamics import particle_lmo, velocity_norm

g = np.array([[2., 1.], [-1., 3.], [0., 1.]])
w = np.array([.2, .3, .5])
v = particle_lmo(g, p=np.inf, weights=w)
np.testing.assert_allclose((w[:, None] * g * v).sum(),
                           -velocity_norm(v, np.inf, w)**2)
```

`from muon_dynamics.torch import schatten_lmo` provides the same selector for
float32/float64 PyTorch matrices without changing device or dtype. It runs
without autograd tracking and raises on invalid inputs or failed SVDs; it
never silently switches to gradient descent or adds random regularization.
This is an optimizer direction, not an API for differentiating through it.

The sum block gauge gives one nuclear-norm scale per operator block. It is
not, in general, a single time change of independently unscaled polar updates.

## Objectives and Gaussian Closures

`mmd_energy(x,y)` and `mmd_force(x,y)` implement the smoothed energy-distance
kernel `-sqrt(|x-y|**2 + epsilon**2)`. Both accept `weights` and
`target_weights`; the force is the spatial first-variation gradient, not the
weighted coordinate gradient. Pairwise memory is quadratic in the particle
counts; these routines are intended for modest educational experiments.

`affine_covariance_rhs(Sigma,H,p)` evaluates the covariance ODE for `g(x)=Hx`
using a square-root factor. Singular covariances are accepted without inverse
force-covariance regularization. This does not choose a unique continuation
of an ODE across every rank-loss event.

`gaussian_kl(Sigma,target)` and `gaussian_kl_rhs(Sigma,target,p)` concern centered
Gaussians. Both require positive definite covariances. An external integrator
must monitor positivity and time-step error; invalid covariances are rejected,
not projected silently. The small Gaussian example uses SciPy `solve_ivp`.

## Static Transport

```python
from muon_dynamics import solve_transport

result = solve_transport([[-1., 0.], [1., 0.]],
                         [[0., -1.], [0., 1.]], p=float("inf"))
print(result.squared_cost, result.marginal_error, result.solver)
```

`TransportResult` contains `plan`, `squared_cost`, `moment`, `marginal_error`,
`status`, and `solver`. The cost is **squared** spectral Wasserstein distance.
For `p=1`, equal uniform clouds use SciPy assignment; otherwise SciPy HiGHS
solves the transport LP. For `p=2` and `p=inf`, CVXPY solves the convex full
coupling problem, with optional `solver` and `solver_options` arguments.
Inaccurate solver status and excessive marginal residuals raise errors.
An optimal status is numerical, not an exact certified duality gap.
See [CVXPY's function reference](https://www.cvxpy.org/tutorial/functions/index.html).

The full coupling has `n*m` entries. Use small clouds for conic solves.
Unlike classical assignment, spectral transport can split mass even with
equal uniform marginals. The larger matching figures in the paper use a
documented heuristic; they do not call this full-coupling solver.

## Checks

```bash
python -m unittest discover -s tests -v
python scripts/reproduce.py --check
python scripts/reproduce.py --examples --output outputs/examples
python scripts/reproduce.py --all --smoke --output outputs/smoke
```

The test suite checks the LMO Fenchel equality, rank-deficient endpoints,
weight normalization, particle replication, NumPy/PyTorch consistency,
finite-difference MMD gradients, Gaussian dissipation, and full-coupling
transport examples. Optional backend tests are skipped when their extras
are not installed. CI installs both extras so they are exercised there.
