"""
SparkMinds AI — Agent 2: Learning Diagnosis Agent
Responsibilities (Section 2.2):
- Identify prerequisite concepts.
- Detect misconceptions.
- Identify specific knowledge gaps.
- Analyse previous learning records.
- Generate diagnostic questions.
- Distinguish student-reported difficulties from verified learning evidence.
"""
import time
from datetime import datetime, timezone
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from app.core.repository import repo
from app.agents.model_client import (
    AgentExecutionError,
    invoke_gemini_or_structured_engine,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LearningDiagnosisInput(BaseModel):
    student_id: str
    grade: int
    detected_subject: str
    detected_topic: str
    extracted_question: str
    student_intent: str
    preferred_explanation_language: str
    simulate_agent_failure: bool = False
    simulate_model_failure: bool = False


class LearningDiagnosisOutput(BaseModel):
    agent_id: Literal["diagnosis"] = "diagnosis"
    agent_name: str = "Learning Diagnosis Agent"
    status: Literal["completed", "failed"] = "completed"
    executed_at: str
    duration_ms: float
    model_used: str
    prerequisite_concepts: List[str] = Field(default_factory=list)
    missing_prerequisite_detected: bool = False
    missing_prerequisite_topic: Optional[str] = None
    already_mastered_topic: bool = False
    detected_historical_misconceptions: List[str] = Field(default_factory=list)
    specific_knowledge_gaps: List[str] = Field(default_factory=list)
    verified_learning_evidence: List[str] = Field(default_factory=list)
    student_self_reported_difficulties: List[str] = Field(default_factory=list)
    diagnostic_question: str
    recommended_pedagogical_route: Literal[
        "TEACH_PREREQUISITE_FIRST",
        "MOVE_DIRECTLY_TO_PRACTICE",
        "STEP_BY_STEP_GUIDED_TUTORING",
    ]
    explanation_language: str


class LearningDiagnosisAgent:
    """Specialist Agent 2: Diagnoses prerequisites, historical gaps, and separates verified evidence from self-reports."""

    def execute(self, inp: LearningDiagnosisInput) -> LearningDiagnosisOutput:
        start_t = time.perf_counter()

        if inp.simulate_agent_failure:
            raise AgentExecutionError("LearningDiagnosisAgent failed: Simulated diagnosis fault.")

        model_res = invoke_gemini_or_structured_engine(
            agent_name="LearningDiagnosisAgent",
            system_instruction="Diagnose prerequisite concepts, historical misconceptions, and verified vs self-reported gaps.",
            user_prompt=f"Subject: {inp.detected_subject}, Topic: {inp.detected_topic}, Question: {inp.extracted_question}",
            simulate_failure=inp.simulate_model_failure,
        )

        # 1. Retrieve multi-year AcademicYearProfile records & LearningMemoryRecord history
        years = repo.academic_years.get(inp.student_id, [])
        memories = repo.learning_memories.get(inp.student_id, [])

        verified_evidence: List[str] = []
        self_reports: List[str] = []
        knowledge_gaps: List[str] = []
        historical_misconceptions: List[str] = []
        topic_mastered_in_verified_test = False

        for y in years:
            for gap in y.unresolved_learning_gaps:
                if gap not in knowledge_gaps:
                    knowledge_gaps.append(f"Grade {y.grade} ({y.academic_year_label}): {gap}")

            for ev in y.evidence_records:
                if ev.evidence_type in ("ACTUAL_ASSESSMENT", "HOMEWORK_PRACTICE"):
                    verified_evidence.append(
                        f"[VERIFIED {ev.evidence_type}] Grade {y.grade} {ev.topic_name}: {ev.score_percentage}% ({ev.trend_indicator}) — {ev.notes}"
                    )
                    if (
                        inp.detected_topic.lower() in ev.topic_name.lower()
                        and ev.evidence_type == "ACTUAL_ASSESSMENT"
                        and (ev.score_percentage or 0) >= 85.0
                    ):
                        topic_mastered_in_verified_test = True
                elif ev.evidence_type == "STUDENT_SELF_REPORT":
                    self_reports.append(
                        f"[SELF-REPORT] Grade {y.grade} {ev.subject_name} ({ev.topic_name}): '{ev.qualitative_rating}'"
                    )

        for mem in memories:
            for misc in mem.detected_misconceptions:
                if misc not in historical_misconceptions:
                    historical_misconceptions.append(misc)

        # 1b. Inspect Exam Marks & Chapter Progress from Exam Study Planner (Requirement 7)
        exam_marks = repo.list_exam_marks(inp.student_id)
        study_plan = repo.get_or_create_study_plan(inp.student_id)
        for mk in exam_marks:
            if mk.subject.lower() == inp.detected_subject.lower():
                chapters_note = (
                    f"Tested chapters: {', '.join(mk.chapters_tested)}"
                    if mk.chapters_tested
                    else "Subject-level exam score only (no chapter-level breakdown reported)"
                )
                entry_line = (
                    f"[{mk.verification_status} EXAM] {mk.subject} — {mk.exam_name} ({mk.exam_type}): "
                    f"{mk.marks_obtained}/{mk.maximum_marks} ({mk.percentage}%, Trend: {mk.trend}). {chapters_note}"
                )
                if mk.verification_status == "OFFICIALLY_VERIFIED":
                    verified_evidence.append(entry_line)
                else:
                    self_reports.append(entry_line)
                if mk.percentage < 65.0:
                    if mk.chapters_tested:
                        gap_msg = f"{mk.subject} Exam Recovery ({mk.exam_name}: {mk.percentage}%): Focus on tested chapters {', '.join(mk.chapters_tested)}"
                    else:
                        gap_msg = f"{mk.subject} Exam Recovery ({mk.exam_name}: {mk.percentage}%): Subject-level performance needs reinforcement (run chapter diagnostic)"
                    if gap_msg not in knowledge_gaps:
                        knowledge_gaps.append(gap_msg)

        for es in study_plan.exam_subjects:
            if es.subject_name.lower() == inp.detected_subject.lower():
                weak_chapters = [
                    ch.chapter_name
                    for ch in es.chapters
                    if ch.difficulty == "Difficult" or ch.additional_practice_needed or ch.completion_status != "Completed"
                ]
                if weak_chapters:
                    self_reports.append(
                        f"[EXAM PLANNER CHAPTER STATUS] {es.subject_name} (Exam: {es.exam_date}): "
                        f"Chapters needing practice/completion: {', '.join(weak_chapters[:5])}"
                    )

        # 1c. Inspect Daily Availability & Personal Schedule (Daily Check-In Integration)
        daily_sched = repo.get_daily_schedule(inp.student_id)
        active_acts = [a for a in daily_sched.activities if not a.is_cancelled_today]
        next_free_window = (
            daily_sched.available_time_windows[0].window_label
            if daily_sched.available_time_windows
            else "Evening study window"
        )
        self_reports.append(
            f"[DAILY AVAILABILITY & SCHEDULE ({daily_sched.date_iso})] "
            f"Check-in completed: {daily_sched.checkin_completed} | "
            f"Available study hours: {daily_sched.available_study_hours} hrs | "
            f"Next free window: {next_free_window} | "
            f"Unavailable commitments today: {len(active_acts)} "
            f"({', '.join(f'{a.activity_name} ({a.start_time} - {a.end_time})' for a in active_acts[:3]) or 'None — Free All Day'})."
        )

        # 2. Identify Prerequisite Concepts & Possible Misconceptions for Topic
        t_lower = inp.detected_topic.lower()
        q_lower = inp.extracted_question.lower()

        if "fraction" in t_lower or "1/4" in q_lower:
            prereqs = [
                "Least Common Multiple (LCM) of denominators",
                "Equivalent fractions (multiplying numerator and denominator by the same factor)",
            ]
            if not historical_misconceptions:
                historical_misconceptions.append(
                    "Common Grade 6–7 misconception: Adding denominators directly (e.g., 1/4 + 1/6 = 2/10) instead of finding LCM(4, 6) = 12."
                )
            diag_q = "Diagnostic Check: Before we add 1/4 and 1/6, what is the Least Common Multiple (LCM) of the denominators 4 and 6?"
        elif "integer" in t_lower:
            prereqs = ["Number line direction", "Absolute value of integers"]
            diag_q = "Diagnostic Check: On a number line, if you start at -3 and move 5 steps to the right, where do you land?"
        elif "nutrition" in t_lower or "photosynthesis" in q_lower:
            prereqs = ["Plant leaf structure (stomata & chlorophyll)", "Raw materials needed by plants"]
            diag_q = "Diagnostic Check: Which green pigment in plant leaves captures sunlight energy during photosynthesis?"
        elif "acid" in t_lower or "base" in q_lower:
            prereqs = ["Natural indicators (Litmus, Turmeric)", "pH taste/touch properties"]
            diag_q = "Diagnostic Check: What happens when blue litmus paper is dipped into an acidic solution like lemon juice?"
        else:
            prereqs = [f"Foundational {inp.detected_subject} definitions", "Step-by-step equation setup"]
            diag_q = f"Diagnostic Check: What is the first given quantity or rule we need to use for '{inp.detected_topic}'?"

        # 3. Determine Conditional Pedagogical Route
        missing_prereq_flag = False
        missing_prereq_topic: Optional[str] = None

        # Detect if question or historical gap shows missing prerequisite (e.g., LCM)
        if (
            inp.student_intent == "prerequisite_help"
            or "don't know lcm" in q_lower
            or "what is lcm" in q_lower
            or any("lcm" in g.lower() for g in knowledge_gaps)
        ):
            missing_prereq_flag = True
            missing_prereq_topic = prereqs[0]

        if inp.student_intent == "practice_request" or (
            topic_mastered_in_verified_test and "already understand" in q_lower
        ):
            route: Literal[
                "TEACH_PREREQUISITE_FIRST",
                "MOVE_DIRECTLY_TO_PRACTICE",
                "STEP_BY_STEP_GUIDED_TUTORING",
            ] = "MOVE_DIRECTLY_TO_PRACTICE"
        elif missing_prereq_flag:
            route = "TEACH_PREREQUISITE_FIRST"
        else:
            route = "STEP_BY_STEP_GUIDED_TUTORING"

        elapsed_ms = round((time.perf_counter() - start_t) * 1000, 2)

        return LearningDiagnosisOutput(
            executed_at=utc_now(),
            duration_ms=elapsed_ms,
            model_used=str(model_res["model_used"]),
            prerequisite_concepts=prereqs,
            missing_prerequisite_detected=missing_prereq_flag,
            missing_prerequisite_topic=missing_prereq_topic,
            already_mastered_topic=topic_mastered_in_verified_test,
            detected_historical_misconceptions=historical_misconceptions,
            specific_knowledge_gaps=knowledge_gaps,
            verified_learning_evidence=verified_evidence,
            student_self_reported_difficulties=self_reports,
            diagnostic_question=diag_q,
            recommended_pedagogical_route=route,
            explanation_language=inp.preferred_explanation_language,
        )

