# Mathematical Audit

Date: 2026-09-27.

## Post-Correction Recheck

Rechecked the implemented repairs and their dependencies in the LMO,
static/dynamic, Gaussian, entropy, Poincare, and spherical arguments.
The following remaining points were corrected directly in the manuscript.
None requires withdrawing the corrected theorems.

### R1. Remainder Depends on the Chosen Coupling

In the proof of `app-prop:gaussian-boundary`, the phrase that expanding along
“any coupling” gives an `O(W_2^2)` remainder was too strong. The correct
bound is

$$
\left|\mathcal F(\nu)-\mathcal F(\mu)
-\int g_\mu(x)\cdot(y-x)\,d\pi\right|
\le C_\mu\int|y-x|^2\,d\pi,
$$

for small displacement of the chosen coupling. Its cost need not be the
optimal Wasserstein cost. For example, with
$\mathcal F(\mu)=\frac12\int|x|^2d\mu$, $\mu=\nu=\mathcal N(0,I_d)$,
and $Y=-X$, the remainder is $2d$ although $W_2(\mu,\nu)=0$.
The main transport--Taylor hypothesis already used the correct bound.
The boundary proof now uses it as well, so its slope and flow conclusions
are unaffected.

### R2. Spherical Action Must Include the Time Horizon

`prop:unbalanced` inherited a general interval `[0,T]` from `prop:sphere`
but compared its action with a distance defined on `[0,1]` without making
the rescaling explicit. It now states
$UW_\gamma(\nu_0,\nu_T)^2\le T\int_0^T\gamma(\int v_tv_t^\top d\mu_t)dt$.
The factor is necessary: in the trace case, the radial path
$\nu_t=(1+t/T)^2\delta_\omega$ has action $1/T$ and squared endpoint
distance $1$. Equality of ambient and projected actions is on the same
time interval. The reaction convention remains $\alpha=2b$, so its cost
is $\alpha^2/4$; this is a rescaled version of the dynamic formulation in
[Chizat et al.](https://arxiv.org/pdf/1508.05216), with the normalization
specified in the manuscript.

### Hypotheses and Proof Details

- Gaussian preservation is now stated on a class of Gaussian states in the
  energy domain. The entropy example excludes singular Gaussians; the
  moment-functional example requires smooth dependence on moments and is
  described in terms of the uncentered cross-moment, not a quadratic
  dependence on centered mean/covariance coordinates.
- The boundary proof explicitly verifies finite velocity action even when
  the affine drift coefficient is not integrable through extinction.
  Energy derivatives are asserted almost everywhere. Interior invariants
  *need not* persist after rank loss; they can remain constant if the mode
  simultaneously becomes stationary.
- Root-norm trace comparison is explicitly proved using square matrices,
  so its constants are independent of the Hilbert target. The entropy
  slope proof cites this comparison in the nonconvex root-norm setting.
- The entropy perturbation calculation now bounds the moving-reference
  velocity norms using $1\pm|\varepsilon|\|u\|_\infty$ and uses the exact
  force pairing. This justifies convergence of the dual norms, not merely
  convergence of the force field at fixed reference measure.
- Qualified the nonlocal Gaussian-entropy discussion: nonlocality is
  generic, not universal; in dimension one every Schatten geometry is W2.

### Checks After Repair

The independent full-matrix LMO check covers positive-definite,
rank-deficient, and zero covariance states, and agrees with the modal ODE
to `5.33e-15`; its action/dissipation error is at most `8.89e-15`.
Affine Gaussian entropy perturbations at `p = 1/2, 3/4, 1, 2, infinity`
give a maximum action error `6.67e-16` and central-difference energy
derivative error `5.75e-10`. The 24-case event/refinement validator was
rerun successfully. These numerical checks support the algebra; the slope,
compactness, and metric statements rely on their analytical proofs.

The entropy slope, root-norm characterization and BB formula, corrected
block gauges, finite-time rank-loss criterion, P-L constants, Gaussian
Poincare comparison, and radial-power strictness argument survived this
recheck. The unproved extensions listed below remain outside the claims.

## Correction Status

The repair plan below has now been implemented in the manuscript. See the
2026-09-27 mathematical-corrections section of `modifications.md` for the
finding-by-finding changes and numerical checks. The original audit is
preserved below; its source hash, line numbers, and statements about what
had not yet been edited refer to the pre-correction snapshot.

All ten findings have been addressed. In particular, the entropy slope has
its own proof, the Gaussian boundary continuation has a conditional metric
verification and event-aware numerical checks, and the spherical statement
is explicitly an action projection rather than a fixed-lift isometry.
The optional square-matrix characterization of root-norm gauges and the
nonconvex commuting counterexample have also been incorporated.

Still not asserted: global PDE existence/uniqueness, a spherical converse
lifting theorem, a uniform local entropy P-L theorem from the pointwise
perturbation expansion alone, or a certified global discretization error.
These are boundaries of the corrected claims, not conclusions supplied by
the numerical tests.

## Original Audit

Scope: the current `neurips/paper.tex`, its notation table, and the Gaussian numerical implementation where it bears on the mathematical claims. This is an audit and repair plan, not a modification of the manuscript. The submitted paper and historical rebuttal are not the mathematical reference version for this report.

Source snapshot: `neurips/paper.tex` SHA-256 `c095cc15421d6de5535fcfe1ce08902f0d301745ff4d48f9699bdf181648c423`. Line references below refer to this snapshot; LaTeX labels are included where useful.

## Assessment

The core construction held up to this pass: I found no counterexample to the finite-dimensional Measure-LMO reduction, the convex-gauge minimax formula, the static--dynamic identity, the root-norm metric extension, the conditional gradient-flow verification theorem, or the two spectral Poincare comparison propositions.

The main problems are at the interfaces between those results and their interpretations. In particular, the spherical reduction needs a specified homogeneous selector; the sum-of-blocks gauge does not model unscaled blockwise polar updates up to a common clock; the infinitesimal norm requires minimization over velocity representatives; and the entropy examples need a slope argument separate from the current gradient-flow theorem. These issues admit fairly compact repairs. They do not require abandoning the spectral transport framework.

The findings distinguish false unqualified statements, gaps in a proof or application, and matters of exposition. A qualification already present in one appendix is not treated as though the paper had claimed a global well-posedness theorem.

| ID | Priority | Finding | Status |
| --- | --- | --- | --- |
| A1 | High | Spherical projection needs a homogeneous selector | Missing hypothesis; unqualified claim has a counterexample |
| A2 | High | Sum gauge versus independently applied polar updates | Modeling mismatch unless the block scaling convention is specified |
| A3 | Medium | Velocity norm versus metric speed; entropy-geodesic proof | Incorrect unrestricted identification and a repairable proof gap |
| A4 | Medium | Entropy is outside the hypotheses of the main flow theorem | Missing bridge, not a refutation of the entropy formulas |
| A5 | Medium | Covariance rank loss in the Gaussian examples | Applicability and numerical-validation gap, partly acknowledged already |
| A6 | Medium | Spherical action identity is not an equality of endpoint distances | Scope clarification; stronger quotient statement is unproved |
| A7 | Medium | Attention forces need more than a second moment | Domain limitation of the illustrative application |
| A8 | Low | Compact-resolvent argument for radial powers below two | Correct conclusion needing a short analytic justification |
| A9 | Low | Spectral Dirichlet energy is generally nonquadratic | Terminology and interpretation of local rates |
| A10 | Low | Differential operator, exponent notation, and clock statements | Local corrections and consistency checks |

## A1. Specify the Homogeneous LMO Selection

Location: [spherical reduction](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:4945), especially `prop:sphere`, versus the definition allowing any Measure-LMO at [Definition of the oracle](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:221).

The derivation of the continuity--reaction equation is correct **if the selected ambient velocity is one-homogeneous**. A two-homogeneous first variation implies that its force is one-homogeneous, but does not imply that every minimizing velocity has that property. The distinction matters at the operator endpoint, where the oracle is not unique.

Here is a counterexample within the paper's smooth finite-particle setting. In dimension two, take

$$
\mathcal F(\mu)=\frac12\int x_1^2\,d\mu,
\qquad
\mu_0=\frac14(\delta_{e_1}+\delta_{-e_1}+\delta_{2e_1}+\delta_{-2e_1}),
\qquad c=\sqrt{5/2}.
$$

The force is $g(x)=(x_1,0)$. For the operator gauge, the field $v(x)=(-x_1,c)$ satisfies

$$
S_g=\operatorname{diag}(5/2,0),\qquad
\int vv^\top d\mu_0=(5/2)I,
$$

and its LMO objective is $-5/2+(5/2)/2=-5/4$, the optimal value. It is therefore a valid Measure-LMO. It is not one-homogeneous even on the support: the values at $e_1$ and $2e_1$ are incompatible with that requirement.

This is not just an isolated choice of a field. The smooth velocity $v_t(x)=(-x_1,ce^{-t})$ transports these atoms to $(e^{-t}x_1(0),c(1-e^{-t}))$ and remains an LMO along the resulting curve. The quadratic energy and this velocity meet the regularity assumptions of the paper's verification theorem.

If one nevertheless defines $b(\omega),\tau(\omega)$ from $v_0(\omega)$ as in the appendix, the claimed spherical equation is wrong. Test it with $\psi(\omega)=\omega_2$. The actual derivative of $\int\psi\,d\Pi_2(\mu_t)=\int |x|x_2\,d\mu_t$ at zero is $3c/2$, whereas the proposed spherical right-hand side gives $5c/2$.

**Repair.** State `prop:sphere` for a continuity equation with a one-homogeneous selected velocity, not for every spectral gradient flow. Explain that the projected selection of `prop:measure-lmo-reduction`, and in particular the canonical Schatten selection, has this property when the force is one-homogeneous. For a closed equation depending only on the spherical measure, fix the matrix selector as a function of the force second moment, rather than allowing an arbitrary selection depending on the particular radial lift. State the differentiability assumptions needed for the first variation; two-homogeneity alone does not provide them. The quadratic-growth test function can then be justified by cutoffs under the second-moment and finite-action bounds.

This preserves the intended result without asserting it for additional nonhomogeneous minimizers.

## A2. Distinguish Two Blockwise Normalizations

Location: [block-wise normalization](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:2159), and the summary that blockwise normalization is exactly covered at [the Muon remark](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:340).

The proposed sum gauge is a valid monotone gauge and really does split the oracle. The issue is which update it produces. For operator gauges on the blocks, set $c_b=\|G_b\|_*$ and let $P_b$ be the compact polar factor of $G_b$. Then

$$
\gamma_{\rm sum}(S)=\sum_b\lambda_{\max}(S_{bb})
\quad\Longrightarrow\quad
J_b(G)=-c_bP_b.
$$

Independently applying the unscaled polar normalization instead gives $-P_b$. These are not generally the same joint trajectory under a time change, since there is a different multiplier in each block. The single-block time-reparametrization observation cannot be applied separately to coupled blocks.

For example, two scalar block gradients $(2,1)$ give velocity $(-2,-1)$ under the sum gauge and $(-1,-1)$ under independent polar updates. No scalar change of clock identifies these directions.

**Repair option 1.** Retain the sum gauge, but explicitly say that it models independent *squared-norm LMOs*, including their individual nuclear-norm multipliers. Do not identify it with independently applied raw polar factors.

**Repair option 2, recommended if the practical polar comparison is intended.** Add the equally admissible maximum gauge

$$
\gamma_{\rm max}(S)=\max_b\lambda_{\max}(S_{bb}).
$$

Its tangent norm and dual are

$$
N(V)=\max_b\|V_b\|_{\rm op},\qquad
N^*(G)=\sum_b\|G_b\|_*.
$$

A canonical oracle is consequently

$$
J_b(G)=-\left(\sum_a\|G_a\|_*\right)P_b,
$$

with zero chosen in zero-gradient blocks. All blocks now share one scalar multiplier, so their deterministic trajectories agree with independent raw polar updates away from the stationary state, up to a common clock. Fixed positive block learning-rate factors $\eta_b$ can be represented by $\max_b\lambda_{\max}(S_{bb})/\eta_b^2$.

Both the sum and maximum gauges are convex, positive and Loewner-monotone on the PSD cone. Thus the static/dynamic theory survives for both, but they describe different optimizers. This is an opportunity for a useful extension rather than an obstruction to the framework.

## A3. Separate Velocity Norms from Metric Speeds

Locations: [infinitesimal interpretation](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:329) and the opening of the proof of `thm:entropyfull` at [minimal velocity representation](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:3912).

The norm $N_\mu(v)$ is a norm on velocity representatives, not automatically the metric norm of the measure derivative generated by $v$. The continuity equation only sees $-\operatorname{div}(\mu v)$.

For example, let $\mu=\mathcal N(0,I_2)$ and $v(x)=(-x_2,x_1)$. Then $\operatorname{div}(\mu v)=0$, so the measure curve is stationary and its metric speed is zero. Nevertheless $N_\mu(v)^2=\gamma(I_2)>0$. This already occurs in ordinary Wasserstein geometry.

The appropriate tangent quantity is the quotient/minimal-representative norm

$$
\|\dot\mu\|_{\gamma,\mu}
=\inf_{-\operatorname{div}(\mu v)=\dot\mu}N_\mu(v),
$$

with its identification with metric speed formulated almost everywhere along suitable absolutely continuous curves. The classical version is explicitly a minimal-velocity result, not equality for all representatives; see Section 2.6 and Theorem 2.15 of [Ambrosio--Savare's lecture notes](https://web.math.ucsb.edu/~kcraig/math/AmbrosioSavareLectureNotes.pdf).

The current proof of `prop:formalGF` avoids this problem correctly: it first proves a speed upper bound and then uses dissipation to obtain equality for the selected descent velocity. However, `thm:entropyfull` starts by taking a minimal representation of an *arbitrary* spectral geodesic and declaring that its action equals the squared endpoint distance. This stronger representation result has not been proved in the paper. The endpoint BB identity alone is not a proof of this assertion for a preassigned curve.

**Compact repair of the entropy proof.** No new velocity theorem is needed there. Let $D=W_\gamma(\mu_0,\mu_1)$ and choose a dual maximizer $Q_*$ for the endpoints. Under that theorem's assumption, $Q_*\succ0$ and $W^{Q_*}(\mu_0,\mu_1)=D$. Along any constant-speed $W_\gamma$ geodesic,

$$
\begin{aligned}
D
&\le W^{Q_*}(\mu_0,\mu_s)
   +W^{Q_*}(\mu_s,\mu_t)
   +W^{Q_*}(\mu_t,\mu_1)\\
&\le sD+(t-s)D+(1-t)D=D.
\end{aligned}
$$

Equality throughout shows that the given curve is also a constant-speed $W^{Q_*}$ geodesic. Apply the invertible coordinate change $Q_*^{1/2}$ and classical entropy convexity. This establishes the all-geodesics conclusion directly, without an unproved spectral minimal-velocity representation.

**Other repair.** Qualify the introductory tangent-norm wording. A general minimal-representative theorem can be added later if needed elsewhere, but is not necessary for this compact proof or for the existing conditional flow theorem.

## A4. Supply an Entropy Slope Lemma

Locations: [hypotheses of the main flow theorem](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:737), [Gaussian KL reduction](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:4187), and [local entropy/Poincare discussion](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:4510).

The main theorem assumes that the energy is finite on a neighborhood of the curve and admits a two-sided quadratic transport remainder against all nearby couplings. Relative entropy with respect to a positive-density reference measure does not satisfy those assumptions. Atomic probabilities are dense in $\mathcal P_2$, and their relative entropy is infinite. Thus entropy is not finite on any nonempty Wasserstein-open neighborhood.

The paper already makes the Poincare slope interpretation conditional, which is appropriate. The remaining gap is that the Gaussian normalized continuity equation and the spectral Dirichlet energy have not themselves been connected to the *ambient metric slope* by the main theorem. Existence of an affine Gaussian ansatz is a different statement.

**Repair.** Add a short, separate lemma tailored to entropy. One useful sufficient setting is $\alpha,\beta\in\mathcal P_2$ with strictly positive $C^1$ densities, finite $\mathrm{KL}(\alpha\mid\beta)$, and

$$
q=\log(d\alpha/d\beta)\in C^2,
\qquad \|D^2q\|_{\rm op}\le M,
\qquad \nabla q\in L^2(\alpha).
$$

Justify the change-of-variables derivative under compactly supported smooth transports using this local density regularity. Convexity of entropy with respect to linear mixing gives, for any $\nu\in\mathcal P_2$,

$$
\mathrm{KL}(\nu\mid\beta)-\mathrm{KL}(\alpha\mid\beta)
\ge \int q\,d(\nu-\alpha).
$$

Consequently, for any coupling $\pi$ of $\alpha,\nu$,

$$
\mathrm{KL}(\nu\mid\beta)-\mathrm{KL}(\alpha\mid\beta)
\ge \int \nabla q(x)\cdot(y-x)\,d\pi
 -\frac M2\int |y-x|^2\,d\pi.
$$

This one-sided inequality suffices for the slope upper bound by the barycentric argument already used in the paper. The reverse bound follows from the entropy derivative under $(\mathrm{Id}+hw)_\sharp\alpha$, first for compactly supported smooth $w$, then by density in $L^2(\alpha)$. It yields

$$
|\partial\mathrm{KL}(\cdot\mid\beta)|_\gamma(\alpha)
=N_\alpha^*(\nabla q).
$$

The argument uses monotonicity and the root-norm property, not a convex covariance gauge. It therefore also covers the root-norm range when these regularity assumptions hold.

For two nondegenerate Gaussians, $q$ is quadratic, so this lemma applies directly. For the local perturbations, take a smooth compactly supported function minus its $\beta$-mean; then $q=\log(1+\varepsilon u)$ has bounded Hessian for sufficiently small $\varepsilon$. A chain-rule argument along the Gaussian ODE supplies the energy identity separately. This closes the relevant gap without claiming global well-posedness or imposing the impossible finite-neighborhood condition on entropy.

## A5. Account for Finite-Time Covariance Rank Loss

Locations: positive definiteness in [the covariance proposition](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:3241), [modal equations](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:3321), [figure parameters](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:3434), and [the implementation](/Users/gpeyre/Dropbox/github/muon-dynamics/python/gaussians/generate_gaussians_notebook.py:284).

The displayed covariance and modal formulas are algebraically consistent. However, positive-definite initialization does not keep the covariance positive definite for $p>1$, even in this simple balanced model. This issue is concrete for the plotted parameters, not only a hypothetical endpoint concern.

For $p>1$, let $q=(2p)'$ and $\eta=1-q/2=(p-1)/(2p-1)>0$. On each interior modal interval,

$$
\frac{d}{dt}(a_i^\eta+b_i^\eta)=0.
$$

This follows immediately from the modal ODE, and the common normalization cancels even when there are several modes. Starting from $a_i=b_i=\alpha_i$, an interior trajectory satisfies

$$
|r_i|<\alpha_i\,2^{1/\eta-1}
=\alpha_i\,2^{p/(p-1)},
$$

where the operator limit is $|r_i|<2\alpha_i$. If the target lies beyond this threshold, the shrinking covariance eigenvalue reaches zero before that target. In fact the hitting time is finite: the error remains bounded away from zero before hitting, and the shrinking eigenvalue obeys $\dot b_i=-c(t)b_i^{q/2}$ with a positive lower bound on $c(t)$ and exponent $q/2<1$ (or the analogous equation for $a_i$).

For the plotted first-mode initialization $\alpha_1=0.1$, the thresholds are $0.4$ for $p=2$, approximately $0.251984$ for $p=4$, and $0.2$ for $p=\infty$. Every plotted first-mode target has magnitude at least $0.35$. Thus all the $p=4$ and operator runs must leave the positive-definite regime to approach those targets; so must three of the four $p=2$ runs.

The numerical appendix already discloses projection of negative eigenvalues and does not claim certified accuracy through rank changes. That qualification is good, but the connection with the positive-definite proposition should be explicit beside the Gaussian figure. Agreement of the implemented RHS with the displayed RHS is not, by itself, an independent justification of the boundary continuation.

**Repair.** State the interior lifetime in the covariance proposition. Either derive the selected Gaussian weak continuation on the PSD boundary directly from the Measure-LMO, with zero on inactive modes, or label the continuation as the particular numerical extension used. Explain that interior invariants cease to constrain the trajectory after a mode vanishes. Add event detection and step-size refinement around rank-loss and zero-error events, rather than relying only on nonnegativity clipping. Do not infer global positive definiteness from balanced initialization for $p>1$.

For $p=1$, the positive product $a_ib_i$ is conserved, so this particular finite-time extinction mechanism is absent. This is a real qualitative difference between the geometries.

## A6. Limit the Spherical Quotient Claim to What Is Proved

Locations: [opening of Appendix J](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:4896) and [ambient/spherical action identity](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:4994), `prop:quotient` and `prop:unbalanced`.

Two statements are proved: the energy factors through $\Pi_2$, and the action of a given homogeneous ambient lift equals its projected spherical action. These do not prove equality between the ambient endpoint distance and the spherical distance, or an equality of their infima over arbitrary lifted paths.

For a direct warning against the first interpretation, take

$$
\mu_0=\delta_{e_1},\qquad
\mu_1=\tfrac12\delta_0+\tfrac12\delta_{\sqrt2 e_1}.
$$

Both project to $\delta_{e_1}$ under $\Pi_2$. Nevertheless, for all the paper's normalized Schatten gauges,

$$
W_\gamma(\mu_0,\mu_1)^2=2-\sqrt2>0,
\qquad
UW_\gamma(\Pi_2\mu_0,\Pi_2\mu_1)=0.
$$

Thus the sentence that the models reduce the ambient transport problem to a spherical problem must be understood at the level of the energy and homogeneous action, not as an isometry of fixed lifts.

**Repair.** Say exactly that. If a stronger metric quotient is intended, formulate it with an infimum over ambient lifts and prove both directions, including lifting of spherical continuity--reaction curves and behavior at the origin. This is an additional theorem, not a consequence of the displayed covariance identity.

The definition of $UW_\gamma$ should also explicitly specify endpoint conditions, narrow continuity of finite spherical measures, tangency and measurability of $\tau$, and the finite-action requirement. The metric property itself can be justified compactly without a static formula: trace comparison bounds its action above and below by the stated WFR action; separation follows from WFR, and concatenation with time rescaling gives the triangle inequality.

## A7. State the Force Domain for Attention

Location: [mean-field shallow attention](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:884), compared with $g\in L^2(\mu)$ in the Measure-LMO definition.

Second moments can suffice to define the attention predictor while being insufficient to define its spectral oracle. For bounded inputs, the head output grows at most quadratically in $(O,V)$, but differentiation with respect to $Q$ or $K$ can introduce a third parameter factor.

An explicit example uses scalar head parameters and two tokens $z_1=1,z_2=-1$. Put $Q=0$, $K=V=O=t$, and let the teacher output at token $j$ be $z_j$. The head output is zero, since the two attention weights are equal. However,

$$
\partial_Q\phi(z,x)_j=t^3z_j,
$$

so for the risk $\frac14\sum_{j=1}^2(H_j-z_j)^2$ the force component is $g_Q(x)=-t^3$ at this law. Choose a law of $t$ with finite second moment and infinite sixth moment, for example density $3t^{-4}$ on $[1,\infty)$. The parameter measure belongs to $\mathcal P_2$ and the risk is finite, but $g\notin L^2(\mu)$.

The main verification theorem already requires a square-integrable force, so this is not a counterexample to that theorem. It is a limitation on interpreting the attention paragraph as defining a flow for arbitrary second-moment laws.

**Repair.** Mark the attention PDE as conditional on force integrability. For bounded or finite data, a finite sixth parameter moment is a simple sufficient growth condition for this part; bounded parameter support is another. Neither condition by itself guarantees preservation of the moment bound, selector regularity, or global existence. Keep those questions separate. Likewise, a first-variation formula should be stated for admissible signed perturbations, not arbitrary zero-mass perturbations that leave the probability cone.

## A8. Justify the Singular Radial Schrodinger Potential

Location: [generalized Gaussian proposition](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:4817), `prop:power-poincare-schatten`.

The strict comparison argument is convincing and the rank-one rigidity argument is correct. The compact-resolvent sentence is compressed when $1<r<2$: the transformed potential

$$
U_r(x)=\frac{r^2}{4}|x|^{2r-2}
-\frac{r(r+d-2)}2|x|^{r-2}
$$

has a negative singularity at zero. The fact that it tends to positive infinity at spatial infinity should be accompanied by a local form-domain justification, not silently treated as the bounded-below continuous-potential case.

**Repair.** Work with the self-adjoint operator associated with the closed weighted Sobolev form. For $1<r<2$, the local negative singularity is a multiple of $|x|^{-(2-r)}$; it belongs to $L^a(B_1)$ for some $a>d/2$ and $a>1$. Sobolev estimates imply infinitesimal form boundedness. The positive confining part controls tails, and local Rellich compactness gives compact embedding of the form domain. The ground-state transform is interpreted at the quadratic-form level; no pointwise $C^2$ regularity of $|x|^r$ at zero is required. Classical confinement criteria are discussed in [Simon's paper on purely discrete spectrum](https://web.ma.utexas.edu/mp_arc/c/08/08-191.pdf); the local singularity still requires the preceding step.

For the ridge contradiction, invoke elliptic regularity away from zero and vary the transverse variable with a fixed nonzero axial coordinate. This avoids any regularity assertion at the singular point.

The existing minimizing-sequence argument must be kept: pointwise strictness of the Schatten inequality alone would not establish a strict gap between the infima. No reversal of the stated strict inequalities is needed.

## A9. Clarify the Nonlinear Poincare Interpretation

Locations: [Hessian/local-gap discussion](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:4523), [definition of the spectral energy](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:4556), and the local-rate conclusion at [the comparison](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:4692).

Except for quadratic tangent geometries, $\mathcal E_\gamma^\beta$ is not a quadratic Dirichlet form. It is a convex, two-homogeneous Dirichlet energy. For example, for standard Gaussian $\beta$ in dimension two and $p=\infty$, put $u=x_1^2-1$ and $w=x_2^2-1$. Then

$$
\mathcal E(u)=\mathcal E(w)=4,\qquad
\mathcal E(u+w)=\mathcal E(u-w)=16.
$$

The parallelogram identity fails. Accordingly, the small-amplitude evolution generally remains nonlinear even at leading order; it is not a linear self-adjoint generator with an ordinary eigenvalue gap. Formally, for a canonical homogeneous selector, it has the form

$$
\partial_tu=-\beta^{-1}\operatorname{div}
\bigl(\beta J_\gamma^\beta(\nabla u)\bigr).
$$

Here $\beta$ in the differential expression denotes its density. Along a sufficiently regular solution, $\frac12\frac{d}{dt}\int u^2d\beta=-\mathcal E_\gamma^\beta(u)$, so the variational Poincare constant still has the intended dissipation meaning.

**Repair.** Prefer "spectral Dirichlet energy" and "variational local dissipation gap." Say that linearization is a small-amplitude expansion, not necessarily a linear PDE. The current word "formally" and the slope-identification caveat are important and should remain. A pointwise perturbation expansion alone is not a uniform local P-L theorem in an unspecified neighborhood of the minimizer; state a topology and uniform bounds before claiming that stronger result.

The Gaussian equality for $p\ge1$ and strict decrease for $1/2\le p<1$ are correct. The radial-power strict increase for $p>1$ and strict decrease for $p<1$ are also consistent with the adopted normalization. A larger constant means a stronger certified dissipation rate, not an ordering of energy values along different trajectories.

## A10. Correct Local Mathematical Presentation

1. [Stochastic closure equation](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:2138): the source has `+divv` rather than `+\divv`. This compiles as a product of letters instead of the divergence operator. Correct the command and inspect the displayed equation.
2. [Explicit Schatten selector](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:1265): $r=2p$ is introduced immediately before $U_r,W_r$ are used for a compact SVD. The same subscript then looks like a rank, although $2p$ need not be an integer. Use $U,W$ or a separate rank symbol. Explicitly set $q=1$ at $p=\infty$ where rational expressions involving $p$ are used.
3. [Attention clock sentence](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:887): it still suggests calibration by comparable small-time energy decay, whereas [the numerical protocol](/Users/gpeyre/Dropbox/github/muon-dynamics/neurips/paper.tex:3462) describes separately normalized nominal clocks with safeguards and no recovered intrinsic times. Report an actual attention-specific initial-decay check or use the more cautious protocol wording. The current text does not substantiate a theoretical-time comparison.
4. At the first definitions, call $\int gg^\top d\mu$ and $\int(y-x)(y-x)^\top d\pi$ **uncentered second-moment matrices**, or explicitly declare the paper's use of "covariance" for these quantities. The formulas correctly retain the mean terms; subtracting the means would change the theory.
5. In the definition of a curve of maximal slope, state local absolute continuity of the energy or give the integrated dissipation identity, consistently with the hypotheses already imposed in the P-L convergence proposition. An a.e. derivative formula should not be presented as a substitute for all time-regularity requirements.

## Results Checked Without Finding a New Error

- **Measure-LMO reduction.** The operator projection preserves the force pairing and decreases the velocity second moment in Loewner order. The transpose and pseudoinverse in the lifted selector have the correct orientation. The result constructs a minimizer; it does not characterize every minimizer.
- **Schatten selectors.** The exponent $q=(2p)'$, the prefactor, the compact-polar convention, and the covariance-equalization identity are consistent. The canonical operator selector is Borel but discontinuous at rank changes; the paper now says so.
- **Inverse-trace certificate.** The inverse belongs to the positive-definite dual cost matrix, not the force covariance. The infimum sign is correct. At the operator endpoint, full-rank $S_g$ gives the full-rank minimizer $\sqrt{S_g}/\operatorname{tr}\sqrt{S_g}$; a blanket rank-one assertion would be wrong.
- **Static theory.** Fixed marginals supply compactness, quadratic moments and the needed continuity/integrability. The minimax argument, Gaussian covariance-block reduction, conditional Brenier theorem and large-mean asymptotics are consistent. The final estimate controlling the $R^2$-weighted certificate error in the large-mean proof is necessary and is present.
- **Dynamic theory.** Conditional barycentric projection and superposition give the two BB inequalities. The perspective convention at singular quadratic costs is correct. The root-norm proof uses operator Minkowski, rather than an unavailable convex support representation.
- **Root-norm threshold.** For $d\ge2$, $p\ge1/2$ is the correct metric threshold; the dimension-one exception is now explicit. This is not a claim that all convex-gauge results extend to that range.
- **Main flow verification.** Under its actual strong hypotheses, the two slope inequalities, characteristic chain rule, energy regularity and speed equality form a coherent argument. The theorem is a verification result, not a global existence theorem.
- **Newton--Schulz.** The fixed-scale stable-region construction is correctly a convex completed *dual dissipation*, whose conjugate is the primal dissipation. It is not a fixed squared-metric gradient flow. Do not reintroduce the older claim that covariance monotonicity alone makes it a $W_\gamma$ flow: the lack of force homogeneity remains even on a nontrivial stable interval.
- **P-L constants.** The energy exponent $2\kappa$, distance exponent $\kappa$, length factor $\sqrt{2/\kappa}$, transfer factor $1/C_\gamma$, and gauge-rescaling factor $1/a$ are correct.
- **Robust Poincare.** Both optimizations are infima. The transformed target is $(Q^{1/2})_\sharp\beta$, not its inverse transform. The Gaussian test perturbation and its strict $p<1$ comparison are correct. The radial-power argument needs the compactness detail in A8, not a change of conclusion.

## Guardrails for Further Extensions

### The commuting Gaussian formula does not extend automatically below p = 1

The commuting formula in Appendix D is currently stated for Schatten norms under the standing convex-gauge convention, so I do not classify it as an error. Nevertheless, its pinching proof fails for $p<1$, and its conclusion can fail even though those gauges are root-norm gauges.

Take $\Sigma_0=\operatorname{diag}(4,1)$ and $\Sigma_1=\operatorname{diag}(1,4)$. At $p=1/2$, the displayed commuting expression would be $\gamma_{1/2}(I)=4$. In the basis $(e_1+e_2)/\sqrt2,(e_1-e_2)/\sqrt2$, define the Gaussian transport by

$$
Y_1=X_1,\qquad Y_2=X_2-\frac65X_1.
$$

It has the required target covariance and displacement covariance $\operatorname{diag}(0,18/5)$ in this basis, with cost $18/5<4$. Thus the commuting closed form must remain restricted to $p\ge1$. This is a useful regression counterexample for any future claim that "the results extend to root-norm gauges."

### A more concrete root-norm characterization is available

The current compatible-family characterization is correct, but close to the definition. A shorter usable test is that $V\mapsto\sqrt{\gamma(V^\top V)}$ need only be a norm on square $d\times d$ matrices. Its automatic left-orthogonal invariance implies contraction under left multiplication by contractions and therefore Loewner monotonicity of $\gamma$. For operators into an arbitrary Hilbert space, compress $T_1+T_2$ isometrically onto a target of dimension at most $d$, apply the square-matrix triangle inequality, and use contraction for the two compressed summands. This proves the full Hilbert-target norm property.

This is an optional improvement, not a required correction. It would make the characterization substantially less circular to readers.

## Plan of Action

1. **Repair the selector and optimizer statements first.** Add the homogeneous-selector hypothesis in Appendix J. Distinguish sum-gauge squared-norm updates from maximum-gauge raw blockwise polar updates, including the common-clock formula. Check the main-text summary against these precise statements.
2. **Close the metric interpretation gaps.** Qualify the tangent-norm wording and replace the opening of the full entropy-convexity proof by the direct fixed-$Q_*$ argument in A3. Add the one-sided entropy slope lemma in A4, then state exactly which Gaussian and perturbative entropy conclusions it proves.
3. **Put the Gaussian examples on their actual domain.** State the lifetime of the positive-definite reduction, record the general interior invariant, and either prove the selected PSD continuation or explicitly limit the theoretical claim. Add rank-event and time-step checks for the plotted runs.
4. **Tighten the remaining application assumptions.** Specify the force domain for attention, the admissible spherical paths, and the distinction between an action projection and a metric quotient. Do not replace these points by an unsupported general well-posedness assertion.
5. **Harden the Poincare presentation.** Add the local form-bound/compactness detail for $1<r<2$, use nonlinear Dirichlet-energy terminology, and retain the distinction between a local variational constant and a global entropy P-L theorem.
6. **Finish with a consistency and rendering pass.** Correct `\divv`, separate SVD rank and exponent notation, reconcile attention clock wording, and explicitly restrict the commuting closed form to $p\ge1$. Rebuild the paper and inspect the affected equations. Update `modifications.md` only when those manuscript changes are actually implemented.

Suggested acceptance checks: the homogeneous-selector counterexample is excluded by the new hypothesis; the two-block example is reproduced by the stated gauge; no arbitrary velocity is equated with metric speed; the entropy examples cite hypotheses they satisfy; rank loss is handled explicitly rather than hidden by projection; and the $p=1/2$ commuting counterexample is not contradicted by an extension claim.

## Verification Performed

I read the statement/proof blocks throughout the current manuscript and checked their mathematical dependencies. I independently recomputed the block scalings, homogeneous-selector counterexample, Gaussian modal extinction thresholds, nonquadratic energy example, and the nonconvex commuting counterexample. Small numerical checks agree with those exact calculations.

I also ran the existing Gaussian validator without its full-horizon option. The maximum tested RHS discrepancy was approximately $3.55\times10^{-15}$, the algebraic invariant derivative error approximately $8.88\times10^{-16}$, and the short-horizon trajectory tests passed. These are algebra/implementation checks, not a proof of global convergence or of accuracy through a rank change. No full training run or new full-horizon refinement experiment was performed for this audit.

No manuscript, figure, bibliography, or rebuttal file was edited in this pass. This report is not a formal proof certificate; in particular, proposed extensions and boundary continuations still need their stated hypotheses and proofs before being promoted to manuscript theorems.
