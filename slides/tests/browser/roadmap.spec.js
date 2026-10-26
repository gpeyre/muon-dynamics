import { test, expect } from '@playwright/test';
import { talkParts } from '../../src/content.js';

for (const viewport of [{ width: 1280, height: 720 }, { width: 1920, height: 1080 }, { width: 390, height: 844 }]) {
  test(`four-part roadmap layout at ${viewport.width}x${viewport.height}`, async ({ page }, testInfo) => {
    await page.setViewportSize(viewport);
    await page.goto('/#/part-1');
    await expect(page.locator('body')).toHaveAttribute('data-lecture-ready', 'true');
    await expect(page.locator('.slides > section')).toHaveCount(35);
    await expect(page.locator('section.roadmap-slide')).toHaveCount(4);
    await expect(page.locator('#index-contents h3')).toHaveCount(4);
    for (const part of talkParts) {
      await page.locator('#open-index').click();
      await page.locator(`[data-slide="${part.id}"]`).click();
      await page.waitForTimeout(250);
      const section = page.locator(`#${part.id}`);
      await expect(section).toHaveClass(/present/);
      await expect(section.locator('canvas')).toHaveCount(4);
      await expect(section.locator('[aria-current="step"]')).toHaveCount(1);
      expect(await section.evaluate(e => e.scrollWidth > e.clientWidth + 1)).toBe(false);
      if (viewport.width > 900) expect(await section.evaluate(e => e.scrollHeight > e.clientHeight + 1)).toBe(false);
      for (const preview of await section.locator('.roadmap-item').all()) {
        const current = await preview.getAttribute('aria-current') === 'step';
        const opacity = await preview.evaluate(e => Number(getComputedStyle(e).opacity));
        expect(opacity).toBe(current ? 1 : .26);
        const metrics = await preview.evaluate(e => ({
          clipped: [...e.querySelectorAll('h3,p')].some(x => x.scrollWidth > x.clientWidth + 1),
          font: parseFloat(getComputedStyle(e.querySelector('h3')).fontSize),
        }));
        expect(metrics.clipped).toBe(false); expect(metrics.font).toBeGreaterThanOrEqual(20);
        expect(await preview.locator('canvas').evaluate(c => {
          const rgba = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
          let count = 0; for (let i = 3; i < rgba.length; i += 4) if (rgba[i] > 30) count += 1;
          return count;
        })).toBeGreaterThan(300);
      }
      await page.screenshot({ path: testInfo.outputPath(`${part.id}.png`) });
      await page.locator('#next-slide').click();
      await expect(page.locator(`#${part.start}`)).toHaveClass(/present/);
    }
  });
}

test('all four previews animate, pause together, and link between parts', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  await page.goto('/#/part-2');
  await expect(page.locator('body')).toHaveAttribute('data-lecture-ready', 'true');
  const canvases = page.locator('#part-2 canvas');
  const before = await canvases.evaluateAll(elements => elements.map(c => c.toDataURL()));
  await page.waitForTimeout(800);
  const after = await canvases.evaluateAll(elements => elements.map(c => c.toDataURL()));
  after.forEach((frame, i) => expect(frame).not.toBe(before[i]));
  await page.locator('#part-2 .ambient-toggle').click();
  await expect(page.locator('#part-2 .ambient-toggle')).toHaveAttribute('aria-label', 'Play animations');
  const paused = await canvases.first().getAttribute('data-animation-time');
  await page.waitForTimeout(200);
  expect(await canvases.first().getAttribute('data-animation-time')).toBe(paused);
  await page.locator('#part-2 a[href="#/part-4"]').click();
  await expect(page.locator('#part-4')).toHaveClass(/present/);
  await page.reload();
  await expect(page.locator('#part-4')).toHaveClass(/present/);
});

test('title respects reduced motion and its forward replay loops', async ({ page }) => {
  test.setTimeout(60000);
  // Speed up animation timestamps, while keeping the application's frame-step cap.
  await page.addInitScript(() => {
    const native = window.requestAnimationFrame.bind(window);
    window.requestAnimationFrame = callback => native(t => callback(t * 20));
  });
  await page.goto('/');
  await expect(page.locator('body')).toHaveAttribute('data-ready', 'true');
  const canvas = page.locator('#cover-canvas');
  await expect(canvas).toHaveAttribute('data-particles', '256');
  await expect(page.locator('#title .ambient-toggle')).toHaveAttribute('aria-label', 'Play animations');
  const initial = await canvas.getAttribute('data-animation-time');
  await page.waitForTimeout(150);
  expect(await canvas.getAttribute('data-animation-time')).toBe(initial);
  const before = await canvas.evaluate(c => c.toDataURL());
  await page.locator('#title .ambient-toggle').click();
  await expect.poll(async () => Number(await canvas.getAttribute('data-animation-time')), { timeout: 30000, intervals: [100] }).toBeGreaterThan(20.5);
  expect(Number(await canvas.getAttribute('data-progress'))).toBeLessThan(.4);
  expect(await canvas.evaluate(c => c.toDataURL())).not.toBe(before);
  await page.locator('#title .ambient-toggle').click();
  const paused = await canvas.getAttribute('data-animation-time');
  await page.waitForTimeout(150);
  expect(await canvas.getAttribute('data-animation-time')).toBe(paused);
});
