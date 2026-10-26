import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import { teachingSlides } from '../src/content.js';
import { FLOW_BOUNDS, FIELD_BOUNDS, powerNorm, diagonalLMO, eigen2, clockState, memoryResponse, gaussianQuotient,
  nsResponse, noiseResponse, bentAction, rectangleKL } from '../src/lecture-math.js';
import { splittingCoupling, splittingCost, gaussianCovariance, radialTest, momentGauge } from '../src/lecture-math.js';

const data = JSON.parse(await readFile(new URL('../public/data/lecture.json', import.meta.url)));
const networks = JSON.parse(await readFile(new URL('../public/data/networks.json', import.meta.url)));
const extensions = JSON.parse(await readFile(new URL('../public/data/extensions.json', import.meta.url)));
const close = (a, b, tolerance = 1e-8) => assert.ok(Math.abs(a - b) < tolerance, `${a} != ${b}`);

test('the 31-slide narrative has unique links, sources and speaker notes', () => {
  assert.equal(teachingSlides.length, 29);
  assert.equal(new Set(teachingSlides.map(slide => slide.id)).size, 29);
  assert.equal(teachingSlides.filter(slide => slide.demo).length, 28);
  for (const slide of teachingSlides) {
    assert.ok(slide.source.length > 10);
    assert.ok(slide.notes.length > 100);
  }
});

test('diagonal Schatten selectors satisfy both LMO dissipation identities', () => {
  for (const p of [.5, .75, 1, 1.5, 2, 4, Infinity]) {
    for (const g of [[1, .2], [-.3, .5], [1, 0], [0, 0], [1, -1]]) {
      const v = diagonalLMO(g, p), q = p === .5 ? Infinity : p === Infinity ? 1 : 2 * p / (2 * p - 1);
      const dissipation = powerNorm(g, q) ** 2;
      close(-g.reduce((s, x, i) => s + x * v[i], 0), dissipation);
      close(powerNorm(v, 2 * p) ** 2, dissipation);
    }
  }
});

test('the exact clock change traces the same canonical diagonal path', () => {
  for (const t of [0, .1, Math.log(3) / 2, 1, 2, 5]) {
    const state = clockState(t), raw = clockState(state.rawTime).raw;
    raw.forEach((x, i) => close(x, state.metric[i]));
  }
});

test('EMA has zero lag at zero momentum and decreasing lag with the time step', () => {
  memoryResponse(0, .1).forEach(point => close(point.force, point.filtered));
  const lag = step => { const last = memoryResponse(.8, step).at(-1); return last.force - last.filtered; };
  assert.ok(lag(.02) < lag(.2));
});

test('MMD simulations share initial states and descend for every n and p', () => {
  assert.equal(data.flow.experiments.length, 20);
  for (const e of data.flow.experiments) {
    const baseline = data.flow.experiments.find(f => f.count === e.count && f.p === '1');
    assert.deepEqual(e.frames[0], baseline.frames[0]);
    assert.equal(e.frames.length, 101);
    assert.ok(e.frames.every(frame => frame.length === 2 * e.count && frame.every(Number.isFinite)));
    assert.ok(e.energies.every(x => x >= -1e-8));
    for (let i = 1; i < e.energies.length; i += 1) assert.ok(e.energies[i] <= e.energies[i - 1] + 1e-7);
  }
});

test('the shared viewports contain every spectral trajectory and initial velocity arrow', () => {
  const contains = (bounds, x) => x[0] > bounds[0] && x[0] < bounds[1] && x[1] > bounds[2] && x[1] < bounds[3];
  for (const e of data.flow.experiments) for (const frame of e.frames) {
    for (let i = 0; i < e.count; i += 1) assert.ok(contains(FLOW_BOUNDS, frame.slice(2 * i, 2 * i + 2)));
  }
  for (const field of data.flow.fields) field.x.forEach((x, i) => {
    assert.ok(contains(FIELD_BOUNDS, x));
    assert.ok(contains(FIELD_BOUNDS, x.map((v, j) => v + .48 * field.v[i][j])));
  });
});

test('static couplings have correct marginals and agree with independent convex duals', () => {
  for (const e of data.transport.experiments) {
    close(e.cost, e.dualCost, 2e-6);
    assert.ok(e.marginalError < 1e-7);
    assert.ok(eigen2(e.moment).values.every(x => x >= 0));
    for (let i = 0; i < e.n; i += 1) {
      close(e.plan[i].reduce((a, b) => a + b, 0), 1 / e.n, 1e-7);
      close(e.plan.reduce((sum, row) => sum + row[i], 0), 1 / e.n, 1e-7);
    }
  }
  const max = data.transport.experiments.find(e => e.n === 16 && e.p === 'inf' && e.angle === 30).cost;
  assert.ok(data.transport.robust.every(e => e.cost <= max + 1e-6 && new Set(e.assignment).size === 16));
});

test('bending increases action and trace action matches its analytic integral', () => {
  for (const e of data.transport.experiments.filter(e => e.n === 8 && e.angle === 30)) {
    const p = e.p === 'inf' ? Infinity : Number(e.p);
    close(bentAction(e, p, 0), e.cost, 2e-6);
    assert.ok(bentAction(e, p, .4) >= e.cost - 2e-6);
    if (p === 1) close(bentAction(e, p, .4), e.cost + .4 ** 2 * Math.PI ** 2 / 2, 1e-7);
  }
});

test('Gaussian training preserves positive definiteness and loss decreases', () => {
  for (const e of data.gaussian.experiments) {
    e.covariance.forEach(s => assert.ok(eigen2(s).values[1] > 1e-5));
    e.losses.forEach((loss, i) => {
      if (i) assert.ok(loss <= e.losses[i - 1] + 1e-8);
      close(loss, .5 * (e.covariance[i][0][1] - 1) ** 2, 2e-8);
    });
  }
});

test('ReLU runs descend, share initial neurons and stay inside the displayed projection', () => {
  assert.equal(networks.relu.experiments.length, 9);
  for (const e of networks.relu.experiments) {
    const baseline = networks.relu.experiments.find(f => f.n === e.n && f.p === '1');
    assert.deepEqual(e.frames[0], baseline.frames[0]);
    assert.equal(e.frames.length, 101);
    for (const frame of e.frames) {
      assert.equal(frame.length, e.n);
      for (const neuron of frame) {
        assert.ok(neuron.every(Number.isFinite));
        assert.ok(neuron.slice(1).every(x => Math.abs(x) < 4));
      }
    }
    e.predictions.forEach((prediction, i) => {
      assert.equal(prediction.length, networks.relu.grid.length);
      const loss = prediction.reduce((sum, y, j) => sum + (y - networks.relu.target[j]) ** 2, 0) / (2 * prediction.length);
      close(loss, e.losses[i], 2e-8);
      if (i) assert.ok(e.losses[i] <= e.losses[i - 1] + 1e-8);
    });
  }
});

test('attention examples are stochastic matrices with the expected zero-scale limit', () => {
  assert.equal(networks.attention.experiments.length, 93);
  for (const e of networks.attention.experiments) {
    assert.ok(e.effectiveTokens >= 1 && e.effectiveTokens <= 8);
    for (const row of e.weights) {
      close(row.reduce((sum, w) => sum + w, 0), 1, 1e-7);
      assert.ok(row.every(w => w >= 0 && w <= 1));
      if (e.scale === 0) row.forEach(w => close(w, 1 / 8));
    }
  }
});

test('halving the ReLU integration step preserves the displayed predictions and losses', () => {
  assert.equal(networks.relu.integrator, 'Heun');
  const checked = networks.relu.experiments.filter(e => e.refinement);
  assert.deepEqual(checked.map(e => e.p), ['1', 'inf']);
  for (const e of checked) {
    assert.equal(e.refinement.dt, networks.relu.dt / 2);
    assert.ok(e.refinement.maximumPredictionRMS < 4e-5);
    assert.ok(e.refinement.relativeFinalEnergyError < 1e-5);
  }
});

test('the Gaussian Poincare test respects the direction of the rate comparisons', () => {
  for (const p of [.5, .75, 1, 2, Infinity]) close(gaussianQuotient(0, p), 1);
  assert.ok(gaussianQuotient(.1, .75) < 1);
  assert.ok(gaussianQuotient(.5, Infinity) > gaussianQuotient(.5, 1));
});

test('classical NS responses are increasing on the verified stable interval', () => {
  for (let k = 0; k <= 6; k += 1) {
    let previous = 0;
    for (let i = 0; i <= 100; i += 1) {
      const value = nsResponse(i / 100, k);
      assert.ok(value >= previous - 1e-12 && value <= 1 + 1e-12);
      previous = value;
    }
  }
  assert.notEqual(nsResponse(.5, 1), 2 * nsResponse(.25, 1));
});

test('the exact noise example is unbiased only before nonlinear normalization', () => {
  const linear = noiseResponse(.6, 1);
  linear.average.forEach((x, i) => close(x, linear.deterministic[i]));
  const muon = noiseResponse(.6, Infinity);
  close(muon.average[1], .2);
  assert.ok(muon.deterministic[1] < 0);
});

test('reflection has infinite midpoint KL while translation remains finite', () => {
  assert.equal(rectangleKL(.5, 1.8, .8, true), Infinity);
  assert.ok(Number.isFinite(rectangleKL(.5, 1.8, .8, false)));
});

test('MMD tighter integrations reproduce both endpoint exponents', () => {
  const checked = data.flow.experiments.filter(e => e.refinement);
  assert.deepEqual(checked.map(e => e.p), ['1', 'inf']);
  for (const e of checked) {
    assert.ok(e.refinement.maximumRMS < 2e-5);
    assert.ok(e.refinement.relativeFinalEnergyError < 1e-5);
  }
});

test('mass splitting has the exact optimal cost and improves every deterministic map', () => {
  for (const p of [1, 1.5, 2, 4, Infinity]) {
    const optimum = 2 ** (p === Infinity ? 0 : 1 / p);
    close(splittingCost(.5, p), optimum);
    close(splittingCost(0, p), 2);
    close(splittingCost(1, p), 2);
    for (let k = 0; k <= 100; k += 1) {
      const c = splittingCoupling(k / 100);
      c.plan.forEach(row => close(row.reduce((s, x) => s + x, 0), .5));
      close(momentGauge(c.moment, p), splittingCost(k / 100, p));
      assert.ok(splittingCost(k / 100, p) >= optimum - 1e-10);
    }
    if (p > 1) assert.ok(optimum < 2);
  }
});

test('quadratic covariance flows agree with the exact endpoints and handle extinction', () => {
  for (const e of extensions.quadratic.experiments) {
    e.factors.forEach((c, i) => {
      const t = extensions.quadratic.times[i];
      assert.ok(c.every(x => x >= 0 && x <= 1));
      close(e.energies[i], .5 * (c[0] ** 2 + e.condition * c[1] ** 2), 2e-9);
      if (i) assert.ok(e.energies[i] <= e.energies[i - 1] + 1e-9);
      if (e.p === '1') { close(c[0], Math.exp(-t)); close(c[1], Math.exp(-e.condition * t)); }
      if (e.p === 'inf') c.forEach(x => close(x, Math.exp(-(1 + e.condition) * t)));
    });
  }
  for (const { n, x } of extensions.quadratic.samples) {
    for (let i = 0; i < 2; i += 1) for (let j = 0; j < 2; j += 1) {
      close(x.reduce((sum, row) => sum + row[i] * row[j] / n, 0), i === j ? 1 : 0);
    }
    assert.ok(x.flat().every(value => Math.abs(value) < 4));
  }
});

test('noncommuting Gaussian transport has feasible covariance blocks and matching dual values', () => {
  assert.equal(extensions.gaussianTransport.experiments.length, 21);
  for (const e of extensions.gaussianTransport.experiments) {
    assert.ok(e.minimumJointEigenvalue > -1e-7);
    close(e.cost, e.lower, 1e-7);
    const p = e.p === 'inf' ? Infinity : Number(e.p);
    const displacement = e.source.map((row, i) => row.map((v, j) => v + e.target[i][j] - e.cross[i][j] - e.cross[j][i]));
    close(momentGauge(displacement, p), e.cost, 1e-8);
    if (e.angle === 0 || e.angle === 90) {
      const target = e.angle === 0 ? [.7, 1.6] : [1.6, .7];
      close(e.cost, powerNorm(target.map((s, i) => (s - [2, .55][i]) ** 2), p), 1e-7);
    }
    assert.ok(e.samples.flat().every(x => Math.abs(x) < extensions.gaussianTransport.bound));
    gaussianCovariance(e, 0).flat().forEach((x, i) => close(x, e.source.flat()[i]));
    gaussianCovariance(e, 1).flat().forEach((x, i) => close(x, e.target.flat()[i]));
    for (const t of [.1, .5, .9]) assert.ok(eigen2(gaussianCovariance(e, t)).values[1] > 0);
  }
  const byP = p => extensions.gaussianTransport.experiments.find(e => e.angle === 45 && e.p === p);
  const difference = gaussianCovariance(byP('1'), .5).flat().map((x, i) => x - gaussianCovariance(byP('inf'), .5).flat()[i]);
  assert.ok(Math.hypot(...difference) > .01);
});

test('radial test quotients use variance-normalized exact moments, not sharp constants', () => {
  for (const e of extensions.radial.experiments) {
    close(e.moments[0], 2);
    for (const p of [1, 1.5, 2, 4, Infinity]) {
      close(radialTest(e.moments, 0, p).quotient, 1);
      for (const a of [-.25, -.1, .1, .25]) {
        const r = radialTest(e.moments, a, p), trace = radialTest(e.moments, a, 1);
        assert.ok(r.gram.every(x => x >= 0) && r.variance > 0);
        assert.ok(r.quotient >= trace.quotient - 1e-10);
        if (e.q === '2') assert.ok(r.quotient >= 1);
      }
    }
  }
  assert.deepEqual(extensions.radial.experiments.find(e => e.q === '2').moments, [2, 8, 48]);
});
