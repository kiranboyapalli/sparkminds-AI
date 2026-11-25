"""
SparkMinds AI — Dedicated AI & Algorithmic Platform Engines for All Student Modules:
1. SmartStudyPlannerEngine (Daily/Weekly/Monthly timetables, weak-subject weighting, breaks, catch-up schedule)
2. ExamPreparationEngine (Curriculum-aligned MCQs + Short + Long questions, auto-evaluation, detailed explanations)
3. SmartRevisionEngine (Flashcards, Active Recall quizzes, Spaced Repetition, Forgotten/Weak topic detection)
4. ProjectCreativityLabEngine (Curriculum project ideas, Socratic milestone guidance, presentation outline, creativity challenge)
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
import uuid
from app.models.schemas import (
    AvailableTimeWindow,
    DailyScheduleRecord,
    ExamChapterEntry,
    ExamGenerateRequest,
    ExamQuestionEvaluation,
    ExamQuestionItem,
    ExamSubmissionRequest,
    ExamSubjectEntry,
    HomeworkItem,
    MockExamRecord,
    PersonalActivityItem,
    ProjectGenerateRequest,
    ProjectRecord,
    RevisionCardItem,
    RevisionGenerateRequest,
    StudyPlanGenerateRequest,
    StudyPlanRecord,
    StudyTaskItem,
    format_minutes_to_12h,
    parse_time_to_minutes,
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def today_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


class SmartStudyPlannerEngine:
    """
    Section 1.C: Intelligent Study Planning Engine.
    - Respects available daily study hours strictly.
    - Allocates higher time weight to weak subjects and unresolved learning gaps.
    - Inserts realistic break periods so total study hours never exceed the student's daily limit.
    - Never invents school syllabus chapters; uses only curriculum chapters or student-supplied chapters.
    """

    @staticmethod
    def generate_study_plan(
        req: StudyPlanGenerateRequest,
        unresolved_gaps: List[str],
        existing_plan: Optional[StudyPlanRecord] = None,
    ) -> StudyPlanRecord:
        now_dt = datetime.now(timezone.utc)
        today_str = now_dt.strftime("%Y-%m-%d")
        today_date_only = datetime.strptime(today_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

        # Build or normalize ExamSubjectEntry list
        exam_subjects: List[ExamSubjectEntry] = []
        if req.exam_subjects:
            exam_subjects = list(req.exam_subjects)
        elif existing_plan and existing_plan.exam_subjects and not req.selected_subjects_and_chapters:
            exam_subjects = list(existing_plan.exam_subjects)
        else:
            # Convert selected_subjects_and_chapters into ExamSubjectEntry items
            raw_map = req.selected_subjects_and_chapters or {"Mathematics": ["Chapter 1"], "Science": ["Chapter 1"]}
            weak_set = {s.lower() for s in req.weak_subjects}
            strong_set = {s.lower() for s in req.strong_subjects}
            for idx, (sub_name, ch_names) in enumerate(raw_map.items()):
                ch_list = ch_names if ch_names else ["Chapter 1"]
                is_w = sub_name.lower() in weak_set or any(w in sub_name.lower() for w in weak_set)
                is_s = sub_name.lower() in strong_set or any(s in sub_name.lower() for s in strong_set)
                diff: str = "Difficult" if is_w else ("Easy" if is_s else "Medium")
                conf: str = "Need help" if is_w else ("Strong" if is_s else "Okay")
                # Check if existing_plan already has an exam_date for this subject
                existing_sub = next(
                    (es for es in (existing_plan.exam_subjects if existing_plan else []) if es.subject_name.lower() == sub_name.lower()),
                    None,
                )
                sub_exam_date = existing_sub.exam_date if existing_sub else req.exam_date
                exam_subjects.append(
                    ExamSubjectEntry(
                        subject_id=existing_sub.subject_id if existing_sub else f"auto_sub_{idx + 1}_{uuid.uuid4().hex[:4]}",
                        subject_name=sub_name,
                        number_of_chapters=len(ch_list),
                        exam_date=sub_exam_date,
                        exam_time=existing_sub.exam_time if existing_sub else "09:30",
                        maximum_marks=existing_sub.maximum_marks if existing_sub else 100.0,
                        subject_difficulty=diff,  # type: ignore
                        confidence_level=conf,  # type: ignore
                        chapters=[
                            ExamChapterEntry(
                                chapter_id=f"ch_{idx + 1}_{c_idx + 1}",
                                chapter_number=c_idx + 1,
                                chapter_name=c_name,
                                difficulty=diff,  # type: ignore
                                completion_status="Not Started",
                                additional_practice_needed=is_w,
                                revision_requirements="Intensive Revision + Practice" if is_w else "Standard Revision",
                            )
                            for c_idx, c_name in enumerate(ch_list)
                        ],
                    )
                )

        # Ensure req.selected_subjects_and_chapters stays synchronized with exam_subjects
        synced_map: Dict[str, List[str]] = {}
        for es in exam_subjects:
            synced_map[es.subject_name] = [c.chapter_name for c in es.chapters]
        req.selected_subjects_and_chapters = synced_map

        # Calculate days remaining per subject and overall
        subject_exam_dt_map: Dict[str, datetime] = {}
        subject_days_remaining: Dict[str, int] = {}
        for es in exam_subjects:
            try:
                sdt = datetime.strptime(es.exam_date[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except Exception:
                sdt = today_date_only + timedelta(days=30)
            subject_exam_dt_map[es.subject_name] = sdt
            subject_days_remaining[es.subject_name] = max(1, (sdt - today_date_only).days)

        try:
            latest_exam_dt = max(subject_exam_dt_map.values()) if subject_exam_dt_map else datetime.strptime(req.exam_date[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            days_until_exam = max(1, (latest_exam_dt - today_date_only).days)
        except Exception:
            days_until_exam = 30

        subjects = [es.subject_name for es in exam_subjects]
        if not subjects:
            subjects = ["Mathematics", "Science"]

        # Calculate subject weights:
        # 1. Earlier exam dates get higher urgency weight
        # 2. Subject difficulty (Difficult=2.4, Medium=1.4, Easy=0.9) and weak_subjects boost weight
        # 3. Difficult chapters & additional_practice_needed boost weight
        weights: Dict[str, float] = {}
        weak_lower = {s.lower() for s in req.weak_subjects}
        strong_lower = {s.lower() for s in req.strong_subjects}
        gaps_text = " ".join(unresolved_gaps).lower()

        for es in exam_subjects:
            sub = es.subject_name
            sub_l = sub.lower()
            w = 1.3
            if es.subject_difficulty == "Difficult" or sub_l in weak_lower or any(w_sub in sub_l for w_sub in weak_lower):
                w = 2.3
                if sub not in req.weak_subjects:
                    req.weak_subjects.append(sub)
            elif es.subject_difficulty == "Easy" or sub_l in strong_lower or any(s_sub in sub_l for s_sub in strong_lower):
                w = 0.95
            # Urgency boost for sooner exams
            days_rem = subject_days_remaining.get(sub, 30)
            urgency_boost = round(max(0.1, min(1.5, 14.0 / max(1, days_rem))), 2)
            w += urgency_boost
            # Difficult chapters boost
            diff_ch_count = sum(1 for c in es.chapters if c.difficulty == "Difficult" or c.additional_practice_needed)
            w += min(0.8, diff_ch_count * 0.15)
            if sub_l in gaps_text or ("math" in sub_l and "fraction" in gaps_text):
                w += 0.3
            weights[sub] = round(w, 2)

        total_weight = sum(weights.values()) or 1.0
        weekly_total_study_hours = round(req.daily_study_hours * 7, 2)

        subject_hours_per_week: Dict[str, float] = {}
        subject_percentages: Dict[str, float] = {}
        for sub, w in weights.items():
            pct = round((w / total_weight) * 100.0, 1)
            hrs = round((w / total_weight) * weekly_total_study_hours, 2)
            subject_percentages[sub] = pct
            subject_hours_per_week[sub] = hrs

        # Determine start hour from preferred_study_time
        start_hour = 18
        if "Morning" in req.preferred_study_time:
            start_hour = 6
        elif "Afternoon" in req.preferred_study_time:
            start_hour = 15

        total_daily_study_minutes = int(round(req.daily_study_hours * 60))
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Preserve completed tasks if regenerating an existing plan
        preserved_completed_by_date: Dict[str, List[StudyTaskItem]] = {}
        if req.preserve_completed_tasks and existing_plan:
            seen_ids = set()
            all_prev_tasks: List[StudyTaskItem] = list(existing_plan.complete_exam_schedule)
            for dt_list in existing_plan.weekly_timetable.values():
                all_prev_tasks.extend(dt_list)
            all_prev_tasks.extend(existing_plan.daily_timetable)
            for t in all_prev_tasks:
                if t.completed and t.task_id not in seen_ids and t.session_type != "Break":
                    seen_ids.add(t.task_id)
                    preserved_completed_by_date.setdefault(t.date_iso, []).append(t)

        # Build prioritized chapter queue per subject (Incomplete chapters first, Difficult chapters repeated/given extra slots)
        subject_chapter_queue: Dict[str, List[ExamChapterEntry]] = {}
        for es in exam_subjects:
            active_chs = [c for c in es.chapters if c.completion_status != "Completed"]
            if not active_chs:
                active_chs = list(es.chapters)
            # Sort so Difficult / In Progress / additional_practice_needed come first
            active_chs_sorted = sorted(
                active_chs,
                key=lambda c: (
                    0 if c.difficulty == "Difficult" else (1 if c.difficulty == "Medium" else 2),
                    0 if c.additional_practice_needed else 1,
                    0 if c.completion_status == "In Progress" else 1,
                ),
            )
            expanded_queue: List[ExamChapterEntry] = []
            for ch in active_chs_sorted:
                expanded_queue.append(ch)
                if ch.difficulty == "Difficult" or ch.additional_practice_needed:
                    expanded_queue.append(ch)  # Extra preparation time for difficult chapters
            subject_chapter_queue[es.subject_name] = expanded_queue or [
                ExamChapterEntry(chapter_name="Chapter 1", difficulty="Medium")
            ]

        subject_entry_map = {es.subject_name: es for es in exam_subjects}
        subject_cursor_idx: Dict[str, int] = {es.subject_name: 0 for es in exam_subjects}

        # Generate Complete Exam Schedule across the preparation horizon (up to 30 days or until last exam)
        horizon_days = max(7, min(45, days_until_exam + 1))
        complete_exam_schedule: List[StudyTaskItem] = []
        weekly_timetable: Dict[str, List[StudyTaskItem]] = {d: [] for d in days_of_week}

        for day_offset in range(horizon_days):
            slot_dt = today_date_only + timedelta(days=day_offset)
            day_date = slot_dt.strftime("%Y-%m-%d")
            day_name = days_of_week[day_offset % 7]

            # Filter eligible subjects whose exam is ON or AFTER slot_dt (NEVER schedule after a subject's exam!)
            eligible_subjects = [
                es.subject_name
                for es in exam_subjects
                if subject_exam_dt_map.get(es.subject_name, slot_dt) >= slot_dt
            ]
            if not eligible_subjects:
                continue

            # Sort eligible subjects for this day:
            # 1. If an exam is tomorrow or in 2 days -> highest priority pre-exam revision!
            # 2. Otherwise sort by earliest exam date + weight
            def day_subject_priority(sub_name: str):
                ex_dt = subject_exam_dt_map[sub_name]
                d_left = (ex_dt - slot_dt).days
                imminent = 0 if d_left <= 2 else 1
                return (imminent, d_left, -weights.get(sub_name, 1.0))

            ordered_day_subjects = sorted(eligible_subjects, key=day_subject_priority)

            remaining_study_mins = total_daily_study_minutes
            cursor_mins = start_hour * 60
            day_tasks: List[StudyTaskItem] = []
            slot_counter = 0

            # First place any preserved completed tasks for this date without overlap
            for comp_task in preserved_completed_by_date.get(day_date, []):
                block_mins = min(comp_task.duration_minutes, remaining_study_mins) if remaining_study_mins > 0 else comp_task.duration_minutes
                s_hr, s_mn = divmod(cursor_mins, 60)
                e_hr, e_mn = divmod(cursor_mins + block_mins, 60)
                comp_copy = comp_task.model_copy(
                    update={
                        "time_slot": f"{s_hr:02d}:{s_mn:02d} - {e_hr:02d}:{e_mn:02d}",
                        "date_iso": day_date,
                        "day_label": day_name,
                    }
                )
                day_tasks.append(comp_copy)
                cursor_mins += block_mins
                remaining_study_mins = max(0, remaining_study_mins - block_mins)
                slot_counter += 1
                if remaining_study_mins > 0:
                    bs_hr, bs_mn = divmod(cursor_mins, 60)
                    be_hr, be_mn = divmod(cursor_mins + 10, 60)
                    day_tasks.append(
                        StudyTaskItem(
                            task_id=f"break_{day_date}_{slot_counter}_{uuid.uuid4().hex[:4]}",
                            day_label=day_name,
                            date_iso=day_date,
                            time_slot=f"{bs_hr:02d}:{bs_mn:02d} - {be_hr:02d}:{be_mn:02d}",
                            subject="Mindful Rest & Hydration Break",
                            chapter="Stretch, hydrate & rest eyes",
                            session_type="Break",
                            duration_minutes=10,
                            completed=False,
                            missed=False,
                            priority_reason="Cognitive recovery between focused study blocks",
                        )
                    )
                    cursor_mins += 10

            while remaining_study_mins > 0 and ordered_day_subjects:
                sub = ordered_day_subjects[(day_offset + slot_counter) % len(ordered_day_subjects)]
                es_obj = subject_entry_map[sub]
                ex_dt = subject_exam_dt_map[sub]
                d_left_to_sub_exam = (ex_dt - slot_dt).days

                ch_queue = subject_chapter_queue[sub]
                ch_entry = ch_queue[subject_cursor_idx[sub] % len(ch_queue)]
                subject_cursor_idx[sub] += 1

                # Difficult chapters get 45-50 mins, standard get 40-45 mins, capped by remaining_study_mins
                preferred_block = 50 if ch_entry.difficulty == "Difficult" else 45
                block_mins = min(preferred_block, remaining_study_mins)
                if remaining_study_mins - block_mins < 15 and remaining_study_mins <= 60:
                    block_mins = remaining_study_mins

                s_hr, s_mn = divmod(cursor_mins, 60)
                e_hr, e_mn = divmod(cursor_mins + block_mins, 60)
                time_slot_str = f"{s_hr:02d}:{s_mn:02d} - {e_hr:02d}:{e_mn:02d}"

                if d_left_to_sub_exam <= 1:
                    session_type = "Revision"
                elif d_left_to_sub_exam == 2 or (day_name == "Sunday" and slot_counter == 0):
                    session_type = "Mock Exam"
                elif ch_entry.additional_practice_needed or slot_counter % 2 == 1:
                    session_type = "Practice"
                elif day_name == "Saturday":
                    session_type = "Revision"
                else:
                    session_type = "Concept Study"

                is_weak = sub in req.weak_subjects or es_obj.subject_difficulty == "Difficult"
                priority_reason = (
                    f"Exam on {es_obj.exam_date} ({d_left_to_sub_exam}d left) • {ch_entry.difficulty} Chapter"
                    + (f" • {ch_entry.revision_requirements}" if ch_entry.revision_requirements else "")
                    + (" • High Priority Boost" if is_weak else "")
                )

                task_item = StudyTaskItem(
                    task_id=f"task_{day_date}_{slot_counter + 1}_{uuid.uuid4().hex[:5]}",
                    day_label=day_name,
                    date_iso=day_date,
                    time_slot=time_slot_str,
                    subject=sub,
                    chapter=ch_entry.chapter_name,
                    session_type=session_type,  # type: ignore
                    duration_minutes=block_mins,
                    completed=False,
                    missed=False,
                    postponed=False,
                    priority_reason=priority_reason,
                    subject_exam_date=es_obj.exam_date,
                    chapter_difficulty=ch_entry.difficulty,
                )
                day_tasks.append(task_item)

                cursor_mins += block_mins
                remaining_study_mins -= block_mins
                slot_counter += 1

                if remaining_study_mins > 0:
                    bs_hr, bs_mn = divmod(cursor_mins, 60)
                    be_hr, be_mn = divmod(cursor_mins + 10, 60)
                    day_tasks.append(
                        StudyTaskItem(
                            task_id=f"break_{day_date}_{slot_counter}_{uuid.uuid4().hex[:5]}",
                            day_label=day_name,
                            date_iso=day_date,
                            time_slot=f"{bs_hr:02d}:{bs_mn:02d} - {be_hr:02d}:{be_mn:02d}",
                            subject="Mindful Rest & Hydration Break",
                            chapter="Stretch, hydrate & rest eyes",
                            session_type="Break",
                            duration_minutes=10,
                            completed=False,
                            missed=False,
                            priority_reason="Cognitive recovery between focused study blocks",
                        )
                    )
                    cursor_mins += 10

            complete_exam_schedule.extend(day_tasks)
            if day_offset < 7:
                weekly_timetable[day_name] = day_tasks

        # Ensure every day of weekly_timetable has tasks if horizon had < 7 eligible days
        first_non_empty = next((tasks for tasks in weekly_timetable.values() if tasks), [])
        for d_name in days_of_week:
            if not weekly_timetable[d_name] and first_non_empty:
                weekly_timetable[d_name] = first_non_empty

        # Build Chapter Completion Targets respecting each subject's individual exam date
        chapter_targets: List[Dict[str, str]] = []
        for es in sorted(exam_subjects, key=lambda x: x.exam_date):
            sub_days = max(1, subject_days_remaining.get(es.subject_name, days_until_exam))
            total_sub_ch = max(1, len(es.chapters))
            for c_idx, ch_obj in enumerate(es.chapters):
                # Target completion is strictly before the subject's exam date
                offset_d = max(0, min(sub_days - 1, int(((c_idx + 1) / total_sub_ch) * max(1, sub_days - 1))))
                target_dt = (today_date_only + timedelta(days=offset_d)).strftime("%Y-%m-%d")
                if target_dt > es.exam_date[:10]:
                    target_dt = es.exam_date[:10]
                chapter_targets.append(
                    {
                        "subject": es.subject_name,
                        "chapter": ch_obj.chapter_name,
                        "chapter_id": ch_obj.chapter_id,
                        "difficulty": ch_obj.difficulty,
                        "completion_status": ch_obj.completion_status,
                        "additional_practice_needed": "Yes" if ch_obj.additional_practice_needed else "No",
                        "revision_requirements": ch_obj.revision_requirements,
                        "exam_date": es.exam_date[:10],
                        "target_completion_date": target_dt,
                        "priority": (
                            "Completed ✓"
                            if ch_obj.completion_status == "Completed"
                            else "High (Difficult / Practice Focus)"
                            if (ch_obj.difficulty == "Difficult" or ch_obj.additional_practice_needed or es.subject_name in req.weak_subjects)
                            else "Standard"
                        ),
                    }
                )

        ordered_subjects = sorted(subjects, key=lambda s: weights.get(s, 1.0), reverse=True)
        monthly_milestones = [
            {
                "week": "Phase 1 — Foundation & Difficult Chapter Focus",
                "focus": f"Prioritise {', '.join(req.weak_subjects) if req.weak_subjects else ordered_subjects[0]} difficult chapters and clear misconceptions before approaching exam dates.",
                "deliverable": "Complete Concept Study + Guided Practice for high-difficulty chapters.",
            },
            {
                "week": "Phase 2 — Application & Subject-Wise Targets",
                "focus": "Complete remaining student-entered chapters ordered by earliest subject exam dates.",
                "deliverable": "Finish 80% of chapter completion targets + Chapter Mock Tests.",
            },
            {
                "week": "Phase 3 — Pre-Exam Revision & Active Recall",
                "focus": "Intensive revision sessions and formula/concept recall prior to each individual subject exam.",
                "deliverable": "100% chapter coverage + Subject Mock Examinations.",
            },
            {
                "week": "Phase 4 — Exam-Day Readiness",
                "focus": "Final pre-exam revision blocks strictly scheduled before each subject's exam date.",
                "deliverable": f"Complete preparation across all {len(exam_subjects)} subject exam(s).",
            },
        ]

        mock_exam_dates = sorted(
            list(
                {
                    (
                        today_date_only
                        + timedelta(days=max(0, subject_days_remaining.get(es.subject_name, 7) - 2))
                    ).strftime("%Y-%m-%d")
                    for es in exam_subjects
                }
            )
        )[:5]
        if not mock_exam_dates:
            mock_exam_dates = [(today_date_only + timedelta(days=min(days_until_exam, 7))).strftime("%Y-%m-%d")]

        daily_tasks = weekly_timetable.get("Monday") or (complete_exam_schedule[:4] if complete_exam_schedule else [])

        return StudyPlanRecord(
            plan_id=existing_plan.plan_id if existing_plan else f"plan_{req.student_id}_{uuid.uuid4().hex[:6]}",
            student_id=req.student_id,
            exam_name=req.exam_name,
            exam_date=req.exam_date,
            days_until_exam=days_until_exam,
            daily_study_hours=req.daily_study_hours,
            preferred_study_time=req.preferred_study_time,
            weak_subjects=req.weak_subjects,
            strong_subjects=req.strong_subjects,
            academic_goal=req.academic_goal,
            exam_subjects=exam_subjects,
            subject_time_allocation_hours_per_week=subject_hours_per_week,
            subject_allocation_percentages=subject_percentages,
            chapter_completion_targets=chapter_targets,
            daily_timetable=daily_tasks,
            weekly_timetable=weekly_timetable,
            complete_exam_schedule=complete_exam_schedule,
            monthly_preparation_milestones=monthly_milestones,
            mock_exam_dates=mock_exam_dates,
            catch_up_schedule=existing_plan.catch_up_schedule if existing_plan else [],
            created_at=existing_plan.created_at if existing_plan else utc_now_iso(),
            updated_at=utc_now_iso(),
        )

    @staticmethod
    def build_catch_up_schedule(plan: StudyPlanRecord) -> StudyPlanRecord:
        """Generates catch-up sessions for any missed or incomplete high-priority tasks."""
        missed_tasks: List[StudyTaskItem] = []
        for day_tasks in plan.weekly_timetable.values():
            for t in day_tasks:
                if t.session_type != "Break" and (t.missed or not t.completed):
                    missed_tasks.append(t)

        catch_up_items: List[StudyTaskItem] = []
        now_dt = datetime.now(timezone.utc)
        for idx, src in enumerate(missed_tasks[:3]):
            catch_date = (now_dt + timedelta(days=idx + 1)).strftime("%Y-%m-%d")
            catch_up_items.append(
                StudyTaskItem(
                    task_id=f"catchup_{idx + 1}_{uuid.uuid4().hex[:5]}",
                    day_label=f"Catch-Up Slot #{idx + 1}",
                    date_iso=catch_date,
                    time_slot="19:30 - 20:00",
                    subject=src.subject,
                    chapter=src.chapter,
                    session_type="Catch-up",
                    duration_minutes=min(30, src.duration_minutes),
                    completed=False,
                    missed=False,
                    priority_reason=f"Adaptive recovery session for {src.subject} ({src.chapter})",
                )
            )
        plan.catch_up_schedule = catch_up_items
        plan.updated_at = utc_now_iso()
        return plan

    @staticmethod
    def calculate_daily_availability_and_plan(
        student_id: str,
        date_iso: str,
        weekday_short: str,
        timezone_name: str,
        wake_up_time: str,
        sleep_time: str,
        free_all_day: bool,
        activities: List[PersonalActivityItem],
        recurring_templates: List[PersonalActivityItem],
        study_plan: StudyPlanRecord,
        pending_homeworks: List[HomeworkItem],
        revision_cards: List[RevisionCardItem],
        unresolved_gaps: List[str],
        current_time_12h: Optional[str] = None,
        checkin_completed: bool = True,
    ) -> Tuple[DailyScheduleRecord, StudyPlanRecord]:
        """
        Daily Availability & Personal Schedule Integration Engine:
        1. Calculates exact available study windows outside student-entered commitments
           (School, Tuition, Chess, Drawing, Sports, Music, Travel, Family, Personal, Sleep/Rest).
        2. Generates the personalised daily study plan ONLY AFTER check-in is submitted.
        3. Preserves completed tasks, never duplicates tasks, and never schedules tasks in the past
           when the student updates their availability mid-day.
        """
        wake_mins = parse_time_to_minutes(wake_up_time)
        sleep_mins = parse_time_to_minutes(sleep_time)
        if sleep_mins <= wake_mins:
            sleep_mins = 21 * 60 + 30

        now_cutoff_mins = wake_mins
        if current_time_12h and current_time_12h.strip():
            try:
                parsed_now = parse_time_to_minutes(current_time_12h)
                now_cutoff_mins = max(wake_mins, parsed_now)
            except Exception:
                now_cutoff_mins = wake_mins

        active_activities = sorted(
            [a for a in activities if not a.is_cancelled_today],
            key=lambda x: (x.start_minutes, x.end_minutes),
        )

        # Preserve already-completed study tasks from today
        completed_tasks: List[StudyTaskItem] = []
        completed_intervals: List[Tuple[int, int]] = []
        completed_keys: set[Tuple[str, str]] = set()
        seen_completed_ids: set[str] = set()
        candidate_existing_tasks = list(study_plan.today_combined_timeline) + list(study_plan.daily_timetable)
        for existing_t in candidate_existing_tasks:
            if (
                existing_t.completed
                and existing_t.session_type not in ("Break", "Unavailable")
                and existing_t.task_id not in seen_completed_ids
                and (not existing_t.date_iso or existing_t.date_iso == date_iso)
            ):
                seen_completed_ids.add(existing_t.task_id)
                completed_tasks.append(existing_t)
                completed_keys.add((existing_t.subject.strip().lower(), existing_t.chapter.strip().lower()))
                try:
                    parts = [p.strip() for p in existing_t.time_slot.split("-")]
                    cs = parse_time_to_minutes(parts[0])
                    ce = parse_time_to_minutes(parts[1])
                    if ce > cs:
                        completed_intervals.append((cs, ce))
                except Exception:
                    pass

        # Build occupied intervals from active activities + already completed tasks
        raw_occupied: List[Tuple[int, int]] = [
            (a.start_minutes, a.end_minutes) for a in active_activities
        ] + completed_intervals
        raw_occupied.sort(key=lambda x: (x[0], x[1]))

        merged_occupied: List[Tuple[int, int]] = []
        for s_iv, e_iv in raw_occupied:
            if not merged_occupied or s_iv > merged_occupied[-1][1]:
                merged_occupied.append((s_iv, e_iv))
            else:
                merged_occupied[-1] = (merged_occupied[-1][0], max(merged_occupied[-1][1], e_iv))

        # Subtract occupied intervals from [now_cutoff_mins, sleep_mins]
        available_windows: List[AvailableTimeWindow] = []
        cursor = now_cutoff_mins
        win_idx = 1
        for occ_s, occ_e in merged_occupied:
            if occ_e <= cursor:
                continue
            if occ_s > cursor:
                gap_end = min(occ_s, sleep_mins)
                if gap_end - cursor >= 20:
                    period_lbl = (
                        "Morning Available Slot"
                        if cursor < 12 * 60
                        else ("Afternoon Available Slot" if cursor < 17 * 60 else "Evening Available Slot")
                    )
                    available_windows.append(
                        AvailableTimeWindow(
                            window_id=f"win_{date_iso}_{win_idx}",
                            start_time=format_minutes_to_12h(cursor),
                            end_time=format_minutes_to_12h(gap_end),
                            start_minutes=cursor,
                            end_minutes=gap_end,
                            duration_minutes=gap_end - cursor,
                            period_label=period_lbl,
                        )
                    )
                    win_idx += 1
            cursor = max(cursor, occ_e)
            if cursor >= sleep_mins:
                break

        if cursor < sleep_mins and (sleep_mins - cursor) >= 20:
            period_lbl = (
                "Morning Available Slot"
                if cursor < 12 * 60
                else ("Afternoon Available Slot" if cursor < 17 * 60 else "Evening Available Slot")
            )
            available_windows.append(
                AvailableTimeWindow(
                    window_id=f"win_{date_iso}_{win_idx}",
                    start_time=format_minutes_to_12h(cursor),
                    end_time=format_minutes_to_12h(sleep_mins),
                    start_minutes=cursor,
                    end_minutes=sleep_mins,
                    duration_minutes=sleep_mins - cursor,
                    period_label=period_lbl,
                )
            )

        total_unavail_mins = sum(a.duration_minutes for a in active_activities)
        # Available study minutes counts windows of at least 25 mins (excluding short 20-min transition breaks)
        total_avail_study_mins = sum(
            w.duration_minutes for w in available_windows if w.duration_minutes >= 25
        )
        total_avail_hours = round(total_avail_study_mins / 60.0, 2)
        unavailable_summary = [
            f"{a.activity_name}: {a.start_time} – {a.end_time}" for a in active_activities
        ]
        next_free_display = (
            f"{available_windows[0].start_time} – {available_windows[0].end_time}"
            if available_windows
            else "No remaining free study slots today"
        )

        if not checkin_completed:
            sched_record = DailyScheduleRecord(
                schedule_id=f"sched_{student_id}_{date_iso}",
                student_id=student_id,
                date_iso=date_iso,
                weekday_short=weekday_short,
                timezone_name=timezone_name,
                checkin_completed=False,
                free_all_day=free_all_day,
                wake_up_time=format_minutes_to_12h(wake_mins),
                sleep_time=format_minutes_to_12h(sleep_mins),
                activities=activities,
                recurring_templates=recurring_templates,
                unavailable_slots_summary=unavailable_summary,
                available_time_windows=available_windows,
                total_unavailable_minutes=total_unavail_mins,
                total_available_study_minutes=total_avail_study_mins,
                total_available_study_hours=total_avail_hours,
                next_free_slot_display=next_free_display,
                generated_daily_timeline=[],
                updated_at=utc_now_iso(),
            )
            return sched_record, study_plan

        # Build prioritised study candidates from Homework, Exam Subjects, Weak Areas, and Revision Cards
        candidates: List[Dict[str, object]] = []
        seen_candidate_keys = set(completed_keys)

        # 1. Urgent Pending Homeworks
        active_hws = [h for h in pending_homeworks if h.status != "completed"]
        active_hws.sort(key=lambda h: (h.due_date, 0 if h.priority == "High" else 1))
        for hw in active_hws[:2]:
            ch_label = f"{hw.title} ({hw.chapter})" if hw.chapter not in hw.title else hw.title
            key = (hw.subject.strip().lower(), ch_label.strip().lower())
            if key not in seen_candidate_keys:
                seen_candidate_keys.add(key)
                candidates.append(
                    {
                        "subject": hw.subject,
                        "chapter": ch_label,
                        "session_type": "Homework",
                        "preferred_mins": min(45, max(30, hw.estimated_minutes)),
                        "priority_reason": f"Pending Homework due {hw.due_date} ({hw.priority} Priority)",
                        "subject_exam_date": None,
                        "chapter_difficulty": "Difficult" if hw.priority == "High" else "Medium",
                    }
                )

        # 2. Exam Study Planner Subjects & Chapters (ordered by earliest exam date & difficulty)
        eligible_exam_subs = [
            es for es in study_plan.exam_subjects if es.exam_date[:10] >= date_iso[:10]
        ]
        eligible_exam_subs.sort(
            key=lambda es: (
                es.exam_date[:10],
                0 if es.subject_difficulty == "Difficult" or es.subject_name in study_plan.weak_subjects else 1,
            )
        )
        for es in eligible_exam_subs:
            inc_chapters = [c for c in es.chapters if c.completion_status != "Completed"]
            if not inc_chapters and es.chapters:
                inc_chapters = [es.chapters[0]]
            inc_chapters.sort(
                key=lambda c: (
                    0 if c.difficulty == "Difficult" else (1 if c.difficulty == "Medium" else 2),
                    0 if c.additional_practice_needed else 1,
                )
            )
            for ch in inc_chapters[:2]:
                key = (es.subject_name.strip().lower(), ch.chapter_name.strip().lower())
                if key not in seen_candidate_keys:
                    seen_candidate_keys.add(key)
                    s_type = (
                        "Revision"
                        if "revision" in ch.revision_requirements.lower() or es.subject_difficulty == "Easy"
                        else ("Practice" if ch.additional_practice_needed else "Concept Study")
                    )
                    candidates.append(
                        {
                            "subject": es.subject_name,
                            "chapter": ch.chapter_name,
                            "session_type": s_type,
                            "preferred_mins": 45 if ch.difficulty == "Difficult" else 30,
                            "priority_reason": f"Exam on {es.exam_date[:10]} • {ch.difficulty} Chapter • {ch.revision_requirements}",
                            "subject_exam_date": es.exam_date[:10],
                            "chapter_difficulty": ch.difficulty,
                        }
                    )

        # 3. Spaced Repetition Revision Cards
        for rc in revision_cards[:2]:
            ch_label = f"{rc.topic} (Revision)"
            key = (rc.subject.strip().lower(), ch_label.strip().lower())
            if key not in seen_candidate_keys:
                seen_candidate_keys.add(key)
                candidates.append(
                    {
                        "subject": rc.subject,
                        "chapter": ch_label,
                        "session_type": "Revision",
                        "preferred_mins": 30,
                        "priority_reason": f"Spaced-repetition active recall ({rc.source_tag})",
                        "subject_exam_date": None,
                        "chapter_difficulty": "Medium",
                    }
                )

        if not candidates:
            candidates.append(
                {
                    "subject": "Mathematics",
                    "chapter": "Core Concept Revision & Practice",
                    "session_type": "Revision",
                    "preferred_mins": 30,
                    "priority_reason": "Daily concept reinforcement",
                    "subject_exam_date": study_plan.exam_date[:10],
                    "chapter_difficulty": "Medium",
                }
            )

        # Target study minutes: respect both student's preferred study hours and actual available time
        already_done_mins = sum(t.duration_minutes for t in completed_tasks)
        max_daily_target_mins = int(round(max(1.5, study_plan.daily_study_hours + 1.0) * 60))
        remaining_target_mins = max(30, min(total_avail_study_mins, max_daily_target_mins - already_done_mins))

        new_study_and_breaks: List[StudyTaskItem] = []
        scheduled_study_mins = 0
        cand_idx = 0
        slot_seq = len(completed_tasks) + 1

        for win in available_windows:
            w_cursor = win.start_minutes
            w_end = win.end_minutes
            w_len = w_end - w_cursor

            preceded_by_class = any(a.end_minutes == win.start_minutes for a in active_activities)
            followed_by_class = any(a.start_minutes == win.end_minutes for a in active_activities)

            # If this is a short 20-30 min gap sandwiched between two unavailable classes (e.g. 5:00 PM - 5:30 PM or 6:30 PM - 7:00 PM),
            # schedule a 20-minute restorative Break instead of cramming a study session between classes!
            if 20 <= w_len < 30 or (w_len == 30 and preceded_by_class and followed_by_class):
                b_end = min(w_end, w_cursor + 20)
                new_study_and_breaks.append(
                    StudyTaskItem(
                        task_id=f"break_{date_iso}_{slot_seq}_{uuid.uuid4().hex[:4]}",
                        day_label="Today",
                        date_iso=date_iso,
                        time_slot=f"{format_minutes_to_12h(w_cursor)} - {format_minutes_to_12h(b_end)}",
                        subject="Break",
                        chapter="Rest, hydrate & recharge between classes",
                        session_type="Break",
                        duration_minutes=b_end - w_cursor,
                        completed=False,
                        missed=False,
                        postponed=False,
                        priority_reason="Restorative break between scheduled commitments",
                    )
                )
                slot_seq += 1
                continue

            # For windows >= 30 mins, place study sessions + reasonable breaks
            # Start at a natural hour if window is very wide (e.g. 7:00 AM if window starts at 6:30 AM),
            # or allow a 15-minute settle-in buffer right after an unavailable class ends (e.g. 8:15 PM after 8:00 PM class)
            if w_cursor == 390 and (w_end - 420) >= 60:
                w_cursor = 420  # 7:00 AM
            elif preceded_by_class and (w_end - (w_cursor + 15)) >= 30:
                w_cursor += 15

            sessions_in_this_window = 0
            while (w_end - w_cursor) >= 30 and scheduled_study_mins < remaining_target_mins:
                cand = candidates[cand_idx % len(candidates)]
                cand_idx += 1

                # Avoid duplicate subject+chapter if we cycled through all candidates
                subj_str = str(cand["subject"])
                chap_str = str(cand["chapter"])
                if any(
                    t.subject.lower() == subj_str.lower() and t.chapter.lower() == chap_str.lower()
                    for t in (completed_tasks + new_study_and_breaks)
                ):
                    if cand_idx >= len(candidates) * 2:
                        break
                    continue

                pref_dur = int(cand.get("preferred_mins", 30))  # type: ignore
                if w_cursor < 9 * 60:
                    block_dur = min(30, w_end - w_cursor)
                else:
                    block_dur = min(pref_dur, w_end - w_cursor)
                    if block_dur < 30:
                        block_dur = 30

                s_end = w_cursor + block_dur
                new_study_and_breaks.append(
                    StudyTaskItem(
                        task_id=f"task_{date_iso}_{slot_seq}_{uuid.uuid4().hex[:5]}",
                        day_label="Today",
                        date_iso=date_iso,
                        time_slot=f"{format_minutes_to_12h(w_cursor)} - {format_minutes_to_12h(s_end)}",
                        subject=subj_str,
                        chapter=chap_str,
                        session_type=str(cand["session_type"]),  # type: ignore
                        duration_minutes=block_dur,
                        completed=False,
                        missed=False,
                        postponed=False,
                        priority_reason=str(cand["priority_reason"]),
                        subject_exam_date=str(cand["subject_exam_date"]) if cand.get("subject_exam_date") else None,
                        chapter_difficulty=str(cand["chapter_difficulty"]),  # type: ignore
                    )
                )
                slot_seq += 1
                w_cursor = s_end
                scheduled_study_mins += block_dur
                sessions_in_this_window += 1

                # Add breakfast/break after morning study session or break between consecutive sessions
                if (w_end - w_cursor) >= 15 and scheduled_study_mins < remaining_target_mins:
                    if w_cursor <= 9 * 60 and (w_end - w_cursor) >= 30:
                        b_dur = 30
                        b_subj = "Breakfast and break"
                        b_chap = "Healthy breakfast & morning refreshment"
                    else:
                        b_dur = 15
                        b_subj = "Break"
                        b_chap = "Mindful stretch & hydration break"
                    b_end = w_cursor + b_dur
                    new_study_and_breaks.append(
                        StudyTaskItem(
                            task_id=f"break_{date_iso}_{slot_seq}_{uuid.uuid4().hex[:4]}",
                            day_label="Today",
                            date_iso=date_iso,
                            time_slot=f"{format_minutes_to_12h(w_cursor)} - {format_minutes_to_12h(b_end)}",
                            subject=b_subj,
                            chapter=b_chap,
                            session_type="Break",
                            duration_minutes=b_dur,
                            completed=False,
                            missed=False,
                            postponed=False,
                            priority_reason="Restorative break between study blocks",
                        )
                    )
                    slot_seq += 1
                    w_cursor = b_end

                    # If we had a morning session (e.g. 7:00 AM - 7:30 AM + 7:30 AM - 8:00 AM Breakfast)
                    # and there is a long daytime span before afternoon classes (e.g. until 4:00 PM),
                    # jump cursor to afternoon study slot (e.g. 3:00 PM = 900 mins) so sessions are well-balanced across the day!
                    if w_cursor <= 9 * 60 and w_end >= 15 * 60 + 45:
                        w_cursor = 15 * 60  # 3:00 PM
                    elif sessions_in_this_window >= 2 and (w_end - w_cursor) > 120:
                        w_cursor = max(w_cursor + 60, min(w_end - 45, 18 * 60))

        # Sort study + break tasks chronologically
        all_study_and_breaks = sorted(
            completed_tasks + new_study_and_breaks,
            key=lambda t: parse_time_to_minutes(t.time_slot.split("-")[0].strip()),
        )

        # Create Unavailable items for the combined daily timeline
        unavailable_items: List[StudyTaskItem] = [
            StudyTaskItem(
                task_id=f"unavail_{act.activity_id}",
                day_label="Today",
                date_iso=date_iso,
                time_slot=f"{act.start_time} - {act.end_time}",
                subject=f"{act.activity_name} (Unavailable)",
                chapter=f"{act.activity_name} (Unavailable)"
                + (f" • {act.location}" if act.location else "")
                + (f" ({act.notes})" if act.notes else ""),
                session_type="Unavailable",
                duration_minutes=act.duration_minutes,
                completed=False,
                missed=False,
                postponed=False,
                priority_reason=f"Personal Schedule ({act.category}) — Do not schedule study here",
            )
            for act in active_activities
        ]

        combined_timeline = sorted(
            all_study_and_breaks + unavailable_items,
            key=lambda t: parse_time_to_minutes(t.time_slot.split("-")[0].strip()),
        )

        study_plan.daily_timetable = all_study_and_breaks
        study_plan.today_combined_timeline = combined_timeline
        study_plan.daily_checkin_completed = True
        study_plan.daily_available_hours = total_avail_hours
        study_plan.updated_at = utc_now_iso()

        sched_record = DailyScheduleRecord(
            schedule_id=f"sched_{student_id}_{date_iso}",
            student_id=student_id,
            date_iso=date_iso,
            weekday_short=weekday_short,
            timezone_name=timezone_name,
            checkin_completed=True,
            free_all_day=free_all_day,
            wake_up_time=format_minutes_to_12h(wake_mins),
            sleep_time=format_minutes_to_12h(sleep_mins),
            activities=activities,
            recurring_templates=recurring_templates,
            unavailable_slots_summary=unavailable_summary,
            available_time_windows=available_windows,
            total_unavailable_minutes=total_unavail_mins,
            total_available_study_minutes=total_avail_study_mins,
            total_available_study_hours=total_avail_hours,
            next_free_slot_display=next_free_display,
            generated_daily_timeline=combined_timeline,
            updated_at=utc_now_iso(),
        )
        return sched_record, study_plan


class ExamPreparationEngine:
    """
    Section 1.E: Exam Preparation Centre.
    Generates curriculum-aligned MCQs, Short Answer, and Long Answer questions,
    automatically evaluates student submissions, provides detailed explanations for mistakes,
    and feeds weak topics into the Smart Revision Centre & Academic Progress Dashboard.
    """

    QUESTION_BANK: Dict[str, List[Dict[str, object]]] = {
        "Fractions & Decimals": [
            {
                "type": "MCQ",
                "q": "What is the value of 1/4 + 1/6 in its simplest form?",
                "options": ["2/10", "5/12", "2/24", "1/5"],
                "ans": "5/12",
                "concepts": ["5/12", "lcm", "12"],
                "marks": 2,
                "exp": "To add fractions with unlike denominators (4 and 6), never add denominators directly. Find LCM(4, 6) = 12. Convert: 1/4 = 3/12 and 1/6 = 2/12. Sum = (3 + 2)/12 = 5/12.",
            },
            {
                "type": "MCQ",
                "q": "Which of the following is equivalent to 0.75 expressed as a fraction in lowest terms?",
                "options": ["7/5", "3/4", "75/10", "1/4"],
                "ans": "3/4",
                "concepts": ["3/4", "75/100"],
                "marks": 2,
                "exp": "0.75 = 75/100. Dividing numerator and denominator by their HCF (25) gives 3/4.",
            },
            {
                "type": "SHORT_ANSWER",
                "q": "Find the LCM of denominators and compute: 2/3 - 1/6.",
                "options": [],
                "ans": "1/2",
                "concepts": ["1/2", "3/6", "6"],
                "marks": 3,
                "exp": "LCM of 3 and 6 is 6. Convert 2/3 to 4/6. Then 4/6 - 1/6 = 3/6, which simplifies to 1/2.",
            },
            {
                "type": "LONG_ANSWER",
                "q": "Aarav read 1/3 of a science book on Monday and 2/5 of the book on Tuesday. What total fraction of the book has he read, and what fraction is left?",
                "options": [],
                "ans": "11/15 read, 4/15 left",
                "concepts": ["11/15", "4/15", "15"],
                "marks": 5,
                "exp": "Step 1: LCM of 3 and 5 is 15. Step 2: Total read = 1/3 + 2/5 = 5/15 + 6/15 = 11/15. Step 3: Remaining fraction = 1 - 11/15 = 4/15.",
            },
        ],
        "Integers & Rational Numbers": [
            {
                "type": "MCQ",
                "q": "Evaluate: (-15) + 8 - (-7)",
                "options": ["-14", "0", "14", "-30"],
                "ans": "0",
                "concepts": ["0", "zero"],
                "marks": 2,
                "exp": "(-15) + 8 = -7. Subtracting a negative (- (-7)) is adding +7: -7 + 7 = 0.",
            },
            {
                "type": "SHORT_ANSWER",
                "q": "What is the product of (-12) × (-5)? Explain the sign rule used.",
                "options": [],
                "ans": "60",
                "concepts": ["60", "positive"],
                "marks": 3,
                "exp": "The product of two negative integers is always positive: (-12) × (-5) = +60.",
            },
        ],
        "Algebraic Expressions & Linear Equations": [
            {
                "type": "MCQ",
                "q": "Solve the linear equation: 3x - 7 = 14",
                "options": ["x = 7", "x = 21", "x = 7/3", "x = 5"],
                "ans": "x = 7",
                "concepts": ["7", "x=7", "x = 7"],
                "marks": 2,
                "exp": "Transpose -7 to the RHS: 3x = 14 + 7 = 21. Divide both sides by 3: x = 21/3 = 7.",
            },
            {
                "type": "SHORT_ANSWER",
                "q": "Simplify by combining like terms: 5x + 3y - 2x + 6y",
                "options": [],
                "ans": "3x + 9y",
                "concepts": ["3x", "9y"],
                "marks": 3,
                "exp": "Group like terms: (5x - 2x) + (3y + 6y) = 3x + 9y.",
            },
        ],
        "Acids, Bases & Salts": [
            {
                "type": "MCQ",
                "q": "What colour change happens when blue litmus paper is dipped into lemon juice (citric acid)?",
                "options": [
                    "Turns red",
                    "Remains blue",
                    "Turns green",
                    "Turns colourless",
                ],
                "ans": "Turns red",
                "concepts": ["red", "turns red"],
                "marks": 2,
                "exp": "Acids turn blue litmus paper red. Lemon juice contains citric acid, so blue litmus turns red.",
            },
            {
                "type": "SHORT_ANSWER",
                "q": "Define neutralisation reaction with a classic everyday or laboratory example.",
                "options": [],
                "ans": "Acid + Base -> Salt + Water + Heat (e.g. HCl + NaOH -> NaCl + H2O)",
                "concepts": ["salt", "water", "acid", "base", "nacl"],
                "marks": 3,
                "exp": "The reaction between an acid and a base to form salt and water with evolution of heat is called neutralisation (e.g., Hydrochloric acid + Sodium hydroxide -> Sodium chloride + Water).",
            },
            {
                "type": "LONG_ANSWER",
                "q": "Why do farmers add slaked lime (calcium hydroxide) or quicklime to soil, and how does antacid relieve indigestion?",
                "options": [],
                "ans": "Both use bases to neutralise excess acid",
                "concepts": ["neutral", "acid", "base", "magnesium", "soil"],
                "marks": 5,
                "exp": "1) Excess chemical fertilisers make soil acidic; basic slaked lime neutralises acidic soil. 2) Indigestion is caused by excess HCl in the stomach; mild bases like Milk of Magnesia neutralise the excess acid.",
            },
        ],
        "Heat, Motion & Time": [
            {
                "type": "MCQ",
                "q": "A car travels 120 km in 2 hours. What is its average speed?",
                "options": ["240 km/h", "60 km/h", "30 km/h", "122 km/h"],
                "ans": "60 km/h",
                "concepts": ["60", "60 km/h"],
                "marks": 2,
                "exp": "Speed = Total Distance / Total Time = 120 km / 2 h = 60 km/h.",
            },
            {
                "type": "SHORT_ANSWER",
                "q": "Distinguish between conduction and convection of heat.",
                "options": [],
                "ans": "Conduction transfers heat in solids without particle movement; convection transfers heat in fluids via actual particle movement.",
                "concepts": ["solid", "fluid", "liquid", "conduction", "convection"],
                "marks": 3,
                "exp": "Conduction occurs mainly in solids through direct molecular collisions without bulk movement of matter, whereas convection occurs in liquids and gases via bulk movement of warmer, less dense fluid rising.",
            },
        ],
        "Numbers 1 to 100": [
            {
                "type": "MCQ",
                "q": "Which number comes immediately after 49 when counting from 1 to 100?",
                "options": ["48", "50", "51", "40"],
                "ans": "50",
                "concepts": ["50", "fifty"],
                "marks": 2,
                "exp": "When counting forward by 1, the number after 49 (4 tens and 9 ones) is 50 (5 tens).",
            },
            {
                "type": "SHORT_ANSWER",
                "q": "How many tens and how many ones are in the number 37?",
                "options": [],
                "ans": "3 tens and 7 ones",
                "concepts": ["3", "7", "ten", "one"],
                "marks": 2,
                "exp": "In 37, the digit 3 is in the tens place (30) and 7 is in the ones place (7), so 37 = 3 tens + 7 ones.",
            },
        ],
        "Addition & Subtraction": [
            {
                "type": "MCQ",
                "q": "Ananya has 12 mangoes and her grandmother gives her 7 more mangoes. How many mangoes does Ananya have in total?",
                "options": ["18", "19", "20", "5"],
                "ans": "19",
                "concepts": ["19"],
                "marks": 2,
                "exp": "Add the ones: 2 + 7 = 9, and keep 1 ten: 12 + 7 = 19 mangoes.",
            },
        ],
        "Large Numbers & Place Value": [
            {
                "type": "MCQ",
                "q": "What is the place value of the digit 6 in the number 46,520?",
                "options": ["60", "600", "6,000", "60,000"],
                "ans": "6,000",
                "concepts": ["6000", "6,000", "thousand"],
                "marks": 2,
                "exp": "In 46,520, the digit 6 is in the thousands place, so its place value is 6 × 1,000 = 6,000.",
            },
            {
                "type": "SHORT_ANSWER",
                "q": "Write the expanded form of 35,408.",
                "options": [],
                "ans": "30000 + 5000 + 400 + 8",
                "concepts": ["30000", "5000", "400", "8"],
                "marks": 3,
                "exp": "35,408 = 30,000 + 5,000 + 400 + 0 + 8.",
            },
        ],
        "Multiplication & Division": [
            {
                "type": "MCQ",
                "q": "A school library has 24 shelves with 15 books on each shelf. How many books are there in total?",
                "options": ["360", "340", "300", "240"],
                "ans": "360",
                "concepts": ["360"],
                "marks": 2,
                "exp": "24 × 15 = 24 × (10 + 5) = 240 + 120 = 360 books.",
            },
        ],
        "Fractions Introduction": [
            {
                "type": "MCQ",
                "q": "If a chapati is cut into 4 equal parts and Diya eats 1 part, what fraction of the chapati is left?",
                "options": ["1/4", "2/4", "3/4", "4/4"],
                "ans": "3/4",
                "concepts": ["3/4"],
                "marks": 2,
                "exp": "Out of 4 equal parts, 1 part is eaten, leaving 4 - 1 = 3 parts out of 4, which is 3/4.",
            },
        ],
        "Real Numbers & Polynomials": [
            {
                "type": "MCQ",
                "q": "What is the HCF of 12 and 18 using prime factorisation?",
                "options": ["3", "6", "12", "36"],
                "ans": "6",
                "concepts": ["6"],
                "marks": 2,
                "exp": "12 = 2² × 3 and 18 = 2 × 3². Taking the product of the smallest powers of common prime factors: 2¹ × 3¹ = 6.",
            },
            {
                "type": "SHORT_ANSWER",
                "q": "Find the zeroes of the quadratic polynomial p(x) = x² - 5x + 6 and verify the sum of zeroes.",
                "options": [],
                "ans": "Zeroes are 2 and 3; sum = 2 + 3 = 5 = -(-5)/1",
                "concepts": ["2", "3", "5"],
                "marks": 3,
                "exp": "x² - 5x + 6 = (x - 2)(x - 3) = 0, so zeroes are x = 2 and x = 3. Sum of zeroes = 2 + 3 = 5, which equals -b/a = -(-5)/1 = 5.",
            },
        ],
        "Quadratic Equations & Arithmetic Progressions": [
            {
                "type": "MCQ",
                "q": "Find the 10th term of the Arithmetic Progression (AP): 2, 7, 12, ...",
                "options": ["42", "47", "52", "37"],
                "ans": "47",
                "concepts": ["47"],
                "marks": 2,
                "exp": "Here a = 2, common difference d = 7 - 2 = 5, and n = 10. Using a_n = a + (n - 1)d: a_10 = 2 + (10 - 1) × 5 = 2 + 45 = 47.",
            },
        ],
        "Mechanics & Rotational Motion": [
            {
                "type": "MCQ",
                "q": "What is the SI unit of Moment of Inertia (I = Σ m r²)?",
                "options": ["kg·m", "kg·m²", "N·m", "J·s"],
                "ans": "kg·m²",
                "concepts": ["kg", "m²", "kg·m²"],
                "marks": 2,
                "exp": "Moment of inertia I = m r², where mass m is in kg and perpendicular distance r is in metres (m), giving SI unit kg·m².",
            },
        ],
        "Calculus (Limits, Derivatives, Integrals)": [
            {
                "type": "MCQ",
                "q": "What is the derivative d/dx (x³ + 4x) with respect to x?",
                "options": ["3x² + 4", "x² + 4", "3x³ + 4", "x⁴/4 + 2x²"],
                "ans": "3x² + 4",
                "concepts": ["3x²", "4", "3x^2 + 4"],
                "marks": 2,
                "exp": "Using the power rule d/dx(x^n) = n x^(n-1): d/dx(x³) = 3x² and d/dx(4x) = 4, so the derivative is 3x² + 4.",
            },
        ],
    }

    @classmethod
    def generate_mock_exam(
        cls,
        req: ExamGenerateRequest,
        grade: int,
        board: str,
    ) -> MockExamRecord:
        chapters = req.chapters or (
            ["Fractions & Decimals", "Integers & Rational Numbers"]
            if "Math" in req.subject
            else ["Acids, Bases & Salts", "Heat, Motion & Time"]
        )

        candidate_pool: List[tuple[str, Dict[str, object]]] = []
        for ch in chapters:
            bank_items = cls.QUESTION_BANK.get(ch)
            if bank_items:
                for item in bank_items:
                    candidate_pool.append((ch, item))
            else:
                # Generate structured curriculum-aligned questions for any selected curriculum chapter
                candidate_pool.append(
                    (
                        ch,
                        {
                            "type": "MCQ",
                            "q": f"[{ch}] Which core principle is fundamental when solving problems in {ch} (Grade {grade} {board})?",
                            "options": [
                                f"Apply step-by-step conservation and definition rules of {ch}",
                                "Guess the final number without writing intermediate steps",
                                "Ignore units and sign conventions",
                                "Skip prerequisite verification",
                            ],
                            "ans": f"Apply step-by-step conservation and definition rules of {ch}",
                            "concepts": ["apply", "step", ch.lower().split()[0]],
                            "marks": 2,
                            "exp": f"In {ch}, systematic application of definitions, units, and step-by-step verification prevents conceptual errors.",
                        },
                    )
                )
                candidate_pool.append(
                    (
                        ch,
                        {
                            "type": "SHORT_ANSWER",
                            "q": f"[{ch}] State the key formula or core concept of {ch} and give one practical example.",
                            "options": [],
                            "ans": f"Core principle and example of {ch}",
                            "concepts": [ch.lower().split()[0], "example"],
                            "marks": 3,
                            "exp": f"A complete short answer defines {ch} clearly and connects it to a real-world or textbook application.",
                        },
                    )
                )

        # Ensure we have up to req.question_count questions
        selected = candidate_pool[: req.question_count]
        questions: List[ExamQuestionItem] = []
        total_marks = 0
        for idx, (ch, item) in enumerate(selected):
            marks = int(item.get("marks", 2))
            total_marks += marks
            questions.append(
                ExamQuestionItem(
                    question_id=f"q_{idx + 1}_{uuid.uuid4().hex[:4]}",
                    question_number=idx + 1,
                    question_type=str(item["type"]),  # type: ignore
                    subject=req.subject,
                    chapter=ch,
                    question_text=str(item["q"]),
                    options=list(item.get("options", [])),  # type: ignore
                    correct_answer=str(item["ans"]),
                    key_concepts_required=list(item.get("concepts", [])),  # type: ignore
                    marks=marks,
                    detailed_explanation=str(item["exp"]),
                )
            )

        return MockExamRecord(
            exam_id=f"exam_{req.student_id}_{uuid.uuid4().hex[:6]}",
            student_id=req.student_id,
            grade=grade,
            school_board=board,
            exam_mode=req.exam_mode,
            title=f"{req.exam_mode}: {req.subject} ({', '.join(chapters[:2])})",
            subject=req.subject,
            chapters=chapters,
            duration_minutes=req.duration_minutes,
            total_marks=total_marks,
            questions=questions,
            status="GENERATED",
            created_at=utc_now_iso(),
        )

    @classmethod
    def evaluate_exam_submission(
        cls,
        exam: MockExamRecord,
        sub: ExamSubmissionRequest,
    ) -> MockExamRecord:
        evaluations: List[ExamQuestionEvaluation] = []
        total_awarded = 0.0
        weak_topics: List[str] = []

        for q in exam.questions:
            raw_ans = (sub.answers.get(q.question_id) or "").strip()
            ans_lower = raw_ans.lower()
            correct_lower = q.correct_answer.lower()

            is_correct = False
            marks_awarded = 0.0

            if q.question_type == "MCQ":
                is_correct = ans_lower == correct_lower or (
                    bool(ans_lower) and ans_lower in correct_lower
                )
                marks_awarded = float(q.marks) if is_correct else 0.0
            else:
                # Short / Long answer conceptual keyword & numerical evaluation
                matched_concepts = [
                    c for c in q.key_concepts_required if c.lower() in ans_lower
                ]
                if ans_lower == correct_lower or len(matched_concepts) >= max(
                    1, len(q.key_concepts_required) - 1
                ):
                    is_correct = True
                    marks_awarded = float(q.marks)
                elif len(matched_concepts) >= 1:
                    is_correct = False
                    marks_awarded = round(q.marks * 0.5, 1)
                else:
                    is_correct = False
                    marks_awarded = 0.0

            total_awarded += marks_awarded
            if not is_correct and q.chapter not in weak_topics:
                weak_topics.append(q.chapter)

            feedback = (
                f"✓ Correct! {q.detailed_explanation}"
                if is_correct
                else f"✗ Needs Revision. Expected '{q.correct_answer}'. Explanation: {q.detailed_explanation}"
            )

            evaluations.append(
                ExamQuestionEvaluation(
                    question_id=q.question_id,
                    question_number=q.question_number,
                    question_type=q.question_type,
                    chapter=q.chapter,
                    student_answer=raw_ans or "(No answer submitted)",
                    correct_answer=q.correct_answer,
                    is_correct=is_correct,
                    marks_awarded=marks_awarded,
                    max_marks=q.marks,
                    feedback_and_explanation=feedback,
                )
            )

        pct = round((total_awarded / max(1, exam.total_marks)) * 100.0, 1)
        recommendations: List[str] = []
        if weak_topics:
            recommendations.append(
                f"Priority Revision Scheduled: Flashcards and spaced-repetition quizzes have been automatically added for {', '.join(weak_topics)}."
            )
            recommendations.append(
                f"Open AI Learning Buddy to walk through step-by-step worked examples in {weak_topics[0]}."
            )
        else:
            recommendations.append(
                f"Excellent mastery ({pct}%)! Proceed to higher-order application problems in {exam.subject}."
            )

        exam.status = "COMPLETED"
        exam.score_awarded = total_awarded
        exam.score_percentage = pct
        exam.question_evaluations = evaluations
        exam.weak_topics_detected = weak_topics
        exam.improvement_recommendations = recommendations
        exam.submitted_at = utc_now_iso()
        return exam


class SmartRevisionEngine:
    """
    Section 1.F: Smart Revision Centre.
    - Automatic flashcard generation & active recall quizzes.
    - Spaced repetition scheduling (SM-2 inspired interval progression: 1d -> 3d -> 7d -> 14d -> 30d).
    - Weak-topic and forgotten-topic detection from learning history & mock exam mistakes.
    """

    TOPIC_FLASHCARDS: Dict[str, Dict[str, object]] = {
        "Fractions & Decimals": {
            "front": "How do you add or subtract two fractions with unlike denominators (e.g., 1/4 + 1/6)?",
            "back": "1. Find the Least Common Multiple (LCM) of the denominators (LCM of 4 and 6 is 12).\n2. Convert each fraction to an equivalent fraction with denominator 12 (3/12 and 2/12).\n3. Add only the numerators (3+2 = 5) and keep the common denominator (5/12).",
            "quiz_q": "What is the first step when adding 2/5 and 1/3?",
            "quiz_opts": [
                "Find the LCM of denominators 5 and 3 (which is 15)",
                "Add denominators 5 + 3 = 8",
                "Multiply numerators 2 × 1",
                "Subtract 3 from 5",
            ],
            "quiz_ans": "Find the LCM of denominators 5 and 3 (which is 15)",
        },
        "Algebraic Expressions & Linear Equations": {
            "front": "What happens to the sign of a term when you transpose it across the '=' sign in a linear equation?",
            "back": "Addition (+) becomes Subtraction (-), Subtraction (-) becomes Addition (+), Multiplication (×) becomes Division (÷), and Division (÷) becomes Multiplication (×).",
            "quiz_q": "When solving 2x - 9 = 11, what is the correct first step?",
            "quiz_opts": [
                "Transpose -9 to RHS to get 2x = 11 + 9",
                "Transpose -9 to RHS to get 2x = 11 - 9",
                "Divide 9 by 2",
                "Subtract 2x from 11",
            ],
            "quiz_ans": "Transpose -9 to RHS to get 2x = 11 + 9",
        },
        "Acids, Bases & Salts": {
            "front": "Memory Aid: How do Litmus and Turmeric indicators react with Acids and Bases?",
            "back": "• Blue Litmus -> turns RED in Acid (remember: BAR = Blue Acid Red).\n• Red Litmus -> turns BLUE in Base.\n• Turmeric (yellow) -> turns REDDISH-BROWN in Base (soap), remains yellow in Acid.",
            "quiz_q": "A drop of soap solution (basic) is placed on a yellow turmeric stain. What colour does it turn?",
            "quiz_opts": ["Reddish-brown", "Bright blue", "Colourless", "Green"],
            "quiz_ans": "Reddish-brown",
        },
        "Heat, Motion & Time": {
            "front": "What are the three modes of heat transfer and the medium each requires?",
            "back": "1. Conduction: Solids (direct contact, no bulk particle movement).\n2. Convection: Liquids & Gases (actual movement of heated fluid particles).\n3. Radiation: Requires NO medium (can travel through vacuum, like sunlight).",
            "quiz_q": "How does heat from the Sun reach the Earth through the vacuum of space?",
            "quiz_opts": ["Radiation", "Conduction", "Convection", "Evaporation"],
            "quiz_ans": "Radiation",
        },
    }

    @classmethod
    def create_revision_card(
        cls,
        student_id: str,
        subject: str,
        topic: str,
        source_tag: str = "Weak Topic",
    ) -> RevisionCardItem:
        template = cls.TOPIC_FLASHCARDS.get(topic)
        if not template:
            # Dynamic match by substring or curriculum fallback
            for k, v in cls.TOPIC_FLASHCARDS.items():
                if k.lower() in topic.lower() or topic.lower() in k.lower():
                    template = v
                    break

        if not template:
            template = {
                "front": f"Key Concept Recall: What is the core rule and common mistake to avoid in '{topic}' ({subject})?",
                "back": f"Core Rule for {topic}: Always write down given quantities with units, state the governing formula/definition, and verify each intermediate step before concluding.",
                "quiz_q": f"During active recall of {topic}, what ensures conceptual retention?",
                "quiz_opts": [
                    "Explaining the 'why' behind each step and testing with an example",
                    "Memorising answers without understanding steps",
                    "Skipping diagrams and units",
                    "Avoiding practice problems",
                ],
                "quiz_ans": "Explaining the 'why' behind each step and testing with an example",
            }

        return RevisionCardItem(
            revision_id=f"rev_{uuid.uuid4().hex[:7]}",
            student_id=student_id,
            subject=subject,
            topic=topic,
            front_prompt=str(template["front"]),
            back_explanation=str(template["back"]),
            active_recall_question=str(template["quiz_q"]),
            active_recall_options=list(template["quiz_opts"]),  # type: ignore
            active_recall_answer=str(template["quiz_ans"]),
            source_tag=source_tag,  # type: ignore
            interval_days=1,
            repetition_count=0,
            next_review_date=today_iso(),
            completed_today=False,
            mastery_level="Needs Immediate Review",
        )

    @staticmethod
    def apply_spaced_repetition_review(
        card: RevisionCardItem,
        recall_quality: str,
    ) -> RevisionCardItem:
        now_dt = datetime.now(timezone.utc)
        card.last_reviewed_at = now_dt.isoformat()

        if recall_quality == "Forgot":
            card.interval_days = 1
            card.repetition_count = 0
            card.completed_today = False
            card.mastery_level = "Needs Immediate Review"
        elif recall_quality == "Hard":
            card.interval_days = max(1, card.interval_days + 1)
            card.repetition_count += 1
            card.completed_today = True
            card.mastery_level = "Reviewing"
        elif recall_quality == "Good":
            progression = {1: 3, 2: 3, 3: 7, 7: 14}
            card.interval_days = progression.get(card.interval_days, min(30, card.interval_days * 2))
            card.repetition_count += 1
            card.completed_today = True
            card.mastery_level = "Retained" if card.interval_days >= 7 else "Reviewing"
        else:  # Easy
            card.interval_days = min(30, max(4, card.interval_days * 3))
            card.repetition_count += 1
            card.completed_today = True
            card.mastery_level = "Retained"

        card.next_review_date = (now_dt + timedelta(days=card.interval_days)).strftime("%Y-%m-%d")
        return card


class ProjectCreativityLabEngine:
    """
    Section 1.I: School Project & Creativity Lab.
    Guides students to build and understand curriculum projects step by step
    rather than doing the project for them.
    """

    @staticmethod
    def generate_guided_project(
        req: ProjectGenerateRequest,
        grade: int,
    ) -> ProjectRecord:
        theme = req.chapter_or_theme
        if "Acid" in theme or "Sci" in req.subject:
            title = f"Natural pH Detective: Testing Household Acids & Bases with Homemade Turmeric & Hibiscus Indicators"
            objective = (
                f"Design and conduct a safe Grade {grade} investigation to classify 6 household liquids "
                f"using natural plant indicators and explain the chemical colour transitions."
            )
            materials = [
                "Turmeric powder + filter paper strips",
                "China rose (Hibiscus) petals steeped in warm water",
                "Test samples: Lemon juice, Vinegar, Soap water, Baking soda solution, Sugar water, Curd",
                "Observation table notebook & transparent droppers",
            ]
        elif "Math" in req.subject or "Fraction" in theme:
            title = f"Fraction & Ratio Architect: Designing a Scale Floor-Plan & Recipe Multiplier"
            objective = (
                f"Apply Grade {grade} {theme} to design a real-world scale room layout and scale an Indian festive recipe "
                f"from 4 servings to 10 servings using exact fraction operations."
            )
            materials = [
                "Grid / graph paper and ruler",
                "Coloured markers to represent fractional area tiles",
                "A family recipe with fractional cup/spoon measurements",
                "Calculation verification sheet",
            ]
        else:
            title = f"{req.project_type}: Exploring {theme} in Our Local Community"
            objective = (
                f"Investigate how concepts from {theme} ({req.subject}) operate in everyday life and present "
                f"evidence-backed findings crafted in your own words."
            )
            materials = [
                "Chart paper or slide deck template",
                "Observation logbook",
                "Textbook reference notes",
                "Diagram sketching tools",
            ]

        milestones = [
            {
                "step": 1,
                "title": "Formulate Your Question & Hypothesis",
                "guidance": f"Before starting, write in your own words what you predict will happen and why based on {theme}.",
                "completed": False,
            },
            {
                "step": 2,
                "title": "Gather Safe Materials & Set Up Observation Table",
                "guidance": "Prepare your materials and draw a clean table to record raw observations honestly (even if an experiment surprises you!).",
                "completed": False,
            },
            {
                "step": 3,
                "title": "Execute Hands-On Trial & Record Evidence",
                "guidance": "Perform each test step by step. Measure carefully and note what changed.",
                "completed": False,
            },
            {
                "step": 4,
                "title": "Connect Observations to Curriculum Theory",
                "guidance": f"Explain why your results occurred using Grade {grade} {req.subject} concepts.",
                "completed": False,
            },
            {
                "step": 5,
                "title": "Prepare Presentation & Self-Reflection",
                "guidance": "Organise your 5-slide presentation outline and practice explaining your project without reading from a script.",
                "completed": False,
            },
        ]

        research_prompts = [
            f"Why does {theme} matter in everyday Indian households, agriculture, or engineering?",
            "What is one variable you will keep constant (control) so your test is fair?",
            "If a classmate asks 'What was your biggest surprise during this project?', what evidence will you point to?",
        ]

        slide_outline = [
            "Slide 1: Project Title, My Curiosity Question & Hypothesis",
            "Slide 2: Core Scientific / Mathematical Principle (Diagram in your own hand)",
            "Slide 3: Materials Used & Step-by-Step Procedure",
            "Slide 4: My Real Observation Table & Data Analysis",
            "Slide 5: Conclusion, Real-World Impact in India & What I Learned",
        ]

        creativity_challenge = (
            f"🌟 Creativity Challenge (Socratic Prompt): Imagine you had to teach {theme} to a Grade {max(1, grade - 2)} "
            f"student using only items found in a kitchen or playground. What original analogy or mini-game would you invent?"
        )

        return ProjectRecord(
            project_id=f"proj_{req.student_id}_{uuid.uuid4().hex[:6]}",
            student_id=req.student_id,
            grade=grade,
            subject=req.subject,
            chapter_or_theme=theme,
            project_type=req.project_type,
            title=title,
            learning_objective=objective,
            materials_needed=materials,
            milestones=milestones,
            research_guidance_prompts=research_prompts,
            presentation_slide_outline=slide_outline,
            socratic_creativity_challenge=creativity_challenge,
            student_notes="",
            student_creativity_response="",
            progress_percentage=0,
            created_at=utc_now_iso(),
            updated_at=utc_now_iso(),
        )
