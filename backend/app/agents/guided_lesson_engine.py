"""
SparkMinds AI — Adaptive Guided Interactive Lesson Engine (Duolingo-Inspired Flow).

Produces short, step-by-step interactive lessons tailored to the student's grade,
school board, subject, topic, and real prior mastery:
  1. Brief learning objective
  2. One small concept at a time (with expandable detailed explanation)
  3. Subject-appropriate interactive activities:
     - MCQ (Multiple Choice)
     - MATCH_PAIRS (Match terms & definitions)
     - FILL_IN_BLANK (Quick recall)
     - ORDER_STEPS (Arrange steps in the correct sequence)
     - TRUE_FALSE (Concept check)
     - SHORT_ANSWER (Rubric-guided short answer)
     - INTERACTIVE_DIAGRAM (Clickable visual hotspots)
  4. Real backend completion tracking updating topic_mastery_records & real gamification streaks/points.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
import sqlite3
import uuid
from typing import Any, Dict, List, Optional

from app.agents.llm_utils import call_gemini_json
from app.agents.math_formatter import format_educational_text
from app.core.config import settings

logger = logging.getLogger("sparkminds.guided_lessons")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _infer_difficulty(grade: int, prior_accuracy: Optional[float]) -> str:
    if prior_accuracy is not None:
        if prior_accuracy >= 85.0:
            return "Hard"
        if prior_accuracy < 60.0:
            return "Easy"
        return "Medium"
    if grade <= 4:
        return "Easy"
    if grade <= 8:
        return "Medium"
    return "Hard"


def _select_interactive_diagram(subject: str, topic: str) -> Dict[str, Any]:
    """Returns a subject-relevant interactive clickable diagram definition."""
    sub_low = (subject or "").lower()
    top_low = (topic or "").lower()

    if "math" in sub_low or "fraction" in top_low or "number" in top_low or "algebra" in top_low:
        return {
            "step_id": "step_diagram",
            "step_type": "INTERACTIVE_DIAGRAM",
            "title": "Explore the Visual Model",
            "prompt": f"Tap each highlighted part to see how {topic} works step by step.",
            "diagram_kind": "fractions_balance",
            "hotspots": [
                {
                    "id": "part_1",
                    "label": "1. Input / Parts",
                    "x": 24,
                    "y": 50,
                    "summary": "Identify the given numbers, terms, or numerator parts clearly before calculating.",
                },
                {
                    "id": "part_2",
                    "label": "2. Common Rule",
                    "x": 52,
                    "y": 50,
                    "summary": "Match denominators/units and apply the exact mathematical rule one step at a time.",
                },
                {
                    "id": "part_3",
                    "label": "3. Balanced Result",
                    "x": 80,
                    "y": 50,
                    "summary": "Simplify your final answer and verify both sides stay equal and signs are right.",
                },
            ],
            "encouragement": "Great exploring! Visualising the parts makes solving much faster.",
        }

    if "bio" in sub_low or "science" in sub_low or "cell" in top_low or "plant" in top_low or "photo" in top_low:
        return {
            "step_id": "step_diagram",
            "step_type": "INTERACTIVE_DIAGRAM",
            "title": "Interactive Science Diagram",
            "prompt": f"Tap each part of the diagram to discover its role in {topic}.",
            "diagram_kind": "science_system",
            "hotspots": [
                {
                    "id": "part_1",
                    "label": "Energy / Input",
                    "x": 22,
                    "y": 36,
                    "summary": "Every natural process starts with an input (like sunlight, force, or reactants).",
                },
                {
                    "id": "part_2",
                    "label": "Core Process",
                    "x": 52,
                    "y": 52,
                    "summary": "The active structure (like a chloroplast, nucleus, or circuit load) transforms the input.",
                },
                {
                    "id": "part_3",
                    "label": "Output / Effect",
                    "x": 80,
                    "y": 36,
                    "summary": "Observe the measurable result (glucose & oxygen, motion, or chemical product).",
                },
            ],
            "encouragement": "Nice observation! Connecting inputs, processes, and outputs helps you remember science naturally.",
        }

    return {
        "step_id": "step_diagram",
        "step_type": "INTERACTIVE_DIAGRAM",
        "title": "Concept Map Explorer",
        "prompt": f"Tap all 3 key pillars of {topic} before continuing.",
        "diagram_kind": "concept_pillars",
        "hotspots": [
            {
                "id": "part_1",
                "label": "Core Idea",
                "x": 22,
                "y": 48,
                "summary": f"Identify the main rule, event, or principle at the heart of {topic}.",
            },
            {
                "id": "part_2",
                "label": "Real Example",
                "x": 52,
                "y": 30,
                "summary": f"Link {topic} to an everyday example so it stays clear during exams.",
            },
            {
                "id": "part_3",
                "label": "Common Trap",
                "x": 80,
                "y": 52,
                "summary": "Watch out for rushed reading or skipping intermediate steps.",
            },
        ],
        "encouragement": "Well done! You now have a clear mental map of this topic.",
    }


def _build_subject_adapted_fallback_steps(
    subject: str,
    topic: str,
    grade: int,
    difficulty: str,
) -> Dict[str, Any]:
    """
    Constructs a high-quality, grade-appropriate interactive lesson with varied
    activity formats tailored to the subject (never forcing one identical format).
    """
    sub_low = (subject or "General").lower()
    diagram_step = _select_interactive_diagram(subject, topic)

    if "math" in sub_low:
        return {
            "learning_objective": f"Understand the core rule behind {topic} and apply it accurately step by step.",
            "steps": [
                {
                    "step_id": "step_1_concept",
                    "step_type": "CONCEPT",
                    "title": f"Let's understand {topic}",
                    "short_text": f"In Grade {grade} Mathematics, solving {topic} becomes simple when you break each problem into clear, balanced steps instead of guessing.",
                    "detailed_explanation": (
                        f"Every problem in {topic} follows a logical pattern: first identify what is given and what you need to find, "
                        "next write down the exact rule or formula, compute one operation at a time keeping units/signs consistent, "
                        "and finally verify by plugging your result back in."
                    ),
                    "key_takeaway": "Write the rule first, solve one step at a time, and double-check signs.",
                },
                diagram_step,
                {
                    "step_id": "step_3_order",
                    "step_type": "ORDER_STEPS",
                    "title": "Arrange the Problem-Solving Steps",
                    "prompt": f"Put the 4 steps for solving a {topic} problem in the best order.",
                    "correct_order": [
                        "Read carefully and list the known values",
                        "Choose the right mathematical rule or formula",
                        "Calculate step by step while checking signs",
                        "Verify your final answer makes sense",
                    ],
                    "explanation": "Following a structured sequence prevents sign slips and calculation errors.",
                },
                {
                    "step_id": "step_4_fill",
                    "step_type": "FILL_IN_BLANK",
                    "title": "Quick Concept Check",
                    "prompt": "When adding fractions with different denominators, first find a common ________.",
                    "accepted_answers": ["denominator", "lcm", "multiple"],
                    "hint": "Think of the bottom number of a fraction.",
                    "explanation": "A common denominator (often the LCM) ensures all parts are the same size before adding.",
                },
                {
                    "step_id": "step_5_mcq",
                    "step_type": "MCQ",
                    "title": "Final Practice Check",
                    "prompt": f"If you get stuck halfway through a {topic} question, what is the smartest next move?",
                    "options": [
                        "Check your previous step and verify the rule or sign",
                        "Skip directly to a random number",
                        "Erase everything without checking what went wrong",
                        "Ignore the units in the question",
                    ],
                    "correct_answer": "Check your previous step and verify the rule or sign",
                    "explanation": "Checking the step right before you got stuck usually reveals a tiny sign or arithmetic slip!",
                },
            ],
        }

    if any(k in sub_low for k in ("science", "physics", "chem", "bio", "evs")):
        return {
            "learning_objective": f"Connect how {topic} works in real life and identify its key parts accurately.",
            "steps": [
                {
                    "step_id": "step_1_concept",
                    "step_type": "CONCEPT",
                    "title": f"Discover {topic}",
                    "short_text": f"In Grade {grade} {subject}, {topic} explains how energy, matter, or living systems interact in a predictable cause-and-effect cycle.",
                    "detailed_explanation": (
                        f"To master {topic}, always ask three questions: (1) What triggers the process? "
                        "(2) What transformation happens during the process? (3) What observable output or real-world effect does it produce? "
                        "Using labeled diagrams alongside concise scientific terms helps you recall facts accurately in exams."
                    ),
                    "key_takeaway": "Link every scientific term to its function and a real-world observation.",
                },
                diagram_step,
                {
                    "step_id": "step_3_match",
                    "step_type": "MATCH_PAIRS",
                    "title": "Match the Scientific Pairs",
                    "prompt": "Tap a term on the left, then tap its matching meaning on the right.",
                    "pairs": [
                        {"left": "Hypothesis", "right": "A testable scientific prediction"},
                        {"left": "Observation", "right": "Information gathered using senses or tools"},
                        {"left": "Variable", "right": "A factor that can change in an experiment"},
                    ],
                    "explanation": "Understanding core scientific terms makes every chapter in Science easier to follow.",
                },
                {
                    "step_id": "step_4_tf",
                    "step_type": "TRUE_FALSE",
                    "title": "True or False?",
                    "prompt": f"Scientific conclusions about {topic} should always be supported by evidence and repeatable observations.",
                    "correct_answer": "True",
                    "explanation": "Evidence and repeatable observation are the foundation of all scientific understanding.",
                },
                {
                    "step_id": "step_5_short",
                    "step_type": "SHORT_ANSWER",
                    "title": "Explain in Your Own Words",
                    "prompt": f"In one short sentence, name one real-world example or reason why {topic} matters.",
                    "rubric_keywords": ["because", "help", "energy", "life", "nature", "change", "use", "work", "process"],
                    "sample_answer": f"{topic} helps explain how everyday natural processes work around us.",
                    "explanation": "Explaining a concept in your own words is one of the strongest ways to build lasting memory.",
                },
            ],
        }

    if any(k in sub_low for k in ("english", "hindi", "telugu", "tamil", "kannada", "grammar", "language")):
        return {
            "learning_objective": f"Build clarity and confidence using {topic} in reading and writing.",
            "steps": [
                {
                    "step_id": "step_1_concept",
                    "step_type": "CONCEPT",
                    "title": f"Mastering {topic}",
                    "short_text": f"Clear communication in {topic} starts with noticing how word choice and sentence structure carry meaning.",
                    "detailed_explanation": (
                        f"When practicing {topic} for Grade {grade}, read your sentence aloud to check flow, "
                        "verify subject-verb agreement and tense consistency, and choose specific words rather than vague ones."
                    ),
                    "key_takeaway": "Read each sentence aloud to spot missing clarity or agreement issues quickly.",
                },
                {
                    "step_id": "step_2_match",
                    "step_type": "MATCH_PAIRS",
                    "title": "Match Language Building Blocks",
                    "prompt": "Pair each grammar element with what it does in a sentence.",
                    "pairs": [
                        {"left": "Verb", "right": "Shows action or state of being"},
                        {"left": "Adjective", "right": "Describes a noun"},
                        {"left": "Conjunction", "right": "Connects words or clauses"},
                    ],
                    "explanation": "Recognizing each part of speech helps you construct clear, accurate sentences.",
                },
                {
                    "step_id": "step_3_fill",
                    "step_type": "FILL_IN_BLANK",
                    "title": "Fill in the Blank",
                    "prompt": "A complete sentence must have a subject and a ________ (action/state word).",
                    "accepted_answers": ["verb", "predicate"],
                    "hint": "What word tells us what the subject is doing?",
                    "explanation": "Every complete sentence pairs a subject with a verb (predicate).",
                },
                {
                    "step_id": "step_4_short",
                    "step_type": "SHORT_ANSWER",
                    "title": "Quick Writing Practice",
                    "prompt": f"Write one clear sentence using what you just learned about {topic}.",
                    "rubric_keywords": ["the", "is", "are", "was", "to", "and", "in", "a"],
                    "sample_answer": f"Practicing {topic} every day makes my writing clearer and easier to read.",
                    "explanation": "Great effort! Short daily writing builds natural fluency.",
                },
            ],
        }

    # Social Science / History / Geography / Computer Science / General
    return {
        "learning_objective": f"Understand the main ideas of {topic} and connect causes, sequence, and impact.",
        "steps": [
            {
                "step_id": "step_1_concept",
                "step_type": "CONCEPT",
                "title": f"Explore {topic}",
                "short_text": f"Let's break {topic} down into clear cause-and-effect points so you can remember it without rote memorization.",
                "detailed_explanation": (
                    f"For Grade {grade} {subject}, focus on WHO or WHAT is involved in {topic}, "
                    "WHY it happened or how it works, and WHAT changed as a result. Grouping facts into a short timeline or map makes revision effortless."
                ),
                "key_takeaway": "Focus on Cause → Key Event/Mechanism → Impact.",
            },
            diagram_step,
            {
                "step_id": "step_3_order",
                "step_type": "ORDER_STEPS",
                "title": "Put the Learning Flow in Order",
                "prompt": f"Arrange the best sequence for analyzing any topic in {subject}.",
                "correct_order": [
                    "Identify the main concept or event",
                    "Understand the key causes or inputs",
                    "Examine the outcome or real-world impact",
                ],
                "explanation": "Connecting cause to outcome builds strong analytical answers.",
            },
            {
                "step_id": "step_4_tf",
                "step_type": "TRUE_FALSE",
                "title": "Quick Check",
                "prompt": f"Connecting {topic} to causes and real-world examples helps you retain it longer than memorizing isolated lines.",
                "correct_answer": "True",
                "explanation": "Meaningful connections make recall faster during exams and class discussions.",
            },
            {
                "step_id": "step_5_mcq",
                "step_type": "MCQ",
                "title": "Wrap-Up Check",
                "prompt": f"What is the best way to revise {topic} before an exam?",
                "options": [
                    "Summarize key causes, effects, and test yourself with recall questions",
                    "Read the page once without checking understanding",
                    "Skip difficult terms completely",
                    "Wait until the morning of the exam",
                ],
                "correct_answer": "Summarize key causes, effects, and test yourself with recall questions",
                "explanation": "Active recall + short summaries lock concepts into long-term memory.",
            },
        ],
    }


def _sanitize_lesson_step(step: Dict[str, Any], idx: int) -> Optional[Dict[str, Any]]:
    """Validate and clean a generated lesson step so malformed AI steps never break the UI."""
    if not isinstance(step, dict):
        return None
    stype = str(step.get("step_type") or "").upper()
    if stype not in ("CONCEPT", "MCQ", "MATCH_PAIRS", "FILL_IN_BLANK", "ORDER_STEPS", "TRUE_FALSE", "SHORT_ANSWER"):
        return None
    clean: Dict[str, Any] = dict(step)
    clean["step_id"] = str(step.get("step_id") or f"s_{idx + 1}")
    clean["step_type"] = stype
    clean["title"] = format_educational_text(str(step.get("title") or f"Step {idx + 1}"))
    for text_key in ("short_text", "detailed_explanation", "key_takeaway", "prompt", "hint", "sample_answer", "explanation"):
        if text_key in clean and isinstance(clean[text_key], str):
            clean[text_key] = format_educational_text(clean[text_key])

    if stype == "MCQ":
        opts = [format_educational_text(str(o)) for o in (step.get("options") or []) if str(o).strip()]
        ans = format_educational_text(str(step.get("correct_answer") or ""))
        if len(opts) < 2 or not ans:
            return None
        if ans not in opts:
            opts[0] = ans
        clean["options"] = opts[:4]
        clean["correct_answer"] = ans
    elif stype == "MATCH_PAIRS":
        pairs = [
            {"left": format_educational_text(str(p["left"])), "right": format_educational_text(str(p["right"]))}
            for p in (step.get("pairs") or [])
            if isinstance(p, dict) and p.get("left") and p.get("right")
        ]
        if len(pairs) < 2:
            return None
        clean["pairs"] = pairs[:4]
    elif stype == "FILL_IN_BLANK":
        acc = [format_educational_text(str(a)) for a in (step.get("accepted_answers") or []) if str(a).strip()]
        if not acc:
            return None
        clean["accepted_answers"] = acc
    elif stype == "ORDER_STEPS":
        order = [format_educational_text(str(o)) for o in (step.get("correct_order") or []) if str(o).strip()]
        if len(order) < 2:
            return None
        clean["correct_order"] = order
    elif stype == "TRUE_FALSE":
        ans = "False" if str(step.get("correct_answer", "True")).strip().lower() == "false" else "True"
        clean["correct_answer"] = ans
    return clean


def _try_gemini_guided_lesson(
    subject: str,
    topic: str,
    grade: int,
    board: str,
    difficulty: str,
    preferred_language: str,
) -> Optional[Dict[str, Any]]:
    prompt = (
        f"Design a short, friendly, Duolingo-inspired interactive lesson for an individual Grade {grade} ({board}) student.\n"
        f"Subject: {subject}\nTopic: {topic}\nDifficulty: {difficulty}\n"
        f"Preferred explanation language: {preferred_language} (keep JSON keys in English).\n"
        "Rules:\n"
        "- Keep instructions short, friendly, and clear (1-2 sentences each), while keeping detailed_explanation thorough.\n"
        "- Format all math cleanly using Unicode symbols (×, ÷, √, π, x², 3/4, °) and NEVER wrap formulas in raw $...$ or LaTeX macros.\n"
        "- For MCQ, correct_answer MUST exactly match one of the options strings.\n"
        "- Return STRICT JSON ONLY matching this exact schema:\n"
        "{\n"
        '  "learning_objective": "short 1-sentence objective",\n'
        '  "steps": [\n'
        '    {"step_id": "s1", "step_type": "CONCEPT", "title": "...", "short_text": "2 short sentences", "detailed_explanation": "thorough clear explanation", "key_takeaway": "1 short line"},\n'
        '    {"step_id": "s2", "step_type": "MCQ", "title": "...", "prompt": "...", "options": ["A", "B", "C", "D"], "correct_answer": "exact option string", "explanation": "simple explanation"},\n'
        '    {"step_id": "s3", "step_type": "MATCH_PAIRS", "title": "...", "prompt": "...", "pairs": [{"left": "...", "right": "..."}, {"left": "...", "right": "..."}, {"left": "...", "right": "..."}], "explanation": "..."},\n'
        '    {"step_id": "s4", "step_type": "FILL_IN_BLANK", "title": "...", "prompt": "Sentence with ________ blank.", "accepted_answers": ["answer1"], "hint": "short hint", "explanation": "..."},\n'
        '    {"step_id": "s5", "step_type": "TRUE_FALSE", "title": "...", "prompt": "Clear statement.", "correct_answer": "True", "explanation": "..."}\n'
        "  ]\n"
        "}\n"
        "You may substitute ORDER_STEPS (with correct_order: [3-4 strings]) or SHORT_ANSWER (with rubric_keywords, sample_answer) where it fits the subject better."
    )
    res = call_gemini_json(prompt=prompt, temperature=0.35, max_output_tokens=2600)
    if not res:
        return None
    parsed, model_used = res
    if isinstance(parsed, dict) and isinstance(parsed.get("steps"), list):
        validated_steps = [
            s for idx, raw_s in enumerate(parsed["steps"])
            for s in [_sanitize_lesson_step(raw_s, idx)]
            if s is not None
        ]
        if len(validated_steps) >= 3:
            diagram = _select_interactive_diagram(subject, topic)
            validated_steps.insert(1, diagram)
            return {
                "learning_objective": format_educational_text(
                    str(
                        parsed.get("learning_objective")
                        or f"Master the core concepts of {topic} step by step."
                    )
                ),
                "steps": validated_steps,
                "generation_source": f"gemini_ai:{model_used}",
            }
    return None


def generate_guided_lesson(
    repo: Any,
    student_id: str,
    subject: str,
    topic: str,
    preferred_language: Optional[str] = None,
) -> Dict[str, Any]:
    student = repo.students.get(student_id) or {}
    grade = int(student.get("current_grade", 7))
    board = str(student.get("school_board", "CBSE"))
    lang = preferred_language or (student.get("language_preferences") or {}).get(
        "preferred_explanation_language", "English"
    )

    # Check prior topic mastery to adapt difficulty honestly
    prior_accuracy: Optional[float] = None
    try:
        with sqlite3.connect(str(repo.sqlite_db_path), timeout=10.0) as conn:
            row = conn.execute(
                "SELECT accuracy_percentage FROM topic_mastery_records WHERE student_id = ? AND lower(subject) = lower(?) AND lower(topic) = lower(?)",
                (student_id, subject, topic),
            ).fetchone()
            if row and row[0] is not None:
                prior_accuracy = float(row[0])
    except Exception:
        pass

    difficulty = _infer_difficulty(grade, prior_accuracy)
    lesson_payload = _try_gemini_guided_lesson(
        subject=subject,
        topic=topic,
        grade=grade,
        board=board,
        difficulty=difficulty,
        preferred_language=lang,
    )
    if not lesson_payload:
        lesson_payload = _build_subject_adapted_fallback_steps(
            subject=subject,
            topic=topic,
            grade=grade,
            difficulty=difficulty,
        )
        lesson_payload["generation_source"] = "curriculum_adaptive_engine"

    lesson_id = f"les_{uuid.uuid4().hex[:10]}"
    return {
        "lesson_id": lesson_id,
        "student_id": student_id,
        "subject": subject,
        "topic": topic,
        "grade": grade,
        "board": board,
        "difficulty": difficulty,
        "prior_mastery_percentage": prior_accuracy,
        "preferred_language": lang,
        "estimated_minutes": max(4, len(lesson_payload["steps"])),
        "learning_objective": lesson_payload["learning_objective"],
        "steps": lesson_payload["steps"],
        "generation_source": lesson_payload["generation_source"],
        "created_at": _utc_now_iso(),
    }


def complete_guided_lesson(
    repo: Any,
    student_id: str,
    lesson_id: str,
    subject: str,
    topic: str,
    correct_count: int,
    total_interactive_steps: int,
) -> Dict[str, Any]:
    """
    Records genuine lesson completion:
    - Updates topic_mastery_records in SQLite with real accuracy
    - Logs real gamification activity ('lesson_completed') so streaks & badges reflect real work
    - Never fabricates points or achievements
    """
    safe_total = max(1, int(total_interactive_steps))
    safe_correct = max(0, min(safe_total, int(correct_count)))
    accuracy = round((safe_correct / safe_total) * 100.0, 1)
    now_iso = _utc_now_iso()

    # Update topic_mastery_records cleanly matching the exact SQLite schema
    # (attempts_count = total evaluated items, correct_count = total correct items, updated_at NOT NULL)
    try:
        with sqlite3.connect(str(repo.sqlite_db_path), timeout=10.0) as conn:
            row = conn.execute(
                "SELECT attempts_count, correct_count, repeated_mistakes_json FROM topic_mastery_records WHERE student_id = ? AND subject = ? AND topic = ?",
                (student_id, subject, topic),
            ).fetchone()
            if row:
                prev_attempts = int(row[0] or 0)
                prev_correct = int(row[1] or 0)
                new_attempts = prev_attempts + safe_total
                new_correct = prev_correct + safe_correct
                cumulative_acc = round((new_correct / max(1, new_attempts)) * 100.0, 1)
                blended_acc = round((0.6 * accuracy) + (0.4 * cumulative_acc), 1)
                status = (
                    "Understood"
                    if blended_acc >= 80
                    else "Partially Understood"
                    if blended_acc >= 60
                    else "Needs Help"
                )
                prev_mistakes = row[2] or "[]"
                updated_mistakes = "[]" if (blended_acc >= 80 and accuracy >= 80) else prev_mistakes
                conn.execute(
                    """
                    UPDATE topic_mastery_records
                    SET attempts_count = ?, correct_count = ?,
                        accuracy_percentage = ?, status = ?, repeated_mistakes_json = ?,
                        last_assessed_at = ?, updated_at = ?
                    WHERE student_id = ? AND subject = ? AND topic = ?
                    """,
                    (
                        new_attempts,
                        new_correct,
                        blended_acc,
                        status,
                        updated_mistakes,
                        now_iso,
                        now_iso,
                        student_id,
                        subject,
                        topic,
                    ),
                )
            else:
                status = (
                    "Understood"
                    if accuracy >= 80
                    else "Partially Understood"
                    if accuracy >= 60
                    else "Needs Help"
                )
                conn.execute(
                    """
                    INSERT INTO topic_mastery_records (
                        student_id, subject, topic, status, accuracy_percentage,
                        attempts_count, correct_count, repeated_mistakes_json,
                        last_assessed_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, '[]', ?, ?)
                    """,
                    (
                        student_id,
                        subject,
                        topic,
                        status,
                        accuracy,
                        safe_total,
                        safe_correct,
                        now_iso,
                        now_iso,
                    ),
                )
            conn.commit()
    except Exception as exc:
        logger.warning("Failed updating topic_mastery_records for lesson completion: %s", type(exc).__name__)

    # Real points awarded strictly based on genuine lesson completion
    points_earned = 25 if accuracy >= 80 else 20 if accuracy >= 50 else 15
    gamif = repo.gamification.record_activity(
        student_id=student_id,
        activity_type="lesson_completed",
        subject=subject,
        topic=topic,
        points=points_earned,
        metadata={
            "lesson_id": lesson_id,
            "correct_count": safe_correct,
            "total_interactive_steps": safe_total,
            "accuracy_percentage": accuracy,
        },
    )

    if accuracy >= 85:
        encouragement = "Excellent work! You've completed this lesson with strong understanding."
    elif accuracy >= 60:
        encouragement = "Great job! You're getting better — ready for the next challenge?"
    else:
        encouragement = "You finished the lesson! Every try builds stronger understanding — review once more whenever you're ready."

    return {
        "status": "lesson_completed",
        "lesson_id": lesson_id,
        "subject": subject,
        "topic": topic,
        "correct_count": safe_correct,
        "total_interactive_steps": safe_total,
        "accuracy_percentage": accuracy,
        "points_earned": points_earned,
        "encouragement": encouragement,
        "gamification": gamif,
        "completed_at": now_iso,
    }
