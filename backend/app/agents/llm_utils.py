"""
SparkMinds AI — Shared Resilient Gemini LLM Client Helper
=========================================================
Centralizes Google Gemini invocations for all SparkMinds AI agents with:
  - Automatic sanitization of invalid/unrecognized model names (avoids wasted 404 round-trips)
  - Ordered fallback model cascade (gemini-2.5-flash -> gemini-2.5-flash-lite -> gemini-2.0-flash)
  - Transient retry/backoff handling (429/500/503) and strict timeouts
  - Secret-safe logging (NEVER logs API keys or student passwords/OTPs)
  - Clean structured JSON extraction with fenced-block tolerance
"""

from __future__ import annotations

import json
import logging
import os
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import settings

logger = logging.getLogger("sparkminds.llm")

# Known valid Google Gemini models in preferred speed/quality order
VERIFIED_GEMINI_MODELS: Tuple[str, ...] = (
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
)

# Invalid/nonexistent model aliases that should be deprioritized behind verified models
_KNOWN_UNAVAILABLE_MODELS = {
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
}


def is_llm_available() -> bool:
    if os.getenv("SPARKMINDS_DISABLE_LIVE_LLM", "").strip().lower() == "true":
        return False
    key = (getattr(settings, "GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")).strip()
    return bool(key) and key != "your_gemini_api_key_here" and len(key) >= 10


def get_candidate_gemini_models() -> List[str]:
    """
    Returns an ordered list of candidate Gemini model IDs without duplicates.
    If the configured GEMINI_MODEL is known-unavailable (e.g. legacy 'gemini-3.5-flash-lite'),
    prioritizes verified live models first so agents don't pay a wasted 404 penalty on every call.
    """
    configured = (
        getattr(settings, "GEMINI_MODEL", "") or os.getenv("GEMINI_MODEL", "") or "gemini-2.5-flash"
    ).strip()

    models: List[str] = []
    if configured and configured not in _KNOWN_UNAVAILABLE_MODELS:
        models.append(configured)
    for m in VERIFIED_GEMINI_MODELS:
        if m not in models:
            models.append(m)
    return models


def _strip_json_fences(raw: str) -> str:
    txt = (raw or "").strip()
    if txt.startswith("```"):
        txt = re.sub(r"^```(?:json)?\s*", "", txt, flags=re.IGNORECASE)
        txt = re.sub(r"\s*```$", "", txt)
    return txt.strip()


def _call_gemini_rest_text(
    *,
    prompt: str,
    system_instruction: Optional[str],
    temperature: float,
    max_output_tokens: int,
    response_mime_type: Optional[str],
    candidate_models: List[str],
    timeout_seconds: float,
) -> Optional[Tuple[str, str]]:
    api_key = (getattr(settings, "GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")).strip()
    gen_cfg: Dict[str, Any] = {
        "temperature": temperature,
        "maxOutputTokens": max_output_tokens,
    }
    if response_mime_type:
        gen_cfg["responseMimeType"] = response_mime_type

    payload: Dict[str, Any] = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": gen_cfg,
    }
    if system_instruction:
        payload["system_instruction"] = {"parts": [{"text": system_instruction}]}

    body = json.dumps(payload).encode("utf-8")
    ssl_ctx = ssl.create_default_context()

    for model_name in candidate_models:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{urllib.parse.quote(model_name, safe='')}:generateContent"
            f"?key={urllib.parse.quote(api_key, safe='')}"
        )
        req = urllib.request.Request(
            url, data=body, headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout_seconds, context=ssl_ctx) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="replace"))
                cands = data.get("candidates") or []
                if cands:
                    parts = (cands[0].get("content") or {}).get("parts") or []
                    text_out = "\n".join(
                        str(p.get("text", "")).strip() for p in parts if p.get("text")
                    ).strip()
                    if text_out:
                        return text_out, model_name
        except urllib.error.HTTPError as exc:
            logger.warning("Gemini REST model=%s returned HTTP %s", model_name, exc.code)
            if exc.code in (404, 429, 500, 503):
                continue
            break
        except Exception as exc:
            logger.warning("Gemini REST model=%s failed: %s", model_name, type(exc).__name__)
            continue
    return None


def call_gemini_text(
    *,
    prompt: str,
    system_instruction: Optional[str] = None,
    temperature: float = 0.35,
    max_output_tokens: int = 2048,
    response_mime_type: Optional[str] = None,
    timeout_seconds: float = 20.0,
) -> Optional[Tuple[str, str]]:
    """
    Calls Google Gemini safely with automatic fallback across verified models.
    Returns (text, model_used) on success, or None if unavailable/failed.
    """
    if not is_llm_available():
        return None

    api_key = (getattr(settings, "GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")).strip()
    candidate_models = get_candidate_gemini_models()

    try:
        from google import genai
        from google.genai import types
    except Exception:
        return _call_gemini_rest_text(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            response_mime_type=response_mime_type,
            candidate_models=candidate_models,
            timeout_seconds=timeout_seconds,
        )

    client = genai.Client(api_key=api_key)
    cfg_kwargs: Dict[str, Any] = {
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
    }
    if system_instruction:
        cfg_kwargs["system_instruction"] = system_instruction
    if response_mime_type:
        cfg_kwargs["response_mime_type"] = response_mime_type
    cfg = types.GenerateContentConfig(**cfg_kwargs)

    for model_name in candidate_models:
        for attempt in range(2):
            try:
                resp = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=cfg,
                )
                txt = (getattr(resp, "text", None) or "").strip()
                if txt:
                    return txt, model_name
                break
            except Exception as exc:
                err_str = str(exc)
                is_transient = any(
                    c in err_str for c in ("429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE", "500")
                )
                logger.warning(
                    "Gemini SDK model=%s attempt=%d failed (%s)",
                    model_name,
                    attempt + 1,
                    type(exc).__name__,
                )
                if not is_transient or attempt == 1:
                    break
                if "503" in err_str or "UNAVAILABLE" in err_str or "per day" in err_str.lower():
                    break
                time.sleep(1.5)
    return None


def call_gemini_json(
    *,
    prompt: str,
    system_instruction: Optional[str] = None,
    temperature: float = 0.3,
    max_output_tokens: int = 2560,
    timeout_seconds: float = 22.0,
) -> Optional[Tuple[Any, str]]:
    """Calls Gemini requesting JSON output and parses safely (tolerating markdown fences)."""
    res = call_gemini_text(
        prompt=prompt,
        system_instruction=system_instruction,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        response_mime_type="application/json",
        timeout_seconds=timeout_seconds,
    )
    if not res:
        return None
    raw_text, model_used = res
    cleaned = _strip_json_fences(raw_text)
    try:
        return json.loads(cleaned), model_used
    except json.JSONDecodeError:
        # Attempt to salvage first JSON object or array
        m = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned)
        if m:
            try:
                return json.loads(m.group(1)), model_used
            except json.JSONDecodeError:
                pass
        logger.warning("Gemini JSON parsing failed for model=%s", model_used)
        return None
