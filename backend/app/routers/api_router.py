"""
SparkMinds AI — REST API Endpoints for All Modules (Phases 2–9)
"""
from base64 import b64decode
from datetime import datetime, timezone
import hmac
import os
from typing import Any, Dict, List, Literal, Optional
from fastapi import APIRouter, Cookie, Header, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.core.account_policy import (
    DUPLICATE_VERIFIED_EMAIL_MESSAGE,
    UNDER_8_PARENT_HELP_MESSAGE,
    DuplicateUsernameError,
    DuplicateVerifiedEmailError,
    EmailDeliveryError,
    EmailVerificationError,
    RateLimitExceededError,
    ResendCooldownError,
)
from app.core.config import SUPPORTED_LANGUAGES
from app.core.repository import repo
from app.curriculum_data.india_curriculum import (
    INDIAN_STATES,
    ONBOARDING_14_CHALLENGES,
    ONBOARDING_9_GOALS,
    SCHOOL_BOARDS,
    get_subjects_for_grade_and_board,
)
from app.models.schemas import (
    AnnualProgressionRequest,
    DailyActivityUpdateRequest,
    DailyScheduleCheckInRequest,
    ExamGenerateRequest,
    ExamMarkEntryRequest,
    ExamSubjectUpsertRequest,
    ExamSubmissionRequest,
    HomeworkCreateRequest,
    HomeworkStatusUpdateRequest,
    LanguagePreferences,
    OnboardingSubmission,
    ParentalConsentVerificationRequest,
    ProjectGenerateRequest,
    ProjectMilestoneUpdateRequest,
    ReminderPreferences,
    ReminderStatusUpdateRequest,
    RevisionGenerateRequest,
    RevisionReviewUpdateRequest,
    StudyPlanGenerateRequest,
    StudyTaskEditRequest,
)
from app.agents.orchestrator import orchestrator
from app.agents.chat_tutor import (
    ChatProviderError,
    ChatProviderNotConfigured,
    ConversationNotFound,
    chat_tutor_engine,
    is_provider_configured,
)
from app.core.config import settings
from app.agents.state_graph_orchestrator import (
    StartTutorSessionRequest,
    SubmitStudentAttemptRequest,
    state_graph_orchestrator,
)

router = APIRouter(prefix="/api")


# ----------------------------------------------------------------------------
# 1. AUTHENTICATION, MULTI-DEVICE CLOUD SYNC & STUDENT PROFILE
# ----------------------------------------------------------------------------

class AuthRegisterRequest(BaseModel):
    student_id: Optional[str] = None
    full_name: str
    age: int = 12
    grade: int = 7
    school_board: Optional[str] = "CBSE"
    date_of_birth: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    email_or_username: Optional[str] = None
    email_verification_token: Optional[str] = None
    strict_registration: bool = False
    password_or_pin: Optional[str] = None
    device_name: str = "Web Browser"


class AuthEmailSendCodeRequest(BaseModel):
    email: str
    purpose: Literal["registration", "recovery"] = "registration"


class AuthEmailVerifyCodeRequest(BaseModel):
    email: str
    code: str
    purpose: Literal["registration", "recovery"] = "registration"


class AuthLoginRequest(BaseModel):
    identifier: str
    password_or_pin: Optional[str] = None
    device_name: str = "Web Browser"


class AuthLogoutRequest(BaseModel):
    session_token: Optional[str] = None
    refresh_token: Optional[str] = None
    student_id: Optional[str] = None


class AuthRefreshRequest(BaseModel):
    refresh_token: Optional[str] = None
    session_token: Optional[str] = None
    device_name: Optional[str] = None


class AuthRevokeSessionsRequest(BaseModel):
    target_token: Optional[str] = None
    revoke_all_other: bool = False


class AuthRecoverInitRequest(BaseModel):
    identifier: str


class AuthRecoverRequest(BaseModel):
    identifier: str
    recovery_proof: str
    new_password_or_pin: str
    device_name: str = "Web Browser"


ACCESS_COOKIE_NAME = "sparkminds_access_token"
REFRESH_COOKIE_NAME = "sparkminds_refresh_token"
ACCESS_COOKIE_MAX_AGE = 60 * 60 * 24  # 24 hours
REFRESH_COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days


def _is_secure_cookie_context(request: Optional[Request]) -> bool:
    if os.getenv("SPARKMINDS_ENV", "").strip().lower() == "production":
        return True
    if request is None:
        return False
    forwarded_proto = (request.headers.get("x-forwarded-proto") or "").strip().lower()
    return request.url.scheme == "https" or forwarded_proto == "https"


def _set_auth_cookies(
    response: Response,
    request: Optional[Request],
    access_token: Optional[str],
    refresh_token: Optional[str] = None,
) -> None:
    secure_flag = _is_secure_cookie_context(request)
    if access_token:
        response.set_cookie(
            key=ACCESS_COOKIE_NAME,
            value=access_token,
            httponly=True,
            secure=secure_flag,
            samesite="lax",
            path="/",
            max_age=ACCESS_COOKIE_MAX_AGE,
        )
    if refresh_token:
        response.set_cookie(
            key=REFRESH_COOKIE_NAME,
            value=refresh_token,
            httponly=True,
            secure=secure_flag,
            samesite="lax",
            path="/api/auth",
            max_age=REFRESH_COOKIE_MAX_AGE,
        )


def _clear_auth_cookies(response: Response, request: Optional[Request]) -> None:
    secure_flag = _is_secure_cookie_context(request)
    response.delete_cookie(
        key=ACCESS_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=secure_flag,
        samesite="lax",
    )
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path="/api/auth",
        httponly=True,
        secure=secure_flag,
        samesite="lax",
    )


def _extract_client_ip(request: Optional[Request]) -> str:
    if request is None:
        return "local"
    xff = (request.headers.get("x-forwarded-for") or "").strip()
    if xff:
        return xff.split(",")[0].strip() or "unknown"
    return request.client.host if request.client else "unknown"


@router.post("/auth/email/send-code")
def send_email_verification_code(req: AuthEmailSendCodeRequest, request: Request):
    client_ip = _extract_client_ip(request)
    norm_email = (req.email or "").strip().lower()
    try:
        # Multi-layer abuse protection: per-IP global cap + per-IP-and-email cap
        repo.rate_limiter.check_and_record(
            f"email_code_ip:{client_ip}",
            max_attempts=30,
            window_seconds=900,
        )
        repo.rate_limiter.check_and_record(
            f"email_code:{client_ip}:{norm_email}",
            max_attempts=5,
            window_seconds=900,
        )
        if req.purpose == "registration" and repo.is_verified_email_registered(norm_email):
            raise DuplicateVerifiedEmailError(DUPLICATE_VERIFIED_EMAIL_MESSAGE)

        result = repo.email_verification.create_verification_code(
            email=req.email, purpose=req.purpose
        )
        repo.sync_aux_tables_to_postgres()
        return {"status": "verification_code_sent", **result}
    except DuplicateVerifiedEmailError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except ResendCooldownError as exc:
        return JSONResponse(
            status_code=429,
            headers={"Retry-After": str(exc.retry_after_seconds)},
            content={
                "detail": str(exc),
                "retry_after_seconds": exc.retry_after_seconds,
            },
        )
    except RateLimitExceededError as exc:
        raise HTTPException(status_code=429, detail=str(exc))
    except EmailVerificationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except EmailDeliveryError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.post("/auth/email/verify-code")
def verify_email_verification_code(req: AuthEmailVerifyCodeRequest, request: Request):
    client_ip = _extract_client_ip(request)
    norm_email = (req.email or "").strip().lower()
    try:
        repo.rate_limiter.check_and_record(
            f"email_verify:{client_ip}:{norm_email}",
            max_attempts=15,
            window_seconds=900,
        )
        result = repo.email_verification.verify_code(
            email=req.email, code=req.code, purpose=req.purpose
        )
        repo.sync_aux_tables_to_postgres()
        return {"status": "email_verified", **result}
    except RateLimitExceededError as exc:
        raise HTTPException(status_code=429, detail=str(exc))
    except EmailVerificationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/auth/register")
def register_or_login_student(req: AuthRegisterRequest, request: Request, response: Response):
    client_ip = _extract_client_ip(request)
    try:
        bundle = repo.authenticate_or_register_account(
            student_id=req.student_id or "",
            full_name=req.full_name,
            age=req.age,
            grade=req.grade,
            date_of_birth=req.date_of_birth,
            email_or_username=req.email_or_username,
            password_or_pin=req.password_or_pin,
            device_name=req.device_name,
            username=req.username,
            email=req.email,
            email_verification_token=req.email_verification_token,
            strict_registration=req.strict_registration,
            rate_limit_key=client_ip,
            school_board=req.school_board,
        )
    except DuplicateUsernameError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except DuplicateVerifiedEmailError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except RateLimitExceededError as exc:
        raise HTTPException(status_code=429, detail=str(exc))
    except EmailVerificationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

    access_token = str(bundle.get("session_token") or "") or None
    refresh_token = str(bundle.get("refresh_token") or "") or None
    _set_auth_cookies(response, request, access_token, refresh_token)

    student = bundle["student"]
    under_8 = bool(student.get("requires_parental_assistance", False))  # type: ignore
    consent_verified = bool(student.get("parent_consent_verified", True))  # type: ignore
    under_8_notice = UNDER_8_PARENT_HELP_MESSAGE if under_8 else None
    return {
        "status": "authenticated" if not (under_8 and not consent_verified) else "parental_assistance_required",
        "requires_parental_assistance": under_8,
        "parent_consent_verified": consent_verified,
        "child_safety_message": under_8_notice,
        "student": student,
        "session_token": access_token,
        "refresh_token": refresh_token,
        "cloud_sync_bundle": bundle,
    }


@router.post("/auth/login")
def login_student_across_devices(req: AuthLoginRequest, request: Request, response: Response):
    client_ip = _extract_client_ip(request)
    try:
        bundle = repo.login_student_account(
            identifier=req.identifier,
            password_or_pin=req.password_or_pin,
            device_name=req.device_name,
            rate_limit_key=client_ip,
        )
    except RateLimitExceededError as exc:
        raise HTTPException(status_code=429, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

    access_token = str(bundle.get("session_token") or "") or None
    refresh_token = str(bundle.get("refresh_token") or "") or None
    _set_auth_cookies(response, request, access_token, refresh_token)

    student = bundle["student"]
    under_8 = bool(student.get("requires_parental_assistance", False))  # type: ignore
    consent_verified = bool(student.get("parent_consent_verified", True))  # type: ignore
    return {
        "status": "authenticated" if not (under_8 and not consent_verified) else "parental_assistance_required",
        "requires_parental_assistance": under_8,
        "parent_consent_verified": consent_verified,
        "child_safety_message": UNDER_8_PARENT_HELP_MESSAGE if under_8 else None,
        "student": student,
        "session_token": access_token,
        "refresh_token": refresh_token,
        "cloud_sync_bundle": bundle,
    }


@router.get("/auth/session")
def get_active_device_session(
    request: Request,
    response: Response,
    session_token: Optional[str] = Query(default=None),
    student_id: Optional[str] = Query(default=None),
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
    x_sparkminds_refresh_token: Optional[str] = Header(default=None),
    sparkminds_access_token: Optional[str] = Cookie(default=None),
    sparkminds_refresh_token: Optional[str] = Cookie(default=None),
):
    explicit_token = session_token or x_sparkminds_token
    if not explicit_token and authorization and authorization.lower().startswith("bearer "):
        explicit_token = authorization[7:].strip()
    # Note: auth_cookie_header_bridge may copy sparkminds_access_token into x-sparkminds-token;
    # detect whether the caller supplied an explicit token distinct from the cookie.
    cookie_access = (sparkminds_access_token or "").strip() or None
    caller_explicit_differs = bool(
        session_token
        or (
            explicit_token
            and cookie_access
            and explicit_token.strip() != cookie_access
        )
    )
    token = explicit_token or cookie_access
    refresh_tok = (x_sparkminds_refresh_token or sparkminds_refresh_token or "").strip() or None

    try:
        bundle = repo.get_session_cloud_sync(session_token=token, student_id=student_id)
        return {
            "status": "authenticated",
            "session_token": bundle.get("session_token") or token,
            "student": bundle["student"],
            "cloud_sync_bundle": bundle,
        }
    except ValueError as exc:
        err_lower = str(exc).lower()
        # Never silently refresh when:
        # 1. Caller explicitly queried a specific/different session token (e.g. checking revoked/expired token)
        # 2. The session was explicitly logged out or mismatched another student
        can_auto_refresh = (
            bool(refresh_tok)
            and not caller_explicit_differs
            and "logged out" not in err_lower
            and "does not match the requested student" not in err_lower
        )
        if can_auto_refresh:
            try:
                refreshed = repo.refresh_device_session(refresh_token=refresh_tok)
                if student_id and str(refreshed["student_id"]) != student_id.strip():
                    raise HTTPException(
                        status_code=403,
                        detail="Access denied: Session token does not match the requested student account.",
                    )
                new_access = str(refreshed["session_token"])
                new_refresh = str(refreshed["refresh_token"])
                _set_auth_cookies(response, request, new_access, new_refresh)
                ref_bundle = refreshed["cloud_sync_bundle"]
                return {
                    "status": "authenticated",
                    "session_refreshed": True,
                    "session_token": new_access,
                    "refresh_token": new_refresh,
                    "student": ref_bundle["student"],
                    "cloud_sync_bundle": ref_bundle,
                }
            except HTTPException:
                raise
            except ValueError:
                pass
        raise HTTPException(status_code=401, detail=str(exc))


@router.get("/auth/sessions")
def list_student_active_sessions(
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
    session_token: Optional[str] = Query(default=None),
    sparkminds_access_token: Optional[str] = Cookie(default=None),
):
    token = session_token or x_sparkminds_token
    if not token and authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    if not token and sparkminds_access_token:
        token = sparkminds_access_token.strip()
    try:
        bundle = repo.get_session_cloud_sync(session_token=token)
        sid = str(bundle["student_id"])
        return {"student_id": sid, "sessions": repo.list_active_sessions(sid)}
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))


@router.post("/auth/sessions/revoke")
def revoke_student_sessions(
    req: AuthRevokeSessionsRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
    sparkminds_access_token: Optional[str] = Cookie(default=None),
):
    token = x_sparkminds_token
    if not token and authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    if not token and sparkminds_access_token:
        token = sparkminds_access_token.strip()
    try:
        bundle = repo.get_session_cloud_sync(session_token=token)
        sid = str(bundle["student_id"])
        return repo.revoke_sessions(
            student_id=sid,
            target_token=req.target_token,
            revoke_all_other=req.revoke_all_other,
            current_token=token,
        )
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))


@router.post("/auth/logout")
def logout_student_session(
    req: AuthLogoutRequest,
    request: Request,
    response: Response,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
    x_sparkminds_refresh_token: Optional[str] = Header(default=None),
    sparkminds_access_token: Optional[str] = Cookie(default=None),
    sparkminds_refresh_token: Optional[str] = Cookie(default=None),
):
    token = req.session_token or x_sparkminds_token
    if not token and authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    if not token and sparkminds_access_token:
        token = sparkminds_access_token.strip()
    refresh_tok = (
        req.refresh_token or x_sparkminds_refresh_token or sparkminds_refresh_token or ""
    ).strip() or None
    _clear_auth_cookies(response, request)
    return repo.logout_session(
        session_token=token,
        refresh_token=refresh_tok,
        student_id=req.student_id,
    )


@router.post("/auth/recover/request")
def request_account_recovery_endpoint(req: AuthRecoverInitRequest):
    try:
        return repo.request_account_recovery(req.identifier)
    except ResendCooldownError as exc:
        return JSONResponse(
            status_code=429,
            headers={"Retry-After": str(exc.retry_after_seconds)},
            content={
                "detail": str(exc),
                "retry_after_seconds": exc.retry_after_seconds,
            },
        )
    except RateLimitExceededError as exc:
        raise HTTPException(status_code=429, detail=str(exc))


@router.post("/auth/recover")
def recover_student_account_endpoint(req: AuthRecoverRequest, request: Request, response: Response):
    try:
        result = repo.recover_student_account(
            identifier=req.identifier,
            recovery_proof=req.recovery_proof,
            new_password_or_pin=req.new_password_or_pin,
            device_name=req.device_name,
        )
        _set_auth_cookies(
            response,
            request,
            str(result.get("session_token") or "") or None,
            str(result.get("refresh_token") or "") or None,
        )
        return result
    except RateLimitExceededError as exc:
        raise HTTPException(status_code=429, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


def verify_admin_access(x_sparkminds_admin_key: Optional[str] = None) -> None:
    """
    Protects administrative audit/backup/restore endpoints in production.
    Requires X-SparkMinds-Admin-Key header matching SPARKMINDS_ADMIN_KEY (constant-time).
    In production, rejects requests with HTTP 403 if SPARKMINDS_ADMIN_KEY is not configured.
    """
    if os.getenv("SPARKMINDS_ENV", "").strip().lower() != "production":
        return
    configured_key = os.getenv("SPARKMINDS_ADMIN_KEY", "").strip()
    supplied_key = (x_sparkminds_admin_key or "").strip()
    if not configured_key or not supplied_key or not hmac.compare_digest(supplied_key, configured_key):
        raise HTTPException(
            status_code=403,
            detail="Administrator authorization is required for this endpoint.",
        )


@router.get("/admin/audit/duplicate-accounts")
def run_non_destructive_duplicate_audit(
    x_sparkminds_admin_key: Optional[str] = Header(default=None),
):
    verify_admin_access(x_sparkminds_admin_key)
    return repo.run_duplicate_account_audit()


@router.post("/auth/parental-consent")
def verify_parent_or_guardian_consent(req: ParentalConsentVerificationRequest):
    try:
        result = repo.verify_under8_parental_consent(req)
        repo.sync_aux_tables_to_postgres()
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/auth/session/refresh")
def refresh_active_device_session(
    request: Request,
    response: Response,
    req: Optional[AuthRefreshRequest] = None,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
    x_sparkminds_refresh_token: Optional[str] = Header(default=None),
    session_token: Optional[str] = Query(default=None),
    sparkminds_access_token: Optional[str] = Cookie(default=None),
    sparkminds_refresh_token: Optional[str] = Cookie(default=None),
):
    """
    Rotates and issues fresh HMAC-signed access + refresh tokens using either:
    1. A valid non-revoked refresh token (from HttpOnly cookie, header, or body), OR
    2. An already valid active access session token.
    Rejects genuinely expired or revoked sessions with HTTP 401.
    """
    refresh_tok = (
        (req.refresh_token if req else None)
        or x_sparkminds_refresh_token
        or sparkminds_refresh_token
        or ""
    ).strip() or None

    access_tok = (req.session_token if req else None) or session_token or x_sparkminds_token
    if not access_tok and authorization and authorization.lower().startswith("bearer "):
        access_tok = authorization[7:].strip()
    if not access_tok and sparkminds_access_token:
        access_tok = sparkminds_access_token.strip()

    try:
        refreshed = repo.refresh_device_session(
            refresh_token=refresh_tok,
            session_token=access_tok,
            device_name=req.device_name if req else None,
        )
    except ValueError as exc:
        _clear_auth_cookies(response, request)
        raise HTTPException(status_code=401, detail=str(exc))

    new_access = str(refreshed["session_token"])
    new_refresh = str(refreshed["refresh_token"])
    _set_auth_cookies(response, request, new_access, new_refresh)
    return {
        "status": "refreshed",
        "student_id": refreshed["student_id"],
        "student": refreshed["cloud_sync_bundle"].get("student"),
        "session_token": new_access,
        "refresh_token": new_refresh,
        "cloud_sync_bundle": refreshed["cloud_sync_bundle"],
    }


def verify_student_access(
    student_id: str,
    authorization: Optional[str] = None,
    x_sparkminds_token: Optional[str] = None,
    session_token: Optional[str] = None,
) -> None:
    """
    Verifies that an authenticated request belongs to the requested student and prevents
    cross-user leakage, while seamlessly validating HMAC-signed spark_sess_v2.* tokens
    (supplied via headers or HttpOnly cookies bridged by middleware) and sliding-refreshing
    active sessions so students are never spuriously logged out.
    """
    public_representative_students = {
        "stu_aarav_g7",
        "stu_ananya_g1",
        "stu_diya_g4",
        "stu_karthik_g10",
        "stu_riya_g12",
        "stu_learner",
    }
    token = session_token or x_sparkminds_token
    if not token and authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    if token:
        sess = repo.resolve_and_validate_session(token)
        if not sess:
            if student_id not in public_representative_students:
                raise HTTPException(status_code=401, detail="Session expired or invalid. Please sign in.")
            return
        sess_student_id = str(sess.get("student_id", ""))
        if sess_student_id != student_id and student_id not in public_representative_students:
            raise HTTPException(
                status_code=403,
                detail="Access denied: You cannot access or modify another student's private records.",
            )
    else:
        # In production, enforce authentication on every registered private student account
        if (
            os.getenv("SPARKMINDS_ENV", "").strip().lower() == "production"
            and student_id not in public_representative_students
            and student_id in repo.students
        ):
            raise HTTPException(
                status_code=401,
                detail="Authentication required to access private student records. Please sign in.",
            )


@router.get("/students/{student_id}")
def get_student_master_profile(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
    session_token: Optional[str] = Query(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token, session_token)
    repo._ensure_student_loaded(student_id)
    student = repo.students.get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    years = repo.academic_years.get(student_id, [])
    active_year = next((y.model_dump() for y in years if y.status == "ACTIVE"), None)
    return {
        "student": repo._sanitize_student_public(student),
        "active_year_profile": active_year,
        "academic_years_count": len(years),
    }


# ----------------------------------------------------------------------------
# 2. CURRICULUM & ONBOARDING OPTIONS
# ----------------------------------------------------------------------------

@router.get("/curriculum/options")
def get_curriculum_options(
    grade: int = Query(default=7, ge=1, le=12),
    board: str = Query(default="CBSE"),
    state: Optional[str] = Query(default=None),
):
    subjects = get_subjects_for_grade_and_board(grade=grade, board=board, state=state)
    return {
        "grade": grade,
        "board": board,
        "state": state,
        "boards": SCHOOL_BOARDS,
        "indian_states": INDIAN_STATES,
        "subjects": subjects,
        "challenges_14": ONBOARDING_14_CHALLENGES,
        "goals_9": ONBOARDING_9_GOALS,
        "supported_languages": SUPPORTED_LANGUAGES,
    }


class CloudSyncRequest(BaseModel):
    session_token: Optional[str] = None
    study_plan_task_update: Optional[Dict[str, Any]] = None
    homework_item: Optional[Dict[str, Any]] = None
    preferences_update: Optional[Dict[str, Any]] = None
    profile_update: Optional[Dict[str, Any]] = None


class StudentProfileUpdateRequest(BaseModel):
    age: Optional[int] = None
    date_of_birth: Optional[str] = None
    full_name: Optional[str] = None
    school_board: Optional[str] = None
    state_name: Optional[str] = None
    current_grade: Optional[int] = None
    parent_consent_verified: Optional[bool] = None
    parent_verification_details: Optional[Dict[str, Any]] = None


@router.post("/onboarding/submit")
def submit_seven_step_onboarding(
    submission: OnboardingSubmission,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(submission.student_id, authorization, x_sparkminds_token)
    try:
        result = repo.save_onboarding(submission)
        bundle = repo.get_cloud_sync_bundle(submission.student_id)
        return {"status": "onboarding_saved", "cloud_sync_bundle": bundle, **result}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.patch("/students/{student_id}/profile")
def update_student_profile(
    student_id: str,
    req: StudentProfileUpdateRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
    session_token: Optional[str] = Query(default=None),
):
    token = session_token or x_sparkminds_token
    verify_student_access(student_id, authorization, x_sparkminds_token, token)
    try:
        updated_student = repo.update_student_profile(
            student_id=student_id,
            age=req.age,
            date_of_birth=req.date_of_birth,
            full_name=req.full_name,
            school_board=req.school_board,
            state_name=req.state_name,
            current_grade=req.current_grade,
            parent_consent_verified=req.parent_consent_verified,
            parent_verification_details=req.parent_verification_details,
        )
        bundle = repo.get_cloud_sync_bundle(student_id, session_token=token)
        return {
            "status": "profile_updated",
            "student": updated_student,
            "cloud_sync_bundle": bundle,
        }
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/students/{student_id}/cloud-sync")
def sync_student_cloud_data(
    student_id: str,
    req: CloudSyncRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
    session_token: Optional[str] = Query(default=None),
):
    token = req.session_token or session_token or x_sparkminds_token
    verify_student_access(student_id, authorization, x_sparkminds_token, token)
    if req.study_plan_task_update:
        task_id = str(req.study_plan_task_update.get("task_id", ""))
        completed = req.study_plan_task_update.get("completed", True)
        if task_id:
            repo.toggle_study_task(student_id, task_id, completed=completed)
    if req.profile_update:
        repo.update_student_profile(
            student_id=student_id,
            age=req.profile_update.get("age"),
            date_of_birth=req.profile_update.get("date_of_birth"),
            full_name=req.profile_update.get("full_name"),
            school_board=req.profile_update.get("school_board"),
            state_name=req.profile_update.get("state_name"),
            current_grade=req.profile_update.get("current_grade"),
            parent_consent_verified=req.profile_update.get("parent_consent_verified"),
            parent_verification_details=req.profile_update.get("parent_verification_details"),
        )
    return {
        "status": "synchronized",
        "cloud_sync_bundle": repo.get_cloud_sync_bundle(student_id, session_token=token),
    }


# ----------------------------------------------------------------------------
# 3. LANGUAGE PREFERENCES (4 SEPARATE SETTINGS)
# ----------------------------------------------------------------------------

@router.put("/students/{student_id}/languages")
def update_student_languages(
    student_id: str,
    prefs: LanguagePreferences,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    if not prefs.preferred_explanation_language.strip():
        raise HTTPException(
            status_code=422,
            detail="Preferred explanation language is mandatory.",
        )
    try:
        updated = repo.update_language_preferences(student_id, prefs)
        return {"status": "languages_updated", "student": updated}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ----------------------------------------------------------------------------
# 4. CENTRAL ORCHESTRATOR & AI LEARNING BUDDY
# ----------------------------------------------------------------------------

class BuddyInteractionRequest(BaseModel):
    student_id: str
    user_message: str
    subject_name: str = "Mathematics"
    interaction_mode: Literal["concept", "homework", "practice", "exam_prep", "project"] = "concept"
    hint_only_requested: bool = False
    temporary_language_override: Optional[str] = None
    temporary_secondary_language_override: Optional[str] = None


@router.post("/orchestrator/interact")
def interact_with_ai_buddy(
    req: BuddyInteractionRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(req.student_id, authorization, x_sparkminds_token)
    response = orchestrator.execute_workflow(
        student_id=req.student_id,
        user_message=req.user_message,
        subject_name=req.subject_name,
        interaction_mode=req.interaction_mode,
        hint_only_requested=req.hint_only_requested,
        temporary_language_override=req.temporary_language_override,
        temporary_secondary_language_override=req.temporary_secondary_language_override,
    )
    return response.model_dump()


# ----------------------------------------------------------------------------
# 4B. STATEFUL HOMEWORK TUTOR GRAPH ENGINE (REDESIGNED AGENTIC ARCHITECTURE)
# ----------------------------------------------------------------------------

@router.post("/tutor/session/start")
def start_stateful_tutor_session(
    req: StartTutorSessionRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    """
    Starts an interactive homework tutoring session:
    STUDENT REQUEST -> UNDERSTANDING AGENT -> LEARNING DIAGNOSIS AGENT -> TEACHING AGENT (Waits for Attempt).
    """
    verify_student_access(req.student_id, authorization, x_sparkminds_token)
    state = state_graph_orchestrator.start_homework_session(req)
    return state.model_dump()


@router.post("/tutor/session/turn")
def submit_student_tutor_turn(
    req: SubmitStudentAttemptRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    """
    Processes a student step attempt, progressive hint request, alternative explanation request,
    full solution request, or similar practice request:
    STUDENT ATTEMPT -> ASSESSMENT AGENT -> CONDITIONAL REMEDIATION / TEACHING AGENT -> LEARNING MEMORY UPDATE.
    """
    raw_existing = repo.tutor_sessions.get(req.session_id)
    if isinstance(raw_existing, dict) and raw_existing.get("student_id"):
        verify_student_access(str(raw_existing["student_id"]), authorization, x_sparkminds_token)
    try:
        state = state_graph_orchestrator.process_student_turn(req)
        return state.model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/tutor/session/{session_id}")
def get_tutor_session_state(
    session_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    raw = repo.tutor_sessions.get(session_id)
    if not raw:
        raise HTTPException(status_code=404, detail="Tutor session not found")
    if isinstance(raw, dict) and raw.get("student_id"):
        verify_student_access(str(raw["student_id"]), authorization, x_sparkminds_token)
    return raw


# ----------------------------------------------------------------------------
# 4C. REAL MULTI-TURN AI LEARNING BUDDY CHAT (LIVE LLM — NO SAMPLE ANSWERS)
# ----------------------------------------------------------------------------

class TutorChatRequest(BaseModel):
    student_id: str
    message: str = ""
    conversation_id: Optional[str] = None
    language_override: Optional[str] = None
    image_base64: Optional[str] = None
    image_mime_type: Optional[str] = None


def _chat_student_record(student_id: str) -> dict:
    student = repo.students.get(student_id)
    if not student:
        student = repo.register_or_get_student(student_id, "Student Learner")
    record = dict(student)
    record["student_id"] = student_id
    return record


@router.get("/tutor/chat/status")
def tutor_chat_status():
    """Reports whether a real AI provider is configured (never exposes the key)."""
    return {
        "provider": "google-gemini",
        "model": settings.GEMINI_MODEL,
        "configured": is_provider_configured(),
    }


@router.post("/tutor/chat")
def tutor_chat_send(
    req: TutorChatRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    """
    Sends the student's exact message plus recent conversation history and live shared
    student learning context (weak topics, assessments, language, uploaded docs) to the real AI model.
    Errors are surfaced honestly, never replaced by sample text.
    """
    verify_student_access(req.student_id, authorization, x_sparkminds_token)
    student = _chat_student_record(req.student_id)
    tutor_ctx = repo.ecosystem.build_tutor_context_block(
        repo=repo, student_id=req.student_id, question=req.message
    )
    effective_message = (
        tutor_ctx["sanitized_question"] if tutor_ctx["prompt_injection_flagged"] else req.message
    )
    try:
        res = chat_tutor_engine.send_message(
            student=student,
            message=effective_message,
            conversation_id=req.conversation_id,
            language_override=req.language_override,
            image_base64=req.image_base64,
            image_mime_type=req.image_mime_type,
            personalized_context=tutor_ctx["context_instruction"],
        )
        repo.gamification.record_activity(
            student_id=req.student_id,
            activity_type="tutor_session",
            metadata={"conversation_id": res.get("conversation_id")},
        )
        return res
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ConversationNotFound:
        raise HTTPException(
            status_code=404,
            detail="This conversation was not found for your account. Please start a new conversation.",
        )
    except ChatProviderNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except ChatProviderError as exc:
        raise HTTPException(status_code=502, detail=f"{exc} No answer was generated — please retry.")


@router.get("/tutor/chat/{conversation_id}")
def tutor_chat_history(
    conversation_id: str,
    student_id: str = Query(...),
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    try:
        return {
            "conversation_id": conversation_id,
            "messages": chat_tutor_engine.get_messages(student_id, conversation_id),
        }
    except ConversationNotFound:
        raise HTTPException(status_code=404, detail="Conversation not found for this student")


@router.delete("/tutor/chat/{conversation_id}")
def tutor_chat_delete(
    conversation_id: str,
    student_id: str = Query(...),
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    chat_tutor_engine.delete_conversation(student_id, conversation_id)
    return {"deleted": True, "conversation_id": conversation_id}


@router.get("/students/{student_id}/learning-memory")
def get_student_learning_memory(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    """Returns all structured LearningMemoryRecords connected to the student's Academic Journey."""
    verify_student_access(student_id, authorization, x_sparkminds_token)
    memories = repo.learning_memories.get(student_id, [])
    return {
        "student_id": student_id,
        "count": len(memories),
        "records": [m.model_dump() for m in memories],
    }


# ----------------------------------------------------------------------------
# 5. PERMANENT ACADEMIC JOURNEY & HISTORICAL COMPARISON (G1–G12)
# ----------------------------------------------------------------------------

@router.get("/students/{student_id}/academic-journey")
def get_academic_journey(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
    session_token: Optional[str] = Query(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token, session_token)
    student = repo.students.get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    years = repo.academic_years.get(student_id, [])
    ups_and_downs = []
    for y in years:
        for ev in y.evidence_records:
            ups_and_downs.append(
                {
                    "grade": y.grade,
                    "academic_year": y.academic_year_label,
                    "subject": ev.subject_name,
                    "topic": ev.topic_name,
                    "evidence_type": ev.evidence_type,
                    "score_percentage": ev.score_percentage,
                    "qualitative_rating": ev.qualitative_rating,
                    "trend_indicator": ev.trend_indicator,
                    "notes": ev.notes,
                }
            )

    return {
        "student": student,
        "completed_and_active_years": [y.model_dump() for y in years],
        "ups_and_downs_analysis": ups_and_downs,
        "timeline_grades_1_to_12": [
            {
                "grade": g,
                "has_record": any(y.grade == g for y in years),
                "year_profile": next((y.model_dump() for y in years if y.grade == g), None),
            }
            for g in range(1, 13)
        ],
    }


# ----------------------------------------------------------------------------
# 6. ANNUAL ACADEMIC PROGRESSION
# ----------------------------------------------------------------------------

@router.post("/students/{student_id}/progression")
def promote_or_progress_student(
    student_id: str,
    req: AnnualProgressionRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    if student_id != req.student_id:
        raise HTTPException(status_code=400, detail="Mismatched student_id")
    try:
        return repo.process_annual_progression(req)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ----------------------------------------------------------------------------
# 7. PARENT DASHBOARD & AUTHORISED READ-ONLY ACCESS
# ----------------------------------------------------------------------------

class ParentActionRequest(BaseModel):
    parent_id: str
    action: Literal["VIEW_SUMMARY", "UPDATE_PARENT_LANGUAGE", "ATTEMPT_ALTER_SCORE"]
    preferred_parent_language: Optional[str] = None


@router.get("/parent/{parent_id}/child/{student_id}")
def get_parent_dashboard(parent_id: str, student_id: str):
    student = repo.students.get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if student.get("parent_id") != parent_id:
        raise HTTPException(
            status_code=403,
            detail="Child Safety & Privacy Guard: You are not authorised to view another student's academic records.",
        )

    years = repo.academic_years.get(student_id, [])
    progress_report = repo.get_academic_progress_report(student_id)
    homeworks = [h.model_dump() for h in repo.list_homeworks(student_id)]
    study_plan = repo.get_or_create_study_plan(student_id).model_dump()
    exams = [e.model_dump() for e in repo.list_mock_exams(student_id)]
    exam_marks = [m.model_dump() for m in repo.list_exam_marks(student_id)]
    reminder_prefs = repo.get_or_create_reminder_preferences(student_id).model_dump()
    notifications_info = repo.get_notifications_and_reminders(student_id)
    daily_schedule = repo.get_daily_schedule(student_id).model_dump()
    recurring_activities = [
        r.model_dump() for r in repo.recurring_activities.get(student_id, [])
    ]

    gamif = repo.gamification.get_student_gamification_summary(student_id)
    real_streak = gamif["current_streak_days"]
    parent_recs = [
        (
            f"Encourage {student.get('full_name', 'your child')} — they currently have a {real_streak}-day active learning streak."
            if real_streak > 0
            else f"Help {student.get('full_name', 'your child')} start a gentle daily study habit with a short 15-minute concept review."
        ),
        "Support regular practice on priority topics using the step-by-step AI Learning Buddy in their preferred language.",
        "Check the upcoming Exam Study Planner schedule and ensure healthy rest breaks between study blocks.",
    ]
    low_marks = [m for m in exam_marks if m["percentage"] < 65.0]
    if low_marks:
        parent_recs.insert(
            0,
            f"Attention Needed: {student.get('full_name', 'Your child')} reported {low_marks[-1]['percentage']}% in {low_marks[-1]['subject']} ({low_marks[-1]['exam_name']}). Extra revision sessions have been added to their timetable.",
        )

    return {
        "authorised": True,
        "parent_id": parent_id,
        "parent_preferred_language": student.get("parent_preferred_language", "English"),
        "parent_consent_verified": student.get("parent_consent_verified", True),
        "requires_parental_assistance": student.get("requires_parental_assistance", False),
        "child_safety_controls": {
            "under_8_assisted_mode": bool(student.get("requires_parental_assistance", False)),
            "age_tier_safety_policy": student.get("age_tier_safety_policy", "TIER_2_MIDDLE"),
            "parent_consent_verified": bool(student.get("parent_consent_verified", True)),
            "verified_parent_name": student.get("verified_parent_name"),
            "verified_parent_relationship": student.get("verified_parent_relationship"),
            "strict_privacy_guard_active": True,
        },
        "child_profile": student,
        "academic_history": [y.model_dump() for y in years],
        "live_progress_summary": progress_report,
        "homeworks": homeworks,
        "study_plan": study_plan,
        "daily_schedule": daily_schedule,
        "recurring_activities": recurring_activities,
        "exams": exams,
        "exam_marks": exam_marks,
        "reminder_preferences": reminder_prefs,
        "daily_reminders": notifications_info["notifications"],
        "parent_recommendations": parent_recs,
        "tamper_protection_notice": "Verified assessment results are read-only and cannot be altered by parents or students.",
    }


@router.post("/parent/{parent_id}/child/{student_id}/action")
def perform_parent_action(parent_id: str, student_id: str, req: ParentActionRequest):
    student = repo.students.get(student_id)
    if not student or student.get("parent_id") != parent_id:
        raise HTTPException(status_code=403, detail="Unauthorised parent access.")

    if req.action == "ATTEMPT_ALTER_SCORE":
        raise HTTPException(
            status_code=403,
            detail="Security Policy (Section 15): Parents cannot silently alter verified assessment results.",
        )

    if req.action == "UPDATE_PARENT_LANGUAGE" and req.preferred_parent_language:
        student["parent_preferred_language"] = req.preferred_parent_language
        repo._persist_to_disk()
        return {
            "status": "parent_language_updated",
            "parent_preferred_language": req.preferred_parent_language,
        }

    return {"status": "ok"}


# ----------------------------------------------------------------------------
# 8. COMPLETE PLATFORM MODULES (DASHBOARD, STUDY PLANNER, HOMEWORK, EXAMS, REVISION, PROGRESS, PROJECTS)
# ----------------------------------------------------------------------------

@router.get("/students/{student_id}/dashboard-summary")
def get_student_dashboard_summary(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    return repo.get_dashboard_summary(student_id)


@router.get("/students/{student_id}/notifications")
def get_student_notifications(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    return repo.get_notifications_and_reminders(student_id)


@router.get("/students/{student_id}/reminders/preferences")
def get_student_reminder_preferences(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    prefs = repo.get_or_create_reminder_preferences(student_id)
    return prefs.model_dump()


@router.put("/students/{student_id}/reminders/preferences")
def update_student_reminder_preferences(
    student_id: str,
    prefs: ReminderPreferences,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    prefs.student_id = student_id
    updated = repo.update_reminder_preferences(student_id, prefs.model_dump())
    return updated.model_dump()


@router.patch("/students/{student_id}/reminders/status")
def update_student_reminder_status(
    student_id: str,
    req: ReminderStatusUpdateRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    req.student_id = student_id
    return repo.update_reminder_task_status(student_id, req)


@router.get("/students/{student_id}/study-plan")
def get_student_study_plan(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
    session_token: Optional[str] = Query(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token, session_token)
    plan = repo.get_or_create_study_plan(student_id)
    return plan.model_dump()


@router.get("/students/{student_id}/daily-schedule")
def get_student_daily_schedule(
    student_id: str,
    date_iso: Optional[str] = Query(default=None),
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    sched = repo.get_daily_schedule(student_id=student_id, date_iso=date_iso)
    return sched.model_dump()


@router.post("/students/{student_id}/daily-schedule/check-in")
def submit_student_daily_schedule_checkin(
    student_id: str,
    req: DailyScheduleCheckInRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    req.student_id = student_id
    try:
        sched = repo.submit_daily_schedule_checkin(student_id=student_id, req=req)
        return sched if isinstance(sched, dict) else sched.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.patch("/students/{student_id}/daily-schedule/activities/{activity_id}")
def update_student_daily_activity(
    student_id: str,
    activity_id: str,
    upd: DailyActivityUpdateRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    upd.student_id = student_id
    upd.activity_id = activity_id
    try:
        sched = repo.update_or_delete_daily_activity(
            student_id=student_id,
            activity_id=activity_id,
            upd=upd,
        )
        return sched if isinstance(sched, dict) else sched.model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/students/{student_id}/daily-schedule/activities/{activity_id}")
def delete_student_daily_activity(
    student_id: str,
    activity_id: str,
    date_iso: Optional[str] = Query(default=None),
    current_time_12h: Optional[str] = Query(default=None),
    regenerate_remaining_plan: bool = Query(default=True),
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    upd = DailyActivityUpdateRequest(
        student_id=student_id,
        date_iso=date_iso,
        activity_id=activity_id,
        delete_activity=True,
        current_time_12h=current_time_12h,
        regenerate_remaining_plan=regenerate_remaining_plan,
    )
    try:
        sched = repo.update_or_delete_daily_activity(
            student_id=student_id,
            activity_id=activity_id,
            upd=upd,
        )
        return sched if isinstance(sched, dict) else sched.model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/students/{student_id}/study-plan/generate")
def generate_student_study_plan(
    student_id: str,
    req: StudyPlanGenerateRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    req.student_id = student_id
    plan = repo.generate_and_save_study_plan(req)
    return plan.model_dump()


@router.post("/students/{student_id}/study-plan/subjects")
def upsert_study_plan_subject(
    student_id: str,
    req: ExamSubjectUpsertRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    req.student_id = student_id
    plan = repo.upsert_exam_subject_in_plan(
        student_id=student_id,
        sub_req=req,
    )
    return plan.model_dump()


@router.delete("/students/{student_id}/study-plan/subjects/{subject_id}")
def delete_study_plan_subject(
    student_id: str,
    subject_id: str,
    auto_regenerate: bool = Query(default=True),
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    try:
        plan = repo.remove_exam_subject_from_plan(
            student_id=student_id,
            subject_id_or_name=subject_id,
        )
        return plan.model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/students/{student_id}/study-plan/tasks/{task_id}")
def toggle_student_study_task(
    student_id: str,
    task_id: str,
    payload: StudyTaskEditRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
    session_token: Optional[str] = Query(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token, session_token)
    plan = repo.toggle_study_task(
        student_id=student_id,
        task_id=task_id,
        completed=payload.completed if payload.completed is not None else False,
        missed=payload.missed if payload.missed is not None else False,
        postponed=payload.postponed if payload.postponed is not None else False,
        edit_req=payload,
    )
    return plan.model_dump()


@router.post("/students/{student_id}/study-plan/catch-up")
def trigger_study_plan_catch_up(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    plan = repo.generate_catch_up_for_plan(student_id)
    return plan.model_dump()


@router.get("/students/{student_id}/exam-marks")
def list_student_exam_marks(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
    session_token: Optional[str] = Query(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token, session_token)
    marks = repo.list_exam_marks(student_id)
    return {
        "student_id": student_id,
        "count": len(marks),
        "exam_marks": [m.model_dump() for m in marks],
    }


@router.post("/students/{student_id}/exam-marks")
def create_student_exam_mark(
    student_id: str,
    req: ExamMarkEntryRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    req.student_id = student_id
    try:
        record = repo.record_or_update_exam_marks(student_id, req, mark_id=req.mark_id)
        return record.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.put("/students/{student_id}/exam-marks/{mark_id}")
def update_student_exam_mark(
    student_id: str,
    mark_id: str,
    req: ExamMarkEntryRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    req.student_id = student_id
    req.mark_id = mark_id
    try:
        record = repo.record_or_update_exam_marks(student_id, req, mark_id=mark_id)
        return record.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/students/{student_id}/homework")
def list_student_homework(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
    session_token: Optional[str] = Query(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token, session_token)
    items = repo.list_homeworks(student_id)
    return {
        "student_id": student_id,
        "count": len(items),
        "items": [h.model_dump() for h in items],
    }


@router.post("/students/{student_id}/homework")
def create_student_homework(
    student_id: str,
    req: HomeworkCreateRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    req.student_id = student_id
    hw = repo.create_homework(req)
    return hw.model_dump()


@router.patch("/students/{student_id}/homework/{homework_id}")
def update_student_homework(
    student_id: str,
    homework_id: str,
    upd: HomeworkStatusUpdateRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    try:
        hw = repo.update_homework(student_id, homework_id, upd)
        return hw.model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/students/{student_id}/exams")
def list_student_mock_exams(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    exams = repo.list_mock_exams(student_id)
    return {
        "student_id": student_id,
        "count": len(exams),
        "exams": [e.model_dump() for e in exams],
    }


@router.post("/students/{student_id}/exams/generate")
def generate_student_mock_exam(
    student_id: str,
    req: ExamGenerateRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    req.student_id = student_id
    exam = repo.create_mock_exam(req)
    return exam.model_dump()


@router.post("/students/{student_id}/exams/{exam_id}/submit")
def submit_student_mock_exam(
    student_id: str,
    exam_id: str,
    sub: ExamSubmissionRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    sub.student_id = student_id
    try:
        evaluated = repo.submit_mock_exam(student_id, exam_id, sub)
        return evaluated.model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/students/{student_id}/revision")
def list_student_revision_cards(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    cards = repo.list_revision_cards(student_id)
    return {
        "student_id": student_id,
        "count": len(cards),
        "due_today_count": len([c for c in cards if not c.completed_today]),
        "cards": [c.model_dump() for c in cards],
    }


@router.post("/students/{student_id}/revision/generate")
def create_student_revision_card(
    student_id: str,
    req: RevisionGenerateRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    req.student_id = student_id
    card = repo.generate_revision_card(req)
    return card.model_dump()


@router.patch("/students/{student_id}/revision/{revision_id}/review")
def review_student_revision_card(
    student_id: str,
    revision_id: str,
    upd: RevisionReviewUpdateRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    upd.student_id = student_id
    try:
        card = repo.review_revision_card(student_id, revision_id, upd)
        return card.model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/students/{student_id}/progress")
def get_student_academic_progress(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    return repo.get_academic_progress_report(student_id)


@router.get("/students/{student_id}/projects")
def list_student_projects(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    projs = repo.list_projects(student_id)
    return {
        "student_id": student_id,
        "count": len(projs),
        "projects": [p.model_dump() for p in projs],
    }


@router.post("/students/{student_id}/projects/generate")
def generate_student_project(
    student_id: str,
    req: ProjectGenerateRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    req.student_id = student_id
    proj = repo.create_project(req)
    return proj.model_dump()


@router.patch("/students/{student_id}/projects/{project_id}")
def update_student_project(
    student_id: str,
    project_id: str,
    upd: ProjectMilestoneUpdateRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    upd.student_id = student_id
    try:
        proj = repo.update_project(student_id, project_id, upd)
        return proj.model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ----------------------------------------------------------------------------
# 8. FILE UPLOAD STORAGE & PRODUCTION DATABASE BACKUP / RECOVERY
# ----------------------------------------------------------------------------

class FileUploadRequest(BaseModel):
    filename: str
    content_base64: Optional[str] = None
    text_content: Optional[str] = None
    content_type: str = "application/octet-stream"
    category: str = "homework"


class DatabaseBackupRequest(BaseModel):
    reason: str = "manual_or_scheduled"


class DatabaseRestoreRequest(BaseModel):
    backup_id: str


@router.post("/students/{student_id}/files/upload")
def upload_student_file(
    student_id: str,
    req: FileUploadRequest,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    raw_bytes = b""
    if req.content_base64:
        payload_str = req.content_base64.split(",")[-1].strip()
        try:
            raw_bytes = b64decode(payload_str)
        except Exception:
            raw_bytes = req.content_base64.encode("utf-8")
    elif req.text_content is not None:
        raw_bytes = req.text_content.encode("utf-8")
    else:
        raise HTTPException(status_code=422, detail="Provide content_base64 or text_content for file upload.")

    meta = repo.save_uploaded_file(
        student_id=student_id,
        filename=req.filename,
        content_bytes=raw_bytes,
        content_type=req.content_type,
        category=req.category,
    )
    return {"status": "file_uploaded", "file": meta}


@router.get("/students/{student_id}/files")
def list_student_uploaded_files(
    student_id: str,
    authorization: Optional[str] = Header(default=None),
    x_sparkminds_token: Optional[str] = Header(default=None),
):
    verify_student_access(student_id, authorization, x_sparkminds_token)
    files = repo.list_uploaded_files(student_id)
    return {
        "student_id": student_id,
        "count": len(files),
        "files": files,
    }


@router.post("/admin/database/backup")
def trigger_database_backup(
    req: Optional[DatabaseBackupRequest] = None,
    x_sparkminds_admin_key: Optional[str] = Header(default=None),
):
    verify_admin_access(x_sparkminds_admin_key)
    reason = req.reason if req else "manual_or_scheduled"
    backup = repo.create_database_backup(reason=reason)
    return {"status": "backup_created", "backup": backup}


@router.get("/admin/database/backups")
def get_database_backups(
    x_sparkminds_admin_key: Optional[str] = Header(default=None),
):
    verify_admin_access(x_sparkminds_admin_key)
    backups = repo.list_database_backups()
    return {"count": len(backups), "backups": backups}


@router.post("/admin/database/restore")
def restore_database_from_backup(
    req: DatabaseRestoreRequest,
    x_sparkminds_admin_key: Optional[str] = Header(default=None),
):
    verify_admin_access(x_sparkminds_admin_key)
    try:
        return repo.restore_database_backup(req.backup_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))



