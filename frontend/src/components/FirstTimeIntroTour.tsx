import React from 'react';
import {
  ArrowLeft,
  ArrowRight,
  CalendarCheck,
  CheckCircle2,
  Flame,
  Sparkles,
  TrendingUp,
} from 'lucide-react';
import { BrandTagline, EduSparkLogo } from '../design-system/EduSparkLogo';
import { BRAND_DESCRIPTION } from '../design-system/tokens';
import { SparkRobotMascot, RobotMood } from './SparkRobotMascot';

interface FirstTimeIntroTourProps {
  onGetStarted: () => void;
  onSkip: () => void;
  isReplay?: boolean;
}

interface IntroSlide {
  number: number;
  eyebrow: string;
  title: string;
  description: string;
  robotMood: RobotMood;
  visualKind: 'welcome' | 'buddy' | 'visuals' | 'planner' | 'growth';
  highlights: string[];
}

const INTRO_SLIDES: IntroSlide[] = [
  {
    number: 1,
    eyebrow: 'Welcome',
    title: 'Welcome to SparkMinds AI',
    description: 'Your journey to smarter learning starts here.',
    robotMood: 'welcome',
    visualKind: 'welcome',
    highlights: ['Grades 1–12', 'CBSE • ICSE • State', '23 Languages'],
  },
  {
    number: 2,
    eyebrow: 'AI Robot Teacher',
    title: 'Meet Your AI Learning Buddy',
    description: 'Ask anything. Understand everything.',
    robotMood: 'happy',
    visualKind: 'buddy',
    highlights: ['Step-by-step teaching', 'Photo homework help', 'Unlimited follow-ups'],
  },
  {
    number: 3,
    eyebrow: 'Visual Understanding',
    title: 'Learn Visually',
    description: 'See it. Understand it. Remember it.',
    robotMood: 'guiding',
    visualKind: 'visuals',
    highlights: ['Interactive Math', 'Animated Science', 'Labelled Diagrams'],
  },
  {
    number: 4,
    eyebrow: 'Smart Routine',
    title: 'Plan Your Learning',
    description: 'Make every day count.',
    robotMood: 'happy',
    visualKind: 'planner',
    highlights: ['Real-schedule fit', 'Smart breaks', 'Exam countdowns'],
  },
  {
    number: 5,
    eyebrow: 'Real Mastery',
    title: 'Track Your Growth',
    description: 'Every step takes you closer to your goals.',
    robotMood: 'celebrating',
    visualKind: 'growth',
    highlights: ['Real streaks', 'Smart revision', 'Grade 1–12 memory'],
  },
];

/**
 * Part 4 — Ultra-Premium 5-Slide First-Time Introduction Tour + Final "Your Future Starts Here." Screen
 */
export const FirstTimeIntroTour: React.FC<FirstTimeIntroTourProps> = ({
  onGetStarted,
  onSkip,
  isReplay = false,
}) => {
  const [step, setStep] = React.useState<number>(0);
  const [demoFractionNum, setDemoFractionNum] = React.useState<number>(3);
  const isFinalScreen = step === INTRO_SLIDES.length;
  const activeSlide = !isFinalScreen ? INTRO_SLIDES[step] : null;

  React.useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' && !isFinalScreen) {
        setStep((s) => Math.min(INTRO_SLIDES.length, s + 1));
      } else if (e.key === 'ArrowLeft' && step > 0) {
        setStep((s) => Math.max(0, s - 1));
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [isFinalScreen, step]);

  return (
    <div
      data-testid="first-time-intro-tour"
      className="min-h-screen flex flex-col justify-between eduspark-mesh-bg spark-light-dot-grid text-[#202943] relative overflow-hidden"
    >
      {/* Top Floating Bar */}
      <header className="relative z-10 max-w-5xl w-full mx-auto px-5 sm:px-8 pt-6 flex items-center justify-between gap-4">
        <EduSparkLogo size="sm" />
        <div className="flex items-center gap-2.5">
          {!isFinalScreen && activeSlide && (
            <span className="px-3.5 py-1.5 rounded-full bg-white/90 backdrop-blur border border-[#DCE2F5] text-[#5146E5] text-xs font-extrabold shadow-sm">
              {activeSlide.number} of {INTRO_SLIDES.length}
            </span>
          )}
          <button
            type="button"
            onClick={onSkip}
            className="px-4 py-2 rounded-xl text-xs font-extrabold text-[#202943]/75 hover:text-[#101B35] bg-white/75 hover:bg-white border border-[#DCE2F5] shadow-sm transition"
          >
            {isReplay ? 'Close' : 'Skip'}
          </button>
        </div>
      </header>

      {/* Main Centered Showcase Card */}
      <main className="relative z-10 flex-1 flex items-center justify-center px-5 sm:px-8 py-8">
        {!isFinalScreen && activeSlide ? (
          <div
            key={activeSlide.number}
            className="w-full max-w-5xl bg-white/95 backdrop-blur-xl rounded-[2.25rem] border border-[#D8E1F6] shadow-[0_32px_80px_-28px_rgba(16,27,53,0.22)] overflow-hidden grid md:grid-cols-12 animate-fade-in"
          >
            {/* Left Cinematic Illustration Stage */}
            <div
              className="md:col-span-6 p-7 sm:p-10 flex flex-col items-center justify-center text-white relative overflow-hidden min-h-[340px]"
              style={{
                background:
                  'linear-gradient(145deg, #0D1630 0%, #1C2663 52%, #5146E5 100%)',
              }}
            >
              <div aria-hidden="true" className="pointer-events-none absolute inset-0 spark-hero-grid opacity-55" />
              <div
                aria-hidden="true"
                className="pointer-events-none absolute -bottom-20 -right-16 w-64 h-64 rounded-full bg-[#35D6E8]/25 blur-3xl"
              />

              {activeSlide.visualKind === 'welcome' && (
                <div className="relative z-10 flex flex-col items-center text-center space-y-5">
                  <div className="relative flex items-center justify-center">
                    <div className="absolute w-40 h-40 rounded-full border border-dashed border-[#35D6E8]/35 animate-orbit-slow" />
                    <SparkRobotMascot mood="welcome" size="xl" />
                  </div>
                  <div className="px-4 py-2.5 rounded-2xl bg-white/10 border border-[#35D6E8]/45 text-xs font-bold text-[#35D6E8] backdrop-blur-md shadow-lg">
                    Hi! I&apos;m Sparky — {BRAND_DESCRIPTION}
                  </div>
                </div>
              )}

              {activeSlide.visualKind === 'buddy' && (
                <div className="relative z-10 w-full space-y-4">
                  <div className="flex items-center gap-3">
                    <SparkRobotMascot mood="happy" size="md" />
                    <div className="flex-1 rounded-2xl rounded-tl-sm bg-white/12 border border-white/25 p-3.5 text-xs font-semibold text-white backdrop-blur-md shadow-md">
                      &ldquo;Why do clouds form during the water cycle?&rdquo;
                    </div>
                  </div>
                  <div className="rounded-2xl bg-[#0B1328]/90 border border-[#35D6E8]/45 p-4 space-y-3 shadow-2xl">
                    <div className="flex items-center justify-between text-[11px] font-extrabold text-[#35D6E8]">
                      <span>Real AI Teacher + Visual Model</span>
                      <span className="px-2 py-0.5 rounded-full bg-[#5146E5]/50 text-white">23 Languages</span>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-[10px] font-bold text-center">
                      <div className="p-2.5 rounded-xl bg-white/10 border border-white/10">1. Warm Vapour</div>
                      <div className="p-2.5 rounded-xl bg-[#5146E5]/80 border border-[#35D6E8]/60 shadow-md">
                        2. Cools in Sky
                      </div>
                      <div className="p-2.5 rounded-xl bg-white/10 border border-white/10">3. Cloud Droplets</div>
                    </div>
                  </div>
                </div>
              )}

              {activeSlide.visualKind === 'visuals' && (
                <div className="relative z-10 w-full space-y-4">
                  <div className="rounded-2xl bg-[#0B1328]/90 border border-[#35D6E8]/50 p-5 space-y-3.5 shadow-2xl">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-extrabold text-[#35D6E8]">
                        Interactive Fraction Visual: {demoFractionNum}/4
                      </span>
                      <button
                        type="button"
                        onClick={() => setDemoFractionNum((n) => (n % 4) + 1)}
                        className="px-3 py-1.5 rounded-xl spark-btn-aqua text-[11px] font-extrabold transition"
                      >
                        Tap to slice
                      </button>
                    </div>
                    <div className="grid grid-cols-4 gap-2 h-12">
                      {[1, 2, 3, 4].map((idx) => (
                        <div
                          key={idx}
                          className={`rounded-xl transition-all duration-300 border flex items-center justify-center text-[11px] font-extrabold ${
                            idx <= demoFractionNum
                              ? 'bg-[#35D6E8] border-white/80 text-[#101B35] shadow-md shadow-[#35D6E8]/30'
                              : 'bg-white/10 border-white/20 text-indigo-200'
                          }`}
                        >
                          1/4
                        </div>
                      ))}
                    </div>
                    <div className="flex items-center justify-between text-[10px] text-indigo-100 font-semibold">
                      <span>Math • Science • Geography • History • English</span>
                      <span className="text-[#35D6E8]">Interactive</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-center gap-2 text-xs font-bold text-indigo-100">
                    <SparkRobotMascot mood="guiding" size="xs" />
                    <span>Tap &ldquo;Tap to slice&rdquo; to preview live visual learning</span>
                  </div>
                </div>
              )}

              {activeSlide.visualKind === 'planner' && (
                <div className="relative z-10 w-full space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="inline-flex items-center gap-2 text-xs font-extrabold text-[#35D6E8]">
                      <CalendarCheck className="w-4 h-4" />
                      <span>Today&apos;s Balanced Study Plan</span>
                    </div>
                    <SparkRobotMascot mood="happy" size="xs" />
                  </div>
                  {[
                    { time: '5:30 PM', task: 'Mathematics — Fractions Visuals', tag: '25 min' },
                    { time: '6:15 PM', task: 'Science — Water Cycle Lab', tag: '20 min' },
                    { time: '7:00 PM', task: 'Smart Revision Active Recall', tag: '15 min' },
                  ].map((item, idx) => (
                    <div
                      key={item.task}
                      className={`p-3.5 rounded-2xl border flex items-center justify-between gap-2 text-xs backdrop-blur ${
                        idx === 0
                          ? 'bg-[#35D6E8]/18 border-[#35D6E8]/60 text-white shadow-lg'
                          : 'bg-white/10 border-white/15 text-indigo-100'
                      }`}
                    >
                      <div className="min-w-0">
                        <div className="text-[10px] font-extrabold text-[#35D6E8]">{item.time}</div>
                        <div className="font-bold truncate">{item.task}</div>
                      </div>
                      <span className="px-2.5 py-1 rounded-lg bg-[#0B1328]/80 text-[10px] font-extrabold shrink-0">
                        {item.tag}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {activeSlide.visualKind === 'growth' && (
                <div className="relative z-10 w-full space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#35D6E8]/20 border border-[#35D6E8]/55 text-[#35D6E8] text-xs font-extrabold">
                      <Flame className="w-3.5 h-3.5" /> Real Daily Mastery
                    </span>
                    <SparkRobotMascot mood="celebrating" size="sm" />
                  </div>
                  <div className="grid grid-cols-2 gap-2.5 text-xs">
                    {[
                      { label: 'Homework Help', sub: 'Step-by-step hints' },
                      { label: 'Exam Readiness', sub: 'Timed mock papers' },
                      { label: 'Smart Revision', sub: 'Spaced recall cards' },
                      { label: 'Grades 1–12', sub: 'Permanent progress' },
                    ].map((card) => (
                      <div
                        key={card.label}
                        className="p-3.5 rounded-2xl bg-white/10 border border-white/15 space-y-1 backdrop-blur"
                      >
                        <div className="font-extrabold text-white flex items-center gap-1.5">
                          <CheckCircle2 className="w-3.5 h-3.5 text-[#35D6E8] shrink-0" />
                          <span>{card.label}</span>
                        </div>
                        <div className="text-[11px] text-indigo-200">{card.sub}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Right Clean Editorial Narrative Column */}
            <div className="md:col-span-6 p-7 sm:p-11 flex flex-col justify-between gap-8">
              <div className="space-y-4">
                <span className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full bg-[#EEEAFE] text-[#5146E5] text-xs font-extrabold">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>{activeSlide.eyebrow}</span>
                </span>
                <h1 className="font-display text-3xl sm:text-4xl font-bold text-[#101B35] tracking-tight leading-[1.12]">
                  {activeSlide.title}
                </h1>
                <p className="text-base sm:text-lg font-medium text-[#202943]/80 leading-relaxed">
                  {activeSlide.description}
                </p>

                <div className="flex flex-wrap gap-2 pt-1">
                  {activeSlide.highlights.map((chip) => (
                    <span
                      key={chip}
                      className="px-3 py-1 rounded-xl bg-[#F6F7FC] border border-[#DCE2F5] text-[11px] font-bold text-[#202943]"
                    >
                      {chip}
                    </span>
                  ))}
                </div>

                <p className="text-xs pt-1 leading-snug">
                  <BrandTagline variant="light" />
                </p>
              </div>

              {/* Step Dots + Controls */}
              <div className="space-y-5">
                <div className="flex items-center gap-2" aria-label="Introduction progress">
                  {INTRO_SLIDES.map((s, idx) => (
                    <button
                      key={s.number}
                      type="button"
                      onClick={() => setStep(idx)}
                      aria-label={`Go to slide ${s.number}`}
                      className={`h-2 rounded-full transition-all duration-300 ${
                        idx === step
                          ? 'w-9 bg-[#5146E5]'
                          : idx < step
                            ? 'w-3.5 bg-[#35D6E8]'
                            : 'w-2.5 bg-[#DCE2F5]'
                      }`}
                    />
                  ))}
                </div>

                <div className="flex items-center justify-between gap-3">
                  <button
                    type="button"
                    disabled={step === 0}
                    onClick={() => setStep((s) => Math.max(0, s - 1))}
                    className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl border border-[#DCE2F5] bg-white hover:bg-[#F6F7FC] text-[#202943] text-xs font-extrabold disabled:opacity-35 transition min-h-[46px]"
                  >
                    <ArrowLeft className="w-4 h-4" />
                    <span>Back</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setStep((s) => s + 1)}
                    className="inline-flex items-center gap-2 px-7 py-2.5 rounded-xl spark-btn-primary text-sm font-extrabold min-h-[46px]"
                  >
                    <span>{step === INTRO_SLIDES.length - 1 ? 'Continue' : 'Next'}</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* FINAL SCREEN: "Your Future Starts Here." + Prominent Get Started CTA */
          <div
            key="final-start"
            className="w-full max-w-2xl rounded-[2.25rem] p-9 sm:p-14 text-center text-white shadow-[0_36px_90px_-24px_rgba(16,27,53,0.45)] border border-[#35D6E8]/40 space-y-6 animate-spark-celebrate relative overflow-hidden"
            style={{
              background:
                'linear-gradient(155deg, #0D1630 0%, #20286B 56%, #5146E5 100%)',
            }}
          >
            <div aria-hidden="true" className="pointer-events-none absolute inset-0 spark-hero-grid opacity-55" />
            <div
              aria-hidden="true"
              className="pointer-events-none absolute -top-24 left-1/2 -translate-x-1/2 w-80 h-80 rounded-full bg-[#35D6E8]/22 blur-3xl"
            />
            <div className="relative z-10 flex flex-col items-center space-y-5">
              <SparkRobotMascot mood="celebrating" size="xl" />

              <span className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full bg-white/10 border border-[#35D6E8]/45 text-[#35D6E8] text-xs font-extrabold backdrop-blur">
                <TrendingUp className="w-3.5 h-3.5" />
                <span>SparkMinds AI • Grades 1–12</span>
              </span>

              <h1 className="font-display text-3xl sm:text-5xl font-bold tracking-tight text-white">
                Your Future Starts Here.
              </h1>

              <p className="text-sm sm:text-base text-indigo-100 font-medium max-w-md leading-relaxed">
                Start your personalised learning journey with SparkMinds AI.
              </p>

              <div className="px-4 py-2.5 rounded-2xl bg-white/[0.08] border border-[#35D6E8]/45 backdrop-blur-md shadow-lg">
                <p className="text-sm sm:text-base leading-snug">
                  <BrandTagline variant="dark" animate />
                </p>
              </div>

              <div className="pt-3 flex flex-col sm:flex-row items-center justify-center gap-3 w-full">
                <button
                  type="button"
                  onClick={() => setStep(INTRO_SLIDES.length - 1)}
                  className="inline-flex items-center justify-center gap-1.5 px-5 py-3 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-white text-xs font-extrabold transition min-h-[50px] w-full sm:w-auto"
                >
                  <ArrowLeft className="w-4 h-4" />
                  <span>Back</span>
                </button>
                <button
                  type="button"
                  onClick={onGetStarted}
                  className="inline-flex items-center justify-center gap-2 px-9 py-3.5 rounded-xl spark-btn-aqua text-base font-extrabold min-h-[52px] w-full sm:w-auto"
                >
                  <span>{isReplay ? 'Back to App' : 'Get Started'}</span>
                  <ArrowRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="relative z-10 text-center pb-5 px-5 text-[11px] font-semibold text-[#202943]/60">
        SparkMinds AI • CBSE, ICSE &amp; State Boards • 23 Languages • Child-Safe Learning
      </footer>
    </div>
  );
};
