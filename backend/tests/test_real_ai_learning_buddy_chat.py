"""
SparkMinds AI — Real AI Learning Buddy Chat Tests

Part A (always runs): verifies the request flow, history handling, isolation and error surfacing
by injecting a recording generator in place of the provider (no fake answers reach production —
the injected generator only exists inside these tests).

Part B (LIVE): sends the user's 10 mixed questions in ONE conversation to the real Gemini model.
Runs when a provider key is configured (skips otherwise). Set SPARKMINDS_SKIP_LIVE_AI=1 to skip.
"""
import os
import re

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.agents import chat_tutor
from app.agents.chat_tutor import chat_tutor_engine, is_provider_configured

client = TestClient(app)


# ---------------------------------------------------------------------------
# Part A — flow, history, isolation, error handling
# ---------------------------------------------------------------------------
class _Recorder:
    def __init__(self):
        self.calls = []
        self.fail_next = False

    def __call__(self, system_instruction, history, message, image_b64, mime):
        self.calls.append({"system": system_instruction, "history": list(history), "message": message})
        if self.fail_next:
            self.fail_next = False
            raise chat_tutor.ChatProviderError("Simulated upstream outage")
        return {"text": f"ANSWER#{len(self.calls)} to: {message}", "model": "recorder"}


@pytest.fixture
def recorder(monkeypatch):
    rec = _Recorder()
    monkeypatch.setattr(chat_tutor_engine, "generate_fn", rec)
    monkeypatch.setattr(chat_tutor, "is_provider_configured", lambda: True)
    return rec


def test_every_message_is_forwarded_with_history(recorder):
    r1 = client.post("/api/tutor/chat", json={"student_id": "stu_aarav_g7", "message": "What are fractions?"})
    assert r1.status_code == 200, r1.text
    conv = r1.json()["conversation_id"]
    assert r1.json()["reply"]["content"] == "ANSWER#1 to: What are fractions?"

    for i, q in enumerate(["Give me an example.", "What if I eat two pieces?"], start=2):
        r = client.post("/api/tutor/chat", json={"student_id": "stu_aarav_g7", "message": q, "conversation_id": conv})
        assert r.status_code == 200
        assert r.json()["reply"]["content"] == f"ANSWER#{i} to: {q}"

    # Third call must carry the previous 4 messages as context
    third = recorder.calls[2]
    assert [m["content"] for m in third["history"]] == [
        "What are fractions?", "ANSWER#1 to: What are fractions?",
        "Give me an example.", "ANSWER#2 to: Give me an example.",
    ]
    # Student grade/board are injected into the system prompt
    assert "Grade 7" in third["system"]


def test_ten_consecutive_messages_and_new_conversation(recorder):
    conv = None
    for i in range(10):
        r = client.post("/api/tutor/chat", json={"student_id": "stu_diya_g4", "message": f"Question {i}", "conversation_id": conv})
        assert r.status_code == 200
        conv = r.json()["conversation_id"]
    assert r.json()["turn_count"] == 10

    fresh = client.post("/api/tutor/chat", json={"student_id": "stu_diya_g4", "message": "Hello again"})
    assert fresh.json()["conversation_id"] != conv
    assert recorder.calls[-1]["history"] == []


def test_failed_request_is_reported_and_retry_works(recorder):
    r1 = client.post("/api/tutor/chat", json={"student_id": "stu_aarav_g7", "message": "Why is the sky blue?"})
    conv = r1.json()["conversation_id"]
    recorder.fail_next = True
    failed = client.post("/api/tutor/chat", json={"student_id": "stu_aarav_g7", "message": "And sunsets?", "conversation_id": conv})
    assert failed.status_code == 502
    assert "No answer was generated" in failed.json()["detail"]
    # Failed turn is not stored; retry succeeds and history has only the first exchange
    retry = client.post("/api/tutor/chat", json={"student_id": "stu_aarav_g7", "message": "And sunsets?", "conversation_id": conv})
    assert retry.status_code == 200
    assert len(recorder.calls[-1]["history"]) == 2


def test_conversations_are_isolated_between_students(recorder):
    r = client.post("/api/tutor/chat", json={"student_id": "stu_aarav_g7", "message": "private question"})
    conv = r.json()["conversation_id"]
    other = client.post("/api/tutor/chat", json={"student_id": "stu_karthik_g10", "message": "hi there", "conversation_id": conv})
    assert other.status_code == 404
    assert client.get(f"/api/tutor/chat/{conv}", params={"student_id": "stu_karthik_g10"}).status_code == 404
    assert client.get(f"/api/tutor/chat/{conv}", params={"student_id": "stu_aarav_g7"}).status_code == 200


def test_missing_api_key_returns_clear_error(monkeypatch):
    monkeypatch.setattr(chat_tutor, "is_provider_configured", lambda: False)
    r = client.post("/api/tutor/chat", json={"student_id": "stu_aarav_g7", "message": "What is 2+2?"})
    assert r.status_code == 503
    assert "not configured" in r.json()["detail"]


def test_empty_message_rejected():
    r = client.post("/api/tutor/chat", json={"student_id": "stu_aarav_g7", "message": "   "})
    assert r.status_code == 400


# ---------------------------------------------------------------------------
# Part B — LIVE test against the real AI model (same conversation, 10 questions)
# ---------------------------------------------------------------------------
LIVE_QUESTIONS = [
    ("What is 25 × 16?", lambda a: "400" in a),
    ("Explain photosynthesis in simple words.", lambda a: any(w in a.lower() for w in ("sunlight", "light", "photo", "సూర్య", "ఆహార"))),
    ("Who was the first Prime Minister of India?", lambda a: "nehru" in a.lower() or "నెహ్రూ" in a or "jawaharlal" in a.lower()),
    ("What is a metaphor?", lambda a: any(w in a.lower() for w in ("compar", "metaphor", "figure", "రూపక"))),
    ("Why does ice float on water?", lambda a: any(w in a.lower() for w in ("dens", "float", "ice", "సాంద్రత", "తేలు"))),
    ("Explain fractions with an example.", lambda a: any(w in a.lower() for w in ("fraction", "numerator", "denominator", "part", "భిన్న", "pizza")) or re.search(r"\d+\s*/\s*\d+", a) is not None),
    ("What is the difference between weather and climate?", lambda a: any(w in a.lower() for w in ("climate", "weather", "atmosphere", "వాతావరణ", "శీతోష్ణస్థితి"))),
    ("Write a simple Python program to add two numbers.", lambda a: "+" in a and any(w in a.lower() for w in ("print", "sum", "python", "num"))),
    ("Explain the answer to question 1 in another way.", lambda a: "400" in a),
    ("Give me three practice questions about photosynthesis.", lambda a: any(w in a.lower() for w in ("photo", "question", "కిరణజన్య", "1.", "1)"))),
]


@pytest.mark.skipif(
    not is_provider_configured() or os.getenv("SPARKMINDS_SKIP_LIVE_AI") == "1",
    reason="No AI provider key configured (live test)",
)
def test_live_ten_mixed_questions_in_one_conversation():
    import json
    import time
    from pathlib import Path

    conv = None
    answers = []
    transcript = []
    for idx, (question, check) in enumerate(LIVE_QUESTIONS):
        if idx:
            time.sleep(float(os.getenv("SPARKMINDS_LIVE_AI_PACING_SECONDS", "7")))  # respect free-tier RPM
        r = client.post("/api/tutor/chat", json={"student_id": "stu_aarav_g7", "message": question, "conversation_id": conv})
        assert r.status_code == 200, f"{question} -> {r.status_code} {r.text[:300]}"
        data = r.json()
        conv = data["conversation_id"]
        answer = data["reply"]["content"]
        transcript.append({"q": question, "model": data["model_used"], "a": answer})
        Path(__file__).with_name("live_chat_transcript.json").write_text(json.dumps(transcript, indent=2, ensure_ascii=False), encoding="utf-8")
        assert data["provider"] == "google-gemini"
        assert check(answer), f"Irrelevant answer for '{question}':\n{answer[:600]}"
        answers.append(answer)
    # All ten answers are distinct (no repeated sample answer)
    assert len(set(answers)) == len(answers)
    assert data["turn_count"] == 10

