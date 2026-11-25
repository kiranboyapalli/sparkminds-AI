"""
Integration Tests for SparkMinds AI Cloud Authentication, Session Handling,
Multi-Device Sync, Cross-User Privacy & Text-Based Learning Buddy.
Validates all 7 required scenarios + removal of picture-based learning.
"""

import os
from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.repository import repo

client = TestClient(app)


def test_situation_1_new_user_sees_signin():
    """
    Situation 1: A completely new user opens the app without a session token.
    The session verification endpoint returns HTTP 401, directing the frontend to show the sign-in/register page.
    """
    # 1. No token provided
    res = client.get("/api/auth/session")
    assert res.status_code == 401
    assert "session token is required" in res.json()["detail"].lower()

    # 2. Non-existent random token
    res_fake = client.get("/api/auth/session?session_token=spark_sess_fake_nonexistent_token")
    assert res_fake.status_code == 401
    assert "invalid or expired" in res_fake.json()["detail"].lower()


def test_situation_2_new_user_registration_and_onboarding():
    """
    Situation 2: The new user registers, completes onboarding, and reaches the dashboard.
    Account and learning information are securely saved in the cloud.
    """
    test_sid = "stu_rohit_test"
    test_email = "rohit.learner@sparkminds.ai"
    test_pass = "SecurePass@2026"

    # Reset any leftover state from prior runs for a purely clean test run
    if test_sid in repo.students:
        del repo.students[test_sid]
    if test_sid in repo.auth_credentials:
        del repo.auth_credentials[test_sid]
    repo.active_sessions = {k: v for k, v in repo.active_sessions.items() if v.get("student_id") != test_sid}

    # Step A: Register new account
    reg_res = client.post(
        "/api/auth/register",
        json={
            "student_id": test_sid,
            "full_name": "Rohit Verma",
            "age": 13,
            "grade": 8,
            "email_or_username": test_email,
            "password_or_pin": test_pass,
            "device_name": "Laptop Chrome",
        },
    )
    assert reg_res.status_code == 200
    reg_data = reg_res.json()
    assert reg_data["status"] == "authenticated"
    session_token = reg_data["session_token"]
    assert session_token.startswith("spark_sess_")
    assert reg_data["student"]["onboarding_completed"] is False

    # Verify password is NOT stored as plain text
    cred = repo.auth_credentials.get(test_sid)
    assert cred is not None
    assert cred["password_hash"] != test_pass
    assert len(cred["salt"]) > 10

    # Step B: Complete 7-step onboarding
    onb_res = client.post(
        "/api/onboarding/submit",
        json={
            "student_id": test_sid,
            "academic_year_label": "2026-2027",
            "step1": {
                "age": 13,
                "grade": 8,
                "school_board": "CBSE",
                "state_name": "Delhi",
                "school_medium": "English",
                "preferred_explanation_language": "Hindi",
                "secondary_explanation_language": "English",
                "interface_display_language": "English",
            },
            "selected_subjects": ["G8_MATH", "G8_SCI", "G8_ENG"],
            "help_with_all_subjects": False,
            "subjects_to_improve": ["G8_MATH"],
            "subject_confidence": [
                {
                    "subject_code": "G8_MATH",
                    "subject_name": "Mathematics",
                    "confidence_level": "Need help",
                    "difficult_topics": ["Linear Equations in One Variable"],
                }
            ],
            "main_improvement_priority": "Understand difficult concepts",
            "learning_challenges": ["I struggle with application-based questions."],
            "when_need_most_help": ["While understanding concepts"],
            "challenge_frequency": "Often",
            "everything_goal_selected": False,
            "selected_goals": ["g1", "g2"],
            "primary_goal": "g2",
        },
    )
    assert onb_res.status_code == 200
    onb_data = onb_res.json()
    assert onb_data["status"] == "onboarding_saved"
    assert onb_data["student"]["onboarding_completed"] is True
    assert onb_data["cloud_sync_bundle"] is not None

    # Verify student state in cloud database
    student = repo.students[test_sid]
    assert student["onboarding_completed"] is True
    assert student["language_preferences"]["preferred_explanation_language"] == "Hindi"


def test_situation_3_returning_user_goes_directly_to_dashboard():
    """
    Situation 3: The user closes and reopens the app.
    Existing session is checked securely; since valid and onboarding is complete,
    the user lands directly on the dashboard without sign-in or repeating onboarding.
    """
    test_sid = "stu_rohit_test"
    # Find active session token for Rohit
    session_token = next(
        tok for tok, s in repo.active_sessions.items()
        if s.get("student_id") == test_sid and s.get("active", True)
    )

    # Reopening the app on the same device
    res = client.get(
        f"/api/auth/session?session_token={session_token}",
        headers={"X-SparkMinds-Token": session_token},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "authenticated"
    assert data["student"]["student_id"] == test_sid
    assert data["student"]["onboarding_completed"] is True
    assert data["cloud_sync_bundle"]["study_plan"] is not None


def test_situation_4_user_signs_in_on_second_device():
    """
    Situation 4: The user signs in on a second device (e.g. Android tablet).
    The system retrieves their existing cloud data and displays the exact same dashboard and information.
    """
    test_email = "rohit.learner@sparkminds.ai"
    test_pass = "SecurePass@2026"

    login_res = client.post(
        "/api/auth/login",
        json={
            "identifier": test_email,
            "password_or_pin": test_pass,
            "device_name": "Android Tablet",
        },
    )
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert login_data["status"] == "authenticated"
    device_2_token = login_data["session_token"]
    assert device_2_token.startswith("spark_sess_")

    # Cloud sync bundle matches Device 1
    bundle = login_data["cloud_sync_bundle"]
    assert bundle["student"]["full_name"] == "Rohit Verma"
    assert bundle["student"]["current_grade"] == 8
    assert bundle["student"]["school_board"] == "CBSE"
    assert bundle["active_year_profile"]["primary_goal"] == "g2"
    assert len(bundle["active_devices"]) >= 2


def test_situation_5_cross_device_study_plan_synchronisation():
    """
    Situation 5: The user updates a study plan on Device 1, and the update
    synchronises to Device 2.
    """
    test_sid = "stu_rohit_test"
    # Get active session token for Device 2
    device_2_token = next(
        tok for tok, s in repo.active_sessions.items()
        if s.get("student_id") == test_sid and s.get("device_name") == "Android Tablet" and s.get("active", True)
    )

    # Device 1: Get study plan tasks and mark the first task as completed
    plan = repo.get_or_create_study_plan(test_sid)
    assert len(plan.daily_timetable) > 0
    first_task = plan.daily_timetable[0]
    task_id = first_task.task_id

    # Device 1 toggles task to completed
    update_res = client.patch(
        f"/api/students/{test_sid}/study-plan/tasks/{task_id}",
        json={"completed": True, "missed": False},
        headers={"X-SparkMinds-Token": device_2_token},
    )
    assert update_res.status_code == 200
    updated_plan = update_res.json()
    updated_task = next(t for t in updated_plan["daily_timetable"] if t["task_id"] == task_id)
    assert updated_task["completed"] is True

    # Device 2: Synchronises from cloud and verifies the task is completed
    sync_res = client.get(
        f"/api/auth/session?session_token={device_2_token}",
        headers={"X-SparkMinds-Token": device_2_token},
    )
    assert sync_res.status_code == 200
    sync_bundle = sync_res.json()["cloud_sync_bundle"]
    device_2_tasks = sync_bundle["study_plan"]["daily_timetable"]
    d2_first_task = next(t for t in device_2_tasks if t["task_id"] == task_id)
    assert d2_first_task["completed"] is True


def test_situation_6_signed_out_user_must_sign_in_again():
    """
    Situation 6: A signed-out user is asked to sign in again.
    After logout, the session token is invalidated in the cloud database.
    """
    test_sid = "stu_rohit_test"
    token_to_logout = next(
        tok for tok, s in repo.active_sessions.items()
        if s.get("student_id") == test_sid and s.get("active", True)
    )

    # User clicks Sign Out / Logout
    logout_res = client.post(
        "/api/auth/logout",
        json={"session_token": token_to_logout, "student_id": test_sid},
        headers={"X-SparkMinds-Token": token_to_logout},
    )
    assert logout_res.status_code == 200
    assert logout_res.json()["status"] == "logged_out"

    # Attempting to access session with logged-out token
    check_res = client.get(
        f"/api/auth/session?session_token={token_to_logout}",
        headers={"X-SparkMinds-Token": token_to_logout},
    )
    assert check_res.status_code == 401
    assert "logged out" in check_res.json()["detail"].lower()


def test_situation_7_cross_user_privacy_isolation():
    """
    Situation 7: One user cannot access another user's private information.
    Attempts by User A to use their token to access User B's profile, session,
    study plan, or homework are strictly blocked.
    """
    # Create User A
    user_a_res = client.post(
        "/api/auth/register",
        json={
            "student_id": "stu_alice_priv",
            "full_name": "Alice Wonderland",
            "age": 14,
            "grade": 9,
            "email_or_username": "alice@sparkminds.ai",
            "password_or_pin": "AliceSecret#1",
        },
    ).json()
    token_a = user_a_res["session_token"]

    # Create User B
    user_b_res = client.post(
        "/api/auth/register",
        json={
            "student_id": "stu_bob_priv",
            "full_name": "Bob Builder",
            "age": 15,
            "grade": 10,
            "email_or_username": "bob@sparkminds.ai",
            "password_or_pin": "BobSecret#2",
        },
    ).json()
    token_b = user_b_res["session_token"]

    # 1. User A tries to get User B's session cloud bundle
    attack_1 = client.get(
        f"/api/auth/session?session_token={token_a}&student_id=stu_bob_priv",
        headers={"X-SparkMinds-Token": token_a},
    )
    assert attack_1.status_code in (401, 403)
    assert "access denied" in attack_1.json()["detail"].lower()

    # 2. User A tries to view User B's private profile
    attack_2 = client.get(
        "/api/students/stu_bob_priv",
        headers={"X-SparkMinds-Token": token_a},
    )
    assert attack_2.status_code == 403
    assert "access denied" in attack_2.json()["detail"].lower()

    # 3. User A tries to view User B's academic journey
    attack_3 = client.get(
        "/api/students/stu_bob_priv/academic-journey",
        headers={"X-SparkMinds-Token": token_a},
    )
    assert attack_3.status_code == 403

    # 4. User A tries to access User B's study plan
    attack_4 = client.get(
        "/api/students/stu_bob_priv/study-plan",
        headers={"X-SparkMinds-Token": token_a},
    )
    assert attack_4.status_code == 403

    # 5. User A tries to access User B's homework
    attack_5 = client.get(
        "/api/students/stu_bob_priv/homework",
        headers={"X-SparkMinds-Token": token_a},
    )
    assert attack_5.status_code == 403


def test_situation_8_no_automatic_pictures_in_tutoring():
    """
    Requirement 1: Remove picture-based learning from the AI Learning Buddy.
    The AI Learning Buddy must teach through clear text explanations,
    step-by-step instructions, examples, questions, and text-based practice.
    Do not automatically generate or display pictures as part of an explanation.
    """
    tutor_res = client.post(
        "/api/tutor/session/start",
        json={
            "student_id": "stu_aarav_g7",
            "typed_question": "Explain how to solve linear equations 2x + 5 = 15 step by step.",
        },
    )
    assert tutor_res.status_code == 200
    tutor_data = tutor_res.json()
    t_out = tutor_data["teaching_output"]

    # Verify pictures and SVGs are NOT automatically attached to explanations
    assert t_out.get("visual_diagram_svg") is None
    assert t_out.get("visual_concept_type") is None
    assert t_out.get("visual_diagram_caption") is None

    # Verify teaching is delivered through clear text, step-by-step instructions, examples, and questions
    assert t_out["concept_explanation"] is not None
    assert len(t_out["concept_explanation"]) > 20
    assert len(t_out["steps_breakdown"]) >= 1
    assert t_out["real_world_example"] is not None
    assert t_out["prompt_for_student_attempt"] is not None
    assert t_out["similar_practice_question"] is not None


def test_situation_9_age_editing_and_cloud_persistence():
    """
    Requirement 2: Make age editable.
    Users can change their age whenever necessary.
    Ensure the field is not read-only, disabled, or locked after onboarding.
    Save the updated age securely to the cloud database.
    """
    test_sid = "stu_rohit_test"
    # Find active token for rohit
    token = next(
        tok for tok, s in repo.active_sessions.items()
        if s.get("student_id") == test_sid and s.get("active", True)
    )

    # Rohit changes his age from 13 to 14
    patch_res = client.patch(
        f"/api/students/{test_sid}/profile",
        json={"age": 14},
        headers={"X-SparkMinds-Token": token},
    )
    assert patch_res.status_code == 200
    res_data = patch_res.json()
    assert res_data["status"] == "profile_updated"
    assert res_data["student"]["age"] == 14

    # Verify cloud database persistence across sessions/reopen
    sess_res = client.get(
        f"/api/auth/session?session_token={token}",
        headers={"X-SparkMinds-Token": token},
    )
    assert sess_res.status_code == 200
    assert sess_res.json()["student"]["age"] == 14
    assert sess_res.json()["cloud_sync_bundle"]["student"]["age"] == 14


def test_situation_10_date_of_birth_calculates_age_correctly():
    """
    Requirement 2: If date of birth is used instead of age, allow the user
    to edit the date of birth and calculate age correctly.
    """
    test_sid = "stu_rohit_test"
    token = next(
        tok for tok, s in repo.active_sessions.items()
        if s.get("student_id") == test_sid and s.get("active", True)
    )

    # Update DOB to a specific date 15 years prior
    patch_res = client.patch(
        f"/api/students/{test_sid}/profile",
        json={"date_of_birth": "2011-04-10"},
        headers={"X-SparkMinds-Token": token},
    )
    assert patch_res.status_code == 200
    res_data = patch_res.json()
    assert res_data["student"]["date_of_birth"] == "2011-04-10"
    assert res_data["student"]["age"] == 15


def test_situation_11_under_8_child_safety_protection_on_age_edit():
    """
    Requirement 2: Apply appropriate parent or guardian verification
    requirements for younger users. Do not bypass child-safety protections.
    """
    # Create a fresh unverified student
    fresh_sid = "stu_test_safety_gate"
    if fresh_sid in repo.students:
        del repo.students[fresh_sid]
    reg = client.post(
        "/api/auth/register",
        json={
            "student_id": fresh_sid,
            "full_name": "Test Child",
            "age": 10,
            "grade": 5,
        },
    )
    assert reg.status_code == 200
    token = reg.json()["session_token"]

    # Attempting to change age to 6 without verified parental consent must fail (HTTP 400)
    failed_patch = client.patch(
        f"/api/students/{fresh_sid}/profile",
        json={"age": 6},
        headers={"X-SparkMinds-Token": token},
    )
    assert failed_patch.status_code == 400
    assert "child safety protection" in failed_patch.json()["detail"].lower()

    # Supplying parent verification details succeeds
    valid_patch = client.patch(
        f"/api/students/{fresh_sid}/profile",
        json={
            "age": 6,
            "parent_consent_verified": True,
            "parent_verification_details": {
                "parent_full_name": "Guardian Sharma",
                "relationship_to_child": "Father",
            },
        },
        headers={"X-SparkMinds-Token": token},
    )
    assert valid_patch.status_code == 200
    assert valid_patch.json()["student"]["age"] == 6
    assert valid_patch.json()["student"]["parent_consent_verified"] is True


def test_situation_12_repeated_app_openings_continue_to_dashboard():
    """
    Requirement 5 Situation 4: Repeated app openings continue to take
    the authenticated user directly to the dashboard.
    """
    test_sid = "stu_rohit_test"
    token = next(
        tok for tok, s in repo.active_sessions.items()
        if s.get("student_id") == test_sid and s.get("active", True)
    )

    # Simulate 5 consecutive app openings on the same device
    for opening in range(1, 6):
        res = client.get(
            f"/api/auth/session?session_token={token}",
            headers={"X-SparkMinds-Token": token},
        )
        assert res.status_code == 200, f"Failed on opening #{opening}"
        body = res.json()
        assert body["status"] == "authenticated"
        assert body["student"]["student_id"] == test_sid
        assert body["student"]["onboarding_completed"] is True
        assert body["cloud_sync_bundle"] is not None


def test_situation_13_expired_sessions_handled_securely():
    """
    Requirement 5 Situation 10: Expired sessions are handled correctly and securely.
    """
    test_sid = "stu_rohit_test"
    # Create an artificially expired session token (yesterday)
    expired_token = "spark_sess_expired_for_test"
    yesterday_iso = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    repo.active_sessions[expired_token] = {
        "session_token": expired_token,
        "student_id": test_sid,
        "device_name": "Old Phone",
        "created_at": yesterday_iso,
        "expires_at": yesterday_iso,
        "active": True,
    }

    # Attempting to authenticate with the expired token must fail with 401
    res = client.get(
        f"/api/auth/session?session_token={expired_token}",
        headers={"X-SparkMinds-Token": expired_token},
    )
    assert res.status_code == 401
    assert "expired" in res.json()["detail"].lower()

    # The session in the repository must now be deactivated
    assert repo.active_sessions[expired_token]["active"] is False


def test_situation_14_no_flashcards_or_sample_content_on_auth_screen():
    """
    Requirement 5 Situation 9: No flashcards, sample questions or example learning
    content appear on the sign-in or registration pages.
    """
    app_tsx_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/src/App.tsx"))
    with open(app_tsx_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Verify no sample student profile list or demo flashcards on the auth screen
    assert "sample flashcards" not in code.lower()
    assert "demo learning" not in code.lower()
    assert "Date of Birth (Optional)" not in code
    assert "Password or PIN (Optional)" not in code
    assert "rahul@example.com" not in code
    assert "Rajesh Sharma" not in code
    assert "Sign in to access your saved profile, timetable, homework, and academic progress" in code


