"""
SparkMinds AI — Real Data-Driven Gamification, Streaks, Points, Badges & Daily Challenges.
Guarantees:
- Streaks are calculated strictly from real logged learning activity dates (never hardcoded!).
- Milestones supported: 3-day, 7-day, 15-day, and 30-day streaks.
- Badges and achievements are deduplicated per student via SQLite primary keys.
- Messaging is always positive, encouraging, and never shaming or discouraging.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import json
import sqlite3
import threading
import uuid
from typing import Any, Dict, List, Optional


STREAK_MILESTONES = [
    (3, "streak_3_day", "3-Day Spark Starter", "Learned consistently for 3 days in a row!"),
    (7, "streak_7_day", "7-Day Steady Learner", "Maintained a full week of real learning activity!"),
    (15, "streak_15_day", "15-Day Focus Champion", "Fifteen days of dedication and curiosity!"),
    (30, "streak_30_day", "30-Day Mastery Legend", "An entire month of consistent learning progress!"),
]

ACTIVITY_POINTS = {
    "tutor_session": 15,
    "lesson_completed": 25,
    "diagnostic_completed": 25,
    "assessment_completed": 25,
    "homework_completed": 20,
    "revision_reviewed": 15,
    "study_task_completed": 15,
    "document_studied": 15,
    "daily_checkin": 10,
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


class GamificationService:
    def __init__(self, sqlite_db_path: str) -> None:
        self.sqlite_db_path = sqlite_db_path
        self._lock = threading.RLock()
        self._ensure_tables()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.sqlite_db_path, timeout=15.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_tables(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_activity_log (
                    activity_id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    activity_type TEXT NOT NULL,
                    activity_date TEXT NOT NULL,
                    subject TEXT,
                    topic TEXT,
                    points INTEGER NOT NULL DEFAULT 10,
                    metadata_json TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_activity_student_date ON learning_activity_log(student_id, activity_date)"
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS gamification_badges (
                    student_id TEXT NOT NULL,
                    badge_key TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL,
                    earned_at TEXT NOT NULL,
                    PRIMARY KEY (student_id, badge_key)
                )
                """
            )
            conn.commit()

    def record_activity(
        self,
        student_id: str,
        activity_type: str,
        subject: Optional[str] = None,
        topic: Optional[str] = None,
        points: Optional[int] = None,
        activity_date: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Logs a genuine student learning activity and evaluates any newly unlocked badges."""
        clean_date = (activity_date or _today_iso())[:10]
        try:
            date.fromisoformat(clean_date)
        except ValueError:
            clean_date = _today_iso()

        pts = points if points is not None else ACTIVITY_POINTS.get(activity_type, 10)
        activity_id = f"act_{uuid.uuid4().hex[:12]}"
        now_iso = _utc_now_iso()

        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO learning_activity_log (
                    activity_id, student_id, activity_type, activity_date,
                    subject, topic, points, metadata_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    activity_id,
                    student_id,
                    activity_type,
                    clean_date,
                    subject,
                    topic,
                    int(pts),
                    json.dumps(metadata or {}),
                    now_iso,
                ),
            )
            conn.commit()

        newly_awarded = self._evaluate_and_award_badges(student_id)
        summary = self.get_student_gamification_summary(student_id)
        summary["last_recorded_activity"] = {
            "activity_id": activity_id,
            "activity_type": activity_type,
            "activity_date": clean_date,
            "points": int(pts),
        }
        summary["newly_awarded_badges"] = newly_awarded
        return summary

    def _compute_streaks_from_dates(
        self, unique_dates_iso: List[str], reference_date: Optional[date] = None
    ) -> Dict[str, int]:
        if not unique_dates_iso:
            return {"current_streak_days": 0, "longest_streak_days": 0}

        parsed = sorted({date.fromisoformat(d[:10]) for d in unique_dates_iso})
        longest = 1
        run = 1
        for i in range(1, len(parsed)):
            if (parsed[i] - parsed[i - 1]).days == 1:
                run += 1
                if run > longest:
                    longest = run
            else:
                run = 1

        today = reference_date or datetime.now(timezone.utc).date()
        date_set = set(parsed)
        # Current streak counts if active today OR yesterday (so evening/morning timezone shifts don't abruptly wipe it mid-day)
        anchor = today if today in date_set else (today - timedelta(days=1) if (today - timedelta(days=1)) in date_set else None)
        current = 0
        if anchor is not None:
            cursor = anchor
            while cursor in date_set:
                current += 1
                cursor -= timedelta(days=1)

        return {"current_streak_days": current, "longest_streak_days": longest}

    def _award_badge_if_missing(
        self,
        conn: sqlite3.Connection,
        student_id: str,
        badge_key: str,
        title: str,
        description: str,
        category: str,
    ) -> Optional[Dict[str, str]]:
        exists = conn.execute(
            "SELECT 1 FROM gamification_badges WHERE student_id = ? AND badge_key = ?",
            (student_id, badge_key),
        ).fetchone()
        if exists:
            return None
        now_iso = _utc_now_iso()
        conn.execute(
            """
            INSERT INTO gamification_badges (student_id, badge_key, title, description, category, earned_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (student_id, badge_key, title, description, category, now_iso),
        )
        return {
            "badge_key": badge_key,
            "title": title,
            "description": description,
            "category": category,
            "earned_at": now_iso,
        }

    def _evaluate_and_award_badges(self, student_id: str) -> List[Dict[str, str]]:
        awarded: List[Dict[str, str]] = []
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT activity_type, activity_date, points FROM learning_activity_log WHERE student_id = ?",
                (student_id,),
            ).fetchall()
            if not rows:
                return awarded

            unique_dates = [str(r["activity_date"]) for r in rows]
            streaks = self._compute_streaks_from_dates(unique_dates)
            best_streak = max(streaks["current_streak_days"], streaks["longest_streak_days"])
            total_points = sum(int(r["points"] or 0) for r in rows)
            counts: Dict[str, int] = {}
            for r in rows:
                t = str(r["activity_type"])
                counts[t] = counts.get(t, 0) + 1

            # First step milestone
            if len(rows) >= 1:
                b = self._award_badge_if_missing(
                    conn,
                    student_id,
                    "first_learning_step",
                    "First Spark Unlocked",
                    "Completed your first real learning activity on SparkMinds AI!",
                    "milestone",
                )
                if b:
                    awarded.append(b)

            # Streak milestones: 3, 7, 15, 30 days
            for days_req, key, title, desc in STREAK_MILESTONES:
                if best_streak >= days_req:
                    b = self._award_badge_if_missing(conn, student_id, key, title, desc, "streak")
                    if b:
                        awarded.append(b)

            # Activity-specific achievements
            if counts.get("diagnostic_completed", 0) >= 1:
                b = self._award_badge_if_missing(
                    conn,
                    student_id,
                    "diagnostic_explorer",
                    "Self-Discovery Explorer",
                    "Completed a diagnostic check to map out your strengths and next steps.",
                    "assessment",
                )
                if b:
                    awarded.append(b)

            if counts.get("assessment_completed", 0) >= 3:
                b = self._award_badge_if_missing(
                    conn,
                    student_id,
                    "quiz_challenger_3",
                    "Practice Builder",
                    "Completed 3 practice assessments with feedback review.",
                    "assessment",
                )
                if b:
                    awarded.append(b)

            if counts.get("document_studied", 0) >= 1:
                b = self._award_badge_if_missing(
                    conn,
                    student_id,
                    "document_scholar",
                    "Note Explorer",
                    "Uploaded and studied directly from your own learning notes.",
                    "study_habit",
                )
                if b:
                    awarded.append(b)

            if total_points >= 100:
                b = self._award_badge_if_missing(
                    conn,
                    student_id,
                    "century_points",
                    "100 Learning Points",
                    "Earned 100 learning points through genuine study effort!",
                    "points",
                )
                if b:
                    awarded.append(b)

            conn.commit()
        return awarded

    def get_student_gamification_summary(self, student_id: str) -> Dict[str, Any]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                """
                SELECT activity_id, activity_type, activity_date, subject, topic, points, created_at
                FROM learning_activity_log
                WHERE student_id = ?
                ORDER BY activity_date DESC, created_at DESC
                """,
                (student_id,),
            ).fetchall()
            badge_rows = conn.execute(
                """
                SELECT badge_key, title, description, category, earned_at
                FROM gamification_badges
                WHERE student_id = ?
                ORDER BY earned_at DESC
                """,
                (student_id,),
            ).fetchall()

        unique_dates = sorted({str(r["activity_date"]) for r in rows})
        streaks = self._compute_streaks_from_dates(unique_dates)
        current_streak = streaks["current_streak_days"]
        longest_streak = streaks["longest_streak_days"]
        total_points = sum(int(r["points"] or 0) for r in rows)
        today_str = _today_iso()
        today_activities = [r for r in rows if str(r["activity_date"]) == today_str]
        today_types = {str(r["activity_type"]) for r in today_activities}

        # Next streak milestone
        next_milestone = next(
            (days for days, _, _, _ in STREAK_MILESTONES if current_streak < days),
            30,
        )

        # Positive, supportive encouraging message (never shaming!)
        if current_streak == 0:
            encouragement = (
                "Every learning journey starts with one small step. Complete a quick concept check, "
                "tutor question, or study task today to start your streak!"
            )
        elif current_streak < 3:
            encouragement = (
                f"Great momentum! You're on a {current_streak}-day streak — just {3 - current_streak} "
                "more day(s) to unlock the 3-Day Spark Starter milestone."
            )
        elif current_streak < 7:
            encouragement = (
                f"Wonderful consistency! {current_streak} days strong — keep learning at your own pace "
                f"toward the 7-Day Steady Learner badge."
            )
        elif current_streak < 15:
            encouragement = (
                f"Awesome dedication! You have a {current_streak}-day learning streak. "
                "Small daily habits build lasting understanding."
            )
        else:
            encouragement = (
                f"Remarkable consistency with a {current_streak}-day learning streak! "
                "Take healthy breaks and celebrate how much you've grown."
            )

        daily_challenges = [
            {
                "challenge_id": "dc_concept_check",
                "title": "Ask or explore one concept with your AI Tutor",
                "points": 15,
                "completed": "tutor_session" in today_types,
            },
            {
                "challenge_id": "dc_practice_quiz",
                "title": "Complete one practice quiz or diagnostic check",
                "points": 25,
                "completed": bool(
                    {"assessment_completed", "diagnostic_completed"} & today_types
                ),
            },
            {
                "challenge_id": "dc_plan_task",
                "title": "Finish one study plan block, homework, or revision card",
                "points": 15,
                "completed": bool(
                    {"study_task_completed", "homework_completed", "revision_reviewed"} & today_types
                ),
            },
        ]

        level = max(1, (total_points // 100) + 1)
        points_into_level = total_points % 100

        return {
            "student_id": student_id,
            "current_streak_days": current_streak,
            "longest_streak_days": longest_streak,
            "total_learning_points": total_points,
            "level": level,
            "points_to_next_level": 100 - points_into_level,
            "active_days_count": len(unique_dates),
            "total_activities_logged": len(rows),
            "next_streak_milestone_days": next_milestone,
            "streak_milestones": [
                {
                    "days": d,
                    "badge_key": k,
                    "title": t,
                    "achieved": max(current_streak, longest_streak) >= d,
                }
                for d, k, t, _ in STREAK_MILESTONES
            ],
            "badges": [dict(b) for b in badge_rows],
            "daily_challenges": daily_challenges,
            "encouragement_message": encouragement,
            "recent_activities": [dict(r) for r in rows[:10]],
        }
