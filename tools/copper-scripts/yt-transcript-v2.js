#!/usr/bin/env node
const { chromium } = require("playwright");

async function getTranscript(videoUrl) {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent:
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
  });
  const page = await context.newPage();

  let captionUrl = null;

  // Intercept network requests to find caption URL
  page.on("response", async (response) => {
    const url = response.url();
    if (url.includes("timedtext") || url.includes("api/timedtext")) {
      captionUrl = url;
      console.error(`[Found caption URL in network]`);
    }
  });

  try {
    console.error("[Loading video page...]");
    await page.goto(videoUrl, { waitUntil: "networkidle", timeout: 45000 });

    // Extract caption tracks from page data
    const captionData = await page.evaluate(() => {
      // Look in ytInitialPlayerResponse
      if (window.ytInitialPlayerResponse) {
        const captions = window.ytInitialPlayerResponse.captions;
        if (captions && captions.playerCaptionsTracklistRenderer) {
          const tracks = captions.playerCaptionsTracklistRenderer.captionTracks;
          if (tracks && tracks.length > 0) {
            return tracks.map((t) => ({
              url: t.baseUrl,
              lang: t.languageCode,
              name: t.name?.simpleText,
            }));
          }
        }
      }

      // Try to find in page HTML
      const html = document.documentElement.innerHTML;
      const match = html.match(
        /"captions":\{"playerCaptionsTracklistRenderer":\{"captionTracks":\[(.*?)\]/,
      );
      if (match) {
        try {
          const tracksJson = "[" + match[1] + "]";
          const tracks = JSON.parse(tracksJson);
          return tracks.map((t) => ({
            url: t.baseUrl,
            lang: t.languageCode,
            name: t.name?.simpleText,
          }));
        } catch (e) {}
      }

      // Search in all script tags
      const scripts = document.querySelectorAll("script");
      for (const script of scripts) {
        const text = script.textContent;
        if (text.includes('"captionTracks"')) {
          const urlMatch = text.match(/"baseUrl":"(https:[^"]+timedtext[^"]+)"/g);
          if (urlMatch) {
            return urlMatch.map((m) => {
              const url = m.match(/"baseUrl":"([^"]+)"/)[1].replace(/\\u0026/g, "&");
              return { url: url, lang: "unknown" };
            });
          }
        }
      }

      return null;
    });

    if (captionData && captionData.length > 0) {
      console.error(`[Found ${captionData.length} caption track(s)]`);

      // Get the first English or any available caption
      let track = captionData.find((t) => t.lang === "en" || t.lang === "en-US") || captionData[0];
      console.error(`[Using: ${track.name || track.lang}]`);

      // Fetch the caption content
      const captionPage = await context.newPage();
      await captionPage.goto(track.url + "&fmt=json3", {
        waitUntil: "networkidle",
        timeout: 30000,
      });

      const captionContent = await captionPage.evaluate(() => document.body.textContent);

      try {
        const data = JSON.parse(captionContent);
        if (data.events) {
          const text = data.events
            .filter((e) => e.segs)
            .map((e) => e.segs.map((s) => s.utf8).join(""))
            .join(" ")
            .replace(/\n/g, " ")
            .replace(/\s+/g, " ")
            .trim();
          console.log(text);
          return;
        }
      } catch (e) {
        // Try XML format
        if (captionContent.includes("<?xml")) {
          const text = captionContent
            .replace(/<[^>]+>/g, " ")
            .replace(/&amp;/g, "&")
            .replace(/&lt;/g, "<")
            .replace(/&gt;/g, ">")
            .replace(/&#39;/g, "'")
            .replace(/&quot;/g, '"')
            .replace(/\s+/g, " ")
            .trim();
          console.log(text);
          return;
        }
      }
    }

    console.error("[No captions found in page data]");

    // Last resort: check if video info shows captions
    const videoInfo = await page.evaluate(() => {
      if (window.ytInitialPlayerResponse) {
        return {
          title: window.ytInitialPlayerResponse.videoDetails?.title,
          hasCaptions: !!window.ytInitialPlayerResponse.captions,
        };
      }
      return null;
    });

    console.error(`[Video info: ${JSON.stringify(videoInfo)}]`);
    process.exit(1);
  } catch (error) {
    console.error(`[Error: ${error.message}]`);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

const videoUrl = process.argv[2] || "https://www.youtube.com/watch?v=b-l9sGh1-UY";
getTranscript(videoUrl);
