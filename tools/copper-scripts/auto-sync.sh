#!/bin/bash
# Auto-sync script for openclaw workspace
# Watches for file changes and auto-commits/pushes to GitHub

WORKSPACE="/Users/arvindsarin/Cursor/Claude-2026/openclaw"
LOGFILE="$WORKSPACE/tools/copper-scripts/auto-sync.log"
LOCKFILE="/tmp/openclaw-sync.lock"

# Exclude patterns (don't trigger sync on these)
EXCLUDE_PATTERNS=(
    "*.log"
    ".git"
    "*.swp"
    "*.tmp"
    ".DS_Store"
    "auto-sync.log"
)

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOGFILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

sync_changes() {
    # Prevent concurrent syncs
    if [ -f "$LOCKFILE" ]; then
        log "Sync already in progress, skipping"
        return
    fi
    touch "$LOCKFILE"

    cd "$WORKSPACE" || exit 1

    # Pull first to avoid conflicts
    log "Pulling latest changes..."
    git pull origin master --no-edit 2>&1 | tee -a "$LOGFILE"

    # Check for local changes
    if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
        log "No local changes to sync"
        rm -f "$LOCKFILE"
        return
    fi

    # Stage all changes
    git add -A

    # Commit with timestamp
    COMMIT_MSG="Auto-sync from Mac at $(date '+%Y-%m-%d %H:%M:%S')"
    git commit -m "$COMMIT_MSG" 2>&1 | tee -a "$LOGFILE"

    # Push
    log "Pushing changes..."
    git push origin master 2>&1 | tee -a "$LOGFILE"

    log "Sync complete"
    rm -f "$LOCKFILE"
}

# Build exclude args for fswatch
EXCLUDE_ARGS=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude '$pattern'"
done

log "Starting auto-sync watcher for $WORKSPACE"
log "Press Ctrl+C to stop"

# Initial sync
sync_changes

# Watch for changes with debounce (wait 5 seconds after last change)
fswatch -o \
    --exclude '\.git' \
    --exclude '\.log$' \
    --exclude '\.swp$' \
    --exclude 'DS_Store' \
    --latency 5 \
    "$WORKSPACE" | while read -r; do
    log "Change detected, syncing..."
    sync_changes
done
