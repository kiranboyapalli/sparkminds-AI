"""
SparkMinds AI — Account Uniqueness, One-Person-One-Account Policy,
Production Gmail SMTP Email OTP Verification, Recovery, Rate Limiting,
and Non-Destructive Duplicate Audit.

Security Invariants:
- Cryptographically secure 6-digit OTPs generated with `secrets.randbelow`.
- OTPs are NEVER returned in API responses, NEVER displayed in UI, NEVER logged.
- OTPs are stored ONLY as PBKDF2-HMAC-SHA256 salted hashes in SQLite.
- Strict 5-minute OTP expiry, single-use verification, 5-attempt lockout,
  60-second resend cooldown, and automatic invalidation of previous OTPs.
- Gmail SMTP credentials are read strictly from environment variables (never hardcoded).
"""

from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import formataddr
import hashlib
import html
import json
import logging
import math
import os
import re
import secrets
import sqlite3
import threading
import time
import uuid
from typing import Any, Callable, Dict, List, Optional

from app.core.email_provider import (
    EmailTransportDeliveryError,
    EmailTransportRecipientError,
    dispatch_transactional_email,
    load_email_provider_config,
    load_smtp_config,
    send_via_smtp,
)

logger = logging.getLogger("sparkminds.email_otp")

# Exact required user-facing messages (DO NOT ALTER WORDING)
DUPLICATE_USERNAME_MESSAGE = "Username is already used. Please choose another username."
DUPLICATE_VERIFIED_EMAIL_MESSAGE = (
    "An account already exists with this verified email. Please sign in or recover your existing account."
)
UNDER_8_PARENT_HELP_MESSAGE = "Please use your parent's help to sign in."
RECOVERY_ENUMERATION_SAFE_MESSAGE = (
    "If an account matches the details provided, a verification code has been sent to the registered email address."
)
PARENT_CONSENT_DISCLAIMER = (
    "Parental consent and guardian attestation have been recorded with a timestamp. "
    "This process records parental consent without OTP or phone collection and does not "
    "perform independent third-party parent identity verification."
)

OTP_EXPIRY_MINUTES = 5
RESEND_COOLDOWN_SECONDS = 60
MAX_OTP_ATTEMPTS = 5
PBKDF2_ITERATIONS = 100_000

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9._-]{3,40}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
OTP_SIX_DIGIT_PATTERN = re.compile(r"^\d{6}$")
GMAIL_APP_PASSWORD_SPACED_PATTERN = re.compile(r"^[A-Za-z0-9]{4}( [A-Za-z0-9]{4}){3}$")


class DuplicateUsernameError(ValueError):
    """Raised when a case-insensitive username is already taken."""

    def __init__(self, message: str = DUPLICATE_USERNAME_MESSAGE) -> None:
        super().__init__(message)


class DuplicateVerifiedEmailError(ValueError):
    """Raised when a normalized verified email already belongs to an existing account."""

    def __init__(self, message: str = DUPLICATE_VERIFIED_EMAIL_MESSAGE) -> None:
        super().__init__(message)


class RateLimitExceededError(ValueError):
    """Raised when registration, verification, or recovery rate limit is exceeded."""


class EmailVerificationError(ValueError):
    """Raised when an email verification code or token is invalid, expired, used, or mismatched."""


class ResendCooldownError(EmailVerificationError):
    """Raised when a student requests another OTP before the 60-second cooldown finishes."""

    def __init__(self, message: str, retry_after_seconds: int) -> None:
        super().__init__(message)
        self.retry_after_seconds = max(1, int(retry_after_seconds))


class EmailDeliveryError(RuntimeError):
    """Raised when Gmail SMTP cannot deliver the verification email."""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_email(email: Optional[str]) -> str:
    """
    Consistent email normalization: strips leading/trailing whitespace and lowercases.
    Intentionally avoids provider-specific dot or plus-addressing transformations.
    """
    if not email:
        return ""
    return str(email).strip().lower()


def is_valid_email(email: Optional[str]) -> bool:
    norm = normalize_email(email)
    return bool(norm and len(norm) <= 254 and EMAIL_PATTERN.match(norm))


def normalize_username(username: Optional[str]) -> str:
    """Case-insensitive consistent username normalization."""
    if not username:
        return ""
    return str(username).strip().lower()


def validate_username_format(username: str) -> str:
    norm = normalize_username(username)
    if not USERNAME_PATTERN.match(norm):
        raise ValueError(
            "Username must be 3 to 40 characters and contain only letters, numbers, dots, hyphens, or underscores."
        )
    return norm


class SlidingWindowRateLimiter:
    """Thread-safe in-memory sliding-window rate limiter for auth abuse protection."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._events: Dict[str, deque] = defaultdict(deque)

    def check_and_record(
        self,
        key: str,
        max_attempts: int = 30,
        window_seconds: int = 60,
    ) -> None:
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            q = self._events[key]
            while q and q[0] < cutoff:
                q.popleft()
            if len(q) >= max_attempts:
                raise RateLimitExceededError(
                    "Too many requests. Please wait a moment before trying again."
                )
            q.append(now)

    def reset(self, key: Optional[str] = None) -> None:
        with self._lock:
            if key is None:
                self._events.clear()
            else:
                self._events.pop(key, None)


def _load_smtp_config() -> Dict[str, Any]:
    """Backward-compatible alias delegating to email_provider.load_smtp_config()."""
    return load_smtp_config()


def _build_verification_email(
    *,
    to_email: str,
    code: str,
    purpose: str,
    ttl_minutes: int,
    from_name: str,
    from_email: str,
) -> EmailMessage:
    """
    Construct a mobile-friendly, responsive multipart (plain text + HTML)
    SparkMinds AI verification email.
    """
    is_registration = purpose == "registration"
    subject = (
        "SparkMinds AI — Your Email Verification Code"
        if is_registration
        else "SparkMinds AI — Account Recovery Verification Code"
    )
    headline = (
        "Verify your email address"
        if is_registration
        else "Confirm your account recovery"
    )
    intro_line = (
        "Welcome to SparkMinds AI! Enter the 6-digit verification code below to confirm your email address and continue setting up your personal learning account."
        if is_registration
        else "We received a request to recover access to your SparkMinds AI account. Enter the 6-digit verification code below to verify ownership."
    )
    spaced_code = " ".join(code)

    plain_body = (
        f"SparkMinds AI — {headline}\n"
        "Dream Beyond Limits. Learn With Fire. Lead With Power!\n\n"
        f"{intro_line}\n\n"
        f"Your 6-digit verification code: {code}\n\n"
        f"Expiry Notice: This verification code expires in {ttl_minutes} minutes and can only be used once.\n\n"
        "Security Warning: Never share this code with anyone. SparkMinds AI will never ask you for your verification code over chat, phone, or social media. "
        "If you did not request this code, you can safely ignore this email.\n\n"
        "— SparkMinds AI (Your Intelligent Learning Buddy)\n"
    )

    safe_headline = html.escape(headline)
    safe_intro = html.escape(intro_line)
    safe_spaced_code = html.escape(spaced_code)

    html_body = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{html.escape(subject)}</title>
  </head>
  <body style="margin:0;padding:0;background-color:#F6F7FC;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#202943;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color:#F6F7FC;padding:24px 12px;">
      <tr>
        <td align="center">
          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width:520px;background-color:#FFFFFF;border-radius:20px;overflow:hidden;border:1px solid #DFE5F6;box-shadow:0 12px 32px rgba(16,27,53,0.08);">
            <tr>
              <td style="background:linear-gradient(135deg,#101B35 0%,#232B68 58%,#5146E5 100%);padding:28px 24px;text-align:center;">
                <div style="font-size:22px;font-weight:800;letter-spacing:-0.02em;color:#FFFFFF;line-height:1.2;">
                  SparkMinds <span style="display:inline-block;background-color:#35D6E8;color:#101B35;font-size:13px;font-weight:800;padding:2px 8px;border-radius:6px;vertical-align:middle;">AI</span>
                </div>
                <div style="margin-top:8px;font-size:12px;font-weight:700;color:#35D6E8;letter-spacing:0.01em;">
                  Dream Beyond Limits. Learn With Fire. Lead With Power!
                </div>
              </td>
            </tr>
            <tr>
              <td style="padding:28px 24px 20px 24px;">
                <h1 style="margin:0 0 12px 0;font-size:20px;font-weight:800;color:#101B35;line-height:1.3;">
                  {safe_headline}
                </h1>
                <p style="margin:0 0 22px 0;font-size:14px;line-height:1.6;color:#202943;">
                  {safe_intro}
                </p>
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin:0 0 20px 0;">
                  <tr>
                    <td align="center" style="background-color:#EAF0FF;border:2px solid #5146E5;border-radius:16px;padding:20px 16px;">
                      <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;color:#5146E5;margin-bottom:8px;">
                        One-Time Verification Code
                      </div>
                      <div style="font-family:'Courier New',Courier,monospace;font-size:32px;font-weight:800;letter-spacing:0.18em;color:#101B35;">
                        {safe_spaced_code}
                      </div>
                    </td>
                  </tr>
                </table>
                <p style="margin:0 0 16px 0;font-size:13px;line-height:1.55;color:#172554;font-weight:600;">
                  &#9201; This code expires in <strong>{ttl_minutes} minutes</strong> and can only be used once.
                </p>
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin:0 0 8px 0;">
                  <tr>
                    <td style="background-color:#FFF7ED;border:1px solid #FDBA74;border-radius:12px;padding:12px 14px;font-size:12px;line-height:1.55;color:#9A3412;">
                      <strong>Security Warning:</strong> Never share this verification code with anyone. SparkMinds AI will never ask for this code by phone, chat, or message. If you did not request this email, you may safely ignore it.
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td style="background-color:#F7F9FF;border-top:1px solid #E4E8F5;padding:16px 24px;text-align:center;font-size:11px;line-height:1.5;color:#64748B;">
                Sent by <strong>SparkMinds AI</strong> &bull; Your Intelligent Learning Buddy
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr((from_name, from_email))
    msg["To"] = to_email
    msg.set_content(plain_body)
    msg.add_alternative(html_body, subtype="html")
    return msg


class EmailVerificationService:
    """
    Production SQLite-backed Gmail SMTP email OTP verification & recovery service.
    - Generates CSPRNG 6-digit OTPs, hashed with PBKDF2-HMAC-SHA256 + per-OTP salt.
    - Delivers OTP strictly via Gmail SMTP using configured environment variables.
    - NEVER exposes OTP values in API responses, UI, or logs.
    - Enforces 5-minute expiry, 60-second resend cooldown, single-use, 5-attempt lockout,
      and automatic invalidation of prior OTPs when a new OTP is issued.
    """

    def __init__(
        self,
        sqlite_db_path: str,
        email_sender: Optional[Callable[[EmailMessage], None]] = None,
    ) -> None:
        self.sqlite_db_path = sqlite_db_path
        self._lock = threading.RLock()
        self._custom_sender = email_sender
        self._ensure_tables()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.sqlite_db_path, timeout=15.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_tables(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS email_verifications (
                    verification_id TEXT PRIMARY KEY,
                    email_normalized TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    code_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    verification_token TEXT,
                    student_id TEXT,
                    expires_at TEXT NOT NULL,
                    verified_at TEXT,
                    consumed_at TEXT,
                    invalidated_at TEXT,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
                """
            )
            # Safe idempotent migration for existing production databases
            cols = {
                row[1]
                for row in conn.execute("PRAGMA table_info(email_verifications)").fetchall()
            }
            if "invalidated_at" not in cols:
                conn.execute("ALTER TABLE email_verifications ADD COLUMN invalidated_at TEXT")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_email_verifications_lookup ON email_verifications(email_normalized, purpose, created_at)"
            )
            conn.commit()

    @staticmethod
    def _hash_code(code: str, salt: str) -> str:
        dk = hashlib.pbkdf2_hmac(
            "sha256",
            code.strip().encode("utf-8"),
            salt.encode("utf-8"),
            PBKDF2_ITERATIONS,
        )
        return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${dk.hex()}"

    @staticmethod
    def _verify_hash(code: str, salt: str, stored_hash: str) -> bool:
        if stored_hash.startswith("pbkdf2_sha256$"):
            computed = EmailVerificationService._hash_code(code, salt)
            return secrets.compare_digest(computed, stored_hash)
        # Backward compatibility for any legacy SHA-256 hash stored prior to upgrade
        legacy = hashlib.sha256(f"{salt}:{code.strip()}".encode("utf-8")).hexdigest()
        return secrets.compare_digest(legacy, stored_hash)

    def _send_smtp_email(self, msg: EmailMessage) -> Dict[str, Any]:
        """
        Dispatches the verification email through the configured transactional email
        provider (Brevo HTTPS API, Resend HTTPS API, or optional Gmail SMTP fallback).
        """
        if self._custom_sender is not None:
            self._custom_sender(msg)
            return {"provider": "smtp_email", "status_code": 250, "message_id": ""}

        try:
            return dispatch_transactional_email(msg)
        except EmailTransportRecipientError as exc:
            raise EmailVerificationError(str(exc)) from exc
        except EmailTransportDeliveryError as exc:
            raise EmailDeliveryError(str(exc)) from exc

    def create_verification_code(
        self,
        email: str,
        purpose: str = "registration",
        student_id: Optional[str] = None,
        ttl_minutes: int = OTP_EXPIRY_MINUTES,
        cooldown_seconds: int = RESEND_COOLDOWN_SECONDS,
    ) -> Dict[str, Any]:
        norm_email = normalize_email(email)
        if not is_valid_email(norm_email):
            raise EmailVerificationError("Please enter a valid email address.")

        now = datetime.now(timezone.utc)
        expires_at = (now + timedelta(minutes=ttl_minutes)).isoformat()

        # 1. Enforce strict 60-second resend cooldown per (email, purpose)
        with self._lock, self._connect() as conn:
            last_row = conn.execute(
                """
                SELECT created_at FROM email_verifications
                WHERE email_normalized = ? AND purpose = ?
                ORDER BY created_at DESC LIMIT 1
                """,
                (norm_email, purpose),
            ).fetchone()
            if last_row and cooldown_seconds > 0:
                last_created = datetime.fromisoformat(last_row["created_at"])
                if last_created.tzinfo is None:
                    last_created = last_created.replace(tzinfo=timezone.utc)
                elapsed = (now - last_created).total_seconds()
                if elapsed < cooldown_seconds:
                    remaining = max(1, int(math.ceil(cooldown_seconds - elapsed)))
                    raise ResendCooldownError(
                        f"Please wait {remaining} seconds before requesting a new verification code.",
                        retry_after_seconds=remaining,
                    )

        # 2. Generate cryptographically secure 6-digit OTP and PBKDF2-salted hash
        code = f"{secrets.randbelow(900000) + 100000}"
        salt = secrets.token_hex(16)
        code_hash = self._hash_code(code, salt)
        verification_id = f"ev_{uuid.uuid4().hex[:14]}"

        # 3. Build & send email via active provider (Brevo/Resend HTTPS or optional SMTP)
        #    BEFORE persisting as active (if delivery fails, no ghost OTP or cooldown lockout is left behind)
        provider_cfg = load_email_provider_config()
        from_email = provider_cfg["from_email"] or "no-reply@sparkminds.ai"
        from_name = provider_cfg["from_name"] or "SparkMinds AI"
        email_msg = _build_verification_email(
            to_email=norm_email,
            code=code,
            purpose=purpose,
            ttl_minutes=ttl_minutes,
            from_name=from_name,
            from_email=from_email,
        )
        delivery_result = self._send_smtp_email(email_msg)
        delivery_channel = str((delivery_result or {}).get("provider") or "smtp_email")

        # 4. Atomically invalidate all previous unconsumed OTPs and persist the new hashed OTP
        now_iso = now.isoformat()
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                UPDATE email_verifications
                SET invalidated_at = ?
                WHERE email_normalized = ? AND purpose = ?
                  AND consumed_at IS NULL AND invalidated_at IS NULL
                """,
                (now_iso, norm_email, purpose),
            )
            conn.execute(
                """
                INSERT INTO email_verifications (
                    verification_id, email_normalized, purpose, code_hash, salt,
                    student_id, expires_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    verification_id,
                    norm_email,
                    purpose,
                    code_hash,
                    salt,
                    student_id,
                    expires_at,
                    now_iso,
                ),
            )
            conn.commit()

        logger.info(
            "Verification OTP email dispatched via channel=%s purpose=%s verification_id=%s",
            delivery_channel,
            purpose,
            verification_id,
        )

        # CRITICAL SECURITY: NEVER include the OTP value in the returned dictionary
        return {
            "verification_id": verification_id,
            "email_normalized": norm_email,
            "purpose": purpose,
            "expires_at": expires_at,
            "expires_in_seconds": int(ttl_minutes * 60),
            "resend_cooldown_seconds": int(cooldown_seconds),
            "delivery_channel": delivery_channel,
            "message": f"A 6-digit verification code has been sent to your email address. It expires in {ttl_minutes} minutes.",
        }

    def verify_code(
        self,
        email: str,
        code: str,
        purpose: str = "registration",
    ) -> Dict[str, Any]:
        norm_email = normalize_email(email)
        if not is_valid_email(norm_email):
            raise EmailVerificationError("Please enter a valid email address.")
        clean_code = str(code or "").strip()
        if not OTP_SIX_DIGIT_PATTERN.match(clean_code):
            raise EmailVerificationError("Please enter a valid 6-digit verification code.")

        now = datetime.now(timezone.utc)
        with self._lock, self._connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM email_verifications
                WHERE email_normalized = ? AND purpose = ? AND invalidated_at IS NULL
                ORDER BY created_at DESC LIMIT 1
                """,
                (norm_email, purpose),
            ).fetchone()
            if not row:
                raise EmailVerificationError(
                    "No active verification code found for this email. Please request a new code."
                )
            if row["verified_at"] is not None or row["consumed_at"] is not None:
                raise EmailVerificationError(
                    "This verification code has already been used. Please request a new code."
                )
            attempts = int(row["attempts"] or 0)
            if attempts >= MAX_OTP_ATTEMPTS:
                conn.execute(
                    "UPDATE email_verifications SET invalidated_at = ? WHERE verification_id = ?",
                    (now.isoformat(), row["verification_id"]),
                )
                conn.commit()
                raise EmailVerificationError(
                    f"Maximum verification attempts ({MAX_OTP_ATTEMPTS}) exceeded. Please request a new verification code."
                )

            exp_dt = datetime.fromisoformat(row["expires_at"])
            if exp_dt.tzinfo is None:
                exp_dt = exp_dt.replace(tzinfo=timezone.utc)
            if now > exp_dt:
                conn.execute(
                    "UPDATE email_verifications SET invalidated_at = ? WHERE verification_id = ?",
                    (now.isoformat(), row["verification_id"]),
                )
                conn.commit()
                raise EmailVerificationError(
                    "Verification code has expired. Please request a new code."
                )

            if not self._verify_hash(clean_code, row["salt"], row["code_hash"]):
                new_attempts = attempts + 1
                if new_attempts >= MAX_OTP_ATTEMPTS:
                    conn.execute(
                        "UPDATE email_verifications SET attempts = ?, invalidated_at = ? WHERE verification_id = ?",
                        (new_attempts, now.isoformat(), row["verification_id"]),
                    )
                    conn.commit()
                    raise EmailVerificationError(
                        f"Maximum verification attempts ({MAX_OTP_ATTEMPTS}) exceeded. Please request a new verification code."
                    )
                conn.execute(
                    "UPDATE email_verifications SET attempts = ? WHERE verification_id = ?",
                    (new_attempts, row["verification_id"]),
                )
                conn.commit()
                remaining = MAX_OTP_ATTEMPTS - new_attempts
                raise EmailVerificationError(
                    f"Invalid verification code. You have {remaining} attempt(s) remaining."
                )

            token = f"sm_evtok_{secrets.token_urlsafe(24)}"
            now_iso = now.isoformat()
            conn.execute(
                """
                UPDATE email_verifications
                SET verified_at = ?, verification_token = ?
                WHERE verification_id = ?
                """,
                (now_iso, token, row["verification_id"]),
            )
            conn.commit()
            return {
                "verified": True,
                "email_normalized": norm_email,
                "purpose": purpose,
                "email_verification_token": token,
                "verified_at": now_iso,
            }

    def validate_and_consume_token(
        self,
        email: str,
        token: str,
        purpose: str = "registration",
        consume: bool = True,
    ) -> bool:
        norm_email = normalize_email(email)
        clean_token = str(token or "").strip()
        if not norm_email or not clean_token:
            return False
        now = datetime.now(timezone.utc)
        with self._lock, self._connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM email_verifications
                WHERE email_normalized = ? AND purpose = ? AND verification_token = ?
                  AND verified_at IS NOT NULL AND consumed_at IS NULL AND invalidated_at IS NULL
                ORDER BY created_at DESC LIMIT 1
                """,
                (norm_email, purpose, clean_token),
            ).fetchone()
            if not row:
                return False
            verified_dt = datetime.fromisoformat(row["verified_at"])
            if verified_dt.tzinfo is None:
                verified_dt = verified_dt.replace(tzinfo=timezone.utc)
            # Allow 30 minutes after successful email verification to finish filling out registration form
            if now > (verified_dt + timedelta(minutes=30)):
                return False
            if consume:
                conn.execute(
                    "UPDATE email_verifications SET consumed_at = ? WHERE verification_id = ?",
                    (now.isoformat(), row["verification_id"]),
                )
                conn.commit()
            return True


def run_duplicate_account_audit(
    sqlite_db_path: str,
    students: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Non-destructive audit of existing accounts for:
    - Repeated normalized emails
    - Duplicate case-insensitive usernames
    - Missing or inconsistent email verification records
    - Shared parent/guardian emails (flagged as possible siblings, NEVER auto-merged or auto-deleted)
    """
    by_email: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    by_username: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    by_parent_email: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    unverified_accounts: List[str] = []
    missing_email_accounts: List[str] = []

    for sid, sdata in students.items():
        if not isinstance(sdata, dict):
            continue
        summary = {
            "student_id": sid,
            "full_name": sdata.get("full_name", ""),
            "grade": sdata.get("current_grade"),
            "email_verified": bool(sdata.get("email_verified", False)),
        }
        raw_email = sdata.get("verified_email") or sdata.get("email") or (
            sdata.get("email_or_username") if "@" in str(sdata.get("email_or_username") or "") else ""
        )
        norm_email = normalize_email(raw_email)
        if norm_email:
            by_email[norm_email].append(summary)
        else:
            missing_email_accounts.append(sid)

        if not sdata.get("email_verified"):
            unverified_accounts.append(sid)

        raw_username = sdata.get("username") or (
            sdata.get("email_or_username")
            if sdata.get("email_or_username") and "@" not in str(sdata.get("email_or_username"))
            else sid
        )
        norm_user = normalize_username(raw_username)
        if norm_user:
            by_username[norm_user].append(summary)

        pdetails = sdata.get("parent_guardian_details")
        if isinstance(pdetails, dict):
            pemail = normalize_email(pdetails.get("parent_email") or pdetails.get("parent_contact"))
            if pemail and "@" in pemail:
                by_parent_email[pemail].append(summary)

    report = {
        "audit_id": f"dup_audit_{uuid.uuid4().hex[:10]}",
        "audited_at": utc_now_iso(),
        "total_accounts_scanned": len(students),
        "auto_deleted_count": 0,
        "auto_merged_count": 0,
        "repeated_normalized_emails": {k: v for k, v in by_email.items() if len(v) > 1},
        "duplicate_case_insensitive_usernames": {k: v for k, v in by_username.items() if len(v) > 1},
        "shared_guardian_emails_possible_siblings": {
            k: v for k, v in by_parent_email.items() if len(v) > 1
        },
        "accounts_missing_email_count": len(missing_email_accounts),
        "accounts_unverified_email_count": len(unverified_accounts),
        "policy_note": (
            "Read-only audit complete. No student accounts or learning records were modified, "
            "deleted, or merged. Shared guardian emails are permitted for siblings with separate student accounts."
        ),
    }

    try:
        with sqlite3.connect(sqlite_db_path, timeout=10.0) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS duplicate_account_audit_reports (
                    audit_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    report_json TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "INSERT OR REPLACE INTO duplicate_account_audit_reports (audit_id, created_at, report_json) VALUES (?, ?, ?)",
                (report["audit_id"], report["audited_at"], json.dumps(report)),
            )
            conn.commit()
    except Exception:
        pass

    return report
