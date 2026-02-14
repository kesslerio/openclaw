# Contact Analysis Scripts - Quick Guide

All three Python contact analysis scripts have been tested and fixed. They are now fully operational on macOS.

## Scripts Overview

### 1. parse-contacts.py

**Purpose**: Parse Google Contacts CSV and build contact management database

**Usage**:

```bash
python3 scripts/parse-contacts.py [path-to-contacts.csv]
```

**What it does**:

- Parses Google Contacts CSV export
- Extracts names, emails, phones, organizations
- Auto-categorizes contacts (business, personal, team)
- Creates `contacts.json` database
- Generates summary statistics

**Output files**:

- `data/contacts/contacts.json` - Full contact database
- `data/contacts/summary.json` - Summary statistics

**Example**:

```bash
python3 scripts/parse-contacts.py ~/Downloads/contacts.csv
```

---

### 2. analyze-contact-frequency.py

**Purpose**: Analyze email history to determine contact frequency and categorize contacts

**Usage**:

```bash
python3 scripts/analyze-contact-frequency.py
```

**What it does**:

- Fetches email history from Himalaya (if installed)
- Analyzes contact frequency (hot/warm/cold/dormant)
- Updates contact database with frequency data
- Generates detailed report with top contacts
- Auto-categorizes by email domain

**Frequency categories**:

- **Hot** (🔥): 10+ emails in 90 days
- **Warm** (🌡️): 3-9 emails in 90 days
- **Cold** (❄️): 1-2 emails in 90 days
- **Dormant** (💀): 0 emails in 90 days

**Output files**:

- `data/contacts/contacts.json` - Updated with frequency data
- `data/contacts/report.json` - Analysis report

**Note**: Works without Himalaya, but email analysis will be skipped. Install Himalaya for full functionality:

```bash
cargo install himalaya
```

---

### 3. reach-out-recommendations.py

**Purpose**: Generate daily reach-out recommendations based on contact frequency

**Usage**:

```bash
python3 scripts/reach-out-recommendations.py
```

**What it does**:

- Analyzes contact database
- Prioritizes warm business contacts
- Recommends 5 contacts to reach out to daily
- Provides suggested actions
- Saves recommendations with timestamp

**Priority system**:

1. Warm business contacts (maintain relationship)
2. Cold/dormant business contacts (re-engage)
3. Personal contacts (stay in touch)

**Output files**:

- `data/contacts/daily-recommendations.json` - Today's recommendations

**Example output**:

```
🎯 DAILY REACH-OUT RECOMMENDATIONS
==================================================

1. John Doe
   Category: business | Frequency: warm
   📱 555-1234
   📧 john@example.com
   🏢 Acme Corp
   💡 Follow up on business opportunity
```

---

## Workflow

### Initial Setup

1. Export contacts from Google Contacts as CSV
2. Parse the CSV file:
   ```bash
   python3 scripts/parse-contacts.py ~/Downloads/contacts.csv
   ```

### Daily Use

1. Analyze contact frequency:

   ```bash
   python3 scripts/analyze-contact-frequency.py
   ```

2. Get daily recommendations:

   ```bash
   python3 scripts/reach-out-recommendations.py
   ```

3. Review recommendations in terminal or view JSON:
   ```bash
   cat data/contacts/daily-recommendations.json
   ```

---

## Data Structure

### contacts.json

```json
{
  "name": "John Doe",
  "first_name": "John",
  "last_name": "Doe",
  "organization": "Acme Corp",
  "title": "CEO",
  "email": "john@acme.com",
  "phones": [{ "number": "555-1234", "label": "Mobile" }],
  "labels": ["business", "client"],
  "category": "business",
  "frequency": "warm",
  "last_contacted": "2026-01-15",
  "contact_count_90d": 5,
  "notes": null
}
```

---

## Troubleshooting

### CSV not found

```bash
# Script will search these locations in order:
# 1. ~/.clawdbot/media/inbound/
# 2. ~/Cursor/Claude-2026/openclaw/tools/copper-scripts/data/contacts/
# 3. Current directory

# Or specify path directly:
python3 scripts/parse-contacts.py /path/to/contacts.csv
```

### Himalaya not found

- Email analysis will be skipped
- Scripts still work with existing contact data
- Install Himalaya for full functionality: `cargo install himalaya`

### Permission errors

```bash
chmod +x scripts/parse-contacts.py
chmod +x scripts/analyze-contact-frequency.py
chmod +x scripts/reach-out-recommendations.py
```

---

## Fixes Applied

All scripts were updated to:

1. Use dynamic path detection (no hard-coded `/home/ubuntu/` paths)
2. Work on macOS and Linux
3. Gracefully handle missing dependencies (Himalaya)
4. Provide clear error messages
5. Support command-line arguments
6. Auto-detect CSV files

---

## Testing Results

All three scripts tested and verified working:

- ✓ parse-contacts.py: Parses CSV and creates database
- ✓ analyze-contact-frequency.py: Analyzes contacts (gracefully skips email if Himalaya not installed)
- ✓ reach-out-recommendations.py: Generates daily recommendations

**Test date**: 2026-02-01
**Platform**: macOS (Darwin 25.2.0)
**Status**: All tests passed
