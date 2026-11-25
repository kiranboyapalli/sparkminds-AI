"""
SparkMinds AI — Managed PostgreSQL Persistent Production Storage Layer.

Provides durable, ACID-compliant persistence on Railway PostgreSQL (via DATABASE_URL)
so student accounts, PBKDF2 password hashes, unique case-insensitive usernames,
verified emails, active & revoked access/refresh sessions, academic profiles,
study plans, learning history, guided lessons, assessments, and gamification progress
ALWAYS survive container restarts, deployments, and cross-device sign-ins.

Security Invariants:
- Never hardcodes database URLs or passwords (reads DATABASE_URL / POSTGRES_URL strictly from env).
- Never logs connection strings, passwords, password hashes, or refresh tokens.
- Uses strictly parameterized SQL queries (zero string-interpolated user values).
- Never drops, truncates, or overwrites existing production accounts on startup/deploy.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
import os
import sqlite3
import threading
from typing import Any, Dict, List, Optional, Tuple

from app.core.account_policy import (
    DUPLICATE_USERNAME_MESSAGE,
    DUPLICATE_VERIFIED_EMAIL_MESSAGE,
    DuplicateUsernameError,
    DuplicateVerifiedEmailError,
    normalize_email,
    normalize_username,
)

logger = logging.getLogger("sparkminds.postgres")

try:
    import psycopg
    from psycopg.rows import dict_row
    from psycopg import errors as pg_errors

    PSYCOPG_AVAILABLE = True
except Exception:  # pragma: no cover - fallback when psycopg is not installed
    psycopg = None  # type: ignore
    dict_row = None  # type: ignore
    pg_errors = None  # type: ignore
    PSYCOPG_AVAILABLE = False


# Auxiliary SQLite module tables mirrored into PostgreSQL so ALL learning progress
# (Guided Lessons, Assessments, Gamification, Document RAG, Notifications, Consents, Email OTP)
# persists across container restarts and deployments.
AUX_SQLITE_TABLES: Tuple[str, ...] = (
    "email_verifications",
    "parent_consents",
    "diagnostic_assessments",
    "topic_mastery_records",
    "agent_execution_logs",
    "learning_documents",
    "document_chunks",
    "learning_activity_log",
    "gamification_badges",
    "push_subscriptions",
    "notification_history",
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_postgres_url(raw_url: str) -> str:
    url = (raw_url or "").strip()
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    return url


class PostgresPersistentStore:
    """
    Thread-safe PostgreSQL persistence store backed by Railway Managed Postgres.
    Gracefully stays disabled when DATABASE_URL is absent (e.g. local unit tests).
    """

    def __init__(self, database_url: Optional[str] = None) -> None:
        raw_url = database_url if database_url is not None else (
            os.getenv("DATABASE_URL", "").strip()
            or os.getenv("POSTGRES_URL", "").strip()
        )
        self._dsn = _normalize_postgres_url(raw_url)
        self._lock = threading.RLock()
        self._connected = False
        self._last_error: Optional[str] = None

        if self._dsn and PSYCOPG_AVAILABLE:
            try:
                self._init_schema()
                self._connected = True
                logger.info("PostgreSQL persistent production database connected and schema verified.")
            except Exception as exc:
                self._last_error = type(exc).__name__
                self._connected = False
                logger.error(
                    "Failed to initialize PostgreSQL persistent database (%s). Check DATABASE_URL.",
                    type(exc).__name__,
                )
        elif self._dsn and not PSYCOPG_AVAILABLE:
            self._last_error = "psycopg_not_installed"
            logger.error("DATABASE_URL is configured but psycopg is not installed.")

    @property
    def is_configured(self) -> bool:
        return bool(self._dsn)

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def last_error(self) -> Optional[str]:
        return self._last_error

    def _connect(self):
        if not self._dsn or not PSYCOPG_AVAILABLE:
            raise RuntimeError("PostgreSQL is not configured or psycopg is unavailable.")
        return psycopg.connect(
            self._dsn,
            connect_timeout=10,
            row_factory=dict_row,
        )

    def _init_schema(self) -> None:
        """Runs idempotent CREATE TABLE IF NOT EXISTS migrations without ever altering existing data."""
        with self._lock, self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS sm_users_accounts (
                        student_id TEXT PRIMARY KEY,
                        username_normalized TEXT UNIQUE,
                        verified_email_normalized TEXT UNIQUE,
                        full_name TEXT NOT NULL,
                        current_grade INTEGER NOT NULL DEFAULT 7,
                        school_board TEXT NOT NULL DEFAULT 'CBSE',
                        onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE,
                        email_verified BOOLEAN NOT NULL DEFAULT FALSE,
                        email_verified_at TEXT,
                        password_hash TEXT,
                        salt TEXT,
                        recovery_pin_hash TEXT,
                        profile_json TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS sm_user_sessions (
                        session_token TEXT PRIMARY KEY,
                        student_id TEXT NOT NULL,
                        device_name TEXT NOT NULL DEFAULT 'Web Browser',
                        refresh_token_hash TEXT UNIQUE,
                        created_at TEXT NOT NULL,
                        expires_at TEXT NOT NULL,
                        refresh_expires_at TEXT,
                        last_seen_at TEXT,
                        active BOOLEAN NOT NULL DEFAULT TRUE,
                        expired BOOLEAN NOT NULL DEFAULT FALSE,
                        revoked_at TEXT
                    );
                    """
                )
                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_sm_user_sessions_student
                    ON sm_user_sessions(student_id);
                    """
                )
                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_sm_user_sessions_refresh_hash
                    ON sm_user_sessions(refresh_token_hash);
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS sm_app_state_snapshots (
                        id INTEGER PRIMARY KEY CHECK (id = 1),
                        updated_at TEXT NOT NULL,
                        payload_json TEXT NOT NULL
                    );
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS sm_aux_sqlite_backup (
                        id INTEGER PRIMARY KEY CHECK (id = 1),
                        updated_at TEXT NOT NULL,
                        tables_json TEXT NOT NULL
                    );
                    """
                )
            conn.commit()

    def health_summary(self) -> Dict[str, Any]:
        """Returns safe health metadata without exposing connection strings or credentials."""
        if not self._connected:
            return {
                "postgresql_configured": self.is_configured,
                "postgresql_connected": False,
                "db_user_accounts_count": None,
                "db_active_sessions_count": None,
                "last_error": self._last_error,
            }
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) AS cnt FROM sm_users_accounts")
                    users_cnt = int((cur.fetchone() or {}).get("cnt", 0))
                    cur.execute("SELECT COUNT(*) AS cnt FROM sm_user_sessions WHERE active = TRUE")
                    sess_cnt = int((cur.fetchone() or {}).get("cnt", 0))
            return {
                "postgresql_configured": True,
                "postgresql_connected": True,
                "db_user_accounts_count": users_cnt,
                "db_active_sessions_count": sess_cnt,
            }
        except Exception as exc:
            self._last_error = type(exc).__name__
            return {
                "postgresql_configured": True,
                "postgresql_connected": False,
                "db_user_accounts_count": None,
                "db_active_sessions_count": None,
                "last_error": self._last_error,
            }

    def has_persisted_data(self) -> bool:
        if not self._connected:
            return False
        with self._lock, self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS cnt FROM sm_users_accounts")
                row = cur.fetchone() or {}
                if int(row.get("cnt", 0)) > 0:
                    return True
                cur.execute("SELECT COUNT(*) AS cnt FROM sm_app_state_snapshots WHERE id = 1")
                snap = cur.fetchone() or {}
                return int(snap.get("cnt", 0)) > 0

    def is_username_taken(self, norm_username: str) -> Optional[str]:
        """Returns owning student_id if case-insensitive username exists in PostgreSQL."""
        if not self._connected or not norm_username:
            return None
        with self._lock, self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT student_id FROM sm_users_accounts WHERE username_normalized = %s LIMIT 1",
                    (norm_username,),
                )
                row = cur.fetchone()
                return str(row["student_id"]) if row else None

    def is_verified_email_taken(self, norm_email: str) -> Optional[str]:
        """Returns owning student_id if normalized verified email exists in PostgreSQL."""
        if not self._connected or not norm_email:
            return None
        with self._lock, self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT student_id FROM sm_users_accounts WHERE verified_email_normalized = %s LIMIT 1",
                    (norm_email,),
                )
                row = cur.fetchone()
                return str(row["student_id"]) if row else None

    def reserve_new_user_account(
        self,
        *,
        student_id: str,
        username_normalized: Optional[str],
        verified_email_normalized: Optional[str],
        full_name: str,
        current_grade: int,
        school_board: str,
        onboarding_completed: bool,
        email_verified: bool,
        email_verified_at: Optional[str],
        password_hash: str,
        salt: str,
        recovery_pin_hash: str,
        profile_dict: Dict[str, Any],
    ) -> None:
        """
        Atomically inserts a brand-new student account into PostgreSQL enforcing
        database-level UNIQUE constraints on username_normalized and verified_email_normalized.
        """
        if not self._connected:
            return
        now_iso = _utc_now_iso()
        clean_username = normalize_username(username_normalized) or normalize_username(student_id)
        clean_email = normalize_email(verified_email_normalized) or None
        with self._lock, self._connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO sm_users_accounts (
                            student_id, username_normalized, verified_email_normalized,
                            full_name, current_grade, school_board, onboarding_completed,
                            email_verified, email_verified_at, password_hash, salt,
                            recovery_pin_hash, profile_json, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s,
                            %s, %s, %s, %s,
                            %s, %s, %s, %s,
                            %s, %s, %s, %s
                        )
                        """,
                        (
                            student_id,
                            clean_username,
                            clean_email,
                            full_name or "Student Learner",
                            int(current_grade or 7),
                            school_board or "CBSE",
                            bool(onboarding_completed),
                            bool(email_verified),
                            email_verified_at,
                            password_hash,
                            salt,
                            recovery_pin_hash,
                            json.dumps(profile_dict),
                            now_iso,
                            now_iso,
                        ),
                    )
                conn.commit()
            except Exception as exc:
                conn.rollback()
                if pg_errors is not None and isinstance(exc, pg_errors.UniqueViolation):
                    err_text = str(exc).lower()
                    if "verified_email_normalized" in err_text:
                        raise DuplicateVerifiedEmailError(DUPLICATE_VERIFIED_EMAIL_MESSAGE) from exc
                    raise DuplicateUsernameError(DUPLICATE_USERNAME_MESSAGE) from exc
                raise

    def upsert_user_account(
        self,
        *,
        student_id: str,
        profile_dict: Dict[str, Any],
        cred_dict: Optional[Dict[str, str]] = None,
    ) -> None:
        if not self._connected or not student_id:
            return
        now_iso = _utc_now_iso()
        raw_u = profile_dict.get("username_normalized") or profile_dict.get("username") or (
            profile_dict.get("email_or_username")
            if profile_dict.get("email_or_username")
            and "@" not in str(profile_dict.get("email_or_username"))
            else student_id
        )
        norm_u = normalize_username(str(raw_u)) or normalize_username(student_id)
        raw_e = profile_dict.get("verified_email") or (
            profile_dict.get("email_or_username")
            if "@" in str(profile_dict.get("email_or_username") or "")
            else ""
        )
        norm_e = normalize_email(str(raw_e)) or None
        pw_hash = (cred_dict or {}).get("password_hash")
        salt = (cred_dict or {}).get("salt")
        rec_hash = (cred_dict or {}).get("recovery_pin_hash")
        with self._lock, self._connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO sm_users_accounts (
                            student_id, username_normalized, verified_email_normalized,
                            full_name, current_grade, school_board, onboarding_completed,
                            email_verified, email_verified_at, password_hash, salt,
                            recovery_pin_hash, profile_json, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s,
                            %s, %s, %s, %s,
                            %s, %s, %s, %s,
                            %s, %s, %s, %s
                        )
                        ON CONFLICT(student_id) DO UPDATE SET
                            full_name = EXCLUDED.full_name,
                            current_grade = EXCLUDED.current_grade,
                            school_board = EXCLUDED.school_board,
                            onboarding_completed = (EXCLUDED.onboarding_completed OR sm_users_accounts.onboarding_completed),
                            email_verified = COALESCE(EXCLUDED.email_verified, sm_users_accounts.email_verified),
                            email_verified_at = COALESCE(EXCLUDED.email_verified_at, sm_users_accounts.email_verified_at),
                            password_hash = COALESCE(EXCLUDED.password_hash, sm_users_accounts.password_hash),
                            salt = COALESCE(EXCLUDED.salt, sm_users_accounts.salt),
                            recovery_pin_hash = COALESCE(EXCLUDED.recovery_pin_hash, sm_users_accounts.recovery_pin_hash),
                            profile_json = EXCLUDED.profile_json,
                            updated_at = EXCLUDED.updated_at
                        """,
                        (
                            student_id,
                            norm_u,
                            norm_e,
                            str(profile_dict.get("full_name") or "Student Learner"),
                            int(profile_dict.get("current_grade") or 7),
                            str(profile_dict.get("school_board") or "CBSE"),
                            bool(profile_dict.get("onboarding_completed", False)),
                            bool(profile_dict.get("email_verified", False)),
                            profile_dict.get("email_verified_at"),
                            pw_hash,
                            salt,
                            rec_hash,
                            json.dumps(profile_dict),
                            now_iso,
                            now_iso,
                        ),
                    )
                conn.commit()
            except Exception as exc:
                conn.rollback()
                # If a legacy baseline row had a non-unique username/email collision, update by student_id cleanly
                if pg_errors is not None and isinstance(exc, pg_errors.UniqueViolation):
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            UPDATE sm_users_accounts SET
                                full_name = %s,
                                current_grade = %s,
                                school_board = %s,
                                onboarding_completed = (%s OR onboarding_completed),
                                password_hash = COALESCE(%s, password_hash),
                                salt = COALESCE(%s, salt),
                                recovery_pin_hash = COALESCE(%s, recovery_pin_hash),
                                profile_json = %s,
                                updated_at = %s
                            WHERE student_id = %s
                            """,
                            (
                                str(profile_dict.get("full_name") or "Student Learner"),
                                int(profile_dict.get("current_grade") or 7),
                                str(profile_dict.get("school_board") or "CBSE"),
                                bool(profile_dict.get("onboarding_completed", False)),
                                pw_hash,
                                salt,
                                rec_hash,
                                json.dumps(profile_dict),
                                now_iso,
                                student_id,
                            ),
                        )
                    conn.commit()
                else:
                    raise

    def find_user_by_identifier(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Authoritative case-insensitive lookup against PostgreSQL sm_users_accounts by:
        1. student_id
        2. username_normalized
        3. verified_email_normalized
        """
        if not self._connected or not identifier or not identifier.strip():
            return None
        clean = identifier.strip()
        norm = clean.lower()
        with self._lock, self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT * FROM sm_users_accounts
                    WHERE student_id = %s
                       OR LOWER(student_id) = %s
                       OR username_normalized = %s
                       OR verified_email_normalized = %s
                    LIMIT 1
                    """,
                    (clean, norm, norm, norm),
                )
                row = cur.fetchone()
                return dict(row) if row else None

    def upsert_session(self, sess: Dict[str, Any]) -> None:
        if not self._connected:
            return
        now_iso = _utc_now_iso()
        with self._lock, self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO sm_user_sessions (
                        session_token, student_id, device_name, refresh_token_hash,
                        created_at, expires_at, refresh_expires_at, last_seen_at,
                        active, expired, revoked_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT(session_token) DO UPDATE SET
                        refresh_token_hash = COALESCE(EXCLUDED.refresh_token_hash, sm_user_sessions.refresh_token_hash),
                        expires_at = EXCLUDED.expires_at,
                        refresh_expires_at = COALESCE(EXCLUDED.refresh_expires_at, sm_user_sessions.refresh_expires_at),
                        last_seen_at = EXCLUDED.last_seen_at,
                        active = EXCLUDED.active,
                        expired = EXCLUDED.expired,
                        revoked_at = COALESCE(EXCLUDED.revoked_at, sm_user_sessions.revoked_at)
                    """,
                    (
                        str(sess["session_token"]),
                        str(sess["student_id"]),
                        str(sess.get("device_name") or "Web Browser"),
                        sess.get("refresh_token_hash"),
                        str(sess.get("created_at") or now_iso),
                        str(sess.get("expires_at") or now_iso),
                        sess.get("refresh_expires_at"),
                        str(sess.get("last_seen_at") or now_iso),
                        bool(sess.get("active", True)),
                        bool(sess.get("expired", False)),
                        sess.get("revoked_at"),
                    ),
                )
            conn.commit()

    def get_session_by_token(self, session_token: str) -> Optional[Dict[str, Any]]:
        if not self._connected or not session_token:
            return None
        with self._lock, self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM sm_user_sessions WHERE session_token = %s LIMIT 1",
                    (session_token,),
                )
                row = cur.fetchone()
                return dict(row) if row else None

    def get_session_by_refresh_hash(self, refresh_token_hash: str) -> Optional[Dict[str, Any]]:
        if not self._connected or not refresh_token_hash:
            return None
        with self._lock, self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM sm_user_sessions WHERE refresh_token_hash = %s LIMIT 1",
                    (refresh_token_hash,),
                )
                row = cur.fetchone()
                return dict(row) if row else None

    def load_all_users_and_sessions(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        if not self._connected:
            return [], []
        with self._lock, self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM sm_users_accounts")
                users = [dict(r) for r in cur.fetchall()]
                cur.execute("SELECT * FROM sm_user_sessions")
                sessions = [dict(r) for r in cur.fetchall()]
        return users, sessions

    def load_full_state_snapshot(self) -> Optional[Dict[str, Any]]:
        if not self._connected:
            return None
        with self._lock, self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT payload_json FROM sm_app_state_snapshots WHERE id = 1")
                row = cur.fetchone()
                if row and row.get("payload_json"):
                    return json.loads(str(row["payload_json"]))
        return None

    def save_full_state(
        self,
        *,
        payload_str: str,
        updated_at: str,
        students: Dict[str, Dict[str, Any]],
        auth_credentials: Dict[str, Dict[str, str]],
        active_sessions: Dict[str, Dict[str, Any]],
        sqlite_db_path: Optional[str] = None,
    ) -> None:
        """
        Transactionally persists full application state snapshot, relational user accounts,
        active/revoked sessions, and auxiliary SQLite module tables into PostgreSQL
        over a single connection for low latency and atomicity.
        """
        if not self._connected:
            return
        aux_json = self._export_aux_sqlite_json(sqlite_db_path) if sqlite_db_path else None
        now_iso = updated_at or _utc_now_iso()
        with self._lock, self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO sm_app_state_snapshots (id, updated_at, payload_json)
                    VALUES (1, %s, %s)
                    ON CONFLICT(id) DO UPDATE SET
                        updated_at = EXCLUDED.updated_at,
                        payload_json = EXCLUDED.payload_json
                    """,
                    (now_iso, payload_str),
                )
                if aux_json is not None:
                    cur.execute(
                        """
                        INSERT INTO sm_aux_sqlite_backup (id, updated_at, tables_json)
                        VALUES (1, %s, %s)
                        ON CONFLICT(id) DO UPDATE SET
                            updated_at = EXCLUDED.updated_at,
                            tables_json = EXCLUDED.tables_json
                        """,
                        (now_iso, aux_json),
                    )
                for sid, sdata in list(students.items()):
                    if not isinstance(sdata, dict):
                        continue
                    cred_dict = auth_credentials.get(sid) or {}
                    raw_u = sdata.get("username_normalized") or sdata.get("username") or (
                        sdata.get("email_or_username")
                        if sdata.get("email_or_username")
                        and "@" not in str(sdata.get("email_or_username"))
                        else sid
                    )
                    norm_u = normalize_username(str(raw_u)) or normalize_username(sid)
                    raw_e = sdata.get("verified_email") or (
                        sdata.get("email_or_username")
                        if "@" in str(sdata.get("email_or_username") or "")
                        else ""
                    )
                    norm_e = normalize_email(str(raw_e)) or None
                    cur.execute("SAVEPOINT sp_user_upsert")
                    try:
                        cur.execute(
                            """
                            INSERT INTO sm_users_accounts (
                                student_id, username_normalized, verified_email_normalized,
                                full_name, current_grade, school_board, onboarding_completed,
                                email_verified, email_verified_at, password_hash, salt,
                                recovery_pin_hash, profile_json, created_at, updated_at
                            ) VALUES (
                                %s, %s, %s,
                                %s, %s, %s, %s,
                                %s, %s, %s, %s,
                                %s, %s, %s, %s
                            )
                            ON CONFLICT(student_id) DO UPDATE SET
                                full_name = EXCLUDED.full_name,
                                current_grade = EXCLUDED.current_grade,
                                school_board = EXCLUDED.school_board,
                                onboarding_completed = (EXCLUDED.onboarding_completed OR sm_users_accounts.onboarding_completed),
                                email_verified = COALESCE(EXCLUDED.email_verified, sm_users_accounts.email_verified),
                                email_verified_at = COALESCE(EXCLUDED.email_verified_at, sm_users_accounts.email_verified_at),
                                password_hash = COALESCE(EXCLUDED.password_hash, sm_users_accounts.password_hash),
                                salt = COALESCE(EXCLUDED.salt, sm_users_accounts.salt),
                                recovery_pin_hash = COALESCE(EXCLUDED.recovery_pin_hash, sm_users_accounts.recovery_pin_hash),
                                profile_json = EXCLUDED.profile_json,
                                updated_at = EXCLUDED.updated_at
                            """,
                            (
                                sid,
                                norm_u,
                                norm_e,
                                str(sdata.get("full_name") or "Student Learner"),
                                int(sdata.get("current_grade") or 7),
                                str(sdata.get("school_board") or "CBSE"),
                                bool(sdata.get("onboarding_completed", False)),
                                bool(sdata.get("email_verified", False)),
                                sdata.get("email_verified_at"),
                                cred_dict.get("password_hash"),
                                cred_dict.get("salt"),
                                cred_dict.get("recovery_pin_hash"),
                                json.dumps(sdata),
                                now_iso,
                                now_iso,
                            ),
                        )
                        cur.execute("RELEASE SAVEPOINT sp_user_upsert")
                    except Exception:
                        cur.execute("ROLLBACK TO SAVEPOINT sp_user_upsert")
                        cur.execute(
                            """
                            UPDATE sm_users_accounts SET
                                full_name = %s,
                                current_grade = %s,
                                school_board = %s,
                                onboarding_completed = (%s OR onboarding_completed),
                                password_hash = COALESCE(%s, password_hash),
                                salt = COALESCE(%s, salt),
                                recovery_pin_hash = COALESCE(%s, recovery_pin_hash),
                                profile_json = %s,
                                updated_at = %s
                            WHERE student_id = %s
                            """,
                            (
                                str(sdata.get("full_name") or "Student Learner"),
                                int(sdata.get("current_grade") or 7),
                                str(sdata.get("school_board") or "CBSE"),
                                bool(sdata.get("onboarding_completed", False)),
                                cred_dict.get("password_hash"),
                                cred_dict.get("salt"),
                                cred_dict.get("recovery_pin_hash"),
                                json.dumps(sdata),
                                now_iso,
                                sid,
                            ),
                        )

                for tok, sess in list(active_sessions.items()):
                    if not isinstance(sess, dict) or not sess.get("student_id"):
                        continue
                    cur.execute("SAVEPOINT sp_sess_upsert")
                    try:
                        cur.execute(
                            """
                            INSERT INTO sm_user_sessions (
                                session_token, student_id, device_name, refresh_token_hash,
                                created_at, expires_at, refresh_expires_at, last_seen_at,
                                active, expired, revoked_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT(session_token) DO UPDATE SET
                                refresh_token_hash = COALESCE(EXCLUDED.refresh_token_hash, sm_user_sessions.refresh_token_hash),
                                expires_at = EXCLUDED.expires_at,
                                refresh_expires_at = COALESCE(EXCLUDED.refresh_expires_at, sm_user_sessions.refresh_expires_at),
                                last_seen_at = EXCLUDED.last_seen_at,
                                active = EXCLUDED.active,
                                expired = EXCLUDED.expired,
                                revoked_at = COALESCE(EXCLUDED.revoked_at, sm_user_sessions.revoked_at)
                            """,
                            (
                                str(sess.get("session_token") or tok),
                                str(sess["student_id"]),
                                str(sess.get("device_name") or "Web Browser"),
                                sess.get("refresh_token_hash"),
                                str(sess.get("created_at") or now_iso),
                                str(sess.get("expires_at") or now_iso),
                                sess.get("refresh_expires_at"),
                                str(sess.get("last_seen_at") or now_iso),
                                bool(sess.get("active", True)),
                                bool(sess.get("expired", False)),
                                sess.get("revoked_at"),
                            ),
                        )
                        cur.execute("RELEASE SAVEPOINT sp_sess_upsert")
                    except Exception:
                        cur.execute("ROLLBACK TO SAVEPOINT sp_sess_upsert")
            conn.commit()

    def sync_aux_sqlite_to_postgres(self, sqlite_db_path: str) -> None:
        if not self._connected or not sqlite_db_path:
            return
        aux_json = self._export_aux_sqlite_json(sqlite_db_path)
        if aux_json is None:
            return
        now_iso = _utc_now_iso()
        with self._lock, self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO sm_aux_sqlite_backup (id, updated_at, tables_json)
                    VALUES (1, %s, %s)
                    ON CONFLICT(id) DO UPDATE SET
                        updated_at = EXCLUDED.updated_at,
                        tables_json = EXCLUDED.tables_json
                    """,
                    (now_iso, aux_json),
                )
            conn.commit()

    def restore_aux_sqlite_from_postgres(self, sqlite_db_path: str) -> bool:
        """Restores all auxiliary SQLite tables from PostgreSQL backup on container boot."""
        if not self._connected or not sqlite_db_path:
            return False
        try:
            with self._lock, self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT tables_json FROM sm_aux_sqlite_backup WHERE id = 1")
                    row = cur.fetchone()
            if not row or not row.get("tables_json"):
                return False
            data = json.loads(str(row["tables_json"]))
            if not isinstance(data, dict):
                return False
            with sqlite3.connect(sqlite_db_path, timeout=15.0) as sconn:
                existing_tables = {
                    r[0]
                    for r in sconn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    ).fetchall()
                }
                for table_name in AUX_SQLITE_TABLES:
                    rows = data.get(table_name)
                    if table_name not in existing_tables or not isinstance(rows, list) or not rows:
                        continue
                    valid_cols = {
                        r[1]
                        for r in sconn.execute(f"PRAGMA table_info({table_name})").fetchall()
                    }
                    for item in rows:
                        if not isinstance(item, dict):
                            continue
                        cols = [c for c in item.keys() if c in valid_cols]
                        if not cols:
                            continue
                        placeholders = ", ".join("?" for _ in cols)
                        col_sql = ", ".join(cols)
                        sconn.execute(
                            f"INSERT OR REPLACE INTO {table_name} ({col_sql}) VALUES ({placeholders})",
                            tuple(item[c] for c in cols),
                        )
                sconn.commit()
            return True
        except Exception as exc:
            logger.warning("Failed to restore auxiliary tables from PostgreSQL: %s", type(exc).__name__)
            return False

    @staticmethod
    def _export_aux_sqlite_json(sqlite_db_path: str) -> Optional[str]:
        try:
            exported: Dict[str, List[Dict[str, Any]]] = {}
            with sqlite3.connect(sqlite_db_path, timeout=15.0) as sconn:
                sconn.row_factory = sqlite3.Row
                existing_tables = {
                    r[0]
                    for r in sconn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    ).fetchall()
                }
                for table_name in AUX_SQLITE_TABLES:
                    if table_name not in existing_tables:
                        continue
                    rows = sconn.execute(f"SELECT * FROM {table_name}").fetchall()
                    exported[table_name] = [dict(r) for r in rows]
            return json.dumps(exported)
        except Exception:
            return None
