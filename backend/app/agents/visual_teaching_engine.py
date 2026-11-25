"""
SparkMinds AI — Visual AI Teaching Engine
=========================================
Decides when a visual diagram, labelled illustration, or lightweight interactive
animation genuinely improves understanding of a student's question alongside the
real AI tutor explanation.

Rules:
- Never force unrelated decorative graphics for greetings or simple non-visual chat.
- Support Mathematics, Science, Geography, History, English, and Computer Science.
- Extract real numbers/fractions/equations from the student's actual question when
  available so diagrams reflect what the student asked.
- Always include labelled parts, a short step-by-step visual walkthrough, an
  interactive check question with instant feedback, and a clean text fallback.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple


def _extract_fractions(text: str) -> List[Tuple[int, int]]:
    matches = re.findall(r"\b(\d{1,2})\s*/\s*(\d{1,2})\b", text)
    parsed: List[Tuple[int, int]] = []
    for num_s, den_s in matches:
        num, den = int(num_s), int(den_s)
        if 0 < den <= 16 and 0 <= num <= den * 2:
            parsed.append((num, den))
    return parsed[:2]


def _extract_small_integers(text: str) -> List[int]:
    nums = [int(n) for n in re.findall(r"-?\b\d{1,2}\b", text)]
    return [n for n in nums if -12 <= n <= 20][:3]


def _has_any(text: str, keywords: Tuple[str, ...]) -> bool:
    """Whole-word/phrase boundary matcher so 'explain' never matches 'plain'."""
    for kw in keywords:
        if re.search(rf"\b{re.escape(kw)}\b", text):
            return True
    return False


def _visual_payload(
    *,
    visual_type: str,
    subject: str,
    concept: str,
    title: str,
    caption: str,
    interactive_animated: bool,
    labels: List[Dict[str, str]],
    step_by_step_walkthrough: List[str],
    check_question: Dict[str, Any],
    fallback_text_explanation: str,
    dynamic_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "should_display_visual": True,
        "visual_type": visual_type,
        "subject": subject,
        "concept": concept,
        "title": title,
        "caption": caption,
        "interactive_animated": interactive_animated,
        "labels": labels,
        "step_by_step_walkthrough": step_by_step_walkthrough,
        "check_question": check_question,
        "fallback_text_explanation": fallback_text_explanation,
        "dynamic_params": dynamic_params or {},
    }


def build_visual_teaching_aid(
    *,
    message: str,
    reply_text: str = "",
    grade: int = 7,
) -> Optional[Dict[str, Any]]:
    """
    Analyze the student's question (and optionally the tutor's reply) to decide
    whether a relevant visual teaching model or animation should accompany the reply.
    Returns None when a visual diagram is not helpful (e.g. greetings, thanks, short meta chat).
    """
    raw_msg = (message or "").strip()
    if not raw_msg:
        return None

    q = raw_msg.lower()
    combined = f"{raw_msg}\n{reply_text or ''}".lower()

    # Skip purely conversational greetings / acknowledgements so visuals stay genuinely helpful
    stripped_alpha = re.sub(r"[^a-z\s]", "", q).strip()
    non_visual_phrases = {
        "hi",
        "hello",
        "hey",
        "thanks",
        "thank you",
        "ok",
        "okay",
        "got it",
        "yes",
        "no",
        "bye",
        "good morning",
        "good evening",
        "good night",
        "who are you",
        "how are you",
    }
    if stripped_alpha in non_visual_phrases or len(stripped_alpha) < 3:
        return None

    # ------------------------------------------------------------------
    # 1. MATHEMATICS VISUALS
    # ------------------------------------------------------------------
    fractions = _extract_fractions(raw_msg)
    if fractions or _has_any(
        q,
        (
            "fraction",
            "fractions",
            "numerator",
            "denominator",
            "lcm",
            "equivalent fraction",
            "half",
            "quarter",
            "ratio",
            "percentage",
            "percent",
        ),
    ):
        num1, den1 = fractions[0] if fractions else (3, 4)
        num2, den2 = fractions[1] if len(fractions) > 1 else (1, 4)
        has_two = len(fractions) > 1
        return _visual_payload(
            visual_type="math_fractions_animated",
            subject="Mathematics",
            concept="Fractions & Equal Parts",
            title=f"Visual Fraction Model ({num1}/{den1}" + (f" & {num2}/{den2})" if has_two else ")"),
            caption="Interactive equal-parts visual showing how numerator and denominator work together.",
            interactive_animated=True,
            labels=[
                {
                    "id": "numerator",
                    "label": f"Numerator ({num1})",
                    "description": "The top number counts how many equal shaded parts we select.",
                },
                {
                    "id": "denominator",
                    "label": f"Denominator ({den1})",
                    "description": "The bottom number tells how many equal parts make one whole.",
                },
                {
                    "id": "whole",
                    "label": "One Whole (1)",
                    "description": f"All {den1} equal slices combined equal 1 complete whole.",
                },
            ],
            step_by_step_walkthrough=[
                f"Divide one whole shape into {den1} equal slices (that is the denominator).",
                f"Shade {min(num1, den1)} slice(s) to represent the numerator ({num1}).",
                "Compare shaded area against the full shape — or use the interactive slicer to test equivalent fractions!",
            ],
            check_question={
                "prompt": f"In the fraction {num1}/{den1}, what does the bottom number ({den1}) tell us?",
                "options": [
                    f"Total equal parts in 1 whole ({den1} parts)",
                    "How many parts are shaded",
                    "The answer after multiplying",
                ],
                "correct_answer": f"Total equal parts in 1 whole ({den1} parts)",
                "hint": "Remember: D for Denominator = Down (bottom) = total equal parts in one whole.",
                "explanation": f"Exactly! The denominator ({den1}) shows how many equal pieces make one whole, while the numerator ({num1}) counts the selected pieces.",
            },
            fallback_text_explanation=f"Picture a bar split into {den1} equal pieces with {num1} pieces shaded.",
            dynamic_params={
                "numerator": num1,
                "denominator": den1,
                "second_numerator": num2 if has_two else None,
                "second_denominator": den2 if has_two else None,
            },
        )

    if _has_any(
        q,
        (
            "number line",
            "integer",
            "integers",
            "negative number",
            "negative numbers",
            "positive number",
            "positive numbers",
            "add on a number line",
            "subtract on a number line",
            "addition",
            "subtraction",
        ),
    ):
        ints = _extract_small_integers(raw_msg)
        start_val = ints[0] if len(ints) >= 1 else -2
        delta_val = ints[1] if len(ints) >= 2 else 5
        if "-" in raw_msg and len(ints) >= 2 and ints[1] > 0 and "subtract" in q:
            delta_val = -delta_val
        end_val = max(-8, min(8, start_val + delta_val))
        return _visual_payload(
            visual_type="math_number_line",
            subject="Mathematics",
            concept="Number Line & Integers",
            title="Interactive Number Line Jumps",
            caption="Watch how moving right adds positive units and moving left subtracts.",
            interactive_animated=True,
            labels=[
                {"id": "origin", "label": "Zero (0)", "description": "Zero separates negative numbers on the left from positive numbers on the right."},
                {"id": "start", "label": f"Start ({start_val})", "description": f"Begin at {start_val} on the number line."},
                {"id": "jump", "label": f"Jump ({'+' if delta_val >= 0 else ''}{delta_val})", "description": "Move right for positive (+) and left for negative (−)."},
                {"id": "result", "label": f"Landing ({end_val})", "description": f"You land on {end_val}."},
            ],
            step_by_step_walkthrough=[
                f"Find your starting point at {start_val} on the number line.",
                f"Move {abs(delta_val)} step(s) to the {'right' if delta_val >= 0 else 'left'}.",
                f"Read the final landing point: {end_val}.",
            ],
            check_question={
                "prompt": "Which direction do you move on a number line when adding a positive number?",
                "options": ["To the right (+)", "To the left (−)", "Stay at zero"],
                "correct_answer": "To the right (+)",
                "hint": "Numbers get larger as you go rightward.",
                "explanation": "Right! Moving right increases the value (addition), while moving left decreases it (subtraction).",
            },
            fallback_text_explanation=f"Start at {start_val}, hop {abs(delta_val)} units {'right' if delta_val >= 0 else 'left'}, and land at {end_val}.",
            dynamic_params={"start": max(-6, min(6, start_val)), "delta": max(-6, min(6, delta_val)), "end": end_val},
        )

    if _has_any(
        q,
        (
            "triangle",
            "triangles",
            "pythagoras",
            "pythagorean",
            "hypotenuse",
            "angle",
            "angles",
            "area",
            "perimeter",
            "circle",
            "circles",
            "radius",
            "diameter",
            "rectangle",
            "geometry",
            "polygon",
        ),
    ):
        shape_kind = "circle" if any(k in q for k in ("circle", "radius", "diameter", "circumference")) else "triangle"
        return _visual_payload(
            visual_type="math_geometry",
            subject="Mathematics",
            concept="Geometry & Measurement",
            title="Labelled Right Triangle & Angles" if shape_kind == "triangle" else "Labelled Circle Anatomy",
            caption="Inspect sides, vertices, and key formulas directly on the shape.",
            interactive_animated=True,
            labels=(
                [
                    {"id": "base", "label": "Base (b)", "description": "The bottom side perpendicular to the height."},
                    {"id": "height", "label": "Height (h)", "description": "The vertical perpendicular distance from base to apex."},
                    {"id": "hypotenuse", "label": "Hypotenuse (c)", "description": "The longest side opposite the 90° right angle (a² + b² = c²)."},
                    {"id": "right_angle", "label": "90° Right Angle", "description": "The square corner marker confirms perpendicular sides."},
                ]
                if shape_kind == "triangle"
                else [
                    {"id": "center", "label": "Centre (O)", "description": "Every point on the circle is equally distant from O."},
                    {"id": "radius", "label": "Radius (r)", "description": "Distance from centre to the edge (r = d ÷ 2)."},
                    {"id": "diameter", "label": "Diameter (d)", "description": "Straight line passing through the centre (d = 2r)."},
                    {"id": "circumference", "label": "Circumference (2πr)", "description": "Total boundary length around the circle."},
                ]
            ),
            step_by_step_walkthrough=[
                "Identify each labelled measurement given in the problem.",
                "Choose the matching formula (Area = ½ × b × h, or a² + b² = c², or Area = πr²).",
                "Substitute the known values carefully and include the correct units.",
            ],
            check_question={
                "prompt": (
                    "In a right-angled triangle, which side is always the longest?"
                    if shape_kind == "triangle"
                    else "If a circle has radius 5 cm, what is its diameter?"
                ),
                "options": (
                    ["Hypotenuse (opposite 90°)", "Base", "Height"]
                    if shape_kind == "triangle"
                    else ["10 cm (2 × radius)", "2.5 cm", "5 cm"]
                ),
                "correct_answer": "Hypotenuse (opposite 90°)" if shape_kind == "triangle" else "10 cm (2 × radius)",
                "hint": "Check the longest highlighted line on the diagram." if shape_kind == "triangle" else "Diameter goes all the way across through the centre.",
                "explanation": (
                    "Correct! The hypotenuse sits opposite the 90° angle and is always the longest side."
                    if shape_kind == "triangle"
                    else "Spot on! Diameter is always twice the radius (2 × 5 = 10 cm)."
                ),
            },
            fallback_text_explanation="Visualize the labelled sides and apply the perimeter or area relationship step by step.",
            dynamic_params={"shape": shape_kind},
        )

    if _has_any(
        q,
        (
            "equation",
            "equations",
            "algebra",
            "linear",
            "quadratic",
            "graph",
            "graphs",
            "slope",
            "coordinate",
            "coordinates",
            "solve for x",
            "variable",
        ),
    ) or "x =" in q or "2x" in q or "3x" in q:
        return _visual_payload(
            visual_type="math_graph_steps",
            subject="Mathematics",
            concept="Algebra & Coordinate Graphs",
            title="Visual Equation & Coordinate Graph",
            caption="See how an algebraic rule connects x-inputs to y-outputs on a coordinate grid.",
            interactive_animated=True,
            labels=[
                {"id": "x_axis", "label": "X-Axis (Input)", "description": "Horizontal axis showing independent variable x."},
                {"id": "y_axis", "label": "Y-Axis (Output)", "description": "Vertical axis showing dependent result y."},
                {"id": "intercept", "label": "Y-Intercept (c)", "description": "Where the line crosses the y-axis when x = 0."},
                {"id": "slope", "label": "Slope (m = Rise / Run)", "description": "How steeply y changes for each +1 step in x."},
            ],
            step_by_step_walkthrough=[
                "Keep the equation balanced like a scale — do the same operation to both sides.",
                "Isolate the variable term first, then divide to find the single variable value.",
                "Plot (x, y) pairs on the coordinate plane to verify the straight-line pattern.",
            ],
            check_question={
                "prompt": "If 2x + 3 = 11, what is the very first step to isolate 2x?",
                "options": [
                    "Subtract 3 from both sides",
                    "Multiply both sides by 3",
                    "Add 11 to both sides",
                ],
                "correct_answer": "Subtract 3 from both sides",
                "hint": "Undo the +3 using the opposite operation on both sides.",
                "explanation": "Awesome! Subtracting 3 from both sides gives 2x = 8, and dividing by 2 gives x = 4.",
            },
            fallback_text_explanation="Balance both sides step by step and plot (x, y) points on the x-y axes.",
            dynamic_params={"grade": grade},
        )

    # ------------------------------------------------------------------
    # 2. SCIENCE VISUALS
    # ------------------------------------------------------------------
    if _has_any(q, ("water cycle", "evaporation", "condensation", "precipitation", "transpiration", "rain cycle")):
        return _visual_payload(
            visual_type="science_water_cycle_animated",
            subject="Science",
            concept="The Water Cycle",
            title="Animated Water Cycle Model",
            caption="Follow solar energy moving water continuously between oceans, clouds, and land.",
            interactive_animated=True,
            labels=[
                {"id": "evaporation", "label": "1. Evaporation", "description": "Sunlight heats surface water into rising invisible water vapour."},
                {"id": "condensation", "label": "2. Condensation", "description": "Vapour cools high in the sky and forms tiny cloud droplets."},
                {"id": "precipitation", "label": "3. Precipitation", "description": "Heavy droplets fall back to Earth as rain, snow, or hail."},
                {"id": "collection", "label": "4. Collection", "description": "Water flows into rivers, lakes, groundwater, and oceans."},
            ],
            step_by_step_walkthrough=[
                "Sun warms oceans and rivers → Evaporation turns liquid water into vapour.",
                "Warm vapour rises and cools → Condensation builds clouds.",
                "Cloud droplets merge and fall → Precipitation returns water to Earth.",
                "Runoff gathers in streams and seas → Collection restarts the cycle.",
            ],
            check_question={
                "prompt": "Which stage of the water cycle turns cooled water vapour into clouds?",
                "options": ["Condensation", "Evaporation", "Collection"],
                "correct_answer": "Condensation",
                "hint": "Look at the rising vapour arrows meeting the cool sky.",
                "explanation": "Yes! Condensation cools water vapour back into tiny liquid droplets that form clouds.",
            },
            fallback_text_explanation="Evaporation (sun heats water) -> Condensation (clouds form) -> Precipitation (rain falls) -> Collection (rivers & oceans).",
        )

    if _has_any(
        q,
        (
            "cell",
            "cells",
            "nucleus",
            "mitochondria",
            "cytoplasm",
            "chloroplast",
            "chloroplasts",
            "organelle",
            "organelles",
            "photosynthesis",
            "plant cell",
            "animal cell",
        ),
    ):
        is_plant = any(k in q for k in ("plant", "chloroplast", "photosynthesis", "cell wall"))
        return _visual_payload(
            visual_type="science_cell_diagram",
            subject="Science",
            concept="Cell Structure & Photosynthesis" if is_plant else "Cell Structure & Organelles",
            title="Labelled Plant Cell & Chloroplasts" if is_plant else "Labelled Eukaryotic Cell",
            caption="Tap each organelle on the diagram to see its exact job inside the cell.",
            interactive_animated=True,
            labels=[
                {"id": "nucleus", "label": "Nucleus", "description": "Control centre storing DNA instructions for the cell."},
                {"id": "mitochondria", "label": "Mitochondria", "description": "Powerhouse converting nutrients into usable cellular energy (ATP)."},
                {"id": "membrane", "label": "Cell Membrane", "description": "Selective gate controlling what enters and exits the cell."},
                {
                    "id": "chloroplast" if is_plant else "cytoplasm",
                    "label": "Chloroplast" if is_plant else "Cytoplasm",
                    "description": (
                        "Captures sunlight, water, and CO₂ to make glucose and oxygen (photosynthesis)."
                        if is_plant
                        else "Jelly-like fluid holding organelles and supporting chemical reactions."
                    ),
                },
            ],
            step_by_step_walkthrough=[
                "The outer membrane (and cell wall in plants) protects and shapes the cell.",
                "The nucleus directs growth and protein building using DNA.",
                "Mitochondria release energy, while plant chloroplasts harness sunlight for food.",
            ],
            check_question={
                "prompt": "Which organelle is known as the powerhouse because it releases energy for the cell?",
                "options": ["Mitochondria", "Cell Membrane", "Vacuole"],
                "correct_answer": "Mitochondria",
                "hint": "Tap the folded bean-shaped organelle in the diagram.",
                "explanation": "Brilliant! Mitochondria carry out cellular respiration to produce usable energy.",
            },
            fallback_text_explanation="Key cell parts: Nucleus (control centre), Mitochondria (energy), Cytoplasm (fluid), Cell Membrane (boundary).",
            dynamic_params={"is_plant": is_plant},
        )

    if _has_any(
        q,
        (
            "circuit",
            "circuits",
            "electricity",
            "electric current",
            "voltage",
            "ohm",
            "resistor",
            "bulb",
            "battery",
            "series circuit",
            "parallel circuit",
            "conductor",
        ),
    ):
        return _visual_payload(
            visual_type="science_electric_circuit_animated",
            subject="Science",
            concept="Electric Circuits & Current Flow",
            title="Interactive Animated Electric Circuit",
            caption="Toggle the switch ON and OFF to watch how closed paths allow current to light the bulb.",
            interactive_animated=True,
            labels=[
                {"id": "battery", "label": "Battery (Voltage V)", "description": "Provides electrical push (potential difference) around the loop."},
                {"id": "switch", "label": "Switch", "description": "Closes the loop so current flows, or opens it to stop current."},
                {"id": "bulb", "label": "Lamp / Resistor (R)", "description": "Converts electrical energy into light and heat."},
                {"id": "wire", "label": "Conducting Wire (Current I)", "description": "Low-resistance copper path carrying moving electric charges."},
            ],
            step_by_step_walkthrough=[
                "A circuit must form a complete closed loop from battery (+) through the bulb back to (−).",
                "Closing the switch connects the path so current (I = V / R) flows smoothly.",
                "Opening the switch breaks the path and stops electron flow immediately.",
            ],
            check_question={
                "prompt": "What happens to the bulb when you open the switch in a simple series circuit?",
                "options": [
                    "It turns off because the loop is broken",
                    "It glows twice as bright",
                    "The battery reverses direction",
                ],
                "correct_answer": "It turns off because the loop is broken",
                "hint": "Try toggling the switch button right on the circuit visual!",
                "explanation": "Spot on! Electric current needs a continuous closed conducting path to flow.",
            },
            fallback_text_explanation="Battery pushes charge through wires -> closed switch completes the loop -> bulb lights up (V = I × R).",
        )

    if _has_any(
        q,
        (
            "force",
            "forces",
            "motion",
            "newton",
            "gravity",
            "friction",
            "acceleration",
            "velocity",
            "speed",
            "inertia",
            "momentum",
        ),
    ):
        return _visual_payload(
            visual_type="science_forces_motion_animated",
            subject="Science",
            concept="Forces, Friction & Motion",
            title="Interactive Force & Motion Vector Lab",
            caption="Compare applied push force vs friction and gravity arrows acting on a moving block.",
            interactive_animated=True,
            labels=[
                {"id": "applied", "label": "Applied Force (F)", "description": "Forward push or pull trying to accelerate the object."},
                {"id": "friction", "label": "Friction (f)", "description": "Surface resistance pushing opposite to the motion direction."},
                {"id": "gravity", "label": "Gravity (Weight = mg)", "description": "Earth's downward pull acting on the object's mass."},
                {"id": "normal", "label": "Normal Force (N)", "description": "Upward support force from the surface balancing gravity."},
            ],
            step_by_step_walkthrough=[
                "Draw arrows from the object showing every force's direction and size.",
                "Net horizontal force = Applied Force − Friction.",
                "If Applied Force > Friction, the object accelerates forward (F_net = m × a).",
            ],
            check_question={
                "prompt": "If a 12 N push acts right and 4 N of friction acts left, what is the net force?",
                "options": ["8 N to the right", "16 N to the right", "4 N to the left"],
                "correct_answer": "8 N to the right",
                "hint": "Opposite forces subtract: 12 N − 4 N.",
                "explanation": "Correct! 12 N − 4 N = 8 N rightward, so the block accelerates to the right.",
            },
            fallback_text_explanation="Net force combines opposing vectors: Push right minus Friction left determines acceleration (F = ma).",
        )

    if _has_any(
        q,
        (
            "solar system",
            "planet",
            "planets",
            "orbit",
            "orbiting",
            "eclipse",
            "moon",
            "earth rotation",
            "revolution",
            "seasons",
            "sun",
            "gravity orbit",
        ),
    ):
        return _visual_payload(
            visual_type="science_solar_system_animated",
            subject="Science",
            concept="Solar System & Planetary Orbits",
            title="Animated Solar System Orbits",
            caption="Watch inner and outer planets revolve around the Sun under gravitational pull.",
            interactive_animated=True,
            labels=[
                {"id": "sun", "label": "The Sun", "description": "Central star whose gravity keeps every planet in orbit."},
                {"id": "inner", "label": "Rocky Inner Planets", "description": "Mercury, Venus, Earth, and Mars orbit closer and faster."},
                {"id": "earth", "label": "Earth (365.25 days)", "description": "Rotates on its tilted axis (day/night) and orbits the Sun (seasons)."},
                {"id": "outer", "label": "Gas & Ice Giants", "description": "Jupiter, Saturn, Uranus, and Neptune travel larger outer orbits."},
            ],
            step_by_step_walkthrough=[
                "The Sun contains over 99% of the Solar System's mass, anchoring orbital paths.",
                "Closer planets complete one revolution faster than distant planets.",
                "Earth's 24-hour spin creates day & night; its 1-year tilted orbit creates seasons.",
            ],
            check_question={
                "prompt": "What causes day and night on Earth?",
                "options": [
                    "Earth's rotation on its axis (24 hours)",
                    "Earth orbiting the Sun once a year",
                    "The Moon blocking sunlight every evening",
                ],
                "correct_answer": "Earth's rotation on its axis (24 hours)",
                "hint": "Think about spinning like a top in front of a lamp.",
                "explanation": "Right! As Earth rotates every 24 hours, one side faces the Sun (day) while the opposite faces away (night).",
            },
            fallback_text_explanation="Planets orbit the central Sun; Earth spins daily (day/night) and revolves yearly on a tilted axis (seasons).",
        )

    if _has_any(
        q,
        (
            "heart",
            "lungs",
            "digestive",
            "respiratory",
            "circulatory",
            "blood",
            "oxygen",
            "human body",
            "organ",
            "organs",
            "brain",
            "stomach",
        ),
    ):
        return _visual_payload(
            visual_type="science_human_body",
            subject="Science",
            concept="Human Body & Circulation",
            title="Labelled Heart–Lungs Oxygen Loop",
            caption="Follow how oxygen moves from lungs into blood and reaches body cells.",
            interactive_animated=True,
            labels=[
                {"id": "lungs", "label": "Lungs (Gas Exchange)", "description": "Absorb fresh oxygen (O₂) and breathe out carbon dioxide (CO₂)."},
                {"id": "heart", "label": "Heart (4-Chamber Pump)", "description": "Pumps oxygen-rich blood through arteries and returns used blood to lungs."},
                {"id": "arteries", "label": "Oxygenated Arteries", "description": "Carry fresh oxygen and nutrients away from the heart to muscles & organs."},
                {"id": "veins", "label": "Deoxygenated Veins", "description": "Return CO₂-carrying blood back to the heart and lungs."},
            ],
            step_by_step_walkthrough=[
                "Inhaled air brings oxygen into the lungs' tiny air sacs (alveoli).",
                "The heart pumps oxygen-rich blood through arteries to every organ.",
                "Veins return low-oxygen blood to the heart, which sends it back to the lungs.",
            ],
            check_question={
                "prompt": "Which blood vessels carry oxygen-rich blood AWAY from the heart to the body?",
                "options": ["Arteries", "Veins", "Airways"],
                "correct_answer": "Arteries",
                "hint": "Remember A for Arteries = Away from the heart.",
                "explanation": "Exactly! Arteries carry oxygenated blood away from the heart, while veins carry blood back.",
            },
            fallback_text_explanation="Lungs load oxygen -> Heart pumps via arteries to body -> Veins return blood to heart & lungs.",
        )

    # ------------------------------------------------------------------
    # 3. GEOGRAPHY VISUALS
    # ------------------------------------------------------------------
    if _has_any(
        q,
        (
            "landform",
            "landforms",
            "mountain",
            "mountains",
            "plateau",
            "plateaus",
            "plain",
            "plains",
            "river",
            "rivers",
            "delta",
            "volcano",
            "climate",
            "monsoon",
            "latitude",
            "equator",
            "geography",
            "soil erosion",
        ),
    ):
        return _visual_payload(
            visual_type="geography_landforms",
            subject="Geography",
            concept="Earth Landforms & River Basin",
            title="Labelled Landforms & River Profile",
            caption="See how elevation changes from mountains and plateaus down to fertile plains and a river delta.",
            interactive_animated=True,
            labels=[
                {"id": "mountain", "label": "Mountain Peak", "description": "High steep elevation where snowmelt starts young fast rivers."},
                {"id": "plateau", "label": "Plateau (Tableland)", "description": "Elevated flat-topped highland rich in minerals."},
                {"id": "plain", "label": "Alluvial Plain", "description": "Flat, fertile lowland formed by river silt deposits."},
                {"id": "delta", "label": "River Delta", "description": "Fan-shaped mouth where the river splits and meets the sea."},
            ],
            step_by_step_walkthrough=[
                "Upper course: Fast river erodes steep mountain valleys.",
                "Middle course: River slows across gentle plains and deposits rich soil.",
                "Lower course: Fine silt fans out into a triangular delta at the sea.",
            ],
            check_question={
                "prompt": "Which landform is a high elevated area with a relatively flat top?",
                "options": ["Plateau", "Delta", "Valley"],
                "correct_answer": "Plateau",
                "hint": "It is often called a 'tableland'.",
                "explanation": "Correct! A plateau rises steeply above surrounding land and has a broad flat top.",
            },
            fallback_text_explanation="Elevation steps down: Mountains (steep peaks) -> Plateau (flat highland) -> Plains (fertile flatlands) -> Delta (river mouth).",
        )

    # ------------------------------------------------------------------
    # 4. HISTORY VISUALS
    # ------------------------------------------------------------------
    if _has_any(
        q,
        (
            "timeline",
            "history",
            "independence",
            "empire",
            "civilization",
            "indus valley",
            "mughal",
            "maurya",
            "world war",
            "revolution",
            "chronology",
            "century",
            "bce",
            "ce",
        ),
    ):
        return _visual_payload(
            visual_type="history_timeline",
            subject="History",
            concept="Historical Cause & Chronology",
            title="Interactive Historical Timeline Framework",
            caption="Organize any historical topic into Background → Turning Point → Key Event → Lasting Impact.",
            interactive_animated=True,
            labels=[
                {"id": "background", "label": "1. Background & Causes", "description": "Social, economic, or political conditions before the change."},
                {"id": "turning_point", "label": "2. Turning Point", "description": "The decisive spark or event that shifted history's direction."},
                {"id": "key_action", "label": "3. Key Developments", "description": "Major leaders, movements, policies, or treaties during the era."},
                {"id": "impact", "label": "4. Lasting Legacy", "description": "Long-term changes in governance, culture, rights, or daily life."},
            ],
            step_by_step_walkthrough=[
                "Place dates in chronological order (BCE counts down to 1; CE counts up).",
                "Link each event to WHY it happened (cause) and WHAT changed (effect).",
                "Recall 1 key date, 1 leader/group, and 1 consequence for exam answers.",
            ],
            check_question={
                "prompt": "Which date happened EARLIER in history: 300 BCE or 100 BCE?",
                "options": ["300 BCE", "100 BCE", "They are the same year"],
                "correct_answer": "300 BCE",
                "hint": "BCE counts backwards before year 1 CE, just like negative numbers!",
                "explanation": "Spot on! 300 BCE is 200 years earlier than 100 BCE.",
            },
            fallback_text_explanation="Timeline flow: Causes -> Turning Point -> Key Developments -> Long-Term Impact.",
        )

    # ------------------------------------------------------------------
    # 5. ENGLISH GRAMMAR & WRITING VISUALS
    # ------------------------------------------------------------------
    if _has_any(
        q,
        (
            "grammar",
            "noun",
            "nouns",
            "verb",
            "verbs",
            "adjective",
            "adjectives",
            "adverb",
            "adverbs",
            "tense",
            "tenses",
            "active voice",
            "passive voice",
            "sentence structure",
            "subject predicate",
            "clause",
            "essay",
            "paragraph",
            "story structure",
        ),
    ):
        return _visual_payload(
            visual_type="english_grammar_tree",
            subject="English",
            concept="Sentence Structure & Grammar",
            title="Visual Sentence Blueprint",
            caption="See how Subject, Action Verb, Modifiers, and Object fit together cleanly.",
            interactive_animated=True,
            labels=[
                {"id": "subject", "label": "Subject (Who/What)", "description": "The person, place, or thing performing the action."},
                {"id": "verb", "label": "Verb (Action / Tense)", "description": "Shows what happens and WHEN (past, present, or future)."},
                {"id": "modifier", "label": "Adjective / Adverb", "description": "Adds vivid detail describing nouns or how actions happen."},
                {"id": "object", "label": "Object (Receiver)", "description": "Who or what receives the verb's action."},
            ],
            step_by_step_walkthrough=[
                "Find the verb (action/state word) first.",
                "Ask 'Who or what does this verb?' to pinpoint the Subject.",
                "Check subject-verb agreement and tense consistency before finishing.",
            ],
            check_question={
                "prompt": "In 'The curious student quickly solved the puzzle', which word is the ADVERB?",
                "options": ["quickly", "curious", "puzzle"],
                "correct_answer": "quickly",
                "hint": "An adverb describes HOW the verb ('solved') happened.",
                "explanation": "Great catch! 'Quickly' modifies the verb 'solved', while 'curious' is an adjective describing 'student'.",
            },
            fallback_text_explanation="Sentence blocks: [Adjective + Subject] -> [Adverb + Verb] -> [Object].",
        )

    # ------------------------------------------------------------------
    # 6. GENERAL VISUAL REQUEST ("draw", "diagram", "visual", "show me how")
    # ------------------------------------------------------------------
    if any(k in q for k in ("diagram", "visual", "picture", "draw", "illustrate", "show me visually", "chart")) and any(
        k in combined for k in ("step", "concept", "science", "math", "explain")
    ):
        return _visual_payload(
            visual_type="math_graph_steps",
            subject="General Study",
            concept="Visual Concept Breakdown",
            title="Step-by-Step Visual Concept Map",
            caption="Interactive structured breakdown to help you see how ideas connect.",
            interactive_animated=True,
            labels=[
                {"id": "core", "label": "Core Idea", "description": "The central rule or definition from your question."},
                {"id": "link", "label": "Key Steps", "description": "Logical sequence connecting cause, method, and result."},
                {"id": "example", "label": "Worked Example", "description": "Concrete illustration linking theory to practice."},
            ],
            step_by_step_walkthrough=[
                "Identify the core definition or rule first.",
                "Trace each labelled connection in order.",
                "Test your understanding by explaining one step in your own words.",
            ],
            check_question={
                "prompt": "What is the best next move after understanding a concept diagram?",
                "options": [
                    "Solve one quick practice question to lock it in",
                    "Close the page without checking",
                    "Memorise words without understanding",
                ],
                "correct_answer": "Solve one quick practice question to lock it in",
                "hint": "Active recall makes concepts stick much longer!",
                "explanation": "Yes! Trying even one quick question right after viewing a visual strengthens memory dramatically.",
            },
            fallback_text_explanation="Break the topic into Core Rule -> Step-by-Step Method -> Worked Example -> Quick Check.",
        )

    return None
