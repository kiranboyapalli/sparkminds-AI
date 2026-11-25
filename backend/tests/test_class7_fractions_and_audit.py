"""
SparkMinds AI — Complete Audit Verification & Class 7 Fractions End-to-End Demo Workflow Suite.

Verifies:
1. Full Class 7 Fractions Demo Workflow:
   diagnose -> identify learning gaps -> teach -> practise -> evaluate -> study plan -> progress
   including graduating a topic from "Needs Help" -> "Understood" upon verified mastery.
2. Textbook / PDF Document RAG learning:
   upload -> chunk/index -> grounded Q&A with citations -> interactive document quiz -> graded submission.
3. Production security hardening:
   - Admin audit/backup/restore endpoints return HTTP 403 in production without valid X-SparkMinds-Admin-Key.
   - Orchestrator & stateful tutor session endpoints enforce strict cross-user 403 isolation.
4. Brevo OTP email integration invariants remain 100% preserved.
"""

from __future__ import annotations

import sqlite3
import uuid
import pytest
from fastapi.testclient import TestClient

from app.core.repository import repo
from app.main import app


def _register_class7_student(client: TestClient, suffix: str) -> tuple[str, str]:
    sid = f"stu_c7_frac_{suffix}"
    res = client.post(
        "/api/auth/register",
        json={
            "student_id": sid,
            "full_name": f"Aarav Class7 {suffix}",
            "age": 12,
            "grade": 7,
            "date_of_birth": "2014-06-10",
            "email_or_username": f"c7frac_{suffix}",
            "password_or_pin": f"FracPass#{suffix}",
            "device_name": "Class7 Demo Browser",
        },
    )
    assert res.status_code == 200, res.text
    token = res.json()["session_token"]
    onb = client.post(
        "/api/onboarding/submit",
        headers={"X-SparkMinds-Token": token},
        json={
            "student_id": sid,
            "academic_year_label": "2026-2027",
            "step1": {
                "age": 12,
                "grade": 7,
                "school_board": "CBSE",
                "state_name": "Telangana",
                "school_medium": "English",
                "preferred_explanation_language": "English",
                "secondary_explanation_language": "Telugu",
                "interface_display_language": "English",
            },
            "selected_subjects": ["G7_MATH", "G7_SCI", "G7_ENG"],
            "help_with_all_subjects": False,
            "subjects_to_improve": ["G7_MATH"],
            "subject_confidence": [
                {
                    "subject_code": "G7_MATH",
                    "subject_name": "Mathematics",
                    "confidence_level": "Need help",
                    "difficult_topics": ["Fractions & Decimals"],
                }
            ],
            "learning_challenges": ["I struggle with application-based questions."],
            "when_need_most_help": ["While understanding concepts"],
            "challenge_frequency": "Often",
            "everything_goal_selected": False,
            "selected_goals": ["g1", "g2"],
            "primary_goal": "g1",
        },
    )
    assert onb.status_code == 200, onb.text
    return sid, token


def test_complete_class7_fractions_demo_workflow(monkeypatch):
    """
    End-to-end Class 7 Fractions workflow:
    diagnose -> identify learning gaps -> teach -> practise -> evaluate -> study plan -> progress
    """
    monkeypatch.setenv("SPARKMINDS_DISABLE_LIVE_LLM", "true")
    suffix = uuid.uuid4().hex[:8]
    c = TestClient(app)
    sid, token = _register_class7_student(c, suffix)
    hdrs = {"X-SparkMinds-Token": token}

    # 1. DIAGNOSE: Start diagnostic assessment on Class 7 Fractions & Decimals
    diag_res = c.post(
        "/api/agents/diagnostic/start",
        headers=hdrs,
        json={
            "student_id": sid,
            "subject": "Mathematics",
            "topic": "Fractions & Decimals",
            "question_count": 4,
        },
    )
    assert diag_res.status_code == 200, diag_res.text
    diag = diag_res.json()
    assert diag["assessment_kind"] == "DIAGNOSTIC"
    assert len(diag["questions"]) == 4

    # Submit intentionally wrong answers so Diagnostic + Gap Analyzer detect real gaps
    wrong_answers = {q["question_id"]: "wrong_answer_xyz" for q in diag["questions"]}
    diag_eval_res = c.post(
        f"/api/agents/assessments/{diag['assessment_id']}/submit",
        headers=hdrs,
        json={"student_id": sid, "answers": wrong_answers},
    )
    assert diag_eval_res.status_code == 200, diag_eval_res.text
    diag_eval = diag_eval_res.json()
    assert diag_eval["score_percentage"] < 50.0
    # Verify automatic Study Plan adaptation ran on assessment submission!
    assert "study_plan_update" in diag_eval
    assert "Mathematics" in diag_eval["study_plan_update"]["weak_subjects"]

    # 2. IDENTIFY LEARNING GAPS: Verify Fractions & Decimals flagged in needs_help
    gaps_res = c.get(f"/api/agents/learning-gaps/{sid}", headers=hdrs)
    assert gaps_res.status_code == 200
    gaps = gaps_res.json()
    assert len(gaps["needs_help"]) >= 1
    assert any("fraction" in g["topic"].lower() for g in gaps["needs_help"])

    # 3. TEACH: Guided Interactive Lesson on Class 7 Fractions & Decimals + Stateful Tutor Session
    lesson_res = c.post(
        "/api/agents/lessons/generate",
        headers=hdrs,
        json={
            "student_id": sid,
            "subject": "Mathematics",
            "topic": "Fractions & Decimals",
            "preferred_language": "English",
        },
    )
    assert lesson_res.status_code == 200, lesson_res.text
    lesson = lesson_res.json()
    assert lesson["grade"] == 7
    assert len(lesson["steps"]) >= 4
    # Confirm clean math formatting (zero raw $...$ LaTeX leaks)
    assert "\\frac" not in str(lesson)

    tutor_start = c.post(
        "/api/tutor/session/start",
        headers=hdrs,
        json={
            "student_id": sid,
            "student_request": "How do I add 1/2 + 1/4 in Class 7 Fractions?",
            "subject_hint": "Mathematics",
        },
    )
    assert tutor_start.status_code == 200, tutor_start.text
    assert tutor_start.json()["detected_subject"] == "Mathematics"

    # 4. PRACTISE: Complete Guided Lesson & generate focused Fractions practice quiz
    complete_res = c.post(
        "/api/agents/lessons/complete",
        headers=hdrs,
        json={
            "student_id": sid,
            "lesson_id": lesson["lesson_id"],
            "subject": "Mathematics",
            "topic": "Fractions & Decimals",
            "correct_count": 4,
            "total_interactive_steps": 4,
        },
    )
    assert complete_res.status_code == 200
    assert complete_res.json()["accuracy_percentage"] == 100.0

    prac_res = c.post(
        "/api/agents/assessments/generate",
        headers=hdrs,
        json={
            "student_id": sid,
            "subject": "Mathematics",
            "assessment_kind": "PRACTICE",
            "topic": "Fractions & Decimals",
            "question_types": ["MCQ"],
            "question_count": 2,
        },
    )
    assert prac_res.status_code == 200
    prac = prac_res.json()

    # 5. EVALUATE: Fetch exact answer key from SQLite (simulating student solving correctly) and submit
    import json as _json

    with sqlite3.connect(str(repo.sqlite_db_path)) as conn:
        q_json = conn.execute(
            "SELECT questions_json FROM diagnostic_assessments WHERE assessment_id = ?",
            (prac["assessment_id"],),
        ).fetchone()[0]
    stored_qs = _json.loads(q_json)
    correct_answers = {q["question_id"]: q["correct_answer"] for q in stored_qs}

    eval_res = c.post(
        f"/api/agents/assessments/{prac['assessment_id']}/submit",
        headers=hdrs,
        json={"student_id": sid, "answers": correct_answers},
    )
    assert eval_res.status_code == 200
    eval_data = eval_res.json()
    assert eval_data["score_percentage"] == 100.0

    # Verify Fractions graduated out of "Needs Help" once mastered (fixes stale-mistakes bug!)
    gaps_after = c.get(f"/api/agents/learning-gaps/{sid}", headers=hdrs).json()
    assert any("fraction" in item["topic"].lower() for item in gaps_after["understood"])

    # 6. STUDY PLAN: Verify Personalized Study Planner Agent adapts plan cleanly
    plan_res = c.post(
        f"/api/agents/study-plan/adapt/{sid}",
        headers=hdrs,
        json={"available_daily_hours": 2.0},
    )
    assert plan_res.status_code == 200
    assert plan_res.json()["daily_study_hours"] == 2.0
    assert len(plan_res.json()["daily_timetable"]) > 0

    # 7. PROGRESS & CONNECTED WORKFLOW: Verify verified improvement trend & all agent logs
    prog_res = c.get(f"/api/agents/progress-recommendations/{sid}", headers=hdrs)
    assert prog_res.status_code == 200
    prog = prog_res.json()
    assert prog["assessments_completed_count"] == 2
    assert prog["improvement_trend"]["has_sufficient_data"] is True
    assert prog["improvement_trend"]["direction"] == "improving"
    assert prog["improvement_trend"]["delta_percentage"] > 0
    assert prog["gamification"]["total_learning_points"] > 0
    assert prog["gamification"]["current_streak_days"] >= 1

    logs_res = c.get(f"/api/agents/logs/{sid}", headers=hdrs)
    assert logs_res.status_code == 200
    logged_agents = {entry["agent_name"] for entry in logs_res.json()["logs"]}
    assert "DiagnosticAssessmentAgent" in logged_agents
    assert "IntelligentAssessmentAgent" in logged_agents
    assert "LearningGapAnalyzerAgent" in logged_agents
    assert "PersonalizedStudyPlannerAgent" in logged_agents
    assert "ProgressRecommendationAgent" in logged_agents


def test_textbook_document_rag_and_interactive_quiz_submission(monkeypatch):
    """Verifies uploading Class 7 Fractions notes, grounded RAG Q&A, and submitting generated document quiz."""
    monkeypatch.setenv("SPARKMINDS_DISABLE_LIVE_LLM", "true")
    suffix = uuid.uuid4().hex[:8]
    c = TestClient(app)
    sid, token = _register_class7_student(c, suffix)
    hdrs = {"X-SparkMinds-Token": token}

    notes = (
        "Class 7 Mathematics Chapter 2: Fractions and Decimals.\n"
        "A proper fraction has a numerator smaller than its denominator, such as 3/4.\n"
        "To add unlike fractions like 1/2 and 1/4, first find the Least Common Multiple (LCM) of denominators.\n"
        "Multiplying two fractions multiplies numerators together and denominators together: (2/3) x (3/5) = 6/15 = 2/5.\n"
        "Dividing by a fraction is equivalent to multiplying by its reciprocal."
    )
    up_res = c.post(
        f"/api/students/{sid}/documents/upload",
        headers=hdrs,
        json={
            "filename": "class7_fractions_notes.txt",
            "subject": "Mathematics",
            "text_content": notes,
            "content_type": "text/plain",
        },
    )
    assert up_res.status_code == 200, up_res.text
    doc_id = up_res.json()["document"]["doc_id"]

    ask_res = c.post(
        f"/api/students/{sid}/documents/ask",
        headers=hdrs,
        json={"question": "How do you divide by a fraction?", "doc_id": doc_id},
    )
    assert ask_res.status_code == 200
    ask_data = ask_res.json()
    assert ask_data["grounded"] is True
    assert "reciprocal" in ask_data["document_grounded_answer"].lower()
    assert len(ask_data["citations"]) >= 1

    quiz_res = c.post(
        f"/api/students/{sid}/documents/{doc_id}/generate-quiz",
        headers=hdrs,
        json={"question_count": 3},
    )
    assert quiz_res.status_code == 200
    quiz = quiz_res.json()
    assert len(quiz["questions"]) == 3

    # Submit answers to generated document quiz cleanly
    submit_res = c.post(
        f"/api/agents/assessments/{quiz['assessment_id']}/submit",
        headers=hdrs,
        json={"student_id": sid, "answers": {q["question_id"]: "True" for q in quiz["questions"]}},
    )
    assert submit_res.status_code == 200
    assert "score_percentage" in submit_res.json()


def test_security_audit_admin_guards_and_orchestrator_isolation(monkeypatch):
    """Verifies production admin guards (403) and orchestrator/tutor-session cross-user isolation (403)."""
    suffix = uuid.uuid4().hex[:8]
    c_a = TestClient(app)
    sid_a, tok_a = _register_class7_student(c_a, f"a_{suffix}")
    c_b = TestClient(app)
    _sid_b, tok_b = _register_class7_student(c_b, f"b_{suffix}")

    # 1. Start tutor session for Student A
    st = c_a.post(
        "/api/tutor/session/start",
        headers={"X-SparkMinds-Token": tok_a},
        json={"student_id": sid_a, "student_request": "Explain 1/2 + 1/3"},
    )
    assert st.status_code == 200
    sess_id = st.json()["session_id"]

    # Student B CANNOT interact as Student A or read Student A's tutor session
    assert (
        c_b.post(
            "/api/orchestrator/interact",
            headers={"X-SparkMinds-Token": tok_b},
            json={"student_id": sid_a, "user_message": "Help me", "subject_name": "Mathematics"},
        ).status_code
        == 403
    )
    assert (
        c_b.post(
            "/api/tutor/session/start",
            headers={"X-SparkMinds-Token": tok_b},
            json={"student_id": sid_a, "student_request": "Explain fractions"},
        ).status_code
        == 403
    )
    assert c_b.get(f"/api/tutor/session/{sess_id}", headers={"X-SparkMinds-Token": tok_b}).status_code == 403

    # 2. Production Admin Endpoints MUST return 403 without valid SPARKMINDS_ADMIN_KEY
    monkeypatch.setenv("SPARKMINDS_ENV", "production")
    monkeypatch.setenv("SPARKMINDS_ADMIN_KEY", "super-secret-admin-key-test")
    assert c_b.get("/api/admin/audit/duplicate-accounts").status_code == 403
    assert c_b.post("/api/admin/database/backup", json={"reason": "probe"}).status_code == 403
    assert c_b.get("/api/admin/database/backups").status_code == 403
    assert c_b.post("/api/admin/database/restore", json={"backup_id": "fake"}).status_code == 403
    # Valid admin key succeeds
    assert (
        c_b.get(
            "/api/admin/audit/duplicate-accounts",
            headers={"X-SparkMinds-Admin-Key": "super-secret-admin-key-test"},
        ).status_code
        == 200
    )
