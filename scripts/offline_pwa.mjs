// Offline check for the field guide. Run after `npm install playwright` and with
// scripts/serve_guide.py already listening. Uses the system Chrome channel.
import { chromium } from "playwright";

const base = process.env.GUIDE_URL || "http://127.0.0.1:4173";

const browser = await chromium.launch({
  channel: "chrome",
  headless: true,
  args: ["--no-sandbox"],
});
const context = await browser.newContext();
const page = await context.newPage();
await page.goto(base + "/index.html", { waitUntil: "networkidle" });
await page.waitForSelector("text=What do you need first?");
await page.waitForFunction(() => navigator.serviceWorker.controller !== null, null, {
  timeout: 15000,
});

await context.setOffline(true);
await page.reload({ waitUntil: "domcontentloaded" });
await page.waitForSelector("text=Not medical advice");
const offlineBanner = await page.locator("#net").innerText();
if (!/offline/i.test(offlineBanner)) {
  throw new Error("expected offline banner, got: " + offlineBanner);
}

await page.locator("#q").fill("cattail");
await page.waitForSelector("text=Broadleaf cattail");
await page.locator("#hits a").first().click();
await page.waitForSelector("text=DEADLY LOOK-ALIKES");
const body = await page.locator("article").innerText();
if (!/single identification/i.test(body)) {
  throw new Error("plant page missing the single-identification rule");
}
if (!/Typha latifolia/.test(body)) {
  throw new Error("plant page missing the scientific name");
}

await page.goto(base + "/#/page/bleeding-control");
await page.waitForSelector("text=pending-clinical");
const aid = await page.locator("article").innerText();
if (!/NOT MEDICAL ADVICE/.test(aid)) {
  throw new Error("first-aid page missing the notice");
}

console.log("offline ok: cattail look-alikes and bleeding page both rendered from cache");
await browser.close();
