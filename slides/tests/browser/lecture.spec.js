import { test, expect } from '@playwright/test';
import { teachingSlides } from '../../src/content.js';

for (const viewport of [{ width: 1440, height: 900 }, { width: 1280, height: 720 }, { width: 390, height: 844 }]) {
  test(`all lecture slides and controls at ${viewport.width}x${viewport.height}`, async ({ page }, testInfo) => {
    test.setTimeout(200000);
    await page.setViewportSize(viewport);
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto('/');
    await expect(page.locator('body')).toHaveAttribute('data-lecture-ready', 'true');
    await page.evaluate(() => document.fonts.ready);
    for (const [i, slide] of teachingSlides.entries()) {
      await page.locator('#open-index').click();
      await page.locator('#index-contents button').nth(i + 2).click();
      const section = page.locator(`#${slide.id}`);
      await expect(section).toHaveClass(/present/);
      await page.waitForTimeout(800);
      const layout = await section.evaluate(element => ({
        overflowX: element.scrollWidth > element.clientWidth + 2,
        overflowY: element.scrollHeight > element.clientHeight + 2,
        formulas: [...element.querySelectorAll('.equation')].filter(e => e.scrollWidth > e.clientWidth + 2).map(e => e.dataset.math),
        smallestEquation: Math.min(...[...element.querySelectorAll('.equation')].map(e => parseFloat(getComputedStyle(e).fontSize))),
        smallestBody: Math.min(...[...element.querySelectorAll('.talk-track > p:not(.qualification)')].map(e => parseFloat(getComputedStyle(e).fontSize))),
      }));
      expect(layout.overflowX, slide.id).toBe(false);
      expect(layout.formulas, slide.id).toEqual([]);
      expect(layout.smallestEquation, slide.id).toBeGreaterThanOrEqual(viewport.width > 900 ? 23 : 18);
      expect(layout.smallestBody, slide.id).toBeGreaterThanOrEqual(viewport.width > 900 ? 22 : 18);
      expect((await section.locator('h2').boundingBox()).y, slide.id).toBeGreaterThanOrEqual(24);
      if (viewport.width > 900) expect(layout.overflowY, slide.id).toBe(false);
      await page.screenshot({ path: testInfo.outputPath(`${slide.id}.png`) });
      if (slide.demo) {
        const canvas = section.locator('canvas');
        const visiblePixels = await canvas.evaluate(c => {
          const pixels = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
          let count = 0; for (let i = 3; i < pixels.length; i += 4) if (pixels[i] > 40) count += 1;
          return count;
        });
        expect(visiblePixels, slide.id).toBeGreaterThan(500);
        expect(Number(await canvas.getAttribute('data-caption-minimum')), slide.id).toBeGreaterThanOrEqual(14);
        expect(JSON.parse(await canvas.getAttribute('data-caption-overflow')), slide.id).toEqual([]);
        const initial = await canvas.evaluate(c => c.toDataURL());
        const readout = await section.locator('.demo-readout').textContent();
        const input = section.locator('input').first();
        const min = await input.getAttribute('min'), max = await input.getAttribute('max');
        await input.fill(await input.inputValue() === max ? min : max);
        const changed = await canvas.evaluate(c => c.toDataURL());
        expect(JSON.parse(await canvas.getAttribute('data-caption-overflow')), slide.id).toEqual([]);
        // Commuting Gaussian geodesics are deliberately independent of p.
        if (slide.id === 'gaussian-transport') {
          expect(changed === initial).toBe(true);
          expect(await section.locator('.demo-readout').textContent()).not.toBe(readout);
        } else expect(changed !== initial, slide.id).toBe(true);
        await canvas.scrollIntoViewIfNeeded();
        await page.screenshot({ path: testInfo.outputPath(`${slide.id}-changed.png`) });
      }
    }
    expect(errors).toEqual([]);
  });
}

test('new slide playback pauses when leaving and deep links reload', async ({ page }) => {
  await page.goto('/#/gaussian-network');
  await expect(page.locator('body')).toHaveAttribute('data-lecture-ready', 'true');
  const slider = page.locator('#gaussian-network-time');
  await page.locator('#gaussian-network .demo-play').click();
  await expect.poll(async () => Number(await slider.inputValue())).toBeGreaterThan(.05);
  await page.locator('#gaussian-network .demo-reset').click();
  await expect(slider).toHaveValue('0');
  await expect(page.locator('#gaussian-network .demo-play')).toHaveAttribute('aria-label', 'Play');
  await page.locator('#gaussian-network .demo-play').click();
  await expect.poll(async () => Number(await slider.inputValue())).toBeGreaterThan(.05);
  await page.locator('#next-slide').click();
  await expect(page.locator('#gaussian-network .demo-play')).toHaveAttribute('aria-label', 'Play');
  await page.waitForURL('**/#/blocks');
  await page.reload();
  await expect(page.locator('#blocks')).toHaveClass(/present/);
  await expect(page.locator('body')).toHaveAttribute('data-lecture-ready', 'true');
});

test('every lecture slider accepts its full range and illustrations stay finite', async ({ page }) => {
  test.setTimeout(120000);
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/#/muon');
  await expect(page.locator('body')).toHaveAttribute('data-lecture-ready', 'true');
  for (const [i, slide] of teachingSlides.entries()) {
    if (!slide.demo) continue;
    await page.locator('#open-index').click();
    await page.locator('#index-contents button').nth(i + 2).click();
    const section = page.locator(`#${slide.id}`);
    await expect(section).toHaveClass(/present/);
    for (const control of slide.controls) {
      const slider = section.locator(`[data-param="${control.key}"]`);
      for (const value of [control.min, control.max, control.value]) {
        const previous = Number(await section.locator('canvas').getAttribute('data-revision'));
        await slider.fill(String(value));
        expect(Number(await section.locator('canvas').getAttribute('data-revision'))).toBeGreaterThan(previous);
        expect(await section.locator('.demo-readout').textContent()).not.toMatch(/NaN|undefined/);
        expect(JSON.parse(await section.locator('canvas').getAttribute('data-caption-overflow')), `${slide.id}: ${control.key}=${value}`).toEqual([]);
      }
    }
  }
  expect(errors).toEqual([]);
});

test('Gaussian fills retain the current measure color and transparency', async ({ page }) => {
  await page.goto('/#/gaussian-transport');
  await expect(page.locator('body')).toHaveAttribute('data-lecture-ready', 'true');
  for (const [time, dominant] of [['0', 0], ['1', 2]]) {
    await page.locator('#gaussian-transport-time').fill(time);
    const pixel = await page.locator('#gaussian-transport canvas').evaluate(canvas => {
      const ctx = canvas.getContext('2d');
      // The centered covariance ellipse contains this pixel, away from its boundary.
      return [...ctx.getImageData(Math.round(canvas.width * .52), Math.round(canvas.height * .49), 1, 1).data];
    });
    expect(pixel[3]).toBeGreaterThan(5);
    expect(pixel[3]).toBeLessThan(40);
    expect(pixel[dominant]).toBeGreaterThan(pixel[dominant === 0 ? 2 : 0]);
  }
});
