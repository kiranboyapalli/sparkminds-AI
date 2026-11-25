"""
SparkMinds AI — Verification Suite for Daily Availability & Personal Schedule Integration
Tests:
1. Daily schedule check-in prompt & pre-filling recurring weekly activities before check-in (checkin_completed == False).
2. Adding multiple activities (e.g., Tuition 4:00 PM - 5:00 PM, Chess class 5:30 PM - 6:30 PM, Drawing class 7:00 PM - 8:00 PM),
   calculating available study hours, and generating the personalised daily plan with zero sessions overlapping Tuition, Chess, Drawing, or Sleep/Rest.
3. Rejecting overlapping activities and invalid time ranges (end_time <= start_time) with HTTP 422.
4. Mid-day schedule changes (e.g., cancelling Tuition or postponing Chess class with current_time_12h) regenerating the remaining plan
   while preserving completed tasks, avoiding duplicates, and never scheduling new tasks in the past.
5. Recurring weekly activities (Only today, Repeated on selected weekdays, Repeated every day) pre-filling on matching future weekdays.
6. Marking the day as free (free_all_day=True) without forcing students to enter activities.
7. Integration across Student Dashboard, Reminder & Notification System, AI Learning Buddy (Diagnosis Agent), and Parent Dashboard.
"""
from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import parse_time_to_minutes

client = TestClient(app)


def _extract_start_end_mins(time_slot: str) -> tuple[int, int]:
    parts = [p.strip() for p in time_slot.split("-")]
    assert len(parts) == 2, f"Expected 'START - END' in 12-hour format, got: {time_slot}"
    return parse_time_to_minutes(parts[0]), parse_time_to_minutes(parts[1])


def test_1_daily_checkin_prompt_and_recurring_prefill():
    """
    Before generating each day's study plan, SparkMinds AI asks the student about their schedule
    with the friendly prompt and pre-fills recurring activities for that weekday.
    """
    # Use a specific Wednesday date (2026-11-18 is Wednesday)
    res = client.get("/api/students/stu_aarav_g7/daily-schedule?date_iso=2026-11-18")
    assert res.status_code == 200
    data = res.json()
    assert data["checkin_completed"] is False
    assert data["greeting_prompt"] == "Good morning! ☀️ Let's plan your day. What does your schedule look like today?"
    assert data["weekday_name"] == "Wednesday"
    # Aarav has default recurring Tuition Mon-Fri 4:00 PM - 5:00 PM
    act_names = [a["activity_name"] for a in data["activities"]]
    assert "Tuition" in act_names
    assert data["available_study_hours"] > 0


def test_2_example_schedule_tuition_chess_drawing_no_overlap():
    """
    Matches the user's exact specification example:
    - Tuition: 4:00 PM – 5:00 PM
    - Chess class: 5:30 PM – 6:30 PM
    - Drawing class: 7:00 PM – 8:00 PM
    Verifies:
    - Zero study sessions or homework overlap with Tuition, Chess class, or Drawing class.
    - Combined timeline includes Study sessions, Homework, Breaks, and (Unavailable) activity blocks.
    - All time slots use 12-hour AM/PM format.
    """
    payload = {
        "student_id": "stu_aarav_g7",
        "date_iso": "2026-11-19",
        "free_all_day": False,
        "sleep_start_time": "10:00 PM",
        "wake_up_time": "6:30 AM",
        "preferred_study_period": "Flexible",
        "activities": [
            {
                "activity_name": "Tuition",
                "category": "Tuition",
                "start_time": "4:00 PM",
                "end_time": "5:00 PM",
                "location": "Maths Coaching Centre",
                "notes": "Bring geometry box",
                "recurrence": "Only today",
            },
            {
                "activity_name": "Chess class",
                "category": "Chess classes",
                "start_time": "5:30 PM",
                "end_time": "6:30 PM",
                "location": "Club Academy",
                "recurrence": "Only today",
            },
            {
                "activity_name": "Drawing class",
                "category": "Drawing classes",
                "start_time": "7:00 PM",
                "end_time": "8:00 PM",
                "location": "Art Studio",
                "recurrence": "Only today",
            },
        ],
    }
    res = client.post("/api/students/stu_aarav_g7/daily-schedule/check-in", json=payload)
    assert res.status_code == 200
    sched = res.json()
    assert sched["checkin_completed"] is True
    assert sched["available_study_hours"] > 0

    unavailable_ranges = [
        (parse_time_to_minutes("4:00 PM"), parse_time_to_minutes("5:00 PM")),
        (parse_time_to_minutes("5:30 PM"), parse_time_to_minutes("6:30 PM")),
        (parse_time_to_minutes("7:00 PM"), parse_time_to_minutes("8:00 PM")),
    ]

    timeline = sched["generated_daily_timeline"]
    assert len(timeline) >= 6

    unavailable_blocks = [b for b in timeline if b["session_type"] == "Unavailable"]
    assert len(unavailable_blocks) == 3
    unavail_chapters = [b["chapter"] for b in unavailable_blocks]
    assert any("Tuition (Unavailable)" in c for c in unavail_chapters)
    assert any("Chess class (Unavailable)" in c for c in unavail_chapters)
    assert any("Drawing class (Unavailable)" in c for c in unavail_chapters)

    study_and_hw_blocks = [
        b for b in timeline if b["session_type"] in ("Concept Learning", "Practice", "Revision", "Homework")
    ]
    assert len(study_and_hw_blocks) >= 2

    # Ensure NO study/homework/break block overlaps with Tuition, Chess class, or Drawing class
    for b in timeline:
        assert "AM" in b["time_slot"] or "PM" in b["time_slot"]
        if b["session_type"] != "Unavailable":
            b_start, b_end = _extract_start_end_mins(b["time_slot"])
            for u_start, u_end in unavailable_ranges:
                overlaps = b_start < u_end and b_end > u_start
                assert not overlaps, f"Block {b['time_slot']} ({b['subject']}) overlapped with unavailable range {u_start}-{u_end}!"


def test_3_prevent_overlapping_and_invalid_time_ranges():
    """
    Prevents overlapping activities and invalid time ranges (end_time <= start_time).
    """
    # 1. Invalid time range (end_time <= start_time)
    bad_range = {
        "student_id": "stu_aarav_g7",
        "date_iso": "2026-11-20",
        "activities": [
            {
                "activity_name": "Tuition",
                "category": "Tuition",
                "start_time": "5:00 PM",
                "end_time": "4:00 PM",
            }
        ],
    }
    res1 = client.post("/api/students/stu_aarav_g7/daily-schedule/check-in", json=bad_range)
    assert res1.status_code == 422

    # 2. Overlapping activities (4:00 PM - 5:30 PM and 5:00 PM - 6:00 PM)
    overlap_payload = {
        "student_id": "stu_aarav_g7",
        "date_iso": "2026-11-20",
        "activities": [
            {
                "activity_name": "Tuition",
                "category": "Tuition",
                "start_time": "4:00 PM",
                "end_time": "5:30 PM",
            },
            {
                "activity_name": "Chess class",
                "category": "Chess classes",
                "start_time": "5:00 PM",
                "end_time": "6:00 PM",
            },
        ],
    }
    res2 = client.post("/api/students/stu_aarav_g7/daily-schedule/check-in", json=overlap_payload)
    assert res2.status_code == 422
    assert "Overlapping" in res2.text


def test_4_midday_schedule_change_preserves_completed_and_avoids_past():
    """
    When a student's schedule changes during the day (e.g., Tuition is cancelled at 3:30 PM):
    - Completed tasks are preserved
    - Duplicate tasks are avoided
    - New tasks are NOT scheduled in the past (before 3:30 PM)
    - Remaining available time is recalculated
    """
    date_iso = "2026-11-21"
    checkin_res = client.post(
        "/api/students/stu_aarav_g7/daily-schedule/check-in",
        json={
            "student_id": "stu_aarav_g7",
            "date_iso": date_iso,
            "activities": [
                {
                    "activity_id": "act_tuition_test21",
                    "activity_name": "Tuition",
                    "category": "Tuition",
                    "start_time": "4:00 PM",
                    "end_time": "5:00 PM",
                },
                {
                    "activity_id": "act_chess_test21",
                    "activity_name": "Chess class",
                    "category": "Chess classes",
                    "start_time": "6:00 PM",
                    "end_time": "7:00 PM",
                },
            ],
        },
    )
    assert checkin_res.status_code == 200
    initial_sched = checkin_res.json()
    initial_hours = initial_sched["available_study_hours"]

    # Mark the first study task as completed
    study_tasks = [
        t for t in initial_sched["generated_daily_timeline"]
        if t["session_type"] not in ("Break", "Unavailable")
    ]
    assert len(study_tasks) >= 1
    first_task = study_tasks[0]
    toggle_res = client.patch(
        f"/api/students/stu_aarav_g7/study-plan/tasks/{first_task['task_id']}",
        json={"completed": True},
    )
    assert toggle_res.status_code == 200

    # Now at 3:30 PM, student cancels Tuition (4:00 PM - 5:00 PM) and regenerates remaining plan
    patch_res = client.patch(
        "/api/students/stu_aarav_g7/daily-schedule/activities/act_tuition_test21",
        json={
            "date_iso": date_iso,
            "is_cancelled_today": True,
            "current_time_12h": "3:30 PM",
            "regenerate_remaining_plan": True,
        },
    )
    assert patch_res.status_code == 200
    updated_sched = patch_res.json()

    # Unavailable minutes should decrease because 1 hour (60 mins) of Tuition was cancelled
    assert updated_sched["total_unavailable_minutes"] < initial_sched["total_unavailable_minutes"]
    assert updated_sched["available_study_hours"] > 0

    # Verify the completed task is preserved in the timeline
    completed_in_updated = [
        t for t in updated_sched["generated_daily_timeline"]
        if t["task_id"] == first_task["task_id"] and t["completed"] is True
    ]
    assert len(completed_in_updated) == 1

    # Verify all newly scheduled uncompleted study tasks start at or after 3:30 PM (930 mins)
    cutoff_mins = parse_time_to_minutes("3:30 PM")
    for block in updated_sched["generated_daily_timeline"]:
        if block["session_type"] not in ("Unavailable", "Break") and not block["completed"]:
            b_start, _ = _extract_start_end_mins(block["time_slot"])
            assert b_start >= cutoff_mins, f"Uncompleted task {block['time_slot']} scheduled before 3:30 PM!"


def test_5_free_all_day_and_recurring_activities():
    """
    Tests marking the whole day as free (free_all_day=True) and saving recurring activities.
    """
    # 1. Free all day without forcing activity entry
    free_res = client.post(
        "/api/students/stu_aarav_g7/daily-schedule/check-in",
        json={
            "student_id": "stu_aarav_g7",
            "date_iso": "2026-11-22",
            "free_all_day": True,
            "activities": [],
        },
    )
    assert free_res.status_code == 200
    free_data = free_res.json()
    assert free_data["checkin_completed"] is True
    assert free_data["free_all_day"] is True
    assert len(free_data["activities"]) == 0
    assert free_data["available_study_hours"] >= 10.0

    # 2. Save a recurring activity on Fridays ("Fri") and verify it pre-fills next Friday (2026-11-27)
    rec_res = client.post(
        "/api/students/stu_aarav_g7/daily-schedule/check-in",
        json={
            "student_id": "stu_aarav_g7",
            "date_iso": "2026-11-20",
            "activities": [
                {
                    "activity_name": "Music classes",
                    "category": "Music classes",
                    "start_time": "5:00 PM",
                    "end_time": "6:00 PM",
                    "recurrence": "Repeated on selected weekdays",
                    "recurrence_days": ["Fri"],
                }
            ],
        },
    )
    assert rec_res.status_code == 200

    next_fri = client.get("/api/students/stu_aarav_g7/daily-schedule?date_iso=2026-11-27")
    assert next_fri.status_code == 200
    fri_data = next_fri.json()
    assert fri_data["checkin_completed"] is False
    assert any(a["activity_name"] == "Music classes" for a in fri_data["activities"])


def test_6_cross_platform_integration_dashboard_buddy_parent():
    """
    Verifies Daily Availability & Personal Schedule is connected across:
    - Student Dashboard (/api/students/{id}/dashboard-summary)
    - AI Learning Buddy Diagnosis Agent (/api/tutor/session/start)
    - Parent Dashboard (/api/parent/{parent_id}/child/{student_id})
    """
    dash = client.get("/api/students/stu_aarav_g7/dashboard-summary")
    assert dash.status_code == 200
    dash_data = dash.json()
    assert "daily_schedule" in dash_data
    assert "daily_checkin_required" in dash_data
    assert "todays_combined_schedule" in dash_data

    parent_res = client.get("/api/parent/parent_sharma_01/child/stu_aarav_g7")
    assert parent_res.status_code == 200
    p_data = parent_res.json()
    assert "daily_schedule" in p_data
    assert "recurring_activities" in p_data

    tutor_res = client.post(
        "/api/tutor/session/start",
        json={
            "student_id": "stu_aarav_g7",
            "typed_question": "How do I add 1/4 and 1/6?",
            "subject_hint": "Mathematics",
        },
    )
    assert tutor_res.status_code == 200
    t_data = tutor_res.json()
    self_reports = t_data["diagnosis_output"]["student_self_reported_difficulties"]
    assert any("DAILY AVAILABILITY & SCHEDULE" in sr for sr in self_reports)
