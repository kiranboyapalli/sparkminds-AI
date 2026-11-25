"""
SparkMinds AI — Complete Production Readiness, Multi-Device Sync, PWA & 13 User Journeys Verification Suite
Tests all 13 mandatory pre-launch user journeys (Section 16):
1. Student registration
2. Student onboarding
3. Login from a second browser / device session (One Account, Multiple Devices without duplicates)
4. Daily schedule check-in
5. Study plan generation
6. Homework entry & persistent file upload
7. AI Learning Buddy question and response
8. Practice test / Mock exam
9. Revision flow
10. Academic progress tracking
11. Parent access & Child Safety
12. Logout and re-login + Account recovery
13. SQLite + JSON database persistence across restarts + Database Backup & Restore + PWA assets
"""
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.core.repository import EduSparkRepository, repo

client = TestClient(app)


def test_complete_13_production_user_journeys_and_multi_device_sync():
    student_id = "stu_prod_vihaan_g8"
    email = "vihaan.g8@sparkminds.ai"
    # Ensure idempotency across consecutive test runs
    repo.auth_credentials.pop(student_id, None)

    # ------------------------------------------------------------------------
    # JOURNEY 1: Student Registration (Laptop Browser)
    # ------------------------------------------------------------------------
    reg_res = client.post(
        "/api/auth/register",
        json={
            "student_id": student_id,
            "full_name": "Vihaan Deshmukh",
            "age": 13,
            "grade": 8,
            "date_of_birth": "2013-04-15",
            "email_or_username": email,
            "password_or_pin": "Spark2026!",
            "device_name": "Windows Laptop Chrome",
        },
    )
    assert reg_res.status_code == 200
    reg_data = reg_res.json()
    assert reg_data["status"] == "authenticated"
    laptop_token = reg_data["session_token"]
    assert laptop_token.startswith("spark_sess_")
    assert reg_data["student"]["student_id"] == student_id
    assert reg_data["student"]["email_or_username"] == email

    # ------------------------------------------------------------------------
    # JOURNEY 2: 7-Step Student Onboarding
    # ------------------------------------------------------------------------
    onb_res = client.post(
        "/api/onboarding/submit",
        json={
            "student_id": student_id,
            "academic_year_label": "2026-2027",
            "step1": {
                "age": 13,
                "grade": 8,
                "school_board": "CBSE",
                "state_name": "Maharashtra",
                "school_medium": "English",
                "preferred_explanation_language": "Marathi",
                "secondary_explanation_language": "English",
                "interface_display_language": "English",
            },
            "selected_subjects": ["G8_MATH", "G8_SCI", "G8_SST", "G8_ENG"],
            "help_with_all_subjects": False,
            "subjects_to_improve": ["G8_MATH", "G8_SCI"],
            "subject_confidence": [
                {
                    "subject_code": "G8_MATH",
                    "subject_name": "Mathematics",
                    "confidence_level": "Need help",
                    "difficult_topics": ["Linear Equations in One Variable", "Mensuration"],
                },
                {
                    "subject_code": "G8_SCI",
                    "subject_name": "General Science",
                    "confidence_level": "Okay",
                    "difficult_topics": ["Force and Pressure"],
                },
            ],
            "main_improvement_priority": "Understand difficult concepts",
            "learning_challenges": [
                "I don't understand some concepts.",
                "I struggle with application-based questions.",
            ],
            "when_need_most_help": ["While solving questions"],
            "challenge_frequency": "Often",
            "everything_goal_selected": True,
            "selected_goals": ["g1", "g2", "g3", "g4", "g5", "g6", "g7", "g8", "g9"],
            "primary_goal": "g2",
        },
    )
    assert onb_res.status_code == 200
    assert onb_res.json()["status"] == "onboarding_saved"

    # ------------------------------------------------------------------------
    # JOURNEY 4: Daily Schedule Check-In (12-Hour AM/PM Personal Schedule)
    # ------------------------------------------------------------------------
    checkin_res = client.post(
        f"/api/students/{student_id}/daily-schedule/check-in",
        json={
            "student_id": student_id,
            "schedule_date": "2026-11-12",
            "rest_of_day_free": False,
            "wake_up_time": "6:30 AM",
            "sleep_time": "10:00 PM",
            "activities": [
                {
                    "activity_name": "School",
                    "category": "School",
                    "start_time": "8:00 AM",
                    "end_time": "3:00 PM",
                },
                {
                    "activity_name": "Chess Classes",
                    "category": "Chess classes",
                    "start_time": "5:00 PM",
                    "end_time": "6:00 PM",
                },
            ],
        },
    )
    assert checkin_res.status_code == 200
    checkin_data = checkin_res.json()
    assert checkin_data["checkin_completed"] is True
    assert checkin_data["total_available_study_minutes"] > 0

    # ------------------------------------------------------------------------
    # JOURNEY 5: Study Plan Generation & Subject Addition
    # ------------------------------------------------------------------------
    plan_res = client.get(f"/api/students/{student_id}/study-plan")
    assert plan_res.status_code == 200
    assert len(plan_res.json()["daily_timetable"]) > 0

    # ------------------------------------------------------------------------
    # JOURNEY 6: Homework Entry & Persistent File Upload Storage
    # ------------------------------------------------------------------------
    hw_res = client.post(
        f"/api/students/{student_id}/homework",
        json={
            "student_id": student_id,
            "subject": "Mathematics",
            "chapter": "Linear Equations in One Variable",
            "title": "Exercise 2.1 Linear Equations",
            "description": "Solve Exercise 2.1 Questions 1 to 5",
            "due_date": "2026-11-15",
            "priority": "High",
            "estimated_minutes": 30,
        },
    )
    assert hw_res.status_code == 200
    assert hw_res.json()["subject"] == "Mathematics"

    upload_res = client.post(
        f"/api/students/{student_id}/files/upload",
        json={
            "filename": "math_worksheet_ex2_1.txt",
            "text_content": "Solve: 2x - 3 = 7",
            "content_type": "text/plain",
            "category": "homework",
        },
    )
    assert upload_res.status_code == 200
    uploaded_file_meta = upload_res.json()["file"]
    assert Path(uploaded_file_meta["stored_path"]).exists()

    files_list_res = client.get(f"/api/students/{student_id}/files")
    assert files_list_res.status_code == 200
    assert files_list_res.json()["count"] >= 1

    # ------------------------------------------------------------------------
    # JOURNEY 3: Login from a Second Device (Android Phone) — Zero Duplicates!
    # ------------------------------------------------------------------------
    student_count_before = len(repo.students)

    # Wrong password must be rejected
    bad_login = client.post(
        "/api/auth/login",
        json={
            "identifier": email,
            "password_or_pin": "WrongPassword123",
            "device_name": "Android Phone Chrome",
        },
    )
    assert bad_login.status_code == 401

    # Correct login via Email on Android Phone
    android_login = client.post(
        "/api/auth/login",
        json={
            "identifier": email,
            "password_or_pin": "Spark2026!",
            "device_name": "Android Phone Chrome",
        },
    )
    assert android_login.status_code == 200
    android_bundle = android_login.json()["cloud_sync_bundle"]
    android_token = android_login.json()["session_token"]

    # Verify zero duplicate profiles created and 100% cloud data synchronisation
    assert len(repo.students) == student_count_before
    assert android_bundle["student_id"] == student_id
    assert android_bundle["student"]["full_name"] == "Vihaan Deshmukh"
    assert android_bundle["student"]["current_grade"] == 8
    assert android_bundle["student"]["school_board"] == "CBSE"
    assert (
        android_bundle["student"]["language_preferences"]["preferred_explanation_language"]
        == "Marathi"
    )
    assert "G8_MATH" in android_bundle["active_year_profile"]["subjects_studied"]
    assert len(android_bundle["homeworks"]) >= 1
    assert len(android_bundle["uploaded_files"]) >= 1
    assert len(android_bundle["active_devices"]) >= 2

    # Verify session restore endpoint using Bearer token
    sess_res = client.get(
        "/api/auth/session",
        headers={"Authorization": f"Bearer {android_token}"},
    )
    assert sess_res.status_code == 200
    assert sess_res.json()["student"]["student_id"] == student_id

    # ------------------------------------------------------------------------
    # JOURNEY 7: AI Learning Buddy Question & Socratic Response
    # ------------------------------------------------------------------------
    tutor_start = client.post(
        "/api/tutor/session/start",
        json={
            "student_id": student_id,
            "typed_question": "Solve 2x - 3 = 7",
            "subject_hint": "Mathematics",
        },
    )
    assert tutor_start.status_code == 200
    session_id = tutor_start.json()["session_id"]
    assert tutor_start.json()["teaching_output"]["concept_explanation"]

    tutor_reply = client.post(
        "/api/tutor/session/turn",
        json={
            "session_id": session_id,
            "student_id": student_id,
            "student_response": "Add 3 to both sides so 2x = 10 and x = 5",
        },
    )
    assert tutor_reply.status_code == 200

    # ------------------------------------------------------------------------
    # JOURNEY 8: Practice Test / Mock Exam Generation & Grading
    # ------------------------------------------------------------------------
    exam_gen = client.post(
        f"/api/students/{student_id}/exams/generate",
        json={
            "student_id": student_id,
            "exam_mode": "Chapter Test",
            "subject": "Mathematics",
            "chapters": ["Linear Equations in One Variable"],
            "duration_minutes": 15,
            "question_count": 3,
        },
    )
    assert exam_gen.status_code == 200
    exam_obj = exam_gen.json()
    exam_id = exam_obj["exam_id"]
    answers_map = {q["question_id"]: q["correct_answer"] for q in exam_obj["questions"]}

    exam_sub = client.post(
        f"/api/students/{student_id}/exams/{exam_id}/submit",
        json={"student_id": student_id, "answers": answers_map},
    )
    assert exam_sub.status_code == 200
    assert exam_sub.json()["score_percentage"] == 100.0

    # ------------------------------------------------------------------------
    # JOURNEY 9: Smart Revision Flow
    # ------------------------------------------------------------------------
    rev_gen = client.post(
        f"/api/students/{student_id}/revision/generate",
        json={
            "student_id": student_id,
            "subject": "Mathematics",
            "topic": "Linear Equations Transposition Rule",
        },
    )
    assert rev_gen.status_code == 200
    rev_id = rev_gen.json()["revision_id"]

    rev_upd = client.patch(
        f"/api/students/{student_id}/revision/{rev_id}/review",
        json={"student_id": student_id, "recall_quality": "Easy"},
    )
    assert rev_upd.status_code == 200
    assert rev_upd.json()["completed_today"] is True

    # ------------------------------------------------------------------------
    # JOURNEY 10: Academic Progress Tracking & Exam Marks Entry
    # ------------------------------------------------------------------------
    mark_res = client.post(
        f"/api/students/{student_id}/exam-marks",
        json={
            "student_id": student_id,
            "subject": "Mathematics",
            "exam_name": "Unit Test 1",
            "exam_date": "2026-10-20",
            "marks_obtained": 44,
            "maximum_marks": 50,
            "weak_chapters": ["Mensuration"],
        },
    )
    assert mark_res.status_code == 200
    assert mark_res.json()["percentage"] == 88.0

    prog_res = client.get(f"/api/students/{student_id}/progress")
    assert prog_res.status_code == 200
    assert len(prog_res.json()["subject_wise_progress"]) >= 1

    # ------------------------------------------------------------------------
    # JOURNEY 11: Parent Access & Overview
    # ------------------------------------------------------------------------
    parent_id = reg_data["student"]["parent_id"]
    parent_res = client.get(
        f"/api/parent/{parent_id}/child/{student_id}"
    )
    assert parent_res.status_code == 200
    assert parent_res.json()["child_profile"]["full_name"] == "Vihaan Deshmukh"
    assert "daily_schedule" in parent_res.json()

    # ------------------------------------------------------------------------
    # JOURNEY 12: Logout, Re-Login & Account Recovery
    # ------------------------------------------------------------------------
    logout_res = client.post(
        "/api/auth/logout",
        json={"session_token": android_token, "student_id": student_id},
    )
    assert logout_res.status_code == 200
    assert logout_res.json()["status"] == "logged_out"

    # Logged-out token must no longer be accepted
    expired_sess = client.get(
        "/api/auth/session",
        headers={"Authorization": f"Bearer {android_token}"},
    )
    assert expired_sess.status_code == 401

    # Account Recovery resets password/PIN using Date of Birth proof
    recover_res = client.post(
        "/api/auth/recover",
        json={
            "identifier": email,
            "recovery_proof": "2013-04-15",
            "new_password_or_pin": "NewPin2027",
            "device_name": "iPad Safari PWA",
        },
    )
    assert recover_res.status_code == 200
    assert recover_res.json()["status"] == "account_recovered"

    # Re-login with new password/PIN works and loads all data
    relogin_res = client.post(
        "/api/auth/login",
        json={
            "identifier": student_id,
            "password_or_pin": "NewPin2027",
            "device_name": "iPad Safari PWA",
        },
    )
    assert relogin_res.status_code == 200
    assert relogin_res.json()["cloud_sync_bundle"]["student"]["full_name"] == "Vihaan Deshmukh"

    # ------------------------------------------------------------------------
    # JOURNEY 13: SQLite + JSON Persistence Across Restart & Backup / Restore
    # ------------------------------------------------------------------------
    assert repo.sqlite_db_path.exists()
    reloaded_repo = EduSparkRepository(db_path=str(repo.db_file))
    assert student_id in reloaded_repo.students
    assert reloaded_repo.students[student_id]["full_name"] == "Vihaan Deshmukh"
    assert len(reloaded_repo.homeworks.get(student_id, [])) >= 1
    assert len(reloaded_repo.exam_marks.get(student_id, [])) >= 1

    # Create & Restore Database Backup
    bkp_res = client.post(
        "/api/admin/database/backup",
        json={"reason": "pre_release_verification"},
    )
    assert bkp_res.status_code == 200
    backup_id = bkp_res.json()["backup"]["backup_id"]

    bkp_list = client.get("/api/admin/database/backups")
    assert bkp_list.status_code == 200
    assert bkp_list.json()["count"] >= 1

    restore_res = client.post(
        "/api/admin/database/restore",
        json={"backup_id": backup_id},
    )
    assert restore_res.status_code == 200
    assert restore_res.json()["status"] == "backup_restored"


def test_pwa_manifest_service_worker_icons_and_offline_fallback_exist():
    frontend_public = Path(__file__).resolve().parent.parent.parent / "frontend" / "public"
    assert (frontend_public / "manifest.json").exists()
    assert (frontend_public / "sw.js").exists()
    assert (frontend_public / "offline.html").exists()
    assert (frontend_public / "icon-192.png").exists()
    assert (frontend_public / "icon-512.png").exists()
    assert (frontend_public / "apple-touch-icon.png").exists()
    assert (frontend_public / "favicon.svg").exists()

    sw_text = (frontend_public / "sw.js").read_text(encoding="utf-8")
    assert "/api/" in sw_text
    assert "SKIP_WAITING" in sw_text
