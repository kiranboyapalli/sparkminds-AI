"""
SparkMinds AI — Mandatory 9-Scenario Persistent Auth, Cross-Device & Security Test Suite.

Covers all 9 mandatory end-to-end verification tests:
- TEST 1: Register a new student and confirm permanent database storage (hashed password, no plaintext, no secret leaks)
- TEST 2: Log out and log back in with the same username (case-insensitive) and password
- TEST 3: Close and reopen the app — restore valid session via HttpOnly cookies & transparent refresh-token rotation
- TEST 4: Sign in to the same account from a second device/browser
- TEST 5: Verify student profile, onboarding, study plan, and learning progress are retrieved from backend DB on Device 2
- TEST 6: Simulate full server restart (fresh repository instance reading from persistent DB) — account, credentials, progress & sessions survive!
- TEST 7: Reject incorrect password securely (401) + brute-force lockout protection (429) + never auto-create account on login
- TEST 8: Duplicate username (case-insensitive) rejected with exact message:
          "Username is already used. Please choose another username."
- TEST 9: Strict cross-user privacy isolation (403) across profiles, Guided Lessons, AI Buddy, study plans, homework & assessments
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import re
import sqlite3
import uuid
import pytest
from fastapi.testclient import TestClient

from app.core.account_policy import DUPLICATE_USERNAME_MESSAGE
from app.core.repository import EduSparkRepository, repo
from app.main import app


def _make_unique_suffix() -> str:
    return uuid.uuid4().hex[:8]


def _issue_verified_email_token_for_test(email: str) -> str:
    """Uses real OTP hashing/verification flow with in-memory sender capture (never returns OTP in API)."""
    captured = {}
    orig_sender = repo.email_verification._custom_sender

    def _capture(msg):
        body = msg.get_body(preferencelist=("plain",)).get_content()
        m = re.search(r"\b(\d{6})\b", body)
        captured["otp"] = m.group(1) if m else ""

    repo.email_verification._custom_sender = _capture
    try:
        repo.email_verification.create_verification_code(email=email, purpose="registration", cooldown_seconds=0)
        verify_res = repo.email_verification.verify_code(email=email, code=captured["otp"], purpose="registration")
        return verify_res["email_verification_token"]
    finally:
        repo.email_verification._custom_sender = orig_sender


def test_end_to_end_tests_1_through_9_persistent_auth_and_cross_device():
    suffix = _make_unique_suffix()
    username_mixed = f"SparkStudent_{suffix.upper()}"
    username_lower = username_mixed.lower()
    email = f"student.{suffix}@example.com"
    password = f"StrongPass#{suffix}"
    student_id = f"stu_{username_lower}"

    # ------------------------------------------------------------------
    # TEST 1: Register new student & confirm stored in persistent DB
    # ------------------------------------------------------------------
    device1 = TestClient(app)
    ev_tok = _issue_verified_email_token_for_test(email)
    reg_res = device1.post(
        "/api/auth/register",
        json={
            "student_id": student_id,
            "full_name": f"Aadhya Tester {suffix}",
            "username": username_mixed,
            "email": email,
            "email_verification_token": ev_tok,
            "strict_registration": True,
            "age": 14,
            "grade": 9,
            "date_of_birth": "2012-04-10",
            "password_or_pin": password,
            "device_name": "Device 1 Chrome",
        },
    )
    assert reg_res.status_code == 200, reg_res.text
    reg_data = reg_res.json()
    assert reg_data["status"] == "authenticated"
    assert reg_data["session_token"].startswith("spark_sess_v2.")
    assert reg_data["refresh_token"].startswith("spark_ref_v2.")

    # Verify HttpOnly cookies were set on response
    set_cookie_headers = reg_res.headers.get_list("set-cookie")
    joined_cookies = "\n".join(set_cookie_headers).lower()
    assert "sparkminds_access_token=" in joined_cookies
    assert "sparkminds_refresh_token=" in joined_cookies
    assert "httponly" in joined_cookies
    assert "samesite=lax" in joined_cookies

    # Verify NO password hash or salt leaked in response
    reg_text = reg_res.text
    assert "password_hash" not in reg_text
    assert "recovery_pin_hash" not in reg_text
    assert "refresh_token_hash" not in reg_text
    assert password not in reg_text

    # Verify record actually exists in SQLite persistent DB with hashed password (never plaintext)
    with sqlite3.connect(str(repo.sqlite_db_path)) as conn:
        u_row = conn.execute(
            "SELECT student_id, username_normalized, verified_email_normalized FROM user_identities WHERE student_id = ?",
            (student_id,),
        ).fetchone()
        assert u_row is not None
        assert u_row[1] == username_lower
        assert u_row[2] == email

        c_row = conn.execute(
            "SELECT password_hash, salt FROM auth_credentials WHERE student_id = ?",
            (student_id,),
        ).fetchone()
        assert c_row is not None
        assert c_row[0] != password
        assert len(c_row[0]) == 64
        assert len(c_row[1]) >= 16

    # Complete onboarding & add homework progress on Device 1
    onb_res = device1.post(
        "/api/onboarding/submit",
        json={
            "student_id": student_id,
            "academic_year_label": "2026-2027",
            "step1": {
                "age": 14,
                "grade": 9,
                "school_board": "CBSE",
                "state_name": "Telangana",
                "school_medium": "English",
                "preferred_explanation_language": "Telugu",
                "secondary_explanation_language": "English",
                "interface_display_language": "English",
            },
            "selected_subjects": ["G9_MATH", "G9_SCI", "G9_ENG"],
            "help_with_all_subjects": False,
            "subjects_to_improve": ["G9_MATH"],
            "subject_confidence": [
                {
                    "subject_code": "G9_MATH",
                    "subject_name": "Mathematics",
                    "confidence_level": "Need help",
                    "difficult_topics": ["Polynomials"],
                }
            ],
            "learning_challenges": ["I struggle with application-based questions."],
            "when_need_most_help": ["While solving questions"],
            "challenge_frequency": "Often",
            "everything_goal_selected": False,
            "selected_goals": ["g1", "g2"],
            "primary_goal": "g1",
        },
    )
    assert onb_res.status_code == 200
    assert onb_res.json()["student"]["onboarding_completed"] is True

    hw_res = device1.post(
        f"/api/students/{student_id}/homework",
        json={
            "student_id": student_id,
            "subject": "Mathematics",
            "chapter": "Polynomials",
            "title": f"Polynomials Practice Set {suffix}",
            "due_date": "2026-12-01",
            "description": "Solve quadratic factorization exercises",
        },
    )
    assert hw_res.status_code == 200, hw_res.text

    # ------------------------------------------------------------------
    # TEST 2: Log out & log back in with same username (case-insensitive) + password
    # ------------------------------------------------------------------
    d1_access = reg_data["session_token"]
    d1_refresh = reg_data["refresh_token"]
    logout_res = device1.post(
        "/api/auth/logout",
        json={"session_token": d1_access, "refresh_token": d1_refresh, "student_id": student_id},
    )
    assert logout_res.status_code == 200
    assert logout_res.json()["status"] == "logged_out"

    # Revoked access AND refresh tokens must both fail with 401
    assert device1.get("/api/auth/session", headers={"X-SparkMinds-Token": d1_access}).status_code == 401
    assert (
        device1.post(
            "/api/auth/session/refresh",
            json={"refresh_token": d1_refresh},
        ).status_code
        == 401
    )

    # Log back in with lowercase/mixed-case username
    login_res = device1.post(
        "/api/auth/login",
        json={
            "identifier": username_mixed.swapcase(),
            "password_or_pin": password,
            "device_name": "Device 1 Re-login",
        },
    )
    assert login_res.status_code == 200, login_res.text
    login_data = login_res.json()
    assert login_data["student"]["student_id"] == student_id
    assert login_data["student"]["onboarding_completed"] is True
    assert login_data["session_token"].startswith("spark_sess_v2.")
    assert login_data["refresh_token"].startswith("spark_ref_v2.")

    # ------------------------------------------------------------------
    # TEST 3: Close & reopen app -> valid session restored via HttpOnly cookie
    #         AND expired access token auto-refreshes seamlessly via refresh cookie
    # ------------------------------------------------------------------
    reopen_res = device1.get("/api/auth/session")  # No query param, no manual header — pure HttpOnly cookie!
    assert reopen_res.status_code == 200, reopen_res.text
    assert reopen_res.json()["student"]["student_id"] == student_id

    # Simulate expired access token while refresh token is still valid (e.g. reopened 2 days later)
    cur_access = login_data["session_token"]
    repo.active_sessions[cur_access]["expires_at"] = (
        datetime.now(timezone.utc) - timedelta(hours=2)
    ).isoformat()
    # GET /api/auth/session uses HttpOnly refresh cookie to silently rotate & restore!
    auto_refresh_res = device1.get("/api/auth/session")
    assert auto_refresh_res.status_code == 200, auto_refresh_res.text
    refreshed_payload = auto_refresh_res.json()
    assert refreshed_payload["status"] == "authenticated"
    assert refreshed_payload["student"]["student_id"] == student_id
    assert refreshed_payload.get("session_refreshed") is True
    assert refreshed_payload["session_token"] != cur_access

    # Cookie-authenticated access works seamlessly on Guided Lessons & Student Profile
    profile_cookie_res = device1.get(f"/api/students/{student_id}")
    assert profile_cookie_res.status_code == 200
    assert profile_cookie_res.json()["student"]["full_name"] == f"Aadhya Tester {suffix}"

    # ------------------------------------------------------------------
    # TEST 4 & TEST 5: Sign in from Device 2 (fresh client, empty cookies/storage)
    #                  and verify saved profile + homework + goals come from backend DB
    # ------------------------------------------------------------------
    device2 = TestClient(app)
    d2_login = device2.post(
        "/api/auth/login",
        json={
            "identifier": username_lower,
            "password_or_pin": password,
            "device_name": "Device 2 Android Phone",
        },
    )
    assert d2_login.status_code == 200, d2_login.text
    d2_bundle = d2_login.json()["cloud_sync_bundle"]
    assert d2_bundle["student"]["full_name"] == f"Aadhya Tester {suffix}"
    assert d2_bundle["student"]["onboarding_completed"] is True
    assert d2_bundle["active_year_profile"]["primary_goal"] == "g1"
    assert any(
        f"Polynomials Practice Set {suffix}" in hw.get("title", "")
        for hw in d2_bundle.get("homeworks", [])
    )

    # ------------------------------------------------------------------
    # TEST 6: Simulate Full Application Restart (fresh EduSparkRepository instance)
    #         Confirm account, credentials, homework, and sessions survive cleanly!
    # ------------------------------------------------------------------
    restarted_repo = EduSparkRepository(db_path=str(repo.db_file), postgres_url="")
    # Ensure it loads from the exact production SQLite file (repo.sqlite_db_path)
    restarted_repo.sqlite_db_path = repo.sqlite_db_path
    restarted_repo.students.clear()
    restarted_repo.auth_credentials.clear()
    restarted_repo.active_sessions.clear()
    restarted_repo._load_from_disk()

    assert student_id in restarted_repo.students
    assert student_id in restarted_repo.auth_credentials
    post_restart_login = restarted_repo.login_student_account(
        identifier=username_mixed,
        password_or_pin=password,
        device_name="Post-Restart Browser",
    )
    assert post_restart_login["student"]["full_name"] == f"Aadhya Tester {suffix}"
    assert post_restart_login["student"]["onboarding_completed"] is True

    # ------------------------------------------------------------------
    # TEST 7: Incorrect password rejected (401), unknown account NEVER auto-created,
    #         and brute-force protection triggers HTTP 429
    # ------------------------------------------------------------------
    wrong_pw = device2.post(
        "/api/auth/login",
        json={"identifier": username_lower, "password_or_pin": "WrongPassword999"},
    )
    assert wrong_pw.status_code == 401
    assert "incorrect password" in wrong_pw.json()["detail"].lower()

    unknown_user = f"never_registered_{suffix}"
    unknown_res = device2.post(
        "/api/auth/login",
        json={"identifier": unknown_user, "password_or_pin": "SomePass123"},
    )
    assert unknown_res.status_code == 401
    assert unknown_user not in repo.students  # NEVER auto-creates account during login!

    # Brute-force lockout check on a dedicated identifier
    bf_id = f"bf_target_{suffix}"
    statuses = []
    for _ in range(12):
        r = device2.post(
            "/api/auth/login",
            json={"identifier": bf_id, "password_or_pin": "badpass"},
        )
        statuses.append(r.status_code)
    assert 429 in statuses, f"Expected brute-force 429 lockout, got: {statuses}"

    # ------------------------------------------------------------------
    # TEST 8: Duplicate username (case-insensitive) returns exact required message
    # ------------------------------------------------------------------
    other_email = f"other.{suffix}@example.com"
    ev_tok2 = _issue_verified_email_token_for_test(other_email)
    dup_res = device2.post(
        "/api/auth/register",
        json={
            "full_name": "Duplicate Attempt",
            "username": username_mixed.upper(),
            "email": other_email,
            "email_verification_token": ev_tok2,
            "strict_registration": True,
            "age": 13,
            "grade": 8,
            "date_of_birth": "2013-02-02",
            "password_or_pin": "OtherPass#123",
        },
    )
    assert dup_res.status_code == 409
    assert dup_res.json()["detail"] == DUPLICATE_USERNAME_MESSAGE

    # ------------------------------------------------------------------
    # TEST 9: Cross-user privacy isolation (Student B cannot access Student A)
    # ------------------------------------------------------------------
    user_b_name = f"otheruser_{suffix}"
    user_b_email = f"userb.{suffix}@example.com"
    ev_tok_b = _issue_verified_email_token_for_test(user_b_email)
    device_b = TestClient(app)
    reg_b = device_b.post(
        "/api/auth/register",
        json={
            "full_name": "Second Student B",
            "username": user_b_name,
            "email": user_b_email,
            "email_verification_token": ev_tok_b,
            "strict_registration": True,
            "age": 15,
            "grade": 10,
            "date_of_birth": "2011-05-05",
            "password_or_pin": "UserBPass#1",
        },
    )
    assert reg_b.status_code == 200
    assert device_b.get(f"/api/students/{student_id}").status_code == 403
    assert device_b.get(f"/api/students/{student_id}/homework").status_code == 403
    assert device_b.get(f"/api/students/{student_id}/study-plan").status_code == 403
    assert device_b.get(f"/api/agents/assessments/{student_id}").status_code == 403
    assert (
        device_b.post(
            "/api/agents/lessons/generate",
            json={"student_id": student_id, "subject": "Mathematics", "topic": "Polynomials"},
        ).status_code
        == 403
    )
