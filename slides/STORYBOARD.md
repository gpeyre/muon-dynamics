# Teaching the paper

## Narrative decision

The paper starts from a general matrix gauge. For a talk, start instead from
the concrete algorithm the audience knows, then ask what geometry makes its
direction a steepest descent. Introduce the general gauge only after showing
polar normalization and its change of clock. Keep one question per slide.

Three candidate orders were considered:

- **Transport first:** economical for an OT audience, but leaves the Muon
  connection unmotivated until late in the talk.
- **Experiments first:** visually immediate, but makes changes in speed easy
  to mistake for geometric improvements.
- **Algorithm, infinitesimal geometry, transport, consequences:** selected.
  The existing measure-optimization slide supplies motivation; the algorithm
  then gives a concrete route back to those measures.

The deck is a modular lecture, approximately 50-65 minutes with demonstrations.
The last technical slides can be skipped for a shorter talk. Equations needed
to follow the argument stay visible. Proof details, regularity assumptions,
sources, and numerical protocols go in speaker notes, with essential caveats
also visible. Red denotes the initial measure, blue the target, and transported
particles interpolate from red to blue. Gray paths carry no method label.

## Four parts

The 31 content slides are preserved. Four roadmap transitions bring the deck
to 35 slides, with exactly four parts:

1. **From Muon to measures:** roadmap at slide 2, content at slides 3-12.
2. **Spectral transport:** roadmap at slide 13, content at slides 14-20.
3. **Learning dynamics:** roadmap at slide 21, content at slides 22-26.
4. **Convergence and limits:** roadmap at slide 27, content at slides 28-35.

Every transition repeats the four animated previews in the same order. Only
the current part is opaque; the other three are faded to 26%. Clicking a
preview jumps to its part. On phones the four columns become a two-by-two
grid. The snippets show, respectively, norm geometry, Gaussian transport,
ReLU training, and P-L envelopes. These are previews of the actual mathematical
objects used later, with their qualifications retained in speaker notes.

The dark title scene replays the existing 256-particle W2 example, with bright
particle heads and short colored tails. The trajectories are not altered for
visual effect. Forward-time replays fade out before restarting; the loops
never reverse a descent. Pause controls and reduced-motion support apply to
the title and all four roadmaps. No additional numerical runs are introduced.

## Slide sequence

The content indices below are stable teaching-item numbers, excluding the four
roadmap transitions. The part ranges above give the displayed slide numbers.

| Content item | Question and takeaway | Experiment | Paper anchor |
| --- | --- | --- | --- |
| 1. Title | Matrix normalization has a transport interpretation. | Animated particle flow. | Abstract |
| 2. Optimization over measures | What are the particles? Samples, neurons, cell states. | Existing MMD flow; particle count and time. | Introduction, Section 5 |
| 3. What Muon does | A matrix update changes singular values, not singular vectors. | Input singular-value ratio versus polar response. | Appendix B; original Muon implementation |
| 4. Removing memory | Small momentum and small time steps lead to an instantaneous force. | A rotating matrix force, EMA coefficient and step size. | Appendix B, momentum |
| 5. Same path, different clock | Raw polar descent and the paper's flow have a state-dependent time change. | Exactly solvable diagonal quadratic; two clocks on the same path. | Section 2, after (2.2) |
| 6. Steepest descent in a norm | The quadratic-penalty LMO is a unit-ball LMO followed by a scalar minimization. | Tangent unit ball and selected descent direction. | Definitions 2.1-2.2 |
| 7. The Schatten family | p=1 preserves the force spectrum; p=infinity equalizes active velocity singular values. | p and force anisotropy; force/velocity spectra. | Appendix A, explicit selectors |
| 8. Rows become particles | The scaling F(X)=n f(alpha_X) makes matrix and empirical velocities agree. | Particle count and p; a selected velocity field. | Proposition 2.5 |
| 9. A finite computation for any measure | Only a d-by-d force second moment is needed. | Force and velocity covariance ellipses; n and p. | Proposition 2.4 |
| 10. A spectral measure flow | The continuity equation transports every particle by the same global normalization rule. | Side-by-side MMD trajectories: trace versus selected p; n and time. | Section 5, MMD |
| 11. An anisotropic quadratic | An affine closure isolates what the normalization changes. | Curvature ratio, p, n and time; matched initial second moments, exact endpoint solutions. | Measure-LMO; Appendix F |
| 12. A cost on displacement covariance | Changing p changes the optimal coupling; splitting is allowed. | Small convex transport solves with p, n and target rotation. | Definition 3.1 |
| 13. Why mass splitting matters | In a two-atom example, splitting strictly improves on every map when p>1. | Coupling mixture, p and interpolation time; exact cost curve. | Exact example of Definition 3.1 |
| 14. Robust quadratic costs | The adversary chooses a PSD cost matrix, not necessarily one projection. | Trace-one Q: orientation and eigenvalue allocation; exact discrete quadratic OT. | Theorem 3.4 |
| 15. Static equals dynamic | Monotonicity and conditional expectation connect a coupling to a velocity field. | Straight versus bent paths and their actions. | Theorem 4.2 |
| 16. Geodesics | Interpolate an optimal coupling, including its split masses. | p, n and time on a computed optimal coupling. | Corollary 4.4 |
| 17. Gaussian transport | The problem reduces to covariance blocks; commuting examples have an explicit answer. | Covariance ellipses, anisotropy, p and interpolation time. | Proposition 3.6; Appendix D |
| 18. Rotated Gaussian transport | Without common axes, p can also change the interpolation. | Target rotation, p and time; joint-Gaussian samples and certified transport values. | Proposition 3.6; Appendix D |
| 19. A metric gradient flow | The LMO gives the energy identity under verification assumptions. | MMD energy curves on the unrescaled metric clock. | Theorem 5.1 |
| 20. Training neurons | Network training moves particles in parameter space, not input space. | ReLU teacher fitting, neuron count, p and time; projected parameter paths. | Section 5, two-layer MLPs |
| 21. Attention heads | A head is another possible parameter particle. | Head count, query/key scale and selected query; attention heatmap and row weights. | Section 5, shallow attention |
| 22. A Gaussian neural network | An affine force closes training on a covariance matrix. | Linear teacher, initial variance, p and time. | Appendix F |
| 23. Independent parameter blocks | Sum and maximum block gauges model different normalization conventions. | Full matrix versus independent blocks; relative block scale. | Appendix B, block gauges |
| 24. Convexity can fail | An optimal operator-cost geodesic can collapse a density to a line. | Translation versus reflection; time and separation. | Appendix H, counterexample |
| 25. P-L without convexity | A slope lower bound gives exponential decay; changing the gauge scale changes the clock. | Guaranteed energy envelope, P-L constant and gauge scale. | Appendix I |
| 26. Local rates and Poincare | Gaussian worst-case rates do not improve for p>=1, despite larger dissipation in many directions. | Rayleigh quotient of a linear-plus-quadratic Gaussian perturbation. | Appendix I, Gaussian targets |
| 27. Beyond the Gaussian | Non-Gaussian radial targets have a strict local-rate gap; a test quotient is not a sharp constant. | Target exponent r, p and cubic amplitude; exact moments at fixed covariance. | Appendix I, generalized Gaussian targets |
| 28. Beyond convex gauges | The root action may remain a norm even when gamma is not convex. | Diagonal root-norm balls across p=1/2 and p=1. | Appendix E, root-norm gauges |
| 29. Finite Newton-Schulz | Stable fixed-scale polynomial updates have convex dissipation, not a fixed squared-norm metric. | Classical cubic iterations and the stable spectral interval. | Appendix B |
| 30. Noise before normalization | Expectation does not commute with a nonlinear LMO. | An exactly enumerable unbiased two-point matrix noise model. | Appendix B, stochastic minibatches |
| 31. What is established | Separate exact geometric results, conditional flow identification, and open approximation questions. | Summary of the chain, with links to paper and code. | Conclusion |

The four additional experiments each resolve a specific ambiguity: the quadratic
separates normalization from a complicated energy; two-atom transport makes
splitting tangible; rotated Gaussians distinguish a special closed form from
the general covariance problem; radial targets contrast the Gaussian no-gap
case with strict improvement. The attention experiment illustrates the
parameterization only, not a training result. For a shorter talk, use
content items 1-10, 12-16, 19-20, 23 and 31, keeping the four roadmaps and
leaving the other teaching items as interactive backup.

## Mathematical safeguards

1. Practical Muon uses momentum, optional Nesterov averaging, finite polynomial
   orthogonalization, block conventions and scale factors. The idealization
   makes these changes explicit. The cubic Newton-Schulz demonstration is
   not presented as the quintic polynomial of the current reference code.
2. For M_{k+1}=m M_k+(1-m)G_k, the discrete relaxation coefficient is
   (1-m)/eta. A finite memory limit uses 1-m ~ eta/tau. Fixed m<1 gives
   vanishing physical memory as eta tends to zero; m tending to zero is a
   particularly transparent route. Limits are formal/local away from rank
   changes, not a global convergence theorem for practical Muon.
3. J_infinity(G)=-||G||_* polar(G). Raw polar descent has the same paths
   only after ds/dt=||G||_* where this factor is positive. A single constant
   time rescaling is not sufficient in general.
4. Forces are uncentered second moments S_g=int gg^T d alpha. Gaussian
   distribution covariances, by contrast, are centered covariances.
5. The particle scaling F=n f is displayed. Increasing n selects a separate
   interacting system, never a visual subsample of a fixed larger system.
6. The operator selector uses the pseudoinverse on the active range and zero
   on its kernel. Measurability does not imply continuity at rank changes.
7. Discrete spectral OT uses the full coupling polytope and convex solvers
   for p=1,2,infinity. Numerical primal/dual gaps and marginal residuals are
   recorded. No assignment heuristic is labeled an exact spectral geodesic.
8. The static cost certificate Q and the force-side inverse-trace certificate
   are different objects. In particular, Muon velocities need not be rank one.
9. All rate comparisons fix the standard gauge normalization. Larger local
   dissipation does not prove pointwise ordering of two distinct trajectories
   or an iteration/runtime advantage.
10. The main flow theorem verifies an existing regular solution. It does not
    prove global PDE well-posedness, particle convergence, or ReLU regularity.
11. The Gaussian transport closed formula is restricted to commuting centered
    covariances; rotated examples instead use certified semidefinite solves.
    Analytic covariance ellipses and sampled particles are distinct objects.
    Gaussian training plots use a linear
    teacher and monitor positive definiteness; no generic Gaussian closure
    is asserted for nonlinear networks.
12. The entropy example refutes convexity along every geodesic, not the
    existence of a good selected geodesic. P-L and geodesic convexity are
    distinct assertions.
13. The Poincare experiment plots test-function quotients, not a numerical
    claim to have computed the infimum over all functions. The radial family
    is rescaled to covariance identity, so a change of variance cannot be
    mistaken for a change of geometry. Its strict-gap statement is the
    paper's theorem, not an inference from the plotted quotients.
14. Nonconvex root-norm gauges retain BB and the metric, but lose a maximum
    of linear costs. Finite-step NS lacks the homogeneity for that metric.
15. Noise is added to the force before normalization. The two-outcome example
    proves bias, not nonconvergence of all stochastic Muon implementations.

## Implementation and verification

- Preserve the existing Reveal.js deck, responsive design and speaker notes.
- Use the repository's numerical toolbox and SciPy/CVXPY for precomputed
  trajectories and transport. Use explicit formulas for small analytic demos.
- Keep article experiments and private drafts untouched. No large training run.
- Check monotone sampled energies, finite coordinates, positive Gaussian
  covariances, coupling feasibility and primal/dual agreement. Compare selected
  MMD runs at tighter tolerances and selected ReLU runs at half the time step.
- Test every slide at presentation and mobile sizes. Verify canvas pixels,
  sliders, playback, reset, links, mathematical rendering and deep-link
  navigation. Enforce font floors instead of shrinking long equations to fit.
- Keep data provenance, theorem assumptions and source pointers in the notes
  and numerical README so the opening slide remains accessible.
