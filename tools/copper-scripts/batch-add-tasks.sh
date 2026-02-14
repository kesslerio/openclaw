#!/bin/bash

# Batch add all tasks from history

cd /home/ubuntu/openclaw

# Personal/Financial Tasks
node scripts/update-kanban.js add --title "Copper Estate Checks" --details "Handle Copper Estate checks" --owner Arvind --category personal --status todo --urgent false
node scripts/update-kanban.js add --title "Dental Payment" --details "Make dental payment" --owner Arvind --category personal --status todo --urgent false
node scripts/update-kanban.js add --title "Send Insurance to Chase" --details "Send insurance documents to Chase" --owner Arvind --category personal --status todo --urgent false
node scripts/update-kanban.js add --title "Mails Sorting" --details "Sort through accumulated mail" --owner Arvind --category personal --status todo --urgent false
node scripts/update-kanban.js add --title "NTTA Dispute" --details "Call NTTA dispute line: 972-229-8949" --owner Arvind --category personal --status todo --urgent false

# Tax-Related
node scripts/update-kanban.js add --title "Rate.com Mortgage Docs" --details "Login to Rate.com for Myers Lane mortgage documents (1099)" --owner Arvind --category personal --status todo --urgent true
node scripts/update-kanban.js add --title "Gather All 1099s & W-2s" --details "Collect all tax documents for 2025 filing" --owner Arvind --category personal --status todo --urgent true

# Business/Admin
node scripts/update-kanban.js add --title "Canyon Drive Sale" --details "Follow up on Canyon Drive property sale (December?)" --owner Arvind --category property --status todo --urgent false
node scripts/update-kanban.js add --title "Salary to Vivia" --details "Process salary payment to Vivia" --owner Arvind --category personal --status todo --urgent false
node scripts/update-kanban.js add --title "Finance & Salary Review" --details "Review finance and salary situation" --owner Arvind --category personal --status todo --urgent false
node scripts/update-kanban.js add --title "Harvard Business Review Call" --details "Call HBR - see memory/hbr-call-brief.md for details" --owner Arvind --category personal --status todo --urgent false
node scripts/update-kanban.js add --title "SHC Advantages - Inn" --details "Follow up on SHC Advantages Inn matter" --owner Arvind --category personal --status todo --urgent false
node scripts/update-kanban.js add --title "Crane St - Jine" --details "Follow up on Crane Street with Jine" --owner Arvind --category property --status todo --urgent false

# Copper AI / Business Development
node scripts/update-kanban.js add --title "Rivvi Partnership - LinkedIn Connect" --details "Connect with Nathan Hayman on LinkedIn, schedule follow-up demo. Rivvi = B2B voice AI, 50-60k calls/mo" --owner Arvind --category copper --status todo --urgent false
node scripts/update-kanban.js add --title "Darwin Vinolas - Friday Meeting" --details "Meeting Friday to finalize partnership & investment. Give Arbitrinity access. Review iCare SOCs" --owner Arvind --category copper --status todo --urgent true
node scripts/update-kanban.js add --title "Colorado Prospect Follow-up" --details "Filipino-owned agency, $4k/mo current spend, target $2k/mo. Post-demo follow-up if demo went well" --owner Arvind --category copper --status todo --urgent false

# Kenneth-Related
node scripts/update-kanban.js add --title "Kenneth - Legal App" --details "Create legal app for Kenneth. Define scope, timeline, deliverables" --owner Arvind --category personal --status todo --urgent false
node scripts/update-kanban.js add --title "Kenneth - Highline Money" --details "Get commitment/payment from Kenneth for Highline money owed" --owner Arvind --category personal --status todo --urgent false
node scripts/update-kanban.js add --title "Kenneth - Collections Discussion" --details "Discuss collections from other people. Who owes what?" --owner Arvind --category personal --status todo --urgent false
node scripts/update-kanban.js add --title "Kwon Payment" --details "Determine amount and timing for payment to Kwon" --owner Arvind --category personal --status todo --urgent false

# Nike Tasks
node scripts/update-kanban.js add --title "Browser Extension Setup" --details "Set up browser extension for Google Drive access" --owner Nike --category nike --status todo --urgent false
node scripts/update-kanban.js add --title "Copper AI Telegram Bot" --details "Set up Copper AI Telegram bot when ready" --owner Nike --category nike --status todo --urgent false

echo "✅ All tasks added!"
