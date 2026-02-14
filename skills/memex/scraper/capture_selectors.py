#!/usr/bin/env python3
"""
Interactive browser session to capture Plaud.AI selectors.
Run this script, log in via Google, then follow the prompts.
"""

from playwright.sync_api import sync_playwright
import json
from pathlib import Path

def main():
    print("=" * 50)
    print("  Plaud.AI Selector Capture Tool")
    print("=" * 50)
    print()

    with sync_playwright() as p:
        # Launch browser (NOT headless so user can interact)
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Navigate to Plaud.AI
        print("Opening Plaud.AI...")
        page.goto("https://web.plaud.ai/")

        print()
        print("=" * 50)
        print("STEP 1: Please log in with Google")
        print("=" * 50)
        print()
        input("Press ENTER after you've logged in and can see your recordings...")

        # Capture current URL
        current_url = page.url
        print(f"\nLogged in! Current URL: {current_url}")

        # Save cookies for future sessions
        cookies = context.cookies()
        cookies_path = Path(__file__).parent / "plaud_cookies.json"
        with open(cookies_path, "w") as f:
            json.dump(cookies, f, indent=2)
        print(f"Cookies saved to: {cookies_path}")

        print()
        print("=" * 50)
        print("STEP 2: Capturing recordings list structure")
        print("=" * 50)
        print()

        # Get page HTML for analysis
        html_content = page.content()
        html_path = Path(__file__).parent / "plaud_recordings_page.html"
        with open(html_path, "w") as f:
            f.write(html_content)
        print(f"Page HTML saved to: {html_path}")

        # Try to find common patterns
        print("\nLooking for recording elements...")

        # Common selectors to try
        selectors_to_try = [
            "[class*='recording']",
            "[class*='item']",
            "[class*='list'] > div",
            "[class*='card']",
            "[data-testid]",
            "article",
            ".MuiCard-root",
            ".ant-list-item",
        ]

        found_selectors = {}
        for selector in selectors_to_try:
            try:
                elements = page.query_selector_all(selector)
                if elements and len(elements) > 0:
                    found_selectors[selector] = len(elements)
                    print(f"  Found {len(elements)} elements matching: {selector}")
            except:
                pass

        print()
        print("=" * 50)
        print("STEP 3: Click on a recording to view transcript")
        print("=" * 50)
        print()
        input("Click on any recording, then press ENTER when viewing the transcript...")

        # Capture transcript page
        transcript_url = page.url
        print(f"\nTranscript URL: {transcript_url}")

        transcript_html = page.content()
        transcript_path = Path(__file__).parent / "plaud_transcript_page.html"
        with open(transcript_path, "w") as f:
            f.write(transcript_html)
        print(f"Transcript HTML saved to: {transcript_path}")

        # Look for transcript content
        print("\nLooking for transcript text elements...")
        transcript_selectors = [
            "[class*='transcript']",
            "[class*='text']",
            "[class*='content']",
            "[class*='speaker']",
            "[class*='segment']",
            "p",
            ".MuiTypography-root",
        ]

        for selector in transcript_selectors:
            try:
                elements = page.query_selector_all(selector)
                if elements and len(elements) > 0:
                    # Get first element's text as sample
                    sample = elements[0].inner_text()[:100] if elements else ""
                    print(f"  {selector}: {len(elements)} elements")
                    if sample:
                        print(f"    Sample: {sample[:50]}...")
            except:
                pass

        print()
        print("=" * 50)
        print("STEP 4: Look for export/download button")
        print("=" * 50)
        print()

        # Look for buttons
        buttons = page.query_selector_all("button")
        print(f"Found {len(buttons)} buttons on page:")
        for i, btn in enumerate(buttons[:10]):  # First 10
            text = btn.inner_text()
            if text:
                print(f"  {i+1}. {text}")

        print()
        input("Press ENTER to close browser and generate report...")

        # Generate summary report
        report = {
            "login_url": "https://web.plaud.ai/",
            "recordings_url": current_url,
            "transcript_url": transcript_url,
            "cookies_file": str(cookies_path),
            "found_selectors": found_selectors,
        }

        report_path = Path(__file__).parent / "plaud_selectors_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print()
        print("=" * 50)
        print("  CAPTURE COMPLETE!")
        print("=" * 50)
        print()
        print("Files saved:")
        print(f"  - {cookies_path}")
        print(f"  - {html_path}")
        print(f"  - {transcript_path}")
        print(f"  - {report_path}")
        print()
        print("Next: I'll analyze these files to build the scraper.")

        browser.close()

if __name__ == "__main__":
    main()
