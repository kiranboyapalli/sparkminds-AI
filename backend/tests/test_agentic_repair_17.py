"""
EDUSPARK AI — Comprehensive 17-Scenario Automated Test Suite (Section 9)
Tests every specialist agent independently AND tests the complete Stateful Graph Orchestrator end to end:

1. Image-based mathematics homework.
2. Text-based science homework.
3. English explanation.
4. Telugu explanation.
5. Bilingual explanation.
6. Identifying missing prerequisite knowledge.
7. Correct student responses.
8. Incorrect student responses.
9. Progressive hints.
10. Alternative explanations.
11. Repeated student mistakes.
12. Similar practice question generation.
13. Historical learning context retrieval.
14. Database updates (LearningMemory & AcademicYearProfile).
15. Agent failures (Never marks failed agent as completed).
16. Model API failures (Explicit error propagation).
17. Orchestrator conditional routing (Unclear question, prerequisite routing, practice routing, remediation routing).
"""
import base64
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _create_svg_homework_image_base64(problem_text: str = "1/4 + 1/6") -> str:
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="80"><text x="10" y="40">{problem_text}</text></svg>'
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("utf-8")


# ============================================================================
# 1. IMAGE-BASED MATHEMATICS HOMEWORK
# ============================================================================
def test_01_image_based_mathematics_homework():
    img_b64 = _create_svg_homework_image_base64("1/4 + 1/6")
    res = client.post(
        "/api/tutor/session/start",
        json={
            "student_id": "stu_aarav_g7",
            "image_base64": img_b64,
            "subject_hint": "Mathematics",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["understanding_output"]["processed_from_image"] is True
    assert "1/4 + 1/6" in data["extracted_question"]
    assert data["detected_subject"] == "Mathematics"
    assert data["detected_topic"] == "Fractions & Decimals"
    # Verify Assessment Agent was NOT called prematurely on session start
    assert data["assessment_output"] is None
    assert data["teaching_output"]["answer_withheld_for_guided_learning"] is True


# ============================================================================
# 2. TEXT-BASED SCIENCE HOMEWORK
# ============================================================================
def test_02_text_based_science_homework():
    res = client.post(
        "/api/tutor/session/start",
        json={
            "student_id": "stu_aarav_g7",
            "typed_question": "Explain the role of chlorophyll and sunlight in photosynthesis.",
            "subject_hint": "Science",
            "language_override": "English",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["detected_subject"] == "Science"
    assert "Nutrition in Plants" in data["detected_topic"]
    assert "Chlorophyll" in data["teaching_output"]["real_world_example"]


# ============================================================================
# 3. ENGLISH EXPLANATION
# ============================================================================
def test_03_english_explanation():
    res = client.post(
        "/api/tutor/session/start",
        json={
            "student_id": "stu_aarav_g7",
            "typed_question": "Solve 1/4 + 1/6",
            "language_override": "English",
            "secondary_language_override": "",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["teaching_output"]["explanation_language"] == "English"
    assert "Least Common Multiple (LCM)" in data["teaching_output"]["concept_explanation"]


# ============================================================================
# 4. TELUGU EXPLANATION
# ============================================================================
def test_04_telugu_explanation():
    res = client.post(
        "/api/tutor/session/start",
        json={
            "student_id": "stu_aarav_g7",
            "typed_question": "Solve 1/4 + 1/6",
            "language_override": "Telugu",
            "secondary_language_override": "",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["teaching_output"]["explanation_language"] == "Telugu"
    assert "తెలుగు" in data["teaching_output"]["concept_explanation"]
    assert "క.సా.గు" in data["teaching_output"]["concept_explanation"]


# ============================================================================
# 5. BILINGUAL EXPLANATION
# ============================================================================
def test_05_bilingual_explanation():
    res = client.post(
        "/api/tutor/session/start",
        json={
            "student_id": "stu_aarav_g7",
            "typed_question": "Solve 1/4 + 1/6",
            "language_override": "Telugu",
            "secondary_language_override": "English",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["teaching_output"]["bilingual_active"] is True
    assert "తెలుగు" in data["teaching_output"]["concept_explanation"]
    assert "[English Bilingual Explanation]" in data["teaching_output"]["bilingual_secondary_explanation"]


# ============================================================================
# 6. IDENTIFYING MISSING PREREQUISITE KNOWLEDGE
# ============================================================================
def test_06_identifying_missing_prerequisite_knowledge():
    res = client.post(
        "/api/tutor/session/start",
        json={
            "student_id": "stu_aarav_g7",
            "typed_question": "I need to add 1/4 + 1/6 but I don't know LCM",
            "language_override": "English",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["diagnosis_output"]["missing_prerequisite_detected"] is True
    assert "LCM" in data["diagnosis_output"]["missing_prerequisite_topic"]
    assert data["conditional_route_taken"] == "MISSING_PREREQUISITE_TEACH_PREREQUISITE_FIRST"
    assert data["teaching_output"]["prerequisite_mini_lesson"] is not None


# ============================================================================
# 7. CORRECT STUDENT RESPONSES (STEP-BY-STEP ADVANCEMENT & FINAL MASTERY)
# ============================================================================
def test_07_correct_student_responses():
    start = client.post(
        "/api/tutor/session/start",
        json={"student_id": "stu_aarav_g7", "typed_question": "Solve 1/4 + 1/6", "language_override": "English"},
    ).json()
    sid = start["session_id"]

    # Step 1 attempt: LCM = 12 (Correct intermediate step)
    turn1 = client.post(
        "/api/tutor/session/turn",
        json={"session_id": sid, "student_id": "stu_aarav_g7", "student_attempt": "12"},
    ).json()
    assert turn1["assessment_output"]["is_attempt_correct"] is True
    assert turn1["assessment_output"]["next_routing_action"] == "ADVANCE_TO_NEXT_STEP"
    assert turn1["current_step_index"] == 2

    # Final answer attempt: 5/12 (Completes problem & verifies mastery)
    turn_final = client.post(
        "/api/tutor/session/turn",
        json={"session_id": sid, "student_id": "stu_aarav_g7", "student_attempt": "5/12"},
    ).json()
    assert turn_final["assessment_output"]["is_attempt_correct"] is True
    assert turn_final["assessment_output"]["conceptual_understanding_verified"] is True
    assert turn_final["current_node"] == "MASTERY_VERIFIED_COMPLETED"


# ============================================================================
# 8. INCORRECT STUDENT RESPONSES (EXACT MISCONCEPTION PINPOINTING)
# ============================================================================
def test_08_incorrect_student_responses():
    start = client.post(
        "/api/tutor/session/start",
        json={"student_id": "stu_aarav_g7", "typed_question": "Solve 1/4 + 1/6", "language_override": "English"},
    ).json()
    sid = start["session_id"]

    # Student adds denominators directly: 1/4 + 1/6 = 2/10
    turn = client.post(
        "/api/tutor/session/turn",
        json={"session_id": sid, "student_id": "stu_aarav_g7", "student_attempt": "2/10"},
    ).json()
    assert turn["assessment_output"]["is_attempt_correct"] is False
    assert "Added denominators directly" in turn["assessment_output"]["detected_misconception"]
    assert turn["assessment_output"]["mistake_step_number"] == 1
    assert turn["teaching_output"]["incorrect_answer_explanation"] is not None


# ============================================================================
# 9. PROGRESSIVE HINTS (LEVEL 1 -> LEVEL 2 -> LEVEL 3)
# ============================================================================
def test_09_progressive_hints():
    start = client.post(
        "/api/tutor/session/start",
        json={"student_id": "stu_aarav_g7", "typed_question": "Solve 1/4 + 1/6", "language_override": "English"},
    ).json()
    sid = start["session_id"]

    h1 = client.post(
        "/api/tutor/session/turn",
        json={"session_id": sid, "student_id": "stu_aarav_g7", "action_type": "REQUEST_PROGRESSIVE_HINT"},
    ).json()
    assert h1["hint_level"] == 1
    assert "Hint 1" in h1["teaching_output"]["active_hint_shown"]

    h2 = client.post(
        "/api/tutor/session/turn",
        json={"session_id": sid, "student_id": "stu_aarav_g7", "action_type": "REQUEST_PROGRESSIVE_HINT"},
    ).json()
    assert h2["hint_level"] == 2
    assert "Hint 2" in h2["teaching_output"]["active_hint_shown"]


# ============================================================================
# 10 & 11. REPEATED STUDENT MISTAKES -> ALTERNATIVE EXPLANATIONS
# ============================================================================
def test_10_and_11_repeated_mistakes_trigger_alternative_explanation():
    start = client.post(
        "/api/tutor/session/start",
        json={"student_id": "stu_aarav_g7", "typed_question": "Solve 1/4 + 1/6", "language_override": "English"},
    ).json()
    sid = start["session_id"]

    # Mistake 1 -> Progressive Hint
    m1 = client.post(
        "/api/tutor/session/turn",
        json={"session_id": sid, "student_id": "stu_aarav_g7", "student_attempt": "2/10"},
    ).json()
    assert m1["mistake_count"] == 1
    assert m1["conditional_route_taken"] == "PROVIDE_PROGRESSIVE_HINT"

    # Mistake 2 -> Automatically switches to Alternative Visual Teaching Strategy
    m2 = client.post(
        "/api/tutor/session/turn",
        json={"session_id": sid, "student_id": "stu_aarav_g7", "student_attempt": "2/12"},
    ).json()
    assert m2["mistake_count"] == 2
    assert m2["conditional_route_taken"] == "SWITCH_TO_ALTERNATIVE_TEACHING_STRATEGY"
    assert m2["teaching_output"]["alternative_explanation"] is not None
    assert "12-box chocolate bar" in m2["teaching_output"]["alternative_explanation"]


# ============================================================================
# 12. SIMILAR PRACTICE QUESTION GENERATION
# ============================================================================
def test_12_similar_practice_question_generation():
    start = client.post(
        "/api/tutor/session/start",
        json={"student_id": "stu_aarav_g7", "typed_question": "Solve 1/4 + 1/6", "language_override": "English"},
    ).json()
    sid = start["session_id"]

    prac = client.post(
        "/api/tutor/session/turn",
        json={"session_id": sid, "student_id": "stu_aarav_g7", "action_type": "REQUEST_SIMILAR_PRACTICE"},
    ).json()
    assert "1/3 + 1/6" in prac["teaching_output"]["similar_practice_question"]["question"]


# ============================================================================
# 13 & 14. HISTORICAL LEARNING CONTEXT RETRIEVAL & DATABASE UPDATES
# ============================================================================
def test_13_and_14_historical_context_and_database_memory_updates():
    start = client.post(
        "/api/tutor/session/start",
        json={"student_id": "stu_aarav_g7", "typed_question": "Solve 1/4 + 1/6", "language_override": "Telugu"},
    ).json()
    sid = start["session_id"]

    # Check historical context retrieved by Diagnosis Agent (distinguishing verified vs self-report)
    diag = start["diagnosis_output"]
    assert len(diag["verified_learning_evidence"]) >= 2
    assert len(diag["student_self_reported_difficulties"]) >= 1

    # Submit wrong attempt then right attempt and verify LearningMemory database persistence
    client.post(
        "/api/tutor/session/turn",
        json={"session_id": sid, "student_id": "stu_aarav_g7", "student_attempt": "2/10"},
    )
    client.post(
        "/api/tutor/session/turn",
        json={"session_id": sid, "student_id": "stu_aarav_g7", "student_attempt": "5/12"},
    )

    mem_res = client.get("/api/students/stu_aarav_g7/learning-memory").json()
    assert mem_res["count"] >= 1
    latest_mem = next(m for m in mem_res["records"] if m["session_id"] == sid)
    assert latest_mem["assessment_result"] == "mastery_verified"
    assert "2/10" in latest_mem["student_attempts"]
    assert "5/12" in latest_mem["student_attempts"]
    assert len(latest_mem["detected_misconceptions"]) >= 1


# ============================================================================
# 15 & 16. AGENT FAILURES & MODEL API FAILURES (NEVER FAKE SUCCESS)
# ============================================================================
def test_15_and_16_agent_and_model_api_failures_never_fake_success():
    # Test 15: Simulated Agent Failure
    fail_agent = client.post(
        "/api/tutor/session/start",
        json={
            "student_id": "stu_aarav_g7",
            "typed_question": "Solve 1/4 + 1/6",
            "simulate_agent_failure": "diagnosis",
        },
    ).json()
    assert fail_agent["current_node"] == "ERROR_HALTED"
    assert fail_agent["error_state"] is not None
    assert any(log["status"] == "failed" for log in fail_agent["execution_logs"])

    # Test 16: Simulated Model API Failure
    fail_model = client.post(
        "/api/tutor/session/start",
        json={
            "student_id": "stu_aarav_g7",
            "typed_question": "Solve 1/4 + 1/6",
            "simulate_model_failure": True,
        },
    ).json()
    assert fail_model["current_node"] == "ERROR_HALTED"
    assert "Model API invocation failed" in fail_model["error_state"]
    assert fail_model["execution_logs"][0]["status"] == "failed"


# ============================================================================
# 17. ORCHESTRATOR CONDITIONAL ROUTING (UNCLEAR QUESTION & DIRECT PRACTICE)
# ============================================================================
def test_17_orchestrator_conditional_routing():
    # Route A: Unclear question -> Halts after UnderstandingAgent and requests clarification
    unclear = client.post(
        "/api/tutor/session/start",
        json={"student_id": "stu_aarav_g7", "typed_question": "?"},
    ).json()
    assert unclear["current_node"] == "AWAITING_CLARIFICATION"
    assert unclear["conditional_route_taken"] == "UNCLEAR_QUESTION_REQUEST_CLARIFICATION"
    # Verify Diagnosis, Teaching, and Assessment agents were NOT called!
    assert len(unclear["execution_logs"]) == 1
    assert unclear["diagnosis_output"] is None
    assert unclear["teaching_output"] is None

    # Route B: Student already understands concept -> Routes directly to practice
    practice_route = client.post(
        "/api/tutor/session/start",
        json={
            "student_id": "stu_aarav_g7",
            "typed_question": "I already understand integers, give me a practice question.",
        },
    ).json()
    assert practice_route["conditional_route_taken"] == "ALREADY_UNDERSTANDS_MOVE_TO_PRACTICE"
    assert practice_route["teaching_output"]["pedagogical_mode_applied"] == "SIMILAR_PRACTICE_QUESTION"

