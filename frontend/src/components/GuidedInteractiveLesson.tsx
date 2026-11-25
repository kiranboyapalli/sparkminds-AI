import React from 'react';
import {
  ArrowLeft,
  ArrowRight,
  ArrowUp,
  ArrowDown,
  BookOpen,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Flame,
  Lightbulb,
  RefreshCw,
  Sparkles,
  Trophy,
} from 'lucide-react';
import { OnboardingState } from '../onboarding/SevenStepOnboarding';
import { getSubjectsForGradeAndBoardFrontend } from '../curriculum/curriculumData';
import { HelpTip } from './HelpTip';
import { SparkRobotMascot } from './SparkRobotMascot';
import { RichMathMarkdown, cleanMathText } from '../utils/formatMathText';

interface HotspotItem {
  id: string;
  label: string;
  x: number;
  y: number;
  summary: string;
}

interface LessonStep {
  step_id: string;
  step_type:
    | 'CONCEPT'
    | 'INTERACTIVE_DIAGRAM'
    | 'MCQ'
    | 'MATCH_PAIRS'
    | 'FILL_IN_BLANK'
    | 'ORDER_STEPS'
    | 'TRUE_FALSE'
    | 'SHORT_ANSWER';
  title: string;
  short_text?: string;
  detailed_explanation?: string;
  key_takeaway?: string;
  prompt?: string;
  diagram_kind?: string;
  hotspots?: HotspotItem[];
  encouragement?: string;
  options?: string[];
  correct_answer?: string;
  pairs?: { left: string; right: string }[];
  accepted_answers?: string[];
  hint?: string;
  correct_order?: string[];
  rubric_keywords?: string[];
  sample_answer?: string;
  explanation?: string;
}

interface GuidedLessonPayload {
  lesson_id: string;
  subject: string;
  topic: string;
  grade: number;
  board: string;
  difficulty: string;
  estimated_minutes: number;
  learning_objective: string;
  steps: LessonStep[];
  generation_source: string;
}

interface CompletionResult {
  accuracy_percentage: number;
  correct_count: number;
  total_interactive_steps: number;
  points_earned: number;
  encouragement: string;
  gamification?: {
    current_streak_days?: number;
    total_points?: number;
    level?: number;
    newly_awarded_badges?: { title: string; description: string }[];
  };
}

interface GuidedInteractiveLessonProps {
  onboarding: OnboardingState;
  initialSubject?: string;
  initialTopic?: string;
  onAskBuddy?: (question: string, subject: string) => void;
}

const POSITIVE_PHRASES = [
  'Great job!',
  "You're getting better!",
  'Excellent work! Keep going.',
  'Spot on! Ready for the next step?',
];

export const GuidedInteractiveLesson: React.FC<GuidedInteractiveLessonProps> = ({
  onboarding,
  initialSubject,
  initialTopic,
  onAskBuddy,
}) => {
  const subjects = React.useMemo(
    () =>
      getSubjectsForGradeAndBoardFrontend(
        onboarding.grade,
        onboarding.board,
        onboarding.stateName
      ),
    [onboarding.grade, onboarding.board, onboarding.stateName]
  );

  const [selectedSubject, setSelectedSubject] = React.useState<string>(
    initialSubject || subjects[0]?.name || 'Mathematics'
  );
  const activeSubjectObj = React.useMemo(
    () => subjects.find((s) => s.name === selectedSubject) || subjects[0],
    [subjects, selectedSubject]
  );
  const [selectedTopic, setSelectedTopic] = React.useState<string>(
    initialTopic || activeSubjectObj?.topics?.[0] || 'Core Concepts'
  );

  const [lesson, setLesson] = React.useState<GuidedLessonPayload | null>(null);
  const [loading, setLoading] = React.useState<boolean>(false);
  const [error, setError] = React.useState<string>('');
  const [sessionExpiredError, setSessionExpiredError] = React.useState<boolean>(false);
  const [stepIdx, setStepIdx] = React.useState<number>(0);

  // Per-step interactive state
  const [showDetailedConcept, setShowDetailedConcept] = React.useState<boolean>(false);
  const [exploredHotspots, setExploredHotspots] = React.useState<string[]>([]);
  const [activeHotspot, setActiveHotspot] = React.useState<HotspotItem | null>(null);

  const [selectedOption, setSelectedOption] = React.useState<string>('');
  const [textInput, setTextInput] = React.useState<string>('');
  const [showHint, setShowHint] = React.useState<boolean>(false);

  // Match-the-pairs state
  const [selectedLeft, setSelectedLeft] = React.useState<string | null>(null);
  const [matchedPairs, setMatchedPairs] = React.useState<Record<string, string>>({});
  const [shuffledRights, setShuffledRights] = React.useState<string[]>([]);

  // Order-steps state
  const [orderedItems, setOrderedItems] = React.useState<string[]>([]);

  // Step feedback & real accuracy tracking
  const [stepFeedback, setStepFeedback] = React.useState<{
    correct: boolean;
    headline: string;
    detail: string;
  } | null>(null);
  const [scoredSteps, setScoredSteps] = React.useState<Record<string, boolean>>({});
  const [completion, setCompletion] = React.useState<CompletionResult | null>(null);
  const [savingResult, setSavingResult] = React.useState<boolean>(false);

  React.useEffect(() => {
    if (activeSubjectObj && !activeSubjectObj.topics.includes(selectedTopic)) {
      setSelectedTopic(activeSubjectObj.topics[0] || 'Core Concepts');
    }
  }, [activeSubjectObj, selectedTopic]);

  const currentStep = lesson ? lesson.steps[stepIdx] : null;

  // Reset per-step controls whenever step changes
  React.useEffect(() => {
    if (!currentStep) return;
    setShowDetailedConcept(false);
    setExploredHotspots([]);
    setActiveHotspot(null);
    setSelectedOption('');
    setTextInput('');
    setShowHint(false);
    setSelectedLeft(null);
    setMatchedPairs({});
    setStepFeedback(null);

    if (currentStep.step_type === 'MATCH_PAIRS' && currentStep.pairs) {
      const rights = currentStep.pairs.map((p) => p.right);
      // Deterministic gentle shuffle (rotate by 1 so it isn't trivially aligned)
      const rotated = rights.length > 1 ? [...rights.slice(1), rights[0]] : rights;
      setShuffledRights(rotated);
    }
    if (currentStep.step_type === 'ORDER_STEPS' && currentStep.correct_order) {
      const items = [...currentStep.correct_order];
      const scrambled = items.length > 1 ? [...items.slice(1), items[0]] : items;
      setOrderedItems(scrambled);
    }
  }, [stepIdx, lesson?.lesson_id, currentStep?.step_id]);

  const handleStartLesson = async (subj?: string, top?: string) => {
    const targetSubj = subj || selectedSubject;
    const targetTop = top || selectedTopic;
    setLoading(true);
    setError('');
    setSessionExpiredError(false);
    setCompletion(null);
    setScoredSteps({});
    setStepIdx(0);
    try {
      const res = await fetch('/api/agents/lessons/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: onboarding.studentId,
          subject: targetSubj,
          topic: targetTop,
          preferred_language: onboarding.preferredExplanationLanguage,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        if (res.status === 401) {
          setSessionExpiredError(true);
          setError('Your session has ended. Please sign in again to continue your guided lesson.');
        } else {
          setError(data.detail || 'Could not load your interactive lesson right now.');
        }
        return;
      }
      setLesson(data);
    } catch {
      setError('Unable to reach the server. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  const recordStepOutcome = (stepId: string, isCorrect: boolean) => {
    setScoredSteps((prev) => {
      // Preserve first genuine attempt accuracy if already answered, or update on retry
      if (prev[stepId] === true) return prev;
      return { ...prev, [stepId]: isCorrect };
    });
  };

  const checkCurrentActivity = () => {
    if (!currentStep) return;
    const positive = POSITIVE_PHRASES[stepIdx % POSITIVE_PHRASES.length];

    if (currentStep.step_type === 'MCQ' || currentStep.step_type === 'TRUE_FALSE') {
      if (!selectedOption) return;
      const isCorrect =
        selectedOption.trim().toLowerCase() === (currentStep.correct_answer || '').trim().toLowerCase();
      recordStepOutcome(currentStep.step_id, isCorrect);
      setStepFeedback({
        correct: isCorrect,
        headline: isCorrect ? positive : "Almost there! Let's try once more.",
        detail: isCorrect
          ? currentStep.explanation || 'You understood that concept clearly.'
          : currentStep.explanation || 'Read the concept clue gently and pick another option.',
      });
      return;
    }

    if (currentStep.step_type === 'FILL_IN_BLANK') {
      const clean = textInput.trim().toLowerCase();
      if (!clean) return;
      const accepted = (currentStep.accepted_answers || []).map((a) => a.toLowerCase().trim());
      const isCorrect = accepted.some((a) => clean === a || clean.includes(a));
      recordStepOutcome(currentStep.step_id, isCorrect);
      setStepFeedback({
        correct: isCorrect,
        headline: isCorrect ? positive : "Let's try once more.",
        detail: isCorrect
          ? currentStep.explanation || 'Spot on!'
          : `${currentStep.hint ? `Hint: ${currentStep.hint} ` : ''}${currentStep.explanation || ''}`,
      });
      return;
    }

    if (currentStep.step_type === 'ORDER_STEPS') {
      const target = currentStep.correct_order || [];
      const isCorrect =
        orderedItems.length === target.length &&
        orderedItems.every((item, i) => item === target[i]);
      recordStepOutcome(currentStep.step_id, isCorrect);
      setStepFeedback({
        correct: isCorrect,
        headline: isCorrect ? positive : "Almost there! Adjust the order and check again.",
        detail: isCorrect
          ? currentStep.explanation || 'Every step is in the exact right sequence.'
          : currentStep.explanation || 'Think about what you need to know first before solving.',
      });
      return;
    }

    if (currentStep.step_type === 'MATCH_PAIRS') {
      const pairs = currentStep.pairs || [];
      if (Object.keys(matchedPairs).length < pairs.length) return;
      const isCorrect = pairs.every((p) => matchedPairs[p.left] === p.right);
      recordStepOutcome(currentStep.step_id, isCorrect);
      setStepFeedback({
        correct: isCorrect,
        headline: isCorrect ? positive : "Almost there! Try matching the pairs once more.",
        detail: currentStep.explanation || 'Matching each term to its meaning builds quick recall.',
      });
      return;
    }

    if (currentStep.step_type === 'SHORT_ANSWER') {
      const clean = textInput.trim().toLowerCase();
      if (clean.length < 4) return;
      const words = clean.split(/\s+/).filter(Boolean);
      const keywords = (currentStep.rubric_keywords || []).map((k) => k.toLowerCase());
      const matched = keywords.some((k) => clean.includes(k));
      const isCorrect = words.length >= 3 && (keywords.length === 0 || matched);
      recordStepOutcome(currentStep.step_id, isCorrect);
      setStepFeedback({
        correct: isCorrect,
        headline: isCorrect ? positive : "Good effort! Add a little more detail.",
        detail: currentStep.sample_answer
          ? `Example answer: "${currentStep.sample_answer}" ${currentStep.explanation || ''}`
          : currentStep.explanation || 'Writing in your own words helps lock in understanding.',
      });
    }
  };

  const handleFinishLesson = async () => {
    if (!lesson) return;
    setSavingResult(true);
    const interactiveSteps = lesson.steps.filter(
      (s) => s.step_type !== 'CONCEPT' && s.step_type !== 'INTERACTIVE_DIAGRAM'
    );
    const total = Math.max(1, interactiveSteps.length);
    const correct = interactiveSteps.filter((s) => scoredSteps[s.step_id] === true).length;

    try {
      const res = await fetch('/api/agents/lessons/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: onboarding.studentId,
          lesson_id: lesson.lesson_id,
          subject: lesson.subject,
          topic: lesson.topic,
          correct_count: correct,
          total_interactive_steps: total,
        }),
      });
      if (res.ok) {
        const data: CompletionResult = await res.json();
        setCompletion(data);
      } else {
        setCompletion({
          accuracy_percentage: Math.round((correct / total) * 100),
          correct_count: correct,
          total_interactive_steps: total,
          points_earned: 0,
          encouragement: "You've completed this lesson!",
        });
      }
    } catch {
      setCompletion({
        accuracy_percentage: Math.round((correct / total) * 100),
        correct_count: correct,
        total_interactive_steps: total,
        points_earned: 0,
        encouragement: "You've completed this lesson!",
      });
    } finally {
      setSavingResult(false);
    }
  };

  const moveOrderItem = (index: number, delta: -1 | 1) => {
    const nextIdx = index + delta;
    if (nextIdx < 0 || nextIdx >= orderedItems.length) return;
    const copy = [...orderedItems];
    [copy[index], copy[nextIdx]] = [copy[nextIdx], copy[index]];
    setOrderedItems(copy);
    setStepFeedback(null);
  };

  // ------------------------------------------------------------------
  // VIEW 1: CLEAN STEP-BY-STEP SUBJECT & TOPIC SELECTOR
  // ------------------------------------------------------------------
  if (!lesson) {
    return (
      <div className="eduspark-card rounded-3xl p-6 md:p-7 space-y-6 animate-fade-in">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3.5">
            <SparkRobotMascot mood="guiding" size="sm" />
            <div className="space-y-1">
              <span className="inline-flex items-center gap-1.5 text-[11px] font-extrabold uppercase tracking-wider text-[#5146E5]">
                <Sparkles className="w-3.5 h-3.5" />
                Guided Interactive Lessons
              </span>
              <h2 className="text-xl md:text-2xl font-extrabold text-[#101B35] tracking-tight">
                First, choose your subject.
              </h2>
              <p className="text-xs text-[#202943]/75 font-medium">
                Short concepts, interactive visuals, and quick checks adapted for Grade {onboarding.grade}.
              </p>
            </div>
          </div>
          <HelpTip
            title="How Guided Lessons Work"
            text="Each lesson teaches one small idea at a time, lets you explore an interactive visual or activity, gives gentle instant feedback, and saves your real score and streak."
          />
        </div>

        {/* Step A: Subject Pills */}
        <div className="flex flex-wrap gap-2">
          {subjects.map((sub) => {
            const active = sub.name === selectedSubject;
            return (
              <button
                key={sub.code}
                type="button"
                onClick={() => {
                  setSelectedSubject(sub.name);
                  setSelectedTopic(sub.topics[0] || 'Core Concepts');
                }}
                className={`px-4 py-2.5 rounded-xl text-xs font-extrabold border-2 transition min-h-[44px] ${
                  active
                    ? 'bg-[#5146E5] border-[#5146E5] text-white shadow-sm'
                    : 'bg-white border-[#DCE2F5] hover:border-[#5146E5] text-[#202943]'
                }`}
              >
                {sub.name}
              </button>
            );
          })}
        </div>

        {/* Step B: Topic Cards */}
        {activeSubjectObj && (
          <div className="space-y-3 pt-2 border-t border-[#EEEAFE]">
            <h3 className="text-sm font-extrabold text-[#101B35]">
              Great! Now select a topic in {activeSubjectObj.name}:
            </h3>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
              {activeSubjectObj.topics.map((topic) => {
                const active = topic === selectedTopic;
                return (
                  <button
                    key={topic}
                    type="button"
                    onClick={() => setSelectedTopic(topic)}
                    className={`p-3.5 rounded-2xl border-2 text-left transition min-h-[56px] flex items-center justify-between gap-2 ${
                      active
                        ? 'border-[#5146E5] bg-[#EEEAFE] text-[#101B35]'
                        : 'border-[#DCE2F5] bg-white hover:border-[#5146E5] text-[#202943]'
                    }`}
                  >
                    <span className="text-xs font-extrabold leading-snug">{topic}</span>
                    {active && <CheckCircle2 className="w-4 h-4 text-[#5146E5] shrink-0" />}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {loading && (
          <div className="p-5 rounded-2xl bg-[#F7F9FF] border border-[#C2D4F8] space-y-3 animate-fade-in">
            <div className="flex items-center gap-2.5 text-xs font-extrabold text-[#5146E5]">
              <Sparkles className="w-4 h-4 animate-pulse" />
              <span>Sparky is building your interactive Grade {onboarding.grade} lesson on {selectedTopic}...</span>
            </div>
            <div className="h-3 w-3/4 rounded-full spark-skeleton" />
            <div className="h-3 w-1/2 rounded-full spark-skeleton" />
          </div>
        )}

        {error && (
          <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 flex flex-wrap items-center justify-between gap-3 text-xs font-bold text-rose-800">
            <span>{error}</span>
            {sessionExpiredError ? (
              <button
                type="button"
                onClick={() => window.dispatchEvent(new CustomEvent('sparkminds-session-expired'))}
                className="px-3.5 py-2 rounded-xl bg-[#5146E5] hover:bg-[#4338CA] text-white text-xs font-extrabold shrink-0 transition"
              >
                Sign In Again →
              </button>
            ) : (
              <button
                type="button"
                onClick={() => handleStartLesson()}
                className="px-3 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-extrabold shrink-0 transition"
              >
                Retry
              </button>
            )}
          </div>
        )}

        <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
          <div className="text-xs text-[#202943]/70 font-semibold">
            Selected: <strong className="text-[#101B35]">{selectedSubject}</strong> •{' '}
            <strong className="text-[#5146E5]">{selectedTopic}</strong>
          </div>
          <div className="flex flex-wrap gap-2">
            {onAskBuddy && (
              <button
                type="button"
                onClick={() =>
                  onAskBuddy(
                    `Explain ${selectedTopic} in ${selectedSubject} step by step with a visual example.`,
                    selectedSubject
                  )
                }
                className="px-4 py-2.5 rounded-xl border border-[#DCE2F5] bg-white hover:bg-[#EEEAFE] text-[#101B35] text-xs font-extrabold transition min-h-[44px]"
              >
                Ask Sparky Instead
              </button>
            )}
            <button
              type="button"
              disabled={loading}
              onClick={() => handleStartLesson()}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-[#5146E5] hover:bg-[#4338CA] text-white text-sm font-extrabold shadow-sm disabled:opacity-50 transition min-h-[44px]"
            >
              <span>{loading ? 'Preparing lesson...' : 'Start Interactive Lesson'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ------------------------------------------------------------------
  // VIEW 2: REAL COMPLETION CELEBRATION SCREEN
  // ------------------------------------------------------------------
  if (completion) {
    return (
      <div className="eduspark-card rounded-3xl p-6 md:p-8 text-center space-y-6 animate-spark-celebrate">
        <div className="flex justify-center">
          <SparkRobotMascot mood="celebrating" size="lg" />
        </div>
        <div className="space-y-1.5 max-w-md mx-auto">
          <span className="text-xs font-extrabold uppercase tracking-wider text-[#5146E5]">
            Lesson Complete
          </span>
          <h2 className="text-2xl font-extrabold text-[#101B35]">
            You&apos;ve completed {lesson.topic}!
          </h2>
          <p className="text-sm text-[#202943]/80 font-medium">{completion.encouragement}</p>
        </div>

        <div className="grid grid-cols-3 gap-3 max-w-lg mx-auto">
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
            <div className="text-[11px] font-bold text-slate-500">Accuracy</div>
            <div className="text-xl font-extrabold text-[#101B35] mt-0.5">
              {completion.accuracy_percentage}%
            </div>
            <div className="text-[10px] text-slate-500">
              {completion.correct_count} / {completion.total_interactive_steps} correct
            </div>
          </div>
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
            <div className="text-[11px] font-bold text-slate-500">Points Earned</div>
            <div className="text-xl font-extrabold text-emerald-700 mt-0.5">
              +{completion.points_earned}
            </div>
            <div className="text-[10px] text-slate-500">Saved to profile</div>
          </div>
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
            <div className="text-[11px] font-bold text-slate-500">Real Streak</div>
            <div className="text-xl font-extrabold text-amber-600 mt-0.5 inline-flex items-center gap-1">
              <Flame className="w-4 h-4" />
              <span>{completion.gamification?.current_streak_days ?? 1}d</span>
            </div>
            <div className="text-[10px] text-slate-500">Active learning</div>
          </div>
        </div>

        {completion.gamification?.newly_awarded_badges &&
          completion.gamification.newly_awarded_badges.length > 0 && (
            <div className="max-w-md mx-auto p-3.5 rounded-2xl bg-amber-50 border border-amber-200 text-xs font-bold text-amber-900">
              New Badge Unlocked:{' '}
              {completion.gamification.newly_awarded_badges.map((b) => b.title).join(', ')}
            </div>
          )}

        <div className="flex flex-wrap justify-center gap-3 pt-2">
          <button
            type="button"
            onClick={() => {
              setLesson(null);
              setCompletion(null);
            }}
            className="px-5 py-2.5 rounded-xl bg-[#101B35] hover:bg-[#1B2654] text-[#35D6E8] text-sm font-extrabold transition min-h-[44px]"
          >
            Choose Next Topic
          </button>
          <button
            type="button"
            onClick={() => handleStartLesson(lesson.subject, lesson.topic)}
            className="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-xl border border-slate-300 bg-white hover:bg-slate-50 text-[#101B35] text-sm font-extrabold transition min-h-[44px]"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Practice Again</span>
          </button>
        </div>
      </div>
    );
  }

  // ------------------------------------------------------------------
  // VIEW 3: ONE-STEP-AT-A-TIME INTERACTIVE LESSON RUNNER
  // ------------------------------------------------------------------
  const isLastStep = stepIdx === lesson.steps.length - 1;
  const progressPct = Math.round(((stepIdx + 1) / lesson.steps.length) * 100);
  const needsCheck =
    currentStep &&
    currentStep.step_type !== 'CONCEPT' &&
    currentStep.step_type !== 'INTERACTIVE_DIAGRAM';

  return (
    <div className="eduspark-card rounded-3xl overflow-hidden animate-fade-in">
      {/* Clean Navy Top Progress Header */}
      <div className="bg-[#101B35] text-white px-6 py-4 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <div className="flex items-center gap-2 text-[11px] font-extrabold text-[#35D6E8] uppercase tracking-wider">
              <span>{lesson.subject}</span>
              <span>•</span>
              <span>{lesson.difficulty} Level</span>
              <span>•</span>
              <span>
                Step {stepIdx + 1} of {lesson.steps.length}
              </span>
            </div>
            <h2 className="text-base sm:text-lg font-extrabold text-white">{lesson.topic}</h2>
          </div>

          <button
            type="button"
            onClick={() => setLesson(null)}
            className="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-xs font-bold text-slate-200 transition"
          >
            Change Topic
          </button>
        </div>

        {/* Smooth Step Pills & Progress Bar */}
        <div
          className="flex items-center gap-1.5"
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={progressPct}
          aria-label={`Lesson progress ${progressPct}%`}
        >
          {lesson.steps.map((s, idx) => (
            <div
              key={s.step_id || idx}
              className={`h-2 flex-1 rounded-full transition-all duration-300 ${
                idx < stepIdx
                  ? 'bg-emerald-400'
                  : idx === stepIdx
                    ? 'bg-[#35D6E8]'
                    : 'bg-white/15'
              }`}
            />
          ))}
        </div>
        <p className="text-xs text-slate-300 font-medium">
          <strong className="text-white">Goal:</strong> {cleanMathText(lesson.learning_objective)}
        </p>
      </div>

      {/* Focused Step Card Body */}
      {currentStep && (
        <div key={currentStep.step_id} className="p-6 md:p-7 space-y-5 animate-fade-in">
          <h3 className="text-lg md:text-xl font-extrabold text-[#101B35]">
            {cleanMathText(currentStep.title)}
          </h3>

          {/* 1. CONCEPT STEP */}
          {currentStep.step_type === 'CONCEPT' && (
            <div className="space-y-4">
              {currentStep.short_text && (
                <RichMathMarkdown
                  text={currentStep.short_text}
                  className="text-sm sm:text-base text-slate-700 font-medium"
                />
              )}

              {currentStep.key_takeaway && (
                <div className="p-4 rounded-2xl bg-[#EAF0FF] border border-[#C2D4F8] flex items-start gap-2.5 text-sm font-bold text-[#101B35]">
                  <Lightbulb className="w-5 h-5 text-[#5146E5] shrink-0 mt-0.5" />
                  <span>{cleanMathText(currentStep.key_takeaway)}</span>
                </div>
              )}

              {currentStep.detailed_explanation && (
                <div>
                  <button
                    type="button"
                    onClick={() => setShowDetailedConcept((v) => !v)}
                    className="inline-flex items-center gap-1.5 text-xs font-extrabold text-[#101B35] hover:text-[#5146E5] transition"
                  >
                    <BookOpen className="w-4 h-4" />
                    <span>
                      {showDetailedConcept ? 'Hide detailed explanation' : 'Read detailed explanation'}
                    </span>
                    {showDetailedConcept ? (
                      <ChevronUp className="w-4 h-4" />
                    ) : (
                      <ChevronDown className="w-4 h-4" />
                    )}
                  </button>
                  {showDetailedConcept && (
                    <div className="mt-2.5 p-4 rounded-2xl bg-[#F7F9FF] border border-[#DFE5F6]">
                      <RichMathMarkdown text={currentStep.detailed_explanation} />
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* 2. INTERACTIVE VISUAL DIAGRAM */}
          {currentStep.step_type === 'INTERACTIVE_DIAGRAM' && (
            <div className="space-y-4">
              <p className="text-sm text-slate-600 font-medium">{currentStep.prompt}</p>
              <div className="relative w-full h-56 rounded-2xl bg-[#101B35] border border-slate-800 overflow-hidden">
                <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                  <line x1="24" y1="45" x2="52" y2="45" stroke="#35D6E8" strokeOpacity="0.45" strokeWidth="1" strokeDasharray="3 2" />
                  <line x1="52" y1="45" x2="78" y2="45" stroke="#35D6E8" strokeOpacity="0.45" strokeWidth="1" strokeDasharray="3 2" />
                  <rect x="10" y="18" width="28" height="64" rx="6" fill="#1B2654" stroke="#35D6E8" strokeOpacity="0.3" strokeWidth="0.6" />
                  <rect x="40" y="18" width="24" height="64" rx="6" fill="#1B2654" stroke="#35D6E8" strokeOpacity="0.3" strokeWidth="0.6" />
                  <rect x="68" y="18" width="24" height="64" rx="6" fill="#1B2654" stroke="#35D6E8" strokeOpacity="0.3" strokeWidth="0.6" />
                </svg>

                {(currentStep.hotspots || []).map((hs) => {
                  const visited = exploredHotspots.includes(hs.id);
                  const isActive = activeHotspot?.id === hs.id;
                  return (
                    <button
                      key={hs.id}
                      type="button"
                      onClick={() => {
                        setActiveHotspot(hs);
                        if (!visited) setExploredHotspots((prev) => [...prev, hs.id]);
                      }}
                      style={{ left: `${hs.x}%`, top: `${hs.y}%` }}
                      className={`absolute -translate-x-1/2 -translate-y-1/2 px-3 py-2 rounded-xl text-xs font-extrabold border-2 transition shadow-md min-h-[38px] ${
                        isActive
                          ? 'bg-[#35D6E8] border-white text-[#101B35] scale-105'
                          : visited
                            ? 'bg-emerald-500 border-emerald-200 text-white'
                            : 'bg-white border-[#35D6E8] text-[#101B35] hover:bg-cyan-50'
                      }`}
                    >
                      {visited ? `✓ ${hs.label}` : hs.label}
                    </button>
                  );
                })}
              </div>

              {activeHotspot ? (
                <div className="p-4 rounded-2xl bg-cyan-50/70 border border-cyan-200 space-y-1 animate-fade-in">
                  <div className="text-xs font-extrabold text-[#101B35]">{activeHotspot.label}</div>
                  <p className="text-sm text-slate-700 font-medium">{activeHotspot.summary}</p>
                </div>
              ) : (
                <div className="text-xs font-bold text-slate-500">
                  Tap any button on the diagram above to inspect it ({exploredHotspots.length}/
                  {(currentStep.hotspots || []).length} explored).
                </div>
              )}

              {currentStep.hotspots &&
                exploredHotspots.length >= currentStep.hotspots.length &&
                currentStep.encouragement && (
                  <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-900">
                    ✓ {currentStep.encouragement}
                  </div>
                )}
            </div>
          )}

          {/* 3. MCQ & TRUE/FALSE */}
          {(currentStep.step_type === 'MCQ' || currentStep.step_type === 'TRUE_FALSE') && (
            <div className="space-y-3">
              <p className="text-sm sm:text-base font-bold text-slate-800">
                {cleanMathText(currentStep.prompt || '')}
              </p>
              <div className="grid gap-2.5">
                {(currentStep.step_type === 'TRUE_FALSE'
                  ? ['True', 'False']
                  : currentStep.options || []
                ).map((opt) => {
                  const chosen = selectedOption === opt;
                  return (
                    <button
                      key={opt}
                      type="button"
                      onClick={() => {
                        setSelectedOption(opt);
                        setStepFeedback(null);
                      }}
                      className={`w-full text-left px-4 py-3.5 rounded-2xl border-2 text-sm font-bold transition min-h-[48px] flex items-center justify-between gap-2 ${
                        chosen
                          ? 'border-[#101B35] bg-[#101B35] text-white'
                          : 'border-slate-200 bg-white hover:border-[#5146E5] text-slate-800'
                      }`}
                    >
                      <span>{cleanMathText(opt)}</span>
                      {chosen && <CheckCircle2 className="w-4 h-4 text-[#35D6E8] shrink-0" />}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* 4. FILL IN THE BLANK */}
          {currentStep.step_type === 'FILL_IN_BLANK' && (
            <div className="space-y-3">
              <p className="text-sm sm:text-base font-bold text-slate-800">
                {cleanMathText(currentStep.prompt || '')}
              </p>
              <input
                type="text"
                value={textInput}
                onChange={(e) => {
                  setTextInput(e.target.value);
                  setStepFeedback(null);
                }}
                placeholder="Type the missing word..."
                className="w-full rounded-2xl border-2 border-slate-300 px-4 py-3 text-sm font-bold text-[#101B35] focus:border-[#101B35] focus:outline-none"
              />
              {currentStep.hint && (
                <button
                  type="button"
                  onClick={() => setShowHint((h) => !h)}
                  className="text-xs font-bold text-[#5146E5] hover:underline"
                >
                  {showHint ? `Hint: ${cleanMathText(currentStep.hint)}` : 'Need a hint?'}
                </button>
              )}
            </div>
          )}

          {/* 5. MATCH THE PAIRS */}
          {currentStep.step_type === 'MATCH_PAIRS' && currentStep.pairs && (
            <div className="space-y-3">
              <p className="text-sm font-bold text-slate-700">{currentStep.prompt}</p>
              <div className="grid sm:grid-cols-2 gap-3">
                <div className="space-y-2">
                  <div className="text-[11px] font-extrabold uppercase text-slate-500">1. Tap a term</div>
                  {currentStep.pairs.map((p) => {
                    const isSel = selectedLeft === p.left;
                    const isMatched = Boolean(matchedPairs[p.left]);
                    return (
                      <button
                        key={p.left}
                        type="button"
                        onClick={() => setSelectedLeft(p.left)}
                        className={`w-full text-left px-4 py-3 rounded-xl border-2 text-xs font-extrabold transition min-h-[46px] ${
                          isSel
                            ? 'border-[#5146E5] bg-cyan-50 text-[#101B35]'
                            : isMatched
                              ? 'border-emerald-300 bg-emerald-50 text-emerald-900'
                              : 'border-slate-200 bg-white text-slate-800'
                        }`}
                      >
                        <div>{p.left}</div>
                        {isMatched && (
                          <div className="text-[10px] font-semibold text-emerald-700 mt-0.5">
                            → {matchedPairs[p.left]}
                          </div>
                        )}
                      </button>
                    );
                  })}
                </div>
                <div className="space-y-2">
                  <div className="text-[11px] font-extrabold uppercase text-slate-500">
                    2. Tap its match
                  </div>
                  {shuffledRights.map((rightText) => {
                    const used = Object.values(matchedPairs).includes(rightText);
                    return (
                      <button
                        key={rightText}
                        type="button"
                        disabled={!selectedLeft}
                        onClick={() => {
                          if (!selectedLeft) return;
                          setMatchedPairs((prev) => ({ ...prev, [selectedLeft]: rightText }));
                          setSelectedLeft(null);
                          setStepFeedback(null);
                        }}
                        className={`w-full text-left px-4 py-3 rounded-xl border-2 text-xs font-bold transition min-h-[46px] ${
                          used
                            ? 'border-emerald-200 bg-emerald-50/50 text-slate-500'
                            : selectedLeft
                              ? 'border-slate-300 bg-white hover:border-[#101B35] text-slate-800'
                              : 'border-slate-200 bg-slate-50 text-slate-500 cursor-not-allowed'
                        }`}
                      >
                        {rightText}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* 6. ARRANGE STEPS IN ORDER */}
          {currentStep.step_type === 'ORDER_STEPS' && (
            <div className="space-y-3">
              <p className="text-sm font-bold text-slate-700">{currentStep.prompt}</p>
              <div className="space-y-2">
                {orderedItems.map((item, idx) => (
                  <div
                    key={item}
                    className="p-3.5 rounded-2xl border-2 border-slate-200 bg-white flex items-center justify-between gap-3"
                  >
                    <div className="flex items-center gap-3">
                      <span className="w-7 h-7 rounded-lg bg-[#101B35] text-[#35D6E8] text-xs font-extrabold flex items-center justify-center shrink-0">
                        {idx + 1}
                      </span>
                      <span className="text-xs sm:text-sm font-bold text-slate-800">{item}</span>
                    </div>
                    <div className="flex items-center gap-1 shrink-0">
                      <button
                        type="button"
                        disabled={idx === 0}
                        onClick={() => moveOrderItem(idx, -1)}
                        aria-label={`Move step ${idx + 1} up`}
                        className="p-2 rounded-lg border border-slate-200 hover:bg-slate-100 disabled:opacity-30"
                      >
                        <ArrowUp className="w-3.5 h-3.5 text-[#101B35]" />
                      </button>
                      <button
                        type="button"
                        disabled={idx === orderedItems.length - 1}
                        onClick={() => moveOrderItem(idx, 1)}
                        aria-label={`Move step ${idx + 1} down`}
                        className="p-2 rounded-lg border border-slate-200 hover:bg-slate-100 disabled:opacity-30"
                      >
                        <ArrowDown className="w-3.5 h-3.5 text-[#101B35]" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 7. SHORT ANSWER */}
          {currentStep.step_type === 'SHORT_ANSWER' && (
            <div className="space-y-3">
              <p className="text-sm sm:text-base font-bold text-slate-800">{currentStep.prompt}</p>
              <textarea
                rows={3}
                value={textInput}
                onChange={(e) => {
                  setTextInput(e.target.value);
                  setStepFeedback(null);
                }}
                placeholder="Write a short sentence in your own words..."
                className="w-full rounded-2xl border-2 border-slate-300 px-4 py-3 text-sm font-medium text-[#101B35] focus:border-[#101B35] focus:outline-none"
              />
            </div>
          )}

          {/* Immediate Encouraging Feedback Banner with Sparky Reaction */}
          {stepFeedback && (
            <div
              className={`p-4 rounded-2xl border-2 flex items-center gap-3 animate-spark-celebrate ${
                stepFeedback.correct
                  ? 'bg-emerald-50 border-emerald-300 text-emerald-950'
                  : 'bg-amber-50 border-amber-300 text-amber-950'
              }`}
            >
              <SparkRobotMascot
                mood={stepFeedback.correct ? 'celebrating' : 'encouraging'}
                size="xs"
              />
              <div className="space-y-0.5">
                <div className="text-sm font-extrabold">{stepFeedback.headline}</div>
                <p className="text-xs font-medium leading-relaxed">{stepFeedback.detail}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Footer Navigation */}
      <div className="px-6 py-4 bg-slate-50 border-t border-slate-200 flex flex-wrap items-center justify-between gap-3">
        <button
          type="button"
          disabled={stepIdx === 0}
          onClick={() => setStepIdx((i) => Math.max(0, i - 1))}
          className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl border border-slate-300 bg-white hover:bg-slate-100 text-xs font-extrabold text-[#101B35] disabled:opacity-40 transition min-h-[44px]"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back</span>
        </button>

        <div className="flex items-center gap-2">
          {needsCheck && (!stepFeedback || !stepFeedback.correct) && (
            <button
              type="button"
              onClick={checkCurrentActivity}
              className="px-5 py-2.5 rounded-xl bg-[#35D6E8] hover:bg-[#5ce0ef] text-[#101B35] text-sm font-extrabold transition min-h-[44px]"
            >
              Check Answer
            </button>
          )}

          {(!needsCheck || stepFeedback) && (
            <button
              type="button"
              disabled={savingResult}
              onClick={() => {
                if (isLastStep) {
                  handleFinishLesson();
                } else {
                  setStepIdx((i) => i + 1);
                }
              }}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-[#5146E5] hover:bg-[#4338CA] text-white text-sm font-extrabold shadow-sm transition min-h-[44px]"
            >
              <span>
                {isLastStep
                  ? savingResult
                    ? 'Saving Result...'
                    : 'Finish Lesson'
                  : 'Continue'}
              </span>
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
