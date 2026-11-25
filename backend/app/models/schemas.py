"""
SparkMinds AI — Pydantic Schemas for Authentication, 7-Step Onboarding,
4 Separate Language Settings, Permanent Multi-Year Academic History,
and the 4 Specialist AI Agents.
"""
from typing import Dict, List, Literal, Optional
import uuid
from pydantic import BaseModel, Field, model_validator


class LanguagePreferences(BaseModel):
    """
    Section 8.1: Maintain Four Separate Language Settings.
    Never assume that these four settings are identical.
    """
    school_medium_language: str = Field(..., min_length=1, description="1. School medium of instruction")
    preferred_explanation_language: str = Field(..., min_length=1, description="2. Mandatory preferred explanation language")
    secondary_explanation_language: Optional[str] = Field(default=None, description="3. Optional secondary language for bilingual mode")
    interface_display_language: str = Field(default="English", description="4. Interface display language")


class SubjectConfidenceSelfReport(BaseModel):
    """
    Step 4: Student self-reported confidence per subject.
    Stored explicitly as SELF_REPORTED evidence, never as verified assessment scores.
    """
    subject_code: str
    subject_name: str
    confidence_level: Literal["Strong", "Okay", "Need help", "Difficult"]
    difficult_topics: List[str] = Field(default_factory=list)


class OnboardingStep1Data(BaseModel):
    age: int = Field(..., ge=4, le=20)
    grade: int = Field(..., ge=1, le=12)
    school_board: Literal["CBSE", "ICSE", "STATE", "OTHER"]
    state_name: Optional[str] = None
    other_board_name: Optional[str] = None
    school_medium: str = Field(..., min_length=1)
    preferred_explanation_language: str = Field(..., min_length=1)
    secondary_explanation_language: Optional[str] = None
    interface_display_language: str = Field(default="English")

    @model_validator(mode="before")
    @classmethod
    def normalize_step1_aliases(cls, data):
        if isinstance(data, dict):
            data = dict(data)
            if data.get("other_board_text") and not data.get("other_board_name"):
                data["other_board_name"] = data["other_board_text"]
        return data

    @model_validator(mode="after")
    def validate_mandatory_explanation_language(self):
        if not self.preferred_explanation_language or not self.preferred_explanation_language.strip():
            raise ValueError("Preferred explanation language is mandatory and cannot be empty.")
        if self.school_board == "STATE" and not self.state_name:
            raise ValueError("State selection is required when State Board is selected.")
        return self


class OnboardingSubmission(BaseModel):
    """
    Complete 7-Step Multiple-Choice Onboarding Payload.
    Proves that every mandatory question is completed via selectable choices without typing custom text.
    """
    student_id: str
    academic_year_label: str = Field(default="2026-2027")
    step1: OnboardingStep1Data
    # Step 2: Selected subjects
    selected_subjects: List[str] = Field(..., min_length=1)
    other_subject_optional: Optional[str] = None
    # Step 3: Subjects to improve (subset of Step 2)
    help_with_all_subjects: bool = False
    subjects_to_improve: List[str] = Field(..., min_length=1)
    # Step 4: Strengths & Weaknesses (Self-Reports)
    subject_confidence: List[SubjectConfidenceSelfReport] = Field(..., min_length=1)
    main_improvement_priority: Optional[str] = Field(default="Understand difficult concepts")
    # Step 5: Learning Challenges
    learning_challenges: List[str] = Field(..., min_length=1)
    when_need_most_help: List[str] = Field(..., min_length=1)
    challenge_frequency: Literal["Almost every day", "Often", "Sometimes", "Rarely"]
    subject_specific_difficulties: List[str] = Field(default_factory=list)
    other_challenge_optional: Optional[str] = None
    # Step 6: Learning Goals & Special Everything Option
    everything_goal_selected: bool = False
    selected_goals: List[str] = Field(..., min_length=1)
    primary_goal: Optional[str] = None

    @model_validator(mode="after")
    def validate_onboarding_consistency(self):
        # Step 3 Rule: If help_with_all_subjects is True, subjects_to_improve must match selected_subjects
        if self.help_with_all_subjects:
            self.subjects_to_improve = list(self.selected_subjects)
        else:
            invalid = [s for s in self.subjects_to_improve if s not in self.selected_subjects]
            if invalid:
                raise ValueError(f"Subjects to improve must be chosen from selected subjects: {invalid}")

        # Step 6 Rule: Everything Goal Synchronization
        all_9_goal_ids = {"g1", "g2", "g3", "g4", "g5", "g6", "g7", "g8", "g9"}
        if self.everything_goal_selected:
            self.selected_goals = sorted(list(all_9_goal_ids))
        elif all_9_goal_ids.issubset(set(self.selected_goals)):
            self.everything_goal_selected = True

        return self


class EvidenceRecord(BaseModel):
    """
    Section 10.5: Evidence-Based Analysis.
    Strictly distinguishes Actual Assessments, Homework/Practice, Student Self-Reports,
    Parent/Teacher Feedback, and AI Estimates.
    """
    record_id: str
    academic_year_id: str
    grade: int
    subject_code: str
    subject_name: str
    topic_name: str
    evidence_type: Literal[
        "ACTUAL_ASSESSMENT",
        "HOMEWORK_PRACTICE",
        "STUDENT_SELF_REPORT",
        "PARENT_TEACHER_FEEDBACK",
        "AI_ESTIMATE",
    ]
    score_percentage: Optional[float] = None
    qualitative_rating: Optional[str] = None
    trend_indicator: Literal[
        "Improvement",
        "Decline",
        "Needs attention",
        "Consistent performance",
        "Learning gap resolved",
    ] = "Needs attention"
    recorded_at: str
    notes: str = ""


class AcademicYearProfile(BaseModel):
    """
    Section 10.1: Separate Academic-Year Profile.
    Preserved permanently from Grade 1 through Grade 12. Never overwritten during promotion.
    """
    academic_year_id: str
    student_id: str
    academic_year_label: str
    grade: int = Field(..., ge=1, le=12)
    school_board: str
    state_name: Optional[str] = None
    school_name_same_as_previous: bool = True
    language_preferences: LanguagePreferences
    subjects_studied: List[str]
    subjects_to_improve: List[str]
    subject_confidence_self_reports: List[SubjectConfidenceSelfReport]
    learning_challenges: List[str]
    when_need_most_help: List[str]
    challenge_frequency: str
    everything_goal_selected: bool
    learning_goals: List[str]
    primary_goal: Optional[str] = None
    status: Literal["ACTIVE", "COMPLETED_PROMOTED", "COMPLETED_REPEATED", "TRANSFERRED"] = "ACTIVE"
    is_locked_historical: bool = False
    evidence_records: List[EvidenceRecord] = Field(default_factory=list)
    ai_recommendations_history: List[Dict[str, object]] = Field(default_factory=list)
    unresolved_learning_gaps: List[str] = Field(default_factory=list)
    resolved_learning_gaps: List[str] = Field(default_factory=list)


class AnnualProgressionRequest(BaseModel):
    """
    Section 11: Annual Academic Progression Workflow.
    Multiple-choice confirmation before creating a new academic-year profile.
    """
    student_id: str
    new_academic_year_label: str = Field(default="2027-2028")
    promotion_decision: Literal[
        "Yes",
        "No",
        "I am repeating my current grade",
        "I am changing schools",
    ]
    board_unchanged: Literal["Yes, same board", "No, I have changed my board"]
    same_school: Literal["Yes", "No"]
    new_school_board: Optional[Literal["CBSE", "ICSE", "STATE", "OTHER"]] = None
    new_state_name: Optional[str] = None
    reselected_subjects: List[str] = Field(..., min_length=1)
    reselected_improvement_subjects: List[str] = Field(..., min_length=1)
    updated_preferred_explanation_language: str = Field(..., min_length=1)
    updated_secondary_explanation_language: Optional[str] = None
    updated_school_medium: str = Field(..., min_length=1)
    updated_challenges: List[str] = Field(default_factory=list)
    updated_goals: List[str] = Field(default_factory=list)
    everything_goal_selected: bool = False


# ============================================================================
# REDESIGNED AGENTIC TUTOR & LEARNING MEMORY SCHEMAS (SECTIONS 2, 3, 6, 7, 8)
# ============================================================================

class AgentExecutionLog(BaseModel):
    """
    Section 6 & 8: Real-time visible agent execution telemetry entry.
    Never simulated; derived strictly from actual backend agent execution.
    """
    log_id: str
    agent_id: Literal["understanding", "diagnosis", "teaching", "assessment", "orchestrator"]
    agent_name: str
    task_description: str
    status: Literal["running", "completed", "failed", "skipped"]
    started_at: str
    completed_at: str
    duration_ms: float
    model_invoked: str
    output_summary: str
    error_message: Optional[str] = None
    student_action_required: bool = False


class LearningMemoryRecord(BaseModel):
    """
    Section 7: Structured Learning Memory connected to the student's Academic Journey.
    Never overwrites previous academic-year learning history.
    """
    memory_id: str
    session_id: str
    student_id: str
    academic_year: str
    grade: int
    subject: str
    topic: str
    question: str
    student_attempts: List[str] = Field(default_factory=list)
    detected_misconceptions: List[str] = Field(default_factory=list)
    hints_provided: List[str] = Field(default_factory=list)
    assessment_result: Literal["correct", "incorrect", "in_progress", "mastery_verified"] = "in_progress"
    concept_mastery_evidence: Optional[str] = None
    recommended_next_action: str = ""
    explanation_language: str
    secondary_explanation_language: Optional[str] = None
    recorded_at: str


# ============================================================================
# COMPLETE PLATFORM MODULE SCHEMAS (STUDY PLANNER, HOMEWORK, EXAMS, REVISION, PROJECTS)
# ============================================================================

def parse_time_to_minutes(time_str: str) -> int:
    """
    Parses a 12-hour AM/PM time string (e.g., '4:00 PM', '08:30 AM', '12:00 PM', '12:30 AM')
    or 24-hour string (e.g., '16:00', '08:30') into minutes since midnight (0..1439).
    """
    raw = (time_str or "").strip().upper()
    if not raw:
        raise ValueError("Time value cannot be empty.")
    has_am = "AM" in raw
    has_pm = "PM" in raw
    cleaned = raw.replace("AM", "").replace("PM", "").strip()
    parts = cleaned.split(":")
    if len(parts) < 2:
        hour = int(parts[0])
        minute = 0
    else:
        hour = int(parts[0])
        minute = int(parts[1])
    if minute < 0 or minute > 59:
        raise ValueError(f"Invalid minutes in time '{time_str}'.")
    if has_am or has_pm:
        if hour < 1 or hour > 12:
            raise ValueError(f"12-hour time '{time_str}' must have hour between 1 and 12.")
        if has_pm and hour != 12:
            hour += 12
        elif has_am and hour == 12:
            hour = 0
    else:
        if hour < 0 or hour > 23:
            raise ValueError(f"24-hour time '{time_str}' must have hour between 0 and 23.")
    return hour * 60 + minute


def format_minutes_to_12h(total_minutes: int) -> str:
    """Formats minutes from midnight (0..1439) into 12-hour AM/PM display (e.g. '4:00 PM')."""
    clamped = max(0, min(23 * 60 + 59, int(total_minutes)))
    h24 = clamped // 60
    m = clamped % 60
    period = "AM" if h24 < 12 else "PM"
    h12 = h24 % 12
    if h12 == 0:
        h12 = 12
    return f"{h12}:{m:02d} {period}"


class StudyTaskItem(BaseModel):
    task_id: str
    day_label: str  # e.g., "Monday" or "Today"
    date_iso: str
    time_slot: str  # e.g., "6:00 PM - 6:45 PM"
    subject: str
    chapter: str
    session_type: Literal[
        "Concept Study",
        "Practice",
        "Revision",
        "Mock Exam",
        "Break",
        "Catch-up",
        "Homework",
        "Unavailable",
    ]
    duration_minutes: int
    completed: bool = False
    missed: bool = False
    postponed: bool = False
    priority_reason: Optional[str] = None
    subject_exam_date: Optional[str] = None
    chapter_difficulty: Optional[Literal["Easy", "Medium", "Difficult"]] = None


class ExamChapterEntry(BaseModel):
    """
    Requirement 1: Student-defined chapter inside an Exam Study Planner subject.
    Never invents chapter names; students enter their actual chapter names.
    """
    chapter_id: str = Field(default_factory=lambda: f"ch_{uuid.uuid4().hex[:6]}")
    chapter_number: int = Field(default=1, ge=1)
    chapter_name: str = Field(..., min_length=1)
    difficulty: Literal["Easy", "Medium", "Difficult"] = "Medium"
    completion_status: Literal["Not Started", "In Progress", "Completed"] = "Not Started"
    additional_practice_needed: bool = False
    revision_requirements: str = "Standard Revision"


class ExamSubjectEntry(BaseModel):
    """
    Requirement 1: Subject entry inside the Exam Study Planner with individual exam date,
    optional exam time, optional maximum marks, difficulty, confidence, and dynamic chapters.
    """
    subject_id: str = Field(default="sub_1")
    subject_name: str = Field(..., min_length=1)
    number_of_chapters: int = Field(..., ge=1, le=60)
    exam_date: str = Field(..., description="Individual exam date YYYY-MM-DD")
    exam_time: Optional[str] = Field(default="09:30", description="Optional exam time HH:MM or 12-hr")
    maximum_marks: Optional[float] = Field(default=100.0, gt=0)
    subject_difficulty: Literal["Easy", "Medium", "Difficult"] = "Medium"
    confidence_level: Optional[Literal["Low", "Medium", "High", "Need help", "Okay", "Strong"]] = "Medium"
    chapters: List[ExamChapterEntry] = Field(default_factory=list)

    @model_validator(mode="after")
    def sync_chapters_count(self):
        # Ensure chapters list matches number_of_chapters without inventing fake syllabus topics
        if len(self.chapters) < self.number_of_chapters:
            for idx in range(len(self.chapters), self.number_of_chapters):
                self.chapters.append(
                    ExamChapterEntry(
                        chapter_id=f"{self.subject_id}_ch_{idx + 1}",
                        chapter_number=idx + 1,
                        chapter_name=f"Chapter {idx + 1}",
                        difficulty=self.subject_difficulty,
                        completion_status="Not Started",
                        additional_practice_needed=(self.subject_difficulty == "Difficult"),
                        revision_requirements="Standard Revision",
                    )
                )
        elif len(self.chapters) > self.number_of_chapters:
            self.chapters = self.chapters[: self.number_of_chapters]
        for idx, ch in enumerate(self.chapters):
            ch.chapter_number = idx + 1
            if not ch.chapter_id:
                ch.chapter_id = f"{self.subject_id}_ch_{idx + 1}"
        return self


class ExamSubjectUpsertRequest(BaseModel):
    student_id: Optional[str] = None
    subject_id: Optional[str] = None
    subject_name: str = Field(default="Mathematics", min_length=1)
    number_of_chapters: int = Field(default=4, ge=1, le=60)
    exam_date: str = Field(default="2026-12-10", min_length=8)
    exam_time: Optional[str] = "9:30 AM - 12:30 PM"
    maximum_marks: Optional[float] = 100.0
    subject_difficulty: Literal["Easy", "Medium", "Difficult"] = "Medium"
    confidence_level: Optional[str] = "Medium"
    student_confidence_level: Optional[str] = None
    chapters: List[ExamChapterEntry] = Field(default_factory=list)
    daily_study_hours: Optional[float] = None
    preferred_study_time: Optional[str] = None
    auto_regenerate_timetable: bool = True

    @model_validator(mode="before")
    @classmethod
    def unwrap_nested_subject(cls, data):
        if isinstance(data, dict) and isinstance(data.get("subject"), dict):
            merged = {**data, **data["subject"]}
            merged.pop("subject", None)
            if merged.get("student_confidence_level") and not merged.get("confidence_level"):
                merged["confidence_level"] = merged["student_confidence_level"]
            return merged
        if isinstance(data, dict) and data.get("student_confidence_level") and not data.get("confidence_level"):
            data = {**data, "confidence_level": data["student_confidence_level"]}
        return data


class StudyTaskEditRequest(BaseModel):
    completed: Optional[bool] = None
    missed: Optional[bool] = None
    postponed: Optional[bool] = None
    new_date_iso: Optional[str] = None
    new_time_slot: Optional[str] = None
    new_chapter: Optional[str] = None
    new_subject: Optional[str] = None
    new_session_type: Optional[
        Literal[
            "Concept Study",
            "Practice",
            "Revision",
            "Mock Exam",
            "Break",
            "Catch-up",
            "Homework",
            "Unavailable",
        ]
    ] = None
    new_duration_minutes: Optional[int] = None


class PersonalActivityItem(BaseModel):
    """
    Daily Availability & Personal Schedule Activity Entry (School, Tuition, Chess, Drawing,
    Sports, Music, Travel, Family, Personal, or Unavailable block) in 12-hour AM/PM format.
    """
    activity_id: str = Field(default_factory=lambda: f"act_{uuid.uuid4().hex[:6]}")
    activity_name: str = Field(..., min_length=1)
    category: str = Field(default="Extracurricular")
    start_time: str = Field(..., min_length=3, description="12-hour AM/PM e.g. '4:00 PM'")
    end_time: str = Field(..., min_length=3, description="12-hour AM/PM e.g. '5:00 PM'")
    start_minutes: int = 0
    end_minutes: int = 0
    duration_minutes: int = 0
    location: Optional[str] = ""
    notes: Optional[str] = ""
    recurrence_type: Literal[
        "Only today",
        "Repeated on selected weekdays",
        "Repeated every day",
    ] = "Only today"
    recurring_weekdays: List[str] = Field(default_factory=list)
    is_cancelled_today: bool = False

    @model_validator(mode="before")
    @classmethod
    def normalize_activity_aliases(cls, data: object):
        if isinstance(data, dict):
            if "recurrence" in data and "recurrence_type" not in data:
                data["recurrence_type"] = data["recurrence"]
            if "recurrence_days" in data and "recurring_weekdays" not in data:
                data["recurring_weekdays"] = data["recurrence_days"]
        return data

    @model_validator(mode="after")
    def validate_and_normalize_times(self):
        if not self.activity_name or not self.activity_name.strip():
            raise ValueError("Activity name cannot be empty.")
        self.activity_name = self.activity_name.strip()
        s_mins = parse_time_to_minutes(self.start_time)
        e_mins = parse_time_to_minutes(self.end_time)
        if e_mins <= s_mins:
            raise ValueError(
                f"Invalid time range for '{self.activity_name}': End time ({self.end_time}) must be after start time ({self.start_time})."
            )
        self.start_minutes = s_mins
        self.end_minutes = e_mins
        self.duration_minutes = e_mins - s_mins
        self.start_time = format_minutes_to_12h(s_mins)
        self.end_time = format_minutes_to_12h(e_mins)
        if self.recurrence_type == "Repeated every day":
            self.recurring_weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        elif self.recurrence_type == "Only today":
            self.recurring_weekdays = []
        return self


class AvailableTimeWindow(BaseModel):
    window_id: str
    start_time: str
    end_time: str
    start_minutes: int
    end_minutes: int
    duration_minutes: int
    period_label: str
    window_label: str = ""

    @model_validator(mode="after")
    def populate_window_label(self):
        if not self.window_label:
            self.window_label = f"{self.start_time} - {self.end_time}"
        return self


class DailyScheduleCheckInRequest(BaseModel):
    """
    Daily Schedule Check-In payload submitted by the student before generating today's personalised study plan.
    Validates that no active activities overlap and all time ranges are valid.
    """
    student_id: Optional[str] = None
    date_iso: Optional[str] = None
    timezone_name: str = "Asia/Kolkata"
    free_all_day: bool = False
    wake_up_time: str = "6:30 AM"
    sleep_time: str = "9:30 PM"
    preferred_study_hours: Optional[float] = None
    current_time_12h: Optional[str] = None
    activities: List[PersonalActivityItem] = Field(default_factory=list)
    auto_generate_daily_plan: bool = True

    @model_validator(mode="before")
    @classmethod
    def normalize_checkin_aliases(cls, data: object):
        if isinstance(data, dict):
            if "sleep_start_time" in data and "sleep_time" not in data:
                data["sleep_time"] = data["sleep_start_time"]
        return data

    @model_validator(mode="after")
    def validate_non_overlapping_activities(self):
        w_mins = parse_time_to_minutes(self.wake_up_time)
        s_mins = parse_time_to_minutes(self.sleep_time)
        if s_mins <= w_mins:
            raise ValueError("Sleep time must be later than wake-up time.")
        self.wake_up_time = format_minutes_to_12h(w_mins)
        self.sleep_time = format_minutes_to_12h(s_mins)

        active_acts = [a for a in self.activities if not a.is_cancelled_today]
        sorted_acts = sorted(active_acts, key=lambda x: (x.start_minutes, x.end_minutes))
        for idx in range(len(sorted_acts) - 1):
            curr = sorted_acts[idx]
            nxt = sorted_acts[idx + 1]
            if curr.end_minutes > nxt.start_minutes:
                raise ValueError(
                    f"Overlapping activities detected: '{curr.activity_name}' ({curr.start_time} – {curr.end_time}) "
                    f"overlaps with '{nxt.activity_name}' ({nxt.start_time} – {nxt.end_time}). Please adjust the times."
                )
        return self


class DailyActivityUpdateRequest(BaseModel):
    student_id: Optional[str] = None
    date_iso: Optional[str] = None
    activity_id: Optional[str] = None
    delete_activity: bool = False
    activity_name: Optional[str] = None
    category: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    recurrence_type: Optional[
        Literal["Only today", "Repeated on selected weekdays", "Repeated every day"]
    ] = None
    recurring_weekdays: Optional[List[str]] = None
    is_cancelled_today: Optional[bool] = None
    current_time_12h: Optional[str] = None
    regenerate_remaining_plan: bool = True


_WEEKDAY_FULL_MAP = {
    "Mon": "Monday",
    "Tue": "Tuesday",
    "Wed": "Wednesday",
    "Thu": "Thursday",
    "Fri": "Friday",
    "Sat": "Saturday",
    "Sun": "Sunday",
}


class DailyScheduleRecord(BaseModel):
    schedule_id: str
    student_id: str
    date_iso: str
    weekday_short: str
    weekday_name: str = ""
    timezone_name: str = "Asia/Kolkata"
    checkin_prompt: str = (
        "Good morning! ☀️ Let's plan your day. What does your schedule look like today?"
    )
    greeting_prompt: str = (
        "Good morning! ☀️ Let's plan your day. What does your schedule look like today?"
    )
    checkin_completed: bool = False
    free_all_day: bool = False
    wake_up_time: str = "6:30 AM"
    sleep_time: str = "9:30 PM"
    activities: List[PersonalActivityItem] = Field(default_factory=list)
    recurring_templates: List[PersonalActivityItem] = Field(default_factory=list)
    unavailable_slots_summary: List[str] = Field(default_factory=list)
    available_time_windows: List[AvailableTimeWindow] = Field(default_factory=list)
    total_unavailable_minutes: int = 0
    total_available_study_minutes: int = 0
    total_available_study_hours: float = 0.0
    available_study_hours: float = 0.0
    next_free_slot_display: Optional[str] = None
    generated_daily_timeline: List[StudyTaskItem] = Field(default_factory=list)

    @model_validator(mode="after")
    def sync_schedule_fields(self):
        if not self.weekday_name:
            self.weekday_name = _WEEKDAY_FULL_MAP.get(self.weekday_short, self.weekday_short)
        if self.total_available_study_hours and not self.available_study_hours:
            self.available_study_hours = self.total_available_study_hours
        elif self.available_study_hours and not self.total_available_study_hours:
            self.total_available_study_hours = self.available_study_hours
        self.greeting_prompt = self.checkin_prompt
        return self
    updated_at: str


class ReminderPreferences(BaseModel):
    """
    Requirement 4: Daily Task Reminders & Android Notification Settings.
    """
    student_id: str = "stu_aarav_g7"
    timezone_name: str = "Asia/Kolkata"
    android_notifications_enabled: bool = False
    android_permission_status: Literal["default", "granted", "denied"] = "default"
    android_notifications_permission: Literal["default", "granted", "denied"] = "default"
    in_app_fallback_enabled: bool = True
    in_app_reminders_enabled: bool = True
    push_notifications_enabled: bool = False
    daily_study_sessions_enabled: bool = True
    pending_chapters_enabled: bool = True
    homework_deadlines_enabled: bool = True
    upcoming_exams_enabled: bool = True
    revision_sessions_enabled: bool = True
    mock_tests_enabled: bool = True
    # Extended Part 17.1 categories & controls
    quiet_hours_enabled: bool = True
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "07:00"
    reminder_frequency: Literal["LOW", "BALANCED", "FREQUENT"] = "BALANCED"
    parent_preferences_respected: bool = True
    custom_reminder_times: List[str] = Field(
        default_factory=lambda: ["6:00 PM", "8:00 AM"]
    )
    reminder_times: Dict[str, str] = Field(
        default_factory=lambda: {
            "daily_study_sessions": "6:00 PM",
            "pending_chapters": "5:00 PM",
            "homework_deadlines": "5:30 PM",
            "upcoming_exams": "8:00 AM",
            "revision_sessions": "7:30 PM",
            "mock_tests": "9:00 AM",
        }
    )
    enabled_categories: Dict[str, bool] = Field(
        default_factory=lambda: {
            "daily_study_sessions": True,
            "pending_chapters": True,
            "homework_deadlines": True,
            "upcoming_exams": True,
            "revision_sessions": True,
            "mock_tests": True,
            "study_reminders": True,
            "daily_learning_goals": True,
            "streak_reminders": True,
            "quiz_and_assessment_reminders": True,
            "revision_alerts": True,
            "weak_topic_practice_reminders": True,
            "study_plan_task_reminders": True,
            "assessment_results_and_feedback": True,
            "ai_tutor_follow_ups": True,
            "achievement_and_badge_alerts": True,
            "weekly_progress_summaries": True,
            "account_and_security_alerts": True,
        }
    )
    task_statuses: Dict[str, Literal["Pending", "Completed", "Postponed", "Missed"]] = Field(default_factory=dict)
    delivered_notification_keys: List[str] = Field(default_factory=list)


class ReminderStatusUpdateRequest(BaseModel):
    student_id: Optional[str] = None
    reminder_id: Optional[str] = None
    notification_id: Optional[str] = None
    status: Literal["Completed", "Postponed", "Missed", "Pending"]
    postponed_to_time: Optional[str] = None
    linked_entity_type: Optional[str] = None
    linked_entity_id: Optional[str] = None

    @model_validator(mode="after")
    def sync_ids(self):
        if not self.reminder_id and self.notification_id:
            self.reminder_id = self.notification_id
        elif not self.notification_id and self.reminder_id:
            self.notification_id = self.reminder_id
        return self


class ParentalConsentVerificationRequest(BaseModel):
    """
    Child Safety — Parent/Guardian Consent & Assistance for Children Under 8.
    Preserves all mandatory guardian consent fields (full name, relationship, parent email,
    parent security PIN, and signed legal attestation statement).
    NOTE: Phone/mobile number and 6-digit OTP have been intentionally removed.
    This records parental consent and does NOT claim independent third-party identity verification.
    """
    student_id: str
    student_full_name: str = Field(default="Student Learner", min_length=1)
    student_age: int = Field(default=6, ge=4, le=20)
    date_of_birth: Optional[str] = None
    grade: int = Field(default=1, ge=1, le=12)
    parent_full_name: str = Field(..., min_length=2)
    relationship_to_child: Literal["Mother", "Father", "Legal Guardian"] = "Mother"
    parent_email: str = Field(..., min_length=5, description="Parent or legal guardian email address (no phone number)")
    parent_access_pin: str = Field(default="", min_length=4, max_length=8, description="4-8 digit parent security PIN")
    parent_pin_code: Optional[str] = None
    guardian_attestation_statement: str = Field(
        ...,
        min_length=10,
        description="Typed parent signature / attestation confirming parental consent",
    )
    child_safety_mode_enabled: bool = True

    @model_validator(mode="before")
    @classmethod
    def normalize_parent_fields(cls, data):
        if isinstance(data, dict):
            data = dict(data)
            if data.get("parent_pin_code") and not data.get("parent_access_pin"):
                data["parent_access_pin"] = data["parent_pin_code"]
            # Reject phone numbers explicitly; allow email passed via legacy alias only if it is a valid email
            if not data.get("parent_email") and data.get("parent_email_or_phone"):
                candidate = str(data.get("parent_email_or_phone") or "").strip()
                if "@" not in candidate:
                    raise ValueError(
                        "Phone numbers are not collected for Parent Verification. Please provide a valid parent or guardian email address."
                    )
                data["parent_email"] = candidate
            # Ignore any removed OTP field without requiring it
            data.pop("verification_otp_code", None)
        return data

    @model_validator(mode="after")
    def validate_parent_email_and_pin(self):
        email = (self.parent_email or "").strip()
        if "@" not in email or "." not in email.split("@")[-1] or len(email.split("@")[0]) < 1:
            raise ValueError(
                "Please enter a valid parent or guardian email address (phone numbers are not accepted)."
            )
        if not self.parent_access_pin.isdigit() or not (4 <= len(self.parent_access_pin) <= 8):
            raise ValueError("Parent security PIN must be 4 to 8 digits.")
        return self


class ExamMarkEntryRequest(BaseModel):
    """
    Requirement 6: Enter Marks After Every Exam with strict validation.
    """
    mark_id: Optional[str] = None
    student_id: Optional[str] = None
    subject: str = Field(..., min_length=1)
    exam_name: str = Field(..., min_length=1)
    exam_type: str = Field(default="Unit Test", min_length=1)
    exam_date: str = Field(..., min_length=8)
    marks_obtained: float
    maximum_marks: float
    remarks: Optional[str] = ""
    chapters_tested: List[str] = Field(default_factory=list)
    officially_verified: bool = False
    verification_status: Optional[str] = None

    @model_validator(mode="after")
    def validate_marks_rules(self):
        if not self.subject.strip():
            raise ValueError("Subject is required.")
        if not self.exam_name.strip():
            raise ValueError("Exam name is required.")
        if not self.exam_date.strip():
            raise ValueError("Exam date is required.")
        if self.maximum_marks <= 0:
            raise ValueError("Maximum marks must be greater than 0.")
        if self.marks_obtained < 0:
            raise ValueError("Marks obtained cannot be negative.")
        if self.marks_obtained > self.maximum_marks:
            raise ValueError(
                f"Marks obtained ({self.marks_obtained}) cannot exceed maximum marks ({self.maximum_marks})."
            )
        if self.verification_status == "OFFICIALLY_VERIFIED":
            self.officially_verified = True
        return self


class ExamMarkRecord(BaseModel):
    mark_id: str
    student_id: str
    academic_year_id: str
    grade: int
    subject: str
    exam_name: str
    exam_type: str
    exam_date: str
    marks_obtained: float
    maximum_marks: float
    percentage: float
    remarks: str = ""
    chapters_tested: List[str] = Field(default_factory=list)
    verification_status: Literal["STUDENT_REPORTED", "OFFICIALLY_VERIFIED"] = "STUDENT_REPORTED"
    trend_indicator: Literal["Improvement", "Decline", "Needs attention", "Consistent performance"] = "Consistent performance"
    trend: Literal["Improvement", "Decline", "Needs attention", "Consistent performance"] = "Consistent performance"
    previous_percentage: Optional[float] = None
    delta_percentage: Optional[float] = None
    needs_additional_attention: bool = False
    ai_buddy_recommendations: List[str] = Field(default_factory=list)
    recorded_at: str = ""
    created_at: str
    updated_at: str

    @model_validator(mode="after")
    def sync_trend_and_dates(self):
        if self.trend_indicator and self.trend == "Consistent performance":
            self.trend = self.trend_indicator
        if not self.recorded_at:
            self.recorded_at = self.created_at
        return self


class StudyPlanGenerateRequest(BaseModel):
    student_id: str
    exam_name: str = Field(default="Term 1 / Half-Yearly Assessment")
    exam_date: str = Field(default="2026-12-10", description="YYYY-MM-DD")
    daily_study_hours: float = Field(default=2.0, ge=0.5, le=10.0)
    preferred_study_time: Literal["Morning (6 AM - 9 AM)", "Afternoon (3 PM - 6 PM)", "Evening (6 PM - 9 PM)", "Flexible"] = "Evening (6 PM - 9 PM)"
    selected_subjects_and_chapters: Dict[str, List[str]] = Field(default_factory=dict, description="Map of subject name -> list of curriculum or student-supplied chapters")
    exam_subjects: Optional[List[ExamSubjectEntry]] = Field(default=None, description="Individual exam subjects with their own exam dates, times, difficulty, and chapters")
    preserve_completed_tasks: bool = True
    weak_subjects: List[str] = Field(default_factory=list)
    strong_subjects: List[str] = Field(default_factory=list)
    academic_goal: str = Field(default="Score 85%+ and master weak chapters before the exam")


class StudyPlanRecord(BaseModel):
    plan_id: str
    student_id: str
    exam_name: str
    exam_date: str
    days_until_exam: int
    daily_study_hours: float
    preferred_study_time: str
    weak_subjects: List[str]
    strong_subjects: List[str]
    academic_goal: str
    exam_subjects: List[ExamSubjectEntry] = Field(default_factory=list)
    subject_time_allocation_hours_per_week: Dict[str, float]
    subject_allocation_percentages: Dict[str, float]
    chapter_completion_targets: List[Dict[str, str]]
    daily_timetable: List[StudyTaskItem]
    weekly_timetable: Dict[str, List[StudyTaskItem]]
    complete_exam_schedule: List[StudyTaskItem] = Field(default_factory=list)
    monthly_preparation_milestones: List[Dict[str, str]]
    mock_exam_dates: List[str]
    catch_up_schedule: List[StudyTaskItem] = Field(default_factory=list)
    daily_checkin_completed: bool = False
    daily_available_hours: Optional[float] = None
    today_combined_timeline: List[StudyTaskItem] = Field(default_factory=list)
    created_at: str
    updated_at: str


class HomeworkCreateRequest(BaseModel):
    student_id: str
    subject: str
    chapter: str
    title: str
    description: str
    due_date: str
    priority: Literal["High", "Medium", "Low"] = "Medium"
    estimated_minutes: int = Field(default=30, ge=5, le=300)
    image_base64: Optional[str] = None


class HomeworkStatusUpdateRequest(BaseModel):
    status: Optional[Literal["pending", "in_progress", "completed"]] = None
    priority: Optional[Literal["High", "Medium", "Low"]] = None
    due_date: Optional[str] = None
    estimated_minutes: Optional[int] = None
    linked_tutor_session_id: Optional[str] = None


class HomeworkItem(BaseModel):
    homework_id: str
    student_id: str
    subject: str
    chapter: str
    title: str
    description: str
    due_date: str
    priority: Literal["High", "Medium", "Low"]
    estimated_minutes: int
    status: Literal["pending", "in_progress", "completed"] = "pending"
    image_base64: Optional[str] = None
    extracted_question_from_image: Optional[str] = None
    linked_tutor_session_id: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


class ExamGenerateRequest(BaseModel):
    student_id: str
    exam_mode: Literal["Chapter Test", "Subject Mock Test", "Custom Paper"] = "Chapter Test"
    subject: str = "Mathematics"
    chapters: List[str] = Field(default_factory=list)
    duration_minutes: int = Field(default=20, ge=5, le=180)
    question_count: int = Field(default=5, ge=3, le=20)
    explanation_language: Optional[str] = None


class ExamQuestionItem(BaseModel):
    question_id: str
    question_number: int
    question_type: Literal["MCQ", "SHORT_ANSWER", "LONG_ANSWER"]
    subject: str
    chapter: str
    question_text: str
    options: List[str] = Field(default_factory=list)
    correct_answer: str
    key_concepts_required: List[str] = Field(default_factory=list)
    marks: int = 2
    detailed_explanation: str


class ExamSubmissionRequest(BaseModel):
    student_id: str
    answers: Dict[str, str]
    time_taken_seconds: int = 300


class ExamQuestionEvaluation(BaseModel):
    question_id: str
    question_number: int
    question_type: str
    chapter: str
    student_answer: str
    correct_answer: str
    is_correct: bool
    marks_awarded: float
    max_marks: int
    feedback_and_explanation: str


class MockExamRecord(BaseModel):
    exam_id: str
    student_id: str
    grade: int
    school_board: str
    exam_mode: str
    title: str
    subject: str
    chapters: List[str]
    duration_minutes: int
    total_marks: int
    questions: List[ExamQuestionItem]
    status: Literal["GENERATED", "COMPLETED"] = "GENERATED"
    score_awarded: Optional[float] = None
    score_percentage: Optional[float] = None
    question_evaluations: List[ExamQuestionEvaluation] = Field(default_factory=list)
    weak_topics_detected: List[str] = Field(default_factory=list)
    improvement_recommendations: List[str] = Field(default_factory=list)
    created_at: str
    submitted_at: Optional[str] = None


class RevisionGenerateRequest(BaseModel):
    student_id: str
    subject: str
    topic: str
    language: Optional[str] = None


class RevisionReviewUpdateRequest(BaseModel):
    student_id: str
    recall_quality: Literal["Easy", "Good", "Hard", "Forgot"]
    quiz_answer_correct: Optional[bool] = None


class RevisionCardItem(BaseModel):
    revision_id: str
    student_id: str
    subject: str
    topic: str
    front_prompt: str
    back_explanation: str
    active_recall_question: str
    active_recall_options: List[str] = Field(default_factory=list)
    active_recall_answer: str
    source_tag: Literal["Weak Topic", "Forgotten Topic", "Mock Exam Mistake", "Tutor Misconception", "Curriculum Core"]
    interval_days: int = 1
    repetition_count: int = 0
    next_review_date: str
    last_reviewed_at: Optional[str] = None
    completed_today: bool = False
    mastery_level: Literal["Needs Immediate Review", "Reviewing", "Retained"] = "Needs Immediate Review"


class ProjectGenerateRequest(BaseModel):
    student_id: str
    subject: str = "Science"
    chapter_or_theme: str = "Acids, Bases & Salts"
    project_type: Literal["Science Experiment", "Working Model", "Research & Survey", "Creative Poster / Presentation"] = "Science Experiment"


class ProjectMilestoneUpdateRequest(BaseModel):
    student_id: str
    milestone_index: Optional[int] = None
    completed: Optional[bool] = None
    student_notes: Optional[str] = None
    student_creativity_response: Optional[str] = None


class ProjectRecord(BaseModel):
    project_id: str
    student_id: str
    grade: int
    subject: str
    chapter_or_theme: str
    project_type: str
    title: str
    learning_objective: str
    materials_needed: List[str]
    milestones: List[Dict[str, object]]
    research_guidance_prompts: List[str]
    presentation_slide_outline: List[str]
    socratic_creativity_challenge: str
    student_notes: str = ""
    student_creativity_response: str = ""
    progress_percentage: int = 0
    created_at: str
    updated_at: str



