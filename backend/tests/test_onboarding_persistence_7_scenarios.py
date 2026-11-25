"""
Comprehensive verification of per-student onboarding completion persistence
across all 7 required user scenarios + backward-compatible existing-student safety.
Uses an isolated temporary repository so local student records are never modified.
"""
import json
from pathlib import Path
import re
from unittest.mock import patch
from fastapi.testclient import TestClient

import app.main as main_mod
import app.routers.api_router as api_router_mod
import app.routers.ecosystem_router as eco_router_mod
from app.core.repository import EduSparkRepository


def _build_isolated_client(tmp_db_file: Path):
    isolated_repo = EduSparkRepository(db_path=str(tmp_db_file), postgres_url="")
    p1 = patch.object(main_mod, "repo", isolated_repo)
    p2 = patch.object(api_router_mod, "repo", isolated_repo)
    p3 = patch.object(eco_router_mod, "repo", isolated_repo)
    p1.start()
    p2.start()
    p3.start()
    client = TestClient(main_mod.app)
    return client, isolated_repo, (p1, p2, p3)


def _register_verified_student(
    client: TestClient,
    repo: EduSparkRepository,
    *,
    full_name: str,
    username: str,
    email: str,
    password: str = "Spark#2026",
    age: int = 13,
    grade: int = 8,
    school_board: str = "CBSE",
):
    captured = {}
    orig_sender = repo.email_verification._custom_sender

    def _capture(msg):
        body = msg.get_body(preferencelist=("plain",)).get_content()
        m = re.search(r"\b(\d{6})\b", body)
        captured["otp"] = m.group(1) if m else ""

    repo.email_verification._custom_sender = _capture
    try:
        repo.email_verification.create_verification_code(
            email=email, purpose="registration", cooldown_seconds=0
        )
        verify_res = repo.email_verification.verify_code(
            email=email, code=captured["otp"], purpose="registration"
        )
        ver_token = verify_res["email_verification_token"]
    finally:
        repo.email_verification._custom_sender = orig_sender

    student_id = f"stu_{username.lower()}"
    res = client.post(
        "/api/auth/register",
        json={
            "student_id": student_id,
            "full_name": full_name,
            "username": username,
            "email": email,
            "email_verification_token": ver_token,
            "strict_registration": True,
            "age": age,
            "grade": grade,
            "school_board": school_board,
            "date_of_birth": "2013-06-15",
            "email_or_username": email,
            "password_or_pin": password,
            "device_name": "Laptop Browser (Device 1)",
        },
    )
    assert res.status_code == 200, res.text
    return res.json()


def test_all_7_onboarding_scenarios_end_to_end(tmp_path: Path):
    db_file = tmp_path / "isolated_onboarding_db.json"
    client, repo, patches = _build_isolated_client(db_file)
    try:
        # ------------------------------------------------------------------
        # SCENARIO 1: New student registers / logs in -> onboarding appears
        # ------------------------------------------------------------------
        reg_a = _register_verified_student(
            client,
            repo,
            full_name="Meera Krishnan",
            username="meera_k8",
            email="meera.k8@example.com",
            age=13,
            grade=8,
            school_board="ICSE",
        )
        sid_a = reg_a["student"]["student_id"]
        tok_a1 = reg_a["session_token"]
        assert reg_a["student"]["onboarding_completed"] is False
        assert reg_a["student"]["school_board"] == "ICSE"
        assert reg_a["cloud_sync_bundle"]["student"]["onboarding_completed"] is False

        # Login before completing onboarding -> onboarding still required
        login_before = client.post(
            "/api/auth/login",
            json={
                "identifier": "meera_k8",
                "password_or_pin": "Spark#2026",
                "device_name": "Laptop Browser (Device 1)",
            },
        )
        assert login_before.status_code == 200
        assert login_before.json()["student"]["onboarding_completed"] is False
        tok_a1 = login_before.json()["session_token"]

        # ------------------------------------------------------------------
        # SCENARIO 2: Student completes onboarding -> saved in database
        # ------------------------------------------------------------------
        onb_payload = {
            "student_id": sid_a,
            "academic_year_label": "2026-2027",
            "step1": {
                "age": 13,
                "grade": 8,
                "school_board": "ICSE",
                "state_name": "Karnataka",
                "other_board_text": None,
                "school_medium": "English",
                "preferred_explanation_language": "Kannada",
                "secondary_explanation_language": "English",
                "interface_display_language": "English",
            },
            "selected_subjects": ["G8_MATH", "G8_PHY", "G8_CHEM", "G8_ENG"],
            "help_with_all_subjects": False,
            "subjects_to_improve": ["G8_MATH", "G8_PHY"],
            "subject_confidence": [
                {
                    "subject_code": "G8_MATH",
                    "subject_name": "Mathematics",
                    "confidence_level": "Need help",
                    "difficult_topics": ["Linear Equations"],
                },
                {
                    "subject_code": "G8_PHY",
                    "subject_name": "Physics",
                    "confidence_level": "Okay",
                    "difficult_topics": [],
                },
            ],
            "main_improvement_priority": "Understand difficult concepts",
            "learning_challenges": ["I don't understand some concepts."],
            "when_need_most_help": ["While understanding concepts"],
            "challenge_frequency": "Often",
            "everything_goal_selected": True,
            "selected_goals": ["g1"],
            "primary_goal": "g1",
        }
        onb_res = client.post(
            "/api/onboarding/submit",
            headers={"Authorization": f"Bearer {tok_a1}"},
            json=onb_payload,
        )
        assert onb_res.status_code == 200, onb_res.text
        onb_data = onb_res.json()
        assert onb_data["status"] == "onboarding_saved"
        assert onb_data["student"]["onboarding_completed"] is True
        assert onb_data["cloud_sync_bundle"]["student"]["onboarding_completed"] is True
        assert repo.students[sid_a]["onboarding_completed"] is True

        # Verify persisted on disk in JSON/SQLite snapshot
        disk_raw = json.loads(db_file.read_text(encoding="utf-8"))
        assert disk_raw["students"][sid_a]["onboarding_completed"] is True

        # ------------------------------------------------------------------
        # SCENARIO 4: Browser refresh (GET /api/auth/session) -> stays True
        # ------------------------------------------------------------------
        refresh_check = client.get(
            "/api/auth/session",
            headers={"Authorization": f"Bearer {tok_a1}"},
        )
        assert refresh_check.status_code == 200
        assert refresh_check.json()["student"]["onboarding_completed"] is True
        assert refresh_check.json()["cloud_sync_bundle"]["student"]["onboarding_completed"] is True

        # ------------------------------------------------------------------
        # SCENARIO 3: Logout and log back in -> onboarding_completed stays True
        # ------------------------------------------------------------------
        client.cookies.clear()
        logout_res = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {tok_a1}"},
            json={"session_token": tok_a1, "student_id": sid_a},
        )
        assert logout_res.status_code == 200
        # Logout MUST NEVER reset onboarding_completed in the database
        assert repo.students[sid_a]["onboarding_completed"] is True

        relogin_res = client.post(
            "/api/auth/login",
            json={
                "identifier": "meera.k8@example.com",
                "password_or_pin": "Spark#2026",
                "device_name": "Laptop Browser (Device 1)",
            },
        )
        assert relogin_res.status_code == 200
        assert relogin_res.json()["student"]["onboarding_completed"] is True
        assert relogin_res.json()["cloud_sync_bundle"]["student"]["onboarding_completed"] is True

        # ------------------------------------------------------------------
        # SCENARIO 5: Login on another device (and across server restart)
        # ------------------------------------------------------------------
        for p in patches:
            p.stop()
        client2, repo2, patches = _build_isolated_client(db_file)
        device2_login = client2.post(
            "/api/auth/login",
            json={
                "identifier": "MEERA_K8",  # case-insensitive username on new device
                "password_or_pin": "Spark#2026",
                "device_name": "Android Phone / Tablet (Device 2)",
            },
        )
        assert device2_login.status_code == 200
        d2_data = device2_login.json()
        assert d2_data["student"]["student_id"] == sid_a
        assert d2_data["student"]["onboarding_completed"] is True
        assert d2_data["student"]["language_preferences"]["preferred_explanation_language"] == "Kannada"

        # ------------------------------------------------------------------
        # SCENARIO 6 & 7: Different new student logs in -> independent False,
        # and incomplete onboarding continues to appear across refresh & relogin
        # ------------------------------------------------------------------
        client2.cookies.clear()
        reg_b = _register_verified_student(
            client2,
            repo2,
            full_name="Rohan Deshmukh",
            username="rohan_d9",
            email="rohan.d9@example.com",
            age=14,
            grade=9,
            school_board="CBSE",
        )
        sid_b = reg_b["student"]["student_id"]
        tok_b = reg_b["session_token"]
        assert reg_b["student"]["onboarding_completed"] is False
        # Student A's completed status remains completely untouched
        assert repo2.students[sid_a]["onboarding_completed"] is True

        # Student B refreshes browser WITHOUT completing onboarding -> still False
        sess_b = client2.get(
            "/api/auth/session",
            headers={"Authorization": f"Bearer {tok_b}"},
        )
        assert sess_b.status_code == 200
        assert sess_b.json()["student"]["onboarding_completed"] is False

        # Student B logs out and logs back in WITHOUT completing onboarding -> still False
        client2.cookies.clear()
        client2.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {tok_b}"},
            json={"session_token": tok_b, "student_id": sid_b},
        )
        relogin_b = client2.post(
            "/api/auth/login",
            json={
                "identifier": "rohan_d9",
                "password_or_pin": "Spark#2026",
                "device_name": "iPad Safari",
            },
        )
        assert relogin_b.status_code == 200
        assert relogin_b.json()["student"]["onboarding_completed"] is False
    finally:
        for p in patches:
            p.stop()


def test_backward_compatible_existing_student_verification(tmp_path: Path):
    """
    Verifies that existing students with genuine completed AcademicYearProfile records
    are recognized as completed even if a legacy flag was False, while existing accounts
    with NO completed onboarding profile stay False (never blindly marking everyone True).
    """
    db_file = tmp_path / "legacy_compat_db.json"
    seed_payload = {
        "students": {
            "stu_legacy_onboarded": {
                "student_id": "stu_legacy_onboarded",
                "full_name": "Legacy Completed Student",
                "age": 12,
                "current_grade": 7,
                "school_board": "CBSE",
                "onboarding_completed": False,  # stale flag despite completed academic year profile
            },
            "stu_legacy_incomplete": {
                "student_id": "stu_legacy_incomplete",
                "full_name": "Legacy Incomplete Student",
                "age": 13,
                "current_grade": 8,
                "school_board": "CBSE",
                "onboarding_completed": False,  # never completed onboarding (no academic year profile)
            },
        },
        "academic_years": {
            "stu_legacy_onboarded": [
                {
                    "academic_year_id": "stu_legacy_onboarded_2026-2027_G7",
                    "student_id": "stu_legacy_onboarded",
                    "academic_year_label": "2026-2027",
                    "grade": 7,
                    "school_board": "CBSE",
                    "state_name": "Telangana",
                    "language_preferences": {
                        "school_medium_language": "English",
                        "preferred_explanation_language": "Telugu",
                        "secondary_explanation_language": "English",
                        "interface_display_language": "English",
                    },
                    "subjects_studied": ["G7_MATH", "G7_SCI"],
                    "subjects_to_improve": ["G7_MATH"],
                    "subject_confidence_self_reports": [],
                    "learning_challenges": ["I don't understand some concepts."],
                    "when_need_most_help": ["While understanding concepts"],
                    "challenge_frequency": "Often",
                    "everything_goal_selected": True,
                    "learning_goals": ["g1"],
                    "status": "ACTIVE",
                    "is_locked_historical": False,
                }
            ],
            "stu_legacy_incomplete": [],
        },
    }
    db_file.write_text(json.dumps(seed_payload), encoding="utf-8")

    repo = EduSparkRepository(db_path=str(db_file), postgres_url="")
    assert repo.students["stu_legacy_onboarded"]["onboarding_completed"] is True
    assert repo.students["stu_legacy_incomplete"]["onboarding_completed"] is False
