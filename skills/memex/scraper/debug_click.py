#!/usr/bin/env python3
"""Debug script to understand file click behavior"""

import json
import asyncio
from playwright.async_api import async_playwright

async def main():
    print("Starting debug session...")

    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()

    # Load cookies
    with open("plaud_cookies.json") as f:
        cookies = json.load(f)
    await context.add_cookies(cookies)

    page = await context.new_page()

    # Go to main page
    await page.goto("https://web.plaud.ai")
    await page.wait_for_load_state("networkidle")

    print(f"Initial URL: {page.url}")

    # Wait for file list
    await page.wait_for_selector(".file-list-item", timeout=10000)

    # Get first file item
    items = await page.query_selector_all(".file-list-item")
    print(f"Found {len(items)} file items")

    if items:
        # Get filename before click
        filename_el = await items[0].query_selector(".file-list-item__filename")
        filename = await filename_el.inner_text() if filename_el else "Unknown"
        print(f"Clicking on: {filename}")

        # Click and wait
        await items[0].click()
        await asyncio.sleep(2)

        print(f"URL after click: {page.url}")

        # Check if transcript loaded
        transcript_items = await page.query_selector_all(".transcript-item")
        print(f"Found {len(transcript_items)} transcript items")

        # Check for file ID in URL or elsewhere
        if "/file/" in page.url:
            file_id = page.url.split("/file/")[-1].split("?")[0]
            print(f"File ID from URL: {file_id}")
        else:
            print("No file ID in URL - checking data attributes...")
            # Check for data attributes or other identifiers
            file_detail = await page.query_selector(".file-detail")
            if file_detail:
                data_id = await file_detail.get_attribute("data-file-id")
                print(f"Data file ID: {data_id}")

        # Print first transcript segment if found
        if transcript_items:
            text = await transcript_items[0].inner_text()
            print(f"First segment preview: {text[:200]}...")

    input("Press Enter to close...")
    await browser.close()
    await playwright.stop()

if __name__ == "__main__":
    asyncio.run(main())
