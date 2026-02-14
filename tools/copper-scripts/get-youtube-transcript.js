#!/usr/bin/env node
const { chromium } = require("playwright");

async function getYouTubeTranscript(videoUrl) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  try {
    await page.goto(videoUrl, { waitUntil: "networkidle", timeout: 30000 });

    // Wait for page to load
    await page.waitForTimeout(3000);

    // Click "More" button to expand description
    try {
      await page.click("#expand", { timeout: 5000 });
    } catch (e) {
      // Button might not exist or already expanded
    }

    // Try to click "Show transcript" button
    try {
      await page.click('button[aria-label="Show transcript"]', { timeout: 5000 });
    } catch (e) {
      // Try alternative selector
      const buttons = await page.$$("button");
      for (const btn of buttons) {
        const text = await btn.textContent();
        if (text && text.includes("transcript")) {
          await btn.click();
          break;
        }
      }
    }

    // Wait for transcript panel
    await page.waitForTimeout(2000);

    // Extract transcript text
    const transcriptSegments = await page.$$eval(
      "ytd-transcript-segment-renderer, yt-formatted-string.segment-text",
      (segments) => segments.map((s) => s.textContent?.trim()).filter(Boolean),
    );

    if (transcriptSegments.length > 0) {
      console.log(transcriptSegments.join(" "));
    } else {
      // Try alternative method - get all text from transcript panel
      const transcriptText = await page
        .$eval(
          "#segments-container, ytd-transcript-renderer",
          (el) => el?.textContent?.trim() || "",
        )
        .catch(() => "");

      if (transcriptText) {
        console.log(transcriptText);
      } else {
        console.log("No transcript found. Video may not have captions enabled.");
      }
    }
  } catch (error) {
    console.error("Error:", error.message);
  } finally {
    await browser.close();
  }
}

const videoUrl = process.argv[2] || "https://www.youtube.com/watch?v=b-l9sGh1-UY";
getYouTubeTranscript(videoUrl);
