"""
End-to-End Grade 7 Mathematics Homework Session Demonstration Script
Demonstrates the complete redesigned agentic workflow:
1. Image Upload -> Understanding Agent -> Learning Diagnosis Agent -> Teaching Agent (Answer Withheld)
2. Student Attempt #1 (Incorrect: '2/10') -> Assessment Agent pinpoints misconception -> Progressive Hint 1
3. Student Attempt #2 (Repeated Mistake: '2/12') -> Assessment Agent triggers Alternative Visual Strategy
4. Student Attempt #3 (Step 1 Correct: '12') -> Advances to Step 2
5. Student Attempt #4 (Final Correct Answer: '5/12') -> Verifies Mastery & Updates Learning Memory + Academic Journey
"""
import base64
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def run_demo() -> None:
    svg_img = '<svg xmlns="http://www.w3.org/2000/svg"><text>Grade 7 Homework: Solve 1/4 + 1/6</text></svg>'
    b64_img = "data:image/svg+xml;base64," + base64.b64encode(svg_img.encode("utf-8")).decode("utf-8")

    print("=== TURN 1: IMAGE UPLOAD & START GRADE 7 MATHS HOMEWORK SESSION ===")
    s1 = client.post(
        "/api/tutor/session/start",
        json={
            "student_id": "stu_aarav_g7",
            "image_base64": b64_img,
            "subject_hint": "Mathematics",
            "language_override": "Telugu",
            "secondary_language_override": "English",
        },
    ).json()
    sid = s1["session_id"]
    print(f"Session ID: {sid}")
    print(f"Agents Executed in Turn 1: {[log['agent_name'] for log in s1['execution_logs']]}")
    print(f"Vision Extracted Question: {s1['extracted_question']}")
    print(f"Diagnosis Route: {s1['diagnosis_output']['recommended_pedagogical_route']}")
    print(f"Full Answer Withheld?: {s1['teaching_output']['answer_withheld_for_guided_learning']}")
    print(f"Step 1 Prompt (Telugu): {s1['teaching_output']['prompt_for_student_attempt']}\n")

    print("=== TURN 2: STUDENT ATTEMPT #1 (INCORRECT: '2/10' — Added Denominators Directly) ===")
    s2 = client.post(
        "/api/tutor/session/turn",
        json={"session_id": sid, "student_id": "stu_aarav_g7", "student_attempt": "2/10"},
    ).json()
    print(f"Assessment Correct?: {s2['assessment_output']['is_attempt_correct']}")
    print(f"Pinpointed Misconception: {s2['assessment_output']['detected_misconception']}")
    print(f"Conditional Route: {s2['conditional_route_taken']}")
    print(f"Progressive Hint 1: {s2['teaching_output']['active_hint_shown']}\n")

    print("=== TURN 3: STUDENT ATTEMPT #2 (REPEATED MISTAKE: '2/12' — Unscaled Numerators) ===")
    s3 = client.post(
        "/api/tutor/session/turn",
        json={"session_id": sid, "student_id": "stu_aarav_g7", "student_attempt": "2/12"},
    ).json()
    print(f"Mistake Count: {s3['mistake_count']}")
    print(f"Conditional Route: {s3['conditional_route_taken']}")
    print(f"Switched to Alternative Visual Strategy: {s3['teaching_output']['alternative_explanation']}\n")

    print("=== TURN 4: STUDENT ATTEMPT #3 (CORRECT STEP 1: '12' FOR LCM) ===")
    s4 = client.post(
        "/api/tutor/session/turn",
        json={"session_id": sid, "student_id": "stu_aarav_g7", "student_attempt": "12"},
    ).json()
    print(f"Assessment Correct?: {s4['assessment_output']['is_attempt_correct']}")
    print(f"Advanced to Step: {s4['current_step_index']} of {s4['total_steps']}\n")

    print("=== TURN 5: STUDENT ATTEMPT #4 (FINAL CORRECT ANSWER: '5/12') ===")
    s5 = client.post(
        "/api/tutor/session/turn",
        json={"session_id": sid, "student_id": "stu_aarav_g7", "student_attempt": "5/12"},
    ).json()
    print(f"Conceptual Understanding Verified?: {s5['assessment_output']['conceptual_understanding_verified']}")
    print(f"Verified Mastery Score: {s5['assessment_output']['mastery_evidence_score']}%")
    print(f"Follow-up Verification Question: {s5['assessment_output']['follow_up_verification_question']}\n")

    print("=== TURN 6: VERIFY LEARNING MEMORY & ACADEMIC JOURNEY PRESERVATION ===")
    mem = client.get("/api/students/stu_aarav_g7/learning-memory").json()
    rec = next(r for r in mem["records"] if r["session_id"] == sid)
    print(f"Saved LearningMemoryRecord ID: {rec['memory_id']}")
    print(f"Recorded Attempts: {rec['student_attempts']}")
    print(f"Recorded Misconceptions: {rec['detected_misconceptions']}")
    print(f"Assessment Status: {rec['assessment_result']}")

    journey = client.get("/api/students/stu_aarav_g7/academic-journey").json()
    grades = [y["grade"] for y in journey["completed_and_active_years"]]
    print(f"Academic Journey Grades Preserved: {grades}")


if __name__ == "__main__":
    run_demo()

