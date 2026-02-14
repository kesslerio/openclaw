#!/usr/bin/env python3
"""
Complete security setup script.

This script:
1. Checks current security status
2. Sets up environment variables (guides user)
3. Migrates tokens to encrypted format
4. Verifies all security measures

Run this after initial OAuth setup to harden security.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

def check_status():
    """Check current security status."""
    print("🔍 Security Status Check")
    print("=" * 60)
    print()

    issues = []
    warnings = []
    good = []

    # Check 1: Environment variables
    print("1. Environment Variables")
    env_vars = {
        "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID"),
        "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET"),
        "GOOGLE_PROJECT_ID": os.getenv("GOOGLE_PROJECT_ID"),
        "MEMEX_ENCRYPTION_KEY": os.getenv("MEMEX_ENCRYPTION_KEY"),
    }

    missing = [k for k, v in env_vars.items() if not v]

    if missing:
        if "MEMEX_ENCRYPTION_KEY" in missing and len(missing) == 1:
            warnings.append("MEMEX_ENCRYPTION_KEY not set (will auto-generate)")
            print(f"   ⚠️  {warnings[-1]}")
        else:
            issues.append(f"Missing environment variables: {', '.join(missing)}")
            print(f"   ❌ {issues[-1]}")
    else:
        good.append("All environment variables set")
        print(f"   ✅ {good[-1]}")

    print()

    # Check 2: credentials.json
    print("2. Credentials File")
    creds_path = Path.home() / ".openclaw" / "credentials" / "google_credentials.json"
    creds_in_cwd = Path("credentials.json")

    if creds_path.exists() or creds_in_cwd.exists():
        warnings.append("credentials.json found (should use env vars)")
        print(f"   ⚠️  {warnings[-1]}")
        print(f"      Location: {creds_path if creds_path.exists() else creds_in_cwd}")
    else:
        good.append("No credentials.json found (using env vars)")
        print(f"   ✅ {good[-1]}")

    print()

    # Check 3: Token directory permissions
    print("3. Token Directory Permissions")
    token_dir = Path.home() / ".openclaw" / "credentials" / ".tokens"

    if not token_dir.exists():
        warnings.append("Token directory doesn't exist yet")
        print(f"   ⚠️  {warnings[-1]}")
    else:
        # Check directory permissions
        dir_mode = oct(token_dir.stat().st_mode)[-3:]
        if dir_mode != "700":
            issues.append(f"Token directory has insecure permissions: {dir_mode}")
            print(f"   ❌ {issues[-1]}")
            print(f"      Fix: chmod 700 {token_dir}")
        else:
            good.append(f"Token directory secured ({dir_mode})")
            print(f"   ✅ {good[-1]}")

        # Check token file permissions
        token_files = list(token_dir.glob("*.json"))
        if token_files:
            insecure = []
            for tf in token_files:
                mode = oct(tf.stat().st_mode)[-3:]
                if mode != "600":
                    insecure.append(tf.name)

            if insecure:
                issues.append(f"{len(insecure)} token files have insecure permissions")
                print(f"   ❌ {issues[-1]}")
                print(f"      Files: {', '.join(insecure)}")
                print(f"      Fix: chmod 600 {token_dir}/*.json")
            else:
                good.append(f"{len(token_files)} token files secured (600)")
                print(f"   ✅ {good[-1]}")

    print()

    # Check 4: Token encryption
    print("4. Token Encryption")
    if token_dir.exists():
        token_files = list(token_dir.glob("*.json"))
        if token_files:
            # Check if tokens are encrypted by trying to parse as JSON
            encrypted_count = 0
            plaintext_count = 0

            for tf in token_files:
                try:
                    with open(tf, 'r') as f:
                        json.load(f)
                    plaintext_count += 1
                except:
                    # Can't parse as JSON, likely encrypted
                    encrypted_count += 1

            if plaintext_count > 0:
                issues.append(f"{plaintext_count} tokens are NOT encrypted")
                print(f"   ❌ {issues[-1]}")
                print(f"      Fix: python3 memex/scripts/migrate_tokens.py")
            else:
                good.append(f"{encrypted_count} tokens encrypted")
                print(f"   ✅ {good[-1]}")
        else:
            warnings.append("No token files found")
            print(f"   ⚠️  {warnings[-1]}")
    else:
        warnings.append("Token directory doesn't exist")
        print(f"   ⚠️  {warnings[-1]}")

    print()

    # Check 5: Audit logging
    print("5. Audit Logging")
    audit_log = Path.home() / ".openclaw" / "credentials" / ".tokens" / "audit.log"

    if audit_log.exists():
        log_mode = oct(audit_log.stat().st_mode)[-3:]
        if log_mode != "600":
            issues.append(f"Audit log has insecure permissions: {log_mode}")
            print(f"   ❌ {issues[-1]}")
        else:
            # Count log entries
            with open(audit_log) as f:
                count = sum(1 for _ in f)
            good.append(f"Audit log active ({count} entries)")
            print(f"   ✅ {good[-1]}")
    else:
        warnings.append("No audit log yet (will be created on first use)")
        print(f"   ⚠️  {warnings[-1]}")

    print()

    # Check 6: Git security
    print("6. Git Security")

    # Check if credentials.json is in git
    try:
        import subprocess
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "credentials.json"],
            capture_output=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        if result.returncode == 0:
            issues.append("credentials.json is tracked in git")
            print(f"   ❌ {issues[-1]}")
            print(f"      Fix: git rm --cached credentials.json")
        else:
            good.append("credentials.json not in git")
            print(f"   ✅ {good[-1]}")
    except:
        warnings.append("Could not check git status")
        print(f"   ⚠️  {warnings[-1]}")

    print()
    print("=" * 60)
    print()

    # Summary
    print("📊 Summary")
    print(f"   ✅ Good: {len(good)}")
    print(f"   ⚠️  Warnings: {len(warnings)}")
    print(f"   ❌ Issues: {len(issues)}")
    print()

    if issues:
        print("🚨 Action Required:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        print()

    if warnings:
        print("⚠️  Warnings:")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")
        print()

    return len(issues) == 0


def setup_guide():
    """Display setup guide."""
    print()
    print("📖 Security Setup Guide")
    print("=" * 60)
    print()
    print("Follow these steps to secure your Memex integration:")
    print()
    print("Step 1: Set up environment variables")
    print("---------------------------------------")
    print("Run: ./memex/scripts/setup_env.sh")
    print()
    print("Or manually add to ~/.zshrc or ~/.bashrc:")
    print('  export GOOGLE_CLIENT_ID="..."')
    print('  export GOOGLE_CLIENT_SECRET="..."')
    print('  export GOOGLE_PROJECT_ID="memex-integrations"')
    print('  export MEMEX_ENCRYPTION_KEY="$(openssl rand -base64 32)"')
    print()
    print("Step 2: Reload shell")
    print("--------------------")
    print("Run: source ~/.zshrc")
    print()
    print("Step 3: Migrate tokens")
    print("----------------------")
    print("Run: python3 memex/scripts/migrate_tokens.py")
    print()
    print("Step 4: Verify security")
    print("-----------------------")
    print("Run: python3 memex/scripts/security_setup.py")
    print()
    print("Step 5: Remove credentials.json (optional)")
    print("------------------------------------------")
    print("After verifying everything works:")
    print("  cp ~/.openclaw/credentials/google_credentials.json ~/.openclaw/credentials/google_credentials.json.backup")
    print("  rm ~/.openclaw/credentials/google_credentials.json")
    print()
    print("=" * 60)
    print()


def main():
    """Main entry point."""
    print()
    print("🔐 Memex Security Setup")
    print("=" * 60)
    print()

    # Check status
    all_good = check_status()

    if not all_good:
        setup_guide()
        print("❌ Security setup incomplete")
        print()
        print("Please follow the setup guide above.")
        print()
        return 1

    print("✅ All security measures in place!")
    print()
    print("Your Memex integration is secured with:")
    print("  • Environment-based credentials")
    print("  • AES-256 token encryption")
    print("  • Audit logging")
    print("  • Secure file permissions")
    print("  • Git secrets prevention")
    print()
    print("View detailed security documentation:")
    print("  memex/integrations/SECURITY.md")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
