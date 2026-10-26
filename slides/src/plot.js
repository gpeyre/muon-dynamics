import { contours } from 'd3-contour';
import { geoPath } from 'd3-geo';
import { BOUNDS, colorAt, interpolate, mixtureDensity } from './experiment.js';

const GRID_STEP = .05;
const DOMAIN_WIDTH = BOUNDS.xMax - BOUNDS.xMin;
const DOMAIN_HEIGHT = BOUNDS.yMax - BOUNDS.yMin;
const GRID_WIDTH = Math.round(DOMAIN_WIDTH / GRID_STEP);
const GRID_HEIGHT = Math.round(DOMAIN_HEIGHT / GRID_STEP);

export function buildContours(mixture) {
  const values = new Float64Array(GRID_WIDTH * GRID_HEIGHT);
  for (let row = 0; row < GRID_HEIGHT; row += 1) {
    for (let col = 0; col < GRID_WIDTH; col += 1) {
      values[row * GRID_WIDTH + col] = mixtureDensity(
        BOUNDS.xMin + (col + .5) * GRID_STEP, BOUNDS.yMax - (row + .5) * GRID_STEP, mixture,
      );
    }
  }
  return contours().size([GRID_WIDTH, GRID_HEIGHT]).thresholds([.012, .035, .07, .115, .17, .225])(values);
}

export class ParticlePlot {
  constructor(canvas, dataset, { cover = false } = {}) {
    this.canvas = canvas;
    this.context = canvas.getContext('2d');
    this.dataset = dataset;
    this.cover = cover;
    this.contours = buildContours(dataset.mixture);
    this.experiment = dataset.experiments[cover ? 4 : 3];
    this.time = 0;
    this.showTrails = true;
    this.resizeObserver = new ResizeObserver(() => this.draw());
    this.resizeObserver.observe(canvas);
  }

  set(experiment, time, trails = true) {
    this.experiment = experiment;
    this.time = time;
    this.showTrails = trails;
    this.draw();
  }

  draw() {
    const { canvas, context: ctx, experiment, dataset, cover } = this;
    const { width, height } = canvas.getBoundingClientRect();
    if (width < 1 || height < 1) return;
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    const pixelWidth = Math.round(width * ratio);
    const pixelHeight = Math.round(height * ratio);
    if (canvas.width !== pixelWidth || canvas.height !== pixelHeight) {
      canvas.width = pixelWidth;
      canvas.height = pixelHeight;
    }
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.clearRect(0, 0, width, height);
    const narrow = width < 700;
    const scale = cover
      ? Math.min(width * (narrow ? .14 : .10), height * .14)
      : Math.min((width - 52) / DOMAIN_WIDTH, (height - 52) / DOMAIN_HEIGHT);
    const centerX = cover ? width * (narrow ? .64 : .79) : width / 2 + 8;
    const centerY = cover ? height * (narrow ? .82 : .56) : height / 2 - 7;
    const yOffset = cover ? 0 : (BOUNDS.yMin + BOUNDS.yMax) / 2;
    const point = (x, y) => [centerX + x * scale, centerY - (y - yOffset) * scale];
    const [left, top] = point(BOUNDS.xMin, BOUNDS.yMax);
    const plotWidth = DOMAIN_WIDTH * scale;
    const plotHeight = DOMAIN_HEIGHT * scale;
    if (!cover) this.drawAxes(left, top, plotWidth, plotHeight, point);

    ctx.save();
    if (!cover) {
      ctx.beginPath();
      ctx.rect(left, top, plotWidth, plotHeight);
      ctx.clip();
    }
    ctx.globalAlpha = cover ? .67 : 1;
    ctx.save();
    ctx.translate(left, top);
    ctx.scale(GRID_STEP * scale, GRID_STEP * scale);
    const path = geoPath(null, ctx);
    for (const contour of this.contours) {
      ctx.beginPath();
      path(contour);
      ctx.fillStyle = 'rgba(37, 99, 219, .018)';
      ctx.fill();
      ctx.strokeStyle = 'rgba(37, 99, 219, .43)';
      ctx.lineWidth = (cover ? 1.1 : .9) / (GRID_STEP * scale);
      ctx.stroke();
    }
    ctx.restore();

    if (this.showTrails) {
      ctx.strokeStyle = cover ? 'rgba(125, 133, 143, .19)' : 'rgba(125, 133, 143, .22)';
      ctx.lineWidth = cover ? .8 : .75;
      ctx.beginPath();
      for (let i = 0; i < experiment.count; i += 1) {
        experiment.frames.forEach((frame, frameIndex) => {
          const [x, y] = point(frame[2 * i], frame[2 * i + 1]);
          if (frameIndex === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        });
      }
      ctx.stroke();
    }

    if (this.time > 0 && !cover) {
      ctx.strokeStyle = 'rgba(223, 71, 84, .50)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      const initial = experiment.frames[0];
      for (let i = 0; i < experiment.count; i += 1) {
        const [x, y] = point(initial[2 * i], initial[2 * i + 1]);
        ctx.moveTo(x + 2.1, y);
        ctx.arc(x, y, 2.1, 0, 2 * Math.PI);
      }
      ctx.stroke();
    }
    const { positions } = interpolate(experiment, this.time, dataset.horizon);
    const radius = cover ? 2.7 : Math.max(2.6, 5.1 - Math.log2(experiment.count / 8) * .45);
    ctx.fillStyle = colorAt(this.time / dataset.horizon);
    ctx.strokeStyle = 'rgba(255, 255, 255, .9)';
    ctx.lineWidth = .7;
    for (let i = 0; i < experiment.count; i += 1) {
      const [x, y] = point(positions[2 * i], positions[2 * i + 1]);
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, 2 * Math.PI);
      ctx.fill();
      if (!cover) ctx.stroke();
    }
    ctx.restore();
    canvas.dataset.time = String(this.time);
    canvas.dataset.count = String(experiment.count);
  }

  drawAxes(left, top, width, height, point) {
    const ctx = this.context;
    ctx.strokeStyle = '#e0e5ec';
    ctx.lineWidth = 1;
    ctx.strokeRect(left, top, width, height);
    ctx.fillStyle = '#929ba7';
    ctx.font = '14px Helvetica, Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    for (const value of [-3, -1, 1, 3]) {
      const [x] = point(value, 0);
      ctx.fillText(String(value), x, top + height + 8);
      ctx.beginPath(); ctx.moveTo(x, top + height); ctx.lineTo(x, top + height + 3); ctx.stroke();
    }
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    for (const value of [-2, 0, 2]) {
      const [, y] = point(0, value);
      ctx.fillText(String(value), left - 8, y);
      ctx.beginPath(); ctx.moveTo(left - 3, y); ctx.lineTo(left, y); ctx.stroke();
    }
  }
}
