import Reveal from 'reveal.js';
import Notes from 'reveal.js/plugin/notes';
import katex from 'katex';
import { createIcons, ArrowUpRight, ChevronLeft, ChevronRight, Maximize, Minimize, Play, Pause, RotateCcw, Route } from 'lucide';
import { colorAt, interpolate, validateDataset } from './experiment.js';
import { ParticlePlot } from './plot.js';
import './style.css';

const icons = { ArrowUpRight, ChevronLeft, ChevronRight, Maximize, Minimize, Play, Pause, RotateCcw, Route };
const $ = id => document.getElementById(id);
const refreshIcons = () => createIcons({ icons });
for (const element of document.querySelectorAll('[data-math]')) {
  katex.render(element.dataset.math, element, { throwOnError: true, output: 'htmlAndMathml' });
}
refreshIcons();

const deck = new Reveal({
  disableLayout: true, controls: false, progress: true, hash: true,
  center: false, transition: 'fade', transitionSpeed: 'fast',
  touch: false, scrollActivationWidth: null, plugins: [Notes],
  keyboardCondition: event => !event.target.closest('input, button, a, select'),
  keyboard: { 32: () => { if (deck.getIndices().h === 1) togglePlayback(); else deck.next(); } },
});

let dataset;
let plot;
let cover;
let playing = false;
let countIndex = 3;
let time = 0;
let lastFrame = null;
let coverClock = 0;
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

function updateNavigation() {
  const index = deck.getIndices().h;
  const total = deck.getTotalSlides();
  $('slide-number').textContent = `${String(index + 1).padStart(2, '0')} / ${String(total).padStart(2, '0')}`;
  $('previous-slide').disabled = index === 0;
  $('next-slide').disabled = index === total - 1;
  if (index !== 1) setPlaying(false);
  requestAnimationFrame(() => { plot?.draw(); cover?.draw(); });
}

function setPlaying(value) {
  playing = value;
  $('play').setAttribute('aria-label', playing ? 'Pause' : 'Play');
  $('play').title = playing ? 'Pause' : 'Play';
  $('play').innerHTML = `<i data-lucide="${playing ? 'pause' : 'play'}"></i>`;
  refreshIcons();
}

function updateExperiment() {
  if (!dataset) return;
  const experiment = dataset.experiments[countIndex];
  $('count-value').textContent = experiment.count;
  $('count-slider').setAttribute('aria-valuetext', `${experiment.count} particles`);
  $('time-value').textContent = time.toFixed(2);
  $('time-slider').value = time;
  $('time-slider').setAttribute('aria-valuetext', `Time ${time.toFixed(2)}`);
  document.documentElement.style.setProperty('--current', colorAt(time / dataset.horizon));
  const { energy } = interpolate(experiment, time, dataset.horizon);
  $('energy-value').textContent = energy.toFixed(3);
  plot.set(experiment, time, $('trails').getAttribute('aria-pressed') === 'true');
}

function togglePlayback() {
  if (!dataset) return;
  if (time >= dataset.horizon) time = 0;
  setPlaying(!playing);
  updateExperiment();
}

$('count-slider').addEventListener('input', event => {
  countIndex = Number(event.target.value);
  updateExperiment();
});
$('time-slider').addEventListener('input', event => {
  setPlaying(false);
  time = Number(event.target.value);
  updateExperiment();
});
$('play').addEventListener('click', togglePlayback);
$('restart').addEventListener('click', () => { setPlaying(false); time = 0; updateExperiment(); });
$('trails').addEventListener('click', () => {
  $('trails').setAttribute('aria-pressed', String($('trails').getAttribute('aria-pressed') !== 'true'));
  updateExperiment();
});
$('previous-slide').addEventListener('click', () => deck.prev());
$('next-slide').addEventListener('click', () => deck.next());
$('fullscreen').addEventListener('click', async () => {
  try {
    if (document.fullscreenElement) await document.exitFullscreen();
    else await document.documentElement.requestFullscreen();
  } catch {
    $('fullscreen').title = 'Full screen is unavailable in this browser';
  }
});
document.addEventListener('fullscreenchange', () => {
  const active = !!document.fullscreenElement;
  $('fullscreen').innerHTML = `<i data-lucide="${active ? 'minimize' : 'maximize'}"></i>`;
  $('fullscreen').setAttribute('aria-label', active ? 'Exit full screen' : 'Full screen');
  $('fullscreen').title = active ? 'Exit full screen' : 'Full screen';
  refreshIcons();
});
if (!document.fullscreenEnabled) $('fullscreen').hidden = true;
document.addEventListener('visibilitychange', () => {
  lastFrame = null;
  if (document.hidden) setPlaying(false);
});
deck.on('slidechanged', updateNavigation);
await deck.initialize();
updateNavigation();

try {
  const response = await fetch(`${import.meta.env.BASE_URL}data/measures.json`);
  if (!response.ok) throw new Error(`Experiment download failed (${response.status})`);
  dataset = validateDataset(await response.json());
  plot = new ParticlePlot($('particle-canvas'), dataset);
  cover = new ParticlePlot($('cover-canvas'), dataset, { cover: true });
  $('time-slider').max = dataset.horizon;
  $('load-status').hidden = true;
  for (const control of document.querySelectorAll('.experiment-controls input, .experiment-controls button')) control.disabled = false;
  updateExperiment();
  document.body.dataset.ready = 'true';
} catch (error) {
  $('load-status').textContent = 'The experiment could not be loaded. Reload to retry.';
  $('load-status').setAttribute('role', 'alert');
  console.error(error);
}

function animate(now) {
  const elapsed = lastFrame === null ? 0 : Math.min((now - lastFrame) / 1000, .1);
  lastFrame = now;
  if (dataset && !document.hidden) {
    if (playing && deck.getIndices().h === 1) {
      time = Math.min(dataset.horizon, time + elapsed * 1.6);
      if (time === dataset.horizon) setPlaying(false);
      updateExperiment();
    } else if (deck.getIndices().h === 0) {
      coverClock += elapsed;
      const phase = reducedMotion.matches ? .72 : (coverClock % 18) / 14;
      const nextTime = Math.min(phase, 1) * dataset.horizon;
      if (cover.time !== nextTime) cover.set(dataset.experiments[4], nextTime);
    }
  }
  requestAnimationFrame(animate);
}
requestAnimationFrame(animate);
