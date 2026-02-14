#!/bin/bash
# Auto-sync script for openclaw workspace (VPS version)
# Watches for file changes and auto-commits/pushes to GitHub

WORKSPACE="/home/ubuntu/openclaw"
LOGFILE="$WORKSPACE/tools/copper-scripts/auto-sync-vps.log"
LOCKFILE="/tmp/openclaw-sync.lock"

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

    # SECURITY CHECK: Verify repository is private before syncing
    REPO_URL=$(git config --get remote.origin.url)
    if [[ "$REPO_URL" =~ github\.com[:/]([^/]+)/([^/.]+) ]]; then
        REPO_OWNER="${BASH_REMATCH[1]}"
        REPO_NAME="${BASH_REMATCH[2]}"
        REPO_FULL="$REPO_OWNER/$REPO_NAME"
        
        VISIBILITY=$(gh repo view "$REPO_FULL" --json visibility -q .visibility 2>/dev/null)
        if [ "$VISIBILITY" != "PRIVATE" ]; then
            log "⚠️  WARNING: Repository '$REPO_FULL' is $VISIBILITY, not PRIVATE"
            log "⚠️  This workspace contains sensitive data that should not be public"
            log "⚠️  Skipping sync for security reasons"
            log "⚠️  Run: gh repo edit $REPO_FULL --visibility private --accept-visibility-change-consequences"
            rm -f "$LOCKFILE"
            return
        fi
        log "✓ Repository verified as PRIVATE"
    fi

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
    COMMIT_MSG="Auto-sync from VPS at $(date '+%Y-%m-%d %H:%M:%S')"
    git commit -m "$COMMIT_MSG" 2>&1 | tee -a "$LOGFILE"

    # Push
    log "Pushing changes..."
    git push origin master 2>&1 | tee -a "$LOGFILE"

    log "Sync complete"
    rm -f "$LOCKFILE"
}

log "Starting auto-sync watcher for $WORKSPACE"
log "Press Ctrl+C to stop"

# Initial sync
sync_changes

# Watch for changes with inotifywait (5 second debounce)
while true; do
    inotifywait -r -q -e modify,create,delete,move         --exclude '\.git|\.log$|\.swp$'         "$WORKSPACE" --timeout 5 && {
        log "Change detected, waiting 5s for more changes..."
        sleep 5
        sync_changes
    }
done
