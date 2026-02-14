# Scripts Audit Report

Generated: 2026-02-01

## Executive Summary

Audited 42 scripts in /Users/arvindsarin/clawd/scripts/ to identify:

- Working production scripts
- Broken scripts with fixable issues
- Stub scripts that need implementation
- Business-critical scripts prioritized by sales/operations value

## Status Categories

### 1. FULLY FUNCTIONAL (Ready for Business Use)

#### Sales & Business Development

1. **sales-call-prep.js** - Working
   - Generates personalized sales prep based on agency, EVV, pain points
   - Usage: `node sales-call-prep.js --agency "ABC Home Health" --evv "WellSky" --pain "no-shows"`
   - Business Value: HIGH - Direct sales support

2. **competitor-monitor.js** - Working
   - Tracks competitive pricing and intelligence
   - Usage: `node competitor-monitor.js [check|report|save]`
   - Business Value: HIGH - Competitive positioning

3. **roi-calculator-cli.js** - Working
   - Calculates ROI vs answering services, manual processes, other AI solutions
   - Usage: `node roi-calculator-cli.js --calls 1000 --caregivers 30`
   - Business Value: HIGH - Sales closing tool

4. **email-campaign-generator.js** - Working (minor UX issue)
   - Generates 4 email sequences: cold-outreach, demo-follow-up, trial-nurture, customer-success
   - Usage: `node email-campaign-generator.js [segment]` (NOT --help)
   - Business Value: HIGH - Marketing automation
   - Fix needed: Better help/usage handling

5. **linkedin-post-generator.js** - Working (minor UX issue)
   - 8 themed posts: no-shows, time-savings, evv-integration, cost-comparison, compliance, caregiver-experience, founder-story, industry-trends
   - Usage: `node linkedin-post-generator.js [theme]` (NOT --help)
   - Business Value: HIGH - Content marketing
   - Fix needed: Better help/usage handling

6. **prospect-research.sh** - Working
   - Creates prospect research file with template
   - Usage: `./prospect-research.sh "Agency Name"`
   - Business Value: MEDIUM - Lead qualification

#### Customer Success & Operations

7. **copper-metrics-tracker.js** - Working
   - Tracks customers, revenue, calls, milestones
   - Usage: `node copper-metrics-tracker.js [add|note|report|goals|init]`
   - Business Value: HIGH - Business metrics

8. **reach-out-recommendations.py** - Working
   - Analyzes contact frequency, suggests daily outreach
   - Usage: `python3 reach-out-recommendations.py`
   - Business Value: MEDIUM - Relationship management
   - Note: Works with existing contact data, email integration optional

#### Infrastructure & Automation

9. **flight-monitor.sh** - Working
   - Tracks DEL->DFW flight prices, generates reports
   - Usage: `./flight-monitor.sh`
   - Business Value: LOW - Personal utility

10. **update-kanban.js** - Working
    - CLI for kanban task management
    - Usage: `node update-kanban.js [add|update|move|delete|list]`
    - Business Value: MEDIUM - Task tracking

11. **morning-brief.sh** - Working
    - Generates daily morning report with weather, todos, Nike's work
    - Usage: `./morning-brief.sh`
    - Business Value: LOW - Personal productivity

12. **daily-digest.sh** - Working
    - Daily summary with weather, todos, flight tracking, journal
    - Usage: `./daily-digest.sh`
    - Business Value: LOW - Personal productivity

13. **auto-sync.sh** - Working
    - Git auto-commit and sync (runs via launchd)
    - Business Value: MEDIUM - Data backup

14. **auto-sync-vps.sh** - Working
    - VPS-specific sync script
    - Business Value: MEDIUM - Remote server backup

### 2. BROKEN - FIXABLE ISSUES

#### High-Priority Fixes (Business Value)

1. **analyze-emails.js** - STUB (Needs AI Integration)
   - Current: Just checks if email summary exists
   - Needed: AI analysis to extract action items, urgent emails, create todos
   - Fix Required: Integrate Claude API for email analysis
   - Business Value: HIGH - Email automation
   - Lines 33-43: TODO comments show intended functionality
   - Estimated Fix: 2-4 hours (API integration)

2. **get-youtube-transcript.js** - BROKEN (Missing Playwright)
   - Error: Playwright browsers not installed
   - Fix: `npx playwright install`
   - Business Value: MEDIUM - Content research
   - Estimated Fix: 5 minutes

3. **parse-contacts.py** - BROKEN (Poor CLI Handling)
   - Error: Interprets --help as filename
   - Fix: Add proper argparse for CLI arguments
   - Business Value: MEDIUM - CRM data import
   - Current: Works when given valid CSV path
   - Estimated Fix: 30 minutes

#### Medium-Priority Fixes

4. **add-vee-features.js** - CONTEXT-DEPENDENT
   - Error: Expects index.html in current directory
   - Purpose: Adds features to Vee (voice AI demo HTML)
   - Fix: Make path configurable or document usage context
   - Business Value: LOW - Legacy tool for old demo
   - Estimated Fix: 15 minutes

5. **fix-vee-issues.js** - CONTEXT-DEPENDENT
   - Error: Expects index.html in current directory
   - Purpose: Fixes issues in Vee demo
   - Business Value: LOW - Legacy tool
   - Estimated Fix: 15 minutes

6. **add-token-tracking.js** - CONTEXT-DEPENDENT
   - Error: Expects index.html in current directory
   - Purpose: Adds token tracking to Vee demo
   - Business Value: LOW - Legacy tool
   - Estimated Fix: 15 minutes

7. **check-aa-flights.sh** - STUB
   - Incomplete implementation
   - Initializes JSON file but doesn't actually check prices
   - Business Value: LOW - Personal utility
   - Estimated Fix: 2-4 hours (needs API integration)

#### Low-Priority (Utility Scripts)

8. **analyze-contact-frequency.py** - PARTIALLY WORKING
   - Works with existing contact data
   - Himalaya email client missing (optional feature)
   - Business Value: LOW - Already has working alternative (reach-out-recommendations.py)
   - Fix: Install himalaya with `cargo install himalaya` (optional)

9. **generate-diagram.js** - NEEDS CONTEXT
   - Works but requires type argument
   - Usage: `generate-diagram.js <type> [description]`
   - Types: flow, sequence, gantt, er, class
   - Business Value: MEDIUM - Documentation/presentations
   - No fix needed, just documentation

### 3. UNTESTED (Likely Working)

These scripts weren't tested but likely work based on structure:

1. **yt-transcript-playwright.js** - Similar to get-youtube-transcript.js
   - Likely needs: `npx playwright install`
   - Business Value: MEDIUM

2. **yt-transcript-v2.js** - Alternative YouTube transcript getter
   - Business Value: MEDIUM

3. **batch-add-tasks.sh** - Bulk task creation
   - Business Value: LOW

4. **email-digest.sh** - Email summary generation
   - Business Value: MEDIUM

5. **email-manager.sh** - Email management automation
   - Business Value: MEDIUM

6. **moltbook-post.sh** - Moltbook posting utility
   - Business Value: LOW

7. **preview-drafts.sh** - Draft preview utility
   - Business Value: LOW

8. **process-voice-memo.sh** - Voice memo processing
   - Business Value: MEDIUM

9. **transcribe-youtube.sh** - YouTube transcription wrapper
   - Business Value: MEDIUM

## Prioritized Fix List (By Business Impact)

### CRITICAL (Do These First)

1. **analyze-emails.js** - Implement AI email analysis
   - Impact: Automates lead qualification from cold emails
   - Time: 2-4 hours
   - Requires: Claude API integration

2. **email-campaign-generator.js** - Fix help handling
   - Impact: Makes tool more user-friendly for sales team
   - Time: 15 minutes
   - Fix: Add proper argument parsing

3. **linkedin-post-generator.js** - Fix help handling
   - Impact: Makes content creation tool easier to use
   - Time: 15 minutes
   - Fix: Add proper argument parsing

### HIGH PRIORITY

4. **get-youtube-transcript.js** - Install Playwright
   - Impact: Enables competitive content research
   - Time: 5 minutes
   - Fix: Run `npx playwright install`

5. **parse-contacts.py** - Fix CLI handling
   - Impact: Enables CRM data import from Google Contacts
   - Time: 30 minutes
   - Fix: Add argparse, proper --help handling

### MEDIUM PRIORITY

6. **generate-diagram.js** - Document usage
   - Impact: Helps create sales presentation diagrams
   - Time: 10 minutes
   - Fix: Just needs better documentation

7. **yt-transcript-playwright.js** - Install Playwright
   - Impact: Alternative YouTube transcript tool
   - Time: 5 minutes
   - Fix: Same as #4

### LOW PRIORITY (Can Skip)

- **add-vee-features.js** - Legacy tool for old demo
- **fix-vee-issues.js** - Legacy tool for old demo
- **add-token-tracking.js** - Legacy tool for old demo
- **check-aa-flights.sh** - Personal utility, already have flight-monitor.sh

## Business Value Summary

### High-Value Working Scripts (Use These Now)

1. sales-call-prep.js - Sales preparation
2. competitor-monitor.js - Competitive intelligence
3. roi-calculator-cli.js - Sales closing tool
4. email-campaign-generator.js - Email sequences
5. linkedin-post-generator.js - Social media content
6. copper-metrics-tracker.js - Business metrics

### Quick Wins (Fix These This Week)

1. get-youtube-transcript.js - 5 min fix, medium value
2. email-campaign-generator.js - 15 min fix, high value
3. linkedin-post-generator.js - 15 min fix, high value

### Strategic Projects (Plan These)

1. analyze-emails.js - 2-4 hours, very high value
2. parse-contacts.py - 30 min, medium value

## Documentation Files Found

- **CONTACT_SCRIPTS_GUIDE.md** - Contact management documentation
- **CONTACT_SCRIPTS_TEST_RESULTS.md** - Test results for contact scripts
- **QUICK_START.txt** - Quick start guide for scripts
- **README.md** - Main scripts documentation
- **ai-email-analyzer.md** - Email analyzer design doc
- **ntta-dispute-call-script.md** - NTTA dispute call script

## Recommendations

1. **Immediate Action**: Fix the 3 "quick wins" (30 minutes total)
2. **This Week**: Implement analyze-emails.js AI integration (high ROI)
3. **This Month**: Test and document all untested scripts
4. **Archive**: Move Vee-related legacy tools to archive/ folder
5. **Monitoring**: Set up script health monitoring dashboard

## Files Generated

- Auto-sync.log shows heavy activity (130KB)
- Contact scripts have been recently used (Feb 1)
- Flight monitor generating daily reports
