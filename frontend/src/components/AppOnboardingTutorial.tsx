import React from 'react';
import {
  Sparkles,
  ArrowRight,
  ArrowLeft,
  X,
  LayoutDashboard,
  Bot,
  CalendarCheck,
  FileText,
  Trophy,
  Layers,
  TrendingUp,
  CheckCircle2,
  RotateCcw,
} from 'lucide-react';
import { ScreenId } from '../design-system/tokens';

interface AppOnboardingTutorialProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigateScreen?: (screen: ScreenId) => void;
  studentName?: string;
  grade?: number;
  board?: string;
}

interface TutorialStep {
  id: string;
  featureName: string;
  screenId: ScreenId;
  headline: string;
  instruction: string;
  tryPrompt: string;
  tryOptions: { label: string; feedback: string }[];
  icon: React.ReactNode;
}

/**
 * SparkMinds AI — Original Duolingo-Inspired 7-Feature Interactive Guided Tour.
 * - One friendly instruction at a time (never cluttered)
 * - Covers Dashboard, AI Learning Buddy, Study Planner, Homework, Exam Prep, Smart Revision, Progress Tracking
 * - Interactive mini-try on every step with encouraging feedback + direct "Open Feature" link
 * - Zero fake streaks, zero fake stats, simple Back / Next / Skip / Replay + keyboard navigation
 */
export const AppOnboardingTutorial: React.FC<AppOnboardingTutorialProps> = ({
  isOpen,
  onClose,
  onNavigateScreen,
  studentName = '',
  grade = 7,
  board = 'CBSE',
}) => {
  const [stepIdx, setStepIdx] = React.useState<number>(0);
  const [selectedTryIdx, setSelectedTryIdx] = React.useState<Record<number, number>>({});

  const firstName =
    studentName &&
    !['Aarav Sharma', 'Ananya Reddy', 'Diya Nair', 'Karthik Rajan', 'Riya Verma', 'Student Learner'].includes(
      studentName
    )
      ? studentName.split(' ')[0]
      : '';

  const steps: TutorialStep[] = React.useMemo(
    () => [
      {
        id: 'dashboard',
        featureName: 'Dashboard',
        screenId: 'dashboard',
        headline: firstName ? `Welcome, ${firstName}! Let's get started.` : "Welcome! Let's get started.",
        instruction: `Your Dashboard shows today's goal, next lesson, and tasks for Grade ${grade} (${board}).`,
        tryPrompt: 'Tap a focus for today to try it:',
        tryOptions: [
          {
            label: 'Learn a new topic',
            feedback: "Great choice! Your Dashboard puts today's next lesson right at the top.",
          },
          {
            label: 'Finish homework first',
            feedback: 'Smart plan! Your Dashboard highlights upcoming homework so nothing gets missed.',
          },
        ],
        icon: <LayoutDashboard className="w-6 h-6 text-[#00E5FF]" />,
      },
      {
        id: 'buddy',
        featureName: 'AI Learning Buddy',
        screenId: 'buddy',
        headline: 'Ask your AI Learning Buddy anything.',
        instruction: 'Stuck on a concept? Your personal tutor explains step by step in your preferred language.',
        tryPrompt: 'Try tapping how you like concepts explained:',
        tryOptions: [
          {
            label: 'Step-by-step hints',
            feedback: "Awesome! AI Buddy guides you one clear step at a time instead of confusing walls of text.",
          },
          {
            label: 'Simple real-life example',
            feedback: 'Great job! You can ask unlimited follow-ups or upload a homework photo anytime.',
          },
        ],
        icon: <Bot className="w-6 h-6 text-[#00E5FF]" />,
      },
      {
        id: 'plan',
        featureName: 'Study Planner',
        screenId: 'plan',
        headline: 'Plan your day without stress.',
        instruction: 'Smart Study Planner fits short study blocks around school, tuition, hobbies, and rest.',
        tryPrompt: 'Pick when you study best:',
        tryOptions: [
          {
            label: 'Morning focus',
            feedback: 'Nice! Your Study Planner adapts to your real daily availability.',
          },
          {
            label: 'Evening study',
            feedback: 'Got it! It automatically avoids clashes with your classes and sleep time.',
          },
        ],
        icon: <CalendarCheck className="w-6 h-6 text-[#00E5FF]" />,
      },
      {
        id: 'homework',
        featureName: 'Homework',
        screenId: 'homework',
        headline: 'Keep homework simple and organized.',
        instruction: 'Track due dates, check off tasks, and jump straight to AI Buddy for hints when needed.',
        tryPrompt: 'Tap to see how a homework task feels:',
        tryOptions: [
          {
            label: 'Mark a task complete',
            feedback: "Done! Every real task you finish updates your progress and streak.",
          },
          {
            label: 'Get a step-by-step hint',
            feedback: "Helpful! One tap opens that exact question inside your AI Learning Buddy.",
          },
        ],
        icon: <FileText className="w-6 h-6 text-[#00E5FF]" />,
      },
      {
        id: 'exams',
        featureName: 'Exam Preparation',
        screenId: 'exams',
        headline: 'Practice with adaptive quizzes.',
        instruction: 'Test yourself with MCQs, fill-in-the-blanks, short answers, and timed mock exams.',
        tryPrompt: 'Choose your starting comfort level:',
        tryOptions: [
          {
            label: 'Quick 4-question check',
            feedback: "Excellent! Quick checks spot weak topics early so you know what to review.",
          },
          {
            label: 'Full chapter practice',
            feedback: "You're ready! Difficulty adapts automatically to your real performance.",
          },
        ],
        icon: <Trophy className="w-6 h-6 text-[#00E5FF]" />,
      },
      {
        id: 'revision',
        featureName: 'Smart Revision',
        screenId: 'practice',
        headline: 'Remember more in less time.',
        instruction: 'Smart Revision brings back tricky topics with quick recall cards right before you forget.',
        tryPrompt: 'Tap to flip a quick memory check:',
        tryOptions: [
          {
            label: 'Why does spaced revision work?',
            feedback: 'Revisiting a topic at growing intervals locks it into long-term memory!',
          },
        ],
        icon: <Layers className="w-6 h-6 text-[#00E5FF]" />,
      },
      {
        id: 'progress',
        featureName: 'Progress Tracking',
        screenId: 'progress',
        headline: "You're all set! Watch your real growth.",
        instruction: 'Track your real accuracy, streaks, learning gaps, and year-by-year progress honestly.',
        tryPrompt: 'Ready to begin your learning journey?',
        tryOptions: [
          {
            label: "Yes — let's start learning!",
            feedback: "Excellent work! You can replay this tour anytime from the Tour button.",
          },
        ],
        icon: <TrendingUp className="w-6 h-6 text-[#00E5FF]" />,
      },
    ],
    [firstName, grade, board]
  );

  // Reset to step 0 whenever reopened
  React.useEffect(() => {
    if (isOpen) {
      setStepIdx(0);
      setSelectedTryIdx({});
    }
  }, [isOpen]);

  // Keyboard navigation (ArrowRight, ArrowLeft, Escape)
  React.useEffect(() => {
    if (!isOpen) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      } else if (e.key === 'ArrowRight') {
        setStepIdx((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
      } else if (e.key === 'ArrowLeft') {
        setStepIdx((prev) => (prev > 0 ? prev - 1 : prev));
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [isOpen, onClose, steps.length]);

  if (!isOpen) return null;

  const current = steps[stepIdx];
  const isFirst = stepIdx === 0;
  const isLast = stepIdx === steps.length - 1;
  const chosenOption =
    selectedTryIdx[stepIdx] !== undefined ? current.tryOptions[selectedTryIdx[stepIdx]] : null;

  const handleTryScreen = () => {
    onClose();
    if (onNavigateScreen) {
      onNavigateScreen(current.screenId);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="SparkMinds AI Interactive Guided Tour"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0A192F]/75 backdrop-blur-sm animate-fade-in"
    >
      <div className="w-full max-w-lg rounded-3xl bg-white border border-slate-200 shadow-2xl overflow-hidden flex flex-col">
        {/* Top Progress Header */}
        <div className="px-6 pt-5 pb-4 bg-[#0A192F] text-white space-y-3">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-white/10 border border-[#00E5FF]/40 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-[#00E5FF]" />
              </div>
              <span className="text-xs font-extrabold tracking-wide text-[#00E5FF]">
                Step {stepIdx + 1} of {steps.length} • {current.featureName}
              </span>
            </div>

            <div className="flex items-center gap-1.5">
              {stepIdx > 0 && (
                <button
                  type="button"
                  onClick={() => {
                    setStepIdx(0);
                    setSelectedTryIdx({});
                  }}
                  className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-[11px] font-bold text-slate-200 transition"
                  title="Replay from Step 1"
                >
                  <RotateCcw className="w-3.5 h-3.5 text-[#00E5FF]" />
                  <span>Replay</span>
                </button>
              )}
              <button
                type="button"
                onClick={onClose}
                className="p-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-slate-300 hover:text-white transition"
                aria-label="Skip and close tour"
                title="Close"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Segmented Duolingo-style Progress Bar */}
          <div className="grid grid-cols-7 gap-1.5" aria-label={`Progress: step ${stepIdx + 1} of ${steps.length}`}>
            {steps.map((s, i) => (
              <button
                key={s.id}
                type="button"
                onClick={() => setStepIdx(i)}
                aria-label={`Jump to ${s.featureName}`}
                className={`h-2 rounded-full transition-all ${
                  i === stepIdx
                    ? 'bg-[#00E5FF]'
                    : i < stepIdx
                      ? 'bg-emerald-400'
                      : 'bg-white/15 hover:bg-white/25'
                }`}
              />
            ))}
          </div>
        </div>

        {/* Single Focused Instruction Body */}
        <div key={current.id} className="p-6 space-y-5 animate-fade-in">
          <div className="flex items-start gap-3.5">
            <div className="w-12 h-12 rounded-2xl bg-[#0A192F] flex items-center justify-center shrink-0 shadow-sm">
              {current.icon}
            </div>
            <div className="space-y-1">
              <h2 className="text-lg sm:text-xl font-extrabold text-[#0A192F] leading-snug">
                {current.headline}
              </h2>
              <p className="text-sm text-slate-600 font-medium leading-relaxed">
                {current.instruction}
              </p>
            </div>
          </div>

          {/* Interactive Mini-Try Box */}
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
            <div className="text-xs font-extrabold text-slate-700">{current.tryPrompt}</div>
            <div className="grid gap-2">
              {current.tryOptions.map((opt, idx) => {
                const active = selectedTryIdx[stepIdx] === idx;
                return (
                  <button
                    key={opt.label}
                    type="button"
                    onClick={() => setSelectedTryIdx((prev) => ({ ...prev, [stepIdx]: idx }))}
                    className={`w-full text-left px-4 py-3 rounded-xl border-2 text-sm font-bold transition flex items-center justify-between gap-2 min-h-[46px] ${
                      active
                        ? 'border-[#0A192F] bg-[#0A192F] text-white'
                        : 'border-slate-200 bg-white hover:border-[#00B8D4] text-slate-800'
                    }`}
                  >
                    <span>{opt.label}</span>
                    {active && <CheckCircle2 className="w-4 h-4 text-[#00E5FF] shrink-0" />}
                  </button>
                );
              })}
            </div>

            {chosenOption && (
              <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-900 flex items-start gap-2 animate-spark-celebrate">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span>{chosenOption.feedback}</span>
              </div>
            )}
          </div>

          {onNavigateScreen && !isLast && (
            <button
              type="button"
              onClick={handleTryScreen}
              className="text-xs font-extrabold text-[#0A192F] hover:text-[#00B8D4] inline-flex items-center gap-1 transition"
            >
              <span>Open {current.featureName} now</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Clean Bottom Controls: Back, Skip, Primary Next */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <button
              type="button"
              disabled={isFirst}
              onClick={() => setStepIdx((p) => Math.max(0, p - 1))}
              className={`inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-extrabold border transition min-h-[44px] ${
                isFirst
                  ? 'border-slate-200 text-slate-400 cursor-not-allowed bg-white'
                  : 'border-slate-300 bg-white hover:bg-slate-100 text-[#0A192F]'
              }`}
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back</span>
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-2.5 rounded-xl text-xs font-bold text-slate-500 hover:text-[#0A192F] transition min-h-[44px]"
            >
              Skip
            </button>
          </div>

          <button
            type="button"
            onClick={() => {
              if (isLast) {
                onClose();
                if (onNavigateScreen) onNavigateScreen('dashboard');
              } else {
                setStepIdx((p) => p + 1);
              }
            }}
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-[#0A192F] hover:bg-[#112240] text-[#00E5FF] text-sm font-extrabold shadow-sm transition min-h-[44px]"
          >
            <span>{isLast ? 'Start Learning' : 'Next'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
