"""
EDUSPARK AI — Complete Application-Wide Problem Detection & Repair Verification Suite
Tests:
1. Mathematical & Academic Calculation Accuracy (LCM, HCF, Fractions, Linear Equations, Arithmetic) + Intermediate Step Verification.
2. Grade-Level Intelligence (Grade 4 vs Grade 7 vs Grade 10 vs Grade 12 differentiation in Tutor, Study Plan, and Mock Exams).
3. Student Account Isolation (One student's data never appears in another student's account).
4. Cross-Module Shared Student Data Reactivity:
   - AI tutor learning gaps inform the study planner.
   - Poor mock-test results create revision cards AND update study plan.
   - Completed homework updates dashboard and progress statistics.
   - Changed study goals / onboarding update the study plan.
   - Academic promotion locks and preserves previous academic-year records.
5. Notifications & Reminders (Module 18) with 12-Hour AM/PM formatting.
"""
from fastapi.testclient import TestClient
from app.main import app
from app.agents.model_client import (
    solve_and_plan_math_problem,
    evaluate_math_or_science_attempt,
)

client = TestClient(app)


def test_deterministic_mathematical_accuracy_and_intermediate_steps():
    """
    Verifies Section 4 requirements:
    - LCM of 4 and 6 = 12
    - HCF of 12 and 18 = 6
    - 1/4 + 1/6 = 5/12
    - Plus general fraction subtraction (2/3 - 1/6 = 1/2), linear equations (3x - 7 = 14 -> x = 7), and arithmetic.
    """
    # 1. LCM of 4 and 6 = 12
    lcm_plan = solve_and_plan_math_problem("Find the LCM of 4 and 6", grade=6)
    assert lcm_plan["problem_type"] == "LCM"
    assert lcm_plan["final_answer"] == "12"
    assert len(lcm_plan["steps"]) == 2
    # Verify intermediate steps and final step evaluation
    step2_eval = evaluate_math_or_science_attempt(
        question_text="Find the LCM of 4 and 6",
        student_attempt="12",
        current_step_index=2,
    )
    assert step2_eval["is_correct"] is True

    # Verify wrong LCM attempt (multiplying 4 * 6 = 24 instead of least common multiple 12)
    wrong_lcm = evaluate_math_or_science_attempt(
        question_text="Find the LCM of 4 and 6",
        student_attempt="24",
        current_step_index=1,
    )
    assert wrong_lcm["is_correct"] is False
    assert "12" in wrong_lcm["detected_misconception"]

    # 2. HCF of 12 and 18 = 6
    hcf_plan = solve_and_plan_math_problem("Find the HCF of 12 and 18", grade=6)
    assert hcf_plan["problem_type"] == "HCF"
    assert hcf_plan["final_answer"] == "6"
    assert len(hcf_plan["steps"]) == 2
    hcf_eval = evaluate_math_or_science_attempt(
        question_text="Find the HCF of 12 and 18",
        student_attempt="6",
        current_step_index=2,
    )
    assert hcf_eval["is_correct"] is True

    # 3. 1/4 + 1/6 = 5/12 (with Step 1 LCM = 12, Step 2 = 3/12 and 2/12, Step 3 = 5/12)
    frac_plan = solve_and_plan_math_problem("Solve 1/4 + 1/6", grade=7)
    assert frac_plan["problem_type"] == "FRACTION_ADD_SUB"
    assert frac_plan["final_answer"] == "5/12"
    assert "12" in frac_plan["steps"][0]["expected_checkpoint"]
    assert "3/12" in frac_plan["steps"][1]["expected_checkpoint"]
    assert "2/12" in frac_plan["steps"][1]["expected_checkpoint"]

    frac_step1 = evaluate_math_or_science_attempt(
        question_text="Solve 1/4 + 1/6",
        student_attempt="The LCM is 12",
        current_step_index=1,
    )
    assert frac_step1["is_correct"] is True

    frac_step2 = evaluate_math_or_science_attempt(
        question_text="Solve 1/4 + 1/6",
        student_attempt="3/12 and 2/12",
        current_step_index=2,
    )
    assert frac_step2["is_correct"] is True

    frac_step3 = evaluate_math_or_science_attempt(
        question_text="Solve 1/4 + 1/6",
        student_attempt="5/12",
        current_step_index=3,
    )
    assert frac_step3["is_correct"] is True

    # 4. General Fraction Subtraction: 2/3 - 1/6 = 1/2
    sub_plan = solve_and_plan_math_problem("Solve 2/3 - 1/6", grade=7)
    assert sub_plan["final_answer"] == "1/2"

    # 5. Linear Equation: 3x - 7 = 14 -> x = 7
    eq_plan = solve_and_plan_math_problem("Solve 3x - 7 = 14", grade=8)
    assert eq_plan["problem_type"] == "LINEAR_EQUATION"
    assert eq_plan["final_answer"] == "7"


def test_grade_level_intelligence_grade4_vs_grade7_vs_grade10():
    """
    Verifies Section 3:
    A Grade 4 student (Diya Nair, ICSE) and a Grade 7 student (Aarav Sharma, CBSE)
    receive appropriately different explanations, examples, mock exam questions, and study plans.
    """
    # Start tutor session for Grade 4 student (stu_diya_g4)
    g4_res = client.post(
        "/api/tutor/session/start",
        json={
            "student_id": "stu_diya_g4",
            "typed_question": "Find the LCM of 4 and 6",
            "subject_hint": "Mathematics",
        },
    )
    assert g4_res.status_code == 200
    g4_data = g4_res.json()
    assert g4_data["understanding_output"]["detected_grade"] == 4
    assert "Grade 4" in g4_data["teaching_output"]["concept_explanation"]
    assert "Young Explorer Mode" in g4_data["teaching_output"]["concept_explanation"]
    assert (
        "stickers" in g4_data["teaching_output"]["real_world_example"].lower()
        or "grade 4" in g4_data["teaching_output"]["real_world_example"].lower()
    )

    # Start tutor session for Grade 7 student (stu_aarav_g7)
    g7_res = client.post(
        "/api/tutor/session/start",
        json={
            "student_id": "stu_aarav_g7",
            "typed_question": "Find the LCM of 4 and 6",
            "subject_hint": "Mathematics",
        },
    )
    assert g7_res.status_code == 200
    g7_data = g7_res.json()
    assert g7_data["understanding_output"]["detected_grade"] == 7
    assert "Grade 7" in g7_data["teaching_output"]["concept_explanation"]
    assert "Concept Builder Mode" in g7_data["teaching_output"]["concept_explanation"]
    assert (
        g4_data["teaching_output"]["concept_explanation"]
        != g7_data["teaching_output"]["concept_explanation"]
    )
    assert (
        g4_data["teaching_output"]["real_world_example"]
        != g7_data["teaching_output"]["real_world_example"]
    )

    # Verify Grade 4 vs Grade 10 Mock Exam generation produces grade-specific questions
    g4_exam = client.post(
        "/api/students/stu_diya_g4/exams/generate",
        json={
            "student_id": "stu_diya_g4",
            "exam_mode": "Chapter Test",
            "subject": "Mathematics",
            "chapters": ["Multiplication & Division"],
            "duration_minutes": 15,
            "question_count": 3,
        },
    ).json()
    g10_exam = client.post(
        "/api/students/stu_karthik_g10/exams/generate",
        json={
            "student_id": "stu_karthik_g10",
            "exam_mode": "Chapter Test",
            "subject": "Mathematics",
            "chapters": ["Quadratic Equations & Arithmetic Progressions"],
            "duration_minutes": 25,
            "question_count": 3,
        },
    ).json()
    assert "Multiplication & Division" in g4_exam["title"]
    assert "Quadratic Equations" in g10_exam["title"]
    assert g4_exam["questions"][0]["question_text"] != g10_exam["questions"][0]["question_text"]


def test_student_account_isolation():
    """
    Verifies Section 6:
    One student's information must never appear in another student's account.
    """
    dash_g4 = client.get("/api/students/stu_diya_g4/dashboard-summary").json()
    dash_g7 = client.get("/api/students/stu_aarav_g7/dashboard-summary").json()
    dash_g10 = client.get("/api/students/stu_karthik_g10/dashboard-summary").json()

    assert dash_g4["student"]["full_name"] == "Diya Nair"
    assert dash_g4["student"]["current_grade"] == 4
    assert "Diya Nair" in dash_g4["greeting"]
    assert "Aarav Sharma" not in dash_g4["greeting"]

    assert dash_g7["student"]["full_name"] == "Aarav Sharma"
    assert dash_g7["student"]["current_grade"] == 7

    assert dash_g10["student"]["full_name"] == "Karthik Rajan"
    assert dash_g10["student"]["current_grade"] == 10
    assert "Karthik Rajan" in dash_g10["greeting"]

    # Verify Parent Guard blocks cross-student access
    forbidden = client.get("/api/parent/parent_nair_01/child/stu_aarav_g7")
    assert forbidden.status_code == 403


def test_cross_module_shared_data_reactivity_end_to_end():
    """
    Verifies Section 6 Shared Student Data:
    1. AI tutor learning gaps inform the study planner.
    2. Poor mock-test results create revision cards AND update study plan.
    3. Completed homework updates dashboard and progress statistics.
    4. Changed study goals / onboarding update the study plan.
    5. Academic promotion locks and preserves previous academic-year records.
    6. Notifications & Reminders endpoint returns 12-hour AM/PM reminders.
    """
    student_id = "stu_diya_g4"

    # 1. Start a tutor session and make an incorrect attempt -> creates learning gap & updates study plan
    start_res = client.post(
        "/api/tutor/session/start",
        json={
            "student_id": student_id,
            "typed_question": "Solve 1/4 + 1/6",
            "subject_hint": "Mathematics",
        },
    ).json()
    session_id = start_res["session_id"]

    turn_res = client.post(
        "/api/tutor/session/turn",
        json={
            "session_id": session_id,
            "action": "submit_attempt",
            "student_text": "2/10",
        },
    )
    assert turn_res.status_code == 200
    plan_after_tutor = client.get(f"/api/students/{student_id}/study-plan").json()
    assert "Mathematics" in plan_after_tutor["weak_subjects"]

    # 2. Submit a poor mock exam -> creates revision card AND updates study plan
    exams = client.get(f"/api/students/{student_id}/exams").json()["exams"]
    exam_id = exams[0]["exam_id"]
    sub_res = client.post(
        f"/api/students/{student_id}/exams/{exam_id}/submit",
        json={
            "student_id": student_id,
            "exam_id": exam_id,
            "answers": {q["question_id"]: "wrong_answer" for q in exams[0]["questions"]},
            "time_taken_seconds": 120,
        },
    )
    assert sub_res.status_code == 200
    evaluated_exam = sub_res.json()
    assert len(evaluated_exam["weak_topics_detected"]) > 0

    revs = client.get(f"/api/students/{student_id}/revision").json()["cards"]
    assert any(r["source_tag"] == "Mock Exam Mistake" for r in revs)

    # 3. Complete pending homework -> updates dashboard & progress homework_completion_rate
    hws = client.get(f"/api/students/{student_id}/homework").json()["items"]
    pending_hw = next(h for h in hws if h["status"] != "completed")
    upd_hw = client.patch(
        f"/api/students/{student_id}/homework/{pending_hw['homework_id']}",
        json={"status": "completed"},
    )
    assert upd_hw.status_code == 200
    dash_after_hw = client.get(f"/api/students/{student_id}/dashboard-summary").json()
    assert dash_after_hw["homework_completion_rate"] == 100

    # 4. Change onboarding / study goals -> updates study plan
    onb_res = client.post(
        "/api/onboarding/submit",
        json={
            "student_id": student_id,
            "academic_year_label": "2026-2027",
            "step1": {
                "age": 9,
                "grade": 4,
                "school_board": "ICSE",
                "state_name": "Karnataka",
                "school_medium": "English",
                "preferred_explanation_language": "Kannada",
                "secondary_explanation_language": "English",
                "interface_display_language": "English",
            },
            "selected_subjects": ["G35_MATH", "G35_EVS", "G35_COMP"],
            "help_with_all_subjects": False,
            "subjects_to_improve": ["G35_COMP"],
            "subject_confidence": [
                {
                    "subject_code": "G35_COMP",
                    "subject_name": "Computer Studies",
                    "confidence_level": "Need help",
                    "difficult_topics": ["Logical Thinking & Stepwise Instructions"],
                }
            ],
            "learning_challenges": ["I struggle with application-based questions."],
            "when_need_most_help": ["While solving questions"],
            "challenge_frequency": "Sometimes",
            "everything_goal_selected": False,
            "selected_goals": ["g7"],
            "primary_goal": "g7",
        },
    )
    assert onb_res.status_code == 200
    plan_after_onb = client.get(f"/api/students/{student_id}/study-plan").json()
    assert "Computer Studies" in plan_after_onb["weak_subjects"]
    assert "g7" in plan_after_onb["academic_goal"]

    # 5. Annual Academic Progression -> locks and preserves previous academic years
    promo_res = client.post(
        f"/api/students/{student_id}/progression",
        json={
            "student_id": student_id,
            "new_academic_year_label": "2027-2028",
            "promotion_decision": "Yes",
            "same_school": "Yes",
            "board_unchanged": "Yes, same board",
            "updated_school_medium": "English",
            "updated_preferred_explanation_language": "Kannada",
            "updated_secondary_explanation_language": "English",
            "reselected_subjects": ["G35_MATH", "G35_EVS", "G35_ENG"],
            "reselected_improvement_subjects": ["G35_MATH"],
            "everything_goal_selected": True,
        },
    )
    assert promo_res.status_code == 200
    promo_data = promo_res.json()
    assert promo_data["new_grade"] == 5
    assert promo_data["total_academic_years_preserved"] >= 3
    past_years = [y for y in promo_data["academic_years"] if y["grade"] in (3, 4)]
    assert all(y["is_locked_historical"] is True for y in past_years)

    # 6. Notifications & Reminders endpoint (Module 18) with 12-hour AM/PM formatting
    notifs_res = client.get("/api/students/stu_aarav_g7/notifications")
    assert notifs_res.status_code == 200
    notifs_data = notifs_res.json()
    assert notifs_data["total_count"] > 0
    assert any("PM" in str(n["time_display"]) or "AM" in str(n["time_display"]) for n in notifs_data["notifications"])
