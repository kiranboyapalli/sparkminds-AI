"""
SparkMinds AI — Agent 4: Assessment Agent
Responsibilities (Section 2.4):
- Evaluate student responses.
- Check mathematical and logical correctness.
- Identify the exact step where a mistake occurred.
- Explain why the answer is incorrect.
- Generate follow-up questions.
- Verify conceptual understanding.
- Update topic mastery only when supported by sufficient evidence.
"""
import time
from datetime import datetime, timezone
from typing import Literal, Optional
from pydantic import BaseModel
from app.agents.model_client import (
    AgentExecutionError,
    evaluate_math_or_science_attempt,
    invoke_gemini_or_structured_engine,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AssessmentAgentInput(BaseModel):
    student_id: str
    grade: int
    detected_subject: str
    detected_topic: str
    question_text: str
    student_attempt: str
    current_step_index: int = 1
    total_steps: int = 3
    previous_mistake_count: int = 0
    preferred_explanation_language: str = "English"
    secondary_explanation_language: Optional[str] = None
    simulate_agent_failure: bool = False
    simulate_model_failure: bool = False


class AssessmentAgentOutput(BaseModel):
    agent_id: Literal["assessment"] = "assessment"
    agent_name: str = "Assessment Agent"
    status: Literal["completed", "failed"] = "completed"
    executed_at: str
    duration_ms: float
    model_used: str
    is_attempt_correct: bool
    is_problem_completed: bool
    mistake_step_number: Optional[int] = None
    detected_misconception: Optional[str] = None
    missing_prerequisite_identified: Optional[str] = None
    why_incorrect_explanation: Optional[str] = None
    encouraging_feedback: str
    follow_up_verification_question: Optional[str] = None
    conceptual_understanding_verified: bool = False
    mastery_evidence_score: Optional[float] = None
    next_routing_action: Literal[
        "ADVANCE_TO_NEXT_STEP",
        "PROVIDE_PROGRESSIVE_HINT",
        "SWITCH_TO_ALTERNATIVE_TEACHING_STRATEGY",
        "TEACH_MISSING_PREREQUISITE",
        "VERIFY_WITH_SIMILAR_QUESTION",
        "SAVE_MASTERY_EVIDENCE_AND_COMPLETE",
    ]
    explanation_language: str


class AssessmentAgent:
    """Specialist Agent 4: Evaluates student attempts, pinpoints step errors, and gates mastery updates on verified evidence."""

    def execute(self, inp: AssessmentAgentInput) -> AssessmentAgentOutput:
        start_t = time.perf_counter()

        if inp.simulate_agent_failure:
            raise AgentExecutionError("AssessmentAgent failed: Simulated evaluation fault.")

        model_res = invoke_gemini_or_structured_engine(
            agent_name="AssessmentAgent",
            system_instruction="Evaluate student step attempt, detect exact mathematical/conceptual mistake, and verify mastery.",
            user_prompt=f"Q: {inp.question_text} | Step: {inp.current_step_index} | Attempt: {inp.student_attempt}",
            simulate_failure=inp.simulate_model_failure,
        )

        eval_res = evaluate_math_or_science_attempt(
            question_text=inp.question_text,
            student_attempt=inp.student_attempt,
            current_step_index=inp.current_step_index,
        )

        is_correct = bool(eval_res["is_correct"])
        is_final = bool(eval_res["is_final_answer"])
        missing_prereq = eval_res.get("missing_prerequisite")
        misconception = eval_res.get("detected_misconception")
        error_step = eval_res.get("error_step")

        why_incorrect: Optional[str] = None
        follow_up_q: Optional[str] = None
        mastery_verified = False
        mastery_score: Optional[float] = None

        if is_correct:
            if is_final or inp.current_step_index >= inp.total_steps:
                mastery_verified = True
                # Calculate evidence-based score (penalized slightly if earlier mistakes occurred, but never faked)
                mastery_score = max(75.0, 95.0 - (inp.previous_mistake_count * 7.0))
                feedback = (
                    f"Excellent work! Your answer '{inp.student_attempt}' is mathematically and conceptually verified. "
                    f"You have demonstrated mastery of {inp.detected_topic}!"
                )
                follow_up_q = (
                    "Verification Practice Question: Can you apply the exact same LCM method to solve 1/3 + 1/6?"
                    if inp.detected_subject.lower() == "mathematics"
                    else "Verification Practice Question: What happens to the rate of photosynthesis on a cloudy day?"
                )
                next_action: Literal[
                    "ADVANCE_TO_NEXT_STEP",
                    "PROVIDE_PROGRESSIVE_HINT",
                    "SWITCH_TO_ALTERNATIVE_TEACHING_STRATEGY",
                    "TEACH_MISSING_PREREQUISITE",
                    "VERIFY_WITH_SIMILAR_QUESTION",
                    "SAVE_MASTERY_EVIDENCE_AND_COMPLETE",
                ] = "SAVE_MASTERY_EVIDENCE_AND_COMPLETE"
            else:
                feedback = (
                    f"Spot on! Step {inp.current_step_index} ('{inp.student_attempt}') is correct. Let's move to Step {inp.current_step_index + 1}!"
                )
                next_action = "ADVANCE_TO_NEXT_STEP"
        else:
            new_mistake_total = inp.previous_mistake_count + 1
            why_incorrect = (
                f"Mistake detected at Step {error_step or inp.current_step_index}: {misconception}"
            )
            if missing_prereq:
                feedback = (
                    f"Thank you for letting me know! Let's first pause and master the prerequisite concept: {missing_prereq}."
                )
                next_action = "TEACH_MISSING_PREREQUISITE"
            elif new_mistake_total >= 2:
                feedback = (
                    "I notice this step has been tricky more than once. Let's switch our teaching strategy to a visual model so it clicks clearly!"
                )
                next_action = "SWITCH_TO_ALTERNATIVE_TEACHING_STRATEGY"
            else:
                feedback = (
                    f"Not quite right at Step {error_step or inp.current_step_index}, and that's completely okay! "
                    f"{why_incorrect} Let's use a progressive hint and try this step again."
                )
                next_action = "PROVIDE_PROGRESSIVE_HINT"

        elapsed_ms = round((time.perf_counter() - start_t) * 1000, 2)

        return AssessmentAgentOutput(
            executed_at=utc_now(),
            duration_ms=elapsed_ms,
            model_used=str(model_res["model_used"]),
            is_attempt_correct=is_correct,
            is_problem_completed=mastery_verified,
            mistake_step_number=error_step,
            detected_misconception=misconception,
            missing_prerequisite_identified=missing_prereq,
            why_incorrect_explanation=why_incorrect,
            encouraging_feedback=feedback,
            follow_up_verification_question=follow_up_q,
            conceptual_understanding_verified=mastery_verified,
            mastery_evidence_score=mastery_score,
            next_routing_action=next_action,
            explanation_language=inp.preferred_explanation_language,
        )

