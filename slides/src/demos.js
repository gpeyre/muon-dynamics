import katex from 'katex';
import { geoPath } from 'd3-geo';
import { buildContours } from './plot.js';
import { colorAt, interpolate, clamp, BOUNDS } from './experiment.js';
import { EXPONENTS, COUNTS, OT_EXPONENTS, FLOW_BOUNDS, FIELD_BOUNDS, pLabel, powerNorm, diagonalLMO, eigen2,
  unitBall, clockState, memoryResponse, gaussianQuotient, nsResponse, noiseResponse,
  bentAction, interpolateRows, rectangleKL } from './lecture-math.js';

const RED = '#df4754', BLUE = '#2563db', INK = '#414b58', TEAL = '#168574', GRAY = '#b6bdc7';
const labelP = p => p === Infinity ? 'infinity' : String(p);
const fmt = x => Number.isFinite(x) ? (Math.abs(x) < 1e-4 && x !== 0 ? x.toExponential(1) : x.toFixed(3)) : 'infinity';
const range = (min, max, count = 160) => Array.from({ length: count + 1 }, (_, i) => min + (max - min) * i / count);

function caption(ctx, value, x, y, { color = INK, align = 'left', size = 14, width } = {}) {
  ctx.fillStyle = color; ctx.font = `${size}px Helvetica, Arial, sans-serif`;
  ctx.textAlign = align; ctx.textBaseline = 'middle';
  if (width) ctx.fillText(value, x, y, width); else ctx.fillText(value, x, y);
}

function dot(ctx, xy, radius, color, open = false) {
  ctx.beginPath(); ctx.arc(xy[0], xy[1], radius, 0, 2 * Math.PI);
  if (open) { ctx.strokeStyle = color; ctx.lineWidth = 1; ctx.stroke(); }
  else { ctx.fillStyle = color; ctx.fill(); }
}

function line(ctx, points, color, width = 1.5, dashed = false) {
  ctx.beginPath(); points.forEach((xy, i) => i ? ctx.lineTo(...xy) : ctx.moveTo(...xy));
  ctx.strokeStyle = color; ctx.lineWidth = width; ctx.setLineDash(dashed ? [5, 4] : []); ctx.stroke(); ctx.setLineDash([]);
}

function arrow(ctx, from, to, color) {
  line(ctx, [from, to], color, 1.3);
  const angle = Math.atan2(to[1] - from[1], to[0] - from[0]);
  line(ctx, [[to[0] - 5 * Math.cos(angle - .4), to[1] - 5 * Math.sin(angle - .4)], to,
    [to[0] - 5 * Math.cos(angle + .4), to[1] - 5 * Math.sin(angle + .4)]], color, 1.3);
}

function chart(ctx, box, bounds, { equal = false, xLabel = '', yLabel = '', ticks = true } = {}) {
  let left = box.x + 40, top = box.y + 25, width = box.w - 54, height = box.h - 63;
  const [xmin, xmax, ymin, ymax] = bounds;
  if (equal) {
    const scale = Math.min(width / (xmax - xmin), height / (ymax - ymin));
    const w = scale * (xmax - xmin), h = scale * (ymax - ymin);
    left += (width - w) / 2; top += (height - h) / 2; width = w; height = h;
  }
  const point = (x, y) => [left + (x - xmin) / (xmax - xmin) * width, top + (ymax - y) / (ymax - ymin) * height];
  ctx.strokeStyle = '#dfe4eb'; ctx.lineWidth = 1; ctx.strokeRect(left, top, width, height);
  if (ticks) {
    for (let i = 0; i <= 4; i += 1) {
      const x = xmin + (xmax - xmin) * i / 4, y = ymin + (ymax - ymin) * i / 4;
      caption(ctx, Number(x.toFixed(2)).toString(), point(x, ymin)[0], top + height + 15, { align: 'center', color: '#84909f', size: 10 });
      caption(ctx, Number(y.toFixed(2)).toString(), left - 8, point(xmin, y)[1], { align: 'right', color: '#84909f', size: 10 });
    }
  }
  if (xLabel) caption(ctx, xLabel, left + width / 2, box.y + box.h - 5, { align: 'center', size: 12 });
  if (yLabel) caption(ctx, yLabel, left, box.y + 9, { size: 12 });
  return { point, left, top, width, height, ctx,
    curve(points, color = TEAL, dashed = false, lineWidth = 2) {
      ctx.save(); ctx.beginPath(); ctx.rect(left, top, width, height); ctx.clip();
      line(ctx, points.filter(p => p.every(Number.isFinite)).map(p => point(...p)), color, lineWidth, dashed); ctx.restore();
    } };
}

function ellipse(plot, covariance, color, { fill = false, center = [0, 0] } = {}) {
  const eig = eigen2(covariance), c = Math.cos(eig.angle), s = Math.sin(eig.angle);
  const points = range(0, 2 * Math.PI, 120).map(theta => {
    const a = Math.sqrt(eig.values[0]) * Math.cos(theta), b = Math.sqrt(eig.values[1]) * Math.sin(theta);
    return plot.point(center[0] + c * a - s * b, center[1] + s * a + c * b);
  });
  line(plot.ctx, points, color, 2);
  if (fill) {
    plot.ctx.save(); plot.ctx.fillStyle = color; plot.ctx.globalAlpha = .08; plot.ctx.fill(); plot.ctx.restore();
  }
}

function bars(ctx, box, groups, names, { signed = false } = {}) {
  const all = groups.flatMap(group => group.values);
  const max = Math.max(.1, ...all.map(Math.abs)) * 1.2;
  const plot = chart(ctx, box, [-.5, names.length - .5, signed ? -max : 0, max], { ticks: false });
  line(ctx, [plot.point(-.5, 0), plot.point(names.length - .5, 0)], GRAY, 1);
  groups.forEach((group, g) => group.values.forEach((value, i) => {
    const center = i + (g - (groups.length - 1) / 2) * .22;
    const [x, y] = plot.point(center - .08, value), [right, zero] = plot.point(center + .08, 0);
    ctx.fillStyle = group.color; ctx.fillRect(x, Math.min(y, zero), right - x, Math.max(1, Math.abs(y - zero)));
    if (names.length <= 2) caption(ctx, fmt(value), (x + right) / 2, value >= 0 ? y - 12 : y + 13, { align: 'center', size: box.w < 400 ? 10 : 12 });
  }));
  names.forEach((name, i) => caption(ctx, name, plot.point(i, 0)[0], plot.top + plot.height + 19, { align: 'center', size: box.w < 400 ? 10 : 13, width: plot.width / names.length * .95 }));
  caption(ctx, Number(max.toFixed(2)).toString(), plot.left - 7, plot.top, { align: 'right', size: 10, color: '#84909f' });
  caption(ctx, '0', plot.left - 7, plot.point(0, 0)[1], { align: 'right', size: 10, color: '#84909f' });
  groups.forEach((group, i) => caption(ctx, group.name, box.x + 20 + i * (box.w - 40) / groups.length, box.y + 10,
    { color: group.color, size: 12, width: (box.w - 45) / groups.length }));
}

function cloud(ctx, box, dataset, experiment, time, contours, title) {
  caption(ctx, title, box.x + box.w / 2, box.y + 10, { align: 'center', size: 15 });
  const plot = chart(ctx, { ...box, y: box.y + 15, h: box.h - 15 }, FLOW_BOUNDS, { equal: true, ticks: false });
  ctx.save(); ctx.beginPath(); ctx.rect(plot.left, plot.top, plot.width, plot.height); ctx.clip();
  const [originX, originY] = plot.point(BOUNDS.xMin, BOUNDS.yMax);
  ctx.save(); ctx.translate(originX, originY); const scale = plot.width / (FLOW_BOUNDS[1] - FLOW_BOUNDS[0]) * .05; ctx.scale(scale, scale);
  const path = geoPath(null, ctx);
  contours.forEach(contour => { ctx.beginPath(); path(contour); ctx.strokeStyle = '#2563db70'; ctx.lineWidth = .7 / scale; ctx.stroke(); });
  ctx.restore();
  for (let i = 0; i < experiment.count; i += 1) {
    line(ctx, experiment.frames.map(frame => plot.point(frame[2 * i], frame[2 * i + 1])), '#abb3be40', .7);
    dot(ctx, plot.point(experiment.frames[0][2 * i], experiment.frames[0][2 * i + 1]), 1.7, `${RED}80`, true);
  }
  const frame = interpolate(experiment, time, dataset.horizon);
  for (let i = 0; i < experiment.count; i += 1) dot(ctx, plot.point(frame.positions[2 * i], frame.positions[2 * i + 1]), experiment.count > 64 ? 2 : 2.7, colorAt(time / dataset.horizon));
  ctx.restore();
  return frame.energy;
}

function transportPicture(ctx, box, coupling, { time = null, bend = 0, assignment = null } = {}) {
  const coordinates = [...coupling.x, ...coupling.y];
  const xs = coordinates.map(a => a[0]), ys = coordinates.map(a => a[1]);
  const plot = chart(ctx, box, [Math.min(...xs) - .4, Math.max(...xs) + .4, Math.min(...ys) - .4, Math.max(...ys) + 1.2], { equal: true, ticks: false });
  const edges = [];
  coupling.x.forEach((x, i) => coupling.y.forEach((y, j) => {
    const weight = assignment ? (assignment[i] === j ? 1 / coupling.n : 0) : coupling.plan[i][j];
    if (weight > 1e-6) edges.push({ x, y, weight });
  }));
  for (const edge of edges) {
    const points = bend ? range(0, 1, 50).map(t => plot.point((1 - t) * edge.x[0] + t * edge.y[0], (1 - t) * edge.x[1] + t * edge.y[1] + bend * Math.sin(Math.PI * t)))
      : [plot.point(...edge.x), plot.point(...edge.y)];
    line(ctx, points, '#98a3b759', .5 + 2 * edge.weight * coupling.n);
  }
  coupling.x.forEach(x => dot(ctx, plot.point(...x), 4, RED, time !== null && time > 0));
  coupling.y.forEach(y => dot(ctx, plot.point(...y), 4, BLUE, time !== null && time < 1));
  if (time !== null) edges.forEach(({ x, y, weight }) => dot(ctx, plot.point((1 - time) * x[0] + time * y[0],
    (1 - time) * x[1] + time * y[1] + bend * Math.sin(Math.PI * time)), 1.5 + 3.8 * Math.sqrt(weight * coupling.n), colorAt(time)));
  caption(ctx, 'initial', box.x + 15, box.y + box.h - 10, { color: RED, size: 12 });
  caption(ctx, 'target', box.x + 76, box.y + box.h - 10, { color: BLUE, size: 12 });
  return plot;
}

export class Demo {
  constructor(section, definition, data, refreshIcons) {
    this.section = section; this.definition = definition; this.data = data; this.refreshIcons = refreshIcons;
    this.panel = section.querySelector('.demo-panel'); this.canvas = this.panel.querySelector('canvas');
    this.ctx = this.canvas.getContext('2d'); this.params = {}; this.playing = false; this.revision = 0;
    this.contours = buildContours(data.flow.mixture);
    definition.controls.forEach(control => {
      const input = this.panel.querySelector(`[data-param="${control.key}"]`);
      this.params[control.key] = control.value; input.disabled = false;
      input.addEventListener('input', () => {
        this.params[control.key] = Number(input.value);
        if (control.key === 'time') this.setPlaying(false);
        this.update();
      });
    });
    this.playButton = this.panel.querySelector('.demo-play');
    if (this.playButton) {
      this.playButton.disabled = false;
      this.playButton.addEventListener('click', () => this.togglePlay());
    }
    this.panel.querySelector('.demo-status').hidden = true;
    new ResizeObserver(() => this.draw()).observe(this.canvas);
    this.update();
  }

  setPlaying(playing) {
    this.playing = playing;
    if (!this.playButton) return;
    this.playButton.innerHTML = `<i data-lucide="${playing ? 'pause' : 'play'}"></i>`;
    this.playButton.title = playing ? 'Pause' : 'Play';
    this.playButton.setAttribute('aria-label', this.playButton.title); this.refreshIcons();
  }

  togglePlay() {
    const control = this.definition.controls.find(control => control.key === 'time');
    if (!control) return;
    if (this.params.time >= control.max) this.params.time = 0;
    this.setPlaying(!this.playing); this.update();
  }

  tick(dt) {
    if (!this.playing) return;
    const control = this.definition.controls.find(control => control.key === 'time');
    this.params.time = Math.min(control.max, this.params.time + dt * control.max / 10);
    if (this.params.time >= control.max) this.setPlaying(false);
    this.update();
  }

  update() {
    this.definition.controls.forEach(control => {
      const value = this.params[control.key];
      const input = this.panel.querySelector(`[data-param="${control.key}"]`);
      input.value = value;
      const output = input.parentElement.querySelector('output');
      let display = control.labels ? control.labels[value] : Number(value.toFixed(2)).toString();
      if (this.definition.demo === 'robust' && control.key === 'weight') display = (value / 20).toFixed(2);
      if (this.definition.demo === 'robust' && control.key === 'angle') display = `${value * 2.5}^\\circ`;
      if (this.definition.demo === 'blocks' && control.key === 'scale') display = (.25 + value * .25).toFixed(2);
      if (this.definition.demo === 'attention' && control.key === 'scale') display = (value / 10).toFixed(1);
      if (output.dataset.value !== display) {
        katex.render(display, output, { throwOnError: true }); output.dataset.value = display;
      }
      input.setAttribute('aria-valuetext', display.replaceAll('\\infty', 'infinity').replaceAll('\\', ''));
    });
    this.draw();
  }

  readout(text) { this.panel.querySelector('.demo-readout').textContent = text; }

  draw() {
    if (!this.section.classList.contains('present')) return;
    const { width: w, height: h } = this.canvas.getBoundingClientRect();
    if (w < 10 || h < 10) return;
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    if (this.canvas.width !== Math.round(w * dpr) || this.canvas.height !== Math.round(h * dpr)) {
      this.canvas.width = Math.round(w * dpr); this.canvas.height = Math.round(h * dpr);
    }
    const ctx = this.ctx; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, w, h);
    const b = { x: 0, y: 0, w, h }, a = this.params, kind = this.definition.demo;
    const p = EXPONENTS[a.p], label = pLabel(p), count = COUNTS[a.n];
    const flow = () => this.data.flow.experiments.find(e => e.p === label && e.count === count);
    const coupling = () => this.data.transport.experiments.find(e => e.p === pLabel(OT_EXPONENTS[a.p]) && e.n === (a.n === 1 ? 16 : 8) && e.angle === (a.rotation === undefined ? 30 : a.rotation * 30));

    if (kind === 'polar' || kind === 'spectrum') {
      const response = kind === 'polar' ? [1, 1] : diagonalLMO([1, a.ratio], p).map(Math.abs);
      bars(ctx, { ...b, y: h * .12, h: h * .65 }, [{ name: 'force singular values', values: [1, a.ratio], color: INK },
        { name: kind === 'polar' ? 'polar update' : 'velocity singular values', values: response, color: TEAL }], ['mode 1', 'mode 2']);
      this.readout(kind === 'polar' ? `Anisotropy ${fmt(1 / a.ratio)} becomes 1` : `p = ${labelP(p)}     velocity ratio = ${fmt(response[0] / response[1])}`);
      caption(ctx, kind === 'polar' ? 'Active singular directions keep their orientation.' : 'The full dual-norm speed factor is included.', w / 2, h * .9, { align: 'center', size: 13, width: w - 30 });
    } else if (kind === 'memory') {
      const values = memoryResponse(a.momentum, a.step), plot = chart(ctx, b, [0, 4, 0, 3.5], { xLabel: 'physical time', yLabel: 'matrix rotation angle (radians)' });
      plot.curve(values.map(v => [v.t, v.force]), INK, true); plot.curve(values.map(v => [v.t, v.filtered]), TEAL);
      values.forEach(v => dot(ctx, plot.point(v.t, v.filtered), 2.2, TEAL));
      this.readout(`force: dashed     EMA polar direction: green     final lag ${fmt(values.at(-1).force - values.at(-1).filtered)}`);
    } else if (kind === 'clocks') {
      const plot = chart(ctx, { ...b, h: h * .57 }, [-.1, 2.2, -.15, 1.25], { equal: true, xLabel: 'first diagonal parameter', yLabel: 'second parameter' });
      plot.curve([[2, 1], [1, 0], [0, 0]], GRAY, false, 3);
      const state = clockState(a.time);
      dot(ctx, plot.point(2, 1), 4, RED, true); dot(ctx, plot.point(...state.raw), 6, INK); dot(ctx, plot.point(...state.metric), 5, TEAL);
      const energy = chart(ctx, { x: 0, y: h * .6, w, h: h * .4 }, [0, 2, 0, 2.6], { xLabel: 'clock value', yLabel: 'quadratic energy' });
      energy.curve(range(0, 2).map(t => [t, .5 * clockState(t).raw.reduce((s, x) => s + x * x, 0)]), INK);
      energy.curve(range(0, 2).map(t => [t, .5 * clockState(t).metric.reduce((s, x) => s + x * x, 0)]), TEAL);
      this.readout(`Raw clock: gray     metric clock: green     s(t) = ${fmt(state.rawTime)}`);
    } else if (kind === 'norm' || kind === 'root') {
      const rp = kind === 'root' ? [.25, .5, .75, 1, 2, 4, Infinity][a.p] : p;
      const plot = chart(ctx, b, [-1.4, 1.4, -1.4, 1.4], { equal: true, xLabel: 'first diagonal velocity', yLabel: 'second diagonal velocity' });
      plot.curve(unitBall(rp), BLUE, false, 2.5);
      if (kind === 'norm') {
        const angle = a.angle * Math.PI / 180, gradient = [Math.cos(angle), Math.sin(angle)];
        const j = diagonalLMO(gradient, p), norm = powerNorm(gradient, p === Infinity ? 1 : 2 * p / (2 * p - 1));
        const u = j.map(x => x / norm), tangent = [-gradient[1], gradient[0]];
        plot.curve([u.map((x, i) => x - tangent[i]), u.map((x, i) => x + tangent[i])], GRAY, true);
        arrow(ctx, plot.point(0, 0), plot.point(...u), TEAL); dot(ctx, plot.point(...u), 5, TEAL);
        this.readout(`Diagonal unit ball of S_${p === Infinity ? 'infinity' : 2 * p}     optimal speed = ${fmt(norm)}`);
      } else {
        this.readout(rp < .5 ? 'p < 1/2: the root action is not a norm' : rp < 1 ? '1/2 <= p < 1: a norm, with nonconvex covariance gauge' : 'p >= 1: convex gauge and norm root action');
        if (rp < .5) plot.curve([[1, 0], [0, 1]], RED, true);
      }
    } else if (kind === 'field' || kind === 'covariance') {
      const field = this.data.flow.fields.find(f => f.p === label && f.n === count);
      if (kind === 'field') {
        const plot = chart(ctx, b, FIELD_BOUNDS, { equal: true });
        field.x.forEach((x, i) => { dot(ctx, plot.point(...x), 2.8, RED); arrow(ctx, plot.point(...x), plot.point(x[0] + field.v[i][0] * .48, x[1] + field.v[i][1] * .48), TEAL); });
        this.readout(`${count} initial particles     p = ${labelP(p)}     arrows use one shared scale`);
      } else {
        const radius = Math.sqrt(Math.max(...eigen2(field.forceMoment).values, ...eigen2(field.velocityMoment).values)) * 1.3;
        const plot = chart(ctx, b, [-radius, radius, -radius, radius], { equal: true });
        ellipse(plot, field.forceMoment, INK); ellipse(plot, field.velocityMoment, TEAL);
        const ev = eigen2(field.velocityMoment).values;
        this.readout(`Force moment: gray     velocity moment: green     eigenvalue ratio ${fmt(ev[0] / ev[1])}`);
      }
    } else if (kind === 'flow') {
      const reference = this.data.flow.experiments.find(e => e.p === '1' && e.count === count);
      const selected = flow();
      const e1 = cloud(ctx, { x: 0, y: 0, w: w / 2, h: h * .77 }, this.data.flow, reference, a.time, this.contours, 'Trace / W2');
      const ep = cloud(ctx, { x: w / 2, y: 0, w: w / 2, h: h * .77 }, this.data.flow, selected, a.time, this.contours, `p = ${labelP(p)}`);
      caption(ctx, `f = ${fmt(e1)}`, w / 4, h * .83, { align: 'center' }); caption(ctx, `f = ${fmt(ep)}`, 3 * w / 4, h * .83, { align: 'center' });
      this.readout(`${count} particles     same initialization, target and metric time`);
    } else if (kind === 'transport' || kind === 'geodesic' || kind === 'action') {
      const plan = coupling();
      transportPicture(ctx, b, plan, { time: kind === 'transport' ? null : a.time, bend: a.bend || 0 });
      if (kind === 'action') {
        const action = bentAction(plan, OT_EXPONENTS[a.p], a.bend);
        this.readout(`Static optimum ${fmt(plan.cost)}     path action ${fmt(action)}`);
      } else if (kind === 'geodesic') this.readout(`Distance = ${fmt(Math.sqrt(plan.cost))}     t = ${a.time.toFixed(2)}     weighted moving masses`);
      else this.readout(`Squared cost ${fmt(plan.cost)}     primal/dual gap ${Math.abs(plan.gap).toExponential(1)}`);
    } else if (kind === 'robust') {
      const plan = this.data.transport.experiments.find(e => e.n === 16 && e.p === 'inf' && e.angle === 30);
      const sample = this.data.transport.robust[a.weight * 73 + a.angle];
      transportPicture(ctx, { ...b, h: h * .74 }, plan, { assignment: sample.assignment });
      const plot = chart(ctx, { x: 0, y: h * .74, w, h: h * .26 }, [0, 180, 0, plan.cost * 1.08], { xLabel: 'cost orientation (degrees)' });
      plot.curve(range(0, 72, 72).map(i => [i * 2.5, this.data.transport.robust[a.weight * 73 + i].cost]), TEAL);
      plot.curve([[0, plan.cost], [180, plan.cost]], INK, true);
      dot(ctx, plot.point(a.angle * 2.5, sample.cost), 4, TEAL);
      this.readout(`Current quadratic OT ${fmt(sample.cost)}     optimal robust cost ${fmt(plan.cost)}`);
    } else if (kind === 'gaussianTransport') {
      const source = [a.width, .45], target = [.7, 1.4], current = source.map((s, i) => (1 - a.time) * s + a.time * target[i]);
      const plot = chart(ctx, b, [-2.9, 2.9, -2.1, 2.1], { equal: true });
      const cov = values => [[values[0] ** 2, 0], [0, values[1] ** 2]];
      ellipse(plot, cov(source), RED); ellipse(plot, cov(target), BLUE); ellipse(plot, cov(current), colorAt(a.time), { fill: true });
      this.readout(`Squared distance ${fmt(powerNorm(source.map((s, i) => (s - target[i]) ** 2), p))}     common principal axes`);
    } else if (kind === 'energy') {
      const chosen = flow();
      const plot = chart(ctx, b, [0, 8, -2.7, .8], { xLabel: 'metric time (no rescaling)', yLabel: 'log10 MMD energy' });
      EXPONENTS.forEach(exponent => {
        const e = this.data.flow.experiments.find(e => e.count === count && e.p === pLabel(exponent));
        plot.curve(e.energies.map((value, i) => [i * .08, Math.log10(Math.max(value, 1e-8))]), exponent === p ? TEAL : exponent === 1 ? INK : '#c6ccd4', exponent === 1, exponent === p ? 2.5 : 1.5);
      });
      const current = interpolate(chosen, a.time, 8).energy;
      dot(ctx, plot.point(a.time, Math.log10(current)), 5, TEAL);
      this.readout(`Selected p = ${labelP(p)}: green     trace: dashed     f(t) = ${fmt(current)}`);
    } else if (kind === 'relu') {
      const dataset = this.data.networks.relu;
      const e = dataset.experiments.find(e => e.p === pLabel(OT_EXPONENTS[a.p]) && e.n === [16, 32, 64][a.n]);
      const index = a.time / 15 * 100, k = Math.min(100, Math.floor(index)), f = index - k;
      const prediction = e.predictions[k].map((y, j) => y * (1 - f) + e.predictions[Math.min(100, k + 1)][j] * f);
      const values = [...e.predictions.flat(), ...dataset.target];
      const fit = chart(ctx, { ...b, h: h * .55 }, [-1, 1, Math.min(...values) - .08, Math.max(...values) + .1], { xLabel: 'input', yLabel: 'network prediction' });
      fit.curve(dataset.grid.map((z, j) => [z, e.predictions[0][j]]), RED, true);
      fit.curve(dataset.grid.map((z, j) => [z, dataset.target[j]]), BLUE, true, 2.5);
      fit.curve(dataset.grid.map((z, j) => [z, prediction[j]]), colorAt(a.time / 15));
      const points = chart(ctx, { x: 0, y: h * .57, w, h: h * .43 }, [-4, 4, -4, 4], { equal: true, ticks: false, yLabel: 'inner-weight projection (w, b)' });
      const frame = interpolateRows(e.frames, a.time / 15);
      for (let i = 0; i < e.n; i += 1) {
        line(ctx, e.frames.map(row => points.point(row[i][1], row[i][2])), '#abb3be60', .6);
        dot(ctx, points.point(e.frames[0][i][1], e.frames[0][i][2]), 2, RED, true);
        dot(ctx, points.point(frame[i][1], frame[i][2]), 2.7, colorAt(a.time / 15));
      }
      const loss = e.losses[k] * (1 - f) + e.losses[Math.min(100, k + 1)] * f;
      this.readout(`${e.n} neurons     p = ${labelP(OT_EXPONENTS[a.p])}     loss = ${fmt(loss)}     teacher: dashed blue`);
    } else if (kind === 'attention') {
      const n = [4, 16, 64][a.n], scale = a.scale / 10;
      const e = this.data.networks.attention.experiments.find(e => e.n === n && e.scale === scale);
      const size = Math.min(w - 70, h - 90), left = (w - size) / 2 + 10, top = (h - size) / 2;
      for (let j = 0; j < 8; j += 1) {
        for (let i = 0; i < 8; i += 1) {
          ctx.fillStyle = `rgba(37, 99, 219, ${e.weights[j][i]})`;
          ctx.fillRect(left + i * size / 8, top + j * size / 8, size / 8, size / 8);
          ctx.strokeStyle = '#e2e7ef'; ctx.lineWidth = .5; ctx.strokeRect(left + i * size / 8, top + j * size / 8, size / 8, size / 8);
        }
        caption(ctx, String(j + 1), left - 12, top + (j + .5) * size / 8, { align: 'right', size: 11 });
        caption(ctx, String(j + 1), left + (j + .5) * size / 8, top + size + 15, { align: 'center', size: 11 });
      }
      caption(ctx, 'query token j', left, top - 17, { size: 12 });
      caption(ctx, 'key token i', left + size / 2, top + size + 35, { align: 'center', size: 12 });
      this.readout(`${n} heads     mean per-head effective tokens = ${e.effectiveTokens.toFixed(2)} / 8     color: weight 0 to 1`);
    } else if (kind === 'network') {
      const variance = [.6, 1, 1.8][a.variance];
      const e = this.data.gaussian.experiments.find(e => e.p === label && e.variance === variance);
      const covariance = interpolateRows(e.covariance, a.time / 4);
      const plot = chart(ctx, { ...b, h: h * .64 }, [-2.6, 2.6, -2.6, 2.6], { equal: true, xLabel: 'outer weight u', yLabel: 'inner weight v' });
      ellipse(plot, [[variance, 0], [0, variance]], RED); ellipse(plot, covariance, colorAt(a.time / 4), { fill: true });
      const graph = chart(ctx, { x: 0, y: h * .65, w, h: h * .35 }, [0, 4, 0, 1.12], { xLabel: 'metric time', yLabel: 'predictor coefficient' });
      graph.curve(e.covariance.map((s, i) => [i * .04, s[0][1]]), TEAL); graph.curve([[0, 1], [4, 1]], BLUE, true);
      dot(ctx, graph.point(a.time, covariance[0][1]), 4, TEAL);
      this.readout(`Teacher coefficient 1     learned ${fmt(covariance[0][1])}     loss ${fmt(.5 * (covariance[0][1] - 1) ** 2)}`);
    } else if (kind === 'blocks') {
      const values = this.data.blocks[a.scale], mode = ['full', 'sum', 'max'][a.mode];
      const names = ['block u / 1', 'block u / 2', 'block v / 1', 'block v / 2'];
      bars(ctx, { ...b, y: h * .12, h: h * .75 }, [{ name: 'force spectrum', values: values.force.flat(), color: INK },
        { name: `${mode} velocity spectrum`, values: values.velocity[mode].flat(), color: TEAL }], names);
      this.readout(`Two matrix blocks     second-block force scale c = ${values.scale.toFixed(2)}`);
    } else if (kind === 'collapse') {
      const reflected = a.mode === 1, height = .8 * (reflected ? Math.abs(1 - 2 * a.time) : 1), L = a.separation;
      const plot = chart(ctx, { ...b, h: h * .56 }, [-.2, 4.3, -1.1, 1.1], { equal: true });
      const rectangle = (x, extent, color, fill = false) => {
        const points = [[x, -extent], [x + 1, -extent], [x + 1, extent], [x, extent], [x, -extent]].map(xy => plot.point(...xy));
        line(ctx, points, color, 2);
        if (fill) { ctx.save(); ctx.fillStyle = color; ctx.globalAlpha = .09; ctx.fill(); ctx.restore(); }
      };
      rectangle(0, .8, RED); rectangle(L, .8, BLUE); rectangle(L * a.time, height, colorAt(a.time), true);
      const graph = chart(ctx, { x: 0, y: h * .59, w, h: h * .41 }, [0, 1, 0, 10], { xLabel: 'geodesic time', yLabel: 'KL to standard Gaussian' });
      graph.curve(range(0, .499, 100).map(t => [t, rectangleKL(t, L, .8, reflected)]), TEAL);
      graph.curve(range(.501, 1, 100).map(t => [t, rectangleKL(t, L, .8, reflected)]), TEAL);
      graph.curve([[0, rectangleKL(0, L, .8, false)], [1, rectangleKL(1, L, .8, false)]], INK, true);
      if (reflected) graph.curve([[.5, 0], [.5, 10]], GRAY, true);
      const kl = rectangleKL(a.time, L, .8, reflected);
      if (Number.isFinite(kl)) dot(ctx, graph.point(a.time, Math.min(9.8, kl)), 4, TEAL);
      this.readout(`Both maps are optimal     cost = ${fmt(L * L)}     KL(t) = ${fmt(kl)}`);
    } else if (kind === 'pl') {
      const plot = chart(ctx, b, [0, 4, 0, 1.05], { xLabel: 'metric time', yLabel: 'guaranteed energy envelope, E(0) = 1' });
      plot.curve(range(0, 4).map(t => [t, Math.exp(-2 * a.kappa * t)]), INK, true);
      plot.curve(range(0, 4).map(t => [t, Math.exp(-2 * a.kappa / a.scale * t)]), TEAL);
      this.readout(`Unscaled gauge: dashed     scaled gauge a gamma_p: green     rate = ${fmt(2 * a.kappa / a.scale)}`);
    } else if (kind === 'poincare') {
      const exponent = [.5, .75, 1, 2, Infinity][a.p];
      const plot = chart(ctx, b, [0, 1, .45, 3.1], { xLabel: 'quadratic perturbation amplitude', yLabel: 'Rayleigh quotient' });
      plot.curve(range(0, 1).map(e => [e, gaussianQuotient(e, 1)]), INK, true);
      plot.curve(range(0, 1).map(e => [e, gaussianQuotient(e, exponent)]), TEAL);
      plot.curve([[0, 1], [1, 1]], GRAY, true);
      dot(ctx, plot.point(a.epsilon, gaussianQuotient(a.epsilon, exponent)), 5, TEAL);
      this.readout(`p = ${labelP(exponent)}     test quotient ${fmt(gaussianQuotient(a.epsilon, exponent))}     Gaussian W2 constant = 1`);
    } else if (kind === 'ns') {
      const plot = chart(ctx, b, [0, 1.8, -1.2, 1.5], { xLabel: 'input singular value / fixed scale', yLabel: 'singular-value response' });
      const start = plot.point(0, 1.5), end = plot.point(1, -1.2);
      ctx.fillStyle = '#1685740c'; ctx.fillRect(start[0], start[1], end[0] - start[0], end[1] - start[1]);
      plot.curve(range(0, 1.8).map(s => [s, clamp(nsResponse(s, a.iterations), -2, 2)]), TEAL);
      plot.curve([[0, 1], [1.8, 1]], INK, true); plot.curve([[1, -1.2], [1, 1.5]], GRAY, true);
      dot(ctx, plot.point(a.ratio, clamp(nsResponse(a.ratio, a.iterations), -1.15, 1.45)), 5, a.ratio <= 1 ? TEAL : RED);
      this.readout(`Classical cubic NS, fixed alpha = 1     ${a.ratio <= 1 ? 'inside the verified stable interval' : 'outside the verified stable interval'}`);
    } else if (kind === 'noise') {
      const result = noiseResponse(a.rho, p);
      bars(ctx, { ...b, y: h * .08, h: h * .8 }, [{ name: 'normalize the mean force', values: result.deterministic, color: INK },
        { name: 'mean normalized velocity', values: result.average, color: TEAL }], ['first diagonal component', 'second diagonal component'], { signed: true });
      this.readout(`Mean force stays diag(1, 0.3)     velocity bias = ${fmt(Math.hypot(...result.average.map((v, i) => v - result.deterministic[i])))}`);
    }
    this.canvas.dataset.revision = String(++this.revision);
    this.canvas.dataset.demo = kind;
  }
}
