const tex = String.raw;
const escape = value => value.replaceAll('&', '&amp;').replaceAll('"', '&quot;').replaceAll('<', '&lt;');
const eq = (value, size = '') => `<div class="equation ${size}" data-math="${escape(value)}"></div>`;
const inline = value => `<span data-math="${escape(value)}"></span>`;
const text = value => `<p>${value}</p>`;
const note = value => `<p class="qualification">${value}</p>`;
const range = (key, label, min, max, step, value, labels) => ({ key, label, min, max, step, value, labels });
const p = (value = 2) => range('p', 'p', 0, 4, 1, value, ['1', '1.5', '2', '4', '\\infty']);
const time = (max = 1, value = 0) => range('time', 't', 0, max, max / 200, value);
const n = () => range('n', 'n', 0, 3, 1, 2, ['16', '32', '64', '128']);
const otP = () => range('p', 'p', 0, 2, 1, 2, ['1', '2', '\\infty']);

export const teachingSlides = [
  {
    id: 'muon', title: 'What Muon does to a matrix', demo: 'polar',
    body: text('Momentum averages the gradient. Orthogonalization changes its singular values.')
      + eq(tex`M_{k+1}=mM_k+(1-m)G_k`)
      + eq(tex`X_{k+1}=X_k-\eta\,\mathrm{Orth}(M_{k+1})`)
      + eq(tex`G=U\operatorname{diag}(s_i)W^\top`)
      + eq(tex`\mathrm{pol}(G)=UW^\top`)
      + note('Compact SVD: each positive singular value becomes 1. Practical Muon uses an approximate polynomial map, often with Nesterov momentum.'),
    controls: [range('ratio', 's_2/s_1', .01, 1, .01, .2)],
    source: 'Appendix B; Jordan et al., Muon',
    notes: 'G is a rectangular parameter-gradient matrix. The SVD is compact over positive singular values, and the partial polar factor is zero on the inactive subspaces. The displayed EMA version suppresses Nesterov, weight decay and fixed shape-dependent learning-rate factors. The reference implementation uses a finite quintic iteration, not an exact SVD or the classical cubic Newton-Schulz iteration. Primary reference: https://github.com/KellerJordan/Muon/blob/master/muon.py .',
  },
  {
    id: 'memory', title: 'From memory to an instantaneous force', demo: 'memory',
    body: text('Removing momentum makes the direction depend on the current force.')
      + eq(tex`m\to0:\quad M_{k+1}\to G_k`)
      + eq(tex`\eta\to0:\quad \frac{dX}{ds}=-\mathrm{pol}(\nabla F(X))`, 'small')
      + text('A finite memory time is a different limit:')
      + eq(tex`1-m\sim\eta/\tau,\qquad\tau\dot M+M=\nabla F(X)`, 'small')
      + note('Formal limits in regular fixed-rank regimes. Fixed m < 1 also gives vanishing physical memory as the step shrinks.'),
    controls: [range('momentum', 'm', 0, .98, .01, .8), range('step', '\\eta', .02, .3, .01, .08)],
    source: 'Appendix B: momentum',
    notes: 'The demonstration feeds an externally prescribed rotating 2-by-2 orthogonal force into the exact EMA recurrence; it is a response experiment, not a training-convergence theorem. M_0=G_0 removes the zero-buffer transient. For fixed m<1, the memory in physical time is O(eta), equivalently eta/|log m| for the exponential decay convention. To retain tau>0, use m=1-eta/tau+o(eta). Polar continuity requires staying away from loss of rank. Weight decay and stochastic gradients are absent.',
  },
  {
    id: 'clocks', title: 'The same path can have two clocks', demo: 'clocks',
    body: eq(tex`\frac{dX}{ds}=-\mathrm{pol}(G)`)
      + eq(tex`\frac{dX}{dt}=-\|G\|_{S_1}\,\mathrm{pol}(G)`)
      + eq(tex`\frac{ds}{dt}=\|\nabla F(X(t))\|_{S_1}>0`)
      + text('The paper studies the second clock: steepest descent for a squared norm.')
      + note('Same deterministic path away from stationarity, generally not the same time parametrization. No runtime comparison follows.'),
    controls: [time(2, .35)],
    source: 'Section 2; Appendix B: time scales',
    notes: 'Exact demonstration: F(X)=||X||_F^2/2, X=diag(a,b), X(0)=diag(2,1). Raw polar flow is (max(2-s,0),max(1-s,0)). For the metric flow, let t*=log(3)/2. Before t*, s(t)=1.5(1-exp(-2t)); afterwards a(t)=exp(-(t-t*)), b=0 and s(t)=2-a(t). The canonical inactive direction remains zero. This explicitly selected solution illustrates the clock, not uniqueness at a rank change. The metric curve reaches its minimum only asymptotically whereas the raw one reaches it at s=2.',
  },
  {
    id: 'steepest', title: 'Steepest descent depends on the norm', demo: 'norm',
    body: eq(tex`\mathrm N(V)=\sqrt{\gamma(V^\top V)}`)
      + eq(tex`\mathrm J_\gamma(G)\in\arg\min_V\Bigl[\langle G,V\rangle_F+\tfrac12\mathrm N(V)^2\Bigr]`, 'small')
      + text('Choose a direction on the unit ball, then choose its speed.')
      + eq(tex`U_G\in\arg\min_{\mathrm N(U)\le1}\langle G,U\rangle_F`, 'small')
      + eq(tex`\mathrm J_\gamma(G)=\mathrm N^*(G)\,U_G`)
      + note('Main assumption: gamma is positive, convex, one-homogeneous and Loewner-monotone on PSD matrices.'),
    controls: [p(), range('angle', '\\theta', 10, 80, 1, 32)],
    source: 'Definitions 2.1-2.2; scaled unit-ball LMO',
    notes: 'This is a two-dimensional diagonal matrix slice. N(diag(v))=||v||_(2p). The dashed line is a supporting hyperplane and the dot is the unit-ball minimizer, not the fully scaled J. The quadratic-penalty terminology LMO is an abuse of the canonical linear oracle; optimizing r>=0 in -r N*(G)+r^2/2 yields r=N*(G). Loewner monotonicity ensures the displayed square-root action is a norm for the main convex-gauge setting.',
  },
  {
    id: 'spectrum', title: 'One exponent connects gradient descent and Muon', demo: 'spectrum',
    body: eq(tex`\gamma_p(S)=\|S\|_{S_p},\quad\mathrm N_p(V)=\|V\|_{S_{2p}}`, 'small')
      + eq(tex`q=(2p)',\qquad c=\|s\|_q^{2-q}`)
      + eq(tex`\mathrm J_p(G)=-c\,U\operatorname{diag}(s_i^{q-1})W^\top`, 'small')
      + eq(tex`\begin{aligned}p=1:&\quad -G\\p=\infty:&\quad-\|G\|_{S_1}\,\mathrm{pol}(G)\end{aligned}`, 'small')
      + note('Only active singular directions are equalized at the operator endpoint. The canonical selector is zero on the kernel.'),
    controls: [p(), range('ratio', 's_2/s_1', .01, 1, .01, .12)],
    source: 'Appendix A: explicit Schatten selectors',
    notes: 'The formula uses the compact SVD. For G=0 the selector is zero. At p=infinity q=1, so all positive output singular values equal the nuclear norm of G. The chart shows the magnitude of the descent response, hence positive bars despite J having a negative sign. At rank loss the operator selector can be discontinuous and minimizers can be nonunique.',
  },
  {
    id: 'particles', title: 'A matrix whose rows are particles', demo: 'field',
    body: text('Each row of X is one parameter particle.')
      + eq(tex`\alpha_X=\frac1n\sum_i\delta_{x_i},\qquad F(X)=n\,f(\alpha_X)`, 'small')
      + eq(tex`g_\alpha=\nabla_x\frac{\delta f}{\delta\alpha},\qquad G_i=g_{\alpha_X}(x_i)^\top`, 'small')
      + eq(tex`\nabla F(X)=G,\qquad \dot X=\mathrm J_p(G)`)
      + text('Global normalization couples the particles through their force matrix.')
      + note('The identity uses a transport chain rule. At collisions, coincident atoms must receive the same selected velocity.'),
    controls: [p(), n()],
    source: 'Proposition 2.5: finite-width interpretation',
    notes: 'The rows of G are the measure force, not the Euclidean gradient of f(alpha_X), which is G/n. Scaling F=n f makes the matrix and measure conventions agree without an extra n-dependent clock. The arrows are initial MMD velocities computed by the toolbox. A common display scale, shared across p and n, is used for all arrows.',
  },
  {
    id: 'measure-lmo', title: 'Infinitely many particles, one small matrix', demo: 'covariance',
    body: eq(tex`S_g=\int g(x)g(x)^\top\,d\alpha(x)`)
      + eq(tex`A_g=P_g\,\mathrm J_\gamma(S_g^{1/2})`)
      + eq(tex`\mathcal J_\gamma^\alpha(g)(x)=A_g^\top S_g^{\dagger/2}g(x)`, 'small')
      + text('Apply the matrix LMO to one d by d matrix. The number of particles disappears from this computation.')
      + note(`${inline('P_g')} projects onto the range of the uncentered moment ${inline('S_g')}. The dagger denotes the pseudoinverse; at zero force, select zero.`),
    controls: [p(4), n()],
    source: 'Proposition 2.4: finite-dimensional Measure-LMO',
    notes: 'Proof idea: represent h by T_h:a->a dot h in L2(alpha). Project T_h onto range(T_g). The pairing with g is unchanged and its Gram matrix decreases in Loewner order. For any unrestricted matrix minimizer B=J_gamma(sqrt(S_g)), A=P_g B has the same linear pairing and no larger gamma(A^T A), hence is also minimizing and satisfies A=P_g A. Thus the shorter displayed expression is exactly the finite-dimensional proposition, not an inverse-trace formula. The velocity norm is N_alpha(v)^2=gamma(int vv^T d alpha). For Muon, v=-tr(sqrt(S_g)) S_g^(dagger/2)g, so int vv^T=tr(sqrt(S_g))^2 P_g. Ellipses depict square-root second moments, not Gaussian confidence regions.',
  },
  {
    id: 'spectral-flow', title: 'A spectral flow of measures', demo: 'flow', wide: true,
    body: eq(tex`\partial_t\alpha_t+\operatorname{div}(\alpha_t v_t)=0`)
      + eq(tex`v_t=\mathcal J_{\gamma_p}^{\alpha_t}(g_{\alpha_t})`)
      + note('Same initial particles, target and metric time. This evolution rule is not by itself a global well-posedness or particle-limit theorem.'),
    controls: [p(4), n(), time(8)],
    source: 'Section 2: normalized PDE; Section 5: MMD flows',
    notes: 'Side-by-side traces use the same target, initial particles and physical metric time. Left p=1; right selected p. Separate simulations are used for each n,p. The smoothed energy-distance kernel is -sqrt(|x-y|^2+0.03^2), with 1024 fixed target samples. Adaptive RK45, rtol=2e-6, atol=2e-8, max step .08, T=8. Every saved energy decreases. At n=32, both endpoint exponents were rerun at 100-times tighter tolerances and half the maximum step: maximum coordinate RMS differences are below 1.7e-5, relative final energy errors below 7e-6. No initial-rate or clock matching is applied. For Muon the explicit field is -tr(sqrt(S_g)) S_g^(dagger/2) g. These small experiments are not runtime evidence.',
  },
  {
    id: 'quadratic', title: 'An anisotropic quadratic landscape', demo: 'quadratic', wide: true,
    body: eq(tex`f(\alpha)=\tfrac12\int(x_1^2+\kappa x_2^2)\,d\alpha`, 'small')
      + eq(tex`S_{x,0}=I_2,\qquad x_t=C_t x_0`)
      + note('An exactly closed covariance evolution. The minimum is the blue point mass at the origin; each particle count has the same initial second moment.'),
    controls: [p(4), range('condition', '\\kappa', 0, 3, 1, 2, ['1', '4', '16', '32']), range('n', 'n', 0, 2, 1, 1, ['16', '64', '256']), time(2, .15)],
    source: 'A solvable example of the measure-LMO; Appendix F: affine closure',
    notes: 'H=diag(1,kappa), force g=Hx. An affine flow closes on C, with Cdot=J_p(HC), C0=I. The initial empirical clouds are centered and whitened separately, so their second moment is exactly I: this closure is exact for each displayed particle system, not only in a Gaussian limit. At p=1, C=diag(exp(-t),exp(-kappa t)); at p=infinity, C=exp(-(1+kappa)t)I. For 1<p<infinity, write q=(2p) prime and c_i=(1-h_i^(q-1)tau)_+^(1/(2-q)); tau dot=(2-q)||HC||_q^(2-q). This scalar ODE handles extinction without negative standard deviations. A common metric clock is used. Faster decay here is an example, not a uniform comparison over energies or an iteration-count result.',
  },
  {
    id: 'static', title: 'Transport pays for a displacement covariance', demo: 'transport',
    body: eq(tex`S_\pi=\int (y-x)(y-x)^\top\,d\pi(x,y)`)
      + eq(tex`\mathsf W_{\gamma}(\alpha,\beta)^2=\min_{\pi\in\Pi(\alpha,\beta)}\gamma(S_\pi)`, 'small')
      + eq(tex`\gamma_1(S)=\operatorname{tr}S,\qquad\gamma_\infty(S)=\lambda_{\max}(S)`, 'small')
      + text('Trace charges total squared displacement. The operator norm charges the largest directional second moment.')
      + note('The optimization is over couplings, not only permutations or maps. A source atom may split its mass.'),
    controls: [otP(), range('n', 'n', 0, 1, 1, 0, ['8', '16']), range('rotation', '\\theta', 0, 2, 1, 1, ['0^\\circ', '30^\\circ', '60^\\circ'])],
    source: 'Definition 3.1; discrete spectral transport',
    notes: 'Uniform clouds, full n-by-n coupling. p=1 is solved by SciPy assignment; p=2 and infinity by the toolbox CVXPY conic solver. A separate convex robust dual gives a numerical primal-dual gap and the marginal error is checked. Small edge masses below the display threshold are omitted from the picture only, not from the numerical costs or interpolated measure. Source and target colors are red and blue.',
  },
  {
    id: 'splitting', title: 'Optimal transport can split atoms', demo: 'splitting', wide: true,
    body: eq(tex`\alpha=\tfrac12(\delta_{-e_1}+\delta_{e_1}),\quad\beta=\tfrac12(\delta_{-e_2}+\delta_{e_2})`, 'small')
      + eq(tex`\mathsf W_{\gamma_p}^2=2^{1/p},\qquad\text{every map costs }2`, 'small')
      + note('For p > 1 the optimal coupling splits each atom equally. At p = 1, every coupling has the same cost. The selected interpolation is a geodesic only when its coupling is optimal.'),
    controls: [p(4), range('mix', '\\theta', 0, 1, .01, .5), time(1, .35)],
    source: 'Exact two-atom example of Definition 3.1',
    notes: 'Order the source atoms as -e1,+e1 and targets as -e2,+e2. Every feasible coupling is pi_theta=1/2[[theta,1-theta],[1-theta,theta]]. Its displacement moment is [[1,1-2theta],[1-2theta,1]], with eigenvalues 2theta and 2(1-theta). Thus the Schatten cost is ||(2theta,2(1-theta))||_p. Strict convexity for 1<p<infinity, or the maximum at p=infinity, gives the unique minimum theta=1/2, value 2^(1/p). A map is theta=0 or 1 and costs 2. In particular splitting halves the squared operator transport cost. This is an exact analytic example, without entropy regularization or a numerical solver. Moving markers carry their coupling masses.',
  },
  {
    id: 'robust', title: 'An adversary chooses the quadratic cost', demo: 'robust',
    body: eq(tex`\gamma(S)=\max_{Q\in\mathcal K_\gamma}\operatorname{tr}(QS)`)
      + eq(tex`\mathsf W_\gamma^2=\max_{Q\in\mathcal K_\gamma}\min_{\pi\in\Pi(\alpha,\beta)}\operatorname{tr}(QS_\pi)`, 'small')
      + eq(tex`\mathcal K_p=\{Q\succeq0:\|Q\|_{S_{p'}}\le1\}`, 'small')
      + eq(tex`p=\infty:\quad Q\succeq0,\quad\operatorname{tr}Q\le1`)
      + note('The maximizing cost need not be rank one. It is not the force-normalization matrix.'),
    controls: [range('weight', 'w', 0, 20, 1, 15), range('angle', '\\theta', 0, 72, 1, 12)],
    source: 'Theorem 3.4: cost-robust representation',
    notes: 'p prime denotes the Holder dual of p, not q=(2p) prime. In the demo Q=R_theta diag(w,1-w) R_theta^T, with w in increments .05 and theta in increments 2.5 degrees. At each grid point the inner quadratic OT is an exact discrete assignment. The displayed optimum is from the continuous convex conic problem, not the maximum on this grid. A saddle-point cost certificate is supported on the top eigenspace of the optimal displacement covariance; multiplicity allows a full-rank Q.',
  },
  {
    id: 'bb', title: 'The same cost has a dynamic formulation', demo: 'action',
    body: eq(tex`\mathcal N_\alpha(v)^2=\gamma\!\left(\int vv^\top d\alpha\right)`, 'small')
      + eq(tex`\mathsf W_\gamma(\alpha_0,\alpha_1)^2=\inf_{\alpha,v}\int_0^1\mathcal N_{\alpha_t}(v_t)^2\,dt`, 'small')
      + text('Fix the endpoints and impose the continuity equation. An optimal coupling yields straight paths with velocity')
      + eq(tex`v_t(z)=\mathbb E[y-x\mid(1-t)x+ty=z]`, 'small')
      + note('Conditional averaging decreases the second moment. Integrating velocities gives the reverse inequality.'),
    controls: [otP(), range('bend', 'b', 0, 1, .05, .3), time(1, .4)],
    source: 'Theorem 4.2: static-dynamic equivalence',
    notes: 'Endpoints lie in P2. The dynamic infimum is over narrowly continuous curves and Borel square-integrable velocity fields solving the continuity equation. Dynamic-to-static uses superposition on absolutely continuous paths and Jensen. Static-to-dynamic uses the conditional expectation formula, not a possibly multivalued particle velocity. The illustration bends each edge by b sin(pi t)e2 and evaluates its Lagrangian action by quadrature. This is an admissible path action for these finite generic curves, with only isolated coincidences, and is at least the optimal static value.',
  },
  {
    id: 'geodesics', title: 'Optimal couplings generate constant-speed geodesics', demo: 'geodesic',
    body: eq(tex`\alpha_t=((1-t)x+ty)_\sharp\pi_\star`, 'small')
      + eq(tex`\mathsf W_\gamma(\alpha_s,\alpha_t)=|t-s|\,\mathsf W_\gamma(\alpha_0,\alpha_1)`, 'small')
      + text('Particles move along straight segments. Their coupling, and therefore the density evolution, depends on the geometry.')
      + note('These are transport geodesics between fixed endpoints. The curved MMD optimization trajectories shown earlier are gradient flows, not geodesics.'),
    controls: [otP(), range('n', 'n', 0, 1, 1, 0, ['8', '16']), time(1, .45)],
    source: 'Corollary 4.4: geodesics',
    notes: 'The theorem concerns an exact optimal coupling. The visual uses the verified numerical conic solution and therefore is a numerical approximation to that geodesic. Each edge carries its own coupling mass; the moving markers are weighted by that mass. Coincident endpoint masses are aggregated measure-theoretically even though the canvas may draw several markers. The target rotation is fixed at 30 degrees.',
  },
  {
    id: 'gaussian-transport', title: 'Gaussians reduce transport to covariance matrices', demo: 'gaussianTransport',
    body: eq(tex`\alpha_i=\mathcal N(0,\Sigma_i)`)
      + eq(tex`\mathsf W_\gamma^2=\min_K\gamma(\Sigma_0+\Sigma_1-K-K^\top)`, 'small')
      + eq(tex`\begin{pmatrix}\Sigma_0&K\\K^\top&\Sigma_1\end{pmatrix}\succeq0`)
      + text('For commuting covariances, let s denote standard deviations in a common eigenbasis.')
      + eq(tex`\mathsf W_{\gamma_p}^2=\bigl\|((s_{1,i}-s_{0,i})^2)_i\bigr\|_p`, 'small')
      + note('In this commuting example, p changes the distance but not the displayed optimal interpolation.'),
    controls: [p(), range('width', 's_{0,1}', .35, 2.5, .05, 2), time(1, .35)],
    source: 'Proposition 3.6; Appendix D: commuting covariances',
    notes: 'The covariance-block formulation is exact because every admissible K is realized by a joint Gaussian. For commuting centered covariances, the common-coordinate square-root coupling is simultaneously optimal for Schatten gauges. The demo uses Sigma0=diag(width^2,.45^2), Sigma1=diag(.7^2,1.4^2), with interpolated standard deviations. The general noncommuting problem has no such displayed closed formula. The ellipses are one-standard-deviation covariance contours.',
  },
  {
    id: 'rotated-gaussians', title: 'Rotating the target changes the coupling', demo: 'rotatedGaussian', wide: true,
    body: eq(tex`\Sigma_t=(1-t)^2\Sigma_0+t^2\Sigma_1+t(1-t)(K+K^\top)`, 'small')
      + text('An optimal joint Gaussian supplies K. Away from a common eigenbasis, p can change the interpolation itself.')
      + note('The colored ellipses are covariance contours. Points sample the optimal joint Gaussian; this need not be a deterministic transport map.'),
    controls: [otP(), range('rotation', '\\theta', 0, 6, 1, 3, ['0^\\circ', '15^\\circ', '30^\\circ', '45^\\circ', '60^\\circ', '75^\\circ', '90^\\circ']), time(1, .5)],
    source: 'Proposition 3.6 and Appendix D: general Gaussian reduction',
    notes: 'Sigma0=diag(4,.55^2); Sigma1=R_theta diag(.7^2,1.6^2) R_theta^T. Each p=1,2,infinity and angle uses its own full 4-by-4 PSD covariance-block optimization. The independent dual maximizes tr(Q(Sigma0+Sigma1))-2||sqrt(Sigma0) Q sqrt(Sigma1)||_* over the PSD dual ball. All 21 primal-dual gaps are below 5e-8; joint covariance eigenvalues are checked. The formula for Sigma_t is exact for a joint Gaussian with cross covariance K. The interpolated ellipse uses this covariance, not an empirical fit to the displayed points. Numerical roundoff in the joint square root is projected to PSD only for sampling. At commuting angles the optimal cost matches the preceding closed formula, although an operator-cost optimizer need not be unique.',
  },
  {
    id: 'gradient-flow', title: 'The normalization is a metric gradient flow', demo: 'energy',
    body: eq(tex`|\partial f|_\gamma(\alpha)=\mathcal N_\alpha^*(g_\alpha)`)
      + eq(tex`\frac{d}{dt}f(\alpha_t)=-\mathcal N_{\alpha_t}^*(g_{\alpha_t})^2`, 'small')
      + eq(tex`|\dot\alpha_t|_\gamma=|\partial f|_\gamma(\alpha_t)`)
      + text('Energy dissipation equals squared metric speed.')
      + note('Conditional theorem: an existing Lipschitz flow and a uniform quadratic transport expansion of f. Not a global existence theorem.'),
    controls: [p(4), n(), time(8, 2)],
    source: 'Theorem 5.1: gradient-flow identification',
    notes: 'Precise hypotheses: continuous velocity, uniformly globally Lipschitz in space with uniform linear growth on a finite time interval; alpha transported by its characteristic flow; f finite near the curve, with L2 force and a uniform O(int |y-x|^2 d pi) transport Taylor remainder for nearby couplings. The slope upper bound uses barycentric projection; deterministic perturbations give the lower bound. The chain rule and LMO identity give dissipation. BB gives a speed upper bound, and the slope inequality gives equality. These hypotheses do not automatically cover ReLU kinks or operator-endpoint rank changes. The chart is the small smooth-kernel MMD experiment, not a verification of every abstract hypothesis.',
  },
  {
    id: 'relu-training', title: 'Training a distribution of ReLU neurons', demo: 'relu', wide: true,
    body: eq(tex`h_\alpha(z)=\int u\,\mathrm{ReLU}(v^\top z)\,d\alpha(u,v)`, 'small')
      + eq(tex`f(\alpha)=\frac1{2m}\sum_{j=1}^m\bigl(h_\alpha(z_j)-y_j\bigr)^2`, 'small')
      + note('Each particle is a neuron (u,v). One joint parameter block, a shared metric clock, and a three-neuron teacher. ReLU kinks require a separate chain-rule argument.'),
    controls: [otP(), range('n', 'n', 0, 2, 1, 1, ['16', '32', '64']), time(40)],
    source: 'Section 5: mean-field two-layer MLPs',
    notes: 'Small lecture illustration, not a rerun of the article experiment. Inputs z=(z_scalar,1) use 97 equally spaced scalar values in [-1,1]. A three-neuron teacher is fitted by n=16,32,64 students. PyTorch autograd computes the empirical gradient, multiplied by n to recover the measure force; Xdot=J_p(n grad_X f(alpha_X)). The repository Torch Schatten LMO supplies velocities. Heun integration dt=.025, T=40, with decreasing saved losses checked. At n=32, halving dt for p=1 and infinity gives maximum prediction RMS differences below 3.8e-5 and relative final-loss differences below 8e-6. These are refinement checks, not rigorous error bounds. Predictor functions are shown separately from parameter particles, projected onto their two inner coordinates (w,b); marker radius reflects the absolute outer weight, not its sign. At intermediate saved times, displayed predictions are interpolated numerical approximations. ReLU kinks are not covered automatically by the smooth-flow theorem.',
  },
  {
    id: 'attention', title: 'A distribution of attention heads', demo: 'attention', wide: true,
    body: eq(tex`w_{ji}=\operatorname{softmax}_i\!\left(\frac{\langle Qz_j,Kz_i\rangle}{\sqrt{d_H}}\right)`, 'small')
      + eq(tex`\phi(z,x)_j=O^\top\sum_i w_{ji}(x)Vz_i`, 'small')
      + note('Each head x = (Q,K,V,O) is a particle. This illustration shows attention weights, not training; the layer averages head outputs.'),
    controls: [range('n', 'n', 0, 2, 1, 1, ['4', '16', '64']), range('scale', 'c', 0, 30, 1, 20), range('query', 'j', 0, 7, 1, 0, ['1', '2', '3', '4', '5', '6', '7', '8'])],
    source: 'Section 5: mean-field shallow attention',
    notes: 'The demonstration has eight scalar tokens and head parameters Q=c q, K=c k, V=O=1. The same nested q,k samples are used at different head counts. The displayed matrix averages row-stochastic attention matrices over heads. Effective token count is averaged per head and query, rather than computed from the averaged heatmap. c scales both Q and K, so logits scale as c squared. The paper trains a higher-dimensional multi-head teacher; no training result is claimed by this attention-only illustration. For bounded covariates, a finite sixth parameter moment suffices for least-squares force integrability, and preservation of this bound remains an additional requirement.',
  },
  {
    id: 'gaussian-network', title: 'A linear network closes on its covariance', demo: 'network', wide: true,
    body: eq(tex`h_\alpha(z)=\Sigma_{uv}z,\qquad f(\alpha)=\tfrac12(\Sigma_{uv}-1)^2`, 'small')
      + eq(tex`\dot\Sigma_t=A_t\Sigma_t+\Sigma_tA_t^\top`, 'small')
      + note('The force is linear in x = (u,v), so the velocity is linear too. A centered Gaussian remains Gaussian, and its cross-covariance learns the teacher coefficient.'),
    controls: [p(4), range('variance', '\\rho_0', 0, 2, 1, 1, ['0.6', '1', '1.8']), time(4)],
    source: 'Appendix F: Gaussian-preserving linear networks',
    notes: 'Input variance is one and teacher coefficient is one. Sigma0=rho0 I. The numerical solver integrates a factor C with Sigma=CC^T and dot C=J_p(L C), using the repository Schatten LMO and SciPy solve_ivp. This avoids an inverse covariance and keeps the representation positive semidefinite. The selected initial variances and time horizon keep all eigenvalues strictly positive; this is checked. The plotted teacher is a scalar predictor coefficient, not a unique target distribution in parameter space. General nonlinear neural networks do not preserve Gaussianity.',
  },
  {
    id: 'blocks', title: 'The block layout is part of the geometry', demo: 'blocks',
    body: text('Split each parameter particle into blocks x = (u,v).')
      + eq(tex`\gamma_{\rm sum}(S)=\gamma_1(S_{11})+\gamma_2(S_{22})`, 'small')
      + text('The LMO separates: each block has its own dual-norm speed.')
      + eq(tex`\gamma_{\rm max}(S)=\max_b\lambda_{\max}(S_{bb})`)
      + eq(tex`\mathrm J_{\rm max}(G)_b=-c\,\mathrm{pol}(G_b),\quad c=\sum_a\|G_a\|_*`, 'small')
      + note('The maximum gauge follows raw blockwise polar updates with one common clock. The sum gauge generally does not. Both are monotone gauges.'),
    controls: [range('scale', 'c', 0, 11, 1, 3), range('mode', '\\gamma', 0, 2, 1, 1, ['\\mathrm{full}', '\\mathrm{sum}', '\\mathrm{max}'])],
    source: 'Appendix B: block-wise normalization',
    notes: 'The example has a 3-by-4 force matrix partitioned into two 3-by-2 column blocks. c rescales only the second force block. Full means the operator gauge on the joint 4-by-4 covariance. Sum means the sum of block operator gauges, giving independent nuclear scales. Max means the maximum block operator gauge, giving a shared sum-of-nuclear-norms scale. Spectra are reported for each velocity block. A block gauge does not factor the joint law into independent marginals; transport still uses one common coupling. Fixed unequal learning-rate factors can be represented by corresponding weights in the maximum gauge.',
  },
  {
    id: 'convexity', title: 'An optimal geodesic can collapse a density', demo: 'collapse', wide: true,
    body: eq(tex`\alpha_0=\mathrm{Unif}([0,1]\times[-a,a])`)
      + eq(tex`\gamma_\infty(S_T)=\gamma_\infty(S_R)=L^2`, 'small')
      + note(`Translation T and translation-plus-reflection R are optimal when ${inline(tex`L^2\ge4a^2/3`)}. Reflection collapses the midpoint to a line: its KL is infinite. Convexity along every geodesic fails.`),
    controls: [range('mode', 'T', 0, 1, 1, 1, ['\\mathrm{translation}', '\\mathrm{reflection}']), time(1, .4), range('separation', 'L', 1, 3, .1, 1.8)],
    source: 'Appendix H: operator-norm counterexample',
    notes: 'a=.8, so L>=1 satisfies the required inequality. Every coupling costs at least L^2 by the mean horizontal displacement, while both shown maps attain it. The reflection interpolation scales the vertical coordinate by 1-2t. At t=1/2, the distribution is singular and KL to the standard Gaussian is infinite. The translation geodesic stays regular. This refutes convexity along all geodesics, not the existence of a favorable selected geodesic. The canvas uses an analytic rectangle and deterministic point samples only for illustration.',
  },
  {
    id: 'pl', title: 'P-L gives rates without geodesic convexity', demo: 'pl',
    body: eq(tex`|\partial f|_\gamma^2\ge2\kappa(f-f_\star)`)
      + eq(tex`E(t)\le E(0)e^{-2\kappa t}`)
      + eq(tex`\gamma\le C\,\operatorname{tr}\quad\Longrightarrow\quad\kappa_\gamma\ge\kappa_2/C`, 'small')
      + text('A W2 P-L bound transfers to every standard Schatten gauge with p at least 1.')
      + note('E is the energy gap. A global flow with the energy identity also converges in distance. These are guarantees, not an ordering of distinct trajectories.'),
    controls: [range('kappa', '\\kappa_2', .2, 2, .1, 1), range('scale', 'a', .25, 3, .05, 1)],
    source: 'Appendix I: P-L convergence and transfer',
    notes: 'E(t)=f(alpha_t)-inf f. Assume a global energy-identity flow in the complete W_gamma space, lower-semicontinuous f, and PL on its range. The tail-length estimate W_gamma(alpha_t,alpha_infinity)<=sqrt(2E(0)/kappa) exp(-kappa t) gives convergence to a minimizer, not uniqueness. The chart is the theoretical envelope E0 exp(-2 kappa2 t/a), gamma=a gamma_p, p>=1, E0=1, not a simulated curve. The metric scales by sqrt(a), the LMO speed and PL constant by 1/a. KL to a lambda-strongly-log-concave law satisfies W2 lambda-PL by log-Sobolev and hence also operator lambda-PL. Larger dissipation at the same state does not order two distinct evolving states.',
  },
  {
    id: 'poincare', title: 'Gaussian targets reveal the worst-case rate', demo: 'poincare',
    body: eq(tex`\lambda_{\rm P}^{p}\operatorname{Var}_\beta(u)\le\|G_u^{1/2}\|_{S_q}^2`, 'small')
      + eq(tex`G_u=\int\nabla u\nabla u^\top d\beta`, 'small')
      + eq(tex`\beta=\mathcal N(0,I_2),\quad u_\varepsilon=x_1+\varepsilon(x_2^2-1)`, 'small')
      + eq(tex`R_p(\varepsilon)=\frac{\|(1,2|\varepsilon|)\|_q^2}{1+2\varepsilon^2}`)
      + text('For p at least 1, linear tests attain the sharp constant 1. Below 1, the sharp constant is strictly smaller.')
      + note('q is dual to 2p. The curve shows test quotients, not the infimum over all functions.'),
    controls: [range('p', 'p', 0, 4, 1, 4, ['0.5', '0.75', '1', '2', '\\infty']), range('epsilon', '\\varepsilon', 0, 1, .01, .3)],
    source: 'Appendix I: spectral Poincare and Gaussian targets',
    notes: 'The full theorem for nondegenerate Gaussian beta=N(m,Sigma) in d>=2 gives lambdaP^p=1/lambda_max(Sigma) for p>=1 and a strict decrease for .5<=p<1. Rank-one linear gradients explain equality for p>=1. Non-Gaussian radial targets exp(-|x|^r), d>1, r>1, r!=2, have strict improvement for p>1 as proved in the paper. Local entropy dissipation is generally nonlinear for spectral norms; this is not an ordinary linear self-adjoint spectral gap outside the trace case.',
  },
  {
    id: 'radial-poincare', title: 'Beyond the Gaussian: a strict local-rate gap', demo: 'radial', wide: true,
    body: eq(tex`\beta_r(dx)\propto e^{-(|x|/s_r)^r}dx`, 'small')
      + eq(tex`r>1,\ r\ne2,\ p>1:\quad\lambda_{\rm P}^{p}>\lambda_{\rm P}^{1}`, 'small')
      + note('Covariance ' + inline(tex`I_2`) + '. Tests ' + inline(tex`u_a=x_1+a\,x_1(|x|^2-c)`) + ', ' + inline(tex`c=\tfrac12\mathbb E_{\beta_r}|x|^4`) + ', give upper bounds, not sharp constants. The strict comparison is a theorem; the infinity limit is the uniform disk.'),
    controls: [range('radial', 'r', 0, 6, 1, 4, ['1.25', '1.5', '2', '3', '4', '8', '\\infty']), p(4), range('amplitude', 'a', -.25, .25, .005, .04)],
    source: 'Appendix I: generalized Gaussian targets',
    notes: 'In dimension two, scale every target to covariance I. Before scaling, radial moments are E[R^j]=Gamma((j+2)/r)/Gamma(2/r), or 2/(j+2) for the uniform unit disk. After scaling M2=2. The displayed test is u_a=x1+a*x1*(|x|^2-c), c=M4/2, so its linear and cubic terms are orthogonal in L2(beta). Its variance is 1+a^2*(M6-M4^2/2)/2. The diagonal force Gram entries are 1+2a*(4-c)+a^2*(4.5*M4-8*c+c^2), and a^2*M4/2. R_p is the squared Schatten-q norm of its square root divided by this variance, q=(2p) prime. Thus every plotted number is an analytic test quotient, hence an upper bound on the corresponding sharp constant; differences of test quotients do not prove differences of sharp constants. The strict theorem uses compactness and the absence of rank-one-gradient first eigenfunctions for r!=2. The uniform disk has the analogous strict gap. At r=2, all p>=1 have sharp constant 1.',
  },
  {
    id: 'root-norm', title: 'The metric extends beyond convex gauges', demo: 'root',
    body: eq(tex`\mathfrak N_\gamma(T)=\sqrt{\gamma(T^*T)}`)
      + text('A root-norm gauge makes this a norm for every Hilbert-space target.')
      + eq(tex`\gamma(S)=\varphi\!\left(\lambda(S)^{1/2}\right)^2`, 'small')
      + text('For spectral gauges, this is equivalent to a symmetric gauge norm on the square-root eigenvalues.')
      + eq(tex`\gamma_p:\quad\mathfrak N_p=\|\cdot\|_{S_{2p}}\quad\Longleftrightarrow\quad p\ge\tfrac12`, 'small')
      + note(`For ${inline(tex`1/2\le p<1`)}, BB and the metric survive, but a maximum-of-linear-costs representation does not. The thresholds concern dimension at least two.`),
    controls: [range('p', 'p', 0, 6, 1, 2, ['0.25', '0.5', '0.75', '1', '2', '4', '\\infty'])],
    source: 'Appendix E: root-norm characterization and BB',
    notes: 'For non-spectral gauges, the full characterization is that V->sqrt(gamma(V^T V)) is a norm on d-by-d matrices, equivalently gamma(S)=N(sqrt(S))^2 for a left-orthogonally invariant norm N. The spectral version shown uses a symmetric gauge norm varphi on R^d. Root-norm gauges are Loewner-monotone, possibly nonconvex. The diagonal slice uses the l_(2p) ball. Below p=.5, this slice is nonconvex and the root-norm criterion fails. In d=1 all Schatten gauges coincide, so the thresholds are inapplicable.',
  },
  {
    id: 'newton-schulz', title: 'Finite orthogonalization gives a different dissipation', demo: 'ns',
    body: eq(tex`Z_0=G/\alpha,\qquad Z_{k+1}=\tfrac12Z_k(3I-Z_k^\top Z_k)`, 'small')
      + eq(tex`h_1(s)=\frac{3s}{2\alpha}-\frac{s^3}{2\alpha^3}`)
      + text('With fixed scale, the stable interval has a nondecreasing singular-value response.')
      + eq(tex`D^*(G)=\sum_i\int_0^{s_i(G)}h_k(s)\,ds`, 'small')
      + note(`On ${inline(tex`\|G\|_{\rm op}\le\alpha`)}, a convex extension gives generalized dissipative descent. For ${inline(tex`k\ge1`)}, the map is not one-homogeneous: this is not a fixed ${inline(tex`\mathsf W_\gamma`)} gradient flow.`),
    controls: [range('iterations', 'k', 0, 6, 1, 1), range('ratio', 's/\\alpha', 0, 1.8, .01, .65)],
    source: 'Appendix B: fixed-scale Newton-Schulz dissipation',
    notes: 'This demonstration uses the classical cubic Newton-Schulz iteration with alpha=1, not the optimized quintic coefficients of the practical reference implementation. For k>=1 on [0,alpha], h_k is nonnegative, nondecreasing and at most one; extending h_k by one gives a convex primitive and a globally convex spectral force dissipation. The covariance potential Psi(S) need not be convex; convexity is on the force variable G. A priori control of the force covariance is still needed to stay in the stable region. Adaptive scaling requires a separate analysis. The plot clips diverging unstable responses to the displayed vertical range.',
  },
  {
    id: 'noise', title: 'Unbiased forces can produce biased velocities', demo: 'noise',
    body: eq(tex`\mathbb E\xi=0\quad\not\Rightarrow\quad\mathbb E\mathcal J_\gamma(g+\xi)=\mathcal J_\gamma(g)`, 'small')
      + eq(tex`G=\operatorname{diag}(1,0.3),\quad\xi=\operatorname{diag}(0,Z)`)
      + eq(tex`Z=\begin{cases}3\rho&\text{with probability }1/4,\\-\rho&\text{with probability }3/4.\end{cases}`, 'small')
      + text('Normalize each random force first, then average its velocity. The result need not point in the deterministic direction.')
      + note('The toy model demonstrates bias, not failure of every stochastic Muon variant. Fixed-variance, fast-resampled force noise does not automatically generate a Laplacian.'),
    controls: [range('rho', '\\rho', 0, 1, .01, .6), p(4)],
    source: 'Appendix B: stochastic minibatches',
    notes: 'The bars exactly enumerate two diagonal-matrix outcomes, using the same squared-norm Schatten selector as the theory. Both G+xi samples are normalized before expectation. For p=1 linearity removes the bias. For p=infinity signs can change across the noisy second singular direction, and the expected second velocity may even reverse despite a positive mean force. A shared minibatch generates an entire correlated random force field in a measure model. Momentum instead requires a joint position-force law and a phase-space Liouville equation; the position marginal alone is generally not a W_gamma gradient flow.',
  },
  {
    id: 'conclusion', title: 'A geometry for normalized mean-field descent', demo: null,
    body: `<div class="summary-row"><h3>Matrix normalization</h3>${eq(tex`\mathrm N(V)^2=\gamma(V^\top V)`)}${text('A norm determines a direction and a clock.')}</div>`
      + `<div class="summary-row"><h3>Particles and measures</h3>${eq(tex`\partial_t\alpha+\operatorname{div}(\alpha\mathcal J_\gamma^\alpha(g_\alpha))=0`, 'small')}${text('The same covariance-based rule acts at every width.')}</div>`
      + `<div class="summary-row"><h3>A transport metric</h3>${eq(tex`\mathsf W_\gamma^2=\min_\pi\gamma(S_\pi)=\inf_{\alpha,v}\int\mathcal N_\alpha(v)^2dt`, 'small')}${text('Static transport, geodesics and conditional gradient-flow identification.')}</div>`
      + note('Still open in general: global well-posedness, quantitative particle limits, stochastic normalized flows, and practical discretization guarantees.')
      + `<div class="closing-links"><a href="https://arxiv.org/abs/2604.04891" target="_blank" rel="noopener">Paper <i data-lucide="arrow-up-right"></i></a><a href="https://github.com/gpeyre/muon-dynamics" target="_blank" rel="noopener">Toolbox and slides <i data-lucide="arrow-up-right"></i></a></div>`,
    source: 'Muon Dynamics as a Spectral Wasserstein Flow',
    notes: 'The work builds a deterministic, idealized, continuous-time geometry. The matrix-to-empirical correspondence is exact under a transport chain rule. Extension of the constitutive rule to arbitrary laws is not a proved particle-limit convergence theorem. The static-dynamic and metric results hold for monotone convex gauges and extend to root-norm gauges. The gradient-flow theorem is conditional on a regular existing curve. No universal practical optimization speedup is claimed.',
  },
];

export const lectureParts = new Map([
  ['title', 'The question'], ['muon', '1. Matrix descent'], ['particles', '2. Particles and measures'],
  ['static', '3. Transport geometry'], ['gradient-flow', '4. Learning'], ['convexity', '5. Convergence'],
  ['root-norm', '6. Extensions'],
]);

export function appendTeachingSlides() {
  const container = document.querySelector('.reveal > .slides');
  for (const slide of teachingSlides) {
    const section = document.createElement('section');
    section.id = slide.id;
    section.className = `teaching-slide${slide.wide ? ' wide-experiment' : ''}${slide.demo ? '' : ' closing-slide'}`;
    section.setAttribute('aria-label', slide.title);
    section.innerHTML = `<header class="slide-heading"><h2>${slide.title}</h2></header>
      <div class="teaching-layout"><div class="talk-track">${slide.body}</div>${slide.demo ? `<div class="demo-panel" data-demo="${slide.demo}">
        <div class="demo-readout" aria-live="off"></div><div class="demo-plot"><canvas aria-label="${slide.title}: numerical illustration" role="img"></canvas></div>
        <div class="demo-controls">${slide.controls.map(control => `<div class="demo-control"><label for="${slide.id}-${control.key}"><span data-math="${escape(control.label)}"></span><output></output></label><input type="range" id="${slide.id}-${control.key}" data-param="${control.key}" min="${control.min}" max="${control.max}" step="${control.step}" value="${control.value}" aria-label="${control.key}" disabled></div>`).join('')}
        ${slide.controls.some(control => control.key === 'time') ? '<div class="demo-actions"><button class="icon-button demo-play" title="Play" aria-label="Play" disabled><i data-lucide="play"></i></button><button class="icon-button demo-reset" title="Reset time" aria-label="Reset time" disabled><i data-lucide="rotate-ccw"></i></button></div>' : ''}</div>
        <p class="demo-status" role="status">Loading experiment...</p></div>` : ''}</div>
      <footer class="source-reference">${slide.source}</footer><aside class="notes">${slide.notes}</aside>`;
    container.append(section);
  }
}
