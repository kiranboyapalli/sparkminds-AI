"""
SparkMinds AI — Central Stateful Workflow Orchestrator (Section 3)
Implements an explicit, testable StateGraph-style workflow engine:

STUDENT REQUEST
       ↓
UNDERSTANDING AGENT
       ↓ (If unclear -> Request Clarification & Stop)
LEARNING DIAGNOSIS AGENT
       ↓ (Routes to Prerequisite Teaching / Guided Step Tutoring / Direct Practice)
TEACHING AGENT
       ↓ (Pauses & waits for STUDENT ATTEMPT)
STUDENT ATTEMPT
       ↓
ASSESSMENT AGENT
       ↓ (Routes to Progressive Hint / Alternative Strategy / Next Step / Mastery Verification)
FEEDBACK AND REMEDIATION (Teaching Agent invoked only when needed)
       ↓
LEARNING MEMORY UPDATE (Connected to Academic Journey without overwriting past years)
"""
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from app.core.repository import repo
from app.core.config import settings
from app.agents.llm_utils import call_gemini_text
from app.agents.math_formatter import format_educational_text
from app.models.schemas import AgentExecutionLog, LearningMemoryRecord
from app.agents.model_client import AgentExecutionError, ModelAPIError
from app.agents.understanding_agent import (
    UnderstandingAgent,
    UnderstandingAgentInput,
    UnderstandingAgentOutput,
)
from app.agents.diagnosis_agent import (
    LearningDiagnosisAgent,
    LearningDiagnosisInput,
    LearningDiagnosisOutput,
)
from app.agents.teaching_agent import (
    TeachingAgent,
    TeachingAgentInput,
    TeachingAgentOutput,
)
from app.agents.assessment_agent import (
    AssessmentAgent,
    AssessmentAgentInput,
    AssessmentAgentOutput,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TutorSessionState(BaseModel):
    """
    Preserves full conversation and execution state across multi-turn homework tutoring.
    """
    session_id: str
    student_id: str
    academic_year_label: str = "2026-2027"
    grade: int
    school_board: str
    state_name: Optional[str] = None
    preferred_explanation_language: str
    secondary_explanation_language: Optional[str] = None
    current_node: Literal[
        "AWAITING_CLARIFICATION",
        "AWAITING_STUDENT_STEP_ATTEMPT",
        "REMEDIATION_IN_PROGRESS",
        "MASTERY_VERIFIED_COMPLETED",
        "ERROR_HALTED",
    ] = "AWAITING_STUDENT_STEP_ATTEMPT"
    conditional_route_taken: str = "INITIALIZED"
    student_response_required: bool = True
    extracted_question: str = ""
    detected_subject: str = "Mathematics"
    detected_topic: str = "Fractions & Decimals"
    current_step_index: int = 1
    total_steps: int = 3
    mistake_count: int = 0
    hint_level: int = 0
    student_attempts_history: List[str] = Field(default_factory=list)
    detected_misconceptions_history: List[str] = Field(default_factory=list)
    hints_provided_history: List[str] = Field(default_factory=list)
    understanding_output: Optional[UnderstandingAgentOutput] = None
    diagnosis_output: Optional[LearningDiagnosisOutput] = None
    teaching_output: Optional[TeachingAgentOutput] = None
    assessment_output: Optional[AssessmentAgentOutput] = None
    execution_logs: List[AgentExecutionLog] = Field(default_factory=list)
    followup_qa_history: List[Dict[str, str]] = Field(default_factory=list)
    practice_streak: int = 0
    learning_memory_id: Optional[str] = None
    error_state: Optional[str] = None


class StartTutorSessionRequest(BaseModel):
    student_id: str = "stu_aarav_g7"
    typed_question: Optional[str] = None
    image_base64: Optional[str] = None
    image_caption_hint: Optional[str] = None
    subject_hint: str = "Mathematics"
    language_override: Optional[str] = None
    secondary_language_override: Optional[str] = None
    request_full_solution: bool = False
    simulate_agent_failure: Optional[Literal["understanding", "diagnosis", "teaching"]] = None
    simulate_model_failure: bool = False


class SubmitStudentAttemptRequest(BaseModel):
    session_id: str
    student_id: str = "stu_aarav_g7"
    action_type: Literal[
        "SUBMIT_STEP_ATTEMPT",
        "REQUEST_PROGRESSIVE_HINT",
        "REQUEST_ALTERNATIVE_EXPLANATION",
        "REQUEST_FULL_SOLUTION",
        "REQUEST_SIMILAR_PRACTICE",
        "ASK_FOLLOWUP_QUESTION",
        "SUBMIT_PRACTICE_ATTEMPT",
    ] = "SUBMIT_STEP_ATTEMPT"
    student_attempt: str = ""
    language_override: Optional[str] = None
    simulate_agent_failure: Optional[Literal["assessment", "teaching"]] = None
    simulate_model_failure: bool = False


class TutorStateGraphOrchestrator:
    """
    Stateful Graph Workflow Engine coordinating the 4 Specialist Agents with conditional routing.
    Never calls agents unnecessarily; never masks agent or model failures.
    """

    def __init__(self) -> None:
        self.understanding_agent = UnderstandingAgent()
        self.diagnosis_agent = LearningDiagnosisAgent()
        self.teaching_agent = TeachingAgent()
        self.assessment_agent = AssessmentAgent()

    def _resolve_student_context(
        self,
        student_id: str,
        language_override: Optional[str],
        secondary_language_override: Optional[str],
    ) -> Dict[str, object]:
        student = repo.students.get(student_id)
        if not student:
            student = repo.register_or_get_student(student_id, "Student Learner")
        lang_prefs = student["language_preferences"]
        pref_lang = (
            language_override
            if language_override
            else str(lang_prefs["preferred_explanation_language"])
        )
        sec_lang = (
            secondary_language_override
            if secondary_language_override is not None
            else lang_prefs.get("secondary_explanation_language")
        )
        return {
            "grade": int(student["current_grade"]),
            "board": str(student["school_board"]),
            "state": student.get("state_name"),
            "preferred_language": pref_lang,
            "secondary_language": sec_lang,
        }

    def start_homework_session(self, req: StartTutorSessionRequest) -> TutorSessionState:
        """
        Entry Graph Flow:
        STUDENT REQUEST -> UNDERSTANDING AGENT -> (Conditional Check) -> LEARNING DIAGNOSIS AGENT -> TEACHING AGENT
        Stops and waits for STUDENT ATTEMPT (does NOT call Assessment Agent prematurely!).
        """
        ctx = self._resolve_student_context(
            req.student_id, req.language_override, req.secondary_language_override
        )
        session_id = f"sess_{uuid.uuid4().hex[:10]}"
        memory_id = f"mem_{session_id}"

        state = TutorSessionState(
            session_id=session_id,
            student_id=req.student_id,
            grade=int(ctx["grade"]),
            school_board=str(ctx["board"]),
            state_name=str(ctx["state"]) if ctx["state"] else None,
            preferred_explanation_language=str(ctx["preferred_language"]),
            secondary_explanation_language=str(ctx["secondary_language"]) if ctx["secondary_language"] else None,
            learning_memory_id=memory_id,
        )

        # --------------------------------------------------------------------
        # NODE 1: UNDERSTANDING AGENT
        # --------------------------------------------------------------------
        t0 = utc_now()
        try:
            u_out = self.understanding_agent.execute(
                UnderstandingAgentInput(
                    student_id=req.student_id,
                    grade=state.grade,
                    school_board=state.school_board,
                    state_name=state.state_name,
                    subject_hint=req.subject_hint,
                    typed_question=req.typed_question,
                    image_base64=req.image_base64,
                    image_caption_hint=req.image_caption_hint,
                    preferred_explanation_language=state.preferred_explanation_language,
                    secondary_explanation_language=state.secondary_explanation_language,
                    simulate_agent_failure=(req.simulate_agent_failure == "understanding"),
                    simulate_model_failure=req.simulate_model_failure,
                )
            )
            state.understanding_output = u_out
            state.extracted_question = u_out.extracted_question
            state.detected_subject = u_out.detected_subject
            state.detected_topic = u_out.detected_topic
            state.execution_logs.append(
                AgentExecutionLog(
                    log_id=f"log_{uuid.uuid4().hex[:8]}",
                    agent_id="understanding",
                    agent_name="Understanding Agent",
                    task_description=(
                        "Processed uploaded homework image & extracted question"
                        if u_out.processed_from_image
                        else "Parsed typed homework question & curriculum context"
                    ),
                    status="completed",
                    started_at=t0,
                    completed_at=u_out.executed_at,
                    duration_ms=u_out.duration_ms,
                    model_invoked=u_out.model_used,
                    output_summary=f"Subject: {u_out.detected_subject} | Topic: {u_out.detected_topic} | Clear: {u_out.is_question_clear}",
                    student_action_required=not u_out.is_question_clear,
                )
            )
        except (AgentExecutionError, ModelAPIError) as exc:
            state.current_node = "ERROR_HALTED"
            state.error_state = str(exc)
            state.student_response_required = False
            state.execution_logs.append(
                AgentExecutionLog(
                    log_id=f"log_{uuid.uuid4().hex[:8]}",
                    agent_id="understanding",
                    agent_name="Understanding Agent",
                    task_description="Attempted to parse student question/image",
                    status="failed",
                    started_at=t0,
                    completed_at=utc_now(),
                    duration_ms=1.0,
                    model_invoked="failed",
                    output_summary="Agent execution failed",
                    error_message=str(exc),
                    student_action_required=False,
                )
            )
            repo.tutor_sessions[session_id] = state.model_dump()
            return state

        # CONDITIONAL ROUTE 1: Question is unclear -> Request clarification and do NOT call downstream agents
        if not u_out.is_question_clear:
            state.current_node = "AWAITING_CLARIFICATION"
            state.conditional_route_taken = "UNCLEAR_QUESTION_REQUEST_CLARIFICATION"
            state.student_response_required = True
            repo.tutor_sessions[session_id] = state.model_dump()
            return state

        # --------------------------------------------------------------------
        # NODE 2: LEARNING DIAGNOSIS AGENT
        # --------------------------------------------------------------------
        t1 = utc_now()
        try:
            d_out = self.diagnosis_agent.execute(
                LearningDiagnosisInput(
                    student_id=req.student_id,
                    grade=state.grade,
                    detected_subject=state.detected_subject,
                    detected_topic=state.detected_topic,
                    extracted_question=state.extracted_question,
                    student_intent=u_out.student_intent,
                    preferred_explanation_language=state.preferred_explanation_language,
                    simulate_agent_failure=(req.simulate_agent_failure == "diagnosis"),
                    simulate_model_failure=False,
                )
            )
            state.diagnosis_output = d_out
            state.execution_logs.append(
                AgentExecutionLog(
                    log_id=f"log_{uuid.uuid4().hex[:8]}",
                    agent_id="diagnosis",
                    agent_name="Learning Diagnosis Agent",
                    task_description="Analysed prerequisites, historical misconceptions & verified vs self-report records",
                    status="completed",
                    started_at=t1,
                    completed_at=d_out.executed_at,
                    duration_ms=d_out.duration_ms,
                    model_invoked=d_out.model_used,
                    output_summary=(
                        f"Route: {d_out.recommended_pedagogical_route} | "
                        f"Missing Prereq: {d_out.missing_prerequisite_topic or 'None'} | "
                        f"Verified Records: {len(d_out.verified_learning_evidence)}"
                    ),
                    student_action_required=False,
                )
            )
        except (AgentExecutionError, ModelAPIError) as exc:
            state.current_node = "ERROR_HALTED"
            state.error_state = str(exc)
            state.student_response_required = False
            state.execution_logs.append(
                AgentExecutionLog(
                    log_id=f"log_{uuid.uuid4().hex[:8]}",
                    agent_id="diagnosis",
                    agent_name="Learning Diagnosis Agent",
                    task_description="Attempted learning gap diagnosis",
                    status="failed",
                    started_at=t1,
                    completed_at=utc_now(),
                    duration_ms=1.0,
                    model_invoked="failed",
                    output_summary="Diagnosis failed",
                    error_message=str(exc),
                )
            )
            repo.tutor_sessions[session_id] = state.model_dump()
            return state

        # CONDITIONAL ROUTE 2: Select pedagogical mode for Teaching Agent based on Diagnosis
        if req.request_full_solution or u_out.student_intent == "full_solution_requested":
            ped_mode: Literal[
                "TEACH_PREREQUISITE_FIRST",
                "STEP_BY_STEP_GUIDED_TUTORING",
                "PROGRESSIVE_HINT",
                "ALTERNATIVE_EXPLANATION",
                "FULL_WORKED_SOLUTION",
                "SIMILAR_PRACTICE_QUESTION",
            ] = "FULL_WORKED_SOLUTION"
            state.conditional_route_taken = "FULL_WORKED_SOLUTION_REQUESTED"
        elif d_out.recommended_pedagogical_route == "TEACH_PREREQUISITE_FIRST":
            ped_mode = "TEACH_PREREQUISITE_FIRST"
            state.conditional_route_taken = "MISSING_PREREQUISITE_TEACH_PREREQUISITE_FIRST"
        elif d_out.recommended_pedagogical_route == "MOVE_DIRECTLY_TO_PRACTICE":
            ped_mode = "SIMILAR_PRACTICE_QUESTION"
            state.conditional_route_taken = "ALREADY_UNDERSTANDS_MOVE_TO_PRACTICE"
        else:
            ped_mode = "STEP_BY_STEP_GUIDED_TUTORING"
            state.conditional_route_taken = "STANDARD_GUIDED_STEP_TUTORING"

        # --------------------------------------------------------------------
        # NODE 3: TEACHING AGENT
        # --------------------------------------------------------------------
        t2 = utc_now()
        try:
            teach_out = self.teaching_agent.execute(
                TeachingAgentInput(
                    student_id=req.student_id,
                    grade=state.grade,
                    school_board=state.school_board,
                    detected_subject=state.detected_subject,
                    detected_topic=state.detected_topic,
                    extracted_question=state.extracted_question,
                    pedagogical_mode=ped_mode,
                    current_step_index=1,
                    hint_level=1,
                    mistake_count=0,
                    missing_prerequisite_topic=d_out.missing_prerequisite_topic,
                    preferred_explanation_language=state.preferred_explanation_language,
                    secondary_explanation_language=state.secondary_explanation_language,
                    request_full_solution=req.request_full_solution,
                    simulate_agent_failure=(req.simulate_agent_failure == "teaching"),
                    simulate_model_failure=False,
                )
            )
            state.teaching_output = teach_out
            state.total_steps = len(teach_out.steps_breakdown)
            state.current_node = "AWAITING_STUDENT_STEP_ATTEMPT"
            state.student_response_required = True
            state.execution_logs.append(
                AgentExecutionLog(
                    log_id=f"log_{uuid.uuid4().hex[:8]}",
                    agent_id="teaching",
                    agent_name="Teaching Agent",
                    task_description=f"Generated {state.preferred_explanation_language} interactive tutoring ({ped_mode})",
                    status="completed",
                    started_at=t2,
                    completed_at=teach_out.executed_at,
                    duration_ms=teach_out.duration_ms,
                    model_invoked=teach_out.model_used,
                    output_summary=(
                        f"Language: {teach_out.explanation_language} | "
                        f"Step 1 of {state.total_steps} | "
                        f"Answer Withheld: {teach_out.answer_withheld_for_guided_learning}"
                    ),
                    student_action_required=True,
                )
            )
        except (AgentExecutionError, ModelAPIError) as exc:
            state.current_node = "ERROR_HALTED"
            state.error_state = str(exc)
            state.student_response_required = False
            state.execution_logs.append(
                AgentExecutionLog(
                    log_id=f"log_{uuid.uuid4().hex[:8]}",
                    agent_id="teaching",
                    agent_name="Teaching Agent",
                    task_description="Attempted interactive lesson generation",
                    status="failed",
                    started_at=t2,
                    completed_at=utc_now(),
                    duration_ms=1.0,
                    model_invoked="failed",
                    output_summary="Teaching agent failed",
                    error_message=str(exc),
                )
            )
            repo.tutor_sessions[session_id] = state.model_dump()
            return state

        # Save initial LearningMemoryRecord (in_progress)
        repo.save_learning_memory(
            LearningMemoryRecord(
                memory_id=memory_id,
                session_id=session_id,
                student_id=req.student_id,
                academic_year=state.academic_year_label,
                grade=state.grade,
                subject=state.detected_subject,
                topic=state.detected_topic,
                question=state.extracted_question,
                student_attempts=[],
                detected_misconceptions=[],
                hints_provided=[],
                assessment_result="in_progress",
                recommended_next_action=teach_out.prompt_for_student_attempt,
                explanation_language=state.preferred_explanation_language,
                secondary_explanation_language=state.secondary_explanation_language,
                recorded_at=utc_now(),
            )
        )

        repo.tutor_sessions[session_id] = state.model_dump()
        return state

    def process_student_turn(self, req: SubmitStudentAttemptRequest) -> TutorSessionState:
        """
        Continuation Graph Flow:
        STUDENT ATTEMPT / ACTION -> ASSESSMENT AGENT -> CONDITIONAL REMEDIATION / TEACHING AGENT -> LEARNING MEMORY UPDATE
        """
        raw_session = repo.tutor_sessions.get(req.session_id)
        if not raw_session:
            raise KeyError(f"Tutor session {req.session_id} not found")

        state = TutorSessionState(**raw_session)
        if req.language_override:
            state.preferred_explanation_language = req.language_override

        # Direct Pedagogical Action Requests (Hint, Alternative Explanation, Full Solution, Similar Practice)
        if req.action_type in (
            "REQUEST_PROGRESSIVE_HINT",
            "REQUEST_ALTERNATIVE_EXPLANATION",
            "REQUEST_FULL_SOLUTION",
            "REQUEST_SIMILAR_PRACTICE",
        ):
            if req.action_type == "REQUEST_PROGRESSIVE_HINT":
                state.hint_level = min(3, state.hint_level + 1)
                mode: Literal[
                    "TEACH_PREREQUISITE_FIRST",
                    "STEP_BY_STEP_GUIDED_TUTORING",
                    "PROGRESSIVE_HINT",
                    "ALTERNATIVE_EXPLANATION",
                    "FULL_WORKED_SOLUTION",
                    "SIMILAR_PRACTICE_QUESTION",
                ] = "PROGRESSIVE_HINT"
                state.conditional_route_taken = f"PROGRESSIVE_HINT_LEVEL_{state.hint_level}"
            elif req.action_type == "REQUEST_ALTERNATIVE_EXPLANATION":
                mode = "ALTERNATIVE_EXPLANATION"
                state.conditional_route_taken = "ALTERNATIVE_VISUAL_EXPLANATION"
            elif req.action_type == "REQUEST_FULL_SOLUTION":
                mode = "FULL_WORKED_SOLUTION"
                state.conditional_route_taken = "FULL_WORKED_SOLUTION_REVEALED"
            else:
                mode = "SIMILAR_PRACTICE_QUESTION"
                state.conditional_route_taken = "GENERATE_SIMILAR_PRACTICE_QUESTION"

            t_start = utc_now()
            try:
                teach_out = self.teaching_agent.execute(
                    TeachingAgentInput(
                        student_id=state.student_id,
                        grade=state.grade,
                        school_board=state.school_board,
                        detected_subject=state.detected_subject,
                        detected_topic=state.detected_topic,
                        extracted_question=state.extracted_question,
                        pedagogical_mode=mode,
                        current_step_index=state.current_step_index,
                        hint_level=max(1, state.hint_level),
                        mistake_count=state.mistake_count,
                        preferred_explanation_language=state.preferred_explanation_language,
                        secondary_explanation_language=state.secondary_explanation_language,
                        request_full_solution=(mode == "FULL_WORKED_SOLUTION"),
                        simulate_agent_failure=(req.simulate_agent_failure == "teaching"),
                        simulate_model_failure=req.simulate_model_failure,
                    )
                )
            except (AgentExecutionError, ModelAPIError) as exc:
                state.current_node = "ERROR_HALTED"
                state.error_state = str(exc)
                state.student_response_required = False
                state.execution_logs.append(
                    AgentExecutionLog(
                        log_id=f"log_{uuid.uuid4().hex[:8]}",
                        agent_id="teaching",
                        agent_name="Teaching Agent",
                        task_description=f"Attempted {mode} in {state.preferred_explanation_language}",
                        status="failed",
                        started_at=t_start,
                        completed_at=utc_now(),
                        duration_ms=1.0,
                        model_invoked="failed",
                        output_summary="Teaching agent failed during turn action",
                        error_message=str(exc),
                    )
                )
                repo.tutor_sessions[state.session_id] = state.model_dump()
                return state
            state.teaching_output = teach_out
            if teach_out.active_hint_shown:
                state.hints_provided_history.append(teach_out.active_hint_shown)

            state.execution_logs.append(
                AgentExecutionLog(
                    log_id=f"log_{uuid.uuid4().hex[:8]}",
                    agent_id="teaching",
                    agent_name="Teaching Agent",
                    task_description=f"Executed {mode} in {state.preferred_explanation_language}",
                    status="completed",
                    started_at=t_start,
                    completed_at=teach_out.executed_at,
                    duration_ms=teach_out.duration_ms,
                    model_invoked=teach_out.model_used,
                    output_summary=f"Mode: {mode} | Hint Level: {state.hint_level}",
                    student_action_required=True,
                )
            )
            repo.tutor_sessions[state.session_id] = state.model_dump()
            return state

        # --------------------------------------------------------------------
        # FOLLOW-UP QUESTIONS DURING TUTORING SESSION
        # --------------------------------------------------------------------
        if req.action_type == "ASK_FOLLOWUP_QUESTION":
            t_start = utc_now()
            q_followup = req.student_attempt.strip()
            followup_ans = ""
            used_model = "sparkminds-socratic-fallback"
            prompt = (
                f"Student is in Grade {state.grade} {state.school_board}. Preferred Language: {state.preferred_explanation_language}.\n"
                f"Current lesson topic: {state.detected_subject} • {state.detected_topic}.\n"
                f"Original question: {state.extracted_question}.\n"
                f"Student is at Step {state.current_step_index} and asked follow-up: \"{q_followup}\".\n"
                f"Provide a clear, pedagogical, concise Socratic answer in {state.preferred_explanation_language} "
                f"clarifying their doubt and encouraging them to proceed with the next step. Do not reveal the full answer. "
                f"Format math cleanly with Unicode symbols (×, ÷, √, x², 3/4, °) and never use raw $...$ LaTeX delimiters."
            )
            llm_res = call_gemini_text(prompt=prompt, temperature=0.35, max_output_tokens=1024)
            if llm_res:
                followup_ans = format_educational_text(llm_res[0])
                used_model = llm_res[1]

            if not followup_ans:
                followup_ans = (
                    f"Great question! Regarding \"{q_followup}\": In Grade {state.grade} {state.detected_subject}, "
                    f"remember that in Step {state.current_step_index}, we isolate the fundamental principles so that "
                    f"every calculation is exact and verifiable. Let's apply this to continue the step!"
                )

            qa_record = {
                "question": q_followup,
                "answer": followup_ans,
                "step": str(state.current_step_index),
                "timestamp": utc_now(),
            }
            state.followup_qa_history.append(qa_record)
            state.conditional_route_taken = "FOLLOWUP_QUESTION_ANSWERED"
            state.execution_logs.append(
                AgentExecutionLog(
                    log_id=f"log_{uuid.uuid4().hex[:8]}",
                    agent_id="teaching",
                    agent_name="Teaching Agent",
                    task_description=f"Answered student follow-up: '{q_followup[:35]}...'",
                    status="completed",
                    started_at=t_start,
                    completed_at=utc_now(),
                    duration_ms=35.0,
                    model_invoked=used_model,
                    output_summary=f"Socratic follow-up provided in {state.preferred_explanation_language}",
                    student_action_required=True,
                )
            )
            repo.tutor_sessions[state.session_id] = state.model_dump()
            return state

        # --------------------------------------------------------------------
        # INTERACTIVE PRACTICE ATTEMPTS EVALUATION
        # --------------------------------------------------------------------
        if req.action_type == "SUBMIT_PRACTICE_ATTEMPT":
            t_assess = utc_now()
            sim_q = (
                state.teaching_output.similar_practice_question.get("question", state.extracted_question)
                if state.teaching_output
                else state.extracted_question
            )
            a_out = self.assessment_agent.execute(
                AssessmentAgentInput(
                    student_id=state.student_id,
                    grade=state.grade,
                    detected_subject=state.detected_subject,
                    detected_topic=state.detected_topic,
                    question_text=sim_q,
                    student_attempt=req.student_attempt,
                    current_step_index=1,
                    total_steps=1,
                    previous_mistake_count=0,
                    preferred_explanation_language=state.preferred_explanation_language,
                    secondary_explanation_language=state.secondary_explanation_language,
                )
            )
            state.assessment_output = a_out
            if a_out.is_attempt_correct:
                state.practice_streak += 1
            state.conditional_route_taken = "PRACTICE_ATTEMPT_EVALUATED"
            state.execution_logs.append(
                AgentExecutionLog(
                    log_id=f"log_{uuid.uuid4().hex[:8]}",
                    agent_id="assessment",
                    agent_name="Assessment Agent",
                    task_description=f"Evaluated practice attempt '{req.student_attempt[:30]}...'",
                    status="completed",
                    started_at=t_assess,
                    completed_at=a_out.executed_at,
                    duration_ms=a_out.duration_ms,
                    model_invoked=a_out.model_used,
                    output_summary=f"Practice Correct: {a_out.is_attempt_correct} | Streak: {state.practice_streak}",
                    student_action_required=True,
                )
            )
            repo.tutor_sessions[state.session_id] = state.model_dump()
            return state

        # --------------------------------------------------------------------
        # NODE 4: ASSESSMENT AGENT (Evaluates Student Attempt)
        # --------------------------------------------------------------------
        state.student_attempts_history.append(req.student_attempt)
        t_assess = utc_now()
        try:
            a_out = self.assessment_agent.execute(
                AssessmentAgentInput(
                    student_id=state.student_id,
                    grade=state.grade,
                    detected_subject=state.detected_subject,
                    detected_topic=state.detected_topic,
                    question_text=state.extracted_question,
                    student_attempt=req.student_attempt,
                    current_step_index=state.current_step_index,
                    total_steps=state.total_steps,
                    previous_mistake_count=state.mistake_count,
                    preferred_explanation_language=state.preferred_explanation_language,
                    secondary_explanation_language=state.secondary_explanation_language,
                    simulate_agent_failure=(req.simulate_agent_failure == "assessment"),
                    simulate_model_failure=req.simulate_model_failure,
                )
            )
            state.assessment_output = a_out
            state.execution_logs.append(
                AgentExecutionLog(
                    log_id=f"log_{uuid.uuid4().hex[:8]}",
                    agent_id="assessment",
                    agent_name="Assessment Agent",
                    task_description=f"Evaluated student attempt '{req.student_attempt}' at Step {state.current_step_index}",
                    status="completed",
                    started_at=t_assess,
                    completed_at=a_out.executed_at,
                    duration_ms=a_out.duration_ms,
                    model_invoked=a_out.model_used,
                    output_summary=(
                        f"Correct: {a_out.is_attempt_correct} | "
                        f"Route: {a_out.next_routing_action} | "
                        f"Misconception: {a_out.detected_misconception or 'None'}"
                    ),
                    student_action_required=not a_out.is_problem_completed,
                )
            )
        except (AgentExecutionError, ModelAPIError) as exc:
            state.current_node = "ERROR_HALTED"
            state.error_state = str(exc)
            state.student_response_required = False
            state.execution_logs.append(
                AgentExecutionLog(
                    log_id=f"log_{uuid.uuid4().hex[:8]}",
                    agent_id="assessment",
                    agent_name="Assessment Agent",
                    task_description="Attempted student response evaluation",
                    status="failed",
                    started_at=t_assess,
                    completed_at=utc_now(),
                    duration_ms=1.0,
                    model_invoked="failed",
                    output_summary="Assessment agent failed",
                    error_message=str(exc),
                )
            )
            repo.tutor_sessions[state.session_id] = state.model_dump()
            return state

        # --------------------------------------------------------------------
        # CONDITIONAL ROUTING BASED ON ASSESSMENT AGENT VERDICT
        # --------------------------------------------------------------------
        state.conditional_route_taken = a_out.next_routing_action

        if a_out.detected_misconception:
            state.detected_misconceptions_history.append(a_out.detected_misconception)

        if a_out.next_routing_action == "SAVE_MASTERY_EVIDENCE_AND_COMPLETE":
            state.current_node = "MASTERY_VERIFIED_COMPLETED"
            state.student_response_required = False
            mem_status: Literal["correct", "incorrect", "in_progress", "mastery_verified"] = "mastery_verified"
        elif a_out.next_routing_action == "ADVANCE_TO_NEXT_STEP":
            state.current_step_index = min(state.total_steps, state.current_step_index + 1)
            state.current_node = "AWAITING_STUDENT_STEP_ATTEMPT"
            state.student_response_required = True
            mem_status = "correct"
            # Invoke Teaching Agent to present the next step prompt
            teach_next = self.teaching_agent.execute(
                TeachingAgentInput(
                    student_id=state.student_id,
                    grade=state.grade,
                    school_board=state.school_board,
                    detected_subject=state.detected_subject,
                    detected_topic=state.detected_topic,
                    extracted_question=state.extracted_question,
                    pedagogical_mode="STEP_BY_STEP_GUIDED_TUTORING",
                    current_step_index=state.current_step_index,
                    hint_level=max(1, state.hint_level),
                    mistake_count=state.mistake_count,
                    preferred_explanation_language=state.preferred_explanation_language,
                    secondary_explanation_language=state.secondary_explanation_language,
                )
            )
            state.teaching_output = teach_next
        else:
            # Student made a mistake -> Increment mistake & hint counters and invoke Teaching Agent for targeted remediation
            state.mistake_count += 1
            state.hint_level = min(3, state.hint_level + 1)
            state.current_node = "REMEDIATION_IN_PROGRESS"
            state.student_response_required = True
            mem_status = "incorrect"

            if a_out.next_routing_action == "TEACH_MISSING_PREREQUISITE":
                rem_mode: Literal[
                    "TEACH_PREREQUISITE_FIRST",
                    "STEP_BY_STEP_GUIDED_TUTORING",
                    "PROGRESSIVE_HINT",
                    "ALTERNATIVE_EXPLANATION",
                    "FULL_WORKED_SOLUTION",
                    "SIMILAR_PRACTICE_QUESTION",
                ] = "TEACH_PREREQUISITE_FIRST"
            elif a_out.next_routing_action == "SWITCH_TO_ALTERNATIVE_TEACHING_STRATEGY":
                rem_mode = "ALTERNATIVE_EXPLANATION"
            else:
                rem_mode = "PROGRESSIVE_HINT"

            t_rem = utc_now()
            teach_rem = self.teaching_agent.execute(
                TeachingAgentInput(
                    student_id=state.student_id,
                    grade=state.grade,
                    school_board=state.school_board,
                    detected_subject=state.detected_subject,
                    detected_topic=state.detected_topic,
                    extracted_question=state.extracted_question,
                    pedagogical_mode=rem_mode,
                    current_step_index=state.current_step_index,
                    hint_level=state.hint_level,
                    mistake_count=state.mistake_count,
                    last_detected_misconception=a_out.detected_misconception,
                    missing_prerequisite_topic=a_out.missing_prerequisite_identified,
                    preferred_explanation_language=state.preferred_explanation_language,
                    secondary_explanation_language=state.secondary_explanation_language,
                )
            )
            state.teaching_output = teach_rem
            if teach_rem.active_hint_shown:
                state.hints_provided_history.append(teach_rem.active_hint_shown)

            state.execution_logs.append(
                AgentExecutionLog(
                    log_id=f"log_{uuid.uuid4().hex[:8]}",
                    agent_id="teaching",
                    agent_name="Teaching Agent",
                    task_description=f"Provided remediation ({rem_mode}, Hint Level {state.hint_level})",
                    status="completed",
                    started_at=t_rem,
                    completed_at=teach_rem.executed_at,
                    duration_ms=teach_rem.duration_ms,
                    model_invoked=teach_rem.model_used,
                    output_summary=(
                        f"Remediation Mode: {rem_mode} | "
                        f"Mistake Count: {state.mistake_count} | "
                        f"Alt Strategy: {bool(teach_rem.alternative_explanation)}"
                    ),
                    student_action_required=True,
                )
            )

        # --------------------------------------------------------------------
        # NODE 5: LEARNING MEMORY UPDATE (Connected to Academic Journey)
        # --------------------------------------------------------------------
        mem_record = LearningMemoryRecord(
            memory_id=state.learning_memory_id or f"mem_{state.session_id}",
            session_id=state.session_id,
            student_id=state.student_id,
            academic_year=state.academic_year_label,
            grade=state.grade,
            subject=state.detected_subject,
            topic=state.detected_topic,
            question=state.extracted_question,
            student_attempts=state.student_attempts_history,
            detected_misconceptions=state.detected_misconceptions_history,
            hints_provided=state.hints_provided_history,
            assessment_result=mem_status,
            concept_mastery_evidence=(
                f"Verified {state.detected_topic} mastery ({a_out.mastery_evidence_score}%) via interactive homework tutoring."
                if mem_status == "mastery_verified"
                else None
            ),
            recommended_next_action=(
                a_out.follow_up_verification_question
                or (state.teaching_output.prompt_for_student_attempt if state.teaching_output else "Continue practice")
            ),
            explanation_language=state.preferred_explanation_language,
            secondary_explanation_language=state.secondary_explanation_language,
            recorded_at=utc_now(),
        )
        repo.save_learning_memory(
            mem_record,
            update_mastery_score=a_out.mastery_evidence_score,
        )

        repo.tutor_sessions[state.session_id] = state.model_dump()
        return state


state_graph_orchestrator = TutorStateGraphOrchestrator()

