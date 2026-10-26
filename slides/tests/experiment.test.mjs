import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import { BLUE, RED, BOUNDS, colorAt, interpolate, mixtureDensity, validateDataset } from '../src/experiment.js';
import { buildContours } from '../src/plot.js';

const data = JSON.parse(await readFile(new URL('../public/data/measures.json', import.meta.url)));

test('all six independent particle systems have complete, descending trajectories', () => {
  assert.equal(validateDataset(data), data);
  assert.equal(data.targetSamples.length, 2 * data.targetCount);
  assert.equal(data.targetCount, 2048);
  for (const experiment of data.experiments) {
    assert.ok(experiment.energies.every(value => value >= -1e-7));
    for (let i = 1; i < data.frameCount; i += 1) {
      assert.ok(experiment.energies[i] <= experiment.energies[i - 1] + 1e-7);
    }
    assert.ok(experiment.energies.at(-1) < .01 * experiment.energies[0]);
    assert.deepEqual(experiment.frames[0], data.experiments.at(-1).frames[0].slice(0, 2 * experiment.count));
    for (const frame of experiment.frames) {
      for (let i = 0; i < frame.length; i += 2) {
        assert.ok(frame[i] > BOUNDS.xMin && frame[i] < BOUNDS.xMax);
        assert.ok(frame[i + 1] > BOUNDS.yMin && frame[i + 1] < BOUNDS.yMax);
      }
    }
  }
});

test('time interpolation has exact endpoints and clamps to the saved interval', () => {
  const experiment = data.experiments[3];
  for (const time of [-1, 0]) {
    assert.deepEqual([...interpolate(experiment, time, data.horizon).positions], experiment.frames[0]);
  }
  for (const time of [data.horizon, 100]) {
    assert.deepEqual([...interpolate(experiment, time, data.horizon).positions], experiment.frames.at(-1));
  }
  const result = interpolate(experiment, .08, data.horizon);
  result.positions.forEach((value, i) => assert.ok(Math.abs(value - (experiment.frames[0][i] + experiment.frames[1][i]) / 2) < 1e-12));
  assert.ok(Math.abs(result.energy - (experiment.energies[0] + experiment.energies[1]) / 2) < 1e-12);
});

test('the population density and contours describe a normalized Gaussian mixture', () => {
  let mass = 0;
  const step = .05;
  for (let x = -8 + step / 2; x < 8; x += step) {
    for (let y = -8 + step / 2; y < 8; y += step) {
      const value = mixtureDensity(x, y, data.mixture);
      assert.ok(value >= 0 && Number.isFinite(value));
      mass += value * step * step;
    }
  }
  assert.ok(Math.abs(mass - 1) < 1e-8);
  const contours = buildContours(data.mixture);
  assert.equal(contours.length, 6);
  assert.ok(contours.every(contour => contour.coordinates.length > 0));
});

test('colors run from blue to red, with bounded endpoints', () => {
  assert.equal(colorAt(-1), `rgb(${BLUE.join(', ')})`);
  assert.equal(colorAt(2), `rgb(${RED.join(', ')})`);
  assert.notEqual(colorAt(.5), colorAt(0));
});

test('invalid frames and nonfinite energies are rejected', () => {
  assert.throws(() => validateDataset({ ...data, version: 0 }));
  const broken = structuredClone(data);
  broken.experiments[0].frames[0].pop();
  assert.throws(() => validateDataset(broken), /Incomplete/);
  const nonfinite = structuredClone(data);
  nonfinite.experiments[0].energies[0] = NaN;
  assert.throws(() => validateDataset(nonfinite), /Incomplete/);
});
