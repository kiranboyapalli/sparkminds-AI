"""
SparkMinds AI — Agent 1: Understanding Agent
Responsibilities (Section 2.1):
- Accept typed questions.
- Process uploaded homework images using vision-capable AI.
- Extract questions accurately.
- Identify subject, grade and topic.
- Understand the student's actual request.
- Retrieve relevant curriculum context.
"""
import time
from datetime import datetime, timezone
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from app.curriculum_data.india_curriculum import get_subjects_for_grade_and_board
from app.agents.model_client import (
    AgentExecutionError,
    extract_homework_from_image_payload,
    invoke_gemini_or_structured_engine,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class UnderstandingAgentInput(BaseModel):
    student_id: str
    grade: int = Field(..., ge=1, le=12)
    school_board: str = "CBSE"
    state_name: Optional[str] = None
    subject_hint: str = "Mathematics"
    typed_question: Optional[str] = None
    image_base64: Optional[str] = None
    image_caption_hint: Optional[str] = None
    preferred_explanation_language: str = "English"
    secondary_explanation_language: Optional[str] = None
    simulate_agent_failure: bool = False
    simulate_model_failure: bool = False


class UnderstandingAgentOutput(BaseModel):
    agent_id: Literal["understanding"] = "understanding"
    agent_name: str = "Understanding Agent"
    status: Literal["completed", "failed"] = "completed"
    executed_at: str
    duration_ms: float
    model_used: str
    extracted_question: str
    is_question_clear: bool
    clarification_prompt: Optional[str] = None
    detected_subject: str
    detected_grade: int
    detected_topic: str
    curriculum_context: List[str] = Field(default_factory=list)
    processed_from_image: bool = False
    student_intent: Literal[
        "homework_guidance",
        "concept_explanation",
        "prerequisite_help",
        "full_solution_requested",
        "practice_request",
    ] = "homework_guidance"
    explanation_language: str
    secondary_explanation_language: Optional[str] = None


class UnderstandingAgent:
    """Specialist Agent 1: Extracts and structures the student's homework/question from text or image."""

    def execute(self, inp: UnderstandingAgentInput) -> UnderstandingAgentOutput:
        start_t = time.perf_counter()

        if inp.simulate_agent_failure:
            raise AgentExecutionError("UnderstandingAgent failed: Simulated agent fault.")

        # 1. Invoke AI model client (checks for live Gemini Vision/Text or raises ModelAPIError on simulated failure)
        model_res = invoke_gemini_or_structured_engine(
            agent_name="UnderstandingAgent",
            system_instruction="Extract homework question, subject, grade, and curriculum topic.",
            user_prompt=inp.typed_question or inp.image_caption_hint or "Extract image question",
            image_base64=inp.image_base64,
            simulate_failure=inp.simulate_model_failure,
        )

        # 2. Process image if uploaded
        processed_from_image = False
        raw_question = (inp.typed_question or "").strip()

        if inp.image_base64:
            vision_data = extract_homework_from_image_payload(
                image_base64=inp.image_base64,
                image_caption_hint=inp.image_caption_hint or raw_question or None,
                subject_hint=inp.subject_hint,
                grade=inp.grade,
            )
            processed_from_image = True
            if not raw_question:
                raw_question = str(vision_data["extracted_question"])

        # 3. Check question clarity (Conditional Routing Rule: if unclear, request clarification)
        is_clear = len(raw_question) >= 4 and raw_question.lower() not in {"?", "help", "hi", "idk", "..."}
        clarification_prompt: Optional[str] = None
        if not is_clear:
            clarification_prompt = (
                "Could you please share the exact homework question or upload a clear photo of the problem so we can solve it step by step?"
            )

        # 4. Detect Subject & Curriculum Topic
        q_lower = raw_question.lower()
        detected_subject = inp.subject_hint
        if any(w in q_lower for w in ["photosynthesis", "chlorophyll", "acid", "base", "litmus", "plant", "cell", "force", "velocity", "conduction", "convection"]):
            detected_subject = "Science"
        elif any(w in q_lower for w in ["fraction", "1/4", "1/6", "lcm", "hcf", "gcd", "denominator", "equation", "integer", "triangle", "algebra"]):
            detected_subject = "Mathematics"

        if any(w in q_lower for w in ["hcf", "gcd", "highest common factor"]):
            detected_topic = "Factors & Multiples (HCF & LCM)"
        elif any(w in q_lower for w in ["fraction", "1/4", "1/6", "2/3", "1/3", "denominator", "lcm"]):
            detected_topic = "Fractions & Decimals"
        elif any(w in q_lower for w in ["integer", "negative", "number line"]):
            detected_topic = "Integers & Rational Numbers"
        elif any(w in q_lower for w in ["equation", "algebra", "variable", "3x", "2x"]):
            detected_topic = "Algebraic Expressions & Linear Equations"
        elif any(w in q_lower for w in ["photosynthesis", "chlorophyll", "plant", "nutrition"]):
            detected_topic = "Nutrition in Plants & Animals"
        elif any(w in q_lower for w in ["acid", "base", "salt", "litmus"]):
            detected_topic = "Acids, Bases & Salts"
        else:
            detected_topic = f"{detected_subject} Core Problem Solving"

        # 5. Retrieve curriculum context from India Curriculum Engine
        board_subjects = get_subjects_for_grade_and_board(
            grade=inp.grade, board=inp.school_board, state=inp.state_name
        )
        curriculum_context: List[str] = []
        for s in board_subjects:
            if detected_subject.lower() in str(s["name"]).lower() or str(s["name"]).lower() in detected_subject.lower():
                curriculum_context = [f"{s['name']} ({inp.school_board} Grade {inp.grade}): {', '.join(s['topics'])}"]
                break
        if not curriculum_context and board_subjects:
            curriculum_context = [
                f"{board_subjects[0]['name']} ({inp.school_board} Grade {inp.grade}): {', '.join(board_subjects[0]['topics'])}"
            ]

        # 6. Identify student intent
        intent: Literal[
            "homework_guidance",
            "concept_explanation",
            "prerequisite_help",
            "full_solution_requested",
            "practice_request",
        ] = "homework_guidance"
        if "full solution" in q_lower or "complete answer" in q_lower or "worked solution" in q_lower:
            intent = "full_solution_requested"
        elif "practice" in q_lower or "already understand" in q_lower or "i know this concept" in q_lower:
            intent = "practice_request"
        elif "don't know lcm" in q_lower or "what is lcm" in q_lower or "prerequisite" in q_lower:
            intent = "prerequisite_help"

        elapsed_ms = round((time.perf_counter() - start_t) * 1000, 2)

        return UnderstandingAgentOutput(
            executed_at=utc_now(),
            duration_ms=elapsed_ms,
            model_used=str(model_res["model_used"]),
            extracted_question=raw_question or "(Unclear / Empty Question)",
            is_question_clear=is_clear,
            clarification_prompt=clarification_prompt,
            detected_subject=detected_subject,
            detected_grade=inp.grade,
            detected_topic=detected_topic,
            curriculum_context=curriculum_context,
            processed_from_image=processed_from_image,
            student_intent=intent,
            explanation_language=inp.preferred_explanation_language,
            secondary_explanation_language=inp.secondary_explanation_language,
        )

