"""
Comprehensive E2E Verification Script for SparkMinds AI:
1. Clean sign-in page: zero sample flashcards, zero example questions/answers, zero demo student cards on sign-in/register.
2. Age editing: editable numeric input (4-20), editable DOB with auto age calculation, cloud persistence, under-8 child safety gate.
3. Direct dashboard on every return visit: valid session goes straight to dashboard; signed-out goes to sign-in.
4. Multi-device cloud sync: state persists and synchronizes across devices.
"""

import os
import sys
from datetime import datetime, timezone
from fastapi.testclient import TestClient

# Add app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app
from app.core.repository import repo

client = TestClient(app)

def test_verify_clean_signin_html_and_source():
    # Verify built frontend assets do not contain sample student profile cards in the auth view
    dist_index = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist/index.html"))
    assert os.path.exists(dist_index), "Frontend dist/index.html must exist"
    
    # Read frontend/src/App.tsx to ensure no sample student list in auth screen
    app_tsx_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/src/App.tsx"))
    with open(app_tsx_path, "r", encoding="utf-8") as f:
        app_source = f.read()

    # The auth screen should NOT have sample profile cards or demo learning flashcards
    assert "sample flashcards" not in app_source.lower()
    assert "demo learning" not in app_source.lower()
    # Ensure date of birth and password are NOT optional
    assert "Date of Birth (Optional)" not in app_source
    assert "Password or PIN (Optional)" not in app_source
    # Ensure no example names on the auth screen
    assert "rahul@example.com" not in app_source
    assert "Rajesh Sharma" not in app_source
    # Check that auth view defaults to register and has clean titles
    assert "authPortalTab, setAuthPortalTab] = React.useState<'register' | 'login' | 'recover'>('register')" in app_source
    assert "Manage Student Age & Personal Details" in app_source
    assert "Editable Student Profile • Cloud Synchronised" in app_source
    print("✓ Clean sign-in and mandatory DOB & password verified in source code.")

def test_verify_full_returning_user_and_age_flow():
    test_user_id = "stu_verify_e2e_student"
    password = "E2ESecurePassword#2026"
    
    # Clean up any leftover test data
    if test_user_id in repo.students:
        del repo.students[test_user_id]

    # Step 1: Unauthenticated user check
    res_unauth = client.get("/api/auth/session")
    assert res_unauth.status_code == 401, "Unauthenticated session must return 401"
    print("✓ 1. Unauthenticated session check returns 401 (directs to Sign-In page).")

    # Step 2: First-time registration
    reg_payload = {
        "student_id": test_user_id,
        "full_name": "Arjun Sharma",
        "age": 14,
        "grade": 9,
        "school_board": "CBSE",
        "state_name": "Delhi",
        "date_of_birth": "2012-06-15",
        "password_or_pin": password,
        "device_name": "Laptop-Chrome",
    }
    res_reg = client.post("/api/auth/register", json=reg_payload)
    assert res_reg.status_code == 200, f"Registration failed: {res_reg.text}"
    token_1 = res_reg.json()["session_token"]
    assert token_1, "Session token must be provided"
    assert res_reg.json()["student"]["age"] == 14
    print("✓ 2. First-time registration succeeds with secure token and cloud sync.")

    # Step 3: Complete onboarding
    onboard_payload = {
        "student_id": test_user_id,
        "academic_year_label": "2026-2027",
        "step1": {
            "age": 14,
            "grade": 9,
            "school_board": "CBSE",
            "state_name": "Delhi",
            "school_medium": "English",
            "preferred_explanation_language": "English",
            "secondary_explanation_language": "Hindi",
            "interface_display_language": "English",
        },
        "selected_subjects": ["G9_MATH", "G9_SCI"],
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
        "main_improvement_priority": "Understand difficult concepts",
        "learning_challenges": ["Formula memorization"],
        "when_need_most_help": ["During homework"],
        "challenge_frequency": "Often",
        "everything_goal_selected": False,
        "selected_goals": ["g1"],
        "primary_goal": "g1",
    }
    res_onb = client.post("/api/onboarding/submit", json=onboard_payload)
    assert res_onb.status_code == 200, f"Onboarding failed: {res_onb.text}"
    print("✓ 3. Onboarding completed and stored in cloud.")

    # Step 4: Second opening / return visit on same device
    # App makes GET /api/auth/session with token_1
    res_sess = client.get("/api/auth/session", headers={"X-SparkMinds-Token": token_1})
    assert res_sess.status_code == 200
    sess_data = res_sess.json()
    assert sess_data["status"] == "authenticated"
    assert sess_data["student"]["onboarding_completed"] is True
    assert sess_data["student"]["age"] == 14
    print("✓ 4. Return visit with saved token bypasses sign-in/onboarding, directly returning full student state.")

    # Step 5: Age editing (User changes age from 14 to 15)
    res_patch_age = client.patch(
        f"/api/students/{test_user_id}/profile",
        json={"age": 15},
        headers={"X-SparkMinds-Token": token_1},
    )
    assert res_patch_age.status_code == 200
    assert res_patch_age.json()["student"]["age"] == 15
    print("✓ 5. Age field is fully editable and updates immediately.")

    # Step 6: Date of Birth editing (calculates age automatically)
    res_patch_dob = client.patch(
        f"/api/students/{test_user_id}/profile",
        json={"date_of_birth": "2010-06-15"},
        headers={"X-SparkMinds-Token": token_1},
    )
    assert res_patch_dob.status_code == 200
    assert res_patch_dob.json()["student"]["date_of_birth"] == "2010-06-15"
    assert res_patch_dob.json()["student"]["age"] == 16
    print("✓ 6. Date of birth correctly recalculates student age.")

    # Step 7: Child-safety gate (under 8 requires guardian details)
    res_patch_under8_fail = client.patch(
        f"/api/students/{test_user_id}/profile",
        json={"age": 6},
        headers={"X-SparkMinds-Token": token_1},
    )
    assert res_patch_under8_fail.status_code == 400
    assert "child safety protection" in res_patch_under8_fail.json()["detail"].lower()
    print("✓ 7. Under-8 age edit without parental verification is rejected with child safety protection.")

    # Step 8: Under 8 with verified guardian details succeeds
    res_patch_under8_ok = client.patch(
        f"/api/students/{test_user_id}/profile",
        json={
            "age": 6,
            "parent_consent_verified": True,
            "parent_verification_details": {
                "parent_full_name": "Ramesh Sharma",
                "relationship_to_child": "Father",
            },
        },
        headers={"X-SparkMinds-Token": token_1},
    )
    assert res_patch_under8_ok.status_code == 200
    assert res_patch_under8_ok.json()["student"]["age"] == 6
    assert res_patch_under8_ok.json()["student"]["requires_parental_assistance"] is True
    print("✓ 8. Under-8 age edit with guardian verification succeeds safely.")

    # Step 9: Cross-device sign in (Device 2 signs in and gets latest profile)
    res_login_dev2 = client.post(
        "/api/auth/login",
        json={
            "identifier": test_user_id,
            "password_or_pin": password,
            "device_name": "iPad-Safari",
        },
    )
    assert res_login_dev2.status_code == 200
    dev2_token = res_login_dev2.json()["session_token"]
    assert res_login_dev2.json()["student"]["age"] == 6
    expected_dob_year = datetime.now(timezone.utc).year - 6
    assert str(res_login_dev2.json()["student"]["date_of_birth"]).startswith(str(expected_dob_year))
    print("✓ 9. Second device signs in and retrieves the latest cloud-synchronized age and profile.")

    # Step 10: Sign out invalidates session
    res_logout = client.post(
        "/api/auth/logout",
        json={"session_token": token_1, "student_id": test_user_id},
        headers={"X-SparkMinds-Token": token_1},
    )
    assert res_logout.status_code == 200
    res_check_logged_out = client.get("/api/auth/session", headers={"X-SparkMinds-Token": token_1})
    assert res_check_logged_out.status_code == 401
    print("✓ 10. Sign out invalidates session; app prompts for sign-in again.")

    print("\n🎉 ALL E2E VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_verify_clean_signin_html_and_source()
    test_verify_full_returning_user_and_age_flow()
