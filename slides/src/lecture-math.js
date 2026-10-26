import { clamp } from './experiment.js';

export const EXPONENTS = [1, 1.5, 2, 4, Infinity];
export const COUNTS = [16, 32, 64, 128];
export const OT_EXPONENTS = [1, 2, Infinity];
export const FLOW_BOUNDS = [-6.5, 4.8, -5.5, 3.4];
export const FIELD_BOUNDS = [-4.8, 2.3, -4.2, 2];
export const pLabel = p => Number.isFinite(p) ? String(p) : 'inf';

export function powerNorm(values, p) {
  const maximum = Math.max(...values.map(Math.abs));
  if (!maximum || p === Infinity) return maximum;
  return maximum * values.reduce((sum, x) => sum + (Math.abs(x) / maximum) ** p, 0) ** (1 / p);
}

// The explicit diagonal restriction of the paper's Schatten duality map.
export function diagonalLMO(values, p) {
  if (p === .5) {
    const top = powerNorm(values, Infinity);
    const active = values.filter(x => Math.abs(x) === top).length;
    return values.map(x => Math.abs(x) === top ? -Math.sign(x) * top / active : 0);
  }
  const q = p === Infinity ? 1 : 2 * p / (2 * p - 1);
  const norm = powerNorm(values, q);
  return values.map(x => norm && x ? -norm * Math.sign(x) * (Math.abs(x) / norm) ** (q - 1) : 0);
}

export function eigen2(s) {
  const a = s[0][0], b = (s[0][1] + s[1][0]) / 2, d = s[1][1];
  const radius = Math.hypot(a - d, 2 * b);
  return { values: [Math.max(0, (a + d + radius) / 2), Math.max(0, (a + d - radius) / 2)],
    angle: .5 * Math.atan2(2 * b, a - d) };
}

export function momentGauge(s, p) { return powerNorm(eigen2(s).values, p); }

export function unitBall(p, samples = 240) {
  const r = 2 * p;
  return Array.from({ length: samples + 1 }, (_, i) => {
    const theta = i / samples * Math.PI * 2;
    const a = [Math.cos(theta), Math.sin(theta)];
    const norm = powerNorm(a, r);
    return a.map(x => x / norm);
  });
}

export function clockState(t) {
  const threshold = Math.log(3) / 2;
  const s = t <= threshold ? 1.5 * (1 - Math.exp(-2 * t)) : 2 - Math.exp(-(t - threshold));
  return { raw: [Math.max(2 - t, 0), Math.max(1 - t, 0)],
    metric: [2 - s, Math.max(1 - s, 0)], rawTime: s };
}

export function memoryResponse(momentum, step) {
  let a = 1, b = 0, previous = 0;
  const points = [];
  for (let k = 0; k <= Math.floor(4 / step); k += 1) {
    const t = k * step;
    const angle = .8 * t;
    if (k) {
      a = momentum * a + (1 - momentum) * Math.cos(angle);
      b = momentum * b + (1 - momentum) * Math.sin(angle);
    }
    let filtered = Math.atan2(b, a);
    while (filtered < previous - Math.PI) filtered += 2 * Math.PI;
    while (filtered > previous + Math.PI) filtered -= 2 * Math.PI;
    points.push({ t, force: angle, filtered });
    previous = filtered;
  }
  return points;
}

export function gaussianQuotient(epsilon, p) {
  const q = p === .5 ? Infinity : p === Infinity ? 1 : 2 * p / (2 * p - 1);
  return powerNorm([1, 2 * Math.abs(epsilon)], q) ** 2 / (1 + 2 * epsilon ** 2);
}

export function nsResponse(s, steps) {
  let h = s;
  for (let i = 0; i < steps; i += 1) h = (3 * h - h ** 3) / 2;
  return h;
}

export function noiseResponse(rho, p) {
  const first = diagonalLMO([1, .3 + 3 * rho], p);
  const second = diagonalLMO([1, .3 - rho], p);
  return { first, second, average: first.map((x, i) => .25 * x + .75 * second[i]),
    deterministic: diagonalLMO([1, .3], p) };
}

export function bentAction(coupling, p, bend) {
  const mean = [0, 0];
  coupling.x.forEach((x, i) => coupling.y.forEach((y, j) => {
    mean[0] += coupling.plan[i][j] * (y[0] - x[0]);
    mean[1] += coupling.plan[i][j] * (y[1] - x[1]);
  }));
  let action = 0;
  const intervals = 240;
  for (let k = 0; k <= intervals; k += 1) {
    const speed = bend * Math.PI * Math.cos(Math.PI * k / intervals);
    const s = coupling.moment;
    const moment = [[s[0][0], s[0][1] + speed * mean[0]],
      [s[1][0] + speed * mean[0], s[1][1] + 2 * speed * mean[1] + speed ** 2]];
    const weight = k === 0 || k === intervals ? 1 : k % 2 ? 4 : 2;
    action += weight * momentGauge(moment, p) / (3 * intervals);
  }
  return action;
}

export function interpolateRows(rows, progress) {
  const index = clamp(progress, 0, 1) * (rows.length - 1);
  const k = Math.floor(index), f = index - k;
  const a = rows[k], b = rows[Math.min(k + 1, rows.length - 1)];
  return a.map((row, i) => row.map((value, j) => value * (1 - f) + b[i][j] * f));
}

export function rectangleKL(t, L, a, reflected) {
  const factor = reflected ? Math.abs(1 - 2 * t) : 1;
  if (factor < 1e-12) return Infinity;
  return -Math.log(2 * a * factor) + Math.log(2 * Math.PI)
    + .5 * ((L * t + .5) ** 2 + 1 / 12 + a * a * factor * factor / 3);
}

export function splittingCoupling(theta) {
  return { n: 2, x: [[-1, 0], [1, 0]], y: [[0, -1], [0, 1]],
    plan: [[theta / 2, (1 - theta) / 2], [(1 - theta) / 2, theta / 2]],
    moment: [[1, 1 - 2 * theta], [1 - 2 * theta, 1]] };
}

export function splittingCost(theta, p) {
  return powerNorm([2 * theta, 2 * (1 - theta)], p);
}

export function gaussianCovariance(experiment, t) {
  return experiment.source.map((row, i) => row.map((value, j) => (1 - t) ** 2 * value
    + t * t * experiment.target[i][j] + t * (1 - t) * (experiment.cross[i][j] + experiment.cross[j][i])));
}

export function radialTest(moments, amplitude, p) {
  const [, m4, m6] = moments, a = amplitude, c = m4 / 2;
  const gram = [1 + 2 * a * (4 - c) + a * a * (4.5 * m4 - 8 * c + c * c), a * a * m4 / 2];
  const variance = 1 + a * a * (m6 - m4 * m4 / 2) / 2;
  const q = p === Infinity ? 1 : 2 * p / (2 * p - 1);
  return { gram, variance, quotient: powerNorm(gram.map(x => Math.sqrt(Math.max(0, x))), q) ** 2 / variance };
}
