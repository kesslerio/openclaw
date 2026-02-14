#!/usr/bin/env node
const { chromium } = require("playwright");

async function getTranscript(videoUrl) {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent:
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
  });
  const page = await context.newPage();

  try {
    console.error("[Loading video page...]");
    await page.goto(videoUrl, { waitUntil: "domcontentloaded", timeout: 30000 });
    await page.waitForTimeout(3000);

    // Accept cookies if dialog appears
    try {
      const acceptBtn = await page.$('button[aria-label*="Accept"], button:has-text("Accept all")');
      if (acceptBtn) await acceptBtn.click();
      await page.waitForTimeout(1000);
    } catch (e) {}

    // Click the "...more" button to expand description
    console.error("[Expanding description...]");
    try {
      await page.click("#expand, tp-yt-paper-button#expand", { timeout: 5000 });
      await page.waitForTimeout(1000);
    } catch (e) {
      console.error("[No expand button found]");
    }

    // Look for "Show transcript" button
    console.error("[Looking for transcript button...]");
    try {
      // Try multiple selectors
      const selectors = [
        'button[aria-label="Show transcript"]',
        'ytd-button-renderer:has-text("Show transcript")',
        'button:has-text("Show transcript")',
        '#primary-button:has-text("transcript")',
      ];

      for (const sel of selectors) {
        try {
          await page.click(sel, { timeout: 3000 });
          console.error(`[Clicked: ${sel}]`);
          break;
        } catch (e) {}
      }

      await page.waitForTimeout(2000);
    } catch (e) {
      console.error("[Could not find transcript button]");
    }

    // Extract transcript text
    console.error("[Extracting transcript...]");

    // Try to get transcript segments
    const transcript = await page.evaluate(() => {
      // Method 1: Look for transcript segments
      const segments = document.querySelectorAll("ytd-transcript-segment-renderer");
      if (segments.length > 0) {
        return Array.from(segments)
          .map((s) => {
            const textEl = s.querySelector("yt-formatted-string.segment-text");
            return textEl ? textEl.textContent.trim() : "";
          })
          .filter(Boolean)
          .join(" ");
      }

      // Method 2: Look for transcript body
      const transcriptBody = document.querySelector("ytd-transcript-body-renderer");
      if (transcriptBody) {
        return transcriptBody.textContent.replace(/\d+:\d+/g, "").trim();
      }

      // Method 3: Check for any transcript-related element
      const transcriptPanel = document.querySelector("#segments-container");
      if (transcriptPanel) {
        return transcriptPanel.textContent.replace(/\d+:\d+/g, "").trim();
      }

      return null;
    });

    if (transcript && transcript.length > 50) {
      console.log(transcript);
    } else {
      // Get page content for debugging
      const title = await page.title();
      console.error(`[Page title: ${title}]`);

      // Check if there's a transcript available in the page data
      const pageData = await page.evaluate(() => {
        const scripts = document.querySelectorAll("script");
        for (const script of scripts) {
          if (script.textContent.includes("captionTracks")) {
            const match = script.textContent.match(/"captionTracks":\[(.*?)\]/);
            if (match) return match[1];
          }
        }
        return null;
      });

      if (pageData) {
        console.error("[Found caption data in page]");
        // Extract the caption URL
        const urlMatch = pageData.match(/"baseUrl":"([^"]+)"/);
        if (urlMatch) {
          const captionUrl = urlMatch[1].replace(/\\u0026/g, "&");
          console.error(`[Caption URL: ${captionUrl}]`);

          // Fetch the captions
          const response = await page.goto(captionUrl);
          const captionXml = await response.text();

          // Parse XML and extract text
          const textContent = captionXml
            .replace(/<[^>]+>/g, " ")
            .replace(/\s+/g, " ")
            .trim();
          console.log(textContent);
        }
      } else {
        console.error("[No transcript or captions found]");
        process.exit(1);
      }
    }
  } catch (error) {
    console.error(`[Error: ${error.message}]`);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

const videoUrl = process.argv[2] || "https://www.youtube.com/watch?v=b-l9sGh1-UY";
getTranscript(videoUrl);
