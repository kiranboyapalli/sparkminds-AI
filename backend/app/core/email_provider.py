"""
SparkMinds AI — Production HTTPS Transactional Email Provider Layer
(Brevo HTTPS API, Resend HTTPS API, and Optional Gmail SMTP Fallback).

Why HTTPS APIs (port 443):
- Railway Free, Trial, and Hobby plans block outbound SMTP ports (25, 465, 587, 2525),
  causing `OSError errno=101 (Network is unreachable)` / connection timeouts.
- HTTPS port 443 is unrestricted on all Railway plans and provides fast, reliable
  transactional email delivery with structured provider error handling.

Security Invariants:
- Reads all API keys, sender settings, and SMTP credentials strictly from environment variables.
- NEVER hardcodes secrets and NEVER logs API keys, passwords, OTP values, or email contents.
- Keeps Gmail SMTP as an optional fallback ONLY when outbound SMTP is supported.
"""

from __future__ import annotations

from email.message import EmailMessage
from email.utils import formataddr
import logging
import os
import re
import smtplib
import socket
import ssl
from typing import Any, Dict, List, Optional, Tuple

import httpx

logger = logging.getLogger("sparkminds.email_transport")

GMAIL_APP_PASSWORD_SPACED_PATTERN = re.compile(r"^[A-Za-z0-9]{4}( [A-Za-z0-9]{4}){3}$")

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"
RESEND_API_URL = "https://api.resend.com/emails"
HTTPS_TIMEOUT_SECONDS = 15.0
SMTP_TIMEOUT_SECONDS = 12.0


class EmailTransportDeliveryError(RuntimeError):
    """Raised when the active transactional email provider cannot deliver an email."""


class EmailTransportRecipientError(ValueError):
    """Raised when the provider rejects the recipient email address."""


def load_smtp_config() -> Dict[str, Any]:
    """
    Load optional Gmail/custom SMTP configuration strictly from environment variables.
    Supports both canonical underscore names (SMTP_FROM_EMAIL, SMTP_FROM_NAME)
    and space-separated fallbacks if entered with spaces in a hosting dashboard.
    Never logs or exposes SMTP_PASSWORD.
    """
    smtp_host = os.getenv("SMTP_HOST", "").strip()
    port_raw = os.getenv("SMTP_PORT", "587").strip()
    try:
        smtp_port = int(port_raw) if port_raw else 587
    except ValueError:
        smtp_port = 587

    smtp_username = (
        os.getenv("SMTP_USERNAME", "").strip()
        or os.getenv("SMTP_USER", "").strip()
    )
    raw_password = os.getenv("SMTP_PASSWORD", "").strip()
    if (
        smtp_host.lower() == "smtp.gmail.com"
        and GMAIL_APP_PASSWORD_SPACED_PATTERN.match(raw_password)
    ):
        smtp_password = raw_password.replace(" ", "")
    else:
        smtp_password = raw_password

    smtp_from_email = (
        os.getenv("SMTP_FROM_EMAIL", "").strip()
        or os.getenv("SMTP_FROM EMAIL", "").strip()
        or os.getenv("SMTP_FROM", "").strip()
        or smtp_username
    )
    smtp_from_name = (
        os.getenv("SMTP_FROM_NAME", "").strip()
        or os.getenv("SMTP_FROM NAME", "").strip()
        or "SparkMinds AI"
    )

    return {
        "host": smtp_host,
        "port": smtp_port,
        "username": smtp_username,
        "password": smtp_password,
        "from_email": smtp_from_email,
        "from_name": smtp_from_name,
    }


def load_email_provider_config() -> Dict[str, Any]:
    """
    Resolve active transactional email provider configuration strictly from env vars.

    Environment variables supported:
    - EMAIL_PROVIDER: "auto" (default) | "brevo" | "resend" | "smtp"
    - BREVO_API_KEY, BREVO_SENDER_EMAIL, BREVO_SENDER_NAME (also supports BREVO_FROM_EMAIL / BREVO_FROM_NAME)
    - RESEND_API_KEY, RESEND_FROM_EMAIL, RESEND_FROM_NAME
    - EMAIL_FROM_EMAIL, EMAIL_FROM_NAME, EMAIL_REPLY_TO
    - SMTP_FALLBACK_ENABLED: "true" | "false" (optional fallback if HTTPS provider unavailable)
    - SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM_EMAIL, SMTP_FROM_NAME
    """
    smtp_cfg = load_smtp_config()
    requested = (os.getenv("EMAIL_PROVIDER", "auto") or "auto").strip().lower()
    if requested not in ("auto", "brevo", "resend", "smtp"):
        requested = "auto"

    brevo_api_key = os.getenv("BREVO_API_KEY", "").strip()
    resend_api_key = os.getenv("RESEND_API_KEY", "").strip()

    shared_from_email = (
        os.getenv("EMAIL_FROM_EMAIL", "").strip()
        or os.getenv("EMAIL_FROM", "").strip()
        or smtp_cfg["from_email"]
    )
    shared_from_name = (
        os.getenv("EMAIL_FROM_NAME", "").strip()
        or smtp_cfg["from_name"]
        or "SparkMinds AI"
    )
    reply_to = os.getenv("EMAIL_REPLY_TO", "").strip()

    brevo_from_email = (
        os.getenv("BREVO_SENDER_EMAIL", "").strip()
        or os.getenv("BREVO_SENDER EMAIL", "").strip()
        or os.getenv("BREVO_FROM_EMAIL", "").strip()
        or shared_from_email
    )
    brevo_from_name = (
        os.getenv("BREVO_SENDER_NAME", "").strip()
        or os.getenv("BREVO_SENDER NAME", "").strip()
        or os.getenv("BREVO_FROM_NAME", "").strip()
        or shared_from_name
    )

    resend_from_email = (
        os.getenv("RESEND_SENDER_EMAIL", "").strip()
        or os.getenv("RESEND_FROM_EMAIL", "").strip()
        or shared_from_email
    )
    resend_from_name = (
        os.getenv("RESEND_SENDER_NAME", "").strip()
        or os.getenv("RESEND_FROM_NAME", "").strip()
        or shared_from_name
    )

    smtp_configured = bool(smtp_cfg["host"] and smtp_cfg["username"] and smtp_cfg["password"])
    smtp_fallback_enabled = (
        os.getenv("SMTP_FALLBACK_ENABLED", "false").strip().lower() in ("1", "true", "yes")
    )

    if requested == "brevo":
        active_provider = "brevo"
    elif requested == "resend":
        active_provider = "resend"
    elif requested == "smtp":
        active_provider = "smtp"
    else:
        # Auto mode: prefer HTTPS API providers (never blocked on Railway) over SMTP
        if brevo_api_key:
            active_provider = "brevo"
        elif resend_api_key:
            active_provider = "resend"
        else:
            active_provider = "smtp"

    if active_provider == "brevo":
        active_from_email = brevo_from_email
        active_from_name = brevo_from_name
    elif active_provider == "resend":
        active_from_email = resend_from_email
        active_from_name = resend_from_name
    else:
        active_from_email = smtp_cfg["from_email"] or shared_from_email
        active_from_name = smtp_cfg["from_name"] or shared_from_name

    return {
        "requested_provider": requested,
        "active_provider": active_provider,
        "brevo_api_key": brevo_api_key,
        "brevo_configured": bool(brevo_api_key),
        "brevo_from_email": brevo_from_email,
        "brevo_from_name": brevo_from_name,
        "resend_api_key": resend_api_key,
        "resend_configured": bool(resend_api_key),
        "resend_from_email": resend_from_email,
        "resend_from_name": resend_from_name,
        "https_api_configured": bool(brevo_api_key or resend_api_key),
        "smtp_configured": smtp_configured,
        "smtp_fallback_enabled": smtp_fallback_enabled,
        "smtp": smtp_cfg,
        "from_email": active_from_email or "no-reply@sparkminds.ai",
        "from_name": active_from_name or "SparkMinds AI",
        "reply_to": reply_to,
    }


def _extract_parts_from_email_message(msg: EmailMessage) -> Tuple[str, str, str, str]:
    """Extracts (to_email, subject, plain_text, html_content) cleanly from an EmailMessage."""
    to_email = str(msg["To"] or "").strip()
    subject = str(msg["Subject"] or "SparkMinds AI — Email Verification").strip()
    plain_part = msg.get_body(preferencelist=("plain",))
    html_part = msg.get_body(preferencelist=("html",))
    plain_text = plain_part.get_content() if plain_part is not None else ""
    html_content = html_part.get_content() if html_part is not None else ""
    return to_email, subject, str(plain_text), str(html_content)


def send_via_brevo_https(
    msg: EmailMessage,
    *,
    api_key: str,
    from_email: str,
    from_name: str,
    reply_to: str = "",
) -> Dict[str, Any]:
    """
    Delivers a transactional email over HTTPS (port 443) via Brevo REST API v3.
    Never logs API keys, OTP codes, or email body contents.
    """
    if not api_key:
        raise EmailTransportDeliveryError(
            "Brevo email API key is not configured. Set BREVO_API_KEY in environment variables."
        )
    if not from_email:
        raise EmailTransportDeliveryError(
            "Brevo sender email is not configured. Set BREVO_SENDER_EMAIL in environment variables."
        )

    to_email, subject, plain_text, html_content = _extract_parts_from_email_message(msg)
    payload: Dict[str, Any] = {
        "sender": {"name": from_name or "SparkMinds AI", "email": from_email},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": plain_text,
    }
    if html_content:
        payload["htmlContent"] = html_content
    if reply_to:
        payload["replyTo"] = {"email": reply_to, "name": from_name or "SparkMinds AI"}

    try:
        with httpx.Client(timeout=HTTPS_TIMEOUT_SECONDS) as client:
            resp = client.post(
                BREVO_API_URL,
                headers={
                    "api-key": api_key,
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                json=payload,
            )
    except httpx.HTTPError as exc:
        logger.error("Brevo HTTPS transport error type=%s", type(exc).__name__)
        raise EmailTransportDeliveryError(
            "Could not reach the email delivery service right now. Please try again in a moment."
        ) from exc

    if 200 <= resp.status_code < 300:
        data = {}
        try:
            data = resp.json()
        except Exception:
            data = {}
        msg_id = str(data.get("messageId") or "")
        logger.info("Brevo HTTPS email accepted status=%s message_id=%s", resp.status_code, msg_id or "ok")
        return {"provider": "brevo_https", "status_code": resp.status_code, "message_id": msg_id}

    if resp.status_code in (401, 403):
        logger.error("Brevo HTTPS API rejected authentication/authorization status=%s", resp.status_code)
        raise EmailTransportDeliveryError(
            "Email service authentication failed. Please verify the configured email provider API key and sender."
        )
    if resp.status_code == 400:
        # Distinguish invalid recipient vs unverified sender without leaking secrets
        err_code = ""
        try:
            err_code = str((resp.json() or {}).get("code") or "")
        except Exception:
            err_code = ""
        body_lower = (resp.text or "").lower()
        logger.warning("Brevo HTTPS API returned 400 Bad Request code=%s", err_code or "bad_request")
        if "invalid" in body_lower and "to" in body_lower:
            raise EmailTransportRecipientError(
                "This email address could not receive mail. Please check the spelling and try again."
            )
        raise EmailTransportDeliveryError(
            "Email sender configuration was rejected by the email provider. Please verify the sender address."
        )
    if resp.status_code == 429:
        logger.warning("Brevo HTTPS API rate limit exceeded status=429")
        raise EmailTransportDeliveryError(
            "Email delivery service is temporarily busy. Please try again in a minute."
        )

    logger.error("Brevo HTTPS API delivery failed status=%s", resp.status_code)
    raise EmailTransportDeliveryError(
        "Could not deliver the verification email right now. Please try again in a moment."
    )


def send_via_resend_https(
    msg: EmailMessage,
    *,
    api_key: str,
    from_email: str,
    from_name: str,
    reply_to: str = "",
) -> Dict[str, Any]:
    """
    Delivers a transactional email over HTTPS (port 443) via Resend REST API.
    Never logs API keys, OTP codes, or email body contents.
    """
    if not api_key:
        raise EmailTransportDeliveryError(
            "Resend email API key is not configured. Set RESEND_API_KEY in environment variables."
        )
    if not from_email:
        raise EmailTransportDeliveryError(
            "Resend sender email is not configured. Set RESEND_FROM_EMAIL or EMAIL_FROM_EMAIL."
        )

    to_email, subject, plain_text, html_content = _extract_parts_from_email_message(msg)
    formatted_from = (
        from_email
        if ("<" in from_email and ">" in from_email)
        else formataddr((from_name or "SparkMinds AI", from_email))
    )
    payload: Dict[str, Any] = {
        "from": formatted_from,
        "to": [to_email],
        "subject": subject,
        "text": plain_text,
    }
    if html_content:
        payload["html"] = html_content
    if reply_to:
        payload["reply_to"] = reply_to

    try:
        with httpx.Client(timeout=HTTPS_TIMEOUT_SECONDS) as client:
            resp = client.post(
                RESEND_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                json=payload,
            )
    except httpx.HTTPError as exc:
        logger.error("Resend HTTPS transport error type=%s", type(exc).__name__)
        raise EmailTransportDeliveryError(
            "Could not reach the email delivery service right now. Please try again in a moment."
        ) from exc

    if 200 <= resp.status_code < 300:
        data = {}
        try:
            data = resp.json()
        except Exception:
            data = {}
        msg_id = str(data.get("id") or "")
        logger.info("Resend HTTPS email accepted status=%s message_id=%s", resp.status_code, msg_id or "ok")
        return {"provider": "resend_https", "status_code": resp.status_code, "message_id": msg_id}

    if resp.status_code in (401, 403):
        logger.error("Resend HTTPS API rejected authentication/domain status=%s", resp.status_code)
        raise EmailTransportDeliveryError(
            "Email service authentication or sender domain verification failed. Please check RESEND_API_KEY and verified domain."
        )
    if resp.status_code == 422:
        logger.warning("Resend HTTPS API rejected request payload status=422")
        raise EmailTransportRecipientError(
            "This email address could not receive mail. Please check the spelling and try again."
        )
    if resp.status_code == 429:
        logger.warning("Resend HTTPS API rate limit exceeded status=429")
        raise EmailTransportDeliveryError(
            "Email delivery service is temporarily busy. Please try again in a minute."
        )

    logger.error("Resend HTTPS API delivery failed status=%s", resp.status_code)
    raise EmailTransportDeliveryError(
        "Could not deliver the verification email right now. Please try again in a moment."
    )


def _open_smtp_connection(host: str, port: int, ssl_context: ssl.SSLContext):
    """
    Opens SMTP / SMTP_SSL using standard smtplib first (preserving mockability and TLS SNI),
    falling back to an explicit IPv4 (AF_INET) socket if IPv6 egress returns ENETUNREACH.
    """
    try:
        if port == 465:
            return smtplib.SMTP_SSL(host, port, timeout=SMTP_TIMEOUT_SECONDS, context=ssl_context)
        return smtplib.SMTP(host, port, timeout=SMTP_TIMEOUT_SECONDS)
    except OSError as exc:
        if getattr(exc, "errno", None) != 101:
            raise
        # Explicit IPv4 fallback when container disables IPv6 egress (ipv6EgressEnabled=false)
        infos = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
        if not infos:
            raise
        ipv4_addr = str(infos[0][4][0])
        if port == 465:
            server = smtplib.SMTP_SSL(timeout=SMTP_TIMEOUT_SECONDS, context=ssl_context)
            server._host = host  # type: ignore[attr-defined]
            raw_sock = socket.create_connection((ipv4_addr, port), timeout=SMTP_TIMEOUT_SECONDS)
            server.sock = ssl_context.wrap_socket(raw_sock, server_hostname=host)
            server.file = server.sock.makefile("rb")
            code, resp = server.getreply()
            if code != 220:
                server.close()
                raise smtplib.SMTPConnectError(code, resp)
            return server
        server = smtplib.SMTP(timeout=SMTP_TIMEOUT_SECONDS)
        server._host = host  # type: ignore[attr-defined]
        server.sock = socket.create_connection((ipv4_addr, port), timeout=SMTP_TIMEOUT_SECONDS)
        server.file = server.sock.makefile("rb")
        code, resp = server.getreply()
        if code != 220:
            server.close()
            raise smtplib.SMTPConnectError(code, resp)
        return server


def send_via_smtp(msg: EmailMessage, cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Optional Gmail / custom SMTP delivery (port 587 STARTTLS or port 465 SSL).
    Only succeeds on hosts that allow outbound SMTP traffic (e.g. local dev or Railway Pro+).
    Never logs SMTP_PASSWORD or email OTP content.
    """
    smtp_cfg = cfg if cfg is not None else load_smtp_config()
    if not smtp_cfg["host"] or not smtp_cfg["username"] or not smtp_cfg["password"]:
        logger.error("SMTP email delivery failed: SMTP environment variables are incomplete.")
        raise EmailTransportDeliveryError(
            "Email verification service is temporarily unavailable. Please try again later."
        )

    ssl_context = ssl.create_default_context()
    try:
        if smtp_cfg["port"] == 465:
            with _open_smtp_connection(smtp_cfg["host"], 465, ssl_context) as server:
                server.ehlo()
                server.login(smtp_cfg["username"], smtp_cfg["password"])
                server.send_message(msg)
        else:
            with _open_smtp_connection(smtp_cfg["host"], smtp_cfg["port"], ssl_context) as server:
                server.ehlo()
                server.starttls(context=ssl_context)
                server.ehlo()
                server.login(smtp_cfg["username"], smtp_cfg["password"])
                server.send_message(msg)
        return {"provider": "smtp_email", "status_code": 250, "message_id": ""}
    except smtplib.SMTPAuthenticationError as exc:
        logger.error("SMTP authentication failed against host=%s port=%s", smtp_cfg["host"], smtp_cfg["port"])
        raise EmailTransportDeliveryError(
            "Unable to send verification email due to mail server authentication failure. Please contact support."
        ) from exc
    except smtplib.SMTPRecipientsRefused as exc:
        logger.warning("SMTP recipient refused for host=%s", smtp_cfg["host"])
        raise EmailTransportRecipientError(
            "This email address could not receive mail. Please check the spelling and try again."
        ) from exc
    except (smtplib.SMTPException, OSError, TimeoutError) as exc:
        errno_val = getattr(exc, "errno", None)
        logger.error(
            "SMTP transport error on host=%s port=%s type=%s errno=%s (outbound SMTP may be blocked by hosting plan; configure BREVO_API_KEY or RESEND_API_KEY for HTTPS port-443 delivery)",
            smtp_cfg["host"],
            smtp_cfg["port"],
            type(exc).__name__,
            errno_val,
        )
        raise EmailTransportDeliveryError(
            "Could not deliver the verification email right now. Please try again in a moment."
        ) from exc


def dispatch_transactional_email(msg: EmailMessage) -> Dict[str, Any]:
    """
    Routes outbound transactional email to the configured HTTPS API provider
    (Brevo or Resend over port 443), keeping Gmail SMTP as an optional fallback
    only when configured/supported.
    """
    cfg = load_email_provider_config()
    provider = cfg["active_provider"]

    if provider == "brevo":
        try:
            return send_via_brevo_https(
                msg,
                api_key=cfg["brevo_api_key"],
                from_email=cfg["brevo_from_email"],
                from_name=cfg["brevo_from_name"],
                reply_to=cfg["reply_to"],
            )
        except EmailTransportDeliveryError:
            if cfg["smtp_fallback_enabled"] and cfg["smtp_configured"]:
                logger.warning("Brevo HTTPS failed; attempting optional SMTP fallback.")
                return send_via_smtp(msg, cfg["smtp"])
            raise

    if provider == "resend":
        try:
            return send_via_resend_https(
                msg,
                api_key=cfg["resend_api_key"],
                from_email=cfg["resend_from_email"],
                from_name=cfg["resend_from_name"],
                reply_to=cfg["reply_to"],
            )
        except EmailTransportDeliveryError:
            if cfg["smtp_fallback_enabled"] and cfg["smtp_configured"]:
                logger.warning("Resend HTTPS failed; attempting optional SMTP fallback.")
                return send_via_smtp(msg, cfg["smtp"])
            raise

    return send_via_smtp(msg, cfg["smtp"])


def _probe_tcp(host: str, port: int, family: int, timeout: float = 2.5) -> Dict[str, Any]:
    """Fixed-target TCP reachability probe used strictly for startup email networking diagnostics."""
    try:
        infos = socket.getaddrinfo(host, port, family, socket.SOCK_STREAM)
    except OSError as exc:
        return {"reachable": False, "error": type(exc).__name__, "errno": getattr(exc, "errno", None)}
    if not infos:
        return {"reachable": False, "error": "no_dns_records", "errno": None}
    sockaddr = infos[0][4]
    s = socket.socket(family, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect(sockaddr)
        return {"reachable": True, "error": None, "errno": None}
    except OSError as exc:
        return {"reachable": False, "error": type(exc).__name__, "errno": getattr(exc, "errno", None)}
    finally:
        try:
            s.close()
        except Exception:
            pass


_CACHED_CONNECTIVITY_PROBE: Optional[Dict[str, Any]] = None


def probe_email_network_connectivity(force_refresh: bool = False) -> Dict[str, Any]:
    """
    Safely probes ONLY hardcoded well-known email endpoints (zero user-controlled hosts)
    to diagnose whether outbound SMTP (ports 587/465) is blocked vs HTTPS APIs (port 443).
    """
    global _CACHED_CONNECTIVITY_PROBE
    if _CACHED_CONNECTIVITY_PROBE is not None and not force_refresh:
        return _CACHED_CONNECTIVITY_PROBE

    result = {
        "smtp_gmail_587_ipv4": _probe_tcp("smtp.gmail.com", 587, socket.AF_INET),
        "smtp_gmail_587_ipv6": _probe_tcp("smtp.gmail.com", 587, socket.AF_INET6),
        "smtp_gmail_465_ipv4": _probe_tcp("smtp.gmail.com", 465, socket.AF_INET),
        "smtp_gmail_465_ipv6": _probe_tcp("smtp.gmail.com", 465, socket.AF_INET6),
        "brevo_https_443_ipv4": _probe_tcp("api.brevo.com", 443, socket.AF_INET),
        "resend_https_443_ipv4": _probe_tcp("api.resend.com", 443, socket.AF_INET),
    }
    _CACHED_CONNECTIVITY_PROBE = result
    return result


def get_email_service_health_summary(include_probe: bool = False) -> Dict[str, Any]:
    """Returns non-sensitive email transport readiness metadata for /api/health."""
    cfg = load_email_provider_config()
    summary: Dict[str, Any] = {
        "active_provider": cfg["active_provider"],
        "https_api_configured": cfg["https_api_configured"],
        "brevo_configured": cfg["brevo_configured"],
        "brevo_sender_configured": bool(cfg["brevo_from_email"]),
        "resend_configured": cfg["resend_configured"],
        "smtp_fallback_configured": cfg["smtp_configured"],
        "smtp_fallback_enabled": cfg["smtp_fallback_enabled"],
    }
    if include_probe:
        summary["network_probe"] = probe_email_network_connectivity()
    return summary
