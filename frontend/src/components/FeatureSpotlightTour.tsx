import React from 'react';
import { ArrowLeft, ArrowRight, CheckCircle2, X } from 'lucide-react';
import { ScreenId } from '../design-system/tokens';
import { SparkRobotMascot, RobotMood } from './SparkRobotMascot';

interface FeatureSpotlightTourProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigateScreen: (screen: ScreenId) => void;
  studentName?: string;
}

interface SpotlightStep {
  tourId: string;
  screen: ScreenId;
  title: string;
  description: string;
  actionLabel: string;
  mood: RobotMood;
}

const SPOTLIGHT_STEPS: SpotlightStep[] = [
  {
    tourId: 'nav-dashboard',
    screen: 'dashboard',
    title: 'Your Learning Dashboard',
    description:
      "See today's learning goals, upcoming homework, daily schedule, and real study streak all in one calm place.",
    actionLabel: 'View Dashboard',
    mood: 'welcome',
  },
  {
    tourId: 'nav-buddy',
    screen: 'buddy',
    title: 'AI Learning Buddy (Sparky)',
    description:
      'Ask any school question in 23 languages! Sparky explains step by step with labelled diagrams and interactive visuals.',
    actionLabel: 'Open AI Buddy',
    mood: 'happy',
  },
  {
    tourId: 'nav-subjects',
    screen: 'subjects',
    title: 'Guided Interactive Lessons',
    description:
      'Learn one small idea at a time with interactive activities, instant feedback, and syllabus-aligned chapters.',
    actionLabel: 'Explore Lessons',
    mood: 'guiding',
  },
  {
    tourId: 'nav-plan',
    screen: 'plan',
    title: 'Smart Study Planner',
    description:
      'Share your school and daily schedule — SparkMinds AI builds balanced study blocks around your real free time.',
    actionLabel: 'Open Study Planner',
    mood: 'happy',
  },
  {
    tourId: 'nav-homework',
    screen: 'homework',
    title: 'Homework Manager',
    description:
      'Track deadlines by priority and tap any assignment to get step-by-step guidance from Sparky.',
    actionLabel: 'Open Homework',
    mood: 'guiding',
  },
  {
    tourId: 'nav-exams',
    screen: 'exams',
    title: 'Exam Preparation Centre',
    description:
      'Practice with timed mock tests, review mistakes immediately, and build confidence before school exams.',
    actionLabel: 'Open Exam Prep',
    mood: 'encouraging',
  },
  {
    tourId: 'nav-practice',
    screen: 'practice',
    title: 'Smart Revision',
    description:
      'Review key concepts with short spaced-repetition flashcards so important ideas stay fresh.',
    actionLabel: 'Open Smart Revision',
    mood: 'happy',
  },
  {
    tourId: 'nav-progress',
    screen: 'progress',
    title: 'Academic Progress & Journey',
    description:
      'Track real mastery scores, resolved learning gaps, and your multi-year academic journey from Grade 1 to 12.',
    actionLabel: 'View Progress',
    mood: 'celebrating',
  },
];

/**
 * Part 10 — Click-by-Click Interactive Interface Spotlight Feature Tour
 * Highlights actual rendered buttons/sections in the real app DOM via data-tour-id,
 * dims the surroundings while keeping the highlighted target clickable, and lets
 * the student move cleanly step by step with Back, Next, Skip Tour, and Finish.
 */
export const FeatureSpotlightTour: React.FC<FeatureSpotlightTourProps> = ({
  isOpen,
  onClose,
  onNavigateScreen,
  studentName,
}) => {
  const [stepIdx, setStepIdx] = React.useState<number>(0);
  const [targetRect, setTargetRect] = React.useState<DOMRect | null>(null);

  const step = SPOTLIGHT_STEPS[stepIdx];
  const isFirst = stepIdx === 0;
  const isLast = stepIdx === SPOTLIGHT_STEPS.length - 1;

  React.useEffect(() => {
    if (isOpen) {
      setStepIdx(0);
    }
  }, [isOpen]);

  const measureTarget = React.useCallback(() => {
    if (!isOpen || !step) return;
    const candidates = Array.from(
      document.querySelectorAll<HTMLElement>(`[data-tour-id="${step.tourId}"]`)
    );
    const visible = candidates.find((el) => {
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0;
    });
    if (visible) {
      visible.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      const rect = visible.getBoundingClientRect();
      setTargetRect(rect);
    } else {
      setTargetRect(null);
    }
  }, [isOpen, step]);

  React.useEffect(() => {
    if (!isOpen) return;
    measureTarget();
    const timer = setTimeout(measureTarget, 120);
    window.addEventListener('resize', measureTarget);
    window.addEventListener('scroll', measureTarget, true);
    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', measureTarget);
      window.removeEventListener('scroll', measureTarget, true);
    };
  }, [isOpen, stepIdx, measureTarget]);

  if (!isOpen || !step) return null;

  const pad = 6;
  const hasRect = Boolean(targetRect);
  const rx = targetRect ? Math.max(4, targetRect.left - pad) : 0;
  const ry = targetRect ? Math.max(4, targetRect.top - pad) : 0;
  const rw = targetRect ? targetRect.width + pad * 2 : 0;
  const rh = targetRect ? targetRect.height + pad * 2 : 0;

  // Position tooltip beside sidebar item on desktop or centred/above bottom nav on mobile
  const tooltipStyle: React.CSSProperties = (() => {
    if (!targetRect || typeof window === 'undefined') {
      return {
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
      };
    }
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const cardW = Math.min(360, vw - 24);

    // Desktop sidebar target on the left
    if (rx < 320 && vw >= 768) {
      const left = Math.min(rx + rw + 18, vw - cardW - 16);
      const top = Math.max(20, Math.min(ry - 24, vh - 310));
      return { top: `${top}px`, left: `${left}px`, width: `${cardW}px` };
    }
    // Bottom nav target on mobile
    if (ry > vh - 140) {
      return {
        bottom: `${vh - ry + 16}px`,
        left: '50%',
        transform: 'translateX(-50%)',
        width: `${cardW}px`,
      };
    }
    const top = ry + rh + 16 < vh - 260 ? ry + rh + 16 : Math.max(16, ry - 270);
    const left = Math.max(12, Math.min(rx, vw - cardW - 12));
    return { top: `${top}px`, left: `${left}px`, width: `${cardW}px` };
  })();

  const handleOpenHighlighted = () => {
    onNavigateScreen(step.screen);
    if (!isLast) {
      setStepIdx((i) => i + 1);
    } else {
      onClose();
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="SparkMinds AI Interactive Feature Tour"
      data-testid="feature-spotlight-tour"
      className="fixed inset-0 z-[95] pointer-events-none"
    >
      {/* Dimmed 4-Panel Backdrop leaving the highlighted real UI button clickable */}
      {hasRect ? (
        <>
          <div
            className="fixed left-0 right-0 top-0 bg-[#101B35]/65 backdrop-blur-[1.5px] pointer-events-auto transition-all duration-200"
            style={{ height: `${ry}px` }}
            onClick={onClose}
          />
          <div
            className="fixed left-0 right-0 bottom-0 bg-[#101B35]/65 backdrop-blur-[1.5px] pointer-events-auto transition-all duration-200"
            style={{ top: `${ry + rh}px` }}
            onClick={onClose}
          />
          <div
            className="fixed left-0 bg-[#101B35]/65 backdrop-blur-[1.5px] pointer-events-auto transition-all duration-200"
            style={{ top: `${ry}px`, height: `${rh}px`, width: `${rx}px` }}
            onClick={onClose}
          />
          <div
            className="fixed right-0 bg-[#101B35]/65 backdrop-blur-[1.5px] pointer-events-auto transition-all duration-200"
            style={{ top: `${ry}px`, height: `${rh}px`, left: `${rx + rw}px` }}
            onClick={onClose}
          />

          {/* Glowing Spotlight Highlight Ring around the ACTUAL button */}
          <div
            className="fixed rounded-2xl border-2 border-[#35D6E8] shadow-[0_0_0_4px_rgba(81,70,229,0.45),0_0_24px_rgba(53,214,232,0.55)] pointer-events-none transition-all duration-200 animate-pulse-glow"
            style={{
              left: `${rx}px`,
              top: `${ry}px`,
              width: `${rw}px`,
              height: `${rh}px`,
            }}
          />
        </>
      ) : (
        <div
          className="fixed inset-0 bg-[#101B35]/65 backdrop-blur-[2px] pointer-events-auto"
          onClick={onClose}
        />
      )}

      {/* Anchored Robot Guide Tooltip Card */}
      <div
        style={tooltipStyle}
        className="fixed z-[96] pointer-events-auto rounded-3xl bg-white border border-[#DCE2F5] shadow-2xl overflow-hidden animate-fade-in"
      >
        <div className="bg-gradient-to-r from-[#101B35] to-[#232B66] px-4 py-3 text-white flex items-center justify-between gap-2">
          <div className="flex items-center gap-2.5 min-w-0">
            <SparkRobotMascot mood={step.mood} size="xs" />
            <div className="min-w-0">
              <div className="text-[10px] font-extrabold uppercase tracking-wider text-[#35D6E8]">
                Feature Tour • {stepIdx + 1} of {SPOTLIGHT_STEPS.length}
              </div>
              <div className="text-xs font-extrabold truncate">
                {studentName ? `Hi ${studentName.split(' ')[0]} — Meet SparkMinds` : 'Sparky Guided Tour'}
              </div>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Skip Feature Tour"
            className="p-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-indigo-100 transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Thin Progress Bar */}
        <div className="h-1 bg-[#EEEAFE]">
          <div
            className="h-full bg-gradient-to-r from-[#5146E5] to-[#35D6E8] transition-all duration-300"
            style={{ width: `${((stepIdx + 1) / SPOTLIGHT_STEPS.length) * 100}%` }}
          />
        </div>

        <div className="p-4 sm:p-5 space-y-4">
          <div className="space-y-1.5">
            <h3 className="text-base font-extrabold text-[#101B35]">{step.title}</h3>
            <p className="text-xs sm:text-sm text-[#202943]/80 font-medium leading-relaxed">
              {step.description}
            </p>
          </div>

          <button
            type="button"
            onClick={handleOpenHighlighted}
            className="w-full py-2 px-3.5 rounded-xl bg-[#EEEAFE] hover:bg-[#e1d9fe] text-[#5146E5] text-xs font-extrabold transition text-center"
          >
            Try &ldquo;{step.actionLabel}&rdquo; now →
          </button>

          <div className="flex items-center justify-between gap-2 pt-1 border-t border-[#EEEAFE]">
            <button
              type="button"
              onClick={onClose}
              className="text-xs font-bold text-[#202943]/60 hover:text-[#101B35] px-2 py-1.5"
            >
              Skip Tour
            </button>

            <div className="flex items-center gap-1.5">
              {!isFirst && (
                <button
                  type="button"
                  onClick={() => setStepIdx((i) => Math.max(0, i - 1))}
                  className="inline-flex items-center gap-1 px-3 py-2 rounded-xl border border-[#DCE2F5] bg-white hover:bg-[#F6F7FC] text-[#202943] text-xs font-extrabold transition"
                >
                  <ArrowLeft className="w-3.5 h-3.5" />
                  <span>Back</span>
                </button>
              )}
              {isLast ? (
                <button
                  type="button"
                  onClick={() => {
                    onNavigateScreen('dashboard');
                    onClose();
                  }}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#5146E5] hover:bg-[#4338CA] text-white text-xs font-extrabold shadow-sm transition"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Finish</span>
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => {
                    const nextStep = SPOTLIGHT_STEPS[stepIdx + 1];
                    setStepIdx((i) => i + 1);
                    if (nextStep) {
                      onNavigateScreen(nextStep.screen);
                    }
                  }}
                  className="inline-flex items-center gap-1 px-4 py-2 rounded-xl bg-[#5146E5] hover:bg-[#4338CA] text-white text-xs font-extrabold shadow-sm transition"
                >
                  <span>Next</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
