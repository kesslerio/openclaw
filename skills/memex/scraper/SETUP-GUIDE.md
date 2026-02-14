# 🚀 Plaud Scraper Setup & Testing Guide

**For:** Arvind  
**Purpose:** Get actual HTML selectors from Plaud.AI so Nike can complete the scraper  
**Time Required:** 15-20 minutes

---

## 🎯 What We Need

The scraper code is 90% complete, but needs **actual HTML selectors** from the Plaud.AI website.

Nike can't access your Plaud account, so **you** need to:

1. Log into Plaud.AI
2. Open browser DevTools
3. Find the HTML elements (Nike will explain how)
4. Copy selectors into a file
5. Nike will update the scraper with real selectors

---

## 📋 Step-by-Step Instructions

### Step 1: Open Plaud.AI in Chrome

1. Go to https://web.plaud.ai
2. Log in with your credentials
3. Navigate to your recordings/dashboard page

### Step 2: Open DevTools

**Mac:**

- Press `Cmd + Option + I`
- Or: Right-click → "Inspect"

**You should see:** A panel with HTML code on the right side of the browser

### Step 3: Find Recording Cards

1. In DevTools, click the **"Select Element" tool** (top-left of DevTools, looks like a cursor icon)
2. Hover over a recording in your dashboard
3. Click on it
4. DevTools will highlight the HTML element

**Take a screenshot** of the highlighted HTML

### Step 4: Copy Selectors

We need selectors for these elements:

#### A. Recording Card Container

**What it is:** The div/element that wraps each recording  
**Look for:** A `<div>` with class names like:

- `.recording-card`
- `.recording-item`
- `.note-card`
- `[data-recording-id]`

**Copy:**

```
Recording card selector: ___________________
```

#### B. Title Element

**What it is:** The text showing the recording's name  
**Look for:** Text like "Team Standup" or "Client Call"

**Copy:**

```
Title selector: ___________________
```

#### C. Date Element

**What it is:** Shows when the recording was made  
**Look for:** Text like "Feb 1, 2026" or "2 hours ago"

**Copy:**

```
Date selector: ___________________
```

#### D. Export/Download Button

**What it is:** Button to export the transcript  
**Look for:** Button with text "Export" or "Download" or a download icon

**Copy:**

```
Export button selector: ___________________
```

#### E. Recording ID (if visible)

**Look for:** Attribute like `data-id` or `data-recording-id` on the recording card

**Copy:**

```
ID attribute: ___________________
```

### Step 5: Check Pagination/Infinite Scroll

1. Scroll to the bottom of your recordings list
2. Do new recordings load automatically? (Infinite scroll)
3. Or is there a "Load More" button?
4. Or page numbers (1, 2, 3...)?

**Answer:**

```
Pagination type: ___________________
```

### Step 6: Test Export Flow

1. Click the export button on ONE recording
2. What happens?
   - Downloads immediately?
   - Opens a modal/popup?
   - Opens a new tab?

**Answer:**

```
Export behavior: ___________________
```

3. If there's a modal, what are the export options?
   - Text file?
   - PDF?
   - Audio?
   - Multiple formats?

**Answer:**

```
Export formats available: ___________________
```

### Step 7: Create Selector File

Create a file: `~/clawd/memex/scraper/plaud-selectors.json`

```json
{
  "recording_card": ".recording-card",
  "title": ".title",
  "date": ".date",
  "duration": ".duration",
  "export_button": "button[aria-label='Export']",
  "recording_id_attribute": "data-id",
  "login": {
    "email_input": "input[type='email']",
    "password_input": "input[type='password']",
    "submit_button": "button[type='submit']",
    "success_url": "/dashboard"
  },
  "pagination": {
    "type": "infinite_scroll",
    "load_more_button": null
  },
  "export": {
    "behavior": "download",
    "modal_selector": null,
    "format_options": ["txt", "pdf"]
  }
}
```

**Fill in the actual values from Steps 3-6 above!**

---

## 🎯 Alternative: Use Developer API (If Available)

### Check for API Access

1. While logged into web.plaud.ai:
2. Go to Settings or Account
3. Look for:
   - "Developer"
   - "API Keys"
   - "Integrations"
   - "Export"

4. **IF YOU FIND API ACCESS:**
   - Take screenshots
   - Copy any API keys or documentation links
   - Tell Nike immediately!

**This would be 10x faster than web scraping!**

---

## 🔐 Security Notes

- **Don't share your password** with Nike (or anyone)
- **Don't commit passwords** to Git
- If you share API keys, use a secure method (Signal, encrypted file)
- We'll use `.env` file for credentials (never committed)

---

## 📤 Send Results to Nike

**Option 1: File Upload**

1. Save `plaud-selectors.json` with your findings
2. Send via Signal or WhatsApp

**Option 2: Telegram Message**
Send Nike a message with:

```
Recording card: .note-item
Title: .note-title
Date: .note-date
Export button: button.export-btn
ID attribute: data-note-id
Pagination: infinite scroll
Export: downloads .txt immediately
```

---

## ✅ What Happens Next

1. **You:** Spend 15 minutes getting selectors (this guide)
2. **Nike:** Updates scraper with real selectors (30 minutes)
3. **We test:** Run scraper on 1 file to verify (5 minutes)
4. **Success:** Run on 10 files, then 100, then all 2,500! 🎉

---

## 🆘 Need Help?

**Can't find an element?**

- Ask Nike via Telegram: "Can't find the export button"
- Share a screenshot of the page
- Nike will guide you

**DevTools confusing?**

- It's okay! Just share screenshots
- Nike can often figure it out from visual inspection

**No time right now?**

- That's fine! Do it when convenient
- But: Memex progress blocked until we have selectors

---

## 🎯 Timeline Impact

**If you do this TODAY:**

- Weekend: Nike completes scraper
- Monday: Download first 100 files
- Week 1: All 2,500 files downloaded
- Week 2: Daily journals working!

**If you do this NEXT WEEK:**

- Memex delayed by ~1 week
- (Still fine, just adjusts timeline)

---

**Let's get your data liberated! 🐾**
