import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.state_graph_orchestrator import (
    state_graph_orchestrator,
    StartTutorSessionRequest,
    SubmitStudentAttemptRequest,
)

test_questions = [
    ("Mathematics", "Solve 1/4 + 1/6"),
    ("Mathematics", "Find HCF of 12 and 18"),
    ("Mathematics", "Find LCM of 4 and 6"),
    ("Mathematics", "Solve 3x - 7 = 14"),
    ("Mathematics", "Calculate 15 + 27"),
    ("Science", "Explain the role of chlorophyll and sunlight in photosynthesis"),
    ("Biology", "What is the function of mitochondria in animal cells?"),
    ("Social Science", "Why was the Indus Valley Civilization famous for urban planning?"),
    ("English", "What is a metaphor and how is it used in poetry?"),
    ("Computer Science", "Explain how a for loop works in Python programming"),
]

print("=== TESTING ALL AGENTS ON 10 DIVERSE SUBJECTS & QUESTION TYPES ===")
all_passed = True

for subject, q in test_questions:
    try:
        # Step 1: Start session
        req = StartTutorSessionRequest(
            student_id="test_student_all_types",
            typed_question=q,
            subject_hint=subject,
            language_override="English",
        )
        s = state_graph_orchestrator.start_homework_session(req)
        assert s.session_id, "Missing session_id"
        assert s.teaching_output, "Missing teaching_output"
        assert len(s.teaching_output.steps_breakdown) > 0, "No steps generated"
        assert s.teaching_output.prompt_for_student_attempt, "No student prompt"

        # Step 2: Submit turn
        turn = SubmitStudentAttemptRequest(
            session_id=s.session_id,
            student_id="test_student_all_types",
            action_type="SUBMIT_STEP_ATTEMPT",
            student_attempt="My test answer for this step",
        )
        s2 = state_graph_orchestrator.process_student_turn(turn)
        assert s2.assessment_output, "Missing assessment_output"
        assert s2.assessment_output.encouraging_feedback, "Missing feedback"

        # Step 3: Request progressive hint
        hint_turn = SubmitStudentAttemptRequest(
            session_id=s.session_id,
            student_id="test_student_all_types",
            action_type="REQUEST_PROGRESSIVE_HINT",
        )
        s3 = state_graph_orchestrator.process_student_turn(hint_turn)
        assert s3.teaching_output.active_hint_shown, "Missing active hint"

        # Step 4: Request alternative explanation
        alt_turn = SubmitStudentAttemptRequest(
            session_id=s.session_id,
            student_id="test_student_all_types",
            action_type="REQUEST_ALTERNATIVE_EXPLANATION",
        )
        s4 = state_graph_orchestrator.process_student_turn(alt_turn)
        assert s4.teaching_output.alternative_explanation, "Missing alternative explanation"

        print(f"✓ [{subject}] '{q[:40]}...' passed all 4 agent steps successfully!")
    except Exception as e:
        print(f"✗ [{subject}] '{q}' FAILED: {e}")
        all_passed = False

if all_passed:
    print("\nALL 10 PROBLEM TYPES PASSED ACROSS ALL 4 AGENTS!")
else:
    raise SystemExit(1)
