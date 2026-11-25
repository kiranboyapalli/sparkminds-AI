"""
SparkMinds AI — Agent 3: Teaching Agent (Interactive Socratic Tutor)
Responsibilities (Section 2.3 & Section 3 Grade-Level Intelligence):
- Explain concepts in simple, grade-appropriate language (distinctly adapted for Grades 1–5, 6–8, 9–10, and 11–12).
- Respect the student's preferred explanation language (English, Telugu, Hindi, Tamil, Kannada + progressive Indian languages).
- Use real-world Indian examples tailored to the student's grade.
- Break complicated problems into smaller steps using exact symbolic calculations (never guessing arithmetic).
- Provide progressive hints (Level 1, Level 2, Level 3).
- Ask the student to attempt each step.
- Explain incorrect answers.
- Offer alternative explanations when a student struggles repeatedly.
- Avoid immediately revealing the complete answer when the student needs guidance.
- Provide a full worked solution when requested or pedagogically appropriate.
- Generate similar practice questions.
"""
import json
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from app.core.config import settings
from app.agents.llm_utils import call_gemini_json
from app.agents.math_formatter import format_educational_text
from app.agents.model_client import (
    AgentExecutionError,
    invoke_gemini_or_structured_engine,
    solve_and_plan_math_problem,
    verify_language_capability,
)
from app.agents.visual_and_video_generator import (
    get_visual_diagram,
    get_curated_video_explanation,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TeachingAgentInput(BaseModel):
    student_id: str
    grade: int
    school_board: str = "CBSE"
    detected_subject: str
    detected_topic: str
    extracted_question: str
    pedagogical_mode: Literal[
        "TEACH_PREREQUISITE_FIRST",
        "STEP_BY_STEP_GUIDED_TUTORING",
        "PROGRESSIVE_HINT",
        "ALTERNATIVE_EXPLANATION",
        "FULL_WORKED_SOLUTION",
        "SIMILAR_PRACTICE_QUESTION",
    ] = "STEP_BY_STEP_GUIDED_TUTORING"
    current_step_index: int = 1
    hint_level: int = Field(default=1, ge=1, le=3)
    mistake_count: int = 0
    last_detected_misconception: Optional[str] = None
    missing_prerequisite_topic: Optional[str] = None
    preferred_explanation_language: str = "English"
    secondary_explanation_language: Optional[str] = None
    request_full_solution: bool = False
    simulate_agent_failure: bool = False
    simulate_model_failure: bool = False


class TeachingStepItem(BaseModel):
    step_number: int
    title: str
    instruction: str
    why_this_step_matters: Optional[str] = None
    step_formula_or_rule: Optional[str] = None
    question_for_student: str
    expected_checkpoint: str


class TeachingAgentOutput(BaseModel):
    agent_id: Literal["teaching"] = "teaching"
    agent_name: str = "Teaching Agent"
    status: Literal["completed", "failed"] = "completed"
    executed_at: str
    duration_ms: float
    model_used: str
    explanation_language: str
    secondary_explanation_language: Optional[str] = None
    bilingual_active: bool = False
    language_capability_notice: Optional[str] = None
    pedagogical_mode_applied: str
    concept_explanation: str
    bilingual_secondary_explanation: Optional[str] = None
    real_world_example: str
    prerequisite_mini_lesson: Optional[str] = None
    steps_breakdown: List[TeachingStepItem] = Field(default_factory=list)
    active_step_number: int = 1
    prompt_for_student_attempt: str
    progressive_hints: List[str] = Field(default_factory=list)
    active_hint_shown: Optional[str] = None
    incorrect_answer_explanation: Optional[str] = None
    alternative_explanation: Optional[str] = None
    full_worked_solution: Optional[str] = None
    answer_withheld_for_guided_learning: bool = True
    similar_practice_question: Dict[str, str]
    visual_diagram_svg: Optional[str] = None
    visual_diagram_caption: Optional[str] = None
    visual_concept_type: Optional[str] = None
    video_explanation: Optional[Dict[str, Any]] = None


# ============================================================================
# MULTILINGUAL INTERACTIVE TUTOR CONTENT BANK (NO FULL-ANSWER SPOILERS BY DEFAULT)
# ============================================================================

LANGUAGE_TUTOR_PACKS: Dict[str, Dict[str, str]] = {
    "English": {
        "fraction_concept": (
            "When two fractions have different denominators (bottom numbers) like 1/4 and 1/6, "
            "their slice sizes are different. We cannot add the bottom numbers directly! "
            "First, we make the slice sizes equal by finding the Least Common Multiple (LCM) of the denominators."
        ),
        "fraction_example": (
            "Real-World Example: Imagine sharing a roti or pizza. 1/4 is one piece out of 4 equal slices, "
            "and 1/6 is one piece out of 6 equal slices. If we cut the whole into 12 equal slices, "
            "both pieces can be counted using the same slice size!"
        ),
        "prereq_lcm": (
            "Prerequisite Mini-Lesson (Finding LCM): List the multiples of 4 (4, 8, 12, 16...) and multiples of 6 (6, 12, 18...). "
            "The smallest multiple they share in common is their LCM!"
        ),
        "step1_prompt": "Step 1 Turn: Look at the denominators 4 and 6. What is the smallest number (LCM) that both 4 and 6 divide into evenly?",
        "step2_prompt": "Step 2 Turn: Great! Since LCM = 12, convert 1/4 and 1/6 into equivalent fractions with denominator 12. What do you get?",
        "step3_prompt": "Step 3 Turn: Now add the numerators of 3/12 and 2/12 while keeping the denominator 12. What is the final fraction?",
        "alt_explanation": (
            "Alternative Conceptual Strategy (Step-by-Step Breakdown): Let's switch from numbers to a real-world sharing example! "
            "A bar with 12 squares divided into 4 equal parts has 3 squares per part (so 1/4 = 3 squares). "
            "Divided into 6 equal parts, it has 2 squares per part (so 1/6 = 2 squares). Counting squares together gives 3 + 2 = 5 squares out of 12!"
        ),
        "science_concept": (
            "Photosynthesis is the process by which green plants make their own food (glucose) using sunlight, "
            "water absorbed by roots, and carbon dioxide taken in through tiny leaf pores called stomata."
        ),
        "science_example": (
            "Real-World Example: Think of the green pigment Chlorophyll inside a leaf as a solar panel on a rooftop in India—it captures sunlight energy to cook food for the plant!"
        ),
        "science_prompt": "Your Turn (Step 1): Name the green pigment in leaves that traps sunlight and the gas released into the air during photosynthesis.",
    },
    "Telugu": {
        "fraction_concept": (
            "తెలుగు వివరణ (Telugu Tutor): 1/4 మరియు 1/6 వంటి భిన్నాల హారాలు (Denominators - క్రింది సంఖ్యలు) వేర్వేరుగా ఉన్నప్పుడు, "
            "వాటిని నేరుగా కూడకూడదు (4 + 6 = 10 చేయడం తప్పు). ముందుగా ఆ రెండు హారాలను సమానం చేయడానికి క.సా.గు (LCM) కనుగొనాలి."
        ),
        "fraction_example": (
            "నిజ జీవిత ఉదాహరణ: ఒక చపాతీని 4 సమాన ముక్కలు చేస్తే ఒక ముక్క 1/4 అవుతుంది, 6 ముక్కలు చేస్తే 1/6 అవుతుంది. "
            "రెండింటినీ 12 సమాన భాగాలుగా మారిస్తే సులభంగా లెక్కించవచ్చు!"
        ),
        "prereq_lcm": (
            "ముందస్తు భావన (క.సా.గు / LCM): 4 యొక్క గుణిజాలు (4, 8, 12, 16...) మరియు 6 యొక్క గుణిజాలు (6, 12, 18...) రాయండి. "
            "రెండింటిలోనూ ఉండే అతి చిన్న ఉమ్మడి సంఖ్యే క.సా.గు (LCM)!"
        ),
        "step1_prompt": "మీ వంతు (Step 1): 4 మరియు 6 యొక్క క.సా.గు (LCM) ఎంత? మీ సమాధానాన్ని నమోదు చేయండి.",
        "step2_prompt": "మీ వంతు (Step 2): శభాష్! క.సా.గు = 12 కదా, ఇప్పుడు 1/4 మరియు 1/6 లను హారం 12 వచ్చేలా సమాన భిన్నాలుగా మారిస్తే ఏమొస్తుంది?",
        "step3_prompt": "మీ వంతు (Step 3): ఇప్పుడు 3/12 మరియు 2/12 యొక్క లవాలను (పై సంఖ్యలను) కూడి తుది భిన్నాన్ని రాయండి!",
        "alt_explanation": (
            "ప్రత్యామ్నాయ దృశ్య వివరణ (Alternative Visual Method): 12 గడులు ఉన్న ఒక చాక్లెట్ బార్‌ను ఊహించుకోండి. "
            "దానిలో 1/4 వంతు అంటే 3 గడులు, 1/6 వంతు అంటే 2 గడులు. మొత్తం కలిపితే 12 గడులలో 5 గడులు!"
        ),
        "science_concept": (
            "కిరణజన్య సంయోగక్రియ (Photosynthesis): ఆకుపచ్చని మొక్కలు సూర్యరశ్మి, నీరు మరియు కార్బన్ డయాక్సైడ్ ఉపయోగించుకొని తమ ఆహారాన్ని (గ్లూకోజ్) తామే తయారు చేసుకునే ప్రక్రియ."
        ),
        "science_example": (
            "నిజ జీవిత ఉదాహరణ: ఆకులోని 'పత్రహరితం' (Chlorophyll) ఇంటిపై ఉండే సోలార్ ప్యానెల్ లాగా సూర్యరశ్మిని గ్రహిస్తుంది!"
        ),
        "science_prompt": "మీ వంతు (Step 1): ఆకులలో సూర్యరశ్మిని గ్రహించే ఆకుపచ్చని పదార్థం పేరు మరియు మొక్కలు విడుదల చేసే వాయువు పేరు రాయండి.",
    },
    "Hindi": {
        "fraction_concept": (
            "हिन्दी ट्यूटर (Hindi Tutor): जब 1/4 और 1/6 जैसे भिन्नों के हर (Denominators) अलग-अलग होते हैं, "
            "तो हम नीचे की संख्याओं को सीधे नहीं जोड़ सकते। पहले हमें हर समान करने के लिए उनका लघुत्तम समापवर्त्य (LCM) निकालना होगा।"
        ),
        "fraction_example": (
            "वास्तविक उदाहरण: मान लीजिए एक रोटी के 4 बराबर टुकड़े किए गए (1/4) और दूसरी के 6 टुकड़े (1/6)। "
            "यदि हम दोनों को 12 बराबर हिस्सों के रूप में देखें, तो जोड़ना आसान हो जाता है!"
        ),
        "prereq_lcm": (
            "आधारभूत नियम (LCM कैसे निकालें): 4 के गुणज (4, 8, 12, 16...) और 6 के गुणज (6, 12, 18...) लिखें। सबसे छोटा साझा गुणज ही LCM है!"
        ),
        "step1_prompt": "आपकी बारी (Step 1): हर 4 और 6 का लघुत्तम समापवर्त्य (LCM) क्या है? अपना उत्तर लिखें।",
        "step2_prompt": "आपकी बारी (Step 2): बहुत बढ़िया! अब 1/4 और 1/6 को हर 12 वाले तुल्य भिन्नों (Equivalent Fractions) में बदलें।",
        "step3_prompt": "आपकी बारी (Step 3): अब 3/12 और 2/12 के अंशों को जोड़कर अंतिम उत्तर बताएं!",
        "alt_explanation": (
            "वैकल्पिक चित्र विधि (Alternative Explanation): 12 चौकोर टुकड़ों वाली एक चॉकलेट बार की कल्पना करें। "
            "उसका 1/4 भाग = 3 टुकड़े, और 1/6 भाग = 2 टुकड़े। दोनों को मिलाने पर 12 में से कितने टुकड़े हुए?"
        ),
        "science_concept": (
            "प्रकाश संश्लेषण (Photosynthesis): वह प्रक्रिया जिसके द्वारा हरे पौधे सूर्य के प्रकाश, जल और कार्बन डाइऑक्साइड की सहायता से अपना भोजन (ग्लूकोज) बनाते हैं।"
        ),
        "science_example": "वास्तविक उदाहरण: पत्तियों में मौजूद क्लोरोफिल (Chlorophyll) सौर पैनल की तरह धूप की ऊर्जा को पकड़ता है।",
        "science_prompt": "आपकी बारी (Step 1): पत्तियों के उस हरे वर्णक (pigment) का नाम बताइए जो सूर्य का प्रकाश सोखता है।",
    },
    "Tamil": {
        "fraction_concept": (
            "தமிழ் ஆசிரியர் (Tamil Tutor): 1/4 மற்றும் 1/6 போன்ற பின்னங்களின் பகுதிகள் (Denominators) வெவ்வேறாக இருக்கும்போது, "
            "பகுதிகளை நேராகக் கூட்டக் கூடாது. முதலில் பகுதிகளின் மீ.சி.ம (LCM) கண்டுபிடித்து சமப் பகுதிகளாக மாற்ற வேண்டும்."
        ),
        "fraction_example": "நடைமுறை எடுத்துக்காட்டு: ஒரு சப்பாத்தியை 12 சம பாகங்களாகப் பிரித்து 1/4 மற்றும் 1/6 பாகங்களை ஒப்பிடுவது போலாகும்.",
        "prereq_lcm": "அடிப்படை (மீ.சி.ம / LCM): 4-இன் மடங்குகள் (4, 8, 12...) மற்றும் 6-இன் மடங்குகள் (6, 12...) ஆகியவற்றில் மிகச்சிறிய பொது மடங்கு எது?",
        "step1_prompt": "உங்கள் முறை (Step 1): 4 மற்றும் 6-இன் மீ.சி.ம (LCM) என்ன? முயற்சி செய்யுங்கள்.",
        "step2_prompt": "உங்கள் முறை (Step 2): நன்று! 1/4 மற்றும் 1/6-ஐ பகுதி 12 கொண்ட சமான பின்னங்களாக மாற்றினால் என்ன கிடைக்கும்?",
        "step3_prompt": "உங்கள் முறை (Step 3): இப்போது 3/12 மற்றும் 2/12-இன் தொகுதிகளைக் கூட்டி விடையைக் கூறுங்கள்!",
        "alt_explanation": "மாற்று விளக்கம்: 12 கட்டங்கள் கொண்ட சாக்லேட்டில் 1/4 என்பது 3 கட்டங்கள், 1/6 என்பது 2 கட்டங்கள்.",
        "science_concept": "ஒளிச்சேர்க்கை (Photosynthesis): பசுந்தாவரங்கள் சூரிய ஒளி, நீர் மற்றும் கார்பன் டை ஆக்சைடு மூலம் உணவு தயாரிக்கும் நிகழ்வு.",
        "science_example": "இலையில் உள்ள பச்சையம் (Chlorophyll) சூரிய ஒளியை ஈர்க்கும்.",
        "science_prompt": "உங்கள் முறை (Step 1): சூரிய ஒளியை ஈர்க்கும் இலையின் பச்சை நிறமி எது?",
    },
    "Kannada": {
        "fraction_concept": (
            "ಕನ್ನಡ ಬೋಧಕ (Kannada Tutor): 1/4 ಮತ್ತು 1/6 ರಂತಹ ಭಿನ್ನರಾಶಿಗಳ ಛೇದಗಳು (Denominators) ಬೇರೆ ಬೇರೆಯಾಗಿದ್ದಾಗ, "
            "ಅವುಗಳನ್ನು ನೇರವಾಗಿ ಕೂಡಬಾರದು. ಮೊದಲು ಛೇದಗಳ ಲ.ಸಾ.ಅ (LCM) ಕಂಡುಹಿಡಿಯಬೇಕು."
        ),
        "fraction_example": "ನಿಜ ಜೀವನದ ಉದಾಹರಣೆ: ಒಂದು ರೊಟ್ಟಿಯನ್ನು 12 ಸಮ ಭಾಗಗಳಾಗಿ ವಿಂಗಡಿಸಿ 1/4 ಮತ್ತು 1/6 ಭಾಗಗಳನ್ನು ಎಣಿಸುವುದು.",
        "prereq_lcm": "ಮೂಲ ಪರಿಕಲ್ಪನೆ (ಲ.ಸಾ.ಅ / LCM): 4 ರ ಅಪವರ್ತ್ಯಗಳು (4, 8, 12...) ಮತ್ತು 6 ರ ಅಪವರ್ತ್ಯಗಳು (6, 12...) ಇವುಗಳಲ್ಲಿ ಚಿಕ್ಕ ಸಾಮಾನ್ಯ ಸಂಖ್ಯೆ ಯಾವುದು?",
        "step1_prompt": "ನಿಮ್ಮ ಸರದಿ (Step 1): 4 ಮತ್ತು 6 ರ ಲ.ಸಾ.ಅ (LCM) ಎಷ್ಟು? ಉತ್ತರಿಸಿ.",
        "step2_prompt": "ನಿಮ್ಮ ಸರದಿ (Step 2): ಉತ್ತಮ! ಈಗ 1/4 ಮತ್ತು 1/6 ನ್ನು ಛೇದ 12 ಬರುವಂತೆ ಸಮಾನ ಭಿನ್ನರಾಶಿಗಳಾಗಿ ಬದಲಿಸಿ.",
        "step3_prompt": "ನಿಮ್ಮ ಸರದಿ (Step 3): ಈಗ 3/12 ಮತ್ತು 2/12 ರ ಅಂಶಗಳನ್ನು ಕೂಡಿ ಅಂತಿಮ ಉತ್ತರ ಬರೆಯಿರಿ!",
        "alt_explanation": "ಪರ್ಯಾಯ ವಿವರಣೆ: 12 ಚೌಕಗಳ ಚಾಕೊಲೇಟ್ ಬಾರ್‌ನಲ್ಲಿ 1/4 ಅಂದರೆ 3 ಚೌಕಗಳು ಮತ್ತು 1/6 ಅಂದರೆ 2 ಚೌಕಗಳು.",
        "science_concept": "ದ್ಯುತಿಸಂಶ್ಲೇಷಣೆ (Photosynthesis): ಹಸಿರು ಸಸ್ಯಗಳು ಸೂರ್ಯನ ಬೆಳಕು, ನೀರು ಮತ್ತು ಇಂಗಾಲದ ಡೈಆಕ್ಸೈಡ್ ಬಳಸಿ ಆಹಾರ ತಯಾರಿಸುವ ಪ್ರಕ್ರಿಯೆ.",
        "science_example": "ಎಲೆಯಲ್ಲಿರುವ ಪತ್ರಹರಿತ್ತು (Chlorophyll) ಸೌರಫಲಕದಂತೆ ಬೆಳಕನ್ನು ಹೀರಿಕೊಳ್ಳುತ್ತದೆ.",
        "science_prompt": "ನಿಮ್ಮ ಸರದಿ (Step 1): ಸೂರ್ಯನ ಬೆಳಕನ್ನು ಹೀರಿಕೊಳ್ಳುವ ಎಲೆಯ ಹಸಿರು ವರ್ಣದ್ರವ್ಯ ಯಾವುದು?",
    },
}


def _get_grade_band_adaptation_prefix(grade: int, school_board: str) -> str:
    """
    Section 3: Grade-Level Intelligence.
    Ensures a Grade 1–5 student, a Grade 6–8 student, a Grade 9–10 student, and a Grade 11–12 student
    receive distinctly adapted explanations and examples.
    """
    if grade <= 5:
        return (
            f"[Young Explorer Mode • Grade {grade} {school_board}]: Let's learn with a fun step-by-step story and simple examples! "
        )
    if grade <= 8:
        return (
            f"[Concept Builder Mode • Grade {grade} {school_board}]: Let's build strong conceptual clarity step by step: "
        )
    if grade <= 10:
        return (
            f"[Board Foundation Mode • Grade {grade} {school_board}]: Let's structure this systematically using board-exam marking steps: "
        )
    return (
        f"[Senior Scholar Mode • Grade {grade} {school_board}]: Analytical derivation and formal verification: "
    )


def _generate_dynamic_subject_lesson(
    inp: TeachingAgentInput, lang: str, grade_prefix: str
) -> Dict[str, Any]:
    """
    Generates a dynamic Socratic lesson for arbitrary school subjects (History, English,
    Physics, Chemistry, Biology, Python, Geography, GK, etc.) using the configured AI model.
    Never returns hardcoded fraction answers for non-fraction questions.
    """
    q = inp.extracted_question.strip()
    subj = inp.detected_subject or "General Education"
    topic = inp.detected_topic or f"{subj} Core Learning"

    prompt = (
        f"Student: Grade {inp.grade} {inp.school_board}. Preferred Language: {lang}.\n"
        f"Subject: {subj}. Topic: {topic}.\n"
        f"Question: {q}\n\n"
        f"Formatting rule: Write math cleanly with Unicode symbols (×, ÷, √, π, x², 3/4, °) and NEVER wrap formulas in raw $...$ or LaTeX macros.\n"
        f"Provide a structured Socratic tutoring lesson in valid JSON format with keys:\n"
        f'- "concept_explanation": clear conceptual explanation answering the question in {lang}\n'
        f'- "real_world_example": intuitive real-world or relatable example\n'
        f'- "step1_title": short title for step 1\n'
        f'- "step1_instruction": instruction guiding the student\n'
        f'- "step1_why_it_matters": conceptual explanation of why this step is essential\n'
        f'- "step1_rule_or_principle": key rule, formula, law, or foundational principle\n'
        f'- "step1_question": Socratic question checking understanding\n'
        f'- "step1_checkpoint": expected short checkpoint/answer for step 1\n'
        f'- "step2_title": short title for step 2\n'
        f'- "step2_instruction": instruction for step 2\n'
        f'- "step2_why_it_matters": conceptual reason for this second step\n'
        f'- "step2_rule_or_principle": principle or reasoning rule for step 2\n'
        f'- "step2_question": Socratic question for step 2\n'
        f'- "step2_checkpoint": expected answer for step 2\n'
        f'- "hints": list of 3 progressive hints (gentle nudge, intermediate clue, detailed scaffold)\n'
        f'- "alternative_explanation": visual metaphor, mnemonic, diagram description, or alternative angle explaining this concept in another way\n'
        f'- "full_worked_solution": complete, comprehensive answer and explanation\n'
        f'- "similar_practice_question": relevant follow-up question for practice\n'
        f'- "expected_concept": short summary of the key concept\n'
    )
    res = call_gemini_json(prompt=prompt, temperature=0.4, max_output_tokens=2400)
    if res and isinstance(res[0], dict):
        parsed = res[0]
        return {
            "concept_text": f"{grade_prefix}{format_educational_text(str(parsed.get('concept_explanation', '')))}",
            "example_text": format_educational_text(str(parsed.get("real_world_example", f"Think about how {subj} applies in daily life."))),
            "steps": [
                TeachingStepItem(
                    step_number=1,
                    title=format_educational_text(str(parsed.get("step1_title", "Understand the Core Concept"))),
                    instruction=format_educational_text(str(parsed.get("step1_instruction", f"Review the key idea behind: {q}"))),
                    why_this_step_matters=format_educational_text(str(parsed.get(
                        "step1_why_it_matters",
                        f"Understanding the fundamental definitions of {subj} sets the foundation for accurate problem solving."
                    ))),
                    step_formula_or_rule=format_educational_text(str(parsed.get(
                        "step1_rule_or_principle",
                        f"Core Principle: Identify given parameters and apply syllabus definitions for {topic}."
                    ))),
                    question_for_student=format_educational_text(str(parsed.get("step1_question", "What is the most important fact or rule about this question?"))),
                    expected_checkpoint=format_educational_text(str(parsed.get("step1_checkpoint", "Key concept"))),
                ),
                TeachingStepItem(
                    step_number=2,
                    title=format_educational_text(str(parsed.get("step2_title", "Apply & Explain"))),
                    instruction=format_educational_text(str(parsed.get("step2_instruction", "Formulate the complete answer in your own words."))),
                    why_this_step_matters=format_educational_text(str(parsed.get(
                        "step2_why_it_matters",
                        "Synthesizing the solution proves deep conceptual mastery beyond memorization."
                    ))),
                    step_formula_or_rule=format_educational_text(str(parsed.get(
                        "step2_rule_or_principle",
                        "Application Rule: Connect cause, mechanism, and conclusion systematically."
                    ))),
                    question_for_student=format_educational_text(str(parsed.get("step2_question", "How would you explain this in your own words?"))),
                    expected_checkpoint=format_educational_text(str(parsed.get("step2_checkpoint", "Application"))),
                ),
            ],
            "hints": [
                format_educational_text(str(h))
                for h in (parsed.get("hints") or [
                    f"Hint 1: Think about the main subject area ({subj}) and key terms in the question.",
                    f"Hint 2: Review how this concept connects to Grade {inp.grade} learning.",
                    f"Hint 3: Recall the central fact or rule needed to answer: {q}.",
                ])
            ],
            "alternative_explanation": format_educational_text(str(parsed.get("alternative_explanation", f"Alternative Conceptual Strategy for {subj}: Let's break this down into clear real-world relationships."))),
            "worked_solution": format_educational_text(str(parsed.get("full_worked_solution", f"Full Explanation for '{q}':\nDetailed curriculum explanation tailored for Grade {inp.grade} {subj}."))),
            "similar_question": {
                "question": format_educational_text(str(parsed.get("similar_practice_question", f"Similar Practice Question on {topic}: Can you explain another example of this concept?"))),
                "topic": topic,
                "expected_concept": format_educational_text(str(parsed.get("expected_concept", topic))),
            },
        }

    # Reliable dynamic fallback when AI service is offline
    return {
        "concept_text": (
            f"{grade_prefix}Let's explore your question about {subj}: \"{q}\". "
            f"In Grade {inp.grade} {subj}, understanding the core definitions and principles is the foundation for mastering this topic."
        ),
        "example_text": (
            f"Relatable Example: When learning {subj}, connecting key facts with real situations helps you remember them easily."
        ),
        "steps": [
            TeachingStepItem(
                step_number=1,
                title="Identify Key Terms & Context",
                instruction=f"Examine the main terms in: \"{q}\".",
                why_this_step_matters=f"Isolating the key terms in {subj} eliminates confusion and directs attention to the governing concept.",
                step_formula_or_rule=f"Curriculum Axiom: In {subj}, every question hinges on specific defined relationships and properties.",
                question_for_student=f"What is the central subject or person/concept being asked about in this question?",
                expected_checkpoint=subj,
            ),
            TeachingStepItem(
                step_number=2,
                title="Synthesize the Explanation",
                instruction=f"Formulate the complete response for {topic}.",
                why_this_step_matters=f"Step-by-step synthesis organizes evidence and confirms complete mastery for Grade {inp.grade}.",
                step_formula_or_rule=f"Logical Formulation: State claim -> Provide mechanism/formula -> Validate against {topic} criteria.",
                question_for_student=f"What is the key answer or definition for: {q}?",
                expected_checkpoint="Complete explanation",
            ),
        ],
        "hints": [
            f"Hint 1: Break down the question into its main subject ({subj}) and key question word.",
            f"Hint 2: Consider how this topic is defined in your Grade {inp.grade} {inp.school_board} syllabus.",
            f"Hint 3: State the direct answer clearly, then add one supporting detail.",
        ],
        "alternative_explanation": f"Alternative Conceptual Strategy for {subj}: Let's break down how this system, concept, or formula works step by step.",
        "worked_solution": (
            f"Full Worked Solution (Grade {inp.grade} {subj}):\n"
            f"Question: {q}\n"
            f"Key Concept: {topic}.\n"
            f"Detailed curriculum-aligned explanation tailored for Grade {inp.grade} {inp.school_board}."
        ),
        "similar_question": {
            "question": f"Similar Practice Question: Can you give another example related to {topic}?",
            "topic": topic,
            "expected_concept": topic,
        },
    }


class TeachingAgent:
    """Specialist Agent 3: Interactive Socratic Tutor that guides step-by-step without spoiling the answer."""

    def execute(self, inp: TeachingAgentInput) -> TeachingAgentOutput:
        start_t = time.perf_counter()

        if inp.simulate_agent_failure:
            raise AgentExecutionError("TeachingAgent failed: Simulated teaching engine error.")

        model_res = invoke_gemini_or_structured_engine(
            agent_name="TeachingAgent",
            system_instruction="Act as an interactive Socratic tutor. Guide step by step in the student's preferred language.",
            user_prompt=f"Grade: {inp.grade}, Mode: {inp.pedagogical_mode}, Lang: {inp.preferred_explanation_language}, Q: {inp.extracted_question}",
            simulate_failure=inp.simulate_model_failure,
        )

        # 1. Verify language support honestly (Never silently substitute another language!)
        lang = inp.preferred_explanation_language
        sec_lang = inp.secondary_explanation_language
        _is_verified_lang, capability_notice = verify_language_capability(lang)

        pack = LANGUAGE_TUTOR_PACKS.get(lang)
        if not pack:
            base_en = LANGUAGE_TUTOR_PACKS["English"]
            pack = {
                k: f"[{lang} Language Notice: Full native script model pack for {lang} is in progressive rollout; showing guided explanation with {lang} context] {v}"
                for k, v in base_en.items()
            }

        bilingual_active = bool(sec_lang and sec_lang.lower() != lang.lower())
        sec_pack = LANGUAGE_TUTOR_PACKS.get(sec_lang or "English", LANGUAGE_TUTOR_PACKS["English"])
        grade_prefix = _get_grade_band_adaptation_prefix(inp.grade, inp.school_board)

        # Safe, robust defaults for every variable across all agent execution paths
        concept_text: str = ""
        sec_concept_text: Optional[str] = None
        example_text: str = ""
        prereq_lesson: Optional[str] = None
        steps: List[TeachingStepItem] = []
        progressive_hints: List[str] = []
        similar_practice: Dict[str, Any] = {
            "question": f"Similar Practice Question: Can you apply this concept to another problem in {inp.detected_topic}?",
            "topic": inp.detected_topic,
            "expected_concept": inp.detected_topic,
        }
        full_solution_text: str = ""
        is_fraction_problem: bool = False
        dyn: Dict[str, Any] = {}
        math_plan: Optional[Dict[str, Any]] = None

        is_science = inp.detected_subject.lower() == "science" or any(
            w in inp.extracted_question.lower() for w in ["photosynthesis", "chlorophyll", "acid", "base", "plant"]
        )

        # 2. Build interactive steps & progressive hints using deterministic symbolic math or science engine
        if is_science:
            concept_text = f"{grade_prefix}{pack['science_concept']}"
            sec_concept_text = (
                f"[{sec_lang} Bilingual Explanation]: {sec_pack['science_concept']}"
                if bilingual_active
                else None
            )
            example_text = (
                f"Grade {inp.grade} Young Explorer Example: Imagine a little green leaf acting like a tiny kitchen that uses sunshine to make sweet food for the plant!"
                if inp.grade <= 5
                else pack["science_example"]
            )
            steps = [
                TeachingStepItem(
                    step_number=1,
                    title="Identify Key Leaf Pigment & Reactants",
                    instruction="Recall how green leaves absorb sunlight and take in carbon dioxide.",
                    why_this_step_matters="Chlorophyll inside chloroplast thylakoids acts like a solar collector, capturing photon packets to split water into hydrogen and oxygen.",
                    step_formula_or_rule="Light-Dependent Reaction: Photons + Chlorophyll + H2O → O2 gas + ATP/NADPH energy packets.",
                    question_for_student=pack["science_prompt"],
                    expected_checkpoint="Chlorophyll and Oxygen",
                ),
                TeachingStepItem(
                    step_number=2,
                    title="Complete the Photosynthesis Word Equation",
                    instruction="Combine Carbon Dioxide + Water in the presence of Sunlight & Chlorophyll.",
                    why_this_step_matters="Carbon fixation (Calvin Cycle) locks carbon from CO2 into glucose sugar (C6H12O6), creating stored chemical energy.",
                    step_formula_or_rule="Overall Balanced Equation: 6CO2 + 6H2O —(Sunlight + Chlorophyll)→ C6H12O6 + 6O2.",
                    question_for_student="Step 2 Turn: What carbohydrate food is produced by the plant along with oxygen?",
                    expected_checkpoint="Glucose",
                ),
            ]
            progressive_hints = [
                "Hint 1 (Gentle Nudge): The green pigment starts with 'Chloro-' and the gas we breathe starts with 'Oxy-'.",
                "Hint 2 (Concept Link): Leaves look green because of Chlorophyll, which traps solar energy to split water and combine it with CO2.",
                "Hint 3 (Direct Scaffold): Chlorophyll traps sunlight, and the plant produces Glucose + Oxygen gas.",
            ]
            similar_practice = {
                "question": "Similar Practice Question: Why do plants kept in a completely dark room for 72 hours test negative for starch in the iodine leaf test?",
                "topic": inp.detected_topic,
                "expected_concept": "Without sunlight, photosynthesis cannot occur to produce glucose/starch.",
            }
            full_solution_text = (
                f"Full Worked Solution (Grade {inp.grade} Science — Photosynthesis):\n"
                "1. Chlorophyll (the green pigment inside chloroplasts of leaves) absorbs sunlight energy.\n"
                "2. Roots absorb water (H2O) and stomata take in Carbon Dioxide (CO2).\n"
                "3. Equation: 6CO2 + 6H2O —(Sunlight & Chlorophyll)→ C6H12O6 (Glucose) + 6O2 (Oxygen)."
            )
        else:
            math_plan = solve_and_plan_math_problem(inp.extracted_question, grade=inp.grade)
            prob_type = math_plan["problem_type"]

            if prob_type in ("HCF", "LCM", "LINEAR_EQUATION", "ARITHMETIC"):
                steps = [TeachingStepItem(**s) for s in math_plan["steps"]]
                progressive_hints = list(math_plan["hints"])
                similar_practice = dict(math_plan["similar_question"])
                full_solution_text = str(math_plan["worked_solution"])
                sec_concept_text = None
                is_fraction_problem = False

                if prob_type == "HCF":
                    a, b = math_plan["operands"]
                    concept_text = (
                        f"{grade_prefix}To find the Highest Common Factor (HCF) of {a} and {b}, "
                        f"we list all exact divisors (factors) of {a} and {b}, find the factors they share in common, "
                        f"and choose the greatest factor among them."
                    )
                    example_text = (
                        f"Real-World Indian Example (Grade {inp.grade}): Imagine packing {a} laddoos and {b} barfis into equal gift boxes "
                        f"with none left over. The largest number of identical boxes you can make is the HCF of {a} and {b}!"
                    )
                elif prob_type == "LCM":
                    a, b = math_plan["operands"]
                    concept_text = (
                        f"{grade_prefix}To find the Least Common Multiple (LCM) of {a} and {b}, "
                        f"we list the multiplication table (multiples) of {a} and {b} and identify the smallest positive number that appears in both lists."
                    )
                    example_text = (
                        f"Real-World Indian Example (Grade {inp.grade}): If one school bell rings every {a} minutes and another rings every {b} minutes, "
                        f"the LCM tells us after how many minutes both bells will ring together again!"
                    )
                elif prob_type == "LINEAR_EQUATION":
                    a, var_name, op, b, c = math_plan["operands"]
                    concept_text = (
                        f"{grade_prefix}To solve the linear equation {a}{var_name} {op} {b} = {c}, "
                        f"treat the '=' sign like a balanced weighing scale (tarazu). First isolate the variable term {a}{var_name} by transposing {op} {b} to the right-hand side with the opposite sign."
                    )
                    example_text = (
                        f"Real-World Example (Grade {inp.grade}): Think of {var_name} as the price of one notebook when {a} notebooks adjusted by {op}{b} rupees equals {c} rupees."
                    )
                elif prob_type == "ARITHMETIC":
                    x, op, y = math_plan["operands"]
                    concept_text = (
                        f"{grade_prefix}Let's solve {x} {op} {y} step by step by aligning place values (hundreds, tens, and ones)."
                    )
                    example_text = (
                        f"Real-World Example (Grade {inp.grade}): Imagine counting {x} mangoes in one basket and combining/comparing with {y} mangoes in another basket!"
                    )
            else:
                is_fraction_problem = bool(
                    re.search(r"\d+\s*/\s*\d+", inp.extracted_question)
                    or "fraction" in inp.extracted_question.lower()
                    or "1/4" in inp.extracted_question
                )
                if is_fraction_problem:
                    concept_text = f"{grade_prefix}{pack['fraction_concept']}"
                    example_text = (
                        f"Grade {inp.grade} Visual Story Example: Imagine sharing a chocolate bar or a warm roti with your friend—cutting into equal-sized pieces makes counting super easy!"
                        if inp.grade <= 5
                        else pack["fraction_example"]
                    )
                    sec_concept_text = (
                        f"[{sec_lang} Bilingual Explanation]: {sec_pack['fraction_concept']}"
                        if bilingual_active
                        else None
                    )
                    steps = [TeachingStepItem(**s) for s in math_plan["steps"]]
                    if math_plan["operands"] == (1, 4, "+", 1, 6) and lang != "English":
                        steps[0].question_for_student = pack["step1_prompt"]
                        steps[1].question_for_student = pack["step2_prompt"]
                        steps[2].question_for_student = pack["step3_prompt"]
                    progressive_hints = list(math_plan["hints"])
                    similar_practice = dict(math_plan["similar_question"])
                    full_solution_text = str(math_plan["worked_solution"])
                else:
                    # DYNAMIC MULTI-SUBJECT LESSON VIA REAL AI
                    dyn = _generate_dynamic_subject_lesson(inp, lang, grade_prefix)
                    concept_text = dyn["concept_text"]
                    example_text = dyn["example_text"]
                    sec_concept_text = None
                    steps = dyn["steps"]
                    progressive_hints = dyn["hints"]
                    similar_practice = dyn["similar_question"]
                    full_solution_text = dyn["worked_solution"]

        # Ensure safe fallback for steps and hints
        if not steps:
            steps = [
                TeachingStepItem(
                    step_number=1,
                    title="Understand & Reason",
                    instruction=f"Examine what is given and required in: {inp.extracted_question}",
                    question_for_student="What is the first step or key fact needed to solve this?",
                    expected_checkpoint="Key fact",
                )
            ]
        if not progressive_hints:
            progressive_hints = [
                f"Hint 1: Review the definitions and rules for {inp.detected_topic}.",
                f"Hint 2: Break down the problem step by step.",
                f"Hint 3: Apply the method learned in Grade {inp.grade} {inp.school_board} syllabus.",
            ]

        # 3. Handle Pedagogical Mode Specifics
        step_idx = max(1, min(inp.current_step_index, len(steps)))
        active_step = steps[step_idx - 1]

        prereq_lesson: Optional[str] = None
        if inp.pedagogical_mode == "TEACH_PREREQUISITE_FIRST" or inp.missing_prerequisite_topic:
            prereq_lesson = (
                pack["prereq_lcm"]
                if is_fraction_problem
                else f"Foundational Prerequisite: Before tackling this question, let's review the core concept of {inp.missing_prerequisite_topic or inp.detected_topic}."
            )

        active_hint: Optional[str] = None
        if inp.pedagogical_mode == "PROGRESSIVE_HINT" or inp.mistake_count > 0:
            h_idx = max(0, min(inp.hint_level - 1, len(progressive_hints) - 1))
            active_hint = progressive_hints[h_idx]

        incorrect_explanation: Optional[str] = None
        if inp.last_detected_misconception:
            incorrect_explanation = (
                f"Why that attempt wasn't quite right: {inp.last_detected_misconception} "
                f"Let's fix that step together using {active_hint or 'the step guide below'}."
            )

        alt_explanation: Optional[str] = None
        if inp.pedagogical_mode == "ALTERNATIVE_EXPLANATION" or inp.mistake_count >= 2:
            if is_fraction_problem:
                alt_explanation = pack.get("alt_explanation")
            elif dyn.get("alternative_explanation"):
                alt_explanation = dyn.get("alternative_explanation")
            else:
                alt_explanation = f"Alternative Conceptual Strategy for {inp.detected_subject}: {example_text}"

        # Crucial Socratic Rule: Never reveal the full worked solution unless explicitly requested
        reveal_full = bool(
            inp.request_full_solution or inp.pedagogical_mode == "FULL_WORKED_SOLUTION"
        )

        # Requirement 1: The AI Learning Buddy must teach through clear text explanations,
        # step-by-step instructions, examples, questions, and text-based practice.
        # Do not automatically generate or display pictures/diagrams as part of an explanation.
        video_module = get_curated_video_explanation(
            detected_subject=inp.detected_subject,
            detected_topic=inp.detected_topic,
            question=inp.extracted_question,
            grade=inp.grade,
            math_plan=math_plan,
        )

        elapsed_ms = round((time.perf_counter() - start_t) * 1000, 2)

        return TeachingAgentOutput(
            executed_at=utc_now(),
            duration_ms=elapsed_ms,
            model_used=str(model_res["model_used"]),
            explanation_language=lang,
            secondary_explanation_language=sec_lang,
            bilingual_active=bilingual_active,
            language_capability_notice=capability_notice,
            pedagogical_mode_applied=inp.pedagogical_mode,
            concept_explanation=concept_text,
            bilingual_secondary_explanation=sec_concept_text,
            real_world_example=example_text,
            prerequisite_mini_lesson=prereq_lesson,
            steps_breakdown=steps,
            active_step_number=step_idx,
            prompt_for_student_attempt=(
                similar_practice["question"]
                if inp.pedagogical_mode == "SIMILAR_PRACTICE_QUESTION"
                else active_step.question_for_student
            ),
            progressive_hints=progressive_hints,
            active_hint_shown=active_hint,
            incorrect_answer_explanation=incorrect_explanation,
            alternative_explanation=alt_explanation,
            full_worked_solution=full_solution_text if reveal_full else None,
            answer_withheld_for_guided_learning=not reveal_full,
            similar_practice_question=similar_practice,
            visual_diagram_svg=None,
            visual_diagram_caption=None,
            visual_concept_type=None,
            video_explanation=video_module,
        )
