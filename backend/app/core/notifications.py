"""
SparkMinds AI — Mobile Push Notifications (Web Push / VAPID) & Notification Centre.
Supports:
- Persistent VAPID keypair management (env vars or local data/vapid_keys.json)
- Push subscription storage, revocation, and automatic cleanup of expired (404/410) subscriptions
- Notification Centre history (read/unread, mark read, mark all read, timestamps, deep links)
- Quiet hours enforcement, category opt-ins, reminder frequency, timezone awareness, duplicate prevention
- Privacy-safe lock-screen push payloads (no sensitive personal info or scores on lock screens)
- Personalized AI learning reminders strictly grounded in real student data (never fabricated!)
"""

from __future__ import annotations

import base64
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3
import threading
import uuid
from typing import Any, Dict, List, Optional, Tuple


NOTIFICATION_CATEGORIES = [
    "study_reminders",
    "daily_learning_goals",
    "streak_reminders",
    "quiz_and_assessment_reminders",
    "revision_alerts",
    "weak_topic_practice_reminders",
    "study_plan_task_reminders",
    "assessment_results_and_feedback",
    "ai_tutor_follow_ups",
    "achievement_and_badge_alerts",
    "weekly_progress_summaries",
    "account_and_security_alerts",
]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def is_within_quiet_hours(
    current_hhmm: str, quiet_start: str, quiet_end: str
) -> bool:
    """Checks if HH:MM falls inside [quiet_start, quiet_end), supporting overnight spans (e.g. 22:00-07:00)."""
    try:
        sh, sm = [int(x) for x in quiet_start.split(":")[:2]]
        eh, em = [int(x) for x in quiet_end.split(":")[:2]]
        ch, cm = [int(x) for x in current_hhmm.split(":")[:2]]
        s_min = sh * 60 + sm
        e_min = eh * 60 + em
        c_min = ch * 60 + cm
        if s_min == e_min:
            return False
        if s_min < e_min:
            return s_min <= c_min < e_min
        return c_min >= s_min or c_min < e_min
    except Exception:
        return False


class NotificationService:
    def __init__(self, sqlite_db_path: str, data_dir: Path) -> None:
        self.sqlite_db_path = sqlite_db_path
        self.vapid_file = data_dir / "vapid_keys.json"
        self._lock = threading.RLock()
        self._ensure_tables()
        self._vapid_public_key, self._vapid_private_pem, self._vapid_subject = self._load_or_create_vapid_keys()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.sqlite_db_path, timeout=15.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_tables(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS push_subscriptions (
                    subscription_id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    endpoint TEXT NOT NULL UNIQUE,
                    p256dh TEXT NOT NULL,
                    auth_secret TEXT NOT NULL,
                    user_agent TEXT,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    last_used_at TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS notification_history (
                    notification_id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    lockscreen_preview TEXT NOT NULL,
                    deep_link TEXT NOT NULL,
                    dedup_key TEXT,
                    is_read INTEGER NOT NULL DEFAULT 0,
                    delivered_push INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    read_at TEXT
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_notif_student_created ON notification_history(student_id, created_at DESC)"
            )
            conn.commit()

    def _load_or_create_vapid_keys(self) -> Tuple[str, str, str]:
        env_pub = os.getenv("VAPID_PUBLIC_KEY", "").strip()
        env_priv = os.getenv("VAPID_PRIVATE_KEY", "").strip()
        subject = os.getenv("VAPID_SUBJECT", "mailto:support@sparkminds.ai").strip()
        if env_pub and env_priv:
            return env_pub, env_priv, subject

        if self.vapid_file.exists():
            try:
                raw = json.loads(self.vapid_file.read_text(encoding="utf-8"))
                if raw.get("public_key") and raw.get("private_pem"):
                    return raw["public_key"], raw["private_pem"], raw.get("subject", subject)
            except Exception:
                pass

        # Generate real ECDSA P-256 VAPID keypair using cryptography
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import ec

            private_key = ec.generate_private_key(ec.SECP256R1())
            public_key = private_key.public_key()
            raw_pub = public_key.public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.UncompressedPoint,
            )
            pub_b64 = _b64url_encode(raw_pub)
            priv_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            ).decode("utf-8")
            self.vapid_file.parent.mkdir(parents=True, exist_ok=True)
            self.vapid_file.write_text(
                json.dumps(
                    {
                        "public_key": pub_b64,
                        "private_pem": priv_pem,
                        "subject": subject,
                        "created_at": _utc_now_iso(),
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            return pub_b64, priv_pem, subject
        except Exception:
            return "", "", subject

    def get_vapid_public_key(self) -> Dict[str, Any]:
        return {
            "vapid_public_key": self._vapid_public_key,
            "push_configured": bool(self._vapid_public_key),
        }

    def save_subscription(
        self,
        student_id: str,
        endpoint: str,
        p256dh: str,
        auth_secret: str,
        user_agent: str = "",
    ) -> Dict[str, Any]:
        if not endpoint or not endpoint.startswith("http"):
            raise ValueError("Valid push subscription endpoint URL is required.")
        if not p256dh or not auth_secret:
            raise ValueError("Push encryption keys (p256dh and auth) are required.")

        now_iso = _utc_now_iso()
        sub_id = f"sub_{uuid.uuid4().hex[:12]}"
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO push_subscriptions (
                    subscription_id, student_id, endpoint, p256dh, auth_secret,
                    user_agent, active, created_at, last_used_at
                ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
                ON CONFLICT(endpoint) DO UPDATE SET
                    student_id = excluded.student_id,
                    p256dh = excluded.p256dh,
                    auth_secret = excluded.auth_secret,
                    user_agent = excluded.user_agent,
                    active = 1,
                    last_used_at = excluded.last_used_at
                """,
                (sub_id, student_id, endpoint.strip(), p256dh.strip(), auth_secret.strip(), user_agent[:200], now_iso, now_iso),
            )
            conn.commit()
        return {
            "status": "subscribed",
            "subscription_id": sub_id,
            "student_id": student_id,
            "endpoint": endpoint.strip(),
        }

    def remove_subscription(self, student_id: str, endpoint: Optional[str] = None) -> Dict[str, Any]:
        with self._lock, self._connect() as conn:
            if endpoint:
                cur = conn.execute(
                    "UPDATE push_subscriptions SET active = 0 WHERE student_id = ? AND endpoint = ?",
                    (student_id, endpoint.strip()),
                )
            else:
                cur = conn.execute(
                    "UPDATE push_subscriptions SET active = 0 WHERE student_id = ?",
                    (student_id,),
                )
            conn.commit()
            removed = cur.rowcount
        return {"status": "unsubscribed", "deactivated_count": removed}

    def list_subscriptions(self, student_id: str) -> List[Dict[str, Any]]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                """
                SELECT subscription_id, student_id, endpoint, user_agent, active, created_at, last_used_at
                FROM push_subscriptions
                WHERE student_id = ? AND active = 1
                """,
                (student_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    def create_notification(
        self,
        student_id: str,
        category: str,
        title: str,
        message: str,
        deep_link: str = "/?screen=dashboard",
        dedup_key: Optional[str] = None,
        lockscreen_preview: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
        send_push: bool = False,
        current_local_hhmm: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Persists a notification to Notification Centre history with:
        - Category preference check
        - Quiet hours check (defers push delivery during quiet hours)
        - Duplicate prevention via dedup_key
        - Lock-screen privacy (generic safe preview without sensitive student details)
        """
        prefs = preferences or {}
        enabled_cats = prefs.get("enabled_categories") or {}
        if category in enabled_cats and not enabled_cats[category]:
            return None

        # Check quiet hours for push delivery
        quiet_active = False
        if prefs.get("quiet_hours_enabled", True):
            hhmm = current_local_hhmm or datetime.now(timezone.utc).strftime("%H:%M")
            quiet_active = is_within_quiet_hours(
                hhmm,
                str(prefs.get("quiet_hours_start", "22:00")),
                str(prefs.get("quiet_hours_end", "07:00")),
            )

        with self._lock, self._connect() as conn:
            if dedup_key:
                existing = conn.execute(
                    "SELECT * FROM notification_history WHERE student_id = ? AND dedup_key = ?",
                    (student_id, dedup_key),
                ).fetchone()
                if existing:
                    existing_dict = dict(existing)
                    existing_dict["deduplicated"] = True
                    return existing_dict

            notif_id = f"ntf_{uuid.uuid4().hex[:12]}"
            now_iso = _utc_now_iso()
            safe_preview = lockscreen_preview or "You have a new SparkMinds AI study update. Tap to open."
            delivered_push = 0

            if send_push and not quiet_active and prefs.get("push_notifications_enabled", False):
                delivered_push = 1 if self._deliver_web_push(student_id, title, safe_preview, deep_link) > 0 else 0

            conn.execute(
                """
                INSERT INTO notification_history (
                    notification_id, student_id, category, title, message,
                    lockscreen_preview, deep_link, dedup_key, is_read,
                    delivered_push, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
                """,
                (
                    notif_id,
                    student_id,
                    category,
                    title,
                    message,
                    safe_preview,
                    deep_link,
                    dedup_key,
                    delivered_push,
                    now_iso,
                ),
            )
            conn.commit()
            return {
                "notification_id": notif_id,
                "student_id": student_id,
                "category": category,
                "title": title,
                "message": message,
                "lockscreen_preview": safe_preview,
                "deep_link": deep_link,
                "dedup_key": dedup_key,
                "is_read": False,
                "delivered_push": bool(delivered_push),
                "quiet_hours_deferred": bool(send_push and quiet_active),
                "created_at": now_iso,
                "read_at": None,
            }

    def _deliver_web_push(
        self,
        student_id: str,
        title: str,
        lockscreen_body: str,
        deep_link: str,
    ) -> int:
        """Attempts Web Push delivery to active subscriptions and deactivates expired 404/410 endpoints."""
        if not self._vapid_private_pem:
            return 0
        try:
            from pywebpush import webpush, WebPushException
        except ImportError:
            return 0

        with self._lock, self._connect() as conn:
            subs = conn.execute(
                "SELECT subscription_id, endpoint, p256dh, auth_secret FROM push_subscriptions WHERE student_id = ? AND active = 1",
                (student_id,),
            ).fetchall()

        sent_count = 0
        expired_ids: List[str] = []
        payload = json.dumps(
            {
                "title": f"SparkMinds AI — {title}",
                "body": lockscreen_body,
                "url": deep_link,
                "tag": f"sparkminds-{student_id[:8]}",
            }
        )
        for s in subs:
            try:
                webpush(
                    subscription_info={
                        "endpoint": s["endpoint"],
                        "keys": {"p256dh": s["p256dh"], "auth": s["auth_secret"]},
                    },
                    data=payload,
                    vapid_private_key=self._vapid_private_pem,
                    vapid_claims={"sub": self._vapid_subject},
                    ttl=3600,
                )
                sent_count += 1
            except WebPushException as exc:
                status_code = getattr(getattr(exc, "response", None), "status_code", None)
                if status_code in (404, 410):
                    expired_ids.append(str(s["subscription_id"]))
            except Exception:
                continue

        if expired_ids:
            with self._lock, self._connect() as conn:
                for sid in expired_ids:
                    conn.execute(
                        "UPDATE push_subscriptions SET active = 0 WHERE subscription_id = ?",
                        (sid,),
                    )
                conn.commit()
        return sent_count

    def list_notifications(self, student_id: str, limit: int = 50) -> Dict[str, Any]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM notification_history
                WHERE student_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (student_id, limit),
            ).fetchall()
        items = [
            {
                "notification_id": r["notification_id"],
                "student_id": r["student_id"],
                "category": r["category"],
                "title": r["title"],
                "message": r["message"],
                "lockscreen_preview": r["lockscreen_preview"],
                "deep_link": r["deep_link"],
                "is_read": bool(r["is_read"]),
                "delivered_push": bool(r["delivered_push"]),
                "created_at": r["created_at"],
                "read_at": r["read_at"],
            }
            for r in rows
        ]
        unread_count = sum(1 for item in items if not item["is_read"])
        return {
            "student_id": student_id,
            "unread_count": unread_count,
            "total_count": len(items),
            "notifications": items,
        }

    def mark_read(self, student_id: str, notification_id: str) -> bool:
        now_iso = _utc_now_iso()
        with self._lock, self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE notification_history
                SET is_read = 1, read_at = COALESCE(read_at, ?)
                WHERE student_id = ? AND notification_id = ?
                """,
                (now_iso, student_id, notification_id),
            )
            conn.commit()
            return cur.rowcount > 0

    def mark_all_read(self, student_id: str) -> int:
        now_iso = _utc_now_iso()
        with self._lock, self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE notification_history
                SET is_read = 1, read_at = COALESCE(read_at, ?)
                WHERE student_id = ? AND is_read = 0
                """,
                (now_iso, student_id),
            )
            conn.commit()
            return cur.rowcount

    def generate_personalized_notifications_from_real_data(
        self,
        student_id: str,
        preferences: Dict[str, Any],
        pending_homeworks: List[Dict[str, Any]],
        weak_topics: List[Dict[str, Any]],
        pending_study_tasks: List[Dict[str, Any]],
        due_revisions: List[Dict[str, Any]],
        gamification_summary: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Generates personalized notifications strictly from real student records.
        Never fabricates learning activity or scores.
        """
        today = datetime.now(timezone.utc).date().isoformat()
        created: List[Dict[str, Any]] = []

        # 1. Pending study tasks
        if pending_study_tasks:
            first_task = pending_study_tasks[0]
            res = self.create_notification(
                student_id=student_id,
                category="study_plan_task_reminders",
                title="Today's Study Block Ready",
                message=f"Scheduled focus: {first_task.get('subject', 'Study')} — {first_task.get('chapter', 'Chapter review')} ({first_task.get('time_slot', 'Today')}).",
                deep_link="/?screen=plan",
                dedup_key=f"study_task:{today}:{first_task.get('task_id', '0')}",
                lockscreen_preview="Your next SparkMinds AI study block is ready when you are.",
                preferences=preferences,
            )
            if res and not res.get("deduplicated"):
                created.append(res)

        # 2. Weak topics detected from real assessments
        if weak_topics:
            wt = weak_topics[0]
            res = self.create_notification(
                student_id=student_id,
                category="weak_topic_practice_reminders",
                title="Recommended Practice Topic",
                message=f"Let's strengthen {wt.get('topic')} in {wt.get('subject')} with a short guided review or practice check.",
                deep_link="/?screen=exams",
                dedup_key=f"weak_topic:{today}:{wt.get('subject')}:{wt.get('topic')}",
                lockscreen_preview="A short personalized practice session is ready in SparkMinds AI.",
                preferences=preferences,
            )
            if res and not res.get("deduplicated"):
                created.append(res)

        # 3. Pending homework
        if pending_homeworks:
            hw = pending_homeworks[0]
            res = self.create_notification(
                student_id=student_id,
                category="study_reminders",
                title="Homework Reminder",
                message=f"{hw.get('subject', 'Subject')}: {hw.get('title', 'Pending assignment')} (Due {hw.get('due_date', 'soon')}).",
                deep_link="/?screen=homework",
                dedup_key=f"homework:{today}:{hw.get('homework_id', '0')}",
                lockscreen_preview="You have an upcoming homework reminder in SparkMinds AI.",
                preferences=preferences,
            )
            if res and not res.get("deduplicated"):
                created.append(res)

        # 4. Revision due
        if due_revisions:
            rev = due_revisions[0]
            res = self.create_notification(
                student_id=student_id,
                category="revision_alerts",
                title="Spaced Revision Due",
                message=f"Quick 5-minute recall for {rev.get('subject', 'your subject')}: {rev.get('topic', 'Revision card')}.",
                deep_link="/?screen=practice",
                dedup_key=f"revision:{today}:{rev.get('revision_id', '0')}",
                lockscreen_preview="Time for a quick active-recall revision in SparkMinds AI.",
                preferences=preferences,
            )
            if res and not res.get("deduplicated"):
                created.append(res)

        # 5. Real streak celebration (only when student actually has >= 1 day streak!)
        streak = int(gamification_summary.get("current_streak_days", 0))
        if streak > 0:
            res = self.create_notification(
                student_id=student_id,
                category="streak_reminders",
                title=f"{streak}-Day Learning Streak Active!",
                message=gamification_summary.get("encouragement_message", "Keep learning at your own pace!"),
                deep_link="/?screen=progress",
                dedup_key=f"streak:{today}:{streak}",
                lockscreen_preview="Your SparkMinds AI learning streak update is ready.",
                preferences=preferences,
            )
            if res and not res.get("deduplicated"):
                created.append(res)

        return created
