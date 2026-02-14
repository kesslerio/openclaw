# Quick Fixes for Broken Scripts

Priority fixes that can be done in under 30 minutes

## 1. Fix get-youtube-transcript.js (5 minutes)

**Issue**: Missing Playwright browsers

**Fix**:

```bash
cd ~/Cursor/Claude-2026/openclaw/tools/copper-scripts
npx playwright install
```

**Test**:

```bash
node get-youtube-transcript.js "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## 2. Fix email-campaign-generator.js (15 minutes)

**Issue**: --help flag not handled, shows error instead of help

**Current Behavior**:

```bash
node email-campaign-generator.js --help
# Error: Segment '--help' not found
```

**Fix**: Edit lines 398-413 in email-campaign-generator.js

Replace:

```javascript
// CLI
const args = process.argv.slice(2);
const segment = args[0];
const flag = args[1];

if (!segment || segment === "all") {
  generateAll();
} else if (flag === "--list") {
  const campaign = segments[segment];
  console.log(`${campaign.name} - ${campaign.emails.length} emails`);
  campaign.emails.forEach((email, i) => {
    console.log(`  ${i + 1}. Day ${email.day}: ${email.subject}`);
  });
} else {
  generateSequence(segment);
}
```

With:

```javascript
// CLI
const args = process.argv.slice(2);
const segment = args[0];
const flag = args[1];

// Handle help
if (!segment || segment === "--help" || segment === "-h" || segment === "help") {
  console.log("Usage: node email-campaign-generator.js [segment] [--list]");
  console.log("\nSegments:");
  Object.keys(segments).forEach((s) => {
    console.log(`  - ${s}: ${segments[s].name}`);
  });
  console.log("\nExamples:");
  console.log("  node email-campaign-generator.js cold-outreach");
  console.log("  node email-campaign-generator.js demo-follow-up --list");
  console.log("  node email-campaign-generator.js all");
  process.exit(0);
}

if (segment === "all") {
  generateAll();
} else if (flag === "--list") {
  const campaign = segments[segment];
  if (!campaign) {
    console.error(`Segment '${segment}' not found.`);
    console.log("\nAvailable segments:");
    Object.keys(segments).forEach((s) => console.log(`  - ${s}`));
    process.exit(1);
  }
  console.log(`${campaign.name} - ${campaign.emails.length} emails`);
  campaign.emails.forEach((email, i) => {
    console.log(`  ${i + 1}. Day ${email.day}: ${email.subject}`);
  });
} else {
  generateSequence(segment);
}
```

**Test**:

```bash
node email-campaign-generator.js --help
node email-campaign-generator.js cold-outreach
```

## 3. Fix linkedin-post-generator.js (15 minutes)

**Issue**: Same as email-campaign-generator.js

**Fix**: Edit lines 279-289 in linkedin-post-generator.js

Replace:

```javascript
// CLI
const args = process.argv.slice(2);
const command = args[0];

if (!command || command === "all") {
  generateAll();
} else {
  console.log(generatePost(command));
  console.log();
  console.log(`Character count: ${generatePost(command).length}`);
}
```

With:

```javascript
// CLI
const args = process.argv.slice(2);
const command = args[0];

// Handle help
if (!command || command === "--help" || command === "-h" || command === "help") {
  console.log("Usage: node linkedin-post-generator.js [theme]");
  console.log("\nThemes:");
  Object.keys(themes).forEach((t) => {
    console.log(`  - ${t}`);
  });
  console.log("\nExamples:");
  console.log("  node linkedin-post-generator.js no-shows");
  console.log("  node linkedin-post-generator.js all");
  process.exit(0);
}

if (command === "all") {
  generateAll();
} else {
  const post = generatePost(command);
  console.log(post);
  console.log();
  console.log(`Character count: ${post.length}`);
}
```

**Test**:

```bash
node linkedin-post-generator.js --help
node linkedin-post-generator.js no-shows
```

## 4. Fix parse-contacts.py (30 minutes)

**Issue**: Doesn't handle --help, interprets it as filename

**Fix**: Replace lines 1-141 with proper argparse

Add at top (after imports):

```python
import argparse
```

Replace the bottom section (lines 135-141) with:

```python
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse Google Contacts CSV and build contact management database.'
    )
    parser.add_argument(
        'csv_path',
        nargs='?',
        default='data/contacts/contacts.csv',
        help='Path to Google Contacts CSV export (default: data/contacts/contacts.csv)'
    )
    parser.add_argument(
        '--output',
        default='data/contacts/contacts.json',
        help='Output JSON file path (default: data/contacts/contacts.json)'
    )

    args = parser.parse_args()

    csv_path = Path(args.csv_path)

    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}")
        print("\nTo export from Google Contacts:")
        print("1. Go to contacts.google.com")
        print("2. Click 'Export' in the left sidebar")
        print("3. Choose 'Google CSV' format")
        print("4. Save to data/contacts/contacts.csv")
        exit(1)

    print(f'Using CSV: {csv_path}')
    print('Parsing contacts...')
    contacts = parse_contacts(csv_path)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)

    print(f'\n✅ Parsed {len(contacts)} contacts')
    print(f'📁 Saved to: {output_path}')

    # Show summary
    orgs = len([c for c in contacts if c.get('organization')])
    with_email = len([c for c in contacts if c.get('email')])
    with_phone = len([c for c in contacts if c.get('phones')])

    print(f'\n📊 Summary:')
    print(f'   Organizations: {orgs}')
    print(f'   With email: {with_email}')
    print(f'   With phone: {with_phone}')
```

**Test**:

```bash
python3 parse-contacts.py --help
python3 parse-contacts.py path/to/contacts.csv
```

## 5. Install Playwright for YouTube Scripts (5 minutes)

**Issue**: Multiple YouTube transcript scripts need Playwright

**Fix**:

```bash
cd ~/Cursor/Claude-2026/openclaw
npx playwright install
```

**Scripts Fixed**:

- get-youtube-transcript.js
- yt-transcript-playwright.js

## Summary

Total time: ~70 minutes
Total scripts fixed: 5
Business value: HIGH

After these fixes, you'll have:

- Working YouTube research tools
- Better UX for email campaign generator
- Better UX for LinkedIn post generator
- Working contact import from Google Contacts
- All Playwright-based tools functional

## Quick Test Suite

Run this to verify all fixes:

```bash
cd ~/Cursor/Claude-2026/openclaw/tools/copper-scripts

# Test 1: Playwright installed
npx playwright --version

# Test 2: Email campaign generator
node email-campaign-generator.js --help
node email-campaign-generator.js cold-outreach | head -20

# Test 3: LinkedIn post generator
node linkedin-post-generator.js --help
node linkedin-post-generator.js no-shows | head -20

# Test 4: Contact parser
python3 parse-contacts.py --help

# Test 5: YouTube transcript
# node get-youtube-transcript.js "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

All tests should pass without errors.
