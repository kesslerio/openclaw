#!/usr/bin/env python3
"""
Migrate existing tokens to encrypted format.

This script:
1. Loads existing unencrypted token files
2. Encrypts them using the SecureCredentialManager
3. Creates backups of original files
4. Updates permissions

Run after setting up environment variables with setup_env.sh
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.security import get_credential_manager, AuditLogger
import json
import shutil
from datetime import datetime

def migrate_tokens():
    """Migrate all existing tokens to encrypted format."""

    print("🔐 Token Migration Script")
    print("=" * 50)
    print()

    manager = get_credential_manager()
    token_dir = manager.token_dir

    if not token_dir.exists():
        print(f"❌ Token directory not found: {token_dir}")
        return

    # Find all .json token files
    token_files = list(token_dir.glob("*.json"))

    if not token_files:
        print(f"✅ No token files found in {token_dir}")
        return

    print(f"Found {len(token_files)} token files:")
    for tf in token_files:
        print(f"  - {tf.name}")
    print()

    # Create backup directory
    backup_dir = token_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(exist_ok=True, mode=0o700)

    print(f"📦 Creating backups in: {backup_dir}")
    print()

    migrated = 0
    failed = 0

    for token_file in token_files:
        try:
            # Skip keyfile and audit log
            if token_file.name in ['.keyfile', 'audit.log']:
                continue

            # Parse filename: service_account.json
            parts = token_file.stem.split('_', 1)
            if len(parts) != 2:
                print(f"⚠️  Skipping {token_file.name} (unexpected format)")
                continue

            service, account = parts

            print(f"🔄 Migrating {service}:{account}...")

            # Backup original
            backup_path = backup_dir / token_file.name
            shutil.copy2(token_file, backup_path)
            print(f"   ✅ Backed up to {backup_path.name}")

            # Read original token
            with open(token_file, 'r') as f:
                token_data = json.load(f)

            # Check if already encrypted (binary file)
            if not isinstance(token_data, dict):
                print(f"   ⚠️  Already encrypted, skipping")
                continue

            # Encrypt and save
            manager.save_token(token_data, service, account)
            print(f"   ✅ Encrypted and saved")

            migrated += 1

        except Exception as e:
            print(f"   ❌ Failed: {e}")
            failed += 1

    print()
    print("=" * 50)
    print(f"✅ Migration complete!")
    print(f"   - Migrated: {migrated}")
    print(f"   - Failed: {failed}")
    print(f"   - Backups: {backup_dir}")
    print()

    if migrated > 0:
        print("🔒 Token files are now encrypted at rest")
        print("📋 Audit log created at:", AuditLogger.audit_log_path)

    # Secure permissions
    print()
    print("🔧 Setting secure permissions...")
    for token_file in token_dir.glob("*.json"):
        token_file.chmod(0o600)

    print("✅ All done!")
    print()
    print("Next steps:")
    print("  1. Test connections: python3 memex/scripts/setup_gmail_calendar.py --test-all")
    print("  2. If all works, you can delete the backup directory")
    print(f"     rm -rf {backup_dir}")


if __name__ == "__main__":
    migrate_tokens()
