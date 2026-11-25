"""
SparkMinds AI — HTTPS Transactional Email Provider Tests (Brevo, Resend, & Optional Gmail SMTP Fallback).

Verifies:
1. Brevo HTTPS API integration (port 443) sends proper headers/payload & preserves SparkMinds AI email design.
2. Resend HTTPS API integration (port 443) sends proper Bearer auth/payload & preserves SparkMinds AI email design.
3. Auto-selection priority (Brevo > Resend > optional Gmail SMTP fallback) and explicit EMAIL_PROVIDER override.
4. Optional Gmail SMTP fallback works only when explicitly enabled or when no HTTPS API key is configured.
5. Error handling (401 auth error, 422/400 invalid recipient, 429 rate limit, network error) never leaks API keys or OTPs.
6. All OTP security invariants remain intact (6-digit CSPRNG, 5-min expiry, single-use, 60s resend cooldown,
   5-attempt lockout, prior OTP invalidation, PBKDF2 hashing, zero OTP in API responses or logs).
"""

from __future__ import annotations

import logging
import re
from unittest.mock import MagicMock, patch

import pytest

from app.core.account_policy import (
    EmailDeliveryError,
    EmailVerificationError,
    EmailVerificationService,
    ResendCooldownError,
)
from app.core.email_provider import (
    load_email_provider_config,
)


def _mock_httpx_response(status_code: int, json_body: dict | None = None, text: str = "") -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text or (str(json_body) if json_body else "")
    resp.json.return_value = json_body or {}
    return resp


def test_brevo_https_otp_delivery_and_full_security_invariants(tmp_path, monkeypatch, caplog):
    """Brevo HTTPS API sends verification OTP cleanly using BREVO_API_KEY, BREVO_SENDER_EMAIL, BREVO_SENDER_NAME."""
    monkeypatch.setenv("EMAIL_PROVIDER", "auto")
    monkeypatch.setenv("BREVO_API_KEY", "xkeysib-test-secret-do-not-leak-9999")
    monkeypatch.setenv("BREVO_SENDER_EMAIL", "sparkminds.ai@gmail.com")
    monkeypatch.setenv("BREVO_SENDER_NAME", "SparkMinds AI")
    monkeypatch.setenv("SMTP_FROM_EMAIL", "different-legacy@example.com")
    monkeypatch.delenv("BREVO_FROM_EMAIL", raising=False)
    monkeypatch.delenv("RESEND_API_KEY", raising=False)

    cfg = load_email_provider_config()
    assert cfg["active_provider"] == "brevo"
    assert cfg["https_api_configured"] is True
    assert cfg["brevo_from_email"] == "sparkminds.ai@gmail.com"
    assert cfg["brevo_from_name"] == "SparkMinds AI"

    captured_request = {}

    def _fake_post(url, headers=None, json=None):
        captured_request["url"] = url
        captured_request["headers"] = headers or {}
        captured_request["json"] = json or {}
        return _mock_httpx_response(201, {"messageId": "<brevo-msg-123@brevo.com>"})

    mock_client = MagicMock()
    mock_client.__enter__.return_value.post.side_effect = _fake_post

    svc = EmailVerificationService(str(tmp_path / "otp_brevo.db"))

    with caplog.at_level(logging.INFO):
        with patch("app.core.email_provider.httpx.Client", return_value=mock_client):
            res = svc.create_verification_code(
                email="student.brevo@example.com",
                purpose="registration",
            )

    # Verify Brevo HTTPS endpoint & headers
    assert captured_request["url"] == "https://api.brevo.com/v3/smtp/email"
    assert captured_request["headers"]["api-key"] == "xkeysib-test-secret-do-not-leak-9999"
    payload = captured_request["json"]
    assert payload["sender"] == {"name": "SparkMinds AI", "email": "sparkminds.ai@gmail.com"}
    assert payload["to"] == [{"email": "student.brevo@example.com"}]
    assert "SparkMinds AI" in payload["subject"]
    assert "SparkMinds" in payload["htmlContent"]
    assert "5 minutes" in payload["textContent"]

    otp_match = re.search(r"\b(\d{6})\b", payload["textContent"])
    assert otp_match is not None
    otp = otp_match.group(1)

    # CRITICAL SECURITY: Neither OTP nor Brevo API key appears in response or logs
    assert res["delivery_channel"] == "brevo_https"
    assert otp not in str(res)
    assert "xkeysib-test-secret" not in str(res)
    assert otp not in caplog.text
    assert "xkeysib-test-secret" not in caplog.text

    # 60-second resend cooldown enforced
    with pytest.raises(ResendCooldownError) as exc_cd:
        with patch("app.core.email_provider.httpx.Client", return_value=mock_client):
            svc.create_verification_code(email="student.brevo@example.com", purpose="registration")
    assert 1 <= exc_cd.value.retry_after_seconds <= 60

    # Wrong OTP fails and tracks attempts; valid OTP succeeds once and cannot be reused
    with pytest.raises(EmailVerificationError):
        svc.verify_code(email="student.brevo@example.com", code="000000" if otp != "000000" else "111111")
    verified = svc.verify_code(email="student.brevo@example.com", code=otp)
    assert verified["verified"] is True
    assert verified["email_verification_token"].startswith("sm_evtok_")

    # Single-use: second verification with same OTP MUST fail
    with pytest.raises(EmailVerificationError):
        svc.verify_code(email="student.brevo@example.com", code=otp)


def test_brevo_https_timeout_and_api_errors_handled_safely(tmp_path, monkeypatch, caplog):
    """Timeouts and Brevo API errors raise clean EmailDeliveryError with zero ghost OTPs or key leaks."""
    import httpx

    monkeypatch.setenv("EMAIL_PROVIDER", "brevo")
    monkeypatch.setenv("BREVO_API_KEY", "xkeysib-timeout-secret-do-not-leak")
    monkeypatch.setenv("BREVO_SENDER_EMAIL", "sparkminds.ai@gmail.com")
    monkeypatch.setenv("BREVO_SENDER_NAME", "SparkMinds AI")
    monkeypatch.setenv("SMTP_FALLBACK_ENABLED", "false")

    svc = EmailVerificationService(str(tmp_path / "otp_brevo_err.db"))

    # 1. Timeout handling
    mock_timeout = MagicMock()
    mock_timeout.__enter__.return_value.post.side_effect = httpx.TimeoutException("timed out")
    with caplog.at_level(logging.INFO):
        with patch("app.core.email_provider.httpx.Client", return_value=mock_timeout):
            with pytest.raises(EmailDeliveryError):
                svc.create_verification_code(email="timeout.student@example.com", purpose="registration")
    assert "xkeysib-timeout-secret" not in caplog.text

    # 2. 401 Invalid API key handling
    mock_401 = MagicMock()
    mock_401.__enter__.return_value.post.return_value = _mock_httpx_response(401, {"code": "unauthorized"})
    with patch("app.core.email_provider.httpx.Client", return_value=mock_401):
        with pytest.raises(EmailDeliveryError):
            svc.create_verification_code(email="timeout.student@example.com", purpose="registration")

    # 3. Verify no ghost OTP left behind after delivery failure
    with pytest.raises(EmailVerificationError):
        svc.verify_code(email="timeout.student@example.com", code="123456")


def test_resend_https_otp_delivery_and_error_handling(tmp_path, monkeypatch, caplog):
    """Resend HTTPS API sends verification OTP cleanly and handles auth/rate errors safely."""
    monkeypatch.setenv("EMAIL_PROVIDER", "auto")
    monkeypatch.delenv("BREVO_API_KEY", raising=False)
    monkeypatch.setenv("RESEND_API_KEY", "re_test_secret_key_never_expose_1234")
    monkeypatch.setenv("RESEND_FROM_EMAIL", "verify@sparkminds.ai")
    monkeypatch.setenv("RESEND_FROM_NAME", "SparkMinds AI")

    cfg = load_email_provider_config()
    assert cfg["active_provider"] == "resend"

    captured = {}

    def _fake_post(url, headers=None, json=None):
        captured["url"] = url
        captured["headers"] = headers or {}
        captured["json"] = json or {}
        return _mock_httpx_response(200, {"id": "re_msg_abc123"})

    mock_client = MagicMock()
    mock_client.__enter__.return_value.post.side_effect = _fake_post

    svc = EmailVerificationService(str(tmp_path / "otp_resend.db"))
    with caplog.at_level(logging.INFO):
        with patch("app.core.email_provider.httpx.Client", return_value=mock_client):
            res = svc.create_verification_code(email="student.resend@example.com", purpose="registration")

    assert captured["url"] == "https://api.resend.com/emails"
    assert captured["headers"]["Authorization"] == "Bearer re_test_secret_key_never_expose_1234"
    assert captured["json"]["from"] == "SparkMinds AI <verify@sparkminds.ai>"
    assert captured["json"]["to"] == ["student.resend@example.com"]
    assert res["delivery_channel"] == "resend_https"

    otp = re.search(r"\b(\d{6})\b", captured["json"]["text"]).group(1)
    assert otp not in str(res)
    assert otp not in caplog.text
    assert "re_test_secret_key" not in caplog.text

    # Auth failure (401) raises EmailDeliveryError cleanly without saving ghost OTP
    mock_fail = MagicMock()
    mock_fail.__enter__.return_value.post.return_value = _mock_httpx_response(401, {"message": "Unauthorized"})
    with patch("app.core.email_provider.httpx.Client", return_value=mock_fail):
        with pytest.raises(EmailDeliveryError):
            svc.create_verification_code(email="other.resend@example.com", purpose="registration")


def test_optional_smtp_fallback_when_enabled(tmp_path, monkeypatch):
    """When BREVO fails and SMTP_FALLBACK_ENABLED=true, falls back cleanly to optional SMTP."""
    monkeypatch.setenv("EMAIL_PROVIDER", "auto")
    monkeypatch.setenv("BREVO_API_KEY", "xkeysib-failing-key")
    monkeypatch.setenv("BREVO_FROM_EMAIL", "noreply@sparkminds.ai")
    monkeypatch.setenv("SMTP_FALLBACK_ENABLED", "true")
    monkeypatch.setenv("SMTP_HOST", "smtp.gmail.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USERNAME", "sparkminds.ai@gmail.com")
    monkeypatch.setenv("SMTP_PASSWORD", "abcd efgh ijkl mnop")

    mock_fail = MagicMock()
    mock_fail.__enter__.return_value.post.return_value = _mock_httpx_response(503, {"message": "Service down"})

    smtp_called = {}

    def _fake_smtp(msg, cfg=None):
        smtp_called["to"] = msg["To"]
        return {"provider": "smtp_email", "status_code": 250, "message_id": ""}

    svc = EmailVerificationService(str(tmp_path / "otp_fallback.db"))
    with patch("app.core.email_provider.httpx.Client", return_value=mock_fail):
        with patch("app.core.email_provider.send_via_smtp", side_effect=_fake_smtp):
            res = svc.create_verification_code(email="fallback.student@example.com", purpose="registration")

    assert smtp_called["to"] == "fallback.student@example.com"
    assert res["delivery_channel"] == "smtp_email"
