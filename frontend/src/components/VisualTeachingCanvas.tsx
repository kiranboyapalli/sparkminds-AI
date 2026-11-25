import React from 'react';
import {
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Eye,
  Lightbulb,
  Play,
  Power,
  Sparkles,
} from 'lucide-react';
import { SparkRobotMascot } from './SparkRobotMascot';

export interface VisualAidLabel {
  id: string;
  label: string;
  description: string;
}

export interface VisualAidCheckQuestion {
  prompt: string;
  options: string[];
  correct_answer: string;
  hint?: string;
  explanation?: string;
}

export interface VisualAidPayload {
  should_display_visual?: boolean;
  visual_type: string;
  subject: string;
  concept: string;
  title: string;
  caption?: string;
  interactive_animated?: boolean;
  labels?: VisualAidLabel[];
  step_by_step_walkthrough?: string[];
  check_question?: VisualAidCheckQuestion;
  fallback_text_explanation?: string;
  dynamic_params?: Record<string, any>;
}

interface VisualTeachingCanvasProps {
  visualAid: VisualAidPayload;
  onAnsweredCheck?: (isCorrect: boolean) => void;
  onAskAnotherWay?: (prompt: string) => void;
}

/**
 * Parts 8 & 9 — Visual AI Teaching Canvas (Pictures, Labelled Diagrams & Lightweight Interactive Animations)
 * Renders curriculum-accurate, interactive SVG diagrams paired with clickable labels,
 * step-by-step walkthrough, quick check question with instant feedback, and text fallback.
 */
export const VisualTeachingCanvas: React.FC<VisualTeachingCanvasProps> = ({
  visualAid,
  onAnsweredCheck,
  onAskAnotherWay,
}) => {
  const [activeLabelId, setActiveLabelId] = React.useState<string | null>(
    visualAid.labels?.[0]?.id || null
  );
  const [showSteps, setShowSteps] = React.useState<boolean>(true);
  const [selectedOption, setSelectedOption] = React.useState<string>('');
  const [checkFeedback, setCheckFeedback] = React.useState<{
    correct: boolean;
    text: string;
  } | null>(null);
  const [showHint, setShowHint] = React.useState<boolean>(false);

  // Interactive controls for animated visuals
  const initNum = Number(visualAid.dynamic_params?.numerator ?? 3);
  const initDen = Math.max(2, Math.min(10, Number(visualAid.dynamic_params?.denominator ?? 4)));
  const [fractionNum, setFractionNum] = React.useState<number>(Math.min(initNum, initDen));
  const [fractionDen, setFractionDen] = React.useState<number>(initDen);
  const [circuitOn, setCircuitOn] = React.useState<boolean>(true);
  const [pushForce, setPushForce] = React.useState<number>(12);

  const activeLabel = (visualAid.labels || []).find((l) => l.id === activeLabelId) || null;

  const handleCheckAnswer = (option: string) => {
    setSelectedOption(option);
    if (!visualAid.check_question) return;
    const isCorrect =
      option.trim().toLowerCase() === visualAid.check_question.correct_answer.trim().toLowerCase();
    setCheckFeedback({
      correct: isCorrect,
      text: isCorrect
        ? visualAid.check_question.explanation || 'Great work! You understood this visual clearly.'
        : visualAid.check_question.hint || 'Almost there — inspect the highlighted label and try again!',
    });
    if (onAnsweredCheck) onAnsweredCheck(isCorrect);
  };

  const renderInteractiveSvg = () => {
    switch (visualAid.visual_type) {
      case 'math_fractions_animated': {
        const pct = Math.round((fractionNum / fractionDen) * 100);
        return (
          <div className="space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
              <span className="font-extrabold text-[#101B35]">
                Fraction: <span className="text-[#5146E5]">{fractionNum}/{fractionDen}</span> ({pct}%)
              </span>
              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  onClick={() => setFractionNum((n) => (n >= fractionDen ? 1 : n + 1))}
                  className="px-2.5 py-1 rounded-lg bg-[#5146E5] hover:bg-[#4338CA] text-white text-[11px] font-extrabold transition"
                >
                  + Shade Slice
                </button>
                <button
                  type="button"
                  onClick={() => {
                    const nextDen = fractionDen >= 8 ? 3 : fractionDen + 1;
                    setFractionDen(nextDen);
                    setFractionNum((n) => Math.min(n, nextDen));
                  }}
                  className="px-2.5 py-1 rounded-lg bg-[#EEEAFE] hover:bg-[#e1d8fd] text-[#5146E5] text-[11px] font-extrabold transition"
                >
                  Change Parts ({fractionDen})
                </button>
              </div>
            </div>
            <svg viewBox="0 0 360 120" className="w-full h-32 rounded-xl bg-[#101B35] p-2">
              <text x="16" y="22" fill="#35D6E8" fontSize="11" fontWeight="700">
                Equal Parts Bar Model ({fractionNum} shaded of {fractionDen})
              </text>
              {Array.from({ length: fractionDen }).map((_, idx) => {
                const gap = 6;
                const totalW = 328;
                const w = (totalW - gap * (fractionDen - 1)) / fractionDen;
                const x = 16 + idx * (w + gap);
                const shaded = idx < fractionNum;
                return (
                  <g key={idx}>
                    <rect
                      x={x}
                      y={34}
                      width={w}
                      height={54}
                      rx={8}
                      fill={shaded ? '#35D6E8' : '#1E2D56'}
                      stroke={shaded ? '#FFFFFF' : '#5146E5'}
                      strokeWidth="1.5"
                    />
                    <text
                      x={x + w / 2}
                      y={65}
                      textAnchor="middle"
                      fill={shaded ? '#101B35' : '#C7D2FE'}
                      fontSize="11"
                      fontWeight="800"
                    >
                      1/{fractionDen}
                    </text>
                  </g>
                );
              })}
              <text x="16" y="108" fill="#C7D2FE" fontSize="10" fontWeight="600">
                Numerator = {fractionNum} shaded slices • Denominator = {fractionDen} equal slices in 1 whole
              </text>
            </svg>
          </div>
        );
      }

      case 'math_number_line': {
        const start = Number(visualAid.dynamic_params?.start ?? -2);
        const delta = Number(visualAid.dynamic_params?.delta ?? 5);
        const end = Math.max(-6, Math.min(6, start + delta));
        const toX = (n: number) => 30 + ((n + 6) / 12) * 300;
        const sx = toX(start);
        const ex = toX(end);
        const midX = (sx + ex) / 2;
        return (
          <svg viewBox="0 0 360 120" className="w-full h-32 rounded-xl bg-[#101B35]">
            <line x1="20" y1="78" x2="340" y2="78" stroke="#94A3B8" strokeWidth="2.5" strokeLinecap="round" />
            {[-6, -4, -2, 0, 2, 4, 6].map((n) => (
              <g key={n}>
                <line x1={toX(n)} y1="72" x2={toX(n)} y2="84" stroke={n === 0 ? '#35D6E8' : '#CBD5E1'} strokeWidth="2" />
                <text x={toX(n)} y="100" textAnchor="middle" fill={n === 0 ? '#35D6E8' : '#E2E8F0'} fontSize="10" fontWeight="700">
                  {n}
                </text>
              </g>
            ))}
            <path
              d={`M ${sx} 72 Q ${midX} 20 ${ex} 72`}
              fill="none"
              stroke="#35D6E8"
              strokeWidth="2.8"
              strokeDasharray="6 4"
              className="animate-dash-flow"
            />
            <circle cx={sx} cy="78" r="6" fill="#5146E5" stroke="#FFFFFF" strokeWidth="2" />
            <circle cx={ex} cy="78" r="6.5" fill="#35D6E8" stroke="#FFFFFF" strokeWidth="2" />
            <text x={midX} y="24" textAnchor="middle" fill="#35D6E8" fontSize="11" fontWeight="800">
              {delta >= 0 ? `+${delta} (Right)` : `${delta} (Left)`}
            </text>
            <text x={sx} y="62" textAnchor="middle" fill="#C7D2FE" fontSize="10" fontWeight="700">
              Start ({start})
            </text>
            <text x={ex} y="62" textAnchor="middle" fill="#FFFFFF" fontSize="10" fontWeight="800">
              End ({end})
            </text>
          </svg>
        );
      }

      case 'math_geometry': {
        const isCircle = visualAid.dynamic_params?.shape === 'circle';
        if (isCircle) {
          return (
            <svg viewBox="0 0 360 150" className="w-full h-40 rounded-xl bg-[#101B35]">
              <circle cx="150" cy="76" r="52" fill="#5146E5" fillOpacity="0.22" stroke="#35D6E8" strokeWidth="3" />
              <line x1="98" y1="76" x2="202" y2="76" stroke="#A5B4FC" strokeWidth="2" strokeDasharray="5 3" />
              <line x1="150" y1="76" x2="188" y2="41" stroke="#35D6E8" strokeWidth="2.8" />
              <circle cx="150" cy="76" r="4.5" fill="#FFFFFF" />
              <text x="150" y="94" textAnchor="middle" fill="#FFFFFF" fontSize="10" fontWeight="700">Centre (O)</text>
              <text x="184" y="54" fill="#35D6E8" fontSize="11" fontWeight="800">Radius (r)</text>
              <text x="120" y="70" fill="#C7D2FE" fontSize="10" fontWeight="700">Diameter (d = 2r)</text>
              <rect x="225" y="34" width="122" height="80" rx="12" fill="#1B2852" stroke="#5146E5" />
              <text x="236" y="56" fill="#35D6E8" fontSize="10" fontWeight="800">Key Formulas</text>
              <text x="236" y="75" fill="#FFFFFF" fontSize="10" fontWeight="600">d = 2 × r</text>
              <text x="236" y="92" fill="#FFFFFF" fontSize="10" fontWeight="600">C = 2πr</text>
              <text x="236" y="108" fill="#FFFFFF" fontSize="10" fontWeight="600">Area = πr²</text>
            </svg>
          );
        }
        return (
          <svg viewBox="0 0 360 150" className="w-full h-40 rounded-xl bg-[#101B35]">
            <polygon points="75,122 225,122 75,30" fill="#5146E5" fillOpacity="0.28" stroke="#35D6E8" strokeWidth="2.8" strokeLinejoin="round" />
            <rect x="75" y="108" width="14" height="14" fill="none" stroke="#FFFFFF" strokeWidth="1.8" />
            <text x="48" y="80" fill="#35D6E8" fontSize="11" fontWeight="800">Height (h)</text>
            <text x="148" y="138" textAnchor="middle" fill="#C7D2FE" fontSize="11" fontWeight="800">Base (b)</text>
            <text x="172" y="68" fill="#FFFFFF" fontSize="11" fontWeight="800">Hypotenuse (c)</text>
            <text x="95" y="118" fill="#35D6E8" fontSize="10" fontWeight="800">90°</text>
            <rect x="242" y="34" width="106" height="82" rx="12" fill="#1B2852" stroke="#5146E5" />
            <text x="252" y="56" fill="#35D6E8" fontSize="10" fontWeight="800">Right Triangle</text>
            <text x="252" y="76" fill="#FFFFFF" fontSize="10" fontWeight="700">a² + b² = c²</text>
            <text x="252" y="96" fill="#C7D2FE" fontSize="10" fontWeight="600">Area = ½·b·h</text>
          </svg>
        );
      }

      case 'science_water_cycle_animated':
        return (
          <svg viewBox="0 0 380 170" className="w-full h-44 rounded-xl bg-gradient-to-b from-[#101B35] via-[#1B2B5C] to-[#13294B]">
            {/* Sun */}
            <circle cx="52" cy="36" r="18" fill="#FBBF24" />
            <circle cx="52" cy="36" r="24" fill="#FBBF24" fillOpacity="0.22" className="animate-antenna-spark" />
            <text x="52" y="68" textAnchor="middle" fill="#FDE68A" fontSize="9.5" fontWeight="800">Sun Heat</text>
            {/* Ocean / Water Body */}
            <path d="M10 138 Q 95 128 190 138 T 370 138 L 370 166 L 10 166 Z" fill="#0EA5BE" fillOpacity="0.65" />
            <text x="85" y="156" fill="#FFFFFF" fontSize="10" fontWeight="800">4. Collection (Ocean & Rivers)</text>
            {/* Mountain Land */}
            <polygon points="220,138 295,62 370,138" fill="#312E81" stroke="#818CF8" strokeWidth="1.5" />
            {/* Clouds */}
            <g>
              <ellipse cx="195" cy="38" rx="34" ry="15" fill="#EEEAFE" />
              <ellipse cx="222" cy="40" rx="24" ry="13" fill="#FFFFFF" />
              <text x="205" y="19" textAnchor="middle" fill="#35D6E8" fontSize="10" fontWeight="800">2. Condensation</text>
            </g>
            {/* Animated Evaporation Arrows */}
            <path d="M92 126 C 92 92 115 76 155 52" fill="none" stroke="#35D6E8" strokeWidth="2.5" strokeDasharray="6 4" className="animate-dash-flow" />
            <text x="78" y="96" fill="#35D6E8" fontSize="10" fontWeight="800">1. Evaporation ↑</text>
            {/* Animated Precipitation Rain */}
            <line x1="226" y1="56" x2="242" y2="96" stroke="#93EBF5" strokeWidth="2.2" strokeDasharray="4 4" className="animate-dash-flow" />
            <line x1="242" y1="56" x2="258" y2="96" stroke="#93EBF5" strokeWidth="2.2" strokeDasharray="4 4" className="animate-dash-flow" />
            <text x="292" y="62" textAnchor="middle" fill="#FFFFFF" fontSize="10" fontWeight="800">3. Precipitation ↓</text>
          </svg>
        );

      case 'science_electric_circuit_animated':
        return (
          <div className="space-y-2.5">
            <div className="flex items-center justify-between gap-2 text-xs">
              <span className="font-extrabold text-[#101B35]">
                Circuit Status:{' '}
                <span className={circuitOn ? 'text-emerald-600' : 'text-rose-600'}>
                  {circuitOn ? 'CLOSED LOOP (Current Flowing)' : 'OPEN LOOP (Current Stopped)'}
                </span>
              </span>
              <button
                type="button"
                onClick={() => setCircuitOn((v) => !v)}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-extrabold transition ${
                  circuitOn
                    ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
                    : 'bg-[#5146E5] hover:bg-[#4338CA] text-white'
                }`}
              >
                <Power className="w-3.5 h-3.5" />
                <span>Switch: {circuitOn ? 'ON' : 'OFF'}</span>
              </button>
            </div>
            <svg viewBox="0 0 360 155" className="w-full h-40 rounded-xl bg-[#101B35]">
              {/* Wire Loop */}
              <rect
                x="58"
                y="34"
                width="244"
                height="90"
                rx="16"
                fill="none"
                stroke={circuitOn ? '#35D6E8' : '#64748B'}
                strokeWidth="3.5"
                strokeDasharray={circuitOn ? '8 6' : 'none'}
                className={circuitOn ? 'animate-dash-flow' : ''}
              />
              {/* Battery */}
              <rect x="38" y="56" width="40" height="46" rx="8" fill="#5146E5" stroke="#FFFFFF" strokeWidth="1.8" />
              <text x="58" y="76" textAnchor="middle" fill="#FFFFFF" fontSize="10" fontWeight="800">9V</text>
              <text x="58" y="92" textAnchor="middle" fill="#35D6E8" fontSize="9" fontWeight="700">Battery</text>
              {/* Bulb */}
              <circle
                cx="302"
                cy="79"
                r="22"
                fill={circuitOn ? '#FDE047' : '#1E293B'}
                fillOpacity={circuitOn ? '0.92' : '1'}
                stroke="#FFFFFF"
                strokeWidth="2"
              />
              <text x="302" y="83" textAnchor="middle" fill={circuitOn ? '#101B35' : '#94A3B8'} fontSize="10" fontWeight="800">
                {circuitOn ? 'LIT!' : 'OFF'}
              </text>
              {/* Switch */}
              <rect x="148" y="112" width="64" height="24" rx="8" fill="#1E293B" stroke="#35D6E8" strokeWidth="1.5" />
              <line
                x1="158"
                y1="124"
                x2={circuitOn ? '202' : '196'}
                y2={circuitOn ? '124' : '110'}
                stroke="#35D6E8"
                strokeWidth="3"
                strokeLinecap="round"
              />
              <text x="180" y="148" textAnchor="middle" fill="#C7D2FE" fontSize="10" fontWeight="700">
                Interactive Switch ({circuitOn ? 'Closed' : 'Open'})
              </text>
              <text x="180" y="24" textAnchor="middle" fill="#35D6E8" fontSize="10" fontWeight="800">
                {circuitOn ? 'Current (I = V / R) → → →' : 'Loop broken — 0 A current'}
              </text>
            </svg>
          </div>
        );

      case 'science_cell_diagram': {
        const isPlant = Boolean(visualAid.dynamic_params?.is_plant);
        return (
          <svg viewBox="0 0 360 165" className="w-full h-44 rounded-xl bg-[#101B35]">
            {isPlant ? (
              <rect x="44" y="20" width="272" height="124" rx="22" fill="#14532D" fillOpacity="0.45" stroke="#34D399" strokeWidth="4" />
            ) : (
              <ellipse cx="180" cy="82" rx="135" ry="62" fill="#312E81" fillOpacity="0.45" stroke="#35D6E8" strokeWidth="3.5" />
            )}
            {/* Nucleus */}
            <circle cx="155" cy="78" r="28" fill="#5146E5" stroke="#FFFFFF" strokeWidth="2" />
            <circle cx="155" cy="78" r="10" fill="#35D6E8" />
            <text x="155" y="118" textAnchor="middle" fill="#FFFFFF" fontSize="10" fontWeight="800">Nucleus (DNA)</text>
            {/* Mitochondria */}
            <ellipse cx="242" cy="64" rx="24" ry="12" fill="#F97316" stroke="#FED7AA" strokeWidth="1.6" />
            <text x="242" y="88" textAnchor="middle" fill="#FED7AA" fontSize="9.5" fontWeight="800">Mitochondria</text>
            {/* Chloroplast or Cytoplasm */}
            {isPlant ? (
              <>
                <ellipse cx="96" cy="58" rx="20" ry="10" fill="#10B981" stroke="#A7F3D0" strokeWidth="1.5" />
                <text x="96" y="80" textAnchor="middle" fill="#A7F3D0" fontSize="9.5" fontWeight="800">Chloroplast</text>
              </>
            ) : (
              <text x="95" y="64" textAnchor="middle" fill="#C7D2FE" fontSize="10" fontWeight="700">Cytoplasm</text>
            )}
            <text x="180" y="156" textAnchor="middle" fill="#35D6E8" fontSize="10" fontWeight="800">
              {isPlant ? 'Cell Wall & Cell Membrane' : 'Selective Cell Membrane'}
            </text>
          </svg>
        );
      }

      case 'science_forces_motion_animated': {
        const friction = 4;
        const net = pushForce - friction;
        return (
          <div className="space-y-2.5">
            <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
              <span className="font-extrabold text-[#101B35]">
                Push: <span className="text-[#5146E5]">{pushForce} N</span> − Friction: 4 N ={' '}
                <span className="text-emerald-700">Net {net} N →</span>
              </span>
              <div className="flex items-center gap-1.5">
                {[8, 12, 18].map((val) => (
                  <button
                    key={val}
                    type="button"
                    onClick={() => setPushForce(val)}
                    className={`px-2.5 py-1 rounded-lg text-[11px] font-extrabold transition ${
                      pushForce === val ? 'bg-[#5146E5] text-white' : 'bg-[#EEEAFE] text-[#5146E5]'
                    }`}
                  >
                    {val} N
                  </button>
                ))}
              </div>
            </div>
            <svg viewBox="0 0 360 140" className="w-full h-36 rounded-xl bg-[#101B35]">
              <line x1="20" y1="104" x2="340" y2="104" stroke="#64748B" strokeWidth="3" />
              <rect x="145" y="54" width="70" height="48" rx="10" fill="#5146E5" stroke="#FFFFFF" strokeWidth="2" />
              <text x="180" y="82" textAnchor="middle" fill="#FFFFFF" fontSize="11" fontWeight="800">Mass (m)</text>
              {/* Push Arrow Right */}
              <line x1="218" y1="78" x2={240 + pushForce * 3.5} y2="78" stroke="#35D6E8" strokeWidth="4" strokeLinecap="round" />
              <text x="275" y="66" textAnchor="middle" fill="#35D6E8" fontSize="10" fontWeight="800">Push ({pushForce} N) →</text>
              {/* Friction Arrow Left */}
              <line x1="142" y1="90" x2="96" y2="90" stroke="#F87171" strokeWidth="3.5" strokeLinecap="round" />
              <text x="95" y="78" textAnchor="middle" fill="#FCA5A5" fontSize="10" fontWeight="800">← Friction (4 N)</text>
              {/* Normal & Gravity */}
              <line x1="180" y1="50" x2="180" y2="20" stroke="#A5B4FC" strokeWidth="2.5" />
              <text x="180" y="15" textAnchor="middle" fill="#C7D2FE" fontSize="9.5" fontWeight="700">Normal Force ↑</text>
              <text x="180" y="124" textAnchor="middle" fill="#E2E8F0" fontSize="10" fontWeight="700">Gravity (Weight = mg) ↓</text>
            </svg>
          </div>
        );
      }

      case 'science_solar_system_animated':
        return (
          <svg viewBox="0 0 360 165" className="w-full h-44 rounded-xl bg-[#101B35]">
            <circle cx="180" cy="82" r="20" fill="#FBBF24" />
            <circle cx="180" cy="82" r="27" fill="#FBBF24" fillOpacity="0.2" />
            <text x="180" y="86" textAnchor="middle" fill="#101B35" fontSize="10" fontWeight="800">Sun</text>
            <circle cx="180" cy="82" r="46" fill="none" stroke="#35D6E8" strokeOpacity="0.4" strokeDasharray="4 4" />
            <circle cx="180" cy="82" r="70" fill="none" stroke="#818CF8" strokeOpacity="0.45" strokeDasharray="4 4" />
            <g className="animate-orbit-fast" style={{ transformOrigin: '180px 82px' }}>
              <circle cx="226" cy="82" r="6.5" fill="#35D6E8" stroke="#FFFFFF" strokeWidth="1.2" />
            </g>
            <g className="animate-orbit-slow" style={{ transformOrigin: '180px 82px' }}>
              <circle cx="180" cy="12" r="8.5" fill="#A78BFA" stroke="#FFFFFF" strokeWidth="1.2" />
            </g>
            <text x="24" y="26" fill="#35D6E8" fontSize="10" fontWeight="800">Inner Orbit (Earth)</text>
            <text x="24" y="42" fill="#C7D2FE" fontSize="10" fontWeight="700">Outer Orbit (Gas Giants)</text>
          </svg>
        );

      case 'science_human_body':
        return (
          <svg viewBox="0 0 360 155" className="w-full h-40 rounded-xl bg-[#101B35]">
            <rect x="34" y="44" width="88" height="62" rx="16" fill="#0EA5BE" fillOpacity="0.35" stroke="#35D6E8" strokeWidth="2" />
            <text x="78" y="72" textAnchor="middle" fill="#FFFFFF" fontSize="11" fontWeight="800">Lungs</text>
            <text x="78" y="88" textAnchor="middle" fill="#35D6E8" fontSize="9.5" fontWeight="700">+O₂ / −CO₂</text>
            <rect x="148" y="44" width="76" height="62" rx="16" fill="#E11D48" fillOpacity="0.4" stroke="#FB7185" strokeWidth="2" />
            <text x="186" y="72" textAnchor="middle" fill="#FFFFFF" fontSize="11" fontWeight="800">Heart</text>
            <text x="186" y="88" textAnchor="middle" fill="#FECDD3" fontSize="9.5" fontWeight="700">4-Chamber</text>
            <rect x="252" y="44" width="82" height="62" rx="16" fill="#5146E5" fillOpacity="0.45" stroke="#A5B4FC" strokeWidth="2" />
            <text x="293" y="72" textAnchor="middle" fill="#FFFFFF" fontSize="11" fontWeight="800">Body Cells</text>
            <text x="293" y="88" textAnchor="middle" fill="#C7D2FE" fontSize="9.5" fontWeight="700">Uses Oxygen</text>
            <path d="M124 62 L250 62" stroke="#FB7185" strokeWidth="3" strokeDasharray="6 4" className="animate-dash-flow" />
            <path d="M250 92 L124 92" stroke="#35D6E8" strokeWidth="3" strokeDasharray="6 4" className="animate-dash-flow" />
            <text x="186" y="30" textAnchor="middle" fill="#FDA4AF" fontSize="10" fontWeight="800">Oxygenated Arteries →</text>
            <text x="186" y="130" textAnchor="middle" fill="#35D6E8" fontSize="10" fontWeight="800">← Deoxygenated Veins</text>
          </svg>
        );

      case 'geography_landforms':
        return (
          <svg viewBox="0 0 360 155" className="w-full h-40 rounded-xl bg-gradient-to-b from-[#101B35] to-[#1D2E5E]">
            <polygon points="16,132 76,34 134,132" fill="#4338CA" stroke="#A5B4FC" strokeWidth="1.8" />
            <polygon points="114,132 132,74 206,74 222,132" fill="#5146E5" fillOpacity="0.8" stroke="#C7D2FE" strokeWidth="1.6" />
            <rect x="214" y="110" width="84" height="22" fill="#10B981" fillOpacity="0.65" />
            <path d="M292 110 Q 326 112 346 132 L 292 132 Z" fill="#35D6E8" fillOpacity="0.75" />
            <text x="76" y="26" textAnchor="middle" fill="#FFFFFF" fontSize="10" fontWeight="800">Mountain</text>
            <text x="168" y="66" textAnchor="middle" fill="#35D6E8" fontSize="10" fontWeight="800">Plateau</text>
            <text x="256" y="102" textAnchor="middle" fill="#A7F3D0" fontSize="10" fontWeight="800">Alluvial Plain</text>
            <text x="322" y="102" textAnchor="middle" fill="#35D6E8" fontSize="10" fontWeight="800">Delta</text>
          </svg>
        );

      case 'history_timeline':
        return (
          <svg viewBox="0 0 360 130" className="w-full h-32 rounded-xl bg-[#101B35]">
            <line x1="34" y1="64" x2="326" y2="64" stroke="#5146E5" strokeWidth="4" strokeLinecap="round" />
            {[
              { x: 52, title: '1. Causes', sub: 'Background' },
              { x: 138, title: '2. Turning Pt', sub: 'Spark' },
              { x: 224, title: '3. Key Events', sub: 'Actions' },
              { x: 308, title: '4. Legacy', sub: 'Impact' },
            ].map((node) => (
              <g key={node.title}>
                <circle cx={node.x} cy="64" r="10" fill="#35D6E8" stroke="#FFFFFF" strokeWidth="2" />
                <text x={node.x} y="38" textAnchor="middle" fill="#FFFFFF" fontSize="10" fontWeight="800">{node.title}</text>
                <text x={node.x} y="94" textAnchor="middle" fill="#C7D2FE" fontSize="9.5" fontWeight="600">{node.sub}</text>
              </g>
            ))}
          </svg>
        );

      case 'english_grammar_tree':
        return (
          <svg viewBox="0 0 360 140" className="w-full h-36 rounded-xl bg-[#101B35]">
            {[
              { x: 16, w: 80, bg: '#5146E5', label: 'SUBJECT', ex: 'The student' },
              { x: 106, w: 72, bg: '#0EA5BE', label: 'ADVERB', ex: 'quickly' },
              { x: 188, w: 68, bg: '#4F46E5', label: 'VERB', ex: 'solved' },
              { x: 266, w: 78, bg: '#312E81', label: 'OBJECT', ex: 'the puzzle' },
            ].map((b) => (
              <g key={b.label}>
                <rect x={b.x} y="38" width={b.w} height="58" rx="12" fill={b.bg} stroke="#35D6E8" strokeWidth="1.5" />
                <text x={b.x + b.w / 2} y="60" textAnchor="middle" fill="#35D6E8" fontSize="9.5" fontWeight="800">{b.label}</text>
                <text x={b.x + b.w / 2} y="80" textAnchor="middle" fill="#FFFFFF" fontSize="10.5" fontWeight="700">{b.ex}</text>
              </g>
            ))}
            <text x="180" y="120" textAnchor="middle" fill="#C7D2FE" fontSize="10" fontWeight="700">
              Clear Sentence Flow: Who → How → Action → Receiver
            </text>
          </svg>
        );

      default:
        return (
          <svg viewBox="0 0 360 150" className="w-full h-40 rounded-xl bg-[#101B35]">
            <line x1="42" y1="120" x2="328" y2="120" stroke="#94A3B8" strokeWidth="2" />
            <line x1="42" y1="120" x2="42" y2="24" stroke="#94A3B8" strokeWidth="2" />
            <line x1="56" y1="108" x2="296" y2="36" stroke="#35D6E8" strokeWidth="3" strokeDasharray="6 4" className="animate-dash-flow" />
            <circle cx="96" cy="96" r="5" fill="#FFFFFF" />
            <circle cx="176" cy="72" r="5" fill="#5146E5" stroke="#FFFFFF" strokeWidth="1.5" />
            <circle cx="256" cy="48" r="5.5" fill="#35D6E8" stroke="#FFFFFF" strokeWidth="1.5" />
            <text x="320" y="136" textAnchor="end" fill="#C7D2FE" fontSize="10" fontWeight="700">X-Axis (Input)</text>
            <text x="52" y="24" fill="#C7D2FE" fontSize="10" fontWeight="700">Y-Axis (Output)</text>
            <text x="200" y="42" fill="#35D6E8" fontSize="10.5" fontWeight="800">y = m·x + c (Linear Pattern)</text>
          </svg>
        );
    }
  };

  return (
    <div
      data-testid="visual-teaching-canvas"
      className="mt-3 rounded-2xl border border-[#C7D7F7] bg-[#F7F9FF] p-4 space-y-3.5 text-[#172554]"
    >
      {/* Visual Card Header */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <span className="w-7 h-7 rounded-xl bg-[#5146E5] text-white flex items-center justify-center shrink-0">
            <Eye className="w-4 h-4" />
          </span>
          <div className="min-w-0">
            <div className="text-[10px] font-extrabold uppercase tracking-wider text-[#5146E5]">
              Visual AI Model • {visualAid.subject}
              {visualAid.interactive_animated ? ' • Interactive' : ''}
            </div>
            <div className="text-sm font-extrabold text-[#101B35] truncate">{visualAid.title}</div>
          </div>
        </div>
        {visualAid.step_by_step_walkthrough && visualAid.step_by_step_walkthrough.length > 0 && (
          <button
            type="button"
            onClick={() => setShowSteps((s) => !s)}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white border border-[#C7D7F7] text-[11px] font-extrabold text-[#4F46E5] hover:bg-[#EEEAFE] transition"
          >
            <span>{showSteps ? 'Hide Steps' : 'Visual Steps'}</span>
            {showSteps ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        )}
      </div>

      {/* Rendered Interactive SVG Diagram */}
      <div>{renderInteractiveSvg()}</div>

      {/* Clickable Labelled Parts */}
      {visualAid.labels && visualAid.labels.length > 0 && (
        <div className="space-y-2">
          <div className="text-[11px] font-extrabold text-[#172554]/75">
            Tap any labelled part to inspect:
          </div>
          <div className="flex flex-wrap gap-1.5">
            {visualAid.labels.map((lbl) => {
              const isSelected = lbl.id === activeLabelId;
              return (
                <button
                  key={lbl.id}
                  type="button"
                  onClick={() => setActiveLabelId(lbl.id)}
                  className={`px-2.5 py-1.5 rounded-xl text-[11px] font-extrabold border transition ${
                    isSelected
                      ? 'bg-[#5146E5] border-[#5146E5] text-white shadow-sm'
                      : 'bg-white border-[#C7D7F7] text-[#172554] hover:border-[#5146E5]'
                  }`}
                >
                  {lbl.label}
                </button>
              );
            })}
          </div>
          {activeLabel && (
            <div className="p-3 rounded-xl bg-white border border-[#DCE6FA] text-xs font-medium text-[#202943] flex items-start gap-2">
              <Lightbulb className="w-4 h-4 text-[#5146E5] shrink-0 mt-0.5" />
              <span>
                <strong className="text-[#101B35]">{activeLabel.label}:</strong> {activeLabel.description}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Step-by-Step Visual Walkthrough */}
      {showSteps && visualAid.step_by_step_walkthrough && visualAid.step_by_step_walkthrough.length > 0 && (
        <div className="p-3 rounded-xl bg-[#EEEAFE]/65 border border-[#5146E5]/15 space-y-1.5">
          <div className="text-[11px] font-extrabold text-[#5146E5] flex items-center gap-1.5">
            <Play className="w-3 h-3 fill-current" />
            <span>Step-by-Step Visual Guide</span>
          </div>
          <ol className="space-y-1 text-xs font-medium text-[#202943]">
            {visualAid.step_by_step_walkthrough.map((st, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="w-4 h-4 rounded-full bg-[#5146E5] text-white text-[10px] font-extrabold flex items-center justify-center shrink-0 mt-0.5">
                  {idx + 1}
                </span>
                <span>{st}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* Quick Interactive Understanding Check */}
      {visualAid.check_question && (
        <div className="p-3.5 rounded-xl bg-white border border-[#C7D7F7] space-y-2.5">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 text-xs font-extrabold text-[#101B35]">
              <Sparkles className="w-3.5 h-3.5 text-[#5146E5]" />
              <span>Quick Check from Sparky</span>
            </div>
            {visualAid.check_question.hint && !checkFeedback?.correct && (
              <button
                type="button"
                onClick={() => setShowHint((h) => !h)}
                className="text-[11px] font-extrabold text-[#5146E5] hover:underline"
              >
                {showHint ? 'Hide Hint' : 'Need a hint?'}
              </button>
            )}
          </div>
          <p className="text-xs font-bold text-[#202943]">{visualAid.check_question.prompt}</p>

          {showHint && visualAid.check_question.hint && (
            <div className="p-2.5 rounded-lg bg-[#EEEAFE] text-[11px] font-bold text-[#101B35]">
              Hint: {visualAid.check_question.hint}
            </div>
          )}

          <div className="grid sm:grid-cols-3 gap-1.5">
            {visualAid.check_question.options.map((opt) => {
              const isChosen = selectedOption === opt;
              const isRight = checkFeedback?.correct && isChosen;
              return (
                <button
                  key={opt}
                  type="button"
                  onClick={() => handleCheckAnswer(opt)}
                  className={`px-3 py-2 rounded-xl border text-left text-[11px] font-extrabold transition ${
                    isRight
                      ? 'bg-emerald-600 border-emerald-600 text-white'
                      : isChosen
                        ? 'bg-[#5146E5] border-[#5146E5] text-white'
                        : 'bg-[#F6F7FC] border-[#DCE2F5] hover:border-[#5146E5] text-[#202943]'
                  }`}
                >
                  {opt}
                </button>
              );
            })}
          </div>

          {checkFeedback && (
            <div
              className={`p-2.5 rounded-xl border flex items-center gap-2.5 text-xs font-bold ${
                checkFeedback.correct
                  ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                  : 'bg-amber-50 border-amber-200 text-amber-900'
              }`}
            >
              <SparkRobotMascot
                mood={checkFeedback.correct ? 'celebrating' : 'encouraging'}
                size="xs"
              />
              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-1">
                  {checkFeedback.correct && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />}
                  <span>{checkFeedback.text}</span>
                </div>
                {!checkFeedback.correct && onAskAnotherWay && (
                  <button
                    type="button"
                    onClick={() =>
                      onAskAnotherWay(
                        `Please explain ${visualAid.concept} in an even simpler way with a daily-life example.`
                      )
                    }
                    className="text-[11px] font-extrabold text-[#5146E5] hover:underline"
                  >
                    Ask Sparky to explain another way →
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
