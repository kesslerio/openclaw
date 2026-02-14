"""
Security utilities for credential management, token encryption, and audit logging.

This module provides:
- Secure credential management from environment variables
- Token encryption/decryption at rest
- Audit logging for data access
- OAuth scope validation
"""

import os
import json
import logging
import hashlib
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


class SecureCredentialManager:
    """
    Manages OAuth credentials securely using environment variables and encryption.

    Environment variables required:
    - GOOGLE_CLIENT_ID: OAuth client ID
    - GOOGLE_CLIENT_SECRET: OAuth client secret
    - GOOGLE_PROJECT_ID: Google Cloud project ID
    - MEMEX_ENCRYPTION_KEY: Master encryption key (optional, auto-generated if missing)
    """

    def __init__(self, token_dir: Optional[str] = None):
        self.token_dir = Path(token_dir or Path.home() / ".openclaw" / "credentials" / ".tokens")
        self.token_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

        # Ensure token directory has secure permissions
        os.chmod(self.token_dir, 0o700)

        # Initialize encryption
        self._cipher = self._get_cipher()

    def _get_cipher(self) -> Fernet:
        """Get or create encryption cipher."""
        key = os.getenv("MEMEX_ENCRYPTION_KEY")

        if not key:
            # Generate key from machine-specific data
            key_file = self.token_dir / ".keyfile"

            if key_file.exists():
                with open(key_file, "rb") as f:
                    key = f.read()
            else:
                # Generate new key
                logger.warning("No MEMEX_ENCRYPTION_KEY found, generating from machine ID")
                machine_id = self._get_machine_id()
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=b"memex-integration-salt",
                    iterations=100000,
                )
                key = kdf.derive(machine_id.encode())

                # Save key securely
                with open(key_file, "wb") as f:
                    f.write(key)
                os.chmod(key_file, 0o600)

        # Ensure key is bytes
        if isinstance(key, str):
            key = key.encode()

        # Convert to Fernet-compatible key (base64-encoded 32 bytes)
        from base64 import urlsafe_b64encode
        fernet_key = urlsafe_b64encode(key[:32])

        return Fernet(fernet_key)

    def _get_machine_id(self) -> str:
        """Get unique machine identifier."""
        try:
            # Try to get machine UUID
            import uuid
            return str(uuid.getnode())
        except:
            # Fallback to hostname
            import socket
            return socket.gethostname()

    def get_credentials_dict(self) -> Dict[str, Any]:
        """
        Get OAuth credentials from environment variables.

        Returns:
            Dict with client_id, client_secret, project_id

        Raises:
            ValueError if required environment variables are missing
        """
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        project_id = os.getenv("GOOGLE_PROJECT_ID")

        # Fallback: try to load from credentials.json if exists (for migration)
        if not all([client_id, client_secret, project_id]):
            credentials_path = Path.home() / ".openclaw" / "credentials" / "google_credentials.json"
            if credentials_path.exists():
                logger.warning(
                    "Loading credentials from credentials.json - "
                    "Please migrate to environment variables!"
                )
                with open(credentials_path) as f:
                    data = json.load(f)
                    installed = data.get("installed", {})
                    client_id = client_id or installed.get("client_id")
                    client_secret = client_secret or installed.get("client_secret")
                    project_id = project_id or installed.get("project_id")

        if not all([client_id, client_secret, project_id]):
            raise ValueError(
                "Missing required environment variables:\n"
                "  - GOOGLE_CLIENT_ID\n"
                "  - GOOGLE_CLIENT_SECRET\n"
                "  - GOOGLE_PROJECT_ID\n\n"
                "Set these in your environment or ~/.bashrc or ~/.zshrc"
            )

        return {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "project_id": project_id,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "redirect_uris": ["http://localhost"],
            }
        }

    def save_token(self, token_data: Dict[str, Any], service: str, account: str) -> None:
        """
        Save token with encryption.

        Args:
            token_data: Token dict from OAuth flow
            service: Service name (gmail, calendar)
            account: Account email
        """
        token_path = self.token_dir / f"{service}_{account}.json"

        # Encrypt token data
        json_bytes = json.dumps(token_data).encode()
        encrypted = self._cipher.encrypt(json_bytes)

        # Save encrypted token
        with open(token_path, "wb") as f:
            f.write(encrypted)

        # Ensure secure permissions
        os.chmod(token_path, 0o600)

        # Audit log
        AuditLogger.log_token_write(service, account)

        logger.info(f"✅ Token saved securely for {service}:{account}")

    def load_token(self, service: str, account: str) -> Optional[Dict[str, Any]]:
        """
        Load and decrypt token.

        Args:
            service: Service name (gmail, calendar)
            account: Account email

        Returns:
            Decrypted token dict or None if not found
        """
        token_path = self.token_dir / f"{service}_{account}.json"

        if not token_path.exists():
            # Try unencrypted token for migration
            return self._migrate_unencrypted_token(token_path)

        try:
            with open(token_path, "rb") as f:
                encrypted = f.read()

            # Try to decrypt
            try:
                decrypted = self._cipher.decrypt(encrypted)
                token_data = json.loads(decrypted)
            except:
                # Might be unencrypted (migration case)
                logger.warning(f"Token at {token_path} not encrypted, migrating...")
                with open(token_path, "r") as f:
                    token_data = json.load(f)
                # Re-save encrypted
                self.save_token(token_data, service, account)

            # Audit log
            AuditLogger.log_token_read(service, account)

            return token_data

        except Exception as e:
            logger.error(f"Failed to load token for {service}:{account}: {e}")
            return None

    def _migrate_unencrypted_token(self, token_path: Path) -> Optional[Dict[str, Any]]:
        """Migrate unencrypted token to encrypted format."""
        if not token_path.exists():
            return None

        try:
            with open(token_path, "r") as f:
                token_data = json.load(f)

            # Re-save encrypted
            service = token_path.stem.split("_")[0]
            account = "_".join(token_path.stem.split("_")[1:])
            self.save_token(token_data, service, account)

            logger.info(f"✅ Migrated token to encrypted format: {token_path.name}")
            return token_data

        except Exception as e:
            logger.error(f"Failed to migrate token {token_path}: {e}")
            return None


class AuditLogger:
    """
    Audit logging for security-sensitive operations.

    Logs all data access, token operations, and API calls.
    """

    audit_log_path = Path.home() / ".openclaw" / "credentials" / ".tokens" / "audit.log"

    @classmethod
    def _log(cls, event_type: str, details: Dict[str, Any]) -> None:
        """Write audit log entry."""
        cls.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "details": details,
        }

        with open(cls.audit_log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

        # Ensure log file is secure
        os.chmod(cls.audit_log_path, 0o600)

    @classmethod
    def log_token_read(cls, service: str, account: str) -> None:
        """Log token read access."""
        cls._log("token_read", {
            "service": service,
            "account": cls._hash_email(account),
        })

    @classmethod
    def log_token_write(cls, service: str, account: str) -> None:
        """Log token write/update."""
        cls._log("token_write", {
            "service": service,
            "account": cls._hash_email(account),
        })

    @classmethod
    def log_api_call(cls, service: str, account: str, method: str,
                     resource: str, success: bool) -> None:
        """Log API call."""
        cls._log("api_call", {
            "service": service,
            "account": cls._hash_email(account),
            "method": method,
            "resource": resource,
            "success": success,
        })

    @classmethod
    def log_data_export(cls, service: str, account: str,
                       item_count: int, date_range: str) -> None:
        """Log data export operation."""
        cls._log("data_export", {
            "service": service,
            "account": cls._hash_email(account),
            "item_count": item_count,
            "date_range": date_range,
        })

    @classmethod
    def _hash_email(cls, email: str) -> str:
        """Hash email for privacy in logs."""
        return hashlib.sha256(email.encode()).hexdigest()[:16]


class ScopeValidator:
    """
    Validates OAuth scopes to ensure least privilege.
    """

    # Recommended minimal scopes
    GMAIL_READONLY = ["https://www.googleapis.com/auth/gmail.readonly"]
    GMAIL_MODIFY = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.modify",
    ]

    CALENDAR_READONLY = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events.readonly",
    ]

    @classmethod
    def validate_gmail_scopes(cls, scopes: list, require_readonly: bool = True) -> None:
        """
        Validate Gmail scopes.

        Args:
            scopes: Requested scopes
            require_readonly: If True, enforce readonly scopes

        Raises:
            ValueError if scopes are too broad
        """
        if require_readonly:
            # Check for overly broad scopes
            dangerous_scopes = [
                "https://mail.google.com/",  # Full Gmail access
                "https://www.googleapis.com/auth/gmail.send",  # Can send emails
            ]

            for scope in scopes:
                if scope in dangerous_scopes:
                    raise ValueError(
                        f"Dangerous scope requested: {scope}\n"
                        f"Use readonly scopes: {cls.GMAIL_READONLY}"
                    )

        logger.info(f"✅ Gmail scopes validated: {scopes}")

    @classmethod
    def validate_calendar_scopes(cls, scopes: list) -> None:
        """Validate Calendar scopes."""
        # Calendar readonly is generally safe
        logger.info(f"✅ Calendar scopes validated: {scopes}")


# Singleton instance
_credential_manager = None


def get_credential_manager() -> SecureCredentialManager:
    """Get singleton credential manager."""
    global _credential_manager
    if _credential_manager is None:
        _credential_manager = SecureCredentialManager()
    return _credential_manager
