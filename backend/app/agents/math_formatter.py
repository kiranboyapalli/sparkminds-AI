"""
SparkMinds AI — Educational Math & Markdown Response Sanitizer / Formatter
==========================================================================
Transforms raw LLM LaTeX, broken math fragments (e.g., 'cin^', unescaped JSON
control chars from '\\frac'/'\\theta'/'\\times'), and stray dollar-sign math
delimiters into clean, student-friendly, readable mathematical typography while:
  1. Preserving fenced code blocks (``` ... ```) untouched.
  2. Preserving genuine currency values ($5, $12.50, $1,200, $10-$20, ₹500).
  3. Preserving multilingual scripts (Telugu, Hindi, Tamil, Kannada, etc.).
  4. Never exposing raw LaTeX delimiters ($, $$, \\(, \\), \\[, \\]) to students.
"""

from __future__ import annotations

import re
from typing import List, Match, Tuple

# Unicode superscript & subscript lookup tables
_SUPERSCRIPTS = str.maketrans(
    "0123456789+-=()nijkxyzabctm",
    "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱʲᵏˣʸᶻᵃᵇᶜᵗᵐ",
)
_SUBSCRIPTS = str.maketrans(
    "0123456789+-=()aeoxhklmnpstij",
    "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₒₓₕₖₗₘₙₚₛₜᵢⱼ",
)

# Common LaTeX symbol replacements (longest keys matched carefully)
_LATEX_SYMBOLS: List[Tuple[str, str]] = [
    (r"\\Longleftrightarrow", "⇔"),
    (r"\\Leftrightarrow", "⇔"),
    (r"\\Longrightarrow", "⇒"),
    (r"\\Longleftarrow", "⇐"),
    (r"\\longrightarrow", "→"),
    (r"\\longleftarrow", "←"),
    (r"\\Rightarrow", "⇒"),
    (r"\\Leftarrow", "⇐"),
    (r"\\rightarrow", "→"),
    (r"\\leftarrow", "←"),
    (r"\\leftrightarrow", "↔"),
    (r"\\implies", "⇒"),
    (r"\\iff", "⇔"),
    (r"\\to\b", "→"),
    (r"\\times\b", "×"),
    (r"\\cdot\b", "·"),
    (r"\\div\b", "÷"),
    (r"\\pm\b", "±"),
    (r"\\mp\b", "∓"),
    (r"\\neq\b", "≠"),
    (r"\\ne\b", "≠"),
    (r"\\leq\b", "≤"),
    (r"\\le\b", "≤"),
    (r"\\geq\b", "≥"),
    (r"\\ge\b", "≥"),
    (r"\\approx\b", "≈"),
    (r"\\equiv\b", "≡"),
    (r"\\propto\b", "∝"),
    (r"\\infty\b", "∞"),
    (r"\\therefore\b", "∴"),
    (r"\\because\b", "∵"),
    (r"\\angle\b", "∠"),
    (r"\\triangle\b", "△"),
    (r"\\perp\b", "⊥"),
    (r"\\parallel\b", "∥"),
    (r"\\cong\b", "≅"),
    (r"\\sim\b", "∼"),
    (r"\\degree\b", "°"),
    (r"\\circ\b", "°"),
    (r"\\pi\b", "π"),
    (r"\\theta\b", "θ"),
    (r"\\alpha\b", "α"),
    (r"\\beta\b", "β"),
    (r"\\gamma\b", "γ"),
    (r"\\delta\b", "δ"),
    (r"\\Delta\b", "Δ"),
    (r"\\lambda\b", "λ"),
    (r"\\mu\b", "μ"),
    (r"\\sigma\b", "σ"),
    (r"\\Sigma\b", "Σ"),
    (r"\\omega\b", "ω"),
    (r"\\Omega\b", "Ω"),
    (r"\\phi\b", "φ"),
    (r"\\rho\b", "ρ"),
    (r"\\epsilon\b", "ε"),
    (r"\\sum\b", "∑"),
    (r"\\prod\b", "∏"),
    (r"\\int\b", "∫"),
    (r"\\partial\b", "∂"),
    (r"\\in\b", "∈"),
    (r"\\notin\b", "∉"),
    (r"\\subset\b", "⊂"),
    (r"\\subseteq\b", "⊆"),
    (r"\\cup\b", "∪"),
    (r"\\cap\b", "∩"),
    (r"\\forall\b", "∀"),
    (r"\\exists\b", "∃"),
    (r"\\emptyset\b", "∅"),
    (r"\\ldots\b", "…"),
    (r"\\cdots\b", "⋯"),
    (r"\\quad\b", "  "),
    (r"\\qquad\b", "   "),
    (r"\\,", " "),
    (r"\\;", " "),
    (r"\\:", " "),
    (r"\\!", ""),
    (r"\\sin\b", "sin"),
    (r"\\cos\b", "cos"),
    (r"\\tan\b", "tan"),
    (r"\\cot\b", "cot"),
    (r"\\sec\b", "sec"),
    (r"\\csc\b", "csc"),
    (r"\\cosec\b", "cosec"),
    (r"\\log\b", "log"),
    (r"\\ln\b", "ln"),
    (r"\\lim\b", "lim"),
    (r"\\exp\b", "exp"),
    (r"\\max\b", "max"),
    (r"\\min\b", "min"),
]

_SUPER_SAFE_CHARS = set("0123456789+-=()nijkxyzabctm")
_SUB_SAFE_CHARS = set("0123456789+-=()aeoxhklmnpstij")


def _to_superscript(expr: str) -> str:
    clean = expr.strip()
    if not clean:
        return ""
    if clean in ("°", r"\circ", "circ"):
        return "°"
    if all(ch in _SUPER_SAFE_CHARS for ch in clean):
        return clean.translate(_SUPERSCRIPTS)
    return f"^({clean})"


def _to_subscript(expr: str) -> str:
    clean = expr.strip()
    if not clean:
        return ""
    if all(ch in _SUB_SAFE_CHARS for ch in clean):
        return clean.translate(_SUBSCRIPTS)
    return f"_{clean}"


def _extract_braced(s: str, start_idx: int) -> Tuple[str, int]:
    """Extract content inside balanced {...} starting at start_idx (pointing at '{')."""
    if start_idx >= len(s) or s[start_idx] != "{":
        return "", start_idx
    depth = 0
    buf: List[str] = []
    i = start_idx
    while i < len(s):
        ch = s[i]
        if ch == "{":
            if depth > 0:
                buf.append(ch)
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return "".join(buf), i + 1
            buf.append(ch)
        else:
            buf.append(ch)
        i += 1
    return "".join(buf), len(s)


def _replace_fracs(expr: str) -> str:
    """Convert \\frac{a}{b}, \\dfrac{a}{b}, \\tfrac{a}{b} into clean readable fractions."""
    out = expr
    for _ in range(6):
        m = re.search(r"\\[dt]?frac\s*\{", out)
        if not m:
            break
        num_start = m.end() - 1
        num, after_num = _extract_braced(out, num_start)
        ws_idx = after_num
        while ws_idx < len(out) and out[ws_idx].isspace():
            ws_idx += 1
        if ws_idx < len(out) and out[ws_idx] == "{":
            den, after_den = _extract_braced(out, ws_idx)
        else:
            # Handle malformed \frac{a}b
            den = out[ws_idx : ws_idx + 1]
            after_den = ws_idx + 1

        num_clean = _convert_math_body(num).strip()
        den_clean = _convert_math_body(den).strip()
        simple_num = bool(re.match(r"^[A-Za-z0-9πθ√²³]+$", num_clean))
        simple_den = bool(re.match(r"^[A-Za-z0-9πθ√²³]+$", den_clean))
        formatted_num = num_clean if simple_num else f"({num_clean})"
        formatted_den = den_clean if simple_den else f"({den_clean})"
        replacement = f"{formatted_num}/{formatted_den}"
        out = out[: m.start()] + replacement + out[after_den:]
    return out


def _replace_sqrts(expr: str) -> str:
    """Convert \\sqrt[n]{x} and \\sqrt{x} into clean readable radical notation."""
    out = expr
    for _ in range(6):
        m = re.search(r"\\sqrt(?:\[([^\]]+)\])?\s*\{", out)
        if not m:
            break
        root_deg = (m.group(1) or "").strip()
        body, after_body = _extract_braced(out, m.end() - 1)
        body_clean = _convert_math_body(body).strip()
        prefix = f"{_to_superscript(root_deg)}√" if root_deg and root_deg != "2" else "√"
        if re.match(r"^[A-Za-z0-9πθ]+$", body_clean):
            rep = f"{prefix}{body_clean}"
        else:
            rep = f"{prefix}({body_clean})"
        out = out[: m.start()] + rep + out[after_body:]
    return out


def _replace_text_wrappers(expr: str) -> str:
    """Strip \\text{...}, \\mathrm{...}, \\mathbf{...}, \\textbf{...}, \\operatorname{...} wrappers."""
    out = expr
    for _ in range(8):
        m = re.search(
            r"\\(?:text|textrm|textbf|textit|mathrm|mathbf|mathit|mathsf|operatorname|boxed)\s*\{",
            out,
        )
        if not m:
            break
        body, after_body = _extract_braced(out, m.end() - 1)
        out = out[: m.start()] + body + out[after_body:]
    return out


def _convert_math_body(expr: str) -> str:
    """Convert a LaTeX math fragment into clean, readable mathematical notation."""
    if not expr:
        return ""
    out = expr.strip()

    # Repair common JSON control-character accidents when LLMs emit single-escaped LaTeX
    out = out.replace("\x0c", r"\f")  # form-feed from \frac
    out = out.replace("\x08", r"\b")  # backspace from \beta / \because

    # Fix broken trig/token typos observed in raw model output (e.g. "cin^2", "cin^")
    out = re.sub(r"\bcin\s*\^", "sin^", out)

    # Remove sizing / alignment commands
    out = re.sub(r"\\(?:left|right|big|Big|bigg|Bigg)\b", "", out)
    out = re.sub(r"\\begin\{(?:aligned|align\*?|equation\*?|gather\*?)\}", "", out)
    out = re.sub(r"\\end\{(?:aligned|align\*?|equation\*?|gather\*?)\}", "", out)
    out = out.replace("&=", "=").replace("\\\\", "\n")

    # Convert structured wrappers, fractions, and square roots
    out = _replace_text_wrappers(out)
    out = _replace_fracs(out)
    out = _replace_sqrts(out)

    # Convert symbols
    for pat, rep in _LATEX_SYMBOLS:
        out = re.sub(pat, rep, out)

    # Convert degree shorthand `^\circ` or `^{\circ}` or `^°`
    out = re.sub(r"\^\s*\{?\s*°\s*\}?", "°", out)

    # Convert braced superscripts ^{...} and subscripts _{...}
    for _ in range(8):
        m_sup = re.search(r"\^\s*\{", out)
        if not m_sup:
            break
        body, after = _extract_braced(out, m_sup.end() - 1)
        out = out[: m_sup.start()] + _to_superscript(body) + out[after:]

    for _ in range(8):
        m_sub = re.search(r"_\s*\{", out)
        if not m_sub:
            break
        body, after = _extract_braced(out, m_sub.end() - 1)
        out = out[: m_sub.start()] + _to_subscript(body) + out[after:]

    # Convert single-token superscripts like x^2, 10^3, sin^2, cos^2, a^n
    out = re.sub(
        r"([A-Za-z0-9\)θπ°])\^([0-9n])(?![0-9A-Za-z])",
        lambda m: f"{m.group(1)}{_to_superscript(m.group(2))}",
        out,
    )
    # Convert single-digit subscripts like H_2, O_2, x_1, a_n (avoid snake_case identifiers!)
    out = re.sub(
        r"\b([A-Za-z]{1,2})_([0-9]+)\b",
        lambda m: f"{m.group(1)}{_to_subscript(m.group(2))}",
        out,
    )

    # Strip remaining stray LaTeX braces & backslashes before punctuation
    out = out.replace(r"\{", "{").replace(r"\}", "}").replace(r"\%", "%").replace(r"\$", "$")
    out = re.sub(r"\\([a-zA-Z]+)", r"\1", out)
    out = re.sub(r"[ \t]{2,}", " ", out)
    return out.strip()


def _is_currency_dollar_context(text: str, dollar_pos: int) -> bool:
    """
    Determine whether a '$' at dollar_pos is a genuine currency symbol (e.g. '$5', '$12.50', '$1,000')
    rather than a LaTeX math delimiter (e.g. '$x + 2 = 5$', '$3/4$', '$2x^2$').
    """
    after = text[dollar_pos + 1 :]
    m_num = re.match(r"^\s*\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?", after)
    if not m_num:
        return False
    rest = after[m_num.end() :]
    # If immediately followed by math operators or closing $ with math inside, it's math
    if re.match(r"^\s*[\^_\\=<>+\-*/×÷]", rest):
        return False
    if re.match(r"^\s*[A-Za-z]\b", rest):
        # e.g., "$5x$" is math, whereas "$5 each", "$5 per", "$5 is", "$5." is currency
        word_m = re.match(r"^\s*([A-Za-z]+)", rest)
        if word_m and len(word_m.group(1)) == 1 and word_m.group(1).lower() in ("x", "y", "z", "a", "b", "c", "n", "k", "t"):
            return False
    return True


def _sanitize_prose_segment(segment: str) -> str:
    """Sanitize a non-code markdown text segment."""
    if not segment:
        return segment

    text = segment
    # 0. Repair accidental control chars from single-escaped JSON LaTeX
    text = text.replace("\x0c", r"\frac" if "rac{" in text else " ")

    # 1. Repair broken trig/math tokens like "cin^2", "cin^", "cos^ ", "sin^ "
    text = re.sub(r"\bcin\s*\^\s*(\d+)?", lambda m: f"sin{_to_superscript(m.group(1) or '2') if m.group(1) else ''}", text)
    text = re.sub(r"\b(sin|cos|tan|cot|sec|csc)\s*\^\s*(?=\s|$|[,\.\)])", r"\1", text)

    # 2. Protect genuine currency expressions like $5, $12.50, $1,250 with sentinel tokens
    currency_tokens: List[str] = []

    def _stash_currency(m: Match[str]) -> str:
        full = m.group(0)
        # Do NOT stash if followed immediately by math operator or closing '$'
        end_idx = m.end()
        tail = text[end_idx : end_idx + 12]
        if re.match(r"^\s*(?:\$|\^|\\|/|×|÷|\+|-|=|\*|x\b|y\b)", tail):
            return full
        token = f"@@CUR{len(currency_tokens)}@@"
        currency_tokens.append(full)
        return token

    text = re.sub(r"\$\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?(?![0-9A-Za-z\\^_])", _stash_currency, text)

    # 3. Convert display math blocks: $$ ... $$ and \[ ... \]
    text = re.sub(
        r"\$\$([\s\S]+?)\$\$",
        lambda m: f"\n{_convert_math_body(m.group(1))}\n",
        text,
    )
    text = re.sub(
        r"\\\[([\s\S]+?)\\\]",
        lambda m: f"\n{_convert_math_body(m.group(1))}\n",
        text,
    )

    # 4. Convert inline math: \( ... \) and $ ... $
    text = re.sub(
        r"\\\((.+?)\\\)",
        lambda m: _convert_math_body(m.group(1)),
        text,
        flags=re.DOTALL,
    )

    def _replace_inline_dollar(m: Match[str]) -> str:
        inner = m.group(1)
        # Guard against spanning across a huge paragraph with unrelated currency
        if "\n\n" in inner or len(inner) > 220:
            return m.group(0)
        return _convert_math_body(inner)

    text = re.sub(r"(?<!\\)\$([^$\n]+?)(?<!\\)\$", _replace_inline_dollar, text)

    # 5. Convert any remaining bare LaTeX commands outside $ delimiters (\frac, \sqrt, \times, \theta, etc.)
    if "\\" in text:
        text = _replace_text_wrappers(text)
        text = _replace_fracs(text)
        text = _replace_sqrts(text)
        for pat, rep in _LATEX_SYMBOLS:
            text = re.sub(pat, rep, text)
        text = re.sub(r"\\(?:left|right)\b", "", text)

    # 6. Clean bare superscripts/subscripts in prose (e.g., x^2 -> x², sin^2 θ -> sin²θ, 10^3 -> 10³, H_2O -> H₂O)
    text = re.sub(
        r"\b(sin|cos|tan|cot|sec|csc)\^([0-9])\b",
        lambda m: f"{m.group(1)}{_to_superscript(m.group(2))}",
        text,
    )
    text = re.sub(
        r"([A-Za-z0-9\)θπ])\^\{([0-9+\-n]+)\}",
        lambda m: f"{m.group(1)}{_to_superscript(m.group(2))}",
        text,
    )
    text = re.sub(
        r"([A-Za-z0-9\)θπ])\^([0-9n])(?![0-9A-Za-z])",
        lambda m: f"{m.group(1)}{_to_superscript(m.group(2))}",
        text,
    )
    text = re.sub(
        r"\b(H|O|C|N|S|Cl|Na|Ca|Fe|Mg|CO|SO|NO|NH|CH)_?(\d)(?=[A-Z\s,\.\)\?!]|$)",
        lambda m: f"{m.group(1)}{_to_subscript(m.group(2))}" if "_" in m.group(0) else m.group(0),
        text,
    )
    # Remove any stray orphaned math '$' delimiter (not a stashed currency token)
    text = re.sub(r"(?<!\w)\$+(?!\d)", "", text)
    text = re.sub(r"\$+(?=\s|$|[,\.\)\]:;!?])", "", text)

    # 7. Restore stashed genuine currency values ($5, $12.50, etc.)
    for idx, cur_val in enumerate(currency_tokens):
        text = text.replace(f"@@CUR{idx}@@", cur_val)

    # Collapse excessive blank lines while preserving intentional paragraph breaks
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def format_educational_text(text: str) -> str:
    """
    Sanitize and format an AI educational response while keeping fenced code
    blocks (```...```) completely intact.
    """
    if not text or not isinstance(text, str):
        return text or ""

    parts = text.split("```")
    formatted: List[str] = []
    for idx, part in enumerate(parts):
        if idx % 2 == 1:
            # Inside fenced code block — preserve verbatim
            formatted.append(part)
        else:
            formatted.append(_sanitize_prose_segment(part))
    return "```".join(formatted).strip()
