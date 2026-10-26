export const BLUE = [37, 99, 219];
export const RED = [223, 71, 84];
export const BOUNDS = { xMin: -4, xMax: 4, yMin: -3.8, yMax: 3.4 };

export function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

export function colorAt(fraction) {
  const s = clamp(fraction, 0, 1);
  return `rgb(${BLUE.map((value, i) => Math.round(value + s * (RED[i] - value))).join(', ')})`;
}

export function interpolate(experiment, time, horizon, output = new Float64Array(experiment.count * 2)) {
  const progress = clamp(time / horizon, 0, 1) * (experiment.frames.length - 1);
  const index = Math.floor(progress);
  const a = experiment.frames[index];
  const b = experiment.frames[Math.min(index + 1, experiment.frames.length - 1)];
  const blend = progress - index;
  for (let i = 0; i < output.length; i += 1) output[i] = a[i] + blend * (b[i] - a[i]);
  const e0 = experiment.energies[index];
  const e1 = experiment.energies[Math.min(index + 1, experiment.energies.length - 1)];
  return { positions: output, energy: e0 + blend * (e1 - e0) };
}

export function mixtureDensity(x, y, mixture) {
  let density = 0;
  for (const { weight, mean, covariance: c } of mixture) {
    const det = c[0][0] * c[1][1] - c[0][1] * c[1][0];
    const dx = x - mean[0];
    const dy = y - mean[1];
    const q = (c[1][1] * dx * dx - 2 * c[0][1] * dx * dy + c[0][0] * dy * dy) / det;
    density += weight * Math.exp(-q / 2) / (2 * Math.PI * Math.sqrt(det));
  }
  return density;
}

export function validateDataset(data) {
  if (data.version !== 1 || !Number.isFinite(data.horizon) || data.horizon <= 0
      || !Array.isArray(data.experiments) || data.experiments.length !== 6) {
    throw new Error('Unsupported experiment data.');
  }
  data.experiments.forEach((experiment, i) => {
    if (experiment.count !== 8 * 2 ** i || experiment.frames.length !== data.frameCount
        || experiment.energies.length !== data.frameCount
        || !experiment.energies.every(Number.isFinite)
        || experiment.frames.some(frame => frame.length !== experiment.count * 2 || !frame.every(Number.isFinite))) {
      throw new Error('Incomplete particle trajectory data.');
    }
  });
  return data;
}
