"""
Production Gmail SMTP Email OTP Verification Test Suite for SparkMinds AI.

Verifies every functional and security requirement:
1. OTP email delivery to Gmail and other valid email providers (Outlook, Yahoo, etc.)
   with mobile-friendly SparkMinds AI branding, 6-digit OTP, 5-minute expiry, and security warning.
2. Gmail SMTP STARTTLS transport & environment variable parsing (including spaced 19-char
   Gmail App Passwords and space-separated Railway env-var fallbacks).
3. Strict secret & OTP hygiene: NEVER returned in API responses, NEVER stored in plaintext
   in SQLite (PBKDF2-HMAC-SHA256 salted hash), NEVER logged in application logs.
4. Correct OTP verification & single-use verification token issuance.
5. Incorrect OTP rejection with remaining-attempt tracking.
6. Maximum attempt enforcement (5 failed attempts lock/invalidate OTP).
7. Expired OTP rejection (5-minute expiry) + requesting a new OTP afterward.
8. Reuse of an already verified OTP rejected (single-use enforcement).
9. Resend OTP functionality & automatic invalidation of previous OTPs.
10. 60-second resend cooldown (HTTP 429 + Retry-After + retry_after_seconds).
11. Rate-limiting protection against OTP request abuse.
12. SMTP authentication failure & missing credential handling (HTTP 503, no secret leak,
    no phantom cooldown lockout).
13. Full registration after successful verification + duplicate email rejection.
14. Registration without email verification strictly blocked (strict mode, forged token,
    cross-email token swap, AND production-mode bypass attempt with strict_registration=False).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
import logging
import re
import smtplib
import sqlite3
from typing import List
import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.account_policy import (
    DUPLICATE_VERIFIED_EMAIL_MESSAGE,
    EmailDeliveryError,
    _load_smtp_config,
)
from app.main import app
from app.routers.api_router import repo

client = TestClient(app)


def _uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _extract_otp(msg: EmailMessage) -> str:
    plain_part = msg.get_body(preferencelist=("plain",))
    body_text = plain_part.get_content() if plain_part else str(msg)
    match = re.search(r"\b(\d{6})\b", body_text)
    assert match, f"Expected 6-digit OTP in email body, got: {body_text}"
    return match.group(1)


def _backdate_otp_row(email: str, *, created_minutes_ago: int = 0, expires_minutes_ago: int = 0) -> None:
    norm = email.strip().lower()
    now = datetime.now(timezone.utc)
    with sqlite3.connect(str(repo.sqlite_db_path), timeout=15.0) as conn:
        if created_minutes_ago:
            new_created = (now - timedelta(minutes=created_minutes_ago)).isoformat()
            conn.execute(
                "UPDATE email_verifications SET created_at = ? WHERE email_normalized = ?",
                (new_created, norm),
            )
        if expires_minutes_ago:
            new_exp = (now - timedelta(minutes=expires_minutes_ago)).isoformat()
            conn.execute(
                "UPDATE email_verifications SET expires_at = ? WHERE email_normalized = ?",
                (new_exp, norm),
            )
        conn.commit()


@pytest.fixture(autouse=True)
def _clean_rate_limiter_and_sender():
    repo.rate_limiter.reset()
    prev_sender = repo.email_verification._custom_sender
    yield
    repo.email_verification._custom_sender = prev_sender
    repo.rate_limiter.reset()


def test_01_smtp_config_reads_env_and_normalizes_gmail_app_password(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.gmail.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USERNAME", "sparkminds.ai@gmail.com")
    monkeypatch.setenv("SMTP_PASSWORD", "abcd efgh ijkl mnop")
    monkeypatch.delenv("SMTP_FROM_EMAIL", raising=False)
    monkeypatch.delenv("SMTP_FROM_NAME", raising=False)
    monkeypatch.setenv("SMTP_FROM EMAIL", "sparkminds.ai@gmail.com")
    monkeypatch.setenv("SMTP_FROM NAME", "SparkMinds AI")

    cfg = _load_smtp_config()
    assert cfg["host"] == "smtp.gmail.com"
    assert cfg["port"] == 587
    assert cfg["username"] == "sparkminds.ai@gmail.com"
    assert cfg["password"] == "abcdefghijklmnop"
    assert cfg["from_email"] == "sparkminds.ai@gmail.com"
    assert cfg["from_name"] == "SparkMinds AI"


def test_02_otp_email_delivery_gmail_and_other_providers_via_starttls(monkeypatch, caplog):
    monkeypatch.setenv("SMTP_HOST", "smtp.gmail.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USERNAME", "sparkminds.ai@gmail.com")
    monkeypatch.setenv("SMTP_PASSWORD", "wxyz 1234 abcd 5678")
    monkeypatch.setenv("SMTP_FROM_EMAIL", "sparkminds.ai@gmail.com")
    monkeypatch.setenv("SMTP_FROM_NAME", "SparkMinds AI")

    sent_envelopes: List[dict] = []

    class FakeSMTP:
        def __init__(self, host, port, timeout=15):
            self.host = host
            self.port = port
            self.timeout = timeout
            self.tls_started = False
            self.logged_in = None

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def ehlo(self):
            return (250, b"ok")

        def starttls(self, context=None):
            self.tls_started = True
            return (220, b"ready")

        def login(self, user, password):
            self.logged_in = (user, password)
            return (235, b"authenticated")

        def send_message(self, msg):
            sent_envelopes.append(
                {
                    "host": self.host,
                    "port": self.port,
                    "tls": self.tls_started,
                    "auth": self.logged_in,
                    "msg": msg,
                }
            )
            return {}

    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    repo.email_verification._custom_sender = None

    providers = [
        f"{_uid('gmail_student')}@gmail.com",
        f"{_uid('outlook_student')}@outlook.com",
        f"{_uid('yahoo_student')}@yahoo.com",
    ]

    with caplog.at_level(logging.DEBUG):
        for recipient in providers:
            res = client.post(
                "/api/auth/email/send-code",
                json={"email": recipient, "purpose": "registration"},
            )
            assert res.status_code == 200, res.text
            body = res.json()
            assert body["delivery_channel"] == "smtp_email"
            assert body["expires_in_seconds"] == 300
            assert body["resend_cooldown_seconds"] == 60
            # Never expose OTP in API response
            for forbidden in (
                "in_app_verification_code",
                "verification_code_preview",
                "otp",
                "code",
            ):
                assert forbidden not in body

    assert len(sent_envelopes) == 3
    all_logs = "\n".join(rec.getMessage() for rec in caplog.records)
    assert "wxyz1234abcd5678" not in all_logs
    assert "wxyz 1234 abcd 5678" not in all_logs

    for env, recipient in zip(sent_envelopes, providers):
        assert env["host"] == "smtp.gmail.com"
        assert env["port"] == 587
        assert env["tls"] is True
        assert env["auth"] == ("sparkminds.ai@gmail.com", "wxyz1234abcd5678")

        msg: EmailMessage = env["msg"]
        assert msg["To"] == recipient
        assert "SparkMinds AI" in msg["From"]
        assert "sparkminds.ai@gmail.com" in msg["From"]

        otp = _extract_otp(msg)
        # OTP must NEVER appear in logs or plaintext in SQLite
        assert otp not in all_logs

        plain = msg.get_body(preferencelist=("plain",)).get_content()
        html_part = msg.get_body(preferencelist=("html",)).get_content()
        for content in (plain, html_part):
            assert "SparkMinds" in content
            assert "5 minutes" in content
            assert "Never share" in content

        with sqlite3.connect(str(repo.sqlite_db_path), timeout=15.0) as conn:
            row = conn.execute(
                "SELECT code_hash, salt FROM email_verifications WHERE email_normalized = ? ORDER BY created_at DESC LIMIT 1",
                (recipient,),
            ).fetchone()
            assert row is not None
            assert row[0].startswith("pbkdf2_sha256$100000$")
            assert otp not in row[0]
            assert otp not in row[1]


def test_03_correct_otp_verification_and_reuse_rejection():
    captured: List[EmailMessage] = []
    repo.email_verification._custom_sender = captured.append
    email = f"{_uid('verify_ok')}@gmail.com"

    send_res = client.post(
        "/api/auth/email/send-code",
        json={"email": email, "purpose": "registration"},
    )
    assert send_res.status_code == 200
    otp = _extract_otp(captured[-1])

    # First verification succeeds
    ver1 = client.post(
        "/api/auth/email/verify-code",
        json={"email": email, "code": otp, "purpose": "registration"},
    )
    assert ver1.status_code == 200, ver1.text
    token = ver1.json()["email_verification_token"]
    assert token.startswith("sm_evtok_")

    # Second attempt reusing the exact same verified OTP MUST fail (single-use)
    ver2 = client.post(
        "/api/auth/email/verify-code",
        json={"email": email, "code": otp, "purpose": "registration"},
    )
    assert ver2.status_code == 400
    assert "already been used" in ver2.json()["detail"].lower()


def test_04_incorrect_otp_rejection_and_max_5_attempts_lockout():
    captured: List[EmailMessage] = []
    repo.email_verification._custom_sender = captured.append
    email = f"{_uid('attempts')}@gmail.com"

    assert client.post(
        "/api/auth/email/send-code", json={"email": email, "purpose": "registration"}
    ).status_code == 200
    real_otp = _extract_otp(captured[-1])
    wrong_otp = "000000" if real_otp != "000000" else "999999"

    # Malformed OTP format rejected cleanly
    bad_fmt = client.post(
        "/api/auth/email/verify-code",
        json={"email": email, "code": "abc", "purpose": "registration"},
    )
    assert bad_fmt.status_code == 400

    # Attempts 1..4 fail with remaining count
    for attempt_num in range(1, 5):
        res = client.post(
            "/api/auth/email/verify-code",
            json={"email": email, "code": wrong_otp, "purpose": "registration"},
        )
        assert res.status_code == 400
        assert f"{5 - attempt_num} attempt(s) remaining" in res.json()["detail"]

    # Attempt 5 locks & invalidates the OTP
    res5 = client.post(
        "/api/auth/email/verify-code",
        json={"email": email, "code": wrong_otp, "purpose": "registration"},
    )
    assert res5.status_code == 400
    assert "maximum verification attempts" in res5.json()["detail"].lower()

    # Even entering the REAL OTP on attempt 6 MUST be rejected because OTP was invalidated
    res6 = client.post(
        "/api/auth/email/verify-code",
        json={"email": email, "code": real_otp, "purpose": "registration"},
    )
    assert res6.status_code == 400


def test_05_expired_otp_rejected_and_new_otp_allowed():
    captured: List[EmailMessage] = []
    repo.email_verification._custom_sender = captured.append
    email = f"{_uid('expired')}@gmail.com"

    assert client.post(
        "/api/auth/email/send-code", json={"email": email, "purpose": "registration"}
    ).status_code == 200
    old_otp = _extract_otp(captured[-1])

    # Expire OTP (past 5-minute TTL and past 60s cooldown)
    _backdate_otp_row(email, created_minutes_ago=6, expires_minutes_ago=1)

    exp_res = client.post(
        "/api/auth/email/verify-code",
        json={"email": email, "code": old_otp, "purpose": "registration"},
    )
    assert exp_res.status_code == 400
    assert "expired" in exp_res.json()["detail"].lower()

    # Student can now request a fresh OTP and verify it
    resend_res = client.post(
        "/api/auth/email/send-code", json={"email": email, "purpose": "registration"}
    )
    assert resend_res.status_code == 200
    fresh_otp = _extract_otp(captured[-1])

    ok_res = client.post(
        "/api/auth/email/verify-code",
        json={"email": email, "code": fresh_otp, "purpose": "registration"},
    )
    assert ok_res.status_code == 200
    assert ok_res.json()["verified"] is True


def test_06_resend_cooldown_60s_and_previous_otp_invalidation():
    captured: List[EmailMessage] = []
    repo.email_verification._custom_sender = captured.append
    email = f"{_uid('resend')}@outlook.com"

    r1 = client.post(
        "/api/auth/email/send-code", json={"email": email, "purpose": "registration"}
    )
    assert r1.status_code == 200
    first_otp = _extract_otp(captured[-1])

    # Immediate resend within 60 seconds MUST be rejected with HTTP 429 + Retry-After
    r2 = client.post(
        "/api/auth/email/send-code", json={"email": email, "purpose": "registration"}
    )
    assert r2.status_code == 429
    assert "Retry-After" in r2.headers
    retry_secs = r2.json().get("retry_after_seconds", 0)
    assert 1 <= retry_secs <= 60

    # Simulate 61 seconds passing -> resend succeeds & invalidates first OTP
    _backdate_otp_row(email, created_minutes_ago=2)
    r3 = client.post(
        "/api/auth/email/send-code", json={"email": email, "purpose": "registration"}
    )
    assert r3.status_code == 200
    second_otp = _extract_otp(captured[-1])

    # If CSPRNG happened to generate same 6 digits (1 in 900,000), skip mismatch assertion
    if first_otp != second_otp:
        old_try = client.post(
            "/api/auth/email/verify-code",
            json={"email": email, "code": first_otp, "purpose": "registration"},
        )
        assert old_try.status_code == 400

    # Latest OTP succeeds
    new_try = client.post(
        "/api/auth/email/verify-code",
        json={"email": email, "code": second_otp, "purpose": "registration"},
    )
    assert new_try.status_code == 200


def test_07_rate_limiting_blocks_excessive_otp_requests():
    captured: List[EmailMessage] = []
    repo.email_verification._custom_sender = captured.append
    email = f"{_uid('ratelimit')}@gmail.com"

    for i in range(5):
        if i > 0:
            _backdate_otp_row(email, created_minutes_ago=2)
        res = client.post(
            "/api/auth/email/send-code", json={"email": email, "purpose": "registration"}
        )
        assert res.status_code == 200, f"Unexpected failure on request #{i + 1}: {res.text}"

    # 6th request within 15-minute window MUST hit rate limit even after cooldown
    _backdate_otp_row(email, created_minutes_ago=2)
    blocked = client.post(
        "/api/auth/email/send-code", json={"email": email, "purpose": "registration"}
    )
    assert blocked.status_code == 429


def test_08_smtp_authentication_failure_handled_gracefully_without_secret_leak(monkeypatch, caplog):
    monkeypatch.setenv("SMTP_HOST", "smtp.gmail.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USERNAME", "sparkminds.ai@gmail.com")
    monkeypatch.setenv("SMTP_PASSWORD", "SuperSecretAppPass99")

    class AuthFailingSMTP:
        def __init__(self, host, port, timeout=15):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def ehlo(self):
            return (250, b"ok")

        def starttls(self, context=None):
            return (220, b"ready")

        def login(self, user, password):
            raise smtplib.SMTPAuthenticationError(535, b"5.7.8 Username and Password not accepted")

    monkeypatch.setattr(smtplib, "SMTP", AuthFailingSMTP)
    repo.email_verification._custom_sender = None
    email = f"{_uid('smtp_fail')}@gmail.com"

    with caplog.at_level(logging.DEBUG):
        res = client.post(
            "/api/auth/email/send-code", json={"email": email, "purpose": "registration"}
        )
    assert res.status_code == 503
    detail = res.json()["detail"]
    assert "authentication failure" in detail.lower()
    assert "SuperSecretAppPass99" not in detail
    all_logs = "\n".join(rec.getMessage() for rec in caplog.records)
    assert "SuperSecretAppPass99" not in all_logs

    # Confirm no phantom OTP row was persisted (so once SMTP is fixed, user isn't stuck in cooldown)
    with sqlite3.connect(str(repo.sqlite_db_path), timeout=15.0) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM email_verifications WHERE email_normalized = ?",
            (email,),
        ).fetchone()[0]
    assert count == 0


def test_09_registration_after_verification_and_token_single_use_and_duplicate_block():
    captured: List[EmailMessage] = []
    repo.email_verification._custom_sender = captured.append
    email = f"{_uid('reg_ok')}@gmail.com"
    uname = _uid("student_ok")

    assert client.post(
        "/api/auth/email/send-code", json={"email": email, "purpose": "registration"}
    ).status_code == 200
    otp = _extract_otp(captured[-1])

    ver = client.post(
        "/api/auth/email/verify-code",
        json={"email": email, "code": otp, "purpose": "registration"},
    )
    assert ver.status_code == 200
    token = ver.json()["email_verification_token"]

    reg = client.post(
        "/api/auth/register",
        json={
            "student_id": f"stu_{uname}",
            "full_name": "Verified Student",
            "username": uname,
            "email": email,
            "email_verification_token": token,
            "strict_registration": True,
            "age": 13,
            "grade": 8,
            "school_board": "CBSE",
            "date_of_birth": "2013-07-10",
            "password_or_pin": "SecurePass2026",
            "device_name": "Chrome Test",
        },
    )
    assert reg.status_code == 200, reg.text
    student = reg.json()["student"]
    assert student["email_verified"] is True
    assert student["verified_email"] == email

    # Reusing the same consumed verification token for another registration MUST fail
    reuse_tok = client.post(
        "/api/auth/register",
        json={
            "student_id": f"stu_{_uid('reuse')}",
            "full_name": "Reuse Attempt",
            "username": _uid("reuse_u"),
            "email": email,
            "email_verification_token": token,
            "strict_registration": True,
            "age": 13,
            "grade": 8,
            "date_of_birth": "2013-07-10",
            "password_or_pin": "Pass1234",
        },
    )
    assert reuse_tok.status_code in (400, 409)

    # Requesting a new OTP for an already-registered verified email returns HTTP 409
    _backdate_otp_row(email, created_minutes_ago=2)
    dup_send = client.post(
        "/api/auth/email/send-code", json={"email": email, "purpose": "registration"}
    )
    assert dup_send.status_code == 409
    assert dup_send.json()["detail"] == DUPLICATE_VERIFIED_EMAIL_MESSAGE


def test_10_registration_without_verification_and_production_bypass_blocked(monkeypatch):
    captured: List[EmailMessage] = []
    repo.email_verification._custom_sender = captured.append

    # 1. Strict registration with no token -> HTTP 400
    r_no_tok = client.post(
        "/api/auth/register",
        json={
            "student_id": f"stu_{_uid('nobypass1')}",
            "full_name": "No Token Student",
            "username": _uid("notok"),
            "email": f"{_uid('notok')}@gmail.com",
            "strict_registration": True,
            "age": 12,
            "grade": 7,
            "date_of_birth": "2014-05-01",
            "password_or_pin": "Pass1234",
        },
    )
    assert r_no_tok.status_code == 400

    # 2. Forged token -> HTTP 400
    r_forged = client.post(
        "/api/auth/register",
        json={
            "student_id": f"stu_{_uid('forged')}",
            "full_name": "Forged Token Student",
            "username": _uid("forged"),
            "email": f"{_uid('forged')}@gmail.com",
            "email_verification_token": "sm_evtok_forged_fake_token_12345",
            "strict_registration": True,
            "age": 12,
            "grade": 7,
            "date_of_birth": "2014-05-01",
            "password_or_pin": "Pass1234",
        },
    )
    assert r_forged.status_code == 400

    # 3. Cross-email token swap (verify email A, try registering email B) -> HTTP 400
    email_a = f"{_uid('email_a')}@gmail.com"
    email_b = f"{_uid('email_b')}@gmail.com"
    assert client.post(
        "/api/auth/email/send-code", json={"email": email_a, "purpose": "registration"}
    ).status_code == 200
    tok_a = client.post(
        "/api/auth/email/verify-code",
        json={"email": email_a, "code": _extract_otp(captured[-1]), "purpose": "registration"},
    ).json()["email_verification_token"]

    r_swap = client.post(
        "/api/auth/register",
        json={
            "student_id": f"stu_{_uid('swap')}",
            "full_name": "Swap Student",
            "username": _uid("swap"),
            "email": email_b,
            "email_verification_token": tok_a,
            "strict_registration": True,
            "age": 12,
            "grade": 7,
            "date_of_birth": "2014-05-01",
            "password_or_pin": "Pass1234",
        },
    )
    assert r_swap.status_code == 400

    # 4. Production bypass attempt (SPARKMINDS_ENV=production, strict_registration=False, email_or_username) -> HTTP 400
    monkeypatch.setenv("SPARKMINDS_ENV", "production")
    r_prod_bypass = client.post(
        "/api/auth/register",
        json={
            "student_id": f"stu_{_uid('prodbypass')}",
            "full_name": "Bypass Attacker",
            "email_or_username": f"{_uid('attacker')}@gmail.com",
            "strict_registration": False,
            "age": 12,
            "grade": 7,
            "date_of_birth": "2014-05-01",
            "password_or_pin": "Pass1234",
        },
    )
    assert r_prod_bypass.status_code == 400
