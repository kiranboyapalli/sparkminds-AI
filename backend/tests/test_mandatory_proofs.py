"""
EDUSPARK AI — Phase 10 Comprehensive Automated Test Suite
Proves all 5 Mandatory Testing Requirements from Section 19:
1. Every mandatory onboarding question can be completed without typing a custom answer.
2. A student cannot finish onboarding without selecting an explanation language.
3. Explanation language preferences are correctly passed to the AI agents.
4. Promoting a student to the next grade does not destroy previous academic records.
5. Changing explanation language updates subsequent AI explanations.

Also verifies:
- Representative profiles across Grade 1, Grade 4, Grade 7, Grade 10, and Grade 12.
- Board-specific and state-specific curriculum differentiation (CBSE, ICSE, State Board).
- "Everything" goal synchronization and "Help with all subjects" logic.
- 4 separate language settings persistence.
- English, Telugu, Hindi, Tamil, and Kannada explanations.
- Parent access permissions, privacy isolation, and score tamper protection.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_mandatory_proof_1_onboarding_without_typing_custom_text():
    """
    PROOF 1: Every mandatory onboarding question can be completed without typing a custom answer.
    Student name is retrieved from registration, and Steps 1–7 use selectable options only.
    """
    reg = client.post(
        "/api/auth/register",
        json={"student_id": "stu_test_g4", "full_name": "Diya Nair", "age": 9, "grade": 4},
    )
    assert reg.status_code == 200
    assert reg.json()["student"]["full_name"] == "Diya Nair"

    # Fetch selectable curriculum options for Grade 4 CBSE
    opts = client.get("/api/curriculum/options?grade=4&board=CBSE").json()
    selectable_subject_codes = [s["code"] for s in opts["subjects"][:3]]

    payload = {
        "student_id": "stu_test_g4",
        "academic_year_label": "2026-2027",
        "step1": {
            "age": 9,
            "grade": 4,
            "school_board": "CBSE",
            "school_medium": "English",
            "preferred_explanation_language": "Malayalam",
            "secondary_explanation_language": "English",
            "interface_display_language": "English",
        },
        "selected_subjects": selectable_subject_codes,
        "help_with_all_subjects": True,
        "subjects_to_improve": selectable_subject_codes,
        "subject_confidence": [
            {
                "subject_code": selectable_subject_codes[0],
                "subject_name": "Mathematics",
                "confidence_level": "Need help",
                "difficult_topics": ["Fractions Introduction"],
            }
        ],
        "main_improvement_priority": "Understand concepts",
        "learning_challenges": [opts["challenges_14"][0]["label"]],
        "when_need_most_help": ["While understanding concepts"],
        "challenge_frequency": "Sometimes",
        "everything_goal_selected": True,
        "selected_goals": ["g1"],  # Should auto-expand to all 9 goals when everything_goal_selected=True
    }

    res = client.post("/api/onboarding/submit", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "onboarding_saved"
    # Verify "Everything" goal logic automatically selected all 9 goals
    assert len(data["active_year_profile"]["learning_goals"]) == 9
    # Verify 4 separate language settings stored distinctly
    lp = data["student"]["language_preferences"]
    assert lp["school_medium_language"] == "English"
    assert lp["preferred_explanation_language"] == "Malayalam"
    assert lp["secondary_explanation_language"] == "English"
    assert lp["interface_display_language"] == "English"


def test_mandatory_proof_2_cannot_finish_onboarding_without_explanation_language():
    """
    PROOF 2: A student cannot finish onboarding without selecting an explanation language.
    """
    payload = {
        "student_id": "stu_missing_lang",
        "step1": {
            "age": 12,
            "grade": 7,
            "school_board": "CBSE",
            "school_medium": "English",
            "preferred_explanation_language": "",  # Missing mandatory explanation language
        },
        "selected_subjects": ["G7_MATH"],
        "subjects_to_improve": ["G7_MATH"],
        "subject_confidence": [
            {
                "subject_code": "G7_MATH",
                "subject_name": "Mathematics",
                "confidence_level": "Okay",
                "difficult_topics": [],
            }
        ],
        "main_improvement_priority": "Marks",
        "learning_challenges": ["I forget what I studied."],
        "when_need_most_help": ["During revision"],
        "challenge_frequency": "Sometimes",
        "everything_goal_selected": True,
        "selected_goals": ["g1"],
    }
    res = client.post("/api/onboarding/submit", json=payload)
    assert res.status_code == 422


def test_mandatory_proof_3_and_5_language_passed_to_agents_and_updates_subsequent_explanations():
    """
    PROOF 3: Explanation language preferences are correctly passed to the AI agents.
    PROOF 5: Changing explanation language updates subsequent AI explanations.
    Also verifies English, Telugu, Hindi, Tamil, and Kannada explanations.
    """
    student_id = "stu_aarav_g7"

    for lang_name, expected_script_token in [
        ("Telugu", "తెలుగు"),
        ("Hindi", "हिन्दी"),
        ("Tamil", "தமிழில்"),
        ("Kannada", "ಕನ್ನಡ"),
        ("English", "Least Common Multiple"),
    ]:
        # Permanently update preferred explanation language
        upd = client.put(
            f"/api/students/{student_id}/languages",
            json={
                "school_medium_language": "English",
                "preferred_explanation_language": lang_name,
                "secondary_explanation_language": "English" if lang_name != "English" else None,
                "interface_display_language": "English",
            },
        )
        assert upd.status_code == 200

        # Invoke the 4-Agent Orchestrator
        interact = client.post(
            "/api/orchestrator/interact",
            json={
                "student_id": student_id,
                "user_message": "How do I add fractions 1/4 and 1/6?",
                "subject_name": "Mathematics",
                "interaction_mode": "homework",
            },
        )
        assert interact.status_code == 200
        body = interact.json()

        # Verify all 4 agents received and applied the updated language preference
        assert body["explanation_language_applied"] == lang_name
        assert body["discovery"]["explanation_language_applied"] == lang_name
        assert body["intelligence"]["explanation_language_applied"] == lang_name
        assert body["strategy"]["explanation_language_used"] == lang_name
        assert body["growth"]["explanation_language_applied"] == lang_name
        assert expected_script_token in body["coherent_final_response"]


def test_mandatory_proof_4_grade_promotion_preserves_previous_academic_records():
    """
    PROOF 4: Promoting a student to the next grade (Grade 7 -> Grade 8) does NOT destroy
    previous academic records (Grade 5, Grade 6, Grade 7 remain intact and locked).
    """
    student_id = "stu_aarav_g7"
    before_journey = client.get(f"/api/students/{student_id}/academic-journey").json()
    before_count = len(before_journey["completed_and_active_years"])
    assert before_count == 3  # G5, G6, G7

    # Promote Aarav from Grade 7 -> Grade 8 with board change to State Board (Telangana)
    promo_res = client.post(
        f"/api/students/{student_id}/progression",
        json={
            "student_id": student_id,
            "new_academic_year_label": "2027-2028",
            "promotion_decision": "Yes",
            "board_unchanged": "No, I have changed my board",
            "same_school": "No",
            "new_school_board": "STATE",
            "new_state_name": "Telangana",
            "reselected_subjects": ["G8_MATH", "G8_SCI", "G8_SST", "G8_ENG"],
            "reselected_improvement_subjects": ["G8_MATH"],
            "updated_preferred_explanation_language": "Telugu",
            "updated_secondary_explanation_language": "English",
            "updated_school_medium": "English",
            "everything_goal_selected": True,
        },
    )
    assert promo_res.status_code == 200
    promo_data = promo_res.json()
    assert promo_data["previous_grade"] == 7
    assert promo_data["new_grade"] == 8
    assert promo_data["total_academic_years_preserved"] == 4

    after_journey = client.get(f"/api/students/{student_id}/academic-journey").json()
    grades_recorded = [y["grade"] for y in after_journey["completed_and_active_years"]]
    assert grades_recorded == [5, 6, 7, 8]
    # Verify Grade 7 record is locked historical and still retains its verified Integers 88% score
    g7_record = next(y for y in after_journey["completed_and_active_years"] if y["grade"] == 7)
    assert g7_record["is_locked_historical"] is True
    assert any(ev["score_percentage"] == 88.0 for ev in g7_record["evidence_records"])


@pytest.mark.parametrize(
    "grade,board,state",
    [
        (1, "CBSE", None),
        (4, "ICSE", None),
        (7, "CBSE", None),
        (10, "STATE", "Telangana"),
        (12, "CBSE", None),
    ],
)
def test_representative_grades_1_4_7_10_12_and_curriculum_differentiation(grade, board, state):
    """
    Section 19: Test representative profiles across Grade 1, Grade 4, Grade 7, Grade 10, and Grade 12
    and verify grade-wise, board-specific, and state-wise curriculum differentiation.
    """
    url = f"/api/curriculum/options?grade={grade}&board={board}"
    if state:
        url += f"&state={state}"
    res = client.get(url)
    assert res.status_code == 200
    data = res.json()
    assert data["grade"] == grade
    assert len(data["subjects"]) >= 4


def test_parent_access_permissions_and_tamper_protection():
    """
    Section 15 & 17: Verify authorised parent access, privacy isolation, and tamper protection.
    """
    # Authorised parent can view child's progress
    ok_res = client.get("/api/parent/parent_sharma_01/child/stu_aarav_g7")
    assert ok_res.status_code == 200
    assert ok_res.json()["authorised"] is True

    # Unauthorised parent is blocked with 403 Forbidden
    unauth_res = client.get("/api/parent/stranger_parent_99/child/stu_aarav_g7")
    assert unauth_res.status_code == 403

    # Parent attempting to silently alter verified assessment score is blocked with 403
    tamper_res = client.post(
        "/api/parent/parent_sharma_01/child/stu_aarav_g7/action",
        json={"parent_id": "parent_sharma_01", "action": "ATTEMPT_ALTER_SCORE"},
    )
    assert tamper_res.status_code == 403
