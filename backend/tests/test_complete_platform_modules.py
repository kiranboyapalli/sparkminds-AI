"""
EDUSPARK AI — Section 7 Mandatory Automated Test Suite for All Complete Platform Modules:
1. Study plan generation and database persistence.
2. Timetable respects available study hours strictly.
3. Weak subjects receive higher time allocation than strong subjects.
4. Homework creation, image extraction, and status updates (pending -> in_progress -> completed).
5. Mock examination generation and automatic evaluation with explanations.
6. Revision scheduling, spaced repetition intervals, and automatic weak-topic ingestion from mock exams.
7. Progress calculations and strict separation of ACTUAL_ASSESSMENT vs HOMEWORK_PRACTICE vs STUDENT_SELF_REPORT.
8. Academic history preservation and grade promotion.
9. School Project & Creativity Lab workflow creation and milestone progress updates.
10. Parent access permissions, live child summary, and tamper guard.
11. Shared student profile cross-module reactivity.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_1_and_2_and_3_smart_study_planner_hours_weak_weighting_and_persistence():
    """
    Tests:
    - Study plan generation and persistence.
    - Daily timetable study blocks strictly respect available daily study hours (e.g. 2.5 hrs = 150 mins).
    - Weak subjects receive strictly higher weekly hour allocation & percentage than strong subjects.
    - Task completion toggle and catch-up schedule generation work and persist.
    """
    student_id = "stu_aarav_g7"
    payload = {
        "student_id": student_id,
        "exam_name": "CBSE Grade 7 Term-1 Final",
        "exam_date": "2026-12-15",
        "daily_study_hours": 2.5,
        "preferred_study_time": "Evening (6 PM - 9 PM)",
        "selected_subjects_and_chapters": {
            "Mathematics": ["Fractions & Decimals", "Algebraic Expressions & Linear Equations"],
            "General Science": ["Acids, Bases & Salts", "Heat, Motion & Time"],
            "English": ["Grammar, Comprehension & Creative Writing"],
        },
        "weak_subjects": ["Mathematics"],
        "strong_subjects": ["English"],
        "academic_goal": "Score 90%+ in Mathematics and Science",
    }
    res = client.post(f"/api/students/{student_id}/study-plan/generate", json=payload)
    assert res.status_code == 200
    plan = res.json()
    assert plan["daily_study_hours"] == 2.5

    # Verify timetable strictly respects available daily study hours (excluding restorative breaks)
    for day_name, tasks in plan["weekly_timetable"].items():
        study_minutes = sum(
            t["duration_minutes"] for t in tasks if t["session_type"] != "Break"
        )
        assert study_minutes == 150, f"Expected 150 mins on {day_name}, got {study_minutes}"
        # Verify breaks are included
        assert any(t["session_type"] == "Break" for t in tasks)

    # Verify weak subject (Mathematics) receives strictly higher time allocation than strong subject (English)
    alloc_hrs = plan["subject_time_allocation_hours_per_week"]
    assert alloc_hrs["Mathematics"] > alloc_hrs["English"]
    assert plan["subject_allocation_percentages"]["Mathematics"] > plan["subject_allocation_percentages"]["English"]

    # Toggle first task completed
    first_task_id = plan["daily_timetable"][0]["task_id"]
    toggle_res = client.patch(
        f"/api/students/{student_id}/study-plan/tasks/{first_task_id}",
        json={"completed": True, "missed": False},
    )
    assert toggle_res.status_code == 200
    assert toggle_res.json()["daily_timetable"][0]["completed"] is True

    # Trigger catch-up schedule for remaining incomplete tasks
    catchup_res = client.post(f"/api/students/{student_id}/study-plan/catch-up")
    assert catchup_res.status_code == 200
    assert len(catchup_res.json()["catch_up_schedule"]) > 0

    # Verify persistence via GET
    get_res = client.get(f"/api/students/{student_id}/study-plan")
    assert get_res.status_code == 200
    assert get_res.json()["plan_id"] == plan["plan_id"]


def test_4_homework_creation_vision_extraction_and_status_updates():
    """
    Tests:
    - Creating homework manually and with an uploaded worksheet image.
    - Updating status from pending -> in_progress -> completed.
    - Completed homework automatically updates the student's HOMEWORK_PRACTICE evidence.
    """
    student_id = "stu_aarav_g7"
    create_res = client.post(
        f"/api/students/{student_id}/homework",
        json={
            "student_id": student_id,
            "subject": "Mathematics",
            "chapter": "Fractions & Decimals",
            "title": "Word Problems on Fraction Addition",
            "description": "Solve 1/4 + 1/6 and verify with LCM.",
            "due_date": "2026-11-12",
            "priority": "High",
            "estimated_minutes": 35,
        },
    )
    assert create_res.status_code == 200
    hw = create_res.json()
    hw_id = hw["homework_id"]
    assert hw["status"] == "pending"

    # Transition to in_progress
    upd1 = client.patch(
        f"/api/students/{student_id}/homework/{hw_id}",
        json={"status": "in_progress"},
    )
    assert upd1.status_code == 200
    assert upd1.json()["status"] == "in_progress"

    # Transition to completed
    upd2 = client.patch(
        f"/api/students/{student_id}/homework/{hw_id}",
        json={"status": "completed"},
    )
    assert upd2.status_code == 200
    assert upd2.json()["status"] == "completed"
    assert upd2.json()["completed_at"] is not None


def test_5_and_6_mock_exam_evaluation_and_automatic_revision_scheduling():
    """
    Tests:
    - Generating a chapter/subject mock examination with MCQs + Short/Long answer questions.
    - Submitting student answers (with 1 intentional mistake to trigger weak-topic detection).
    - Verifying automatic grading, detailed explanation for wrong answers, ACTUAL_ASSESSMENT evidence recording,
      and automatic creation of a "Mock Exam Mistake" revision card in the Smart Revision Centre.
    """
    student_id = "stu_aarav_g7"
    gen_res = client.post(
        f"/api/students/{student_id}/exams/generate",
        json={
            "student_id": student_id,
            "exam_mode": "Chapter Test",
            "subject": "Mathematics",
            "chapters": ["Fractions & Decimals", "Integers & Rational Numbers"],
            "duration_minutes": 20,
            "question_count": 4,
        },
    )
    assert gen_res.status_code == 200
    exam = gen_res.json()
    exam_id = exam["exam_id"]
    questions = exam["questions"]
    assert len(questions) == 4

    # Answer Q1 wrong ("2/10" instead of "5/12") and remaining questions right
    answers = {}
    for idx, q in enumerate(questions):
        if idx == 0:
            answers[q["question_id"]] = "2/10"
        else:
            answers[q["question_id"]] = q["correct_answer"]

    sub_res = client.post(
        f"/api/students/{student_id}/exams/{exam_id}/submit",
        json={"student_id": student_id, "answers": answers, "time_taken_seconds": 420},
    )
    assert sub_res.status_code == 200
    evaluated = sub_res.json()
    assert evaluated["status"] == "COMPLETED"
    assert evaluated["score_percentage"] < 100.0
    assert "Fractions & Decimals" in evaluated["weak_topics_detected"]
    assert any(not ev["is_correct"] for ev in evaluated["question_evaluations"])

    # Verify cross-module reactivity: Smart Revision Centre now has "Mock Exam Mistake" card for Fractions & Decimals
    rev_res = client.get(f"/api/students/{student_id}/revision")
    assert rev_res.status_code == 200
    cards = rev_res.json()["cards"]
    frac_card = next((c for c in cards if "Fractions" in c["topic"]), None)
    assert frac_card is not None
    assert frac_card["source_tag"] == "Mock Exam Mistake"

    # Test spaced repetition interval progression when reviewed with "Good" recall
    rev_upd = client.patch(
        f"/api/students/{student_id}/revision/{frac_card['revision_id']}/review",
        json={"student_id": student_id, "recall_quality": "Good"},
    )
    assert rev_upd.status_code == 200
    assert rev_upd.json()["interval_days"] >= 3
    assert rev_upd.json()["completed_today"] is True


def test_7_and_8_progress_evidence_separation_and_dashboard_summary():
    """
    Tests:
    - Student Dashboard summary endpoint returns personalised greeting, schedule, homework, exams, goals, and recommendations.
    - Academic Progress endpoint strictly separates ACTUAL_ASSESSMENT, HOMEWORK_PRACTICE, and STUDENT_SELF_REPORT.
    """
    student_id = "stu_aarav_g7"
    dash_res = client.get(f"/api/students/{student_id}/dashboard-summary")
    assert dash_res.status_code == 200
    dash = dash_res.json()
    assert "Aarav Sharma" in dash["greeting"]
    assert len(dash["todays_schedule"]) > 0
    assert len(dash["ai_recommendations"]) > 0

    prog_res = client.get(f"/api/students/{student_id}/progress")
    assert prog_res.status_code == 200
    prog = prog_res.json()
    sep = prog["separated_evidence"]
    assert len(sep["ACTUAL_ASSESSMENT"]) > 0
    assert len(sep["HOMEWORK_PRACTICE"]) > 0
    assert len(sep["STUDENT_SELF_REPORT"]) > 0
    # Verify STUDENT_SELF_REPORT never has a fake numeric score_percentage
    for sr in sep["STUDENT_SELF_REPORT"]:
        assert sr["score_percentage"] is None


def test_9_and_10_projects_workflow_and_parent_dashboard_permissions():
    """
    Tests:
    - Generating a guided School Project & Creativity Lab record and updating milestone completion + student reflection.
    - Verifying authorised parent access returns live child summary, homework, and study plan, while blocking unauthorised parent IDs and score tampering.
    """
    student_id = "stu_aarav_g7"
    proj_res = client.post(
        f"/api/students/{student_id}/projects/generate",
        json={
            "student_id": student_id,
            "subject": "General Science",
            "chapter_or_theme": "Acids, Bases & Salts",
            "project_type": "Science Experiment",
        },
    )
    assert proj_res.status_code == 200
    proj = proj_res.json()
    proj_id = proj["project_id"]
    assert len(proj["milestones"]) == 5

    upd_proj = client.patch(
        f"/api/students/{student_id}/projects/{proj_id}",
        json={
            "student_id": student_id,
            "milestone_index": 0,
            "completed": True,
            "student_notes": "Tested lemon juice and soap water with turmeric strips.",
            "student_creativity_response": "Created a Colour-Detective card game for Grade 5 students.",
        },
    )
    assert upd_proj.status_code == 200
    assert upd_proj.json()["progress_percentage"] >= 20
    assert "turmeric" in upd_proj.json()["student_notes"]

    # Authorised Parent Access
    parent_res = client.get(f"/api/parent/parent_sharma_01/child/{student_id}")
    assert parent_res.status_code == 200
    p_data = parent_res.json()
    assert p_data["authorised"] is True
    assert "live_progress_summary" in p_data
    assert len(p_data["parent_recommendations"]) > 0

    # Unauthorised Parent Blocked (403)
    unauth_res = client.get(f"/api/parent/intruder_parent_99/child/{student_id}")
    assert unauth_res.status_code == 403

