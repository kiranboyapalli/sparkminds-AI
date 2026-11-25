"""
EDUSPARK AI — Complete Exam Planner, Daily Reminders, Child Safety and Academic Tracking Upgrade
Comprehensive 20-Scenario Verification Suite (Section 10)
"""
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.core.repository import EduSparkRepository, repo

client = TestClient(app)
_TOKENS: dict[str, str] = {}


def _as_student(sid: str) -> None:
    client.cookies.clear()
    tok = _TOKENS.get(sid)
    if tok:
        client.cookies.set("sparkminds_access_token", tok)


def _parse_12h_to_minutes(time_str: str) -> int:
    s = time_str.strip().upper()
    parts = s.split()
    hm = parts[0].split(":")
    h = int(hm[0])
    m = int(hm[1]) if len(hm) > 1 else 0
    meridiem = parts[1] if len(parts) > 1 else "AM"
    if meridiem == "PM" and h != 12:
        h += 12
    elif meridiem == "AM" and h == 12:
        h = 0
    return h * 60 + m


def _parse_range_to_interval(time_slot: str):
    left, right = [x.strip() for x in time_slot.split("-")]
    return _parse_12h_to_minutes(left), _parse_12h_to_minutes(right)


def test_01_add_single_subject_in_exam_study_planner():
    """1. Adding 1 subject in the Exam Study Planner."""
    sid = "stu_test_upgrade_01"
    repo.students.pop(sid, None)
    repo.study_plans.pop(sid, None)
    repo.exam_marks.pop(sid, None)
    repo.reminder_preferences.pop(sid, None)
    reg1 = client.post(
        "/api/auth/register",
        json={"student_id": sid, "full_name": "Test One Subject", "age": 12, "grade": 7},
    )
    _TOKENS[sid] = reg1.json().get("session_token", "")
    exam_dt = (date.today() + timedelta(days=10)).isoformat()
    res = client.post(
        f"/api/students/{sid}/study-plan/subjects",
        json={
            "student_id": sid,
            "auto_regenerate_timetable": True,
            "subject": {
                "subject_name": "Mathematics",
                "number_of_chapters": 4,
                "exam_date": exam_dt,
                "exam_time": "9:30 AM - 12:30 PM",
                "maximum_marks": 100,
                "subject_difficulty": "Difficult",
                "student_confidence_level": "Need help",
            },
        },
    )
    assert res.status_code == 200
    plan = res.json()
    assert len(plan["exam_subjects"]) == 1
    sub = plan["exam_subjects"][0]
    assert sub["subject_name"] == "Mathematics"
    assert sub["number_of_chapters"] == 4
    assert len(sub["chapters"]) == 4
    # Must never invent syllabus chapters when not provided
    assert sub["chapters"][0]["chapter_name"] == "Chapter 1"


def test_02_add_five_subjects_with_different_chapter_counts_and_exam_dates():
    """2. Adding 5 subjects with different chapter counts and exam dates."""
    sid = "stu_test_upgrade_02"
    repo.students.pop(sid, None)
    repo.study_plans.pop(sid, None)
    repo.exam_marks.pop(sid, None)
    repo.reminder_preferences.pop(sid, None)
    reg2 = client.post(
        "/api/auth/register",
        json={"student_id": sid, "full_name": "Test Five Subjects", "age": 13, "grade": 8},
    )
    _TOKENS[sid] = reg2.json().get("session_token", "")
    base_dt = date.today()
    subjects_spec = [
        ("Mathematics", 12, (base_dt + timedelta(days=5)).isoformat(), "Difficult"),
        ("Science", 10, (base_dt + timedelta(days=8)).isoformat(), "Difficult"),
        ("English", 8, (base_dt + timedelta(days=11)).isoformat(), "Easy"),
        ("Social Studies", 9, (base_dt + timedelta(days=14)).isoformat(), "Medium"),
        ("Hindi", 6, (base_dt + timedelta(days=17)).isoformat(), "Easy"),
    ]
    for name, ch_count, ex_dt, diff in subjects_spec:
        res = client.post(
            f"/api/students/{sid}/study-plan/subjects",
            json={
                "student_id": sid,
                "auto_regenerate_timetable": True,
                "subject": {
                    "subject_name": name,
                    "number_of_chapters": ch_count,
                    "exam_date": ex_dt,
                    "subject_difficulty": diff,
                },
            },
        )
        assert res.status_code == 200

    plan = client.get(f"/api/students/{sid}/study-plan").json()
    assert len(plan["exam_subjects"]) == 5
    names = [s["subject_name"] for s in plan["exam_subjects"]]
    assert names == ["Mathematics", "Science", "English", "Social Studies", "Hindi"]


def test_03_add_new_subject_after_timetable_already_generated():
    """3. Adding a new subject after the timetable is already generated."""
    sid = "stu_test_upgrade_02"
    base_dt = date.today()
    res = client.post(
        f"/api/students/{sid}/study-plan/subjects",
        json={
            "student_id": sid,
            "auto_regenerate_timetable": True,
            "subject": {
                "subject_name": "Computer Science",
                "number_of_chapters": 5,
                "exam_date": (base_dt + timedelta(days=6)).isoformat(),
                "subject_difficulty": "Medium",
            },
        },
    )
    assert res.status_code == 200
    plan = res.json()
    assert len(plan["exam_subjects"]) == 6
    assert any(
        t["subject"] == "Computer Science"
        for t in plan["complete_exam_schedule"]
        if t["session_type"] != "Break"
    )


def test_04_edit_and_remove_subject():
    """4. Editing and removing a subject."""
    sid = "stu_test_upgrade_02"
    plan = client.get(f"/api/students/{sid}/study-plan").json()
    cs_sub = next(s for s in plan["exam_subjects"] if s["subject_name"] == "Computer Science")
    sub_id = cs_sub["subject_id"]

    # Edit Computer Science chapter count from 5 to 7
    edit_res = client.post(
        f"/api/students/{sid}/study-plan/subjects",
        json={
            "student_id": sid,
            "auto_regenerate_timetable": True,
            "subject": {
                "subject_id": sub_id,
                "subject_name": "Computer Science & AI",
                "number_of_chapters": 7,
                "exam_date": cs_sub["exam_date"],
                "subject_difficulty": "Difficult",
            },
        },
    )
    assert edit_res.status_code == 200
    updated_plan = edit_res.json()
    edited_sub = next(s for s in updated_plan["exam_subjects"] if s["subject_id"] == sub_id)
    assert edited_sub["subject_name"] == "Computer Science & AI"
    assert edited_sub["number_of_chapters"] == 7
    assert len(edited_sub["chapters"]) == 7

    # Remove Computer Science & AI
    del_res = client.delete(f"/api/students/{sid}/study-plan/subjects/{sub_id}")
    assert del_res.status_code == 200
    after_del = del_res.json()
    assert len(after_del["exam_subjects"]) == 5
    assert all(s["subject_id"] != sub_id for s in after_del["exam_subjects"])


def test_05_change_exam_dates_and_regenerate_schedule():
    """5. Changing exam dates and regenerating the schedule."""
    sid = "stu_test_upgrade_01"
    _as_student(sid)
    plan = client.get(f"/api/students/{sid}/study-plan").json()
    math_sub = plan["exam_subjects"][0]
    new_exam_date = (date.today() + timedelta(days=4)).isoformat()

    res = client.post(
        f"/api/students/{sid}/study-plan/subjects",
        json={
            "student_id": sid,
            "auto_regenerate_timetable": True,
            "subject": {
                "subject_id": math_sub["subject_id"],
                "subject_name": "Mathematics",
                "number_of_chapters": 4,
                "exam_date": new_exam_date,
                "subject_difficulty": "Difficult",
            },
        },
    )
    assert res.status_code == 200
    new_plan = res.json()
    assert new_plan["exam_subjects"][0]["exam_date"] == new_exam_date
    for task in new_plan["complete_exam_schedule"]:
        if task["subject"] == "Mathematics":
            assert task["date_iso"] <= new_exam_date


def test_06_change_chapter_names_and_completion_status():
    """6. Changing chapter names and completion status."""
    sid = "stu_test_upgrade_01"
    _as_student(sid)
    plan = client.get(f"/api/students/{sid}/study-plan").json()
    math_sub = plan["exam_subjects"][0]
    custom_chapters = [
        {
            "chapter_number": 1,
            "chapter_name": "Integers",
            "difficulty": "Easy",
            "completion_status": "Completed",
            "additional_practice_needed": False,
            "revision_requirements": "Quick formula check",
        },
        {
            "chapter_number": 2,
            "chapter_name": "Fractions and Decimals",
            "difficulty": "Difficult",
            "completion_status": "In Progress",
            "additional_practice_needed": True,
            "revision_requirements": "Practice LCM word problems",
        },
        {
            "chapter_number": 3,
            "chapter_name": "Simple Equations",
            "difficulty": "Medium",
            "completion_status": "Not Started",
            "additional_practice_needed": True,
            "revision_requirements": "Full chapter revision",
        },
        {
            "chapter_number": 4,
            "chapter_name": "Lines and Angles",
            "difficulty": "Medium",
            "completion_status": "Not Started",
            "additional_practice_needed": False,
            "revision_requirements": "Geometry diagrams",
        },
    ]
    res = client.post(
        f"/api/students/{sid}/study-plan/subjects",
        json={
            "student_id": sid,
            "auto_regenerate_timetable": True,
            "subject": {
                "subject_id": math_sub["subject_id"],
                "subject_name": "Mathematics",
                "number_of_chapters": 4,
                "exam_date": math_sub["exam_date"],
                "subject_difficulty": "Difficult",
                "chapters": custom_chapters,
            },
        },
    )
    assert res.status_code == 200
    updated = res.json()
    saved_chapters = updated["exam_subjects"][0]["chapters"]
    assert saved_chapters[0]["chapter_name"] == "Integers"
    assert saved_chapters[0]["completion_status"] == "Completed"
    assert saved_chapters[1]["chapter_name"] == "Fractions and Decimals"
    assert saved_chapters[1]["additional_practice_needed"] is True


def test_07_generate_combined_study_timetable_across_all_subjects():
    """7. Generating a combined study timetable across all subjects."""
    sid = "stu_test_upgrade_02"
    _as_student(sid)
    plan = client.get(f"/api/students/{sid}/study-plan").json()
    assert len(plan["daily_timetable"]) > 0
    assert len(plan["weekly_timetable"]) == 7
    assert len(plan["complete_exam_schedule"]) > 0
    scheduled_subjects = {
        t["subject"]
        for t in plan["complete_exam_schedule"]
        if t["session_type"] != "Break"
    }
    assert len(scheduled_subjects) >= 3


def test_08_ensure_no_overlapping_study_sessions():
    """8. Ensuring no overlapping study sessions are created."""
    sid = "stu_test_upgrade_02"
    _as_student(sid)
    plan = client.get(f"/api/students/{sid}/study-plan").json()
    by_date = {}
    for task in plan["complete_exam_schedule"]:
        by_date.setdefault(task["date_iso"], []).append(task)

    for dt_iso, tasks in by_date.items():
        intervals = [_parse_range_to_interval(t["time_slot"]) for t in tasks]
        intervals.sort(key=lambda x: x[0])
        for i in range(len(intervals) - 1):
            assert intervals[i][1] <= intervals[i + 1][0], (
                f"Overlapping sessions detected on {dt_iso}: {intervals[i]} vs {intervals[i+1]}"
            )


def test_09_ensure_no_study_sessions_scheduled_after_subject_exam_date():
    """9. Ensuring no study sessions are scheduled after a subject's exam date."""
    sid = "stu_test_upgrade_02"
    _as_student(sid)
    plan = client.get(f"/api/students/{sid}/study-plan").json()
    exam_dates_by_subject = {
        s["subject_name"]: s["exam_date"] for s in plan["exam_subjects"]
    }
    for task in plan["complete_exam_schedule"]:
        sub = task["subject"]
        if sub in exam_dates_by_subject:
            assert task["date_iso"] <= exam_dates_by_subject[sub], (
                f"Task for {sub} scheduled on {task['date_iso']} after exam date {exam_dates_by_subject[sub]}"
            )


def test_10_complete_and_postpone_study_tasks():
    """10. Completing and postponing study tasks."""
    sid = "stu_test_upgrade_02"
    _as_student(sid)
    plan = client.get(f"/api/students/{sid}/study-plan").json()
    study_tasks = [t for t in plan["daily_timetable"] if t["session_type"] != "Break"]
    first_task = study_tasks[0]
    second_task = study_tasks[1]

    # Mark first task completed
    res1 = client.patch(
        f"/api/students/{sid}/study-plan/tasks/{first_task['task_id']}",
        json={"completed": True, "missed": False, "postponed": False},
    )
    assert res1.status_code == 200
    p1 = res1.json()
    t1_updated = next(t for t in p1["daily_timetable"] if t["task_id"] == first_task["task_id"])
    assert t1_updated["completed"] is True

    # Postpone second task & edit chapter target
    res2 = client.patch(
        f"/api/students/{sid}/study-plan/tasks/{second_task['task_id']}",
        json={
            "completed": False,
            "missed": False,
            "postponed": True,
            "new_chapter": "Postponed Chapter Revision Target",
        },
    )
    assert res2.status_code == 200
    p2 = res2.json()
    t2_updated = next(t for t in p2["daily_timetable"] if t["task_id"] == second_task["task_id"])
    assert t2_updated["postponed"] is True
    assert t2_updated["chapter"] == "Postponed Chapter Revision Target"
    assert len(p2["catch_up_schedule"]) >= 1


def test_11_regenerate_timetable_while_preserving_completed_tasks():
    """11. Regenerating the timetable while preserving completed tasks."""
    sid = "stu_test_upgrade_02"
    _as_student(sid)
    before_plan = client.get(f"/api/students/{sid}/study-plan").json()
    completed_ids = {
        t["task_id"] for t in before_plan["daily_timetable"] if t["completed"]
    }
    assert len(completed_ids) >= 1

    # Add another subject and auto-regenerate
    res = client.post(
        f"/api/students/{sid}/study-plan/subjects",
        json={
            "student_id": sid,
            "auto_regenerate_timetable": True,
            "subject": {
                "subject_name": "Sanskrit",
                "number_of_chapters": 4,
                "exam_date": (date.today() + timedelta(days=9)).isoformat(),
                "subject_difficulty": "Medium",
            },
        },
    )
    assert res.status_code == 200
    after_plan = res.json()
    after_completed_ids = {
        t["task_id"] for t in after_plan["daily_timetable"] if t["completed"]
    }
    assert completed_ids.issubset(after_completed_ids)


def test_12_daily_reminders_and_notification_permissions():
    """12. Daily reminders and notification permissions."""
    sid = "stu_test_upgrade_02"
    _as_student(sid)
    notifs_res = client.get(f"/api/students/{sid}/notifications")
    assert notifs_res.status_code == 200
    notifs_data = notifs_res.json()
    assert len(notifs_data["notifications"]) > 0

    # Verify zero duplicate notification IDs
    ids = [n["id"] for n in notifs_data["notifications"]]
    assert len(ids) == len(set(ids))

    # Update reminder preferences (custom times, Android permission, category toggles)
    prefs_res = client.put(
        f"/api/students/{sid}/reminders/preferences",
        json={
            "student_id": sid,
            "daily_study_sessions_enabled": True,
            "pending_chapters_enabled": True,
            "homework_deadlines_enabled": True,
            "upcoming_exams_enabled": True,
            "revision_sessions_enabled": True,
            "mock_tests_enabled": False,
            "custom_reminder_times": ["6:30 PM", "7:45 AM"],
            "android_notifications_permission": "granted",
            "in_app_reminders_enabled": True,
            "timezone_name": "Asia/Kolkata",
        },
    )
    assert prefs_res.status_code == 200
    prefs = prefs_res.json()
    assert prefs["android_notifications_permission"] == "granted"
    assert "6:30 PM" in prefs["custom_reminder_times"]

    # Mark a reminder Completed
    first_notif = notifs_data["notifications"][0]
    status_res = client.patch(
        f"/api/students/{sid}/reminders/status",
        json={
            "student_id": sid,
            "notification_id": first_notif["id"],
            "status": "Completed",
            "linked_entity_type": first_notif.get("linked_entity_type"),
            "linked_entity_id": first_notif.get("linked_entity_id"),
        },
    )
    assert status_res.status_code == 200
    updated_notif = next(
        n for n in status_res.json()["notifications"] if n["id"] == first_notif["id"]
    )
    assert updated_notif["status"] == "Completed"


def test_13_registration_for_children_under_8_requiring_parental_assistance():
    """13. Registration for children under 8 requiring parental assistance and consent."""
    sid = "stu_child_under8_test"
    client.cookies.clear()
    repo.students.pop(sid, None)
    repo.academic_years.pop(sid, None)
    reg_res = client.post(
        "/api/auth/register",
        json={
            "student_id": sid,
            "full_name": "Aarav Junior",
            "age": 6,
            "grade": 1,
            "date_of_birth": "2020-05-10",
        },
    )
    assert reg_res.status_code == 200
    data = reg_res.json()
    assert data["requires_parental_assistance"] is True
    assert data["parent_consent_verified"] is False
    assert data["child_safety_message"] == "Please use your parent's help to sign in."

    onboarding_payload = {
        "student_id": sid,
        "academic_year_label": "2026-2027",
        "step1": {
            "age": 6,
            "grade": 1,
            "school_board": "CBSE",
            "school_medium": "English",
            "preferred_explanation_language": "Telugu",
            "secondary_explanation_language": "English",
            "interface_display_language": "English",
        },
        "selected_subjects": ["G1_MATH", "G1_ENG"],
        "help_with_all_subjects": False,
        "subjects_to_improve": ["G1_MATH"],
        "subject_confidence": [
            {
                "subject_code": "G1_MATH",
                "subject_name": "Mathematics",
                "confidence_level": "Need help",
                "difficult_topics": ["Counting and Addition"],
            }
        ],
        "main_improvement_priority": "Understand difficult concepts",
        "learning_challenges": ["I take too much time to complete homework."],
        "when_need_most_help": ["While solving questions"],
        "challenge_frequency": "Sometimes",
        "everything_goal_selected": True,
        "selected_goals": ["g1"],
    }

    # Attempt to bypass parental verification and submit onboarding directly -> MUST FAIL (HTTP 422)
    bypass_res = client.post("/api/onboarding/submit", json=onboarding_payload)
    assert bypass_res.status_code == 422
    assert "under 8" in str(bypass_res.json()["detail"]).lower()

    # Complete multi-factor parental consent verification
    consent_res = client.post(
        "/api/auth/parental-consent",
        json={
            "student_id": sid,
            "parent_full_name": "Priya Sharma",
            "relationship_to_child": "Mother",
            "parent_email_or_phone": "priya.sharma@example.com",
            "parent_pin_code": "4829",
            "verification_otp_code": "654321",
            "guardian_attestation_statement": "I am the legal mother and I authorise assisted registration and supervision for my child.",
            "child_safety_mode_enabled": True,
        },
    )
    assert consent_res.status_code == 200
    assert consent_res.json()["parent_consent_verified"] is True

    # Now onboarding succeeds
    onb_res = client.post("/api/onboarding/submit", json=onboarding_payload)
    assert onb_res.status_code == 200


def test_14_registration_for_students_aged_8_and_above():
    """14. Registration for students aged 8 and above."""
    sid = "stu_age_10_normal"
    reg_res = client.post(
        "/api/auth/register",
        json={"student_id": sid, "full_name": "Rohan Kumar", "age": 10, "grade": 5},
    )
    assert reg_res.status_code == 200
    data = reg_res.json()
    assert data["requires_parental_assistance"] is False
    assert data["parent_consent_verified"] is True
    assert data["status"] == "authenticated"


def test_15_enter_exam_marks_and_calculate_percentages():
    """15. Entering exam marks and calculating percentages."""
    sid = "stu_test_upgrade_02"
    _as_student(sid)
    res = client.post(
        f"/api/students/{sid}/exam-marks",
        json={
            "student_id": sid,
            "subject": "Mathematics",
            "exam_name": "Unit Test 1",
            "exam_type": "Unit Test",
            "exam_date": "2026-10-15",
            "marks_obtained": 42,
            "maximum_marks": 50,
            "remarks": "Good algebra accuracy",
        },
    )
    assert res.status_code == 200
    mk = res.json()
    assert mk["percentage"] == 84.0
    assert mk["verification_status"] == "STUDENT_REPORTED"


def test_16_reject_invalid_marks_negative_or_exceeding_maximum():
    """16. Rejecting invalid marks such as negative values or marks exceeding maximum marks."""
    sid = "stu_test_upgrade_02"
    _as_student(sid)
    # Negative marks
    neg_res = client.post(
        f"/api/students/{sid}/exam-marks",
        json={
            "student_id": sid,
            "subject": "Mathematics",
            "exam_name": "Invalid Negative Test",
            "exam_type": "Unit Test",
            "exam_date": "2026-10-20",
            "marks_obtained": -5,
            "maximum_marks": 100,
        },
    )
    assert neg_res.status_code == 422

    # Marks obtained > Maximum marks
    exceed_res = client.post(
        f"/api/students/{sid}/exam-marks",
        json={
            "student_id": sid,
            "subject": "Mathematics",
            "exam_name": "Invalid Exceed Test",
            "exam_type": "Unit Test",
            "exam_date": "2026-10-20",
            "marks_obtained": 105,
            "maximum_marks": 100,
        },
    )
    assert exceed_res.status_code == 422


def test_17_preserve_previous_exam_records_when_new_marks_added():
    """17. Preserving previous exam records when new marks are added."""
    sid = "stu_test_upgrade_02"
    _as_student(sid)
    res2 = client.post(
        f"/api/students/{sid}/exam-marks",
        json={
            "student_id": sid,
            "subject": "Mathematics",
            "exam_name": "Mid-Term Exam",
            "exam_type": "Mid-Term / Half-Yearly",
            "exam_date": "2026-11-05",
            "marks_obtained": 92,
            "maximum_marks": 100,
            "remarks": "Improved speed",
        },
    )
    assert res2.status_code == 200
    assert res2.json()["trend"] == "Improvement"

    history_res = client.get(f"/api/students/{sid}/exam-marks")
    assert history_res.status_code == 200
    marks_list = history_res.json()["exam_marks"]
    assert len(marks_list) == 2
    exam_names = [m["exam_name"] for m in marks_list]
    assert "Unit Test 1" in exam_names
    assert "Mid-Term Exam" in exam_names


def test_18_update_academic_progress_and_ai_recommendations_after_low_marks():
    """18. Updating academic progress and AI recommendations after low exam marks (without inventing chapters)."""
    sid = "stu_test_upgrade_02"
    _as_student(sid)
    low_res = client.post(
        f"/api/students/{sid}/exam-marks",
        json={
            "student_id": sid,
            "subject": "Science",
            "exam_name": "Term-1 Science Exam",
            "exam_type": "Term Exam",
            "exam_date": "2026-11-08",
            "marks_obtained": 45,
            "maximum_marks": 100,
            "remarks": "Struggled with numericals",
            "chapters_tested": [],  # Subject-level marks only!
        },
    )
    assert low_res.status_code == 200

    # Check Academic Progress Report
    prog = client.get(f"/api/students/{sid}/progress").json()
    assert "Science" in prog["subjects_requiring_attention"]

    # Check Study Plan automatically prioritized Science as weak subject
    plan = client.get(f"/api/students/{sid}/study-plan").json()
    assert "Science" in plan["weak_subjects"]

    # Check AI Learning Buddy Diagnosis Agent receives exam marks without inventing chapter weaknesses
    tutor_res = client.post(
        "/api/tutor/session/start",
        json={
            "student_id": sid,
            "typed_question": "Explain how to improve my Science exam topics",
            "subject_hint": "Science",
        },
    )
    assert tutor_res.status_code == 200
    tutor_state = tutor_res.json()
    diag_out = tutor_state["diagnosis_output"]
    assert any(
        "Subject-level exam score only" in s
        for s in diag_out["student_self_reported_difficulties"]
    )


def test_19_parent_access_permissions():
    """19. Parent access permissions."""
    sid = "stu_test_upgrade_02"
    student = repo.students[sid]
    authorised_parent_id = student["parent_id"]

    # Authorised parent can view exam marks, study tasks, homework, reminders, and safety controls
    ok_res = client.get(f"/api/parent/{authorised_parent_id}/child/{sid}")
    assert ok_res.status_code == 200
    p_data = ok_res.json()
    assert p_data["authorised"] is True
    assert len(p_data["exam_marks"]) == 3
    assert "reminder_preferences" in p_data
    assert "child_safety_controls" in p_data

    # Unauthorised parent is strictly blocked with HTTP 403
    unauth_res = client.get(f"/api/parent/parent_intruder_999/child/{sid}")
    assert unauth_res.status_code == 403


def test_20_data_persistence_after_logout_and_login():
    """20. Data persistence after logout and login (and disk reload)."""
    sid = "stu_test_upgrade_02"
    # Instantiate a fresh EduSparkRepository reading from the persisted JSON store on disk
    fresh_repo = EduSparkRepository()
    assert sid in fresh_repo.students
    persisted_plan = fresh_repo.get_or_create_study_plan(sid)
    assert len(persisted_plan.exam_subjects) == 6
    persisted_marks = fresh_repo.list_exam_marks(sid)
    assert len(persisted_marks) == 3
    persisted_prefs = fresh_repo.get_or_create_reminder_preferences(sid)
    assert "6:30 PM" in persisted_prefs.custom_reminder_times

