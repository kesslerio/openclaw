#!/usr/bin/env python3
"""
Cookie Refresh Helper for Plaud.AI

Since web.plaud.ai uses Google OAuth, we can't fully automate login
from a headless SSH session. This script provides multiple strategies
to get fresh cookies.

Strategy 1: Extract from running Safari/Chrome on this Mac
Strategy 2: Launch non-headless browser (requires Mac desktop access)
Strategy 3: Import from exported cookie JSON file
"""

import json
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

COOKIES_PATH = Path(__file__).parent / "plaud_cookies.json"


def strategy_1_safari() -> Optional[List[Dict]]:
    """
    Extract Plaud cookies from Safari's cookie store.

    Safari stores cookies in a binary cookie file at:
    ~/Library/Cookies/Cookies.binarycookies

    However, this requires special parsing. Instead, we use
    the sqlite-based approach for Chrome.
    """
    print("Strategy 1: Extracting from Safari...")
    print("  Safari binary cookies are hard to parse.")
    print("  Trying Chrome instead...")
    return None


def strategy_2_chrome() -> Optional[List[Dict]]:
    """
    Extract Plaud cookies from Chrome's cookie database.

    Chrome stores cookies in an SQLite database at:
    ~/Library/Application Support/Google/Chrome/Default/Cookies

    Note: Chrome encrypts cookie values on macOS using the Keychain.
    We can read cookie names/domains but values need decryption.
    """
    print("Strategy 2: Extracting from Chrome...")

    chrome_cookie_paths = [
        Path.home() / "Library/Application Support/Google/Chrome/Default/Cookies",
        Path.home() / "Library/Application Support/Google/Chrome/Profile 1/Cookies",
    ]

    for cookie_path in chrome_cookie_paths:
        if not cookie_path.exists():
            continue

        print(f"  Found Chrome cookies at: {cookie_path}")
        print("  NOTE: Chrome cookie values are encrypted on macOS.")
        print("  This method can find cookie NAMES but not values.")
        print("  Use Strategy 3 (Playwright export) instead.")

        try:
            # Copy to temp file to avoid locking issues
            tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
            tmp.close()
            subprocess.run(['cp', str(cookie_path), tmp.name], check=True)

            conn = sqlite3.connect(tmp.name)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name, host_key, path, expires_utc "
                "FROM cookies WHERE host_key LIKE '%plaud%'"
            )
            rows = cursor.fetchall()
            conn.close()

            Path(tmp.name).unlink()

            if rows:
                print(f"  Found {len(rows)} Plaud cookies in Chrome:")
                for name, host, path, expires in rows:
                    print(f"    {name} ({host})")
                print("\n  Values are encrypted. Use Strategy 3 to get full cookies.")
            else:
                print("  No Plaud cookies found in Chrome.")

        except Exception as e:
            print(f"  Failed to read Chrome cookies: {e}")

    return None


def strategy_3_playwright_export():
    """
    Launch a browser via Playwright so the user can log in.

    This requires display access (Mac desktop or VNC).
    """
    print("Strategy 3: Playwright browser login...")
    print()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  Playwright not installed. Install with:")
        print("  pip install playwright && playwright install chromium")
        return None

    # Check if we have a display
    import os
    display = os.environ.get('DISPLAY', '')
    is_ssh = os.environ.get('SSH_TTY', '') or os.environ.get('SSH_CLIENT', '')

    if is_ssh and not display:
        print("  You're on SSH without a display.")
        print("  Options:")
        print("    a) Run this from the Mac's desktop/terminal")
        print("    b) Set up VNC: 'sudo /System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart -activate -configure -access -on -restart -agent -privs -all'")
        print("    c) Use Strategy 4 (manual cookie paste)")
        print()
        return None

    print("  Launching browser - please log in to Plaud.AI...")
    print("  After logging in, the script will save cookies automatically.")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://web.plaud.ai/")

        input("  Press ENTER after you've logged in and see your recordings...")

        if "/login" in page.url:
            print("  Still on login page. Try again.")
            browser.close()
            return None

        cookies = context.cookies()
        save_cookies(cookies)

        print(f"  Saved {len(cookies)} cookies to {COOKIES_PATH}")
        browser.close()
        return cookies


def strategy_4_manual_paste():
    """
    User manually exports cookies from browser DevTools.

    Instructions:
    1. Open web.plaud.ai in browser
    2. Log in
    3. Open DevTools (F12)
    4. Go to Console tab
    5. Paste the cookie extraction script
    6. Copy the output and paste it here
    """
    print("Strategy 4: Manual cookie paste")
    print()
    print("Instructions:")
    print("  1. Open https://web.plaud.ai in your browser")
    print("  2. Log in with Google")
    print("  3. Open DevTools (Cmd+Option+I / F12)")
    print("  4. Go to the Console tab")
    print("  5. Paste this script and press Enter:")
    print()
    print('  copy(JSON.stringify(document.cookie.split("; ").map(c => {')
    print('    const [name, ...rest] = c.split("=");')
    print('    return {name, value: rest.join("="), domain: "web.plaud.ai", path: "/"};')
    print('  }), null, 2))')
    print()
    print("  6. The cookies are now in your clipboard")
    print("  7. Paste them below (then press Enter twice):")
    print()

    lines = []
    while True:
        try:
            line = input()
            if line:
                lines.append(line)
            else:
                if lines:
                    break
        except EOFError:
            break

    if not lines:
        print("  No input received.")
        return None

    try:
        text = '\n'.join(lines)
        cookies = json.loads(text)
        save_cookies(cookies)
        print(f"  Saved {len(cookies)} cookies to {COOKIES_PATH}")
        return cookies
    except json.JSONDecodeError as e:
        print(f"  Failed to parse cookie JSON: {e}")
        return None


def strategy_5_applescript():
    """
    Use AppleScript to extract cookies from Safari.

    This can work over SSH since it uses the macOS scripting bridge.
    """
    print("Strategy 5: AppleScript Safari cookie extraction...")
    print()

    # Check if Safari has a Plaud session
    script = '''
    tell application "Safari"
        set tabList to {}
        repeat with w in windows
            repeat with t in tabs of w
                if URL of t contains "plaud.ai" then
                    set end of tabList to URL of t
                end if
            end repeat
        end repeat
        return tabList
    end tell
    '''

    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and 'plaud.ai' in result.stdout:
            print(f"  Found Plaud tab in Safari: {result.stdout.strip()}")
            print("  Safari doesn't expose cookies via AppleScript.")
            print("  Use Strategy 4 (manual paste from DevTools).")
        else:
            print("  No Plaud.ai tabs found in Safari.")
    except Exception as e:
        print(f"  AppleScript failed: {e}")

    return None


def save_cookies(cookies: List[Dict]):
    """Save cookies to the standard location."""
    with open(COOKIES_PATH, 'w') as f:
        json.dump(cookies, f, indent=2)


def check_existing_cookies() -> bool:
    """Check if existing cookies are likely still valid."""
    if not COOKIES_PATH.exists():
        print("No saved cookies found.")
        return False

    with open(COOKIES_PATH, 'r') as f:
        cookies = json.load(f)

    plaud_cookies = [c for c in cookies if 'plaud.ai' in c.get('domain', '')]
    print(f"Found {len(plaud_cookies)} Plaud cookies in saved file")

    # Check expiry
    now = datetime.now().timestamp()
    expired = 0
    for c in plaud_cookies:
        exp = c.get('expires', 0)
        if exp > 0 and exp < now:
            expired += 1

    if expired > 0:
        print(f"  {expired}/{len(plaud_cookies)} cookies are expired")
        return False

    # Check age of cookie file
    file_age = datetime.now() - datetime.fromtimestamp(COOKIES_PATH.stat().st_mtime)
    print(f"  Cookie file age: {file_age.days} days, {file_age.seconds // 3600} hours")

    if file_age.days > 1:
        print("  Cookies are likely expired (> 1 day old)")
        return False

    print("  Cookies appear fresh")
    return True


def main():
    print("=" * 60)
    print("  Plaud.AI Cookie Refresh Tool")
    print("=" * 60)
    print()

    # Check existing
    has_valid = check_existing_cookies()
    print()

    if has_valid:
        answer = input("Cookies appear valid. Refresh anyway? [y/N]: ").strip().lower()
        if answer != 'y':
            print("Keeping existing cookies.")
            return

    print("Available strategies:")
    print("  3) Launch browser (requires Mac desktop)")
    print("  4) Manual paste from DevTools (works over SSH)")
    print("  5) Check Safari tabs via AppleScript")
    print()

    choice = input("Choose strategy [4]: ").strip() or "4"

    if choice == "3":
        strategy_3_playwright_export()
    elif choice == "4":
        strategy_4_manual_paste()
    elif choice == "5":
        strategy_5_applescript()
    else:
        print(f"Unknown strategy: {choice}")


if __name__ == "__main__":
    main()
