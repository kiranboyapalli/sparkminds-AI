"""
SparkMinds AI — Agentic AI Ecosystem, Document RAG, Gamification & Push Notification API Router.
All student-scoped routes enforce student privacy via verify_student_access.
"""

from __future__ import annotations

from base64 import b64decode
from typing import Any, Dict, List, Literal, Optional
from fastapi import APIRouter, File, Form, Header, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field

from app.agents.guided_lesson_engine import (
    complete_guided_lesson,
    generate_guided_lesson,
)
from app.core.repository import repo
from app.models.schemas import ReminderPreferences
from app.routers.api_router import verify_student_access


ecosystem_router = APIRouter(prefix="/api", tags=["SparkMinds Agentic Ecosystem"])


# ============================================================================
# 1. CENTRALIZED 6-AGENT ECOSYSTEM & INTELLIGENT ASSESSMENTS
# ============================================================================

class DiagnosticStartRequest(BaseModel):
    student_id: str
    subject: str = "Mathematics"
    topic: Optional[str] = None
    question_count: int = Field(default=4, ge=1, le=10)


class AssessmentGenerateRequest(BaseModel):
    student_id: str
    subject: str = "Mathematics"
    assessment_kind: Literal["DIAGNOSTIC", "QUIZ", "PRACTICE", "REVISION", "DOCUMENT_QUIZ"] = "QUIZ"
    topic: Optional[str] = None
    difficulty: Optional[Literal["Easy", "Medium", "Hard"]] = None
    question_types: Optional[List[Literal["MCQ", "FILL_IN_BLANK", "TRUE_FALSE", "DESCRIPTIVE"]]] = None
    question_count: int = Field(default=4, ge=1, le=10)
    doc_id: Optional[str] = None


class AssessmentSubmitRequest(BaseModel):
    student_id: str
    answers: Dict[str, str] = Field(default_factory=dict)


class StudyPlanAdaptRequest(BaseModel):
    available_daily_hours: Optional[float] = Field(default=None, ge=0.5, le=8.0)


class WorkflowRunRequest(BaseModel):
    student_id: str
    subject: str = "Mathematics"
    topic: Optional[str] = None
    goal: Optional[str] = None


@ecosystem_router.post("/agents/diagnostic/start")
def start_diagnostic_assessment(
    req: DiagnosticStartRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(req.student_id, authorization, x_sparkminds_token)
    res = repo.ecosystem.create_assessment(
        repo=repo,
        student_id=req.student_id,
        subject=req.subject,
        assessment_kind="DIAGNOSTIC",
        topic=req.topic,
        question_count=req.question_count,
    )
    repo.sync_aux_tables_to_postgres()
    return res


@ecosystem_router.post("/agents/assessments/generate")
def generate_intelligent_assessment(
    req: AssessmentGenerateRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(req.student_id, authorization, x_sparkminds_token)
    try:
        res = repo.ecosystem.create_assessment(
            repo=repo,
            student_id=req.student_id,
            subject=req.subject,
            assessment_kind=req.assessment_kind,
            topic=req.topic,
            difficulty=req.difficulty,
            question_types=req.question_types,
            question_count=req.question_count,
            doc_id=req.doc_id,
        )
        repo.sync_aux_tables_to_postgres()
        return res
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@ecosystem_router.post("/agents/assessments/{assessment_id}/submit")
def submit_intelligent_assessment(
    assessment_id: str,
    req: AssessmentSubmitRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(req.student_id, authorization, x_sparkminds_token)
    try:
        res = repo.ecosystem.submit_assessment(
            repo=repo,
            student_id=req.student_id,
            assessment_id=assessment_id,
            answers=req.answers,
        )
        repo.sync_aux_tables_to_postgres()
        return res
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@ecosystem_router.get("/agents/assessments/{student_id}")
def list_student_assessments(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    items = repo.ecosystem.list_assessments(student_id)
    return {"student_id": student_id, "count": len(items), "assessments": items}


@ecosystem_router.get("/agents/learning-gaps/{student_id}")
def get_student_learning_gaps(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    return repo.ecosystem.analyze_learning_gaps(repo, student_id)


@ecosystem_router.post("/agents/study-plan/adapt/{student_id}")
def adapt_student_study_plan(
    student_id: str,
    req: Optional[StudyPlanAdaptRequest] = None,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    hours = req.available_daily_hours if req else None
    return repo.ecosystem.adapt_study_plan_for_gaps(repo, student_id, available_daily_hours=hours)


@ecosystem_router.get("/agents/progress-recommendations/{student_id}")
def get_student_progress_recommendations(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    return repo.ecosystem.get_progress_and_recommendations(repo, student_id)


@ecosystem_router.post("/agents/workflow/run")
def run_connected_agent_workflow(
    req: WorkflowRunRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(req.student_id, authorization, x_sparkminds_token)
    res = repo.ecosystem.run_connected_learning_cycle(
        repo=repo,
        student_id=req.student_id,
        subject=req.subject,
        topic=req.topic,
        goal=req.goal,
    )
    repo.sync_aux_tables_to_postgres()
    return res


@ecosystem_router.get("/agents/logs/{student_id}")
def get_agent_execution_logs(
    student_id: str,
    limit: int = Query(default=25, ge=1, le=100),
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    logs = repo.ecosystem.get_agent_execution_logs(student_id, limit=limit)
    return {"student_id": student_id, "count": len(logs), "logs": logs}


class GuidedLessonGenerateRequest(BaseModel):
    student_id: str
    subject: str = "Mathematics"
    topic: str = "Core Concepts"
    preferred_language: Optional[str] = None


class GuidedLessonCompleteRequest(BaseModel):
    student_id: str
    lesson_id: str
    subject: str
    topic: str
    correct_count: int = Field(default=0, ge=0)
    total_interactive_steps: int = Field(default=1, ge=1)


@ecosystem_router.post("/agents/lessons/generate")
def create_guided_interactive_lesson(
    req: GuidedLessonGenerateRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(req.student_id, authorization, x_sparkminds_token)
    return generate_guided_lesson(
        repo=repo,
        student_id=req.student_id,
        subject=req.subject,
        topic=req.topic,
        preferred_language=req.preferred_language,
    )


@ecosystem_router.post("/agents/lessons/complete")
def finish_guided_interactive_lesson(
    req: GuidedLessonCompleteRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(req.student_id, authorization, x_sparkminds_token)
    res = complete_guided_lesson(
        repo=repo,
        student_id=req.student_id,
        lesson_id=req.lesson_id,
        subject=req.subject,
        topic=req.topic,
        correct_count=req.correct_count,
        total_interactive_steps=req.total_interactive_steps,
    )
    repo.sync_aux_tables_to_postgres()
    return res


# ============================================================================
# 2. DOCUMENT LEARNING & RETRIEVAL-AUGMENTED GENERATION (RAG)
# ============================================================================

class DocumentUploadJsonRequest(BaseModel):
    filename: str
    subject: str = "General"
    content_base64: Optional[str] = None
    text_content: Optional[str] = None
    content_type: str = "text/plain"


class DocumentAskRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2000)
    doc_id: Optional[str] = None


class DocumentQuizRequest(BaseModel):
    question_count: int = Field(default=4, ge=1, le=8)


@ecosystem_router.post("/students/{student_id}/documents/upload")
def upload_learning_document_json(
    student_id: str,
    req: DocumentUploadJsonRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    raw_bytes = b""
    if req.content_base64:
        try:
            raw_bytes = b64decode(req.content_base64.split(",")[-1].strip())
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 document payload.")
    elif req.text_content is not None:
        raw_bytes = req.text_content.encode("utf-8")
    else:
        raise HTTPException(status_code=422, detail="Provide content_base64 or text_content.")

    try:
        doc = repo.document_rag.upload_and_index_document(
            student_id=student_id,
            filename=req.filename,
            content_bytes=raw_bytes,
            content_type=req.content_type,
            subject=req.subject,
        )
        repo.gamification.record_activity(
            student_id=student_id,
            activity_type="document_studied",
            subject=req.subject,
            topic=req.filename,
        )
        repo.sync_aux_tables_to_postgres()
        return {"status": "document_indexed", "document": doc}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@ecosystem_router.post("/students/{student_id}/documents/upload-file")
async def upload_learning_document_multipart(
    student_id: str,
    file: UploadFile = File(...),
    subject: str = Form(default="General"),
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    raw_bytes = await file.read()
    try:
        doc = repo.document_rag.upload_and_index_document(
            student_id=student_id,
            filename=file.filename or "document.txt",
            content_bytes=raw_bytes,
            content_type=file.content_type or "application/octet-stream",
            subject=subject,
        )
        repo.gamification.record_activity(
            student_id=student_id,
            activity_type="document_studied",
            subject=subject,
            topic=file.filename or "document",
        )
        repo.sync_aux_tables_to_postgres()
        return {"status": "document_indexed", "document": doc}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@ecosystem_router.get("/students/{student_id}/documents")
def list_student_learning_documents(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    docs = repo.document_rag.list_documents(student_id)
    return {"student_id": student_id, "count": len(docs), "documents": docs}


@ecosystem_router.post("/students/{student_id}/documents/ask")
def ask_student_learning_documents(
    student_id: str,
    req: DocumentAskRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    student = repo.students.get(student_id, {})
    lang = (student.get("language_preferences") or {}).get("preferred_explanation_language", "English")
    grade = int(student.get("current_grade", 8))
    return repo.document_rag.answer_question_from_documents(
        student_id=student_id,
        question=req.question,
        doc_id=req.doc_id,
        preferred_language=lang,
        grade=grade,
    )


@ecosystem_router.post("/students/{student_id}/documents/{doc_id}/generate-quiz")
def generate_quiz_from_uploaded_document(
    student_id: str,
    doc_id: str,
    req: Optional[DocumentQuizRequest] = None,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    q_count = req.question_count if req else 4
    try:
        res = repo.ecosystem.create_assessment(
            repo=repo,
            student_id=student_id,
            subject="Document Study",
            assessment_kind="DOCUMENT_QUIZ",
            question_count=q_count,
            doc_id=doc_id,
        )
        repo.sync_aux_tables_to_postgres()
        return res
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ============================================================================
# 3. REAL GAMIFICATION, STREAKS, POINTS & BADGES
# ============================================================================

class GamificationActivityRequest(BaseModel):
    activity_type: str = "study_task_completed"
    subject: Optional[str] = None
    topic: Optional[str] = None
    points: Optional[int] = None
    activity_date: Optional[str] = None


@ecosystem_router.get("/students/{student_id}/gamification")
def get_student_gamification(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    return repo.gamification.get_student_gamification_summary(student_id)


@ecosystem_router.post("/students/{student_id}/gamification/activity")
def log_student_gamification_activity(
    student_id: str,
    req: GamificationActivityRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    res = repo.gamification.record_activity(
        student_id=student_id,
        activity_type=req.activity_type,
        subject=req.subject,
        topic=req.topic,
        points=req.points,
        activity_date=req.activity_date,
    )
    repo.sync_aux_tables_to_postgres()
    return res


# ============================================================================
# 4. MOBILE PUSH NOTIFICATIONS (VAPID) & NOTIFICATION CENTRE
# ============================================================================

class PushSubscribeRequest(BaseModel):
    endpoint: str
    p256dh: str
    auth: str
    user_agent: str = ""


class PushUnsubscribeRequest(BaseModel):
    endpoint: Optional[str] = None


@ecosystem_router.get("/notifications/vapid-public-key")
def get_vapid_public_key():
    return repo.notifications.get_vapid_public_key()


@ecosystem_router.post("/students/{student_id}/notifications/subscribe")
def subscribe_student_push(
    student_id: str,
    req: PushSubscribeRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    try:
        sub = repo.notifications.save_subscription(
            student_id=student_id,
            endpoint=req.endpoint,
            p256dh=req.p256dh,
            auth_secret=req.auth,
            user_agent=req.user_agent,
        )
        prefs = repo.get_or_create_reminder_preferences(student_id)
        prefs.push_notifications_enabled = True
        prefs.android_notifications_enabled = True
        prefs.android_notifications_permission = "granted"
        prefs.android_permission_status = "granted"
        repo.reminder_preferences[student_id] = prefs
        repo._persist_to_disk()
        return sub
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@ecosystem_router.delete("/students/{student_id}/notifications/unsubscribe")
def unsubscribe_student_push(
    student_id: str,
    req: Optional[PushUnsubscribeRequest] = None,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    endpoint = req.endpoint if req else None
    res = repo.notifications.remove_subscription(student_id, endpoint=endpoint)
    if not repo.notifications.list_subscriptions(student_id):
        prefs = repo.get_or_create_reminder_preferences(student_id)
        prefs.push_notifications_enabled = False
        repo.reminder_preferences[student_id] = prefs
        repo._persist_to_disk()
    return res


@ecosystem_router.get("/students/{student_id}/notifications/centre")
def get_student_notification_centre(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    prefs = repo.get_or_create_reminder_preferences(student_id).model_dump()
    centre = repo.notifications.list_notifications(student_id)
    subs = repo.notifications.list_subscriptions(student_id)
    return {
        **centre,
        "preferences": prefs,
        "active_push_subscriptions_count": len(subs),
        "vapid_public_key": repo.notifications.get_vapid_public_key()["vapid_public_key"],
    }


@ecosystem_router.post("/students/{student_id}/notifications/generate-personalized")
def generate_personalized_notifications(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    prefs = repo.get_or_create_reminder_preferences(student_id).model_dump()
    pending_hws = [h.model_dump() for h in repo.list_homeworks(student_id) if h.status != "Completed"]
    gaps = repo.ecosystem.analyze_learning_gaps(repo, student_id)
    weak_topics = gaps["needs_help"] + gaps["partially_understood"]
    plan = repo.get_or_create_study_plan(student_id)
    pending_tasks = [t.model_dump() for t in plan.daily_timetable if not t.completed]
    due_revs = [r.model_dump() for r in repo.list_revision_cards(student_id) if not r.completed_today]
    gamif = repo.gamification.get_student_gamification_summary(student_id)

    created = repo.notifications.generate_personalized_notifications_from_real_data(
        student_id=student_id,
        preferences=prefs,
        pending_homeworks=pending_hws,
        weak_topics=weak_topics,
        pending_study_tasks=pending_tasks,
        due_revisions=due_revs,
        gamification_summary=gamif,
    )
    return {"student_id": student_id, "generated_count": len(created), "notifications": created}


@ecosystem_router.patch("/students/{student_id}/notifications/{notification_id}/read")
def mark_notification_read(
    student_id: str,
    notification_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    updated = repo.notifications.mark_read(student_id, notification_id)
    return {"status": "marked_read" if updated else "not_found", "notification_id": notification_id}


@ecosystem_router.post("/students/{student_id}/notifications/mark-all-read")
def mark_all_notifications_read(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    count = repo.notifications.mark_all_read(student_id)
    return {"status": "all_marked_read", "updated_count": count}


@ecosystem_router.get("/students/{student_id}/notifications/preferences")
def get_notification_preferences(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    return repo.get_or_create_reminder_preferences(student_id).model_dump()


@ecosystem_router.put("/students/{student_id}/notifications/preferences")
def update_notification_preferences(
    student_id: str,
    prefs: ReminderPreferences,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    saved = repo.update_reminder_preferences(student_id, prefs)
    return saved.model_dump()
