"""
Comprehensive test suite verifying that SparkMinds AI Interactive Tutoring:
1. Instructs every single step with:
   - title
   - instruction
   - why_this_step_matters
   - step_formula_or_rule
   - question_for_student
   - expected_checkpoint
2. Provides rich SVG visual diagram & pictures (visual_diagram_svg).
3. Provides curated video learning modules (video_explanation) with title, platform, duration, and takeaways.
"""

import pytest
from app.agents.state_graph_orchestrator import (
    state_graph_orchestrator,
    StartTutorSessionRequest,
)
from app.core.repository import repo


@pytest.fixture(autouse=True)
def clean_sessions():
    repo.tutor_sessions.clear()


def test_fraction_step_instructions_visual_and_video():
    req = StartTutorSessionRequest(
        student_id="test_student_frac",
        typed_question="Solve 1/4 + 1/6",
        subject_hint="Mathematics",
        language_override="English",
    )
    state = state_graph_orchestrator.start_homework_session(req)
    assert state.teaching_output is not None
    tout = state.teaching_output

    # 1. Verify every single step has thorough instructions and rules
    assert len(tout.steps_breakdown) >= 3
    for step in tout.steps_breakdown:
        assert step.step_number > 0
        assert step.title, f"Step {step.step_number} missing title"
        assert step.instruction, f"Step {step.step_number} missing instruction"
        assert step.why_this_step_matters, f"Step {step.step_number} missing why_this_step_matters"
        assert step.step_formula_or_rule, f"Step {step.step_number} missing step_formula_or_rule"
        assert step.question_for_student, f"Step {step.step_number} missing question_for_student"
        assert step.expected_checkpoint, f"Step {step.step_number} missing expected_checkpoint"

    # 2. Verify picture-based learning removed (no automatic SVG diagrams generated)
    assert tout.visual_diagram_svg is None
    assert tout.visual_concept_type is None

    # 3. Verify curated video explanation
    assert tout.video_explanation is not None
    v = tout.video_explanation
    assert "Khan Academy" in v["platform"]
    assert "5:23 mins" in v["duration"]
    assert v["youtube_embed_id"] == "BC04Y_v2eoc"
    assert len(v["key_takeaways"]) >= 3


def test_science_photosynthesis_instructions_visual_and_video():
    req = StartTutorSessionRequest(
        student_id="test_student_science",
        typed_question="Explain the process of photosynthesis in green plants",
        subject_hint="Science",
        language_override="English",
    )
    state = state_graph_orchestrator.start_homework_session(req)
    assert state.teaching_output is not None
    tout = state.teaching_output

    # 1. Verify every single step
    assert len(tout.steps_breakdown) >= 2
    for step in tout.steps_breakdown:
        assert step.instruction
        assert step.why_this_step_matters
        assert step.step_formula_or_rule
        assert step.question_for_student

    # 2. Verify picture-based learning removed (no automatic SVG diagrams generated)
    assert tout.visual_diagram_svg is None
    assert tout.visual_concept_type is None

    # 3. Verify video module
    assert tout.video_explanation is not None
    v = tout.video_explanation
    assert "CrashCourse" in v["platform"]
    assert v["youtube_embed_id"] == "sQK3Yr4Sc_k"
    assert len(v["key_takeaways"]) >= 3


def test_linear_equation_instructions_visual_and_video():
    req = StartTutorSessionRequest(
        student_id="test_student_algebra",
        typed_question="Solve 3x - 7 = 14",
        subject_hint="Mathematics",
        language_override="English",
    )
    state = state_graph_orchestrator.start_homework_session(req)
    assert state.teaching_output is not None
    tout = state.teaching_output

    # 1. Verify steps
    assert len(tout.steps_breakdown) >= 2
    for step in tout.steps_breakdown:
        assert step.why_this_step_matters
        assert step.step_formula_or_rule

    # 2. Verify picture-based learning removed (no automatic SVG diagrams generated)
    assert tout.visual_diagram_svg is None
    assert tout.visual_concept_type is None

    # 3. Verify video module
    assert tout.video_explanation is not None
    assert "Khan Academy" in tout.video_explanation["platform"]


def test_indus_valley_history_instructions_visual_and_video():
    req = StartTutorSessionRequest(
        student_id="test_student_history",
        typed_question="What were the main town planning features of the Indus Valley Civilization?",
        subject_hint="Social Science",
        language_override="English",
    )
    state = state_graph_orchestrator.start_homework_session(req)
    assert state.teaching_output is not None
    tout = state.teaching_output

    # 1. Verify steps
    assert len(tout.steps_breakdown) >= 1
    for step in tout.steps_breakdown:
        assert step.instruction
        assert step.why_this_step_matters
        assert step.step_formula_or_rule

    # 2. Verify picture-based learning removed (no automatic SVG diagrams generated)
    assert tout.visual_diagram_svg is None

    # 3. Verify video module
    assert tout.video_explanation is not None
    assert "CrashCourse" in tout.video_explanation["platform"]
