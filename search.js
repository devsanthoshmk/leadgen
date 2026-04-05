export default async ({ page }) => {
  // Use a real browser-like context
  await page.goto("https://www.google.com", {
    waitUntil: "domcontentloaded",
    timeout: 60000
  });

  // Handle consent screen (very common in India/EU)
  try {
    await page.locator('button:has-text("Accept")').click({ timeout: 5000 });
  } catch (e) {}

  // Wait until search box is actually visible
  await page.waitForSelector('textarea[name="q"]', {
    timeout: 15000,
    state: "visible"
  });

  // Click + type like human
  await page.click('textarea[name="q"]');

  await page.type(
    'textarea[name="q"]',
    'site:linkedin.com/company "restorants in chennai"',
    { delay: 120 }
  );

  await page.keyboard.press("Enter");

  // Wait for results to actually load
  await page.waitForSelector('#search', { timeout: 15000 });

  // Keep open
  await new Promise(() => {});
};