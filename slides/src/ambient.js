import { geoPath } from 'd3-geo';
import { BOUNDS, clamp, colorAt, interpolate } from './experiment.js';
import { buildContours } from './plot.js';
import { diagonalLMO, eigen2, gaussianCovariance, powerNorm, unitBall } from './lecture-math.js';

const RED = '#df4754', BLUE = '#2563db', TEAL = '#168574', GRAY = '#aab5c3';
const smooth = x => { const t = clamp(x, 0, 1); return t * t * (3 - 2 * t); };

// The reset is hidden by a fade, never by running a descent trajectory backwards.
export function loopState(seconds, duration = 18) {
  const phase = ((seconds % duration) + duration) % duration / duration;
  return { phase, progress: clamp((phase - .05) / .82, 0, 1),
    opacity: Math.min(smooth(phase / .055), smooth((1 - phase) / .085)) };
}

function stroke(ctx, points, color, width = 1.5, dashed = false) {
  ctx.beginPath(); points.forEach((p, i) => i ? ctx.lineTo(...p) : ctx.moveTo(...p));
  ctx.strokeStyle = color; ctx.lineWidth = width;
  ctx.setLineDash(dashed ? [5, 4] : []); ctx.stroke(); ctx.setLineDash([]);
}

function point(ctx, xy, radius, color, core = false) {
  ctx.beginPath(); ctx.arc(...xy, radius, 0, 2 * Math.PI); ctx.fillStyle = color; ctx.fill();
  if (core) {
    ctx.beginPath(); ctx.arc(...xy, Math.max(.8, radius * .32), 0, 2 * Math.PI);
    ctx.fillStyle = '#ffffff'; ctx.fill();
  }
}

function covarianceContour(ctx, map, covariance, color, scale = 1, fill = false) {
  const { values, angle } = eigen2(covariance), c = Math.cos(angle), s = Math.sin(angle);
  const points = Array.from({ length: 121 }, (_, i) => {
    const t = i / 120 * 2 * Math.PI;
    const x = scale * Math.sqrt(values[0]) * Math.cos(t), y = scale * Math.sqrt(values[1]) * Math.sin(t);
    return map(c * x - s * y, s * x + c * y);
  });
  stroke(ctx, points, color, 1.4);
  if (fill) { ctx.save(); ctx.globalAlpha *= .08; ctx.fillStyle = color; ctx.fill(); ctx.restore(); }
}

class Scene {
  constructor(canvas) {
    this.canvas = canvas; this.ctx = canvas.getContext('2d'); this.seconds = 0;
    this.resize = new ResizeObserver(() => this.draw(this.seconds));
    this.resize.observe(canvas);
  }

  prepare(seconds) {
    this.seconds = seconds;
    if (!this.canvas.closest('section').classList.contains('present')) return null;
    const { width: w, height: h } = this.canvas.getBoundingClientRect();
    if (w < 1 || h < 1) return null;
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    const resized = this.canvas.width !== Math.round(w * ratio) || this.canvas.height !== Math.round(h * ratio);
    if (resized) { this.canvas.width = Math.round(w * ratio); this.canvas.height = Math.round(h * ratio); }
    this.ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    this.ctx.clearRect(0, 0, w, h);
    this.canvas.dataset.animationTime = seconds.toFixed(4);
    return { ctx: this.ctx, w, h, ratio, resized };
  }
}

export class CoverScene extends Scene {
  constructor(canvas, dataset) {
    super(canvas);
    this.dataset = dataset; this.experiment = dataset.experiments.at(-1);
    this.contours = buildContours(dataset.mixture);
    this.background = document.createElement('canvas');
  }

  draw(seconds = this.seconds) {
    if (!this.dataset) return;
    const view = this.prepare(seconds); if (!view) return;
    const { ctx, w, h, ratio } = view;
    const box = this.canvas.getBoundingClientRect();
    const text = document.querySelector('.title-content').getBoundingClientRect();
    const portrait = w <= 900 && h > w;
    const region = portrait
      ? { x: 16, y: text.bottom - box.top + 12, w: w - 32, h: h - (text.bottom - box.top) - 66 }
      : { x: text.right - box.left + 16, y: 24, w: w - (text.right - box.left) - 34, h: h - 65 };
    const scale = Math.max(1, Math.min(region.w / 8, region.h / 7.2));
    const cx = region.x + region.w / 2, cy = region.y + region.h / 2;
    const map = (x, y) => [cx + x * scale, cy - (y + .2) * scale];
    const key = [w, h, ratio, ...Object.values(region)].join(':');
    if (key !== this.backgroundKey) {
      this.backgroundKey = key;
      this.background.width = this.canvas.width; this.background.height = this.canvas.height;
      const bg = this.background.getContext('2d'); bg.setTransform(ratio, 0, 0, ratio, 0, 0);
      for (let i = 0; i < this.experiment.count; i += 1) {
        stroke(bg, this.experiment.frames.map(frame => map(frame[2 * i], frame[2 * i + 1])), '#b7c8dd22', .8);
      }
      bg.save(); bg.translate(...map(BOUNDS.xMin, BOUNDS.yMax)); bg.scale(.05 * scale, .05 * scale);
      const path = geoPath(null, bg);
      for (const contour of this.contours) {
        bg.beginPath(); path(contour); bg.fillStyle = '#62aaff08'; bg.fill();
        bg.strokeStyle = '#62aaffbb'; bg.lineWidth = 1 / (.05 * scale); bg.stroke();
      }
      bg.restore();
    }
    ctx.drawImage(this.background, 0, 0, w, h);
    const state = loopState(seconds, 20), time = state.progress * this.dataset.horizon;
    const { positions } = interpolate(this.experiment, time, this.dataset.horizon);
    const index = state.progress * (this.experiment.frames.length - 1), k = Math.floor(index);
    const luminous = `rgb(${[255, 91, 105].map((v, i) => Math.round(v + state.progress * ([91, 166, 255][i] - v))).join(',')})`;
    ctx.save(); ctx.globalAlpha = state.opacity;
    for (let i = 0; i < this.experiment.count; i += 1) {
      const tail = this.experiment.frames.slice(Math.max(0, k - 9), k + 1).map(row => map(row[2 * i], row[2 * i + 1]));
      tail.push(map(positions[2 * i], positions[2 * i + 1]));
      stroke(ctx, tail, luminous, 1.15);
    }
    ctx.shadowColor = luminous; ctx.shadowBlur = 9;
    for (let i = 0; i < this.experiment.count; i += 1) point(ctx, map(positions[2 * i], positions[2 * i + 1]), portrait ? 2 : 2.8, luminous, true);
    ctx.restore();
    this.canvas.dataset.progress = state.progress.toFixed(5);
    this.canvas.dataset.loopOpacity = state.opacity.toFixed(5);
    this.canvas.dataset.particles = this.experiment.count;
  }
}

export class RoadmapPreview extends Scene {
  constructor(canvas, data) {
    super(canvas); this.kind = Number(canvas.dataset.preview); this.data = data;
    this.gaussian = data.extensions.gaussianTransport.experiments.find(e => e.angle === 45 && e.p === 'inf');
    this.network = data.networks.relu.experiments.find(e => e.n === 32 && e.p === 'inf');
  }

  draw(seconds = this.seconds) {
    if (!this.data) return;
    const view = this.prepare(seconds); if (!view) return;
    const { ctx, w, h } = view;
    const phase = ((seconds % 14) + 14) % 14 / 14;
    if (this.kind === 0) {
      const map = (x, y) => [w / 2 + x * Math.min(w, h) / 2.7, h / 2 - y * Math.min(w, h) / 2.7];
      const mix = .5 - .5 * Math.cos(phase * 2 * Math.PI), p = mix > .999 ? Infinity : 1 / (1 - mix);
      for (const exponent of [1, 2, Infinity]) stroke(ctx, unitBall(exponent, 120).map(x => map(...x)), '#e0e6eb', 1);
      stroke(ctx, unitBall(p, 160).map(x => map(...x)), BLUE, 2.5);
      const g = [.9, .42], q = p === Infinity ? 1 : 2 * p / (2 * p - 1);
      const unit = diagonalLMO(g, p).map(x => x / powerNorm(g, q));
      const endpoint = map(...unit), start = map(0, 0), tangent = [-g[1], g[0]];
      stroke(ctx, [map(unit[0] - tangent[0], unit[1] - tangent[1]), map(unit[0] + tangent[0], unit[1] + tangent[1])], GRAY, 1, true);
      stroke(ctx, [start, endpoint], TEAL, 2.5); point(ctx, endpoint, 5, TEAL, true);
    } else if (this.kind === 1) {
      const state = loopState(seconds + 3, 16), t = state.progress, e = this.gaussian;
      const scale = Math.min(w, h) / 13, map = (x, y) => [w / 2 + x * scale, h / 2 - y * scale];
      covarianceContour(ctx, map, e.source, RED, 3);
      covarianceContour(ctx, map, e.target, BLUE, 3);
      for (const xy of e.samples.filter((_, i) => i % 3 === 0)) stroke(ctx, [map(xy[0], xy[1]), map(xy[2], xy[3])], '#c9d0d94d', .8);
      ctx.save(); ctx.globalAlpha = state.opacity;
      covarianceContour(ctx, map, gaussianCovariance(e, t), colorAt(t), 2, true);
      for (const xy of e.samples) point(ctx, map((1 - t) * xy[0] + t * xy[2], (1 - t) * xy[1] + t * xy[3]), 1.8, colorAt(t));
      ctx.restore();
    } else if (this.kind === 2) {
      const state = loopState(seconds + 6, 18), t = state.progress, dataset = this.data.networks.relu;
      const map = (x, y) => [12 + (x + 1) / 2 * (w - 24), h - 20 - (y + .2) / .8 * (h - 40)];
      stroke(ctx, [map(-1, 0), map(1, 0)], '#e0e6eb', 1);
      stroke(ctx, dataset.grid.map((z, j) => map(z, this.network.predictions[0][j])), `${RED}65`, 1);
      stroke(ctx, dataset.grid.map((z, j) => map(z, dataset.target[j])), BLUE, 2, true);
      const index = t * 100, k = Math.floor(index), f = index - k;
      const prediction = this.network.predictions[k].map((y, i) => y * (1 - f) + this.network.predictions[Math.min(100, k + 1)][i] * f);
      ctx.save(); ctx.globalAlpha = state.opacity;
      stroke(ctx, dataset.grid.map((z, j) => map(z, prediction[j])), colorAt(t), 3);
      dataset.grid.forEach((z, j) => { if (j % 12 === 0) point(ctx, map(z, prediction[j]), 3, colorAt(t), true); });
      ctx.restore();
    } else {
      const state = loopState(seconds + 9, 16), t = state.progress * 4;
      const map = (x, y) => [16 + x / 4 * (w - 32), h - 22 - y * (h - 44)];
      stroke(ctx, [map(0, 1), map(0, 0), map(4, 0)], '#d5dde5', 1);
      for (const [rate, color] of [[1, GRAY], [2, TEAL]]) {
        const curve = Array.from({ length: 101 }, (_, i) => map(i / 25, Math.exp(-rate * i / 25)));
        stroke(ctx, curve, `${color}55`, 1.5);
        ctx.save(); ctx.globalAlpha = state.opacity;
        stroke(ctx, Array.from({ length: 101 }, (_, i) => map(t * i / 100, Math.exp(-rate * t * i / 100))), color, 2.5);
        point(ctx, map(t, Math.exp(-rate * t)), 4.5, color, true); ctx.restore();
      }
    }
  }
}
