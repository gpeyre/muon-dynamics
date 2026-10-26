import { test, expect } from '@playwright/test';

async function ready(page, hash = '') {
  await page.goto(`/${hash}`);
  await expect(page.locator('body')).toHaveAttribute('data-ready', 'true');
  await page.evaluate(() => document.fonts.ready);
}

async function canvasPixels(page) {
  return page.locator('#particle-canvas').evaluate(canvas => {
    const pixels = canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height).data;
    let visible = 0;
    let blue = 0;
    let red = 0;
    for (let i = 0; i < pixels.length; i += 4) {
      if (pixels[i + 3] > 20) visible += 1;
      if (pixels[i + 3] > 180 && pixels[i + 2] > pixels[i] + 50) blue += 1;
      if (pixels[i + 3] > 180 && pixels[i] > pixels[i + 2] + 50) red += 1;
    }
    return { visible, blue, red };
  });
}

for (const viewport of [{ width: 1440, height: 900 }, { width: 1280, height: 720 }, { width: 1920, height: 1080 }, { width: 390, height: 844 }]) {
  test(`layout and nonblank canvas at ${viewport.width}x${viewport.height}`, async ({ page }, testInfo) => {
    await page.setViewportSize(viewport);
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await ready(page);
    await expect(page.locator('#title')).toHaveClass(/present/);
    await page.screenshot({ path: testInfo.outputPath('title.png') });
    await page.locator('#next-slide').click();
    await expect(page.locator('#measures')).toHaveClass(/present/);
    await expect(page.locator('#time-slider')).toBeEnabled();
    await page.waitForTimeout(800);
    const layout = await page.locator('#measures').evaluate(section => {
      const selectors = ['h2', '.objective', '.empirical', '.example-equation', '.example p', '.plot-heading', '.experiment-controls'];
      const parent = section.getBoundingClientRect();
      return {
        horizontalOverflow: section.scrollWidth > section.clientWidth + 1,
        verticalOverflow: section.scrollHeight > section.clientHeight + 1,
        outside: selectors.flatMap(selector => [...section.querySelectorAll(selector)])
          .filter(element => {
            const box = element.getBoundingClientRect();
            return box.left < parent.left || box.right > parent.right + 1 || element.scrollWidth > element.clientWidth + 2;
          }).map(element => element.className),
      };
    });
    expect(layout.horizontalOverflow).toBe(false);
    expect(layout.outside).toEqual([]);
    if (viewport.width > 900) expect(layout.verticalOverflow).toBe(false);
    await page.locator('#particle-canvas').scrollIntoViewIfNeeded();
    await page.screenshot({ path: testInfo.outputPath('measures.png') });
    const initial = await canvasPixels(page);
    expect(initial.visible).toBeGreaterThan(1000);
    expect(initial.red).toBeGreaterThan(300);
    await page.locator('#time-slider').fill('16');
    expect((await canvasPixels(page)).blue).toBeGreaterThan(300);
    await page.screenshot({ path: testInfo.outputPath('final.png') });
    expect(errors).toEqual([]);
  });
}

test('particle count, scrubbing, playback, reset and trajectories work independently of navigation', async ({ page }) => {
  await ready(page, '#/measures');
  const slider = page.locator('#time-slider');
  await page.locator('#count-slider').fill('0');
  await expect(page.locator('#count-value')).toHaveText('8');
  await expect(page.locator('#particle-canvas')).toHaveAttribute('data-count', '8');
  await page.locator('#count-slider').fill('5');
  await expect(page.locator('#particle-canvas')).toHaveAttribute('data-count', '256');
  const initialEnergy = Number(await page.locator('#energy-value').textContent());
  const start = await page.locator('#particle-canvas').evaluate(canvas => canvas.toDataURL());
  await slider.fill('8');
  await expect(page.locator('#time-value')).toHaveText('8.00');
  expect(Number(await page.locator('#energy-value').textContent())).toBeLessThan(initialEnergy);
  expect(await page.locator('#particle-canvas').evaluate(canvas => canvas.toDataURL())).not.toBe(start);
  await slider.focus();
  await page.keyboard.press('ArrowLeft');
  await expect(page.locator('#measures')).toHaveClass(/present/);
  await expect(page.locator('#time-value')).toHaveText('7.99');
  await page.locator('#play').click();
  await expect(page.locator('#play')).toHaveAttribute('aria-label', 'Pause');
  await expect.poll(async () => Number(await slider.inputValue())).toBeGreaterThan(8.1);
  await page.locator('#play').click();
  const stoppedTime = await slider.inputValue();
  await page.waitForTimeout(150);
  expect(await slider.inputValue()).toBe(stoppedTime);
  const withTrails = await page.locator('#particle-canvas').evaluate(canvas => canvas.toDataURL());
  await page.locator('#trails').click();
  await expect(page.locator('#trails')).toHaveAttribute('aria-pressed', 'false');
  expect(await page.locator('#particle-canvas').evaluate(canvas => canvas.toDataURL())).not.toBe(withTrails);
  await page.locator('#restart').click();
  await expect(page.locator('#time-value')).toHaveText('0.00');
  await page.locator('#previous-slide').click();
  await expect(page.locator('#slide-number')).toHaveText('01 / 27');
});

test('failed data downloads leave an accessible error and disabled controls', async ({ page }) => {
  await page.route('**/data/measures.json', route => route.fulfill({ status: 503, body: 'Unavailable' }));
  await page.goto('/#/measures');
  await expect(page.locator('#load-status')).toHaveAttribute('role', 'alert');
  await expect(page.locator('#time-slider')).toBeDisabled();
});
