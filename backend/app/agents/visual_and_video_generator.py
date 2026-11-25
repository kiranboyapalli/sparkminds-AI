"""
Visual Diagram & Curated Video Module Generator for SparkMinds AI Tutoring Engine.
Provides responsive, high-contrast SVG concept diagrams and syllabus-aligned curated video modules.
"""

from typing import Dict, Any, List, Optional, Tuple
import html
import re


def generate_fraction_svg(
    n1: int, d1: int, op: str, n2: int, d2: int, lcm_val: int, eq_n1: int, eq_n2: int, final_ans: str
) -> str:
    """
    Generates a responsive SVG visual comparison of fraction bars.
    Shows the first fraction, the second fraction, and the unified common-denominator bar.
    """
    total_w = 720
    bar_w = 600
    start_x = 90
    bar_h = 32

    # Segment width for common denominator
    seg_w = bar_w / max(1, lcm_val)

    # First fraction segments (eq_n1 segments of size seg_w)
    f1_fill_w = eq_n1 * seg_w
    # Second fraction segments (eq_n2 segments of size seg_w)
    f2_fill_w = eq_n2 * seg_w

    # Combined bar width
    combined_n = (eq_n1 + eq_n2) if op == "+" else abs(eq_n1 - eq_n2)
    combined_fill_w = combined_n * seg_w

    # Grid lines for common denominator bar
    lines_svg = "".join(
        f'<line x1="{start_x + i * seg_w:.1f}" y1="180" x2="{start_x + i * seg_w:.1f}" y2="{180 + bar_h}" stroke="#475569" stroke-width="1.5" />'
        for i in range(1, lcm_val)
    )

    return f"""<svg viewBox="0 0 {total_w} 250" xmlns="http://www.w3.org/2000/svg" className="w-full h-auto max-w-full" style="background: linear-gradient(135deg, #0A192F 0%, #0F2847 100%); border-radius: 16px; font-family: ui-sans-serif, system-ui, sans-serif;">
  <!-- Title & Legend Header -->
  <text x="25" y="32" fill="#00E5FF" font-size="14" font-weight="800" letter-spacing="0.5">VISUAL FRACTION MODEL: COMMON SLICE SIZE (LCM = {lcm_val})</text>
  <text x="{total_w - 25}" y="32" fill="#94A3B8" font-size="12" font-weight="600" text-anchor="end">Slice size must match before adding/subtracting</text>

  <!-- Row 1: Fraction 1 -->
  <text x="25" y="72" fill="#E2E8F0" font-size="13" font-weight="700">{n1}/{d1}</text>
  <text x="60" y="72" fill="#00E5FF" font-size="11" font-weight="600">({eq_n1}/{lcm_val})</text>
  <rect x="{start_x}" y="52" width="{bar_w}" height="{bar_h}" rx="6" fill="#1E293B" stroke="#334155" stroke-width="1.5" />
  <rect x="{start_x}" y="52" width="{f1_fill_w:.1f}" height="{bar_h}" rx="6" fill="url(#cyanGrad)" />
  <text x="{start_x + f1_fill_w / 2:.1f}" y="72" fill="#0A192F" font-size="12" font-weight="800" text-anchor="middle">{eq_n1} slices</text>

  <!-- Row 2: Fraction 2 -->
  <text x="25" y="132" fill="#E2E8F0" font-size="13" font-weight="700">{op} {n2}/{d2}</text>
  <text x="60" y="132" fill="#818CF8" font-size="11" font-weight="600">({eq_n2}/{lcm_val})</text>
  <rect x="{start_x}" y="112" width="{bar_w}" height="{bar_h}" rx="6" fill="#1E293B" stroke="#334155" stroke-width="1.5" />
  <rect x="{start_x}" y="112" width="{f2_fill_w:.1f}" height="{bar_h}" rx="6" fill="url(#indigoGrad)" />
  <text x="{start_x + f2_fill_w / 2:.1f}" y="132" fill="#FFFFFF" font-size="12" font-weight="800" text-anchor="middle">{eq_n2} slices</text>

  <!-- Row 3: Result Combined Bar -->
  <text x="25" y="198" fill="#10B981" font-size="13" font-weight="800">Total =</text>
  <rect x="{start_x}" y="180" width="{bar_w}" height="{bar_h}" rx="6" fill="#1E293B" stroke="#10B981" stroke-width="2" />
  <rect x="{start_x}" y="180" width="{f1_fill_w:.1f}" height="{bar_h}" rx="4" fill="url(#cyanGrad)" opacity="0.9" />
  <rect x="{start_x + f1_fill_w:.1f}" y="180" width="{f2_fill_w:.1f}" height="{bar_h}" rx="4" fill="url(#indigoGrad)" opacity="0.9" />
  {lines_svg}
  <text x="{start_x + combined_fill_w + 15:.1f}" y="201" fill="#10B981" font-size="13" font-weight="800">{combined_n}/{lcm_val} = {final_ans}</text>

  <!-- Gradients -->
  <defs>
    <linearGradient id="cyanGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00E5FF" />
      <stop offset="100%" stop-color="#38BDF8" />
    </linearGradient>
    <linearGradient id="indigoGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#6366F1" />
      <stop offset="100%" stop-color="#A855F7" />
    </linearGradient>
  </defs>
</svg>"""


def generate_linear_equation_svg(a: int, var_name: str, op: str, b: int, c: int, x_str: str) -> str:
    """Generates a balance scale (Tarazu) SVG representing linear equation equality."""
    return f"""<svg viewBox="0 0 720 250" xmlns="http://www.w3.org/2000/svg" className="w-full h-auto max-w-full" style="background: linear-gradient(135deg, #0A192F 0%, #0F2847 100%); border-radius: 16px; font-family: ui-sans-serif, system-ui, sans-serif;">
  <!-- Title -->
  <text x="25" y="32" fill="#00E5FF" font-size="14" font-weight="800">EQUATION BALANCE SCALE: {a}{var_name} {op} {b} = {c}</text>
  <text x="695" y="32" fill="#94A3B8" font-size="12" font-weight="600" text-anchor="end">What you do to one side, you must do to the other</text>

  <!-- Central Fulcrum & Beam -->
  <polygon points="360,195 340,225 380,225" fill="#64748B" />
  <circle cx="360" cy="195" r="7" fill="#00E5FF" />
  <line x1="160" y1="130" x2="560" y2="130" stroke="#94A3B8" stroke-width="6" stroke-linecap="round" />

  <!-- Equality Badge -->
  <circle cx="360" cy="130" r="18" fill="#0A192F" stroke="#00E5FF" stroke-width="2" />
  <text x="360" y="136" fill="#00E5FF" font-size="18" font-weight="900" text-anchor="middle">=</text>

  <!-- Left Pan Strings & Pan -->
  <line x1="180" y1="130" x2="140" y2="175" stroke="#64748B" stroke-width="2" />
  <line x1="260" y1="130" x2="300" y2="175" stroke="#64748B" stroke-width="2" />
  <line x1="130" y1="175" x2="310" y2="175" stroke="#00E5FF" stroke-width="4" stroke-linecap="round" />

  <!-- Left Pan Weights -->
  <rect x="150" y="140" width="70" height="32" rx="6" fill="#0284C7" stroke="#38BDF8" stroke-width="1.5" />
  <text x="185" y="161" fill="#FFFFFF" font-size="13" font-weight="800" text-anchor="middle">{a}{var_name}</text>
  <rect x="230" y="145" width="55" height="27" rx="6" fill="#F59E0B" stroke="#FDE68A" stroke-width="1.5" />
  <text x="257" y="163" fill="#0A192F" font-size="12" font-weight="800" text-anchor="middle">{op} {b}</text>

  <!-- Right Pan Strings & Pan -->
  <line x1="460" y1="130" x2="420" y2="175" stroke="#64748B" stroke-width="2" />
  <line x1="540" y1="130" x2="580" y2="175" stroke="#64748B" stroke-width="2" />
  <line x1="410" y1="175" x2="590" y2="175" stroke="#10B981" stroke-width="4" stroke-linecap="round" />

  <!-- Right Pan Weights -->
  <rect x="460" y="135" width="80" height="37" rx="8" fill="#10B981" stroke="#A7F3D0" stroke-width="1.5" />
  <text x="500" y="159" fill="#0A192F" font-size="15" font-weight="900" text-anchor="middle">{c}</text>

  <!-- Solved State Annotation -->
  <rect x="230" y="215" width="260" height="26" rx="6" fill="#1E293B" stroke="#00E5FF" stroke-width="1" />
  <text x="360" y="233" fill="#00E5FF" font-size="12" font-weight="800" text-anchor="middle">Step: Transpose {op}{b} → {var_name} = {x_str}</text>
</svg>"""


def generate_hcf_svg(a: int, b: int, hcf_val: int, fac_a: List[int], fac_b: List[int], common: List[int]) -> str:
    """Generates a Venn Diagram SVG showing shared factors and highest common factor."""
    only_a = [f for f in fac_a if f not in common]
    only_b = [f for f in fac_b if f not in common]

    str_only_a = ", ".join(map(str, only_a)) or "—"
    str_only_b = ", ".join(map(str, only_b)) or "—"
    str_common = ", ".join(map(str, common))

    return f"""<svg viewBox="0 0 720 250" xmlns="http://www.w3.org/2000/svg" className="w-full h-auto max-w-full" style="background: linear-gradient(135deg, #0A192F 0%, #0F2847 100%); border-radius: 16px; font-family: ui-sans-serif, system-ui, sans-serif;">
  <text x="25" y="32" fill="#00E5FF" font-size="14" font-weight="800">FACTOR VENN DIAGRAM: HCF OF {a} AND {b} = {hcf_val}</text>
  <text x="695" y="32" fill="#94A3B8" font-size="12" font-weight="600" text-anchor="end">Highest Common Factor is the largest shared divisor</text>

  <!-- Circle A -->
  <circle cx="280" cy="140" r="85" fill="#0284C7" fill-opacity="0.35" stroke="#38BDF8" stroke-width="2.5" />
  <text x="215" y="100" fill="#38BDF8" font-size="13" font-weight="800">Factors of {a}</text>
  <text x="215" y="145" fill="#E2E8F0" font-size="13" font-weight="700">{str_only_a}</text>

  <!-- Circle B -->
  <circle cx="440" cy="140" r="85" fill="#7C3AED" fill-opacity="0.35" stroke="#A78BFA" stroke-width="2.5" />
  <text x="505" y="100" fill="#A78BFA" font-size="13" font-weight="800">Factors of {b}</text>
  <text x="505" y="145" fill="#E2E8F0" font-size="13" font-weight="700">{str_only_b}</text>

  <!-- Intersection -->
  <text x="360" y="95" fill="#F59E0B" font-size="11" font-weight="800" text-anchor="middle">Common</text>
  <text x="360" y="125" fill="#FDE68A" font-size="13" font-weight="700" text-anchor="middle">{str_common}</text>

  <!-- HCF Highlight Badge -->
  <rect x="310" y="150" width="100" height="30" rx="8" fill="#10B981" stroke="#A7F3D0" stroke-width="1.5" />
  <text x="360" y="170" fill="#0A192F" font-size="12" font-weight="900" text-anchor="middle">HCF = {hcf_val}</text>
</svg>"""


def generate_lcm_svg(a: int, b: int, lcm_val: int) -> str:
    """Generates an LCM cycle jump visualization SVG."""
    return f"""<svg viewBox="0 0 720 250" xmlns="http://www.w3.org/2000/svg" className="w-full h-auto max-w-full" style="background: linear-gradient(135deg, #0A192F 0%, #0F2847 100%); border-radius: 16px; font-family: ui-sans-serif, system-ui, sans-serif;">
  <text x="25" y="32" fill="#00E5FF" font-size="14" font-weight="800">SYNCHRONIZATION TIMELINE: LCM({a}, {b}) = {lcm_val}</text>
  <text x="695" y="32" fill="#94A3B8" font-size="12" font-weight="600" text-anchor="end">Smallest positive number divisible by both</text>

  <!-- Number line base -->
  <line x1="50" y1="140" x2="670" y2="140" stroke="#475569" stroke-width="3" stroke-linecap="round" />
  
  <!-- Step jumps for a -->
  <path d="M 60,140 Q 150,70 240,140" fill="none" stroke="#00E5FF" stroke-width="2.5" stroke-dasharray="4 2" />
  <path d="M 240,140 Q 330,70 420,140" fill="none" stroke="#00E5FF" stroke-width="2.5" stroke-dasharray="4 2" />
  <path d="M 420,140 Q 510,70 600,140" fill="none" stroke="#00E5FF" stroke-width="2.5" />
  <text x="150" y="85" fill="#00E5FF" font-size="11" font-weight="700" text-anchor="middle">+{a}</text>
  <text x="330" y="85" fill="#00E5FF" font-size="11" font-weight="700" text-anchor="middle">+{a}</text>
  <text x="510" y="85" fill="#00E5FF" font-size="11" font-weight="700" text-anchor="middle">+{a}</text>

  <!-- Step jumps for b -->
  <path d="M 60,140 Q 195,200 330,140" fill="none" stroke="#F59E0B" stroke-width="2.5" stroke-dasharray="4 2" />
  <path d="M 330,140 Q 465,200 600,140" fill="none" stroke="#F59E0B" stroke-width="2.5" />
  <text x="195" y="195" fill="#F59E0B" font-size="11" font-weight="700" text-anchor="middle">+{b}</text>
  <text x="465" y="195" fill="#F59E0B" font-size="11" font-weight="700" text-anchor="middle">+{b}</text>

  <!-- Starting point -->
  <circle cx="60" cy="140" r="7" fill="#94A3B8" />
  <text x="60" y="165" fill="#94A3B8" font-size="12" font-weight="700" text-anchor="middle">0</text>

  <!-- Collision / Alignment point -->
  <circle cx="600" cy="140" r="11" fill="#10B981" stroke="#A7F3D0" stroke-width="3" />
  <rect x="520" y="210" width="160" height="28" rx="8" fill="#10B981" />
  <text x="600" y="229" fill="#0A192F" font-size="12" font-weight="900" text-anchor="middle">FIRST MATCH: LCM = {lcm_val}</text>
</svg>"""


def generate_photosynthesis_svg() -> str:
    """Generates a biological leaf diagram SVG explaining Photosynthesis."""
    return """<svg viewBox="0 0 720 250" xmlns="http://www.w3.org/2000/svg" className="w-full h-auto max-w-full" style="background: linear-gradient(135deg, #0A192F 0%, #0F2847 100%); border-radius: 16px; font-family: ui-sans-serif, system-ui, sans-serif;">
  <text x="25" y="32" fill="#00E5FF" font-size="14" font-weight="800">PHOTOSYNTHESIS BIOLOGICAL SYSTEM: 6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂</text>
  <text x="695" y="32" fill="#94A3B8" font-size="12" font-weight="600" text-anchor="end">Chloroplasts convert solar energy into chemical bonds</text>

  <!-- Sunlight Sun -->
  <circle cx="90" cy="80" r="28" fill="#F59E0B" />
  <line x1="90" y1="40" x2="90" y2="25" stroke="#FDE68A" stroke-width="3" />
  <line x1="50" y1="80" x2="35" y2="80" stroke="#FDE68A" stroke-width="3" />
  <line x1="120" y1="105" x2="160" y2="130" stroke="#FDE68A" stroke-width="3" stroke-dasharray="4 2" />
  <text x="90" y="125" fill="#FDE68A" font-size="11" font-weight="700" text-anchor="middle">Sunlight Energy</text>

  <!-- Green Leaf Schematic -->
  <path d="M 180,140 C 220,70 380,70 450,140 C 380,210 220,210 180,140 Z" fill="#059669" stroke="#34D399" stroke-width="3" />
  <line x1="180" y1="140" x2="445" y2="140" stroke="#10B981" stroke-width="2.5" />
  <text x="315" y="130" fill="#FFFFFF" font-size="12" font-weight="800" text-anchor="middle">Chloroplasts (Chlorophyll)</text>

  <!-- Reactant: CO2 In -->
  <path d="M 240,40 L 260,85" stroke="#00E5FF" stroke-width="2.5" marker-end="url(#arrow)" />
  <rect x="200" y="20" width="90" height="22" rx="4" fill="#0284C7" />
  <text x="245" y="35" fill="#FFFFFF" font-size="11" font-weight="700" text-anchor="middle">+ CO₂ (Air)</text>

  <!-- Reactant: H2O In (Roots) -->
  <path d="M 240,230 L 260,185" stroke="#38BDF8" stroke-width="2.5" />
  <rect x="200" y="215" width="90" height="22" rx="4" fill="#0369A1" />
  <text x="245" y="230" fill="#FFFFFF" font-size="11" font-weight="700" text-anchor="middle">+ H₂O (Roots)</text>

  <!-- Product: Glucose (Stored Food) -->
  <rect x="490" y="80" width="180" height="36" rx="8" fill="#10B981" stroke="#A7F3D0" stroke-width="1.5" />
  <text x="580" y="103" fill="#0A192F" font-size="12" font-weight="900" text-anchor="middle">Glucose (C₆H₁₂O₆ Food)</text>

  <!-- Product: Oxygen Released -->
  <rect x="490" y="145" width="180" height="36" rx="8" fill="#6366F1" stroke="#C7D2FE" stroke-width="1.5" />
  <text x="580" y="168" fill="#FFFFFF" font-size="12" font-weight="800" text-anchor="middle">Oxygen Released (6O₂)</text>
</svg>"""


def generate_pythagorean_svg() -> str:
    """Generates a geometric diagram illustrating the Pythagorean Theorem."""
    return """<svg viewBox="0 0 720 250" xmlns="http://www.w3.org/2000/svg" className="w-full h-auto max-w-full" style="background: linear-gradient(135deg, #0A192F 0%, #0F2847 100%); border-radius: 16px; font-family: ui-sans-serif, system-ui, sans-serif;">
  <text x="25" y="32" fill="#00E5FF" font-size="14" font-weight="800">PYTHAGOREAN THEOREM: a² + b² = c² (RIGHT TRIANGLE)</text>
  <text x="695" y="32" fill="#94A3B8" font-size="12" font-weight="600" text-anchor="end">Hypotenuse is always the longest side opposite the 90° angle</text>

  <!-- Right Triangle -->
  <polygon points="280,180 280,80 440,180" fill="#0284C7" fill-opacity="0.3" stroke="#38BDF8" stroke-width="3" />
  
  <!-- Right Angle Square -->
  <rect x="280" y="165" width="15" height="15" fill="none" stroke="#00E5FF" stroke-width="1.5" />

  <!-- Side a (vertical) -->
  <text x="260" y="135" fill="#00E5FF" font-size="13" font-weight="800" text-anchor="end">Side a (3)</text>
  <rect x="180" y="80" width="100" height="100" fill="#00E5FF" fill-opacity="0.2" stroke="#00E5FF" stroke-width="1.5" stroke-dasharray="3 3" />
  <text x="230" y="135" fill="#00E5FF" font-size="12" font-weight="700" text-anchor="middle">a² = 9</text>

  <!-- Side b (horizontal) -->
  <text x="360" y="205" fill="#F59E0B" font-size="13" font-weight="800" text-anchor="middle">Side b (4)</text>
  <rect x="280" y="180" width="160" height="50" fill="#F59E0B" fill-opacity="0.2" stroke="#F59E0B" stroke-width="1.5" stroke-dasharray="3 3" />
  <text x="360" y="215" fill="#F59E0B" font-size="12" font-weight="700" text-anchor="middle">b² = 16</text>

  <!-- Hypotenuse c -->
  <text x="385" y="120" fill="#10B981" font-size="13" font-weight="900">Hypotenuse c (5)</text>

  <!-- Calculation Summary Badge -->
  <rect x="490" y="80" width="190" height="75" rx="10" fill="#1E293B" stroke="#10B981" stroke-width="2" />
  <text x="585" y="105" fill="#FFFFFF" font-size="12" font-weight="700" text-anchor="middle">3² + 4² = c²</text>
  <text x="585" y="125" fill="#A7F3D0" font-size="12" font-weight="700" text-anchor="middle">9 + 16 = 25</text>
  <text x="585" y="145" fill="#10B981" font-size="13" font-weight="900" text-anchor="middle">c = √25 = 5</text>
</svg>"""


def generate_cell_structure_svg() -> str:
    """Generates a labeled biological diagram of plant and animal cell organelles."""
    return """<svg viewBox="0 0 720 260" xmlns="http://www.w3.org/2000/svg" className="w-full h-auto max-w-full" style="background: linear-gradient(135deg, #0A192F 0%, #0F2847 100%); border-radius: 16px; font-family: ui-sans-serif, system-ui, sans-serif;">
  <text x="25" y="32" fill="#00E5FF" font-size="14" font-weight="800">CELL STRUCTURE & ORGANELLES (PLANT & ANIMAL)</text>
  <text x="695" y="32" fill="#94A3B8" font-size="12" font-weight="600" text-anchor="end">Specialized organelles coordinate cellular metabolism</text>

  <!-- Cell Wall & Membrane Outline -->
  <rect x="50" y="60" width="380" height="175" rx="28" fill="#064E3B" fill-opacity="0.3" stroke="#10B981" stroke-width="3" />
  <rect x="58" y="68" width="364" height="159" rx="22" fill="#0F172A" fill-opacity="0.7" stroke="#34D399" stroke-width="1.5" stroke-dasharray="4 2" />

  <!-- Nucleus & Nucleolus -->
  <circle cx="150" cy="145" r="42" fill="#4338CA" fill-opacity="0.6" stroke="#818CF8" stroke-width="2.5" />
  <circle cx="150" cy="145" r="16" fill="#A78BFA" />
  <text x="150" y="149" fill="#FFFFFF" font-size="10" font-weight="800" text-anchor="middle">Nucleolus</text>

  <!-- Mitochondria (Powerhouse) -->
  <ellipse cx="280" cy="105" rx="32" ry="16" fill="#B45309" fill-opacity="0.7" stroke="#F59E0B" stroke-width="2" />
  <path d="M 255,105 Q 267,98 280,105 T 305,105" fill="none" stroke="#FDE68A" stroke-width="2" />

  <!-- Chloroplast (Plant Solar Factory) -->
  <ellipse cx="285" cy="180" rx="30" ry="16" fill="#047857" fill-opacity="0.8" stroke="#34D399" stroke-width="2" />
  <circle cx="275" cy="180" r="5" fill="#A7F3D0" />
  <circle cx="285" cy="180" r="5" fill="#A7F3D0" />
  <circle cx="295" cy="180" r="5" fill="#A7F3D0" />

  <!-- Central Vacuole -->
  <rect x="340" y="120" width="60" height="85" rx="14" fill="#0284C7" fill-opacity="0.4" stroke="#38BDF8" stroke-width="1.5" />
  <text x="370" y="165" fill="#7DD3FC" font-size="10" font-weight="700" text-anchor="middle">Vacuole</text>

  <!-- Labels & Callout Legend Panel -->
  <rect x="460" y="60" width="235" height="175" rx="12" fill="#1E293B" stroke="#475569" stroke-width="1.5" />
  <text x="475" y="85" fill="#E2E8F0" font-size="12" font-weight="800">Organelle Key & Function</text>
  
  <circle cx="475" cy="110" r="6" fill="#818CF8" />
  <text x="490" y="114" fill="#E2E8F0" font-size="11" font-weight="700">Nucleus:</text>
  <text x="545" y="114" fill="#94A3B8" font-size="10">Genetic Control (DNA)</text>

  <circle cx="475" cy="138" r="6" fill="#F59E0B" />
  <text x="490" y="142" fill="#E2E8F0" font-size="11" font-weight="700">Mitochondria:</text>
  <text x="568" y="142" fill="#94A3B8" font-size="10">ATP Energy Powerhouse</text>

  <circle cx="475" cy="166" r="6" fill="#10B981" />
  <text x="490" y="170" fill="#E2E8F0" font-size="11" font-weight="700">Chloroplast:</text>
  <text x="558" y="170" fill="#94A3B8" font-size="10">Photosynthesis (Plants)</text>

  <circle cx="475" cy="194" r="6" fill="#38BDF8" />
  <text x="490" y="198" fill="#E2E8F0" font-size="11" font-weight="700">Cell Wall & Vacuole:</text>
  <text x="590" y="198" fill="#94A3B8" font-size="10">Turgor Pressure</text>
</svg>"""


def generate_water_cycle_svg() -> str:
    """Generates an Earth science diagram illustrating the Water Cycle."""
    return """<svg viewBox="0 0 720 260" xmlns="http://www.w3.org/2000/svg" className="w-full h-auto max-w-full" style="background: linear-gradient(135deg, #0A192F 0%, #0F2847 100%); border-radius: 16px; font-family: ui-sans-serif, system-ui, sans-serif;">
  <text x="25" y="32" fill="#00E5FF" font-size="14" font-weight="800">HYDROLOGICAL CYCLE: CONTINUOUS GLOBAL WATER CIRCULATION</text>
  <text x="695" y="32" fill="#94A3B8" font-size="12" font-weight="600" text-anchor="end">Solar energy and gravity drive the endless cycle</text>

  <!-- Sun -->
  <circle cx="80" cy="80" r="26" fill="#F59E0B" />
  <text x="80" y="125" fill="#FDE68A" font-size="10" font-weight="800" text-anchor="middle">Solar Energy</text>

  <!-- Ocean Reservoir (Left) -->
  <rect x="40" y="180" width="220" height="60" rx="8" fill="#0284C7" fill-opacity="0.8" stroke="#38BDF8" stroke-width="2" />
  <text x="150" y="215" fill="#FFFFFF" font-size="12" font-weight="800" text-anchor="middle">Ocean Reservoir</text>

  <!-- Evaporation Arrows Up -->
  <path d="M 120,170 Q 125,140 135,115" fill="none" stroke="#00E5FF" stroke-width="3" stroke-dasharray="4 2" />
  <path d="M 160,170 Q 165,140 175,115" fill="none" stroke="#00E5FF" stroke-width="3" stroke-dasharray="4 2" />
  <rect x="95" y="130" width="90" height="20" rx="4" fill="#0F2847" stroke="#00E5FF" stroke-width="1" />
  <text x="140" y="144" fill="#00E5FF" font-size="10" font-weight="800" text-anchor="middle">1. Evaporation ↑</text>

  <!-- Clouds (Condensation) -->
  <ellipse cx="320" cy="85" rx="45" ry="22" fill="#CBD5E1" />
  <ellipse cx="355" cy="80" rx="35" ry="26" fill="#E2E8F0" />
  <ellipse cx="290" cy="90" rx="30" ry="18" fill="#94A3B8" />
  <rect x="270" y="120" width="110" height="20" rx="4" fill="#0F2847" stroke="#94A3B8" stroke-width="1" />
  <text x="325" y="134" fill="#E2E8F0" font-size="10" font-weight="800" text-anchor="middle">2. Condensation →</text>

  <!-- Mountain Landmass (Right) -->
  <polygon points="450,240 550,130 650,240" fill="#334155" stroke="#64748B" stroke-width="2" />
  <polygon points="520,165 550,130 580,165" fill="#E2E8F0" />
  <text x="550" y="195" fill="#E2E8F0" font-size="11" font-weight="800" text-anchor="middle">High Mountains</text>

  <!-- Precipitation Arrows Down -->
  <line x1="430" y1="110" x2="430" y2="155" stroke="#38BDF8" stroke-width="2.5" stroke-dasharray="3 3" />
  <line x1="450" y1="110" x2="450" y2="155" stroke="#38BDF8" stroke-width="2.5" stroke-dasharray="3 3" />
  <rect x="390" y="160" width="95" height="20" rx="4" fill="#0F2847" stroke="#38BDF8" stroke-width="1" />
  <text x="437" y="174" fill="#38BDF8" font-size="10" font-weight="800" text-anchor="middle">3. Precipitation ↓</text>

  <!-- Surface Runoff Back to Ocean -->
  <path d="M 480,220 Q 350,235 260,215" fill="none" stroke="#10B981" stroke-width="3.5" />
  <rect x="290" y="210" width="120" height="22" rx="4" fill="#064E3B" stroke="#10B981" stroke-width="1" />
  <text x="350" y="225" fill="#A7F3D0" font-size="10" font-weight="800" text-anchor="middle">4. Surface Runoff ←</text>
</svg>"""


def generate_human_heart_circulation_svg() -> str:
    """Generates a human heart anatomy diagram showing oxygenated and deoxygenated circulation."""
    return """<svg viewBox="0 0 720 260" xmlns="http://www.w3.org/2000/svg" className="w-full h-auto max-w-full" style="background: linear-gradient(135deg, #0A192F 0%, #0F2847 100%); border-radius: 16px; font-family: ui-sans-serif, system-ui, sans-serif;">
  <text x="25" y="32" fill="#00E5FF" font-size="14" font-weight="800">HUMAN CIRCULATORY SYSTEM: 4-CHAMBERED DOUBLE CIRCULATION</text>
  <text x="695" y="32" fill="#94A3B8" font-size="12" font-weight="600" text-anchor="end">Blue: Deoxygenated (Lungs) • Red: Oxygenated (Body Tissues)</text>

  <!-- Right Heart (Deoxygenated - Left side of drawing) -->
  <rect x="180" y="65" width="120" height="75" rx="16" fill="#0284C7" fill-opacity="0.4" stroke="#38BDF8" stroke-width="2.5" />
  <text x="240" y="95" fill="#38BDF8" font-size="12" font-weight="800" text-anchor="middle">Right Atrium</text>
  <text x="240" y="115" fill="#94A3B8" font-size="10" text-anchor="middle">(From Vena Cava)</text>

  <rect x="180" y="150" width="120" height="85" rx="16" fill="#0369A1" fill-opacity="0.5" stroke="#38BDF8" stroke-width="2.5" />
  <text x="240" y="185" fill="#38BDF8" font-size="12" font-weight="800" text-anchor="middle">Right Ventricle</text>
  <text x="240" y="205" fill="#BAE6FD" font-size="10" text-anchor="middle">(Pumps to Lungs)</text>

  <!-- Central Septum Dividing Wall -->
  <line x1="310" y1="65" x2="310" y2="235" stroke="#E2E8F0" stroke-width="4" stroke-dasharray="6 3" />
  <text x="310" y="152" fill="#E2E8F0" font-size="10" font-weight="800" text-anchor="middle" transform="rotate(-90 310 152)">SEPTUM</text>

  <!-- Left Heart (Oxygenated - Right side of drawing) -->
  <rect x="320" y="65" width="120" height="75" rx="16" fill="#BE123C" fill-opacity="0.4" stroke="#FB7185" stroke-width="2.5" />
  <text x="380" y="95" fill="#FDA4AF" font-size="12" font-weight="800" text-anchor="middle">Left Atrium</text>
  <text x="380" y="115" fill="#FEE2E2" font-size="10" text-anchor="middle">(From Pulm. Veins)</text>

  <rect x="320" y="150" width="120" height="85" rx="16" fill="#9F1239" fill-opacity="0.5" stroke="#FB7185" stroke-width="2.5" />
  <text x="380" y="185" fill="#FDA4AF" font-size="12" font-weight="800" text-anchor="middle">Left Ventricle</text>
  <text x="380" y="205" fill="#FFE4E6" font-size="10" text-anchor="middle">(Thick Wall • To Aorta)</text>

  <!-- Lungs Box (Top Right) -->
  <rect x="470" y="65" width="210" height="75" rx="12" fill="#1E293B" stroke="#00E5FF" stroke-width="1.5" />
  <text x="485" y="90" fill="#00E5FF" font-size="12" font-weight="800">1. Pulmonary Circuit</text>
  <text x="485" y="110" fill="#E2E8F0" font-size="10">CO₂ exchanged for O₂ in alveoli.</text>
  <text x="485" y="126" fill="#94A3B8" font-size="10">High-efficiency gas diffusion.</text>

  <!-- Systemic Body Box (Bottom Right) -->
  <rect x="470" y="155" width="210" height="80" rx="12" fill="#1E293B" stroke="#F43F5E" stroke-width="1.5" />
  <text x="485" y="180" fill="#F43F5E" font-size="12" font-weight="800">2. Systemic Circuit</text>
  <text x="485" y="200" fill="#E2E8F0" font-size="10">Aorta branches to brain, muscles & organs.</text>
  <text x="485" y="218" fill="#94A3B8" font-size="10">Nutrient and oxygen delivery.</text>
</svg>"""


def generate_solar_system_svg() -> str:
    """Generates an astronomical diagram of the Solar System and planetary orbits."""
    return """<svg viewBox="0 0 720 260" xmlns="http://www.w3.org/2000/svg" className="w-full h-auto max-w-full" style="background: linear-gradient(135deg, #0A192F 0%, #0F2847 100%); border-radius: 16px; font-family: ui-sans-serif, system-ui, sans-serif;">
  <text x="25" y="32" fill="#00E5FF" font-size="14" font-weight="800">SOLAR SYSTEM: HELIOCENTRIC PLANETARY ORBITS & SCALE</text>
  <text x="695" y="32" fill="#94A3B8" font-size="12" font-weight="600" text-anchor="end">Gravitational equilibrium keeps planets in elliptical orbits</text>

  <!-- Sun -->
  <circle cx="50" cy="140" r="38" fill="#F59E0B" />
  <circle cx="50" cy="140" r="44" fill="#FDE68A" fill-opacity="0.2" />
  <text x="50" y="145" fill="#0A192F" font-size="12" font-weight="900" text-anchor="middle">SUN</text>

  <!-- Orbit Arcs & Planets -->
  <!-- Mercury -->
  <circle cx="120" cy="140" r="5" fill="#94A3B8" />
  <text x="120" y="165" fill="#94A3B8" font-size="9" font-weight="700" text-anchor="middle">Mercury</text>

  <!-- Venus -->
  <circle cx="165" cy="140" r="8" fill="#FBBF24" />
  <text x="165" y="165" fill="#FDE68A" font-size="9" font-weight="700" text-anchor="middle">Venus</text>

  <!-- Earth & Moon -->
  <circle cx="220" cy="140" r="9" fill="#0284C7" stroke="#38BDF8" stroke-width="1.5" />
  <circle cx="232" cy="132" r="2.5" fill="#E2E8F0" />
  <text x="220" y="165" fill="#38BDF8" font-size="10" font-weight="800" text-anchor="middle">Earth</text>

  <!-- Mars -->
  <circle cx="280" cy="140" r="7" fill="#DC2626" />
  <text x="280" y="165" fill="#F87171" font-size="9" font-weight="700" text-anchor="middle">Mars</text>

  <!-- Asteroid Belt -->
  <line x1="320" y1="70" x2="320" y2="210" stroke="#64748B" stroke-width="2" stroke-dasharray="2 4" />
  <text x="320" y="60" fill="#64748B" font-size="9" font-weight="700" text-anchor="middle">Asteroid Belt</text>

  <!-- Jupiter -->
  <circle cx="380" cy="140" r="22" fill="#D97706" stroke="#FDE68A" stroke-width="1.5" />
  <line x1="360" y1="135" x2="400" y2="135" stroke="#FDE68A" stroke-width="1.5" />
  <text x="380" y="180" fill="#FBBF24" font-size="10" font-weight="800" text-anchor="middle">Jupiter</text>

  <!-- Saturn & Ring -->
  <circle cx="465" cy="140" r="17" fill="#CA8A04" />
  <ellipse cx="465" cy="140" rx="30" ry="8" fill="none" stroke="#FEF08A" stroke-width="2.5" />
  <text x="465" y="180" fill="#FEF08A" font-size="10" font-weight="800" text-anchor="middle">Saturn</text>

  <!-- Uranus -->
  <circle cx="545" cy="140" r="12" fill="#06B6D4" />
  <text x="545" y="170" fill="#67E8F9" font-size="9" font-weight="700" text-anchor="middle">Uranus</text>

  <!-- Neptune -->
  <circle cx="615" cy="140" r="11" fill="#2563EB" />
  <text x="615" y="170" fill="#93C5FD" font-size="9" font-weight="700" text-anchor="middle">Neptune</text>

  <!-- Orbit Distance Timeline Line -->
  <line x1="90" y1="215" x2="650" y2="215" stroke="#334155" stroke-width="2" />
  <text x="370" y="235" fill="#94A3B8" font-size="11" font-weight="600" text-anchor="middle">Inner Terrestrial Planets (Dense Rock) ⟵ ⟶ Outer Gas Giants (Hydrogen & Helium)</text>
</svg>"""


def generate_indus_valley_svg() -> str:
    """Generates an archaeological schematic of Indus Valley urban town planning."""
    return """<svg viewBox="0 0 720 260" xmlns="http://www.w3.org/2000/svg" className="w-full h-auto max-w-full" style="background: linear-gradient(135deg, #0A192F 0%, #0F2847 100%); border-radius: 16px; font-family: ui-sans-serif, system-ui, sans-serif;">
  <text x="25" y="32" fill="#00E5FF" font-size="14" font-weight="800">INDUS VALLEY CIVILIZATION: URBAN PLANNING & THE GREAT BATH</text>
  <text x="695" y="32" fill="#94A3B8" font-size="12" font-weight="600" text-anchor="end">Baked bricks • Grid street plan • Covered municipal drainage</text>

  <!-- Western Citadel (Raised Mound) -->
  <rect x="50" y="65" width="260" height="175" rx="14" fill="#1E293B" stroke="#D97706" stroke-width="2.5" />
  <text x="180" y="90" fill="#FBBF24" font-size="12" font-weight="800" text-anchor="middle">WESTERN CITADEL (MOUND)</text>

  <!-- The Great Bath Tank -->
  <rect x="80" y="105" width="200" height="110" rx="6" fill="#0284C7" fill-opacity="0.6" stroke="#38BDF8" stroke-width="2" />
  <text x="180" y="150" fill="#FFFFFF" font-size="12" font-weight="800" text-anchor="middle">The Great Bath</text>
  <text x="180" y="170" fill="#BAE6FD" font-size="10" font-weight="600" text-anchor="middle">Waterproofed with Bitumen/Tar</text>

  <!-- Flight of Steps -->
  <rect x="90" y="110" width="20" height="10" fill="#D97706" />
  <rect x="90" y="195" width="20" height="10" fill="#D97706" />
  <text x="115" y="120" fill="#FDE68A" font-size="9">North Steps</text>
  <text x="115" y="203" fill="#FDE68A" font-size="9">South Steps</text>

  <!-- Lower Town Grid Streets (East) -->
  <rect x="330" y="65" width="350" height="175" rx="14" fill="#1E293B" stroke="#10B981" stroke-width="2" />
  <text x="505" y="90" fill="#34D399" font-size="12" font-weight="800" text-anchor="middle">LOWER TOWN: RIGHT-ANGLE GRID PLAN</text>

  <!-- Grid streets & Blocks -->
  <line x1="430" y1="105" x2="430" y2="225" stroke="#00E5FF" stroke-width="3" />
  <line x1="530" y1="105" x2="530" y2="225" stroke="#00E5FF" stroke-width="3" />
  <line x1="350" y1="165" x2="660" y2="165" stroke="#00E5FF" stroke-width="3" />

  <rect x="355" y="110" width="65" height="45" rx="4" fill="#334155" />
  <text x="387" y="137" fill="#E2E8F0" font-size="9" font-weight="700" text-anchor="middle">Houses</text>

  <rect x="440" y="110" width="80" height="45" rx="4" fill="#334155" />
  <text x="480" y="137" fill="#E2E8F0" font-size="9" font-weight="700" text-anchor="middle">Granary</text>

  <rect x="540" y="110" width="110" height="45" rx="4" fill="#334155" />
  <text x="595" y="137" fill="#E2E8F0" font-size="9" font-weight="700" text-anchor="middle">Covered Drains</text>

  <rect x="355" y="175" width="295" height="45" rx="6" fill="#0F172A" stroke="#34D399" stroke-width="1" />
  <text x="502" y="202" fill="#A7F3D0" font-size="10" font-weight="800" text-anchor="middle">Standardized 1:2:4 Brick Ratio & Municipal Sanitation</text>
</svg>"""


def generate_python_loop_svg() -> str:
    """Generates a computer science control flow diagram for iteration and loops."""
    return """<svg viewBox="0 0 720 260" xmlns="http://www.w3.org/2000/svg" className="w-full h-auto max-w-full" style="background: linear-gradient(135deg, #0A192F 0%, #0F2847 100%); border-radius: 16px; font-family: ui-sans-serif, system-ui, sans-serif;">
  <text x="25" y="32" fill="#00E5FF" font-size="14" font-weight="800">PYTHON CONTROL FLOW: LOOP ITERATION & ACCUMULATION</text>
  <text x="695" y="32" fill="#94A3B8" font-size="12" font-weight="600" text-anchor="end">Deterministic step execution with condition verification</text>

  <!-- Step 1: Initialization -->
  <rect x="40" y="90" width="130" height="65" rx="10" fill="#1E293B" stroke="#38BDF8" stroke-width="2" />
  <text x="105" y="115" fill="#38BDF8" font-size="11" font-weight="800" text-anchor="middle">1. Initialize</text>
  <text x="105" y="135" fill="#E2E8F0" font-size="11" font-mono font-weight="600" text-anchor="middle">total = 0, i = 1</text>

  <!-- Arrow to Condition -->
  <line x1="170" y1="122" x2="220" y2="122" stroke="#00E5FF" stroke-width="3" />
  <polygon points="220,122 210,116 210,128" fill="#00E5FF" />

  <!-- Step 2: Decision Diamond -->
  <polygon points="300,75 370,122 300,170 230,122" fill="#1E293B" stroke="#F59E0B" stroke-width="2" />
  <text x="300" y="118" fill="#FDE68A" font-size="11" font-weight="800" text-anchor="middle">2. Condition?</text>
  <text x="300" y="135" fill="#FFFFFF" font-size="11" font-mono font-weight="700" text-anchor="middle">i &lt;= n</text>

  <!-- True Branch (Right to Loop Body) -->
  <line x1="370" y1="122" x2="430" y2="122" stroke="#10B981" stroke-width="3" />
  <polygon points="430,122 420,116 420,128" fill="#10B981" />
  <text x="395" y="115" fill="#34D399" font-size="10" font-weight="800">TRUE</text>

  <!-- Step 3: Loop Body Execution -->
  <rect x="430" y="85" width="160" height="75" rx="10" fill="#1E293B" stroke="#10B981" stroke-width="2" />
  <text x="510" y="110" fill="#34D399" font-size="11" font-weight="800" text-anchor="middle">3. Loop Body</text>
  <text x="510" y="130" fill="#E2E8F0" font-size="10" font-mono text-anchor="middle">total += i</text>
  <text x="510" y="148" fill="#FBBF24" font-size="10" font-mono text-anchor="middle">i += 1 (Step)</text>

  <!-- Loopback Arc -->
  <path d="M 510,85 Q 510,45 300,45 Q 300,55 300,75" fill="none" stroke="#34D399" stroke-width="2.5" stroke-dasharray="4 2" />
  <text x="400" y="40" fill="#34D399" font-size="10" font-weight="700" text-anchor="middle">Iterate Next Element ⟲</text>

  <!-- False Branch (Down to Exit) -->
  <line x1="300" y1="170" x2="300" y2="210" stroke="#F43F5E" stroke-width="3" />
  <polygon points="300,210 294,200 306,200" fill="#F43F5E" />
  <text x="310" y="195" fill="#FB7185" font-size="10" font-weight="800">FALSE</text>

  <!-- Exit Box -->
  <rect x="220" y="210" width="160" height="38" rx="8" fill="#0F172A" stroke="#F43F5E" stroke-width="2" />
  <text x="300" y="234" fill="#FFFFFF" font-size="11" font-weight="800" text-anchor="middle">Exit: return total ✓</text>
</svg>"""


def generate_general_concept_flow_svg(subject: str, topic: str, question: str) -> str:
    """Generates a universal conceptual architecture and step flow diagram."""
    clean_sub = html.escape(subject[:24] if subject else "Core Knowledge")
    clean_top = html.escape(topic[:30] if topic else "Key Concept")
    clean_q = html.escape(question[:40] if question else "Problem Formulation")
    
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 240" width="100%" height="auto">
  <defs>
    <linearGradient id="bg_concept" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0A192F" />
      <stop offset="100%" stop-color="#0F2442" />
    </linearGradient>
    <linearGradient id="cyan_grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00E5FF" />
      <stop offset="100%" stop-color="#3B82F6" />
    </linearGradient>
  </defs>
  <rect width="640" height="240" fill="url(#bg_concept)" rx="14" stroke="#1E3A8A" stroke-width="2" />

  <!-- Header -->
  <text x="320" y="28" fill="#00E5FF" font-size="13" font-weight="800" text-anchor="middle" letter-spacing="1">
    SPARKMINDS CONCEPT ARCHITECTURE • {clean_sub.upper()}
  </text>
  <text x="320" y="46" fill="#94A3B8" font-size="10" font-weight="600" text-anchor="middle">
    Topic: {clean_top}
  </text>

  <!-- Node 1: Input / Inquiry -->
  <rect x="25" y="75" width="160" height="95" rx="10" fill="#0F172A" stroke="#38BDF8" stroke-width="2" />
  <circle cx="45" cy="95" r="10" fill="#0284C7" />
  <text x="45" y="99" fill="#FFFFFF" font-size="10" font-weight="800" text-anchor="middle">1</text>
  <text x="65" y="98" fill="#38BDF8" font-size="11" font-weight="800">Observation</text>
  <text x="35" y="122" fill="#E2E8F0" font-size="9" font-weight="600">Question Context:</text>
  <text x="35" y="138" fill="#94A3B8" font-size="9">{clean_q}...</text>
  <text x="35" y="154" fill="#38BDF8" font-size="8" font-weight="700">Identify Given Variables</text>

  <!-- Arrow 1 -> 2 -->
  <line x1="185" y1="122" x2="235" y2="122" stroke="#00E5FF" stroke-width="2.5" />
  <polygon points="235,122 225,116 225,128" fill="#00E5FF" />

  <!-- Node 2: Core Principle / Formula -->
  <rect x="235" y="75" width="170" height="95" rx="10" fill="#1E293B" stroke="#10B981" stroke-width="2" />
  <circle cx="255" cy="95" r="10" fill="#059669" />
  <text x="255" y="99" fill="#FFFFFF" font-size="10" font-weight="800" text-anchor="middle">2</text>
  <text x="275" y="98" fill="#34D399" font-size="11" font-weight="800">Core Principle</text>
  <text x="245" y="122" fill="#E2E8F0" font-size="9" font-weight="600">Apply Academic Rule:</text>
  <text x="245" y="138" fill="#FDE047" font-size="9" font-weight="700">Prerequisite Law/Theorem</text>
  <text x="245" y="154" fill="#34D399" font-size="8" font-weight="700">Step-by-step Socratic Flow</text>

  <!-- Arrow 2 -> 3 -->
  <line x1="405" y1="122" x2="455" y2="122" stroke="#10B981" stroke-width="2.5" />
  <polygon points="455,122 445,116 445,128" fill="#10B981" />

  <!-- Node 3: Synthesis & Verification -->
  <rect x="455" y="75" width="160" height="95" rx="10" fill="#0F172A" stroke="#F59E0B" stroke-width="2" />
  <circle cx="475" cy="95" r="10" fill="#D97706" />
  <text x="475" y="99" fill="#FFFFFF" font-size="10" font-weight="800" text-anchor="middle">3</text>
  <text x="495" y="98" fill="#FBBF24" font-size="11" font-weight="800">Verification</text>
  <text x="465" y="122" fill="#E2E8F0" font-size="9" font-weight="600">Conceptual Proof:</text>
  <text x="465" y="138" fill="#A7F3D0" font-size="9" font-weight="700">Consistent Solution ✓</text>
  <text x="465" y="154" fill="#FBBF24" font-size="8" font-weight="700">Interactive Practice Ready</text>

  <!-- Bottom Guidance Footer -->
  <rect x="30" y="190" width="580" height="34" rx="8" fill="#061020" stroke="#1E293B" stroke-width="1" />
  <text x="320" y="211" fill="#38BDF8" font-size="10" font-weight="700" text-anchor="middle">
    💡 SparkMinds Socratic Loop: Connects prerequisite memory to verified problem mastery.
  </text>
</svg>"""


def get_visual_diagram(
    detected_subject: str,
    detected_topic: str,
    question: str,
    math_plan: Optional[Dict[str, Any]] = None,
) -> Tuple[str, str, str]:
    """
    Returns (svg_markup, caption, concept_type) tailored specifically to the problem.
    """
    q_low = question.lower()
    subj_low = detected_subject.lower()

    # 1. Math Plan specific diagrams
    if math_plan:
        ptype = math_plan.get("problem_type")
        if ptype == "FRACTION_ADD_SUB":
            n1, d1, op, n2, d2 = math_plan["operands"]
            svg = generate_fraction_svg(
                n1, d1, op, n2, d2,
                math_plan["lcm_val"],
                math_plan["eq_n1"],
                math_plan["eq_n2"],
                math_plan["final_answer"],
            )
            caption = f"Fraction Bar Model: Dividing both fractions into {math_plan['lcm_val']} equal slices allows direct combining."
            return svg, caption, "FRACTION_BAR_MODEL"
        elif ptype == "LINEAR_EQUATION":
            a, var_name, op, b, c = math_plan["operands"]
            svg = generate_linear_equation_svg(a, var_name, op, b, c, math_plan["final_answer"])
            caption = f"Algebra Balance Scale: Preserving equality while isolating the unknown {var_name}."
            return svg, caption, "BALANCE_SCALE_MODEL"
        elif ptype == "HCF":
            a, b = math_plan["operands"]
            fac_a = [x for x in range(1, a + 1) if a % x == 0]
            fac_b = [x for x in range(1, b + 1) if b % x == 0]
            common = [x for x in fac_a if x in fac_b]
            svg = generate_hcf_svg(a, b, int(math_plan["final_answer"]), fac_a, fac_b, common)
            caption = f"Factor Venn Diagram: Highlighting all divisors and the Highest Common Factor of {a} and {b}."
            return svg, caption, "FACTOR_VENN_DIAGRAM"
        elif ptype == "LCM":
            a, b = math_plan["operands"]
            svg = generate_lcm_svg(a, b, int(math_plan["final_answer"]))
            caption = f"Timeline Jump Diagram: Visualizing the first common landing point of {a} and {b}."
            return svg, caption, "LCM_TIMELINE_MODEL"

    # 2. Photosynthesis / Plant Science
    if "photosynthesis" in q_low or "chlorophyll" in q_low or "leaf" in q_low:
        svg = generate_photosynthesis_svg()
        caption = "Botanical System Diagram: Solar photons driving Glucose synthesis and Oxygen gas release."
        return svg, caption, "PHOTOSYNTHESIS_SYSTEM"

    # 3. Cell Biology / Organelles
    if "cell" in q_low or "mitochondria" in q_low or "nucleus" in q_low or "organelle" in q_low:
        svg = generate_cell_structure_svg()
        caption = "Cytological Diagram: Cell wall, nucleus, mitochondria powerhouses, and chloroplasts."
        return svg, caption, "CELL_STRUCTURE_ORGANELLES"

    # 4. Water Cycle / Hydrology
    if "water cycle" in q_low or "evaporation" in q_low or "precipitation" in q_low or "condensation" in q_low:
        svg = generate_water_cycle_svg()
        caption = "Hydrological Cycle Model: Solar-driven Evaporation, Condensation, Precipitation, and Runoff."
        return svg, caption, "WATER_CYCLE_SYSTEM"

    # 5. Heart & Blood Circulation
    if "heart" in q_low or "circulat" in q_low or "blood" in q_low or "ventricle" in q_low or "atrium" in q_low:
        svg = generate_human_heart_circulation_svg()
        caption = "Cardiovascular Flow Model: 4-chambered heart driving pulmonary and systemic circulation."
        return svg, caption, "HEART_CIRCULATION_SYSTEM"

    # 6. Solar System & Planets
    if "solar system" in q_low or "planet" in q_low or "orbit" in q_low or "jupiter" in q_low or "mars" in q_low:
        svg = generate_solar_system_svg()
        caption = "Astronomical Scale Model: Heliocentric planetary orbits and asteroid belt structure."
        return svg, caption, "SOLAR_SYSTEM_ORBITS"

    # 7. Indus Valley Civilization
    if "indus" in q_low or "harappa" in q_low or "mohenjo" in q_low or "urban planning" in q_low:
        svg = generate_indus_valley_svg()
        caption = "Archaeological Citadel Schematic: Western Great Bath and Eastern grid-pattern town planning."
        return svg, caption, "INDUS_VALLEY_PLANNING"

    # 8. Python & Programming Loops
    if "python" in q_low or "loop" in q_low or "for loop" in q_low or "iteration" in q_low:
        svg = generate_python_loop_svg()
        caption = "Algorithmic Control Flow: Sequential loop initialization, condition evaluation, and termination."
        return svg, caption, "PYTHON_LOOP_FLOW"

    # 9. Geometry / Pythagorean Theorem
    if "pythagor" in q_low or "hypotenuse" in q_low or "right triangle" in q_low or "right-angled" in q_low:
        svg = generate_pythagorean_svg()
        caption = "Pythagorean Geometric Proof: The sum of the areas of squares on legs a and b equals the square on hypotenuse c."
        return svg, caption, "PYTHAGOREAN_GEOMETRY"

    # 10. Universal Concept Flowchart
    svg = generate_general_concept_flow_svg(detected_subject, detected_topic, question)
    caption = f"Interactive Conceptual Architecture: Breakdown of {detected_subject} principles and structured logic."
    return svg, caption, "CONCEPT_ARCHITECTURE_FLOW"


def get_curated_video_explanation(
    detected_subject: str,
    detected_topic: str,
    question: str,
    grade: int,
    math_plan: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Returns curated, curriculum-aligned educational video module with title, platform badge,
    duration, youtube_embed_id, search_query, and key takeaways.
    """
    q_low = question.lower()
    subj_low = detected_subject.lower()

    # 1. Fraction Addition / Subtraction
    if (math_plan and math_plan.get("problem_type") == "FRACTION_ADD_SUB") or "fraction" in q_low:
        return {
            "title": "Khan Academy & NCERT: Adding and Subtracting Fractions with Unlike Denominators",
            "platform": "Khan Academy",
            "duration": "5:23 mins",
            "youtube_embed_id": "BC04Y_v2eoc",
            "search_query": "adding fractions unlike denominators khan academy",
            "recommended_timestamp": "01:10",
            "key_takeaways": [
                "Why denominator slice sizes must be identical before combining numerators.",
                "How to find the Least Common Multiple (LCM) of denominators quickly.",
                "Converting to equivalent fractions and simplifying the final sum.",
            ],
        }

    # 2. Linear Equations / Algebra
    if (math_plan and math_plan.get("problem_type") == "LINEAR_EQUATION") or "linear equation" in q_low or "solve for x" in q_low:
        return {
            "title": "Khan Academy & NCERT: Solving Two-Step Linear Equations Step by Step",
            "platform": "Khan Academy",
            "duration": "4:50 mins",
            "youtube_embed_id": "LDIiYKYvvdA",
            "search_query": "solving two step equations khan academy",
            "recommended_timestamp": "00:45",
            "key_takeaways": [
                "Treating an equation like a balanced scale where both sides stay equal.",
                "Using inverse operations (transposition) to undo addition and subtraction.",
                "Dividing by the coefficient to isolate the unknown variable.",
            ],
        }

    # 3. HCF / GCD
    if (math_plan and math_plan.get("problem_type") == "HCF") or "hcf" in q_low or "gcd" in q_low:
        return {
            "title": "Math Antics & NCERT: Greatest Common Factor (HCF) Explained",
            "platform": "Math Antics",
            "duration": "5:45 mins",
            "youtube_embed_id": "3W8SeYgZcMo",
            "search_query": "greatest common factor math antics",
            "recommended_timestamp": "01:05",
            "key_takeaways": [
                "Listing exact divisors and prime factors of each number.",
                "Finding the shared intersection of common factors.",
                "Choosing the highest factor to solve equal grouping problems.",
            ],
        }

    # 4. LCM
    if (math_plan and math_plan.get("problem_type") == "LCM") or "lcm" in q_low or "least common multiple" in q_low:
        return {
            "title": "Math Antics & NCERT: Least Common Multiple (LCM) Made Easy",
            "platform": "Math Antics",
            "duration": "5:10 mins",
            "youtube_embed_id": "znmPfDfsir8",
            "search_query": "least common multiple math antics",
            "recommended_timestamp": "00:50",
            "key_takeaways": [
                "Listing multiples of each number systematically.",
                "Spotting the smallest number shared across both lists.",
                "Applying LCM to clock cycles and common denominator math.",
            ],
        }

    # 5. Photosynthesis / Plant Biology
    if "photosynthesis" in q_low or "chlorophyll" in q_low or "leaf" in q_low:
        return {
            "title": "CrashCourse & NCERT: Photosynthesis and Cellular Respiration",
            "platform": "CrashCourse",
            "duration": "6:15 mins",
            "youtube_embed_id": "sQK3Yr4Sc_k",
            "search_query": "photosynthesis crash course biology",
            "recommended_timestamp": "00:40",
            "key_takeaways": [
                "How chlorophyll in chloroplast thylakoids absorbs solar photons.",
                "Splitting water (H₂O) and fixing carbon dioxide (CO₂) into glucose.",
                "The vital role of oxygen gas release in sustaining life on Earth.",
            ],
        }

    # 6. Pythagorean Theorem / Right Triangles
    if "pythagor" in q_low or "hypotenuse" in q_low or "right triangle" in q_low:
        return {
            "title": "3Blue1Brown & Khan Academy: The Pythagorean Theorem Visual Proof",
            "platform": "3Blue1Brown",
            "duration": "6:30 mins",
            "youtube_embed_id": "AA6RfgP-AHU",
            "search_query": "pythagorean theorem visual proof 3blue1brown",
            "recommended_timestamp": "01:15",
            "key_takeaways": [
                "Identifying the hypotenuse directly opposite the 90° right angle.",
                "Understanding the area relationship a² + b² = c² geometrically.",
                "Calculating unknown distances and diagonals in real-world scenarios.",
            ],
        }

    # 7. Indus Valley Civilization / History
    if "indus" in q_low or "harappa" in q_low or "mohenjo" in q_low:
        return {
            "title": "CrashCourse World History: The Indus Valley Civilization",
            "platform": "CrashCourse",
            "duration": "9:35 mins",
            "youtube_embed_id": "n7ndRwqJYDM",
            "search_query": "indus valley civilization crash course",
            "recommended_timestamp": "01:30",
            "key_takeaways": [
                "Mastery of grid-pattern urban planning and standardized baked bricks.",
                "Pioneering public health with covered drainage systems and the Great Bath.",
                "Extensive bronze age trade networks connecting Mesopotamia and India.",
            ],
        }

    # 8. Water Cycle / Earth Science
    if "water cycle" in q_low or "evaporation" in q_low or "precipitation" in q_low or "condensation" in q_low:
        return {
            "title": "CrashCourse Kids & NCERT: The Water Cycle Explained",
            "platform": "CrashCourse Kids",
            "duration": "4:40 mins",
            "youtube_embed_id": "al-do-HGuIk",
            "search_query": "water cycle crash course kids",
            "recommended_timestamp": "00:35",
            "key_takeaways": [
                "Evaporation driven by solar heat transforming liquid into vapor.",
                "Cloud condensation as water vapor cools at high altitudes.",
                "Precipitation (rain/snow) returning moisture to land and oceans.",
            ],
        }

    # 9. Human Heart & Circulation
    if "heart" in q_low or "circulat" in q_low or "blood" in q_low:
        return {
            "title": "Amoeba Sisters & NCERT: Circulatory System and the Heart",
            "platform": "Amoeba Sisters",
            "duration": "7:50 mins",
            "youtube_embed_id": "q0s-1MC1hcE",
            "search_query": "circulatory system amoeba sisters",
            "recommended_timestamp": "01:20",
            "key_takeaways": [
                "Path of blood through atria and ventricles.",
                "Pulmonary circulation for oxygenation vs systemic circulation for tissue delivery.",
                "Role of heart valves in maintaining unidirectional blood flow.",
            ],
        }

    # 10. Solar System & Planets
    if "solar system" in q_low or "planet" in q_low or "orbit" in q_low:
        return {
            "title": "National Geographic & NCERT: Solar System 101",
            "platform": "National Geographic",
            "duration": "4:10 mins",
            "youtube_embed_id": "libKTYPPR-w",
            "search_query": "solar system 101 national geographic",
            "recommended_timestamp": "00:45",
            "key_takeaways": [
                "The 8 planets and their division into rocky terrestrial and gas giants.",
                "Gravitational equilibrium and elliptical planetary orbital paths.",
                "Scale and astronomical distances across the solar neighborhood.",
            ],
        }

    # 11. Python & Computer Science
    if "python" in q_low or "code" in q_low or "loop" in q_low or "programming" in q_low:
        return {
            "title": "Programming with Mosh: Python Fundamentals & Control Flow",
            "platform": "EduSpark Code Studio",
            "duration": "7:20 mins",
            "youtube_embed_id": "_uQrJ0TkZlc",
            "search_query": "python for beginners programming with mosh",
            "recommended_timestamp": "01:00",
            "key_takeaways": [
                "Understanding sequential program execution and variables.",
                "How loops evaluate conditions and iterate through steps.",
                "Debugging logic errors and tracking intermediate variable state.",
            ],
        }

    # 12. General Subject / Fallback
    return {
        "title": f"NCERT & EduSpark Studio: Mastering {detected_topic} (Grade {grade})",
        "platform": "NCERT & EduSpark Studio",
        "duration": "6:45 mins",
        "youtube_embed_id": "BC04Y_v2eoc",
        "search_query": f"{detected_topic} Grade {grade} {detected_subject} explanation",
        "recommended_timestamp": "00:30",
        "key_takeaways": [
            f"Core conceptual definition and principles of {detected_topic}.",
            "Step-by-step problem breakdown aligned with school board curriculum.",
            "Relatable real-world applications and exam problem-solving tips.",
        ],
    }
