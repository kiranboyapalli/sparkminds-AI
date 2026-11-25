import React from 'react';
import {
  Calendar,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  BookOpen,
  FileText,
  Trophy,
  RefreshCw,
  Upload,
  Plus,
  Play,
  Lightbulb,
  Layers,
  TrendingUp,
  Shield,
  Flame,
  ArrowRight,
  Award,
} from 'lucide-react';
import { OnboardingState } from '../onboarding/SevenStepOnboarding';
import {
  ALL_23_INDIAN_LANGUAGES,
  getSubjectsForGradeAndBoardFrontend as getCurriculumSubjects,
} from '../curriculum/curriculumData';
import { BrandTagline } from '../design-system/EduSparkLogo';
import {
  ScreenId,
  getGradeExperienceMeta as getGradeBandMeta,
} from '../design-system/tokens';
import { HistoricalYearRecord } from './CoreFeatureScreens';
import {
  formatTime12Hour,
  formatTimeRange12Hour,
  formatHomeworkDeadline12Hour,
  formatExamSchedule12Hour,
  formatRevisionSchedule12Hour,
} from '../utils/timeFormat';
import {
  IntelligentAssessmentLabPanel,
  DocumentStudyRAGPanel,
  LearningGapsAndGamificationPanel,
} from '../components/AgenticEcosystemPanels';
import { GuidedInteractiveLesson } from '../components/GuidedInteractiveLesson';
import { HelpTip } from '../components/HelpTip';
import { SparkRobotMascot } from '../components/SparkRobotMascot';
import { RobotGuideTip } from '../components/RobotGuideTip';

// ============================================================================
// A. STUDENT DASHBOARD VIEW (CONNECTED TO /api/students/{id}/dashboard-summary)
// ============================================================================

export interface PersonalActivityItemUI {
  activity_id?: string;
  activity_name: string;
  category: string;
  start_time: string;
  end_time: string;
  duration_minutes?: number;
  location?: string;
  notes?: string;
  recurrence_type:
  | 'Only today'
  | 'Repeated on selected weekdays'
  | 'Repeated every day';
  recurring_weekdays: string[];
  is_cancelled_today?: boolean;
}

export interface AvailableTimeWindowUI {
  window_id: string;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  period_label: string;
  window_label?: string;
}

export interface DailyScheduleDataUI {
  schedule_id: string;
  student_id: string;
  date_iso: string;
  weekday_short: string;
  weekday_name?: string;
  checkin_prompt: string;
  greeting_prompt?: string;
  checkin_completed: boolean;
  free_all_day: boolean;
  wake_up_time: string;
  sleep_time: string;
  activities: PersonalActivityItemUI[];
  recurring_templates: PersonalActivityItemUI[];
  unavailable_slots_summary: string[];
  available_time_windows: AvailableTimeWindowUI[];
  total_unavailable_minutes: number;
  total_available_study_minutes: number;
  total_available_study_hours: number;
  available_study_hours: number;
  next_free_slot_display?: string | null;
  generated_daily_timeline: {
    task_id: string;
    day_label: string;
    date_iso: string;
    time_slot: string;
    subject: string;
    chapter: string;
    session_type: string;
    duration_minutes: number;
    completed: boolean;
    missed?: boolean;
    postponed?: boolean;
    priority_reason?: string;
  }[];
}

interface DashboardSummaryResponse {
  greeting: string;
  study_streak_days: number;
  homework_completion_rate: number;
  daily_checkin_required?: boolean;
  daily_schedule?: DailyScheduleDataUI;
  todays_schedule: {
    task_id: string;
    day_label: string;
    time_slot: string;
    subject: string;
    chapter: string;
    session_type: string;
    duration_minutes: number;
    completed: boolean;
    priority_reason?: string;
  }[];
  todays_combined_schedule?: {
    task_id: string;
    day_label: string;
    time_slot: string;
    subject: string;
    chapter: string;
    session_type: string;
    duration_minutes: number;
    completed: boolean;
    priority_reason?: string;
  }[];
  pending_homework: {
    homework_id: string;
    subject: string;
    chapter: string;
    title: string;
    description: string;
    due_date: string;
    priority: string;
    estimated_minutes: number;
    status: string;
  }[];
  upcoming_exams: {
    exam_name: string;
    exam_date: string;
    days_remaining?: number;
    status?: string;
    score_percentage?: number | null;
  }[];
  daily_learning_goals: {
    goal: string;
    completed: boolean;
  }[];
  subject_progress: {
    subject: string;
    overall_mastery_percentage: number;
    verified_assessment_average: number | null;
    homework_practice_average: number | null;
    self_reported_confidence: string;
  }[];
  ai_recommendations: string[];
  active_gaps: string[];
}

export const StudentDashboardView: React.FC<{
  onboarding: OnboardingState;
  academicYearsCount: number;
  onSelectScreen: (s: ScreenId) => void;
  onOpenBuddyWithQuestion: (q: string, subject: string) => void;
  onOpenAgeEditor?: () => void;
}> = ({
  onboarding,
  academicYearsCount,
  onSelectScreen,
  onOpenBuddyWithQuestion,
  onOpenAgeEditor,
}) => {
    const [data, setData] = React.useState<DashboardSummaryResponse | null>(null);
    const [loading, setLoading] = React.useState<boolean>(true);
    const [error, setError] = React.useState<string | null>(null);

    const fetchDashboard = React.useCallback(async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(
          `/api/students/${onboarding.studentId}/dashboard-summary`
        );
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json: DashboardSummaryResponse = await res.json();
        setData(json);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : 'Failed to load dashboard');
      } finally {
        setLoading(false);
      }
    }, [onboarding.studentId]);

    React.useEffect(() => {
      fetchDashboard();
    }, [fetchDashboard]);

    const toggleScheduleTask = async (taskId: string, current: boolean) => {
      try {
        await fetch(
          `/api/students/${onboarding.studentId}/study-plan/tasks/${taskId}`,
          {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ completed: !current, missed: false }),
          }
        );
        fetchDashboard();
      } catch {
        // ignore
      }
    };

    const cleanFirstName =
      onboarding.studentName &&
      !['Aarav Sharma', 'Ananya Reddy', 'Diya Nair', 'Karthik Rajan', 'Riya Verma', 'Student Learner'].includes(
        onboarding.studentName
      )
        ? onboarding.studentName.split(' ')[0]
        : '';

    const completedGoalsCount = (data?.daily_learning_goals || []).filter((g) => g.completed).length;
    const totalGoalsCount = (data?.daily_learning_goals || []).length;
    const goalProgressPct =
      totalGoalsCount > 0 ? Math.round((completedGoalsCount / totalGoalsCount) * 100) : 0;

    const activeScheduleItems = (
      data?.todays_combined_schedule && data.todays_combined_schedule.length > 0
        ? data.todays_combined_schedule
        : data?.todays_schedule || []
    );

    const nextStudyItem = activeScheduleItems.find(
      (i) => !i.completed && i.session_type !== 'Unavailable' && i.session_type !== 'Break'
    );

    const topRecommendation =
      data?.ai_recommendations?.[0] ||
      (nextStudyItem
        ? `Continue ${nextStudyItem.chapter} in ${nextStudyItem.subject}.`
        : 'Start a short interactive lesson to build momentum today.');

    const curriculumPreviewSubjects = React.useMemo(
      () => getCurriculumSubjects(onboarding.grade, onboarding.board, onboarding.stateName).slice(0, 3),
      [onboarding.grade, onboarding.board, onboarding.stateName]
    );
    const ringRadius = 36;
    const ringCircumference = 2 * Math.PI * ringRadius;
    const ringOffset = ringCircumference * (1 - Math.min(100, Math.max(0, goalProgressPct)) / 100);

    return (
      <div
        data-testid="bluish-dashboard-canvas"
        className="spark-dashboard-canvas rounded-[2rem] p-3.5 sm:p-6 lg:p-7 space-y-6 animate-fade-in text-[#172554] overflow-hidden"
      >
        <RobotGuideTip
          tipId="dashboard_overview"
          studentId={onboarding.studentId}
          title="Sparky's Daily Tip"
          message="Check today's goal ring, continue your next interactive lesson, or tap Ask AI Buddy anytime for visual step-by-step explanations."
          mood="guiding"
        />

        {/* 1. PREMIUM BLUISH BENTO HERO: WELCOME + SPARKY ROBOT + CONTINUE LEARNING + DAILY GOAL RING */}
        <div className="grid lg:grid-cols-12 gap-5">
          {/* Left Hero Card: Midnight-Indigo Layered Welcome + Interactive Continue Learning Path */}
          <div
            className="lg:col-span-8 min-w-0 rounded-3xl text-white p-5 sm:p-6 md:p-7 shadow-[0_24px_56px_-22px_rgba(16,27,53,0.55)] border border-[#4F46E5]/35 flex flex-col justify-between gap-6 relative overflow-hidden"
            style={{
              background:
                'linear-gradient(135deg, #0D1630 0%, #1B275D 55%, #4F46E5 100%)',
            }}
          >
            <div aria-hidden="true" className="pointer-events-none absolute inset-0 spark-hero-grid opacity-55" />
            <div
              aria-hidden="true"
              className="pointer-events-none absolute -top-24 -right-20 w-72 h-72 rounded-full bg-[#35D6E8]/20 blur-3xl"
            />
            <div className="relative z-10 flex flex-wrap items-center justify-between gap-4 min-w-0">
              <div className="space-y-2.5 flex-1 min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#35D6E8]/18 border border-[#35D6E8]/50 text-[#35D6E8] text-xs font-extrabold backdrop-blur">
                    <Flame className="w-3.5 h-3.5" />
                    <span>{data?.study_streak_days ?? 0}-Day Streak</span>
                  </span>
                  <span className="px-2.5 py-1 rounded-full bg-white/10 border border-white/15 text-xs font-bold text-indigo-100">
                    Grade {onboarding.grade} • {onboarding.board}
                  </span>
                  <button
                    type="button"
                    onClick={() => {
                      if (onOpenAgeEditor) onOpenAgeEditor();
                      else onSelectScreen('profile');
                    }}
                    className="px-2.5 py-1 rounded-full bg-white/10 hover:bg-white/20 text-indigo-100 text-[11px] font-bold transition"
                    title="Edit student age"
                  >
                    Age {onboarding.age}
                  </button>
                </div>

                <h2 className="font-display text-2xl sm:text-3xl md:text-[2.1rem] font-bold tracking-tight text-white leading-tight">
                  {cleanFirstName
                    ? `Welcome back, ${cleanFirstName}!`
                    : "Welcome! Let's spark today's learning."}
                </h2>
                <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-[#0B1328]/65 border border-[#35D6E8]/40 backdrop-blur-sm max-w-full shadow-sm">
                  <Sparkles className="w-3.5 h-3.5 text-[#FBBF24] shrink-0" />
                  <BrandTagline
                    variant="dark"
                    className="text-xs sm:text-[13.5px] leading-snug"
                  />
                </div>
                <p className="text-sm text-indigo-100/90 font-medium max-w-xl">
                  {nextStudyItem
                    ? `Up next: ${nextStudyItem.subject} — ${nextStudyItem.chapter}.`
                    : 'Launch an interactive lesson or explore visual diagrams with Sparky.'}
                </p>
              </div>

              <div className="hidden sm:flex flex-col items-center gap-1.5 shrink-0 relative">
                <div className="absolute -inset-3 rounded-full bg-[#35D6E8]/15 blur-xl pointer-events-none" />
                <SparkRobotMascot mood="welcome" size="lg" />
                <span className="relative z-10 text-[10px] font-extrabold text-[#35D6E8] bg-[#0B1328]/80 px-3 py-0.5 rounded-full border border-[#35D6E8]/40 shadow-sm">
                  Sparky AI Online
                </span>
              </div>
            </div>

            {/* Continue Learning Path Strip */}
            <div className="relative z-10 p-4 rounded-2xl bg-[#0B1328]/70 backdrop-blur-md border border-white/15 space-y-3 shadow-inner">
              <div className="flex items-center justify-between gap-2">
                <span className="text-[11px] font-extrabold uppercase tracking-wider text-[#35D6E8]">
                  Continue Learning Path
                </span>
                <span className="text-[11px] font-semibold text-indigo-200/80">
                  Tap any step to launch
                </span>
              </div>
              <div className="grid grid-cols-1 xl:grid-cols-3 gap-2.5 min-w-0">
                {curriculumPreviewSubjects.map((sub, idx) => (
                  <button
                    key={sub.code}
                    type="button"
                    onClick={() => onSelectScreen('subjects')}
                    className={`w-full min-w-0 overflow-hidden p-3 rounded-xl border text-left transition flex items-center gap-3 min-h-[58px] ${
                      idx === 0
                        ? 'spark-btn-aqua border-[#7CEAF6] text-[#101B35]'
                        : 'bg-white/[0.07] border-white/15 text-white hover:border-[#35D6E8]/60 hover:bg-white/14'
                    }`}
                  >
                    <span
                      className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-extrabold shrink-0 ${
                        idx === 0
                          ? 'bg-[#101B35] text-[#35D6E8]'
                          : 'bg-[#4F46E5] text-white'
                      }`}
                    >
                      {idx + 1}
                    </span>
                    <div className="min-w-0">
                      <div className="text-xs font-extrabold truncate">{sub.name}</div>
                      <div
                        className={`text-[11px] truncate ${
                          idx === 0 ? 'text-[#101B35]/80 font-bold' : 'text-indigo-200'
                        }`}
                      >
                        {sub.topics[0] || 'Interactive Lesson'}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <div className="relative z-10 flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={() => onSelectScreen('subjects')}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl spark-btn-aqua text-sm font-extrabold min-h-[46px]"
              >
                <Play className="w-4 h-4 fill-current" />
                <span>Start Guided Lesson</span>
              </button>
              <button
                type="button"
                onClick={() => onSelectScreen('buddy')}
                className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-white/12 hover:bg-white/22 border border-white/25 text-white text-sm font-extrabold backdrop-blur transition min-h-[46px]"
              >
                <Sparkles className="w-4 h-4 text-[#35D6E8]" />
                <span>Ask Sparky AI</span>
              </button>
            </div>
          </div>

          {/* Right Bluish Card (#F7F9FF): Today's Daily Goal Circular SVG Ring */}
          <div className="lg:col-span-4 min-w-0 spark-dashboard-card spark-dashboard-card-hover rounded-3xl p-5 sm:p-6 flex flex-col justify-between gap-4">
            <div className="flex items-center justify-between gap-2">
              <h3 className="text-sm font-extrabold text-[#172554]">Today&apos;s Learning Goal</h3>
              <HelpTip
                title="Daily Learning Goal"
                text="Your goal updates automatically from real completed study blocks, homework, quizzes, and guided lessons."
              />
            </div>

            <div className="flex items-center gap-5 py-1">
              <div className="relative w-24 h-24 shrink-0">
                <svg className="w-24 h-24 -rotate-90" viewBox="0 0 88 88" aria-hidden="true">
                  <defs>
                    <linearGradient id="dashRingGrad" x1="0" y1="0" x2="88" y2="88" gradientUnits="userSpaceOnUse">
                      <stop offset="0%" stopColor="#4F46E5" />
                      <stop offset="100%" stopColor="#35D6E8" />
                    </linearGradient>
                  </defs>
                  <circle
                    cx="44"
                    cy="44"
                    r={ringRadius}
                    fill="none"
                    stroke="#DCE6FA"
                    strokeWidth="8"
                  />
                  <circle
                    cx="44"
                    cy="44"
                    r={ringRadius}
                    fill="none"
                    stroke="url(#dashRingGrad)"
                    strokeWidth="8"
                    strokeLinecap="round"
                    strokeDasharray={ringCircumference}
                    strokeDashoffset={ringOffset}
                    className="transition-all duration-500"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="font-display text-xl font-bold text-[#172554]">{goalProgressPct}%</span>
                  <span className="text-[10px] font-extrabold text-[#4F46E5]">
                    {completedGoalsCount}/{totalGoalsCount || 1}
                  </span>
                </div>
              </div>

              <div className="space-y-1.5 min-w-0">
                <div className="text-sm font-extrabold text-[#172554]">
                  {goalProgressPct >= 100
                    ? 'Goal complete!'
                    : completedGoalsCount > 0
                      ? 'Great momentum today!'
                      : 'Ready to begin today?'}
                </div>
                <p className="text-xs text-[#172554]/75 font-medium">
                  Homework: <strong className="text-[#172554]">{data?.homework_completion_rate ?? 0}%</strong> •{' '}
                  Free time: <strong className="text-[#172554]">{data?.daily_schedule?.available_study_hours ?? 0}h</strong>
                </p>
              </div>
            </div>

            <div className="space-y-1.5">
              {(data?.daily_learning_goals || []).slice(0, 2).map((g, idx) => (
                <div
                  key={idx}
                  className={`px-3 py-2 rounded-xl border text-xs font-semibold flex items-center gap-2 truncate ${
                    g.completed
                      ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                      : 'bg-[#EAF0FF] border-[#C2D4F8] text-[#172554]'
                  }`}
                >
                  <span className="text-[#4F46E5] font-extrabold">{g.completed ? '✓' : '○'}</span>
                  <span className="truncate">{formatTime12Hour(g.goal)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 1B. EXECUTIVE 4-METRIC REAL-DATA KPI STRIP */}
        {data && (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5 sm:gap-4">
            {[
              {
                label: 'Active Study Streak',
                value: `${data.study_streak_days ?? 0} Day${(data.study_streak_days ?? 0) === 1 ? '' : 's'}`,
                sub: 'Real verified sessions',
                icon: <Flame className="w-4 h-4 text-[#4F46E5]" />,
                accent: 'from-[#4F46E5] to-[#35D6E8]',
                pct: Math.min(100, Math.max(8, (data.study_streak_days ?? 0) * 14)),
              },
              {
                label: 'Daily Goal Progress',
                value: `${goalProgressPct}%`,
                sub: `${completedGoalsCount} of ${totalGoalsCount || 1} milestones`,
                icon: <Award className="w-4 h-4 text-[#4F46E5]" />,
                accent: 'from-[#4F46E5] to-[#35D6E8]',
                pct: Math.max(6, goalProgressPct),
              },
              {
                label: 'Homework Mastery',
                value: `${data.homework_completion_rate ?? 0}%`,
                sub: `${data.pending_homework.length} pending task${data.pending_homework.length === 1 ? '' : 's'}`,
                icon: <FileText className="w-4 h-4 text-[#4F46E5]" />,
                accent: 'from-[#4F46E5] to-[#35D6E8]',
                pct: Math.max(6, data.homework_completion_rate ?? 0),
              },
              {
                label: 'Available Study Time',
                value: `${data.daily_schedule?.available_study_hours ?? 0} hrs`,
                sub: `${academicYearsCount} academic year${academicYearsCount === 1 ? '' : 's'} tracked`,
                icon: <Clock className="w-4 h-4 text-[#4F46E5]" />,
                accent: 'from-[#4F46E5] to-[#35D6E8]',
                pct: Math.min(100, Math.max(12, Math.round(((data.daily_schedule?.available_study_hours ?? 0) / 16) * 100))),
              },
            ].map((kpi) => (
              <div
                key={kpi.label}
                className="spark-dashboard-card spark-dashboard-card-hover rounded-2xl p-4 space-y-2.5 min-w-0"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="text-[11px] font-bold text-[#172554]/70 truncate">{kpi.label}</span>
                  <span className="w-8 h-8 rounded-xl bg-[#EAF0FF] border border-[#C2D4F8] flex items-center justify-center shrink-0">
                    {kpi.icon}
                  </span>
                </div>
                <div className="font-display text-xl sm:text-2xl font-bold text-[#172554] tracking-tight">
                  {kpi.value}
                </div>
                <div className="space-y-1">
                  <div className="h-1.5 w-full rounded-full bg-[#DCE6FA] overflow-hidden">
                    <div
                      className={`h-full rounded-full bg-gradient-to-r ${kpi.accent}`}
                      style={{ width: `${kpi.pct}%` }}
                    />
                  </div>
                  <div className="text-[10px] font-semibold text-[#172554]/65 truncate">{kpi.sub}</div>
                </div>
              </div>
            ))}
          </div>
        )}

        {loading && !data && (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5 sm:gap-4" aria-label="Loading dashboard metrics">
            {[0, 1, 2, 3].map((i) => (
              <div key={i} className="spark-dashboard-card rounded-2xl p-4 space-y-3">
                <div className="h-3 w-24 rounded-full spark-skeleton" />
                <div className="h-7 w-16 rounded-lg spark-skeleton" />
                <div className="h-1.5 w-full rounded-full spark-skeleton" />
              </div>
            ))}
          </div>
        )}

        {error && (
          <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 flex flex-wrap items-center justify-between gap-3 text-xs font-bold text-rose-900">
            <span>Could not refresh dashboard: {error}</span>
            <button
              type="button"
              onClick={fetchDashboard}
              className="px-3 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-extrabold transition"
            >
              Retry
            </button>
          </div>
        )}

        {data && (
          <>
            {/* 2. AI RECOMMENDED NEXT STEP STRIP */}
            <div className="spark-dashboard-card spark-dashboard-card-hover rounded-2xl p-5 flex flex-wrap items-center justify-between gap-4 border-l-4 border-l-[#4F46E5]">
              <div className="flex items-start gap-3.5 max-w-2xl">
                <div className="w-10 h-10 rounded-xl bg-[#4F46E5] text-white flex items-center justify-center shrink-0 shadow-sm">
                  <Sparkles className="w-5 h-5 text-[#35D6E8]" />
                </div>
                <div>
                  <div className="text-[11px] font-extrabold uppercase tracking-wider text-[#4F46E5]">
                    AI Recommended Next Step
                  </div>
                  <p className="text-sm font-extrabold text-[#172554] mt-0.5">
                    {formatTime12Hour(topRecommendation)}
                  </p>
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => onSelectScreen('plan')}
                  className="px-4 py-2.5 rounded-xl border border-[#C7D7F7] bg-white hover:bg-[#EAF0FF] text-[#172554] text-xs font-extrabold transition min-h-[42px]"
                >
                  {data.daily_schedule?.checkin_completed ? 'Study Plan' : 'Plan Today'}
                </button>
                <button
                  type="button"
                  onClick={() => onSelectScreen('exams')}
                  className="px-4 py-2.5 rounded-xl bg-[#4F46E5] hover:bg-[#4338CA] text-white text-xs font-extrabold transition min-h-[42px] shadow-sm"
                >
                  Quick Quiz →
                </button>
              </div>
            </div>

            {/* 3. TODAY'S STUDY SCHEDULE & UPCOMING HOMEWORK */}
            <div className="grid lg:grid-cols-12 gap-5">
              {/* Today's Study Blocks */}
              <div className="lg:col-span-7 min-w-0 spark-dashboard-card rounded-3xl p-5 sm:p-6 space-y-4">
                <div className="flex items-center justify-between gap-2 pb-3 border-b border-[#DCE6FA]">
                  <h3 className="text-sm font-extrabold text-[#172554] flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-[#4F46E5]" />
                    <span>Daily Study Schedule</span>
                  </h3>
                  <button
                    type="button"
                    onClick={() => onSelectScreen('plan')}
                    className="text-xs font-extrabold text-[#4F46E5] hover:text-[#172554] inline-flex items-center gap-1"
                  >
                    <span>Full Planner</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>

                {activeScheduleItems.length === 0 ? (
                  <p className="text-xs text-[#172554]/70 font-medium py-3">
                    No blocks scheduled yet. Open Study Planner to set today&apos;s free slots.
                  </p>
                ) : (
                  <div className="space-y-2.5">
                    {activeScheduleItems.slice(0, 5).map((item) => (
                      <div
                        key={item.task_id}
                        className={`p-3.5 rounded-2xl border transition flex flex-wrap items-center justify-between gap-3 ${
                          item.session_type === 'Unavailable'
                            ? 'bg-[#EAF0FF]/70 border-[#DCE6FA] text-[#172554]/60'
                            : item.completed
                              ? 'bg-emerald-50/70 border-emerald-200 opacity-85'
                              : 'bg-white border-[#C7D7F7] hover:border-[#4F46E5]'
                        }`}
                      >
                        <div className="flex items-center gap-3 min-w-0">
                          {item.session_type !== 'Unavailable' && item.session_type !== 'Break' ? (
                            <input
                              type="checkbox"
                              checked={item.completed}
                              onChange={() => toggleScheduleTask(item.task_id, item.completed)}
                              aria-label={`Mark ${item.subject} ${item.chapter} done`}
                              className="w-4 h-4 rounded text-[#4F46E5] cursor-pointer shrink-0"
                            />
                          ) : (
                            <Clock className="w-4 h-4 text-[#4F46E5]/60 shrink-0" />
                          )}
                          <div className="min-w-0">
                            <div className="text-xs font-extrabold text-[#172554] truncate">
                              {formatTimeRange12Hour(item.time_slot)} • {item.subject}
                            </div>
                            <div className="text-xs text-[#172554]/75 truncate">
                              {item.chapter} ({item.duration_minutes}m)
                            </div>
                          </div>
                        </div>

                        {item.session_type !== 'Break' && item.session_type !== 'Unavailable' && (
                          <button
                            type="button"
                            onClick={() =>
                              onOpenBuddyWithQuestion(
                                `Teach me ${item.chapter} in ${item.subject} step by step with a visual example.`,
                                item.subject
                              )
                            }
                            className="px-3 py-1.5 rounded-xl bg-[#4F46E5] hover:bg-[#4338CA] text-white text-xs font-extrabold transition shrink-0"
                          >
                            Learn →
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Homework & Deadlines */}
              <div className="lg:col-span-5 min-w-0 spark-dashboard-card rounded-3xl p-5 sm:p-6 space-y-4">
                <div className="flex items-center justify-between gap-2 pb-3 border-b border-[#DCE6FA]">
                  <h3 className="text-sm font-extrabold text-[#172554] flex items-center gap-2">
                    <FileText className="w-4 h-4 text-[#4F46E5]" />
                    <span>Homework &amp; Deadlines ({data.pending_homework.length})</span>
                  </h3>
                  <button
                    type="button"
                    onClick={() => onSelectScreen('homework')}
                    className="text-xs font-extrabold text-[#4F46E5] hover:text-[#172554]"
                  >
                    Manage →
                  </button>
                </div>

                {data.pending_homework.length === 0 ? (
                  <div className="p-4 rounded-2xl bg-emerald-50/80 border border-emerald-200 text-xs font-bold text-emerald-900">
                    All caught up on homework! Great job.
                  </div>
                ) : (
                  <div className="space-y-2.5">
                    {data.pending_homework.slice(0, 3).map((hw) => {
                      const hwTiming = formatHomeworkDeadline12Hour(hw.due_date, hw.priority);
                      return (
                        <div
                          key={hw.homework_id}
                          className="p-3.5 rounded-2xl border border-[#C7D7F7] bg-white space-y-1.5 text-xs"
                        >
                          <div className="flex items-center justify-between gap-2">
                            <span className="font-extrabold text-[#172554]">{hw.subject}</span>
                            <span
                              className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold ${
                                hw.priority === 'High'
                                  ? 'bg-rose-100 text-rose-800'
                                  : 'bg-[#EAF0FF] text-[#4F46E5]'
                              }`}
                            >
                              Due {hwTiming.dueDisplay}
                            </span>
                          </div>
                          <div className="font-semibold text-[#172554]/85">{hw.title}</div>
                          <button
                            type="button"
                            onClick={() => onOpenBuddyWithQuestion(hw.description, hw.subject)}
                            className="text-[#4F46E5] hover:text-[#172554] font-extrabold inline-flex items-center gap-1 pt-0.5"
                          >
                            <span>Ask Sparky for a hint</span>
                            <ArrowRight className="w-3 h-3" />
                          </button>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>

            {/* 4. LEARNING PROGRESS & UPCOMING EXAMS */}
            <div className="grid md:grid-cols-2 gap-5">
              {/* Subject Progress */}
              <div className="spark-dashboard-card rounded-3xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-extrabold text-[#172554] flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-[#4F46E5]" />
                    <span>Learning Progress</span>
                  </h3>
                  <button
                    type="button"
                    onClick={() => onSelectScreen('progress')}
                    className="text-xs font-extrabold text-[#4F46E5] hover:text-[#172554]"
                  >
                    Full Report →
                  </button>
                </div>
                <div className="space-y-3 text-xs">
                  {data.subject_progress.map((sp) => (
                    <div key={sp.subject} className="space-y-1">
                      <div className="flex justify-between font-extrabold text-[#172554]">
                        <span>{sp.subject}</span>
                        <span className="text-[#4F46E5]">{sp.overall_mastery_percentage}%</span>
                      </div>
                      <div className="w-full h-2.5 rounded-full bg-[#DCE6FA] overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-[#4F46E5] to-[#35D6E8] rounded-full transition-all duration-500"
                          style={{
                            width: `${Math.min(100, sp.overall_mastery_percentage)}%`,
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Upcoming Exams & Academic Archive */}
              <div className="spark-dashboard-card rounded-3xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-extrabold text-[#172554] flex items-center gap-2">
                    <Trophy className="w-4 h-4 text-[#4F46E5]" />
                    <span>Upcoming Exams &amp; Milestones</span>
                  </h3>
                  <button
                    type="button"
                    onClick={() => onSelectScreen('exams')}
                    className="text-xs font-extrabold text-[#4F46E5] hover:text-[#172554]"
                  >
                    Exam Prep →
                  </button>
                </div>
                <div className="space-y-2.5 text-xs">
                  {data.upcoming_exams.slice(0, 3).map((ex, i) => (
                    <div
                      key={i}
                      className="p-3.5 rounded-2xl bg-white border border-[#C7D7F7] flex items-center justify-between gap-3"
                    >
                      <div>
                        <div className="font-extrabold text-[#172554]">{ex.exam_name}</div>
                        <div className="text-[#172554]/65 mt-0.5">
                          {formatExamSchedule12Hour(
                            ex.exam_date,
                            i === 0 ? '09:30 - 11:00' : '14:30 - 16:00'
                          )}
                        </div>
                      </div>
                      {ex.days_remaining !== undefined ? (
                        <span className="px-2.5 py-1 rounded-full bg-[#172554] text-[#35D6E8] font-extrabold shrink-0">
                          {ex.days_remaining}d left
                        </span>
                      ) : (
                        <span className="font-extrabold text-[#4F46E5] shrink-0">
                          {ex.status}
                          {ex.score_percentage !== null && ex.score_percentage !== undefined
                            ? ` (${ex.score_percentage}%)`
                            : ''}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    );
  };

// ============================================================================
// C. SMART STUDY PLANNER VIEW (CONNECTED TO /api/students/{id}/study-plan)
// ============================================================================

interface ExamChapterEntryUI {
  chapter_number: number;
  chapter_name: string;
  difficulty: 'Easy' | 'Medium' | 'Difficult';
  completion_status: 'Not Started' | 'In Progress' | 'Completed';
  additional_practice_needed: boolean;
  revision_requirements: string;
}

interface ExamSubjectEntryUI {
  subject_id?: string;
  subject_name: string;
  number_of_chapters: number;
  exam_date: string;
  exam_time?: string | null;
  maximum_marks?: number | null;
  subject_difficulty: 'Easy' | 'Medium' | 'Difficult';
  student_confidence_level?: string | null;
  chapters: ExamChapterEntryUI[];
}

interface StudyTask {
  task_id: string;
  day_label: string;
  date_iso: string;
  time_slot: string;
  subject: string;
  chapter: string;
  session_type: string;
  duration_minutes: number;
  completed: boolean;
  missed: boolean;
  postponed?: boolean;
  subject_exam_date?: string | null;
  chapter_difficulty?: string | null;
  priority_reason?: string;
}

interface StudyPlanData {
  plan_id: string;
  exam_name: string;
  exam_date: string;
  days_until_exam: number;
  daily_study_hours: number;
  preferred_study_time: string;
  weak_subjects: string[];
  strong_subjects: string[];
  academic_goal: string;
  exam_subjects?: ExamSubjectEntryUI[];
  subject_time_allocation_hours_per_week: Record<string, number>;
  subject_allocation_percentages: Record<string, number>;
  chapter_completion_targets: {
    subject: string;
    chapter: string;
    target_completion_date: string;
    priority: string;
    completion_status?: string;
    difficulty?: string;
  }[];
  daily_timetable: StudyTask[];
  today_combined_timeline?: StudyTask[];
  daily_checkin_completed?: boolean;
  daily_available_hours?: number;
  weekly_timetable: Record<string, StudyTask[]>;
  complete_exam_schedule?: StudyTask[];
  monthly_preparation_milestones: {
    week: string;
    focus: string;
    deliverable: string;
  }[];
  mock_exam_dates: string[];
  catch_up_schedule: StudyTask[];
}

export const SmartStudyPlannerView: React.FC<{
  onboarding: OnboardingState;
}> = ({ onboarding }) => {
  const curriculumSubjects = React.useMemo(
    () =>
      getCurriculumSubjects(
        onboarding.grade,
        onboarding.board,
        onboarding.stateName
      ),
    [onboarding.grade, onboarding.board, onboarding.stateName]
  );

  const [plan, setPlan] = React.useState<StudyPlanData | null>(null);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [examName, setExamName] = React.useState<string>(
    'Term-1 / Half-Yearly School Examination'
  );
  const [examDate, setExamDate] = React.useState<string>('2026-12-10');
  const [dailyHours, setDailyHours] = React.useState<number>(2.0);
  const [preferredTime, setPreferredTime] = React.useState<string>(
    'Evening (6 PM - 9 PM)'
  );
  const [weakSubjects, setWeakSubjects] = React.useState<string[]>([
    curriculumSubjects[0]?.name || 'Mathematics',
  ]);
  const [strongSubjects, setStrongSubjects] = React.useState<string[]>([
    curriculumSubjects[2]?.name || 'English',
  ]);
  const [academicGoal, setAcademicGoal] = React.useState<string>(
    'Complete all syllabus chapters on time and score 85%+ in weak subjects'
  );
  const [customChapterInput, setCustomChapterInput] = React.useState<string>('');
  const [activeTab, setActiveTab] = React.useState<
    'daily' | 'weekly' | 'complete' | 'monthly' | 'catchup'
  >('daily');
  const [selectedDay, setSelectedDay] = React.useState<string>('Monday');

  // + Add Subject Form & Dynamic Chapter Management States (Requirement 1)
  const [showAddSubjectForm, setShowAddSubjectForm] = React.useState<boolean>(false);
  const [editingSubjectId, setEditingSubjectId] = React.useState<string | undefined>(
    undefined
  );
  const [subjectFormName, setSubjectFormName] = React.useState<string>('Mathematics');
  const [subjectFormChaptersCount, setSubjectFormChaptersCount] = React.useState<number>(4);
  const [subjectFormExamDate, setSubjectFormExamDate] = React.useState<string>('2026-12-01');
  const [subjectFormExamTime, setSubjectFormExamTime] = React.useState<string>('9:30 AM - 12:30 PM');
  const [subjectFormMaxMarks, setSubjectFormMaxMarks] = React.useState<number>(100);
  const [subjectFormDifficulty, setSubjectFormDifficulty] = React.useState<
    'Easy' | 'Medium' | 'Difficult'
  >('Medium');
  const [subjectFormConfidence, setSubjectFormConfidence] = React.useState<string>('Okay');
  const [subjectFormChapters, setSubjectFormChapters] = React.useState<ExamChapterEntryUI[]>([
    {
      chapter_number: 1,
      chapter_name: 'Chapter 1',
      difficulty: 'Medium',
      completion_status: 'Not Started',
      additional_practice_needed: false,
      revision_requirements: 'Standard revision before exam',
    },
    {
      chapter_number: 2,
      chapter_name: 'Chapter 2',
      difficulty: 'Medium',
      completion_status: 'Not Started',
      additional_practice_needed: false,
      revision_requirements: 'Standard revision before exam',
    },
    {
      chapter_number: 3,
      chapter_name: 'Chapter 3',
      difficulty: 'Medium',
      completion_status: 'Not Started',
      additional_practice_needed: false,
      revision_requirements: 'Standard revision before exam',
    },
    {
      chapter_number: 4,
      chapter_name: 'Chapter 4',
      difficulty: 'Medium',
      completion_status: 'Not Started',
      additional_practice_needed: false,
      revision_requirements: 'Standard revision before exam',
    },
  ]);
  const [confirmDeleteSubjectId, setConfirmDeleteSubjectId] = React.useState<string | null>(
    null
  );

  // Editable Study Task States (Requirement 3)
  const [editingTaskId, setEditingTaskId] = React.useState<string | null>(null);
  const [editTaskDate, setEditTaskDate] = React.useState<string>('');
  const [editTaskTimeSlot, setEditTaskTimeSlot] = React.useState<string>('');
  const [editTaskChapter, setEditTaskChapter] = React.useState<string>('');

  // Daily Schedule Check-In & Personal Availability States
  const [dailySchedule, setDailySchedule] =
    React.useState<DailyScheduleDataUI | null>(null);
  const [scheduleActivities, setScheduleActivities] = React.useState<
    PersonalActivityItemUI[]
  >([]);
  const [wakeUpTime12h, setWakeUpTime12h] = React.useState<string>('6:30 AM');
  const [sleepTime12h, setSleepTime12h] = React.useState<string>('9:30 PM');
  const [currentTimeMidday12h, setCurrentTimeMidday12h] =
    React.useState<string>('');
  const [showActivityForm, setShowActivityForm] =
    React.useState<boolean>(false);
  const [editingActivityIndex, setEditingActivityIndex] = React.useState<
    number | null
  >(null);
  const [actFormName, setActFormName] = React.useState<string>('Tuition');
  const [actFormCategory, setActFormCategory] =
    React.useState<string>('Tuition');
  const [actFormStartTime, setActFormStartTime] =
    React.useState<string>('4:00 PM');
  const [actFormEndTime, setActFormEndTime] = React.useState<string>('5:00 PM');
  const [actFormLocation, setActFormLocation] = React.useState<string>('');
  const [actFormNotes, setActFormNotes] = React.useState<string>('');
  const [actFormRecurrence, setActFormRecurrence] = React.useState<
    'Only today' | 'Repeated on selected weekdays' | 'Repeated every day'
  >('Only today');
  const [actFormWeekdays, setActFormWeekdays] = React.useState<string[]>([
    'Mon',
    'Wed',
    'Fri',
  ]);
  const [checkinError, setCheckinError] = React.useState<string | null>(null);
  const [checkinSuccessMsg, setCheckinSuccessMsg] = React.useState<
    string | null
  >(null);

  const TIME_SLOTS_12H = React.useMemo(
    () => [
      '6:00 AM',
      '6:30 AM',
      '7:00 AM',
      '7:30 AM',
      '8:00 AM',
      '8:30 AM',
      '9:00 AM',
      '9:30 AM',
      '10:00 AM',
      '10:30 AM',
      '11:00 AM',
      '11:30 AM',
      '12:00 PM',
      '12:30 PM',
      '1:00 PM',
      '1:30 PM',
      '2:00 PM',
      '2:30 PM',
      '3:00 PM',
      '3:30 PM',
      '4:00 PM',
      '4:30 PM',
      '5:00 PM',
      '5:30 PM',
      '6:00 PM',
      '6:30 PM',
      '7:00 PM',
      '7:30 PM',
      '8:00 PM',
      '8:30 PM',
      '9:00 PM',
      '9:30 PM',
      '10:00 PM',
      '10:30 PM',
    ],
    []
  );

  const ACTIVITY_PRESETS = React.useMemo(
    () => [
      { label: '🏫 School', name: 'School', category: 'School', start: '8:30 AM', end: '2:30 PM' },
      { label: '📘 Tuition', name: 'Tuition', category: 'Tuition', start: '4:00 PM', end: '5:00 PM' },
      { label: '♟️ Chess classes', name: 'Chess class', category: 'Chess classes', start: '5:30 PM', end: '6:30 PM' },
      { label: '🎨 Drawing classes', name: 'Drawing class', category: 'Drawing classes', start: '7:00 PM', end: '8:00 PM' },
      { label: '⚽ Sports', name: 'Sports practice', category: 'Sports', start: '5:00 PM', end: '6:00 PM' },
      { label: '🎵 Music classes', name: 'Music class', category: 'Music classes', start: '6:00 PM', end: '7:00 PM' },
      { label: '🌟 Other extracurricular', name: 'Extracurricular class', category: 'Other extracurricular activities', start: '4:30 PM', end: '5:30 PM' },
      { label: '👨‍👩‍👧 Family commitments', name: 'Family time', category: 'Family commitments', start: '7:30 PM', end: '8:30 PM' },
      { label: '🚌 Travel time', name: 'School / Tuition Travel', category: 'Travel time', start: '3:30 PM', end: '4:00 PM' },
      { label: '🧘 Personal activities', name: 'Personal rest / hobby', category: 'Personal activities', start: '6:30 PM', end: '7:00 PM' },
      { label: '🔒 Mark Slot Unavailable', name: 'Unavailable Slot', category: 'Unavailable', start: '5:00 PM', end: '6:00 PM' },
    ],
    []
  );

  const handleDynamicChapterCountChange = (newCount: number) => {
    const clamped = Math.max(1, Math.min(50, newCount || 1));
    setSubjectFormChaptersCount(clamped);
    setSubjectFormChapters((prev) => {
      if (clamped === prev.length) return prev;
      if (clamped < prev.length) {
        return prev.slice(0, clamped).map((c, idx) => ({
          ...c,
          chapter_number: idx + 1,
        }));
      }
      const next = [...prev];
      for (let i = prev.length + 1; i <= clamped; i++) {
        next.push({
          chapter_number: i,
          chapter_name: `Chapter ${i}`,
          difficulty: subjectFormDifficulty,
          completion_status: 'Not Started',
          additional_practice_needed: false,
          revision_requirements: 'Standard revision before exam',
        });
      }
      return next;
    });
  };

  const openNewSubjectForm = () => {
    setEditingSubjectId(undefined);
    setSubjectFormName('');
    setSubjectFormChaptersCount(3);
    setSubjectFormExamDate('2026-12-05');
    setSubjectFormExamTime('9:30 AM - 12:30 PM');
    setSubjectFormMaxMarks(100);
    setSubjectFormDifficulty('Medium');
    setSubjectFormConfidence('Okay');
    setSubjectFormChapters([
      {
        chapter_number: 1,
        chapter_name: 'Chapter 1',
        difficulty: 'Medium',
        completion_status: 'Not Started',
        additional_practice_needed: false,
        revision_requirements: 'Standard revision before exam',
      },
      {
        chapter_number: 2,
        chapter_name: 'Chapter 2',
        difficulty: 'Medium',
        completion_status: 'Not Started',
        additional_practice_needed: false,
        revision_requirements: 'Standard revision before exam',
      },
      {
        chapter_number: 3,
        chapter_name: 'Chapter 3',
        difficulty: 'Medium',
        completion_status: 'Not Started',
        additional_practice_needed: false,
        revision_requirements: 'Standard revision before exam',
      },
    ]);
    setShowAddSubjectForm(true);
  };

  const openEditSubjectForm = (sub: ExamSubjectEntryUI) => {
    setEditingSubjectId(sub.subject_id);
    setSubjectFormName(sub.subject_name);
    setSubjectFormChaptersCount(sub.number_of_chapters);
    setSubjectFormExamDate(sub.exam_date);
    setSubjectFormExamTime(sub.exam_time || '9:30 AM - 12:30 PM');
    setSubjectFormMaxMarks(sub.maximum_marks || 100);
    setSubjectFormDifficulty(sub.subject_difficulty || 'Medium');
    setSubjectFormConfidence(sub.student_confidence_level || 'Okay');
    setSubjectFormChapters(
      sub.chapters && sub.chapters.length > 0
        ? sub.chapters.map((c, idx) => ({
          chapter_number: idx + 1,
          chapter_name: c.chapter_name,
          difficulty: c.difficulty || 'Medium',
          completion_status: c.completion_status || 'Not Started',
          additional_practice_needed: Boolean(c.additional_practice_needed),
          revision_requirements:
            c.revision_requirements || 'Standard revision before exam',
        }))
        : Array.from({ length: sub.number_of_chapters }, (_, idx) => ({
          chapter_number: idx + 1,
          chapter_name: `Chapter ${idx + 1}`,
          difficulty: sub.subject_difficulty || 'Medium',
          completion_status: 'Not Started',
          additional_practice_needed: false,
          revision_requirements: 'Standard revision before exam',
        }))
    );
    setShowAddSubjectForm(true);
  };

  const handleSaveExamSubject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subjectFormName.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(
        `/api/students/${onboarding.studentId}/study-plan/subjects`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            student_id: onboarding.studentId,
            auto_regenerate_timetable: true,
            subject: {
              subject_id: editingSubjectId,
              subject_name: subjectFormName.trim(),
              number_of_chapters: subjectFormChaptersCount,
              exam_date: subjectFormExamDate,
              exam_time: subjectFormExamTime || null,
              maximum_marks: subjectFormMaxMarks || null,
              subject_difficulty: subjectFormDifficulty,
              student_confidence_level: subjectFormConfidence || null,
              chapters: subjectFormChapters,
            },
          }),
        }
      );
      if (res.ok) {
        const updatedPlan: StudyPlanData = await res.json();
        setPlan(updatedPlan);
        setShowAddSubjectForm(false);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveExamSubject = async (subjectId: string) => {
    setLoading(true);
    try {
      const res = await fetch(
        `/api/students/${onboarding.studentId}/study-plan/subjects/${subjectId}?auto_regenerate=true`,
        { method: 'DELETE' }
      );
      if (res.ok) {
        const updatedPlan: StudyPlanData = await res.json();
        setPlan(updatedPlan);
        setConfirmDeleteSubjectId(null);
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchPlan = React.useCallback(async () => {
    setLoading(true);
    try {
      const [res, schedRes] = await Promise.all([
        fetch(`/api/students/${onboarding.studentId}/study-plan`),
        fetch(`/api/students/${onboarding.studentId}/daily-schedule`),
      ]);
      if (res.ok) {
        const data: StudyPlanData = await res.json();
        setPlan(data);
        setExamName(data.exam_name);
        setExamDate(data.exam_date);
        setDailyHours(data.daily_study_hours);
        setPreferredTime(data.preferred_study_time);
        setWeakSubjects(data.weak_subjects);
        setStrongSubjects(data.strong_subjects);
        setAcademicGoal(data.academic_goal);
      }
      if (schedRes.ok) {
        const sData: DailyScheduleDataUI = await schedRes.json();
        setDailySchedule(sData);
        setScheduleActivities(sData.activities || []);
        setWakeUpTime12h(sData.wake_up_time || '6:30 AM');
        setSleepTime12h(sData.sleep_time || '9:30 PM');
      }
    } finally {
      setLoading(false);
    }
  }, [onboarding.studentId]);

  const handleOpenAddActivity = (preset?: {
    name: string;
    category: string;
    start: string;
    end: string;
  }) => {
    setCheckinError(null);
    setEditingActivityIndex(null);
    setActFormName(preset?.name || '');
    setActFormCategory(preset?.category || 'Extracurricular');
    setActFormStartTime(preset?.start || '4:00 PM');
    setActFormEndTime(preset?.end || '5:00 PM');
    setActFormLocation('');
    setActFormNotes('');
    setActFormRecurrence('Only today');
    setActFormWeekdays(['Mon', 'Wed', 'Fri']);
    setShowActivityForm(true);
  };

  const handleOpenEditActivity = (act: PersonalActivityItemUI, idx: number) => {
    setCheckinError(null);
    setEditingActivityIndex(idx);
    setActFormName(act.activity_name);
    setActFormCategory(act.category || 'Extracurricular');
    setActFormStartTime(act.start_time);
    setActFormEndTime(act.end_time);
    setActFormLocation(act.location || '');
    setActFormNotes(act.notes || '');
    setActFormRecurrence(act.recurrence_type || 'Only today');
    setActFormWeekdays(
      act.recurring_weekdays && act.recurring_weekdays.length > 0
        ? act.recurring_weekdays
        : ['Mon', 'Wed', 'Fri']
    );
    setShowActivityForm(true);
  };

  const handleSaveActivityToList = (e: React.FormEvent) => {
    e.preventDefault();
    if (!actFormName.trim()) {
      setCheckinError('Please enter an activity name.');
      return;
    }
    const newItem: PersonalActivityItemUI = {
      activity_id:
        editingActivityIndex !== null
          ? scheduleActivities[editingActivityIndex]?.activity_id
          : `act_${Date.now()}`,
      activity_name: actFormName.trim(),
      category: actFormCategory,
      start_time: actFormStartTime,
      end_time: actFormEndTime,
      location: actFormLocation.trim(),
      notes: actFormNotes.trim(),
      recurrence_type: actFormRecurrence,
      recurring_weekdays:
        actFormRecurrence === 'Repeated every day'
          ? ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
          : actFormRecurrence === 'Repeated on selected weekdays'
            ? actFormWeekdays
            : [],
      is_cancelled_today: false,
    };

    if (editingActivityIndex !== null) {
      setScheduleActivities((prev) =>
        prev.map((item, i) => (i === editingActivityIndex ? newItem : item))
      );
    } else {
      setScheduleActivities((prev) => [...prev, newItem]);
    }
    setShowActivityForm(false);
    setEditingActivityIndex(null);
    setCheckinError(null);
  };

  const handleRemoveActivityFromList = (idx: number) => {
    setScheduleActivities((prev) => prev.filter((_, i) => i !== idx));
  };

  const handleToggleCancelActivityToday = (idx: number) => {
    setScheduleActivities((prev) =>
      prev.map((item, i) =>
        i === idx
          ? { ...item, is_cancelled_today: !item.is_cancelled_today }
          : item
      )
    );
  };

  const handleSubmitDailyScheduleCheckIn = async (freeAllDay = false) => {
    setLoading(true);
    setCheckinError(null);
    setCheckinSuccessMsg(null);
    try {
      const res = await fetch(
        `/api/students/${onboarding.studentId}/daily-schedule/check-in`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            student_id: onboarding.studentId,
            date_iso: dailySchedule?.date_iso || undefined,
            free_all_day: freeAllDay,
            wake_up_time: wakeUpTime12h,
            sleep_time: sleepTime12h,
            preferred_study_hours: dailyHours,
            current_time_12h: currentTimeMidday12h.trim() || null,
            activities: freeAllDay ? [] : scheduleActivities,
            auto_generate_daily_plan: true,
          }),
        }
      );
      if (!res.ok) {
        const errJson = await res.json().catch(() => null);
        const detail =
          errJson?.detail ||
          'Could not save schedule. Please check for overlapping times or invalid time ranges.';
        setCheckinError(
          typeof detail === 'string' ? detail : JSON.stringify(detail)
        );
        return;
      }
      const data = await res.json();
      const updatedSched: DailyScheduleDataUI = data.daily_schedule || data;
      setDailySchedule(updatedSched);
      setScheduleActivities(updatedSched.activities || []);
      if (data.study_plan) {
        setPlan(data.study_plan);
      } else {
        await fetchPlan();
      }
      setActiveTab('daily');
      setCheckinSuccessMsg(
        freeAllDay
          ? `Whole day marked as free! Generated your personalised daily plan (${updatedSched.available_study_hours} hrs available).`
          : `Daily schedule saved! Generated your personalised study plan around ${(updatedSched.activities || []).filter((a) => !a.is_cancelled_today)
            .length
          } activity commitment(s) (${updatedSched.available_study_hours} hrs available).`
      );
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchPlan();
  }, [fetchPlan]);

  const handleGeneratePlan = async () => {
    setLoading(true);
    try {
      const subjectChaptersMap: Record<string, string[]> = {};
      curriculumSubjects.forEach((s) => {
        subjectChaptersMap[s.name] = [...s.topics];
      });
      if (customChapterInput.trim() && curriculumSubjects[0]) {
        subjectChaptersMap[curriculumSubjects[0].name].push(
          customChapterInput.trim()
        );
      }

      const res = await fetch(
        `/api/students/${onboarding.studentId}/study-plan/generate`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            student_id: onboarding.studentId,
            exam_name: examName,
            exam_date: examDate,
            daily_study_hours: dailyHours,
            preferred_study_time: preferredTime,
            selected_subjects_and_chapters: subjectChaptersMap,
            exam_subjects: plan?.exam_subjects || [],
            weak_subjects: weakSubjects,
            strong_subjects: strongSubjects,
            academic_goal: academicGoal,
            preserve_completed_tasks: true,
          }),
        }
      );
      if (res.ok) {
        const data: StudyPlanData = await res.json();
        setPlan(data);
        setCustomChapterInput('');
      }
    } finally {
      setLoading(false);
    }
  };

  const toggleTask = async (
    taskId: string,
    completed: boolean,
    missed = false,
    postponed = false,
    newDateIso?: string,
    newTimeSlot?: string,
    newChapter?: string
  ) => {
    const res = await fetch(
      `/api/students/${onboarding.studentId}/study-plan/tasks/${taskId}`,
      {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          completed,
          missed,
          postponed,
          new_date_iso: newDateIso || null,
          new_time_slot: newTimeSlot || null,
          new_chapter: newChapter || null,
        }),
      }
    );
    if (res.ok) {
      setPlan(await res.json());
      setEditingTaskId(null);
      const schedRes = await fetch(
        `/api/students/${onboarding.studentId}/daily-schedule`
      );
      if (schedRes.ok) {
        setDailySchedule(await schedRes.json());
      }
    }
  };

  const triggerCatchUp = async () => {
    const res = await fetch(
      `/api/students/${onboarding.studentId}/study-plan/catch-up`,
      { method: 'POST' }
    );
    if (res.ok) {
      setPlan(await res.json());
      setActiveTab('catchup');
    }
  };

  const toggleWeakSubject = (subName: string) => {
    setWeakSubjects((prev) =>
      prev.includes(subName)
        ? prev.filter((s) => s !== subName)
        : [...prev, subName]
    );
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <RobotGuideTip
        tipId="study_planner"
        studentId={onboarding.studentId}
        title="Sparky's Study Planner Guide"
        message="Enter your school, tuition, or free hours first — SparkMinds AI fits realistic study sessions into your open time slots."
        mood="guiding"
      />
      {/* Midnight-Indigo Daily Schedule Check-In Header */}
      <div
        className="rounded-3xl border border-[#5146E5]/30 text-white p-6 shadow-lg space-y-5"
        style={{ background: 'linear-gradient(135deg, #101B35 0%, #232A6B 60%, #5146E5 100%)' }}
      >
        <div className="flex flex-wrap items-start justify-between gap-4 border-b border-white/10 pb-4">
          <div className="space-y-1.5">
            <div className="flex flex-wrap items-center gap-2">
              <span className="px-3 py-1 rounded-full bg-[#35D6E8]/15 border border-[#35D6E8]/40 text-[#35D6E8] text-[11px] font-extrabold uppercase tracking-wider">
                Daily Schedule • {dailySchedule?.weekday_name || 'Today'}
              </span>
              {dailySchedule?.checkin_completed && (
                <span className="px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-[11px] font-extrabold">
                  ✓ Confirmed
                </span>
              )}
            </div>
            <h2 className="text-xl md:text-2xl font-extrabold text-white tracking-tight">
              Plan your day around your real schedule.
            </h2>
            <p className="text-xs text-slate-300 max-w-xl">
              Add school, tuition, or activities — or mark today free — and we&apos;ll fit focused study blocks into your open slots.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            <button
              type="button"
              onClick={() => handleOpenAddActivity()}
              className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-[#35D6E8] text-[#101B35] hover:bg-cyan-300 text-xs font-extrabold shadow-sm transition min-h-[42px]"
            >
              <Plus className="w-4 h-4" />
              <span>Add Activity</span>
            </button>
            <button
              type="button"
              disabled={loading}
              onClick={() => handleSubmitDailyScheduleCheckIn(true)}
              className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-white text-xs font-extrabold transition min-h-[42px]"
            >
              I&apos;m Free All Day — Generate Plan
            </button>
            <button
              type="button"
              disabled={loading}
              onClick={() => handleSubmitDailyScheduleCheckIn(false)}
              className="px-5 py-2.5 rounded-xl bg-[#35D6E8] hover:bg-cyan-300 text-[#101B35] text-xs font-extrabold shadow-lg shadow-cyan-500/25 transition"
            >
              {loading
                ? 'Calculating & Generating...'
                : '⚡ Generate My Daily Plan'}
            </button>
          </div>
        </div>

        {/* Live Availability KPI Strip */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
          <div className="p-3.5 rounded-2xl bg-white/10 border border-white/15 space-y-1">
            <div className="text-[10px] uppercase font-extrabold text-[#35D6E8]">
              Available Study Hours Today
            </div>
            <div className="text-lg font-extrabold text-white">
              {dailySchedule?.available_study_hours ?? 4.5} hrs (
              {dailySchedule?.total_available_study_minutes ?? 270} mins)
            </div>
            <div className="text-[11px] text-slate-300">
              Wake: {wakeUpTime12h} • Sleep: {sleepTime12h}
            </div>
          </div>

          <div className="p-3.5 rounded-2xl bg-white/10 border border-white/15 space-y-1">
            <div className="text-[10px] uppercase font-extrabold text-amber-300">
              Unavailable Time Slots
            </div>
            <div className="text-sm font-extrabold text-white">
              {scheduleActivities.filter((a) => !a.is_cancelled_today).length}{' '}
              Active Commitment(s)
            </div>
            <div className="text-[11px] text-slate-300 truncate">
              {scheduleActivities
                .filter((a) => !a.is_cancelled_today)
                .map((a) => `${a.activity_name} (${a.start_time} - ${a.end_time})`)
                .join(' • ') || 'None — Entire day free'}
            </div>
          </div>

          <div className="p-3.5 rounded-2xl bg-white/10 border border-white/15 space-y-1">
            <div className="text-[10px] uppercase font-extrabold text-emerald-300">
              Available Free Study Windows
            </div>
            <div className="text-sm font-extrabold text-white">
              {dailySchedule?.available_time_windows?.length ?? 2} Free Window(s)
            </div>
            <div className="text-[11px] text-slate-300 truncate">
              {dailySchedule?.available_time_windows
                ?.map((w) => `${w.start_time} – ${w.end_time}`)
                .join(' • ') || '6:30 AM – 9:30 PM'}
            </div>
          </div>

          <div className="p-3.5 rounded-2xl bg-white/10 border border-white/15 space-y-1.5">
            <div className="text-[10px] uppercase font-extrabold text-[#35D6E8]">
              Changes During the Day (Mid-Day Sync)
            </div>
            <div className="flex items-center gap-1.5">
              <select
                value={currentTimeMidday12h}
                onChange={(e) => setCurrentTimeMidday12h(e.target.value)}
                aria-label="Current time for mid-day reschedule"
                className="flex-1 rounded-lg bg-[#101B35] border border-white/25 text-white px-2 py-1 text-[11px] font-bold"
              >
                <option value=""> Full Day (From {wakeUpTime12h})</option>
                {TIME_SLOTS_12H.map((t) => (
                  <option key={t} value={t}>
                    From {t} onwards
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={() => handleSubmitDailyScheduleCheckIn(false)}
                className="px-2.5 py-1 rounded-lg bg-[#35D6E8] text-[#101B35] font-extrabold text-[11px] whitespace-nowrap"
              >
                Recalculate
              </button>
            </div>
          </div>
        </div>

        {/* Quick Preset Activity Pills */}
        <div className="space-y-1.5">
          <div className="text-[11px] font-extrabold text-[#35D6E8] uppercase tracking-wider">
            Quick Add Personal Activity or Unavailable Time Slot:
          </div>
          <div className="flex flex-wrap gap-2">
            {ACTIVITY_PRESETS.map((p) => (
              <button
                key={p.label}
                type="button"
                onClick={() => handleOpenAddActivity(p)}
                className="px-3 py-1.5 rounded-xl bg-white/10 hover:bg-[#35D6E8] hover:text-[#101B35] border border-white/20 text-white text-xs font-bold transition"
              >
                + {p.label}
              </button>
            ))}
          </div>
        </div>

        {checkinError && (
          <div className="p-3.5 rounded-2xl bg-rose-500/20 border border-rose-400 text-rose-100 text-xs font-extrabold">
            ⚠️ Schedule Validation Alert: {checkinError}
          </div>
        )}

        {checkinSuccessMsg && (
          <div className="p-3.5 rounded-2xl bg-emerald-500/20 border border-emerald-400 text-emerald-100 text-xs font-extrabold">
            ✓ {checkinSuccessMsg}
          </div>
        )}

        {/* + Add / Edit Activity Modal Form */}
        {showActivityForm && (
          <form
            onSubmit={handleSaveActivityToList}
            className="p-5 rounded-2xl bg-white text-slate-900 border-2 border-[#35D6E8] space-y-4 text-xs shadow-lg"
          >
            <div className="flex items-center justify-between border-b border-slate-200 pb-2.5">
              <div>
                <h3 className="text-sm font-extrabold text-[#101B35]">
                  {editingActivityIndex !== null
                    ? '✏️ Edit Activity / Unavailable Slot'
                    : '➕ Add Personal Activity or Unavailable Time Slot'}
                </h3>
                <p className="text-[11px] text-slate-600">
                  SparkMinds AI will never schedule study sessions during this time slot.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setShowActivityForm(false)}
                className="text-xs font-extrabold text-slate-500 hover:text-slate-900"
              >
                Cancel ✕
              </button>
            </div>

            <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-3">
              <div>
                <label className="block font-extrabold text-slate-800 mb-1">
                  Activity Name (Manual Entry) *
                </label>
                <input
                  type="text"
                  required
                  value={actFormName}
                  onChange={(e) => setActFormName(e.target.value)}
                  placeholder="e.g., Tuition, Chess class, School"
                  className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-bold text-slate-900"
                />
              </div>

              <div>
                <label className="block font-extrabold text-slate-800 mb-1">
                  Category
                </label>
                <select
                  value={actFormCategory}
                  onChange={(e) => setActFormCategory(e.target.value)}
                  className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-bold text-slate-900"
                >
                  <option value="School">School</option>
                  <option value="Tuition">Tuition</option>
                  <option value="Chess classes">Chess classes</option>
                  <option value="Drawing classes">Drawing classes</option>
                  <option value="Sports">Sports</option>
                  <option value="Music classes">Music classes</option>
                  <option value="Other extracurricular activities">
                    Other extracurricular activities
                  </option>
                  <option value="Family commitments">Family commitments</option>
                  <option value="Travel time">Travel time</option>
                  <option value="Personal activities">Personal activities</option>
                  <option value="Unavailable">Unavailable Slot</option>
                </select>
              </div>

              <div>
                <label className="block font-extrabold text-slate-800 mb-1">
                  Start Time (12-Hour AM/PM) *
                </label>
                <select
                  value={actFormStartTime}
                  onChange={(e) => setActFormStartTime(e.target.value)}
                  className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-bold text-slate-900"
                >
                  {TIME_SLOTS_12H.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-extrabold text-slate-800 mb-1">
                  End Time (12-Hour AM/PM) *
                </label>
                <select
                  value={actFormEndTime}
                  onChange={(e) => setActFormEndTime(e.target.value)}
                  className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-bold text-slate-900"
                >
                  {TIME_SLOTS_12H.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-extrabold text-slate-800 mb-1">
                  Location (Optional)
                </label>
                <input
                  type="text"
                  value={actFormLocation}
                  onChange={(e) => setActFormLocation(e.target.value)}
                  placeholder="e.g., Coaching Centre, Room 4"
                  className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-semibold text-slate-900"
                />
              </div>

              <div>
                <label className="block font-extrabold text-slate-800 mb-1">
                  Notes (Optional)
                </label>
                <input
                  type="text"
                  value={actFormNotes}
                  onChange={(e) => setActFormNotes(e.target.value)}
                  placeholder="e.g., Bring workbook"
                  className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-semibold text-slate-900"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block font-extrabold text-slate-800 mb-1">
                  Remember Recurring Activity?
                </label>
                <select
                  value={actFormRecurrence}
                  onChange={(e) =>
                    setActFormRecurrence(
                      e.target.value as
                      | 'Only today'
                      | 'Repeated on selected weekdays'
                      | 'Repeated every day'
                    )
                  }
                  className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-bold text-slate-900"
                >
                  <option value="Only today">Only today</option>
                  <option value="Repeated on selected weekdays">
                    Repeated on selected weekdays
                  </option>
                  <option value="Repeated every day">Repeated every day</option>
                </select>
              </div>
            </div>

            {actFormRecurrence === 'Repeated on selected weekdays' && (
              <div className="flex flex-wrap items-center gap-2 pt-1">
                <span className="font-extrabold text-slate-700">
                  Select Weekdays:
                </span>
                {(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] as const).map(
                  (d) => {
                    const active = actFormWeekdays.includes(d);
                    return (
                      <button
                        key={d}
                        type="button"
                        onClick={() =>
                          setActFormWeekdays((prev) =>
                            prev.includes(d)
                              ? prev.filter((x) => x !== d)
                              : [...prev, d]
                          )
                        }
                        className={`px-3 py-1 rounded-lg font-extrabold text-xs border ${active
                            ? 'bg-[#101B35] text-[#35D6E8] border-[#101B35]'
                            : 'bg-slate-100 text-slate-700 border-slate-300'
                          }`}
                      >
                        {d}
                      </button>
                    );
                  }
                )}
              </div>
            )}

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowActivityForm(false)}
                className="px-4 py-2 rounded-xl border border-slate-300 bg-white text-slate-700 font-bold"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-5 py-2 rounded-xl bg-[#101B35] hover:bg-slate-800 text-[#35D6E8] font-extrabold shadow-sm"
              >
                {editingActivityIndex !== null
                  ? 'Update Activity in Today’s List'
                  : 'Add Activity to Today’s Schedule'}
              </button>
            </div>
          </form>
        )}

        {/* List of Today's Activities (Including Pre-Filled Recurring Activities) */}
        <div className="space-y-2">
          <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
            <span className="font-extrabold text-white">
              📋 Today&apos;s Personal Schedule & Recurring Commitments ({scheduleActivities.length}):
            </span>
            <span className="text-[11px] text-slate-300">
              Class cancelled or postponed today? Toggle &ldquo;Cancel Today&rdquo; or Edit times and click &ldquo;Generate My Daily Plan&rdquo;.
            </span>
          </div>

          {scheduleActivities.length === 0 ? (
            <div className="p-4 rounded-2xl bg-white/5 border border-white/15 text-xs text-slate-300 flex flex-wrap items-center justify-between gap-2">
              <span>
                No personal activities entered for today — SparkMinds AI will treat your day as free between {wakeUpTime12h} and {sleepTime12h}.
              </span>
              <button
                type="button"
                onClick={() => handleOpenAddActivity()}
                className="px-3 py-1.5 rounded-xl bg-[#35D6E8] text-[#101B35] font-extrabold text-xs"
              >
                + Add Activity
              </button>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 gap-2.5">
              {scheduleActivities.map((act, idx) => (
                <div
                  key={act.activity_id || idx}
                  className={`p-3.5 rounded-2xl border flex flex-wrap items-center justify-between gap-2 text-xs ${act.is_cancelled_today
                      ? 'bg-white/5 border-white/10 opacity-60 line-through'
                      : 'bg-white/10 border-[#35D6E8]/30'
                    }`}
                >
                  <div className="space-y-0.5">
                    <div className="flex flex-wrap items-center gap-2 font-extrabold text-white">
                      <span className="text-[#35D6E8]">
                        {act.start_time} – {act.end_time}
                      </span>
                      <span>•</span>
                      <span>{act.activity_name}</span>
                      <span className="px-2 py-0.5 rounded-full bg-white/15 text-[10px]">
                        {act.category}
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-300">
                      {act.recurrence_type !== 'Only today' && (
                        <span className="text-emerald-300 font-bold mr-2">
                          ↻ {act.recurrence_type}
                          {act.recurring_weekdays?.length
                            ? ` (${act.recurring_weekdays.join(', ')})`
                            : ''}
                        </span>
                      )}
                      {act.location && <span>📍 {act.location} </span>}
                      {act.notes && <span>• {act.notes}</span>}
                    </div>
                  </div>

                  <div className="flex items-center gap-1.5">
                    <button
                      type="button"
                      onClick={() => handleOpenEditActivity(act, idx)}
                      className="px-2.5 py-1 rounded-lg bg-white/15 hover:bg-white/25 text-white font-bold text-[11px]"
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      onClick={() => handleToggleCancelActivityToday(idx)}
                      className="px-2.5 py-1 rounded-lg bg-amber-400/20 hover:bg-amber-400/30 text-amber-200 font-bold text-[11px]"
                    >
                      {act.is_cancelled_today ? 'Restore Today' : 'Cancel Today'}
                    </button>
                    <button
                      type="button"
                      onClick={() => handleRemoveActivityFromList(idx)}
                      className="px-2.5 py-1 rounded-lg bg-rose-500/25 hover:bg-rose-500/40 text-rose-200 font-bold text-[11px]"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Study Plan Configuration Card */}
      <div className="eduspark-card rounded-3xl p-6 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-100">
          <div>
            <span className="text-xs font-extrabold uppercase text-blue-600">
              Intelligent Study Planning Engine • Grade {onboarding.grade}{' '}
              {onboarding.board}
            </span>
            <h2 className="text-xl font-extrabold text-slate-900">
              Smart Study Planner & Exam Preparation Timetable
            </h2>
            <p className="text-xs text-slate-600">
              Strictly respects your available daily study hours, weights weak subjects higher, includes restorative breaks, and sources chapters directly from your selected {onboarding.board} curriculum.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={openNewSubjectForm}
              className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-gradient-to-r from-[#2563EB] to-[#7C3AED] hover:opacity-95 text-white text-xs font-extrabold shadow-md transition"
            >
              <Plus className="w-4 h-4" />
              <span>+ Add Subject</span>
            </button>
            <button
              onClick={triggerCatchUp}
              className="px-4 py-2.5 rounded-xl bg-amber-100 hover:bg-amber-200 text-amber-950 text-xs font-extrabold"
            >
              ⚡ Generate Catch-Up Schedule for Missed Sessions
            </button>
          </div>
        </div>

        {/* + ADD SUBJECT & DYNAMIC CHAPTER MANAGEMENT FORM (Requirement 1) */}
        {showAddSubjectForm && (
          <form
            onSubmit={handleSaveExamSubject}
            className="p-5 rounded-2xl bg-gradient-to-br from-blue-50/90 via-white to-violet-50/80 border-2 border-blue-300 space-y-4 text-xs shadow-md"
          >
            <div className="flex items-center justify-between border-b border-blue-200 pb-2.5">
              <div>
                <h3 className="text-sm font-extrabold text-slate-900">
                  {editingSubjectId
                    ? '✏️ Edit Subject & Individual Exam Date'
                    : '➕ Add Subject to Exam Study Planner'}
                </h3>
                <p className="text-[11px] text-slate-600">
                  Enter your actual subject name, number of chapters, individual exam date, and chapter details. We never invent syllabus chapters.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setShowAddSubjectForm(false)}
                className="text-xs font-extrabold text-slate-500 hover:text-slate-900"
              >
                Cancel ✕
              </button>
            </div>

            <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-3">
              <div>
                <label className="block font-extrabold text-slate-800 mb-1">
                  Subject Name (Manual Entry Allowed) *
                </label>
                <input
                  type="text"
                  required
                  value={subjectFormName}
                  onChange={(e) => setSubjectFormName(e.target.value)}
                  placeholder="e.g., Mathematics, Science, Hindi"
                  className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-bold"
                />
              </div>
              <div>
                <label className="block font-extrabold text-slate-800 mb-1">
                  Number of Chapters *
                </label>
                <input
                  type="number"
                  min={1}
                  max={50}
                  required
                  value={subjectFormChaptersCount}
                  onChange={(e) =>
                    handleDynamicChapterCountChange(Number(e.target.value) || 1)
                  }
                  className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-bold"
                />
              </div>
              <div>
                <label className="block font-extrabold text-slate-800 mb-1">
                  Individual Exam Date *
                </label>
                <input
                  type="date"
                  required
                  value={subjectFormExamDate}
                  onChange={(e) => setSubjectFormExamDate(e.target.value)}
                  className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-bold"
                />
              </div>
              <div>
                <label className="block font-extrabold text-slate-800 mb-1">
                  Exam Time (Optional • 12-Hr AM/PM)
                </label>
                <input
                  type="text"
                  value={subjectFormExamTime}
                  onChange={(e) => setSubjectFormExamTime(e.target.value)}
                  placeholder="e.g., 9:30 AM - 12:30 PM"
                  className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-bold"
                />
              </div>
              <div>
                <label className="block font-extrabold text-slate-800 mb-1">
                  Maximum Marks (Optional)
                </label>
                <input
                  type="number"
                  min={1}
                  max={500}
                  value={subjectFormMaxMarks}
                  onChange={(e) =>
                    setSubjectFormMaxMarks(Number(e.target.value) || 100)
                  }
                  className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-bold"
                />
              </div>
              <div>
                <label className="block font-extrabold text-slate-800 mb-1">
                  Subject Difficulty *
                </label>
                <select
                  value={subjectFormDifficulty}
                  onChange={(e) =>
                    setSubjectFormDifficulty(
                      e.target.value as 'Easy' | 'Medium' | 'Difficult'
                    )
                  }
                  className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-bold"
                >
                  <option value="Easy">Easy</option>
                  <option value="Medium">Medium</option>
                  <option value="Difficult">Difficult</option>
                </select>
              </div>
              <div>
                <label className="block font-extrabold text-slate-800 mb-1">
                  Student Confidence Level (Optional)
                </label>
                <select
                  value={subjectFormConfidence}
                  onChange={(e) => setSubjectFormConfidence(e.target.value)}
                  className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-bold"
                >
                  <option value="Strong">Strong</option>
                  <option value="Okay">Okay</option>
                  <option value="Need help">Need help</option>
                </select>
              </div>
            </div>

            {/* Dynamic Chapter Rows */}
            <div className="space-y-2 pt-2 border-t border-blue-200">
              <div className="font-extrabold text-slate-900">
                Dynamic Chapter Management ({subjectFormChapters.length} Chapter
                {subjectFormChapters.length === 1 ? '' : 's'}):
              </div>
              <div className="max-h-72 overflow-y-auto space-y-2 pr-1">
                {subjectFormChapters.map((ch, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-xl bg-white border border-slate-200 grid sm:grid-cols-2 md:grid-cols-6 gap-2 items-center"
                  >
                    <div className="md:col-span-2">
                      <label className="block text-[10px] font-bold text-slate-500">
                        Chapter #{idx + 1} Name
                      </label>
                      <input
                        type="text"
                        value={ch.chapter_name}
                        onChange={(e) => {
                          const val = e.target.value;
                          setSubjectFormChapters((prev) =>
                            prev.map((item, i) =>
                              i === idx ? { ...item, chapter_name: val } : item
                            )
                          );
                        }}
                        className="w-full rounded-lg border border-slate-300 px-2.5 py-1 text-xs font-bold"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold text-slate-500">
                        Difficulty
                      </label>
                      <select
                        value={ch.difficulty}
                        onChange={(e) => {
                          const val = e.target.value as
                            | 'Easy'
                            | 'Medium'
                            | 'Difficult';
                          setSubjectFormChapters((prev) =>
                            prev.map((item, i) =>
                              i === idx ? { ...item, difficulty: val } : item
                            )
                          );
                        }}
                        className="w-full rounded-lg border border-slate-300 px-2 py-1 text-xs font-bold"
                      >
                        <option value="Easy">Easy</option>
                        <option value="Medium">Medium</option>
                        <option value="Difficult">Difficult</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold text-slate-500">
                        Status
                      </label>
                      <select
                        value={ch.completion_status}
                        onChange={(e) => {
                          const val = e.target.value as
                            | 'Not Started'
                            | 'In Progress'
                            | 'Completed';
                          setSubjectFormChapters((prev) =>
                            prev.map((item, i) =>
                              i === idx
                                ? { ...item, completion_status: val }
                                : item
                            )
                          );
                        }}
                        className="w-full rounded-lg border border-slate-300 px-2 py-1 text-xs font-bold"
                      >
                        <option value="Not Started">Not Started</option>
                        <option value="In Progress">In Progress</option>
                        <option value="Completed">Completed</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold text-slate-500">
                        Revision Notes
                      </label>
                      <input
                        type="text"
                        value={ch.revision_requirements}
                        onChange={(e) => {
                          const val = e.target.value;
                          setSubjectFormChapters((prev) =>
                            prev.map((item, i) =>
                              i === idx
                                ? { ...item, revision_requirements: val }
                                : item
                            )
                          );
                        }}
                        className="w-full rounded-lg border border-slate-300 px-2 py-1 text-xs font-semibold"
                      />
                    </div>
                    <div className="flex items-center pt-3">
                      <label className="inline-flex items-center gap-1.5 cursor-pointer font-bold text-slate-700">
                        <input
                          type="checkbox"
                          checked={ch.additional_practice_needed}
                          onChange={(e) => {
                            const checked = e.target.checked;
                            setSubjectFormChapters((prev) =>
                              prev.map((item, i) =>
                                i === idx
                                  ? {
                                    ...item,
                                    additional_practice_needed: checked,
                                  }
                                  : item
                              )
                            );
                          }}
                          className="rounded border-slate-300 text-blue-600"
                        />
                        <span className="text-[11px]">Extra Practice</span>
                      </label>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowAddSubjectForm(false)}
                className="px-4 py-2 rounded-xl border border-slate-300 bg-white text-slate-700 font-bold"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-5 py-2 rounded-xl bg-gradient-to-r from-[#2563EB] to-[#7C3AED] text-white font-extrabold shadow-sm"
              >
                {loading
                  ? 'Saving & Updating Timetable...'
                  : 'Save Subject & Update Automatic Exam Timetable →'}
              </button>
            </div>
          </form>
        )}

        {/* INDIVIDUAL SUBJECT EXAM DATES TABLE (Requirement 1) */}
        {plan && plan.exam_subjects && plan.exam_subjects.length > 0 && (
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-3 text-xs">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="text-sm font-extrabold text-slate-900">
                📚 Added Exam Subjects & Individual Exam Dates ({plan.exam_subjects.length})
              </h3>
              <span className="text-[11px] font-bold text-emerald-700">
                ✓ Timetable automatically prioritises sooner exams & never schedules after a subject&apos;s exam date
              </span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 text-[11px] uppercase text-slate-500 font-extrabold">
                    <th className="py-2 px-3">Subject</th>
                    <th className="py-2 px-3">Chapters</th>
                    <th className="py-2 px-3">Individual Exam Date</th>
                    <th className="py-2 px-3">Exam Time (12-Hr)</th>
                    <th className="py-2 px-3">Difficulty</th>
                    <th className="py-2 px-3">Max Marks</th>
                    <th className="py-2 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200/70">
                  {plan.exam_subjects.map((sub) => (
                    <tr key={sub.subject_id || sub.subject_name} className="bg-white/70">
                      <td className="py-2.5 px-3 font-extrabold text-slate-900">
                        {sub.subject_name}
                      </td>
                      <td className="py-2.5 px-3 font-bold text-blue-700">
                        {sub.number_of_chapters} ch (
                        {
                          (sub.chapters || []).filter(
                            (c) => c.completion_status === 'Completed'
                          ).length
                        }{' '}
                        done)
                      </td>
                      <td className="py-2.5 px-3 font-extrabold text-amber-900">
                        {sub.exam_date}
                      </td>
                      <td className="py-2.5 px-3 font-semibold text-slate-700">
                        {formatTimeRange12Hour(sub.exam_time || '9:30 AM - 12:30 PM')}
                      </td>
                      <td className="py-2.5 px-3">
                        <span
                          className={`px-2 py-0.5 rounded-full font-extrabold text-[10px] ${sub.subject_difficulty === 'Difficult'
                              ? 'bg-rose-100 text-rose-800'
                              : sub.subject_difficulty === 'Medium'
                                ? 'bg-amber-100 text-amber-800'
                                : 'bg-emerald-100 text-emerald-800'
                            }`}
                        >
                          {sub.subject_difficulty}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 font-bold text-slate-700">
                        {sub.maximum_marks || 100}
                      </td>
                      <td className="py-2.5 px-3 text-right space-x-1.5">
                        <button
                          type="button"
                          onClick={() => openEditSubjectForm(sub)}
                          className="px-2.5 py-1 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 font-extrabold text-[11px]"
                        >
                          Edit
                        </button>
                        {confirmDeleteSubjectId === sub.subject_id ? (
                          <span className="inline-flex items-center gap-1">
                            <button
                              type="button"
                              onClick={() =>
                                sub.subject_id &&
                                handleRemoveExamSubject(sub.subject_id)
                              }
                              className="px-2 py-1 rounded-lg bg-rose-600 text-white font-extrabold text-[10px]"
                            >
                              Confirm Remove
                            </button>
                            <button
                              type="button"
                              onClick={() => setConfirmDeleteSubjectId(null)}
                              className="px-2 py-1 rounded-lg bg-slate-200 text-slate-700 font-bold text-[10px]"
                            >
                              Cancel
                            </button>
                          </span>
                        ) : (
                          <button
                            type="button"
                            onClick={() =>
                              setConfirmDeleteSubjectId(sub.subject_id || null)
                            }
                            className="px-2.5 py-1 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-700 font-extrabold text-[11px]"
                          >
                            Remove
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          <div>
            <label className="block font-bold text-slate-700 mb-1">
              Target Examination Name
            </label>
            <input
              type="text"
              value={examName}
              onChange={(e) => setExamName(e.target.value)}
              className="w-full rounded-xl border border-slate-300 px-3 py-2 font-semibold"
            />
          </div>

          <div>
            <label className="block font-bold text-slate-700 mb-1">
              Examination Date
            </label>
            <input
              type="date"
              value={examDate}
              onChange={(e) => setExamDate(e.target.value)}
              className="w-full rounded-xl border border-slate-300 px-3 py-2 font-semibold"
            />
          </div>

          <div>
            <label className="block font-bold text-slate-700 mb-1">
              Available Daily Study Hours ({dailyHours} hrs/day)
            </label>
            <input
              type="number"
              step="0.5"
              min="0.5"
              max="8"
              value={dailyHours}
              onChange={(e) =>
                setDailyHours(Math.max(0.5, Number(e.target.value) || 2))
              }
              className="w-full rounded-xl border border-slate-300 px-3 py-2 font-semibold"
            />
          </div>

          <div>
            <label className="block font-bold text-slate-700 mb-1">
              Preferred Study Time (12-Hour AM/PM)
            </label>
            <select
              value={preferredTime}
              onChange={(e) => setPreferredTime(e.target.value)}
              className="w-full rounded-xl border border-slate-300 px-3 py-2 font-semibold"
            >
              <option value="Morning (6 AM - 9 AM)">
                Morning (6:00 AM - 9:00 AM)
              </option>
              <option value="Afternoon (3 PM - 6 PM)">
                Afternoon (3:00 PM - 6:00 PM)
              </option>
              <option value="Evening (6 PM - 9 PM)">
                Evening (6:00 PM - 9:00 PM)
              </option>
              <option value="Flexible">Flexible (6:00 PM - 9:00 PM)</option>
            </select>
          </div>
        </div>

        {/* Weak Subjects Selector & Optional School Syllabus Chapter Addition */}
        <div className="grid md:grid-cols-2 gap-4 text-xs pt-1">
          <div>
            <label className="block font-bold text-slate-700 mb-1.5">
              Select Priority / Weak Subjects (Receives Higher Time Allocation):
            </label>
            <div className="flex flex-wrap gap-2">
              {curriculumSubjects.map((sub) => {
                const isWeak = weakSubjects.includes(sub.name);
                return (
                  <button
                    key={sub.code}
                    type="button"
                    onClick={() => toggleWeakSubject(sub.name)}
                    className={`px-3 py-1.5 rounded-xl border font-bold transition ${isWeak
                        ? 'border-2 border-amber-500 bg-amber-50 text-amber-950'
                        : 'border-slate-200 bg-slate-50 text-slate-700'
                      }`}
                  >
                    {isWeak ? '🔥 Weak Focus: ' : ''}
                    {sub.name}
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <label className="block font-bold text-slate-700 mb-1.5">
              Add Specific School Syllabus Chapter (Optional — We Never Invent Chapters):
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={customChapterInput}
                onChange={(e) => setCustomChapterInput(e.target.value)}
                placeholder="e.g., Chapter 4: Simple Equations"
                className="flex-1 rounded-xl border border-slate-300 px-3 py-1.5"
              />
              <button
                type="button"
                onClick={handleGeneratePlan}
                disabled={loading}
                className="px-5 py-2 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-extrabold shadow-sm"
              >
                {loading ? 'Generating...' : 'Regenerate & Save Study Plan'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {plan && (
        <>
          {/* Subject-Wise Time Allocation & Mock Exam Dates */}
          <div className="grid md:grid-cols-3 gap-4">
            <div className="md:col-span-2 bg-white border border-slate-200 rounded-3xl p-5 shadow-sm space-y-3">
              <h3 className="text-sm font-extrabold text-slate-900">
                ⚖️ Subject-Wise Weekly Time Allocation (Weak Subjects Weighted Higher)
              </h3>
              <div className="space-y-2.5 text-xs">
                {Object.entries(
                  plan.subject_time_allocation_hours_per_week
                ).map(([sub, hrs]) => {
                  const pct = plan.subject_allocation_percentages[sub] || 25;
                  const isWeak = plan.weak_subjects.includes(sub);
                  return (
                    <div key={sub} className="space-y-1">
                      <div className="flex justify-between font-bold">
                        <span className="text-slate-900">
                          {sub}{' '}
                          {isWeak && (
                            <span className="text-amber-700 font-extrabold">
                              (Priority Weak Subject Boost)
                            </span>
                          )}
                        </span>
                        <span className="text-blue-700">
                          {hrs} hrs/week ({pct}%)
                        </span>
                      </div>
                      <div className="w-full h-2.5 rounded-full bg-slate-100 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${isWeak ? 'bg-amber-500' : 'bg-blue-600'
                            }`}
                          style={{ width: `${Math.min(100, pct)}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-3xl p-5 shadow-sm space-y-3 text-xs">
              <h3 className="text-sm font-extrabold text-slate-900">
                🗓️ Scheduled Mock Exam Dates
              </h3>
              <p className="text-slate-600">
                Countdown: <strong>{plan.days_until_exam} days</strong> until{' '}
                {plan.exam_name}
              </p>
              <div className="space-y-2">
                {plan.mock_exam_dates.map((dt, idx) => (
                  <div
                    key={idx}
                    className="p-2.5 rounded-xl bg-violet-50 border border-violet-200 font-bold text-violet-950 flex flex-wrap items-center justify-between gap-1"
                  >
                    <span>Mock Test #{idx + 1}</span>
                    <span>
                      {formatExamSchedule12Hour(
                        dt,
                        idx % 2 === 0 ? '09:30 - 11:00' : '14:30 - 16:00'
                      )}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Timetable Tabs: Daily | Weekly | Complete Exam Schedule | Monthly | Catch-Up */}
          <div className="eduspark-card rounded-3xl p-6 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-3">
              <div className="flex flex-wrap gap-2">
                {(
                  [
                    { id: 'daily', label: 'Daily Timetable' },
                    { id: 'weekly', label: 'Weekly Timetable (7 Days)' },
                    {
                      id: 'complete',
                      label: `Complete Exam Schedule (${(plan.complete_exam_schedule || []).length
                        })`,
                    },
                    { id: 'monthly', label: 'Monthly Preparation & Chapter Targets' },
                    {
                      id: 'catchup',
                      label: `Catch-Up Schedule (${plan.catch_up_schedule.length})`,
                    },
                  ] as const
                ).map((t) => (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() => setActiveTab(t.id)}
                    className={`px-4 py-2 rounded-xl text-xs font-extrabold transition ${activeTab === t.id
                        ? 'bg-[#2563EB] text-white'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                      }`}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
              <span className="text-xs font-bold text-emerald-700">
                ✓ Daily Study Limit Strictly Respected: {plan.daily_study_hours}{' '}
                hrs ({plan.daily_study_hours * 60} mins) + Restorative Breaks • Zero Overlaps
              </span>
            </div>

            {activeTab === 'daily' && (
              <div className="space-y-3">
                {dailySchedule && !dailySchedule.checkin_completed && (
                  <div className="p-4 rounded-2xl bg-amber-50 border-2 border-amber-300 flex flex-wrap items-center justify-between gap-3 text-xs">
                    <div className="space-y-0.5">
                      <div className="font-extrabold text-amber-950">
                        ☀️ Daily Schedule Check-In Pending for Today ({dailySchedule.weekday_name}, {dailySchedule.date_iso})
                      </div>
                      <div className="text-amber-900">
                        Review your pre-filled recurring activities above (or add today&apos;s classes) and click <strong>Generate My Daily Plan</strong> so SparkMinds AI schedules around your personal commitments.
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleSubmitDailyScheduleCheckIn(false)}
                      className="px-4 py-2 rounded-xl bg-[#101B35] text-[#35D6E8] font-extrabold shadow-sm"
                    >
                      ✓ Confirm Schedule & Generate Today&apos;s Plan
                    </button>
                  </div>
                )}

                {(dailySchedule?.generated_daily_timeline &&
                  dailySchedule.generated_daily_timeline.length > 0
                  ? dailySchedule.generated_daily_timeline
                  : plan.today_combined_timeline &&
                    plan.today_combined_timeline.length > 0
                    ? plan.today_combined_timeline
                    : plan.daily_timetable
                ).map((task) => (
                  <div
                    key={task.task_id}
                    className={`p-4 rounded-2xl border flex flex-col gap-3 text-xs ${task.session_type === 'Unavailable'
                        ? 'bg-slate-900 text-white border-slate-700'
                        : task.session_type === 'Break'
                          ? 'bg-emerald-50/60 border-emerald-200'
                          : task.completed
                            ? 'bg-slate-50 border-slate-200 opacity-75'
                            : 'bg-white border-slate-200'
                      }`}
                  >
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div className="space-y-1">
                        <div
                          className={`flex flex-wrap items-center gap-2 font-extrabold ${task.session_type === 'Unavailable'
                              ? 'text-white'
                              : 'text-slate-900'
                            }`}
                        >
                          <span
                            className={
                              task.session_type === 'Unavailable'
                                ? 'text-[#35D6E8]'
                                : 'text-blue-700'
                            }
                          >
                            {formatTimeRange12Hour(task.time_slot)}
                          </span>
                          <span>•</span>
                          <span>{task.subject}</span>
                          <span
                            className={`px-2 py-0.5 rounded-md ${task.session_type === 'Unavailable'
                                ? 'bg-[#35D6E8]/20 text-[#35D6E8] border border-[#35D6E8]/40'
                                : task.session_type === 'Homework'
                                  ? 'bg-amber-100 text-amber-900'
                                  : 'bg-blue-100 text-blue-900'
                              }`}
                          >
                            {task.session_type} ({task.duration_minutes} mins)
                          </span>
                          {task.postponed && (
                            <span className="px-2 py-0.5 rounded-full bg-amber-100 text-amber-900 text-[10px] font-extrabold">
                              Postponed
                            </span>
                          )}
                        </div>
                        <div
                          className={
                            task.session_type === 'Unavailable'
                              ? 'text-slate-300 font-semibold'
                              : 'text-slate-700 font-semibold'
                          }
                        >
                          {task.session_type === 'Unavailable'
                            ? `Personal Activity: ${task.chapter}`
                            : `Chapter: ${task.chapter}`}
                        </div>
                        {task.priority_reason && (
                          <div
                            className={
                              task.session_type === 'Unavailable'
                                ? 'text-slate-400'
                                : 'text-slate-500'
                            }
                          >
                            {formatTime12Hour(task.priority_reason)}
                          </div>
                        )}
                      </div>
                      {task.session_type !== 'Unavailable' && (
                        <div className="flex flex-wrap items-center gap-2">
                          {task.session_type !== 'Break' && (
                            <button
                              type="button"
                              onClick={() => {
                                setEditingTaskId(task.task_id);
                                setEditTaskDate(task.date_iso);
                                setEditTaskTimeSlot(
                                  formatTimeRange12Hour(task.time_slot)
                                );
                                setEditTaskChapter(task.chapter);
                              }}
                              className="px-2.5 py-1.5 rounded-xl border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 font-bold"
                            >
                              ✏️ Edit
                            </button>
                          )}
                          <button
                            type="button"
                            onClick={() =>
                              toggleTask(
                                task.task_id,
                                !task.completed,
                                false,
                                false
                              )
                            }
                            className={`px-3 py-1.5 rounded-xl font-extrabold ${task.completed
                                ? 'bg-emerald-600 text-white'
                                : 'bg-slate-100 text-slate-800 hover:bg-emerald-50'
                              }`}
                          >
                            {task.completed ? '✓ Completed' : 'Mark Complete'}
                          </button>
                          {task.session_type !== 'Break' && !task.completed && (
                            <>
                              <button
                                type="button"
                                onClick={() =>
                                  toggleTask(task.task_id, false, false, true)
                                }
                                className="px-3 py-1.5 rounded-xl bg-indigo-50 text-indigo-900 font-bold hover:bg-indigo-100"
                              >
                                ⏳ Postpone
                              </button>
                              <button
                                type="button"
                                onClick={() =>
                                  toggleTask(task.task_id, false, true, false)
                                }
                                className="px-3 py-1.5 rounded-xl bg-amber-100 text-amber-900 font-bold"
                              >
                                Mark Missed
                              </button>
                            </>
                          )}
                        </div>
                      )}
                    </div>

                    {editingTaskId === task.task_id && (
                      <div className="p-3 rounded-xl bg-slate-50 border border-blue-200 grid sm:grid-cols-4 gap-2 items-end">
                        <div>
                          <label className="block text-[10px] font-bold text-slate-600">
                            Study Date
                          </label>
                          <input
                            type="date"
                            value={editTaskDate}
                            onChange={(e) => setEditTaskDate(e.target.value)}
                            className="w-full rounded-lg border border-slate-300 bg-white px-2.5 py-1 text-xs font-bold"
                          />
                        </div>
                        <div>
                          <label className="block text-[10px] font-bold text-slate-600">
                            Time Slot (12-Hr AM/PM)
                          </label>
                          <input
                            type="text"
                            value={editTaskTimeSlot}
                            onChange={(e) => setEditTaskTimeSlot(e.target.value)}
                            className="w-full rounded-lg border border-slate-300 bg-white px-2.5 py-1 text-xs font-bold"
                          />
                        </div>
                        <div>
                          <label className="block text-[10px] font-bold text-slate-600">
                            Chapter Target
                          </label>
                          <input
                            type="text"
                            value={editTaskChapter}
                            onChange={(e) => setEditTaskChapter(e.target.value)}
                            className="w-full rounded-lg border border-slate-300 bg-white px-2.5 py-1 text-xs font-bold"
                          />
                        </div>
                        <div className="flex gap-1.5">
                          <button
                            type="button"
                            onClick={() =>
                              toggleTask(
                                task.task_id,
                                task.completed,
                                task.missed,
                                Boolean(task.postponed),
                                editTaskDate,
                                editTaskTimeSlot,
                                editTaskChapter
                              )
                            }
                            className="px-3 py-1.5 rounded-lg bg-blue-600 text-white font-extrabold text-xs"
                          >
                            Save Task
                          </button>
                          <button
                            type="button"
                            onClick={() => setEditingTaskId(null)}
                            className="px-2.5 py-1.5 rounded-lg bg-slate-200 text-slate-700 font-bold text-xs"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'complete' && (
              <div className="space-y-2.5 text-xs">
                <div className="p-3 rounded-xl bg-blue-50 border border-blue-200 text-blue-950 font-semibold">
                  Unified Complete Exam Study Timetable combining all subjects, chapters, and individual exam dates. Completed tasks are preserved when regenerating!
                </div>
                <div className="max-h-96 overflow-y-auto space-y-2 pr-1">
                  {(plan.complete_exam_schedule || []).map((task) => (
                    <div
                      key={task.task_id}
                      className="p-3.5 rounded-2xl border border-slate-200 bg-white flex flex-wrap items-center justify-between gap-2"
                    >
                      <div>
                        <span className="font-extrabold text-slate-900">
                          {task.date_iso} ({task.day_label})
                        </span>{' '}
                        •{' '}
                        <span className="font-extrabold text-blue-700">
                          {formatTimeRange12Hour(task.time_slot)}
                        </span>{' '}
                        —{' '}
                        <span className="font-extrabold text-slate-900">
                          {task.subject}: {task.chapter}
                        </span>{' '}
                        <span className="text-slate-500">
                          ({task.session_type}, {task.duration_minutes}m)
                        </span>
                        {task.subject_exam_date && (
                          <span className="ml-2 px-2 py-0.5 rounded-full bg-amber-100 text-amber-900 text-[10px] font-extrabold">
                            Exam: {task.subject_exam_date}
                          </span>
                        )}
                      </div>
                      <button
                        type="button"
                        onClick={() =>
                          toggleTask(task.task_id, !task.completed, false, false)
                        }
                        className={`px-3 py-1 rounded-lg font-bold ${task.completed
                            ? 'bg-emerald-600 text-white'
                            : 'bg-slate-100 text-slate-700'
                          }`}
                      >
                        {task.completed ? '✓ Completed' : 'Mark Complete'}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'weekly' && (
              <div className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  {Object.keys(plan.weekly_timetable).map((day) => (
                    <button
                      key={day}
                      type="button"
                      onClick={() => setSelectedDay(day)}
                      className={`px-3.5 py-1.5 rounded-xl text-xs font-extrabold ${selectedDay === day
                          ? 'bg-violet-700 text-white'
                          : 'bg-slate-100 text-slate-700'
                        }`}
                    >
                      {day}
                    </button>
                  ))}
                </div>
                <div className="space-y-2">
                  {(plan.weekly_timetable[selectedDay] || []).map((task) => (
                    <div
                      key={task.task_id}
                      className="p-3.5 rounded-2xl border border-slate-200 flex items-center justify-between text-xs"
                    >
                      <div>
                        <span className="font-extrabold text-blue-700">
                          {formatTimeRange12Hour(task.time_slot)}
                        </span>{' '}
                        <span className="font-extrabold text-slate-900">
                          — {task.subject}: {task.chapter}
                        </span>{' '}
                        <span className="text-slate-500">
                          ({task.session_type}, {task.duration_minutes}m)
                        </span>
                      </div>
                      <button
                        type="button"
                        onClick={() =>
                          toggleTask(task.task_id, !task.completed, false)
                        }
                        className={`px-3 py-1 rounded-lg font-bold ${task.completed
                            ? 'bg-emerald-600 text-white'
                            : 'bg-slate-100 text-slate-700'
                          }`}
                      >
                        {task.completed ? '✓ Done' : 'Complete'}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'monthly' && (
              <div className="grid md:grid-cols-2 gap-4 text-xs">
                <div className="space-y-2.5">
                  <h4 className="font-extrabold text-slate-900 uppercase">
                    4-Week Preparation Roadmap
                  </h4>
                  {plan.monthly_preparation_milestones.map((m, i) => (
                    <div
                      key={i}
                      className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-1"
                    >
                      <div className="font-extrabold text-blue-800">
                        {m.week}
                      </div>
                      <div className="text-slate-700">{m.focus}</div>
                      <div className="font-bold text-emerald-800">
                        Target: {m.deliverable}
                      </div>
                    </div>
                  ))}
                </div>
                <div className="space-y-2.5">
                  <h4 className="font-extrabold text-slate-900 uppercase">
                    Curriculum Chapter Completion Targets
                  </h4>
                  {plan.chapter_completion_targets.map((ct, i) => (
                    <div
                      key={i}
                      className="p-3 rounded-2xl border border-slate-200 flex items-center justify-between"
                    >
                      <div>
                        <div className="font-extrabold text-slate-900">
                          {ct.subject}: {ct.chapter}
                        </div>
                        <div className="text-amber-800 font-semibold">
                          {ct.priority}
                        </div>
                      </div>
                      <span className="px-2.5 py-1 rounded-lg bg-blue-50 text-blue-900 font-extrabold">
                        By {ct.target_completion_date},{' '}
                        {formatTime12Hour('20:00')}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'catchup' && (
              <div className="space-y-3 text-xs">
                {plan.catch_up_schedule.length === 0 ? (
                  <div className="p-4 rounded-2xl bg-slate-50 text-slate-600 font-semibold">
                    No catch-up sessions generated yet. Click &quot;Generate Catch-Up Schedule for Missed Sessions&quot; above to build recovery blocks.
                  </div>
                ) : (
                  plan.catch_up_schedule.map((c) => (
                    <div
                      key={c.task_id}
                      className="p-4 rounded-2xl bg-amber-50 border border-amber-300 flex items-center justify-between"
                    >
                      <div>
                        <div className="font-extrabold text-amber-950">
                          {c.day_label} ({c.date_iso} •{' '}
                          {formatTimeRange12Hour(c.time_slot)}) — {c.subject}:{' '}
                          {c.chapter}
                        </div>
                        <div className="text-amber-800">
                          {formatTime12Hour(c.priority_reason)}
                        </div>
                      </div>
                      <span className="px-3 py-1 rounded-full bg-amber-200 text-amber-950 font-extrabold">
                        {c.duration_minutes} mins Recovery
                      </span>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

// ============================================================================
// D. HOMEWORK MANAGER VIEW (CONNECTED TO /api/students/{id}/homework)
// ============================================================================

interface HomeworkRecord {
  homework_id: string;
  student_id: string;
  subject: string;
  chapter: string;
  title: string;
  description: string;
  due_date: string;
  priority: 'High' | 'Medium' | 'Low';
  estimated_minutes: number;
  status: 'pending' | 'in_progress' | 'completed';
  extracted_question_from_image?: string | null;
}

export const HomeworkManagerView: React.FC<{
  onboarding: OnboardingState;
  onOpenInBuddy: (question: string, subject: string) => void;
}> = ({ onboarding, onOpenInBuddy }) => {
  const curriculumSubjects = React.useMemo(
    () =>
      getCurriculumSubjects(
        onboarding.grade,
        onboarding.board,
        onboarding.stateName
      ),
    [onboarding.grade, onboarding.board, onboarding.stateName]
  );

  const [items, setItems] = React.useState<HomeworkRecord[]>([]);
  const [subject, setSubject] = React.useState<string>(
    curriculumSubjects[0]?.name || 'Mathematics'
  );
  const [chapter, setChapter] = React.useState<string>(
    curriculumSubjects[0]?.topics[0] || 'Fractions & Decimals'
  );
  const [title, setTitle] = React.useState<string>('');
  const [description, setDescription] = React.useState<string>('');
  const [dueDate, setDueDate] = React.useState<string>('2026-11-15');
  const [priority, setPriority] = React.useState<'High' | 'Medium' | 'Low'>(
    'High'
  );
  const [estimatedMinutes, setEstimatedMinutes] = React.useState<number>(30);
  const [imageBase64, setImageBase64] = React.useState<string>('');
  const [filterStatus, setFilterStatus] = React.useState<string>('ALL');

  const fetchHomework = React.useCallback(async () => {
    const res = await fetch(`/api/students/${onboarding.studentId}/homework`);
    if (res.ok) {
      const data = await res.json();
      setItems(data.items || []);
    }
  }, [onboarding.studentId]);

  React.useEffect(() => {
    fetchHomework();
  }, [fetchHomework]);

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === 'string') setImageBase64(reader.result);
    };
    reader.readAsDataURL(file);
  };

  const handleAddHomework = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    const res = await fetch(`/api/students/${onboarding.studentId}/homework`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: onboarding.studentId,
        subject,
        chapter,
        title,
        description: description || title,
        due_date: dueDate,
        priority,
        estimated_minutes: estimatedMinutes,
        image_base64: imageBase64 || null,
      }),
    });
    if (res.ok) {
      setTitle('');
      setDescription('');
      setImageBase64('');
      fetchHomework();
    }
  };

  const updateStatus = async (
    hwId: string,
    status: 'pending' | 'in_progress' | 'completed'
  ) => {
    await fetch(`/api/students/${onboarding.studentId}/homework/${hwId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });
    fetchHomework();
  };

  const filtered = items.filter((i) =>
    filterStatus === 'ALL' ? true : i.status === filterStatus
  );

  return (
    <div className="space-y-6 animate-fade-in">
      <RobotGuideTip
        tipId="homework_manager"
        studentId={onboarding.studentId}
        title="Sparky's Homework Tip"
        message="Add school assignments with due dates or worksheet photos, then tap any task to get step-by-step hints from Sparky."
        mood="happy"
      />
      {/* Midnight-Indigo Homework Header */}
      <div
        className="rounded-3xl text-white p-6 border border-[#5146E5]/30 shadow-lg flex flex-wrap items-center justify-between gap-4"
        style={{ background: 'linear-gradient(135deg, #101B35 0%, #232A6B 60%, #5146E5 100%)' }}
      >
        <div className="space-y-1">
          <span className="text-[11px] font-extrabold uppercase tracking-wider text-[#35D6E8]">
            Homework Manager
          </span>
          <h2 className="text-xl md:text-2xl font-extrabold text-white">
            Keep assignments organized and stress-free.
          </h2>
        </div>
        <div className="flex flex-wrap gap-2 text-xs font-extrabold">
          <span className="px-3 py-1.5 rounded-xl bg-white/10 border border-white/15 text-amber-300">
            Pending: {items.filter((i) => i.status === 'pending').length}
          </span>
          <span className="px-3 py-1.5 rounded-xl bg-white/10 border border-white/15 text-[#35D6E8]">
            In Progress: {items.filter((i) => i.status === 'in_progress').length}
          </span>
          <span className="px-3 py-1.5 rounded-xl bg-white/10 border border-white/15 text-emerald-300">
            Done: {items.filter((i) => i.status === 'completed').length}
          </span>
        </div>
      </div>

      {/* Add Homework Card */}
      <form
        onSubmit={handleAddHomework}
        className="eduspark-card rounded-3xl p-6 space-y-4"
      >
        <div className="flex items-center justify-between gap-2 border-b border-slate-100 pb-3">
          <h3 className="text-sm font-extrabold text-[#101B35]">Add a New Assignment</h3>
          <HelpTip
            title="Homework & AI Buddy"
            text="Add a task manually or attach a worksheet photo. Tap 'Get Hint' on any assignment to solve it step by step with your AI Learning Buddy."
          />
        </div>

        <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          <div>
            <label className="block font-bold text-slate-700 mb-1">
              Subject
            </label>
            <select
              value={subject}
              onChange={(e) => {
                setSubject(e.target.value);
                const found = curriculumSubjects.find(
                  (s) => s.name === e.target.value
                );
                if (found && found.topics[0]) setChapter(found.topics[0]);
              }}
              className="w-full rounded-xl border border-slate-300 px-3 py-2 font-semibold"
            >
              {curriculumSubjects.map((s) => (
                <option key={s.code} value={s.name}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block font-bold text-slate-700 mb-1">
              Chapter
            </label>
            <input
              type="text"
              value={chapter}
              onChange={(e) => setChapter(e.target.value)}
              className="w-full rounded-xl border border-slate-300 px-3 py-2 font-semibold"
            />
          </div>

          <div>
            <label className="block font-bold text-slate-700 mb-1">
              Due Date
            </label>
            <input
              type="date"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              className="w-full rounded-xl border border-slate-300 px-3 py-2 font-semibold"
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block font-bold text-slate-700 mb-1">
                Priority
              </label>
              <select
                value={priority}
                onChange={(e) =>
                  setPriority(e.target.value as 'High' | 'Medium' | 'Low')
                }
                className="w-full rounded-xl border border-slate-300 px-2 py-2 font-semibold"
              >
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
            <div>
              <label className="block font-bold text-slate-700 mb-1">
                Est. Mins
              </label>
              <input
                type="number"
                value={estimatedMinutes}
                onChange={(e) =>
                  setEstimatedMinutes(Number(e.target.value) || 30)
                }
                className="w-full rounded-xl border border-slate-300 px-2 py-2 font-semibold"
              />
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-3 text-xs">
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Homework Title (e.g., Ex 2.2 Fraction Word Problems Q1-Q5)"
            className="rounded-xl border border-slate-300 px-3 py-2.5 font-semibold"
            required
          />
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Specific question or instructions (e.g., Solve 1/4 + 1/6 using LCM)..."
            className="rounded-xl border border-slate-300 px-3 py-2.5 font-semibold"
          />
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3">
          <label className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 text-xs font-bold text-slate-700 cursor-pointer">
            <Upload className="w-4 h-4 text-blue-600" />
            <span>
              {imageBase64
                ? '✓ Homework Photo Attached'
                : 'Attach Homework Worksheet Image (Optional)'}
            </span>
            <input
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleImageSelect}
            />
          </label>

          <button
            type="submit"
            className="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-extrabold shadow-sm"
          >
            <Plus className="w-4 h-4" />
            <span>Add Homework Task</span>
          </button>
        </div>
      </form>

      {/* Filter & Task List */}
      <div className="eduspark-card rounded-3xl p-6 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex gap-2">
            {['ALL', 'pending', 'in_progress', 'completed'].map((st) => (
              <button
                key={st}
                type="button"
                onClick={() => setFilterStatus(st)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-extrabold uppercase ${filterStatus === st
                    ? 'bg-[#2563EB] text-white'
                    : 'bg-slate-100 text-slate-700'
                  }`}
              >
                {st.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-3">
          {filtered.map((hw) => {
            const hwTiming = formatHomeworkDeadline12Hour(
              hw.due_date,
              hw.priority
            );
            return (
              <div
                key={hw.homework_id}
                className="p-4 rounded-2xl border border-slate-200 flex flex-wrap items-center justify-between gap-4 text-xs"
              >
                <div className="space-y-1 max-w-2xl">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-extrabold text-sm text-slate-900">
                      {hw.title}
                    </span>
                    <span className="px-2 py-0.5 rounded-md bg-blue-50 text-blue-800 font-bold">
                      {hw.subject} • {hw.chapter}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded-full font-bold ${hw.priority === 'High'
                          ? 'bg-red-100 text-red-800'
                          : hw.priority === 'Medium'
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-slate-100 text-slate-700'
                        }`}
                    >
                      {hw.priority} Priority
                    </span>
                    <span className="text-slate-600 font-bold">
                      Due: {hwTiming.dueDisplay} • 🔔 Reminder:{' '}
                      {hwTiming.reminderDisplay} • ~{hw.estimated_minutes} mins
                    </span>
                  </div>
                  <p className="text-slate-600">{hw.description}</p>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  <select
                    value={hw.status}
                    onChange={(e) =>
                      updateStatus(
                        hw.homework_id,
                        e.target.value as 'pending' | 'in_progress' | 'completed'
                      )
                    }
                    className="rounded-xl border border-slate-300 px-3 py-1.5 font-extrabold text-slate-800"
                  >
                    <option value="pending">Pending</option>
                    <option value="in_progress">In Progress</option>
                    <option value="completed">Completed ✓</option>
                  </select>

                  <button
                    type="button"
                    onClick={() => onOpenInBuddy(hw.description, hw.subject)}
                    className="px-3.5 py-2 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-extrabold"
                  >
                    Solve with AI Learning Buddy →
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// E. EXAM PREPARATION CENTRE VIEW (CONNECTED TO /api/students/{id}/exams)
// ============================================================================

interface ExamQuestion {
  question_id: string;
  question_number: number;
  question_type: 'MCQ' | 'SHORT_ANSWER' | 'LONG_ANSWER';
  subject: string;
  chapter: string;
  question_text: string;
  options: string[];
  correct_answer: string;
  marks: number;
  detailed_explanation: string;
}

interface ExamRecord {
  exam_id: string;
  exam_mode: string;
  title: string;
  subject: string;
  chapters: string[];
  duration_minutes: number;
  total_marks: number;
  questions: ExamQuestion[];
  status: 'GENERATED' | 'COMPLETED';
  score_awarded?: number | null;
  score_percentage?: number | null;
  question_evaluations: {
    question_id: string;
    question_number: number;
    chapter: string;
    student_answer: string;
    correct_answer: string;
    is_correct: boolean;
    marks_awarded: number;
    max_marks: number;
    feedback_and_explanation: string;
  }[];
  weak_topics_detected: string[];
  improvement_recommendations: string[];
}

interface ExamMarkRecordUI {
  mark_id: string;
  student_id: string;
  subject: string;
  exam_name: string;
  exam_type: string;
  exam_date: string;
  marks_obtained: number;
  maximum_marks: number;
  percentage: number;
  remarks?: string | null;
  chapters_tested: string[];
  verification_status: 'STUDENT_REPORTED' | 'OFFICIALLY_VERIFIED';
  trend: 'Improvement' | 'Decline' | 'Consistent performance' | 'Needs attention';
  recorded_at: string;
}

export const ExamPreparationCentreView: React.FC<{
  onboarding: OnboardingState;
  onSelectScreen: (s: ScreenId) => void;
}> = ({ onboarding, onSelectScreen }) => {
  const curriculumSubjects = React.useMemo(
    () =>
      getCurriculumSubjects(
        onboarding.grade,
        onboarding.board,
        onboarding.stateName
      ),
    [onboarding.grade, onboarding.board, onboarding.stateName]
  );

  const [exams, setExams] = React.useState<ExamRecord[]>([]);
  const [activeExam, setActiveExam] = React.useState<ExamRecord | null>(null);
  const [answers, setAnswers] = React.useState<Record<string, string>>({});
  const [examMode, setExamMode] = React.useState<string>('Chapter Test');
  const [selectedSubject, setSelectedSubject] = React.useState<string>(
    curriculumSubjects[0]?.name || 'Mathematics'
  );
  const [remainingSeconds, setRemainingSeconds] = React.useState<number>(1200);
  const [submitting, setSubmitting] = React.useState<boolean>(false);

  // Post-Exam Marks Entry & History States (Requirement 6 & 7)
  const [examMarksList, setExamMarksList] = React.useState<ExamMarkRecordUI[]>([]);
  const [editingMarkId, setEditingMarkId] = React.useState<string | null>(null);
  const [markSubject, setMarkSubject] = React.useState<string>(
    curriculumSubjects[0]?.name || 'Mathematics'
  );
  const [markExamName, setMarkExamName] = React.useState<string>('Term-1 Final Exam');
  const [markExamType, setMarkExamType] = React.useState<string>('Term Exam');
  const [markExamDate, setMarkExamDate] = React.useState<string>('2026-12-01');
  const [marksObtained, setMarksObtained] = React.useState<number>(78);
  const [maximumMarks, setMaximumMarks] = React.useState<number>(100);
  const [markRemarks, setMarkRemarks] = React.useState<string>('');
  const [markChaptersInput, setMarkChaptersInput] = React.useState<string>('');
  const [markError, setMarkError] = React.useState<string>('');
  const [markSuccess, setMarkSuccess] = React.useState<string>('');

  const fetchExamMarks = React.useCallback(async () => {
    try {
      const res = await fetch(`/api/students/${onboarding.studentId}/exam-marks`);
      if (res.ok) {
        const data = await res.json();
        setExamMarksList(data.exam_marks || []);
      }
    } catch {
      // ignore offline
    }
  }, [onboarding.studentId]);

  const fetchExams = React.useCallback(async () => {
    const res = await fetch(`/api/students/${onboarding.studentId}/exams`);
    if (res.ok) {
      const data = await res.json();
      const list: ExamRecord[] = data.exams || [];
      setExams(list);
      if (list.length > 0 && !activeExam) {
        setActiveExam(list[0]);
        setRemainingSeconds(list[0].duration_minutes * 60);
      }
    }
  }, [onboarding.studentId, activeExam]);

  React.useEffect(() => {
    fetchExams();
    fetchExamMarks();
  }, [fetchExams, fetchExamMarks]);

  const handleSaveExamMark = async (e: React.FormEvent) => {
    e.preventDefault();
    setMarkError('');
    setMarkSuccess('');

    if (!markSubject.trim() || !markExamName.trim() || !markExamDate.trim()) {
      setMarkError('Subject, Exam name, and Exam date are required.');
      return;
    }
    if (marksObtained < 0) {
      setMarkError('Marks obtained cannot be negative.');
      return;
    }
    if (maximumMarks <= 0) {
      setMarkError('Maximum marks must be greater than zero.');
      return;
    }
    if (marksObtained > maximumMarks) {
      setMarkError(
        `Marks obtained (${marksObtained}) cannot exceed maximum marks (${maximumMarks}).`
      );
      return;
    }

    const chaptersTested = markChaptersInput
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);

    const url = editingMarkId
      ? `/api/students/${onboarding.studentId}/exam-marks/${editingMarkId}`
      : `/api/students/${onboarding.studentId}/exam-marks`;
    const method = editingMarkId ? 'PUT' : 'POST';

    try {
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mark_id: editingMarkId || null,
          student_id: onboarding.studentId,
          subject: markSubject.trim(),
          exam_name: markExamName.trim(),
          exam_type: markExamType,
          exam_date: markExamDate,
          marks_obtained: marksObtained,
          maximum_marks: maximumMarks,
          remarks: markRemarks.trim() || null,
          chapters_tested: chaptersTested,
          verification_status: 'STUDENT_REPORTED',
        }),
      });
      if (!res.ok) {
        const err = await res.json();
        setMarkError(err.detail || 'Validation error while saving exam marks.');
        return;
      }
      const saved: ExamMarkRecordUI = await res.json();
      setMarkSuccess(
        `✓ Saved ${saved.subject} (${saved.exam_name}): ${saved.marks_obtained}/${saved.maximum_marks} (${saved.percentage}%) — Trend: ${saved.trend}`
      );
      setEditingMarkId(null);
      setMarkRemarks('');
      fetchExamMarks();
    } catch {
      setMarkError('Could not connect to server to save exam marks.');
    }
  };

  // Live countdown timer when an exam is GENERATED
  React.useEffect(() => {
    if (!activeExam || activeExam.status !== 'GENERATED') return;
    const timer = window.setInterval(() => {
      setRemainingSeconds((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => window.clearInterval(timer);
  }, [activeExam]);

  const generateNewExam = async () => {
    const subObj =
      curriculumSubjects.find((s) => s.name === selectedSubject) ||
      curriculumSubjects[0];
    const res = await fetch(
      `/api/students/${onboarding.studentId}/exams/generate`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: onboarding.studentId,
          exam_mode: examMode,
          subject: selectedSubject,
          chapters: subObj ? subObj.topics.slice(0, 2) : ['Fractions & Decimals'],
          duration_minutes: 20,
          question_count: 4,
        }),
      }
    );
    if (res.ok) {
      const created: ExamRecord = await res.json();
      setActiveExam(created);
      setAnswers({});
      setRemainingSeconds(created.duration_minutes * 60);
      fetchExams();
    }
  };

  const submitExam = async () => {
    if (!activeExam) return;
    setSubmitting(true);
    try {
      const res = await fetch(
        `/api/students/${onboarding.studentId}/exams/${activeExam.exam_id}/submit`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            student_id: onboarding.studentId,
            answers,
            time_taken_seconds:
              activeExam.duration_minutes * 60 - remainingSeconds,
          }),
        }
      );
      if (res.ok) {
        const evaluated: ExamRecord = await res.json();
        setActiveExam(evaluated);
        fetchExams();
      }
    } finally {
      setSubmitting(false);
    }
  };

  const formatTimer = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <RobotGuideTip
        tipId="exam_prep"
        studentId={onboarding.studentId}
        title="Sparky's Exam Prep Coach"
        message="Practice timed mock papers with instant mistake reviews, and record real school exam marks to track genuine improvement."
        mood="encouraging"
      />
      {/* Midnight-Indigo Exam Prep Header */}
      <div
        className="rounded-3xl text-white p-6 border border-[#5146E5]/30 shadow-lg flex flex-wrap items-center justify-between gap-4"
        style={{ background: 'linear-gradient(135deg, #101B35 0%, #232A6B 60%, #5146E5 100%)' }}
      >
        <div className="space-y-1">
          <span className="text-[11px] font-extrabold uppercase tracking-wider text-[#35D6E8]">
            Exam Preparation & Practice
          </span>
          <h2 className="text-xl md:text-2xl font-extrabold text-white">
            Practice smarter, spot weak topics, and log school exam marks.
          </h2>
        </div>
        {maximumMarks > 0 && marksObtained >= 0 && marksObtained <= maximumMarks && (
          <div className="px-4 py-2 rounded-xl bg-[#35D6E8] text-[#101B35] text-xs font-extrabold">
            Preview Score: {Math.round((marksObtained / maximumMarks) * 1000) / 10}%
          </div>
        )}
      </div>

      {/* Post-Exam Marks Entry Card (Clean Unified Surface) */}
      <form
        onSubmit={handleSaveExamMark}
        className="eduspark-card rounded-3xl p-6 space-y-4"
      >
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-3">
          <div>
            <h3 className="text-base font-extrabold text-[#101B35]">
              Log School Exam Marks
            </h3>
            <p className="text-xs text-slate-500">
              Percentages calculate automatically and sync with your study plan.
            </p>
          </div>
          <HelpTip
            title="Marks Verification Policy"
            text="Manually entered marks are labeled STUDENT_REPORTED until verified, and all previous exam records are preserved permanently."
          />
        </div>

        <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          <div>
            <label className="block font-extrabold text-slate-800 mb-1">
              Subject *
            </label>
            <input
              type="text"
              required
              value={markSubject}
              onChange={(e) => setMarkSubject(e.target.value)}
              placeholder="e.g., Mathematics"
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-bold"
            />
          </div>
          <div>
            <label className="block font-extrabold text-slate-800 mb-1">
              Exam Name *
            </label>
            <input
              type="text"
              required
              value={markExamName}
              onChange={(e) => setMarkExamName(e.target.value)}
              placeholder="e.g., Term-1 Final Exam"
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-bold"
            />
          </div>
          <div>
            <label className="block font-extrabold text-slate-800 mb-1">
              Exam Type *
            </label>
            <select
              value={markExamType}
              onChange={(e) => setMarkExamType(e.target.value)}
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-bold"
            >
              <option value="Unit Test">Unit Test</option>
              <option value="Chapter Test">Chapter Test</option>
              <option value="Mid-Term / Half-Yearly">Mid-Term / Half-Yearly</option>
              <option value="Term Exam">Term Exam</option>
              <option value="Annual / Final Exam">Annual / Final Exam</option>
            </select>
          </div>
          <div>
            <label className="block font-extrabold text-slate-800 mb-1">
              Exam Date *
            </label>
            <input
              type="date"
              required
              value={markExamDate}
              onChange={(e) => setMarkExamDate(e.target.value)}
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-bold"
            />
          </div>
          <div>
            <label className="block font-extrabold text-slate-800 mb-1">
              Marks Obtained *
            </label>
            <input
              type="number"
              step="0.5"
              required
              value={marksObtained}
              onChange={(e) => setMarksObtained(Number(e.target.value))}
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-bold"
            />
          </div>
          <div>
            <label className="block font-extrabold text-slate-800 mb-1">
              Maximum Marks *
            </label>
            <input
              type="number"
              step="0.5"
              required
              value={maximumMarks}
              onChange={(e) => setMaximumMarks(Number(e.target.value))}
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-bold"
            />
          </div>
          <div>
            <label className="block font-extrabold text-slate-800 mb-1">
              Chapters Tested (Optional, comma-separated)
            </label>
            <input
              type="text"
              value={markChaptersInput}
              onChange={(e) => setMarkChaptersInput(e.target.value)}
              placeholder="Leave blank if subject-level only"
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-semibold"
            />
          </div>
          <div>
            <label className="block font-extrabold text-slate-800 mb-1">
              Optional Remarks
            </label>
            <input
              type="text"
              value={markRemarks}
              onChange={(e) => setMarkRemarks(e.target.value)}
              placeholder="e.g., Need more time on word problems"
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-semibold"
            />
          </div>
        </div>

        {markError && (
          <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-extrabold">
            ⚠️ {markError}
          </div>
        )}
        {markSuccess && (
          <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs font-extrabold">
            {markSuccess}
          </div>
        )}

        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="text-[11px] font-bold text-slate-600">
            {editingMarkId
              ? 'Editing existing exam mark entry (history is preserved).'
              : 'Low scores (< 65%) automatically allocate extra study & revision sessions and alert AI Learning Buddy.'}
          </div>
          <div className="flex gap-2">
            {editingMarkId && (
              <button
                type="button"
                onClick={() => setEditingMarkId(null)}
                className="px-4 py-2 rounded-xl border border-slate-300 bg-white text-slate-700 text-xs font-bold"
              >
                Cancel Edit
              </button>
            )}
            <button
              type="submit"
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#2563EB] to-[#7C3AED] text-white text-xs font-extrabold shadow-sm"
            >
              {editingMarkId
                ? 'Update Exam Marks →'
                : '+ Save Exam Marks & Update Academic Progress →'}
            </button>
          </div>
        </div>

        {/* Complete Examination History Table */}
        {examMarksList.length > 0 && (
          <div className="pt-3 border-t border-indigo-100 space-y-2 text-xs">
            <div className="font-extrabold text-slate-900">
              📜 Complete Examination Marks History ({examMarksList.length} Record
              {examMarksList.length === 1 ? '' : 's'} — Never Deleted)
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 text-[10px] uppercase text-slate-500 font-extrabold">
                    <th className="py-2 px-2.5">Subject</th>
                    <th className="py-2 px-2.5">Exam Name & Type</th>
                    <th className="py-2 px-2.5">Date</th>
                    <th className="py-2 px-2.5">Marks</th>
                    <th className="py-2 px-2.5">Percentage</th>
                    <th className="py-2 px-2.5">Trend</th>
                    <th className="py-2 px-2.5">Verification</th>
                    <th className="py-2 px-2.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200/70">
                  {examMarksList.map((mk) => (
                    <tr key={mk.mark_id} className="bg-white/80">
                      <td className="py-2 px-2.5 font-extrabold text-slate-900">
                        {mk.subject}
                      </td>
                      <td className="py-2 px-2.5 font-semibold text-slate-700">
                        {mk.exam_name} ({mk.exam_type})
                      </td>
                      <td className="py-2 px-2.5 text-slate-600">{mk.exam_date}</td>
                      <td className="py-2 px-2.5 font-bold text-slate-900">
                        {mk.marks_obtained} / {mk.maximum_marks}
                      </td>
                      <td className="py-2 px-2.5">
                        <span
                          className={`px-2 py-0.5 rounded-full font-extrabold ${mk.percentage < 65
                              ? 'bg-rose-100 text-rose-800'
                              : mk.percentage >= 80
                                ? 'bg-emerald-100 text-emerald-800'
                                : 'bg-blue-100 text-blue-800'
                            }`}
                        >
                          {mk.percentage}%
                        </span>
                      </td>
                      <td className="py-2 px-2.5 font-bold text-slate-700">
                        {mk.trend}
                      </td>
                      <td className="py-2 px-2.5">
                        <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-900 text-[10px] font-extrabold">
                          {mk.verification_status}
                        </span>
                      </td>
                      <td className="py-2 px-2.5 text-right space-x-1.5">
                        <button
                          type="button"
                          onClick={() => {
                            setEditingMarkId(mk.mark_id);
                            setMarkSubject(mk.subject);
                            setMarkExamName(mk.exam_name);
                            setMarkExamType(mk.exam_type);
                            setMarkExamDate(mk.exam_date);
                            setMarksObtained(mk.marks_obtained);
                            setMaximumMarks(mk.maximum_marks);
                            setMarkRemarks(mk.remarks || '');
                            setMarkChaptersInput((mk.chapters_tested || []).join(', '));
                          }}
                          className="px-2 py-1 rounded bg-blue-50 text-blue-700 font-extrabold text-[10px]"
                        >
                          Edit
                        </button>
                        {mk.percentage < 70 && (
                          <button
                            type="button"
                            onClick={() => onSelectScreen('buddy')}
                            className="px-2 py-1 rounded bg-violet-600 text-white font-extrabold text-[10px]"
                          >
                            AI Buddy Help →
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </form>

      {/* Paper Generator Controls */}
      <div className="eduspark-card rounded-3xl p-6 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <span className="text-xs font-extrabold uppercase text-blue-600">
              Timed Examinations • Auto-Evaluation • Weak-Topic Revision Sync
            </span>
            <h2 className="text-xl font-extrabold text-slate-900">
              Exam Preparation Centre (MCQs + Short & Long Answer Papers)
            </h2>
          </div>

          <div className="flex flex-wrap items-center gap-2 text-xs">
            <select
              value={examMode}
              onChange={(e) => setExamMode(e.target.value)}
              className="rounded-xl border border-slate-300 px-3 py-2 font-bold"
            >
              <option value="Chapter Test">Chapter Test</option>
              <option value="Subject Mock Test">Subject Mock Test</option>
              <option value="Custom Paper">Custom Question Paper</option>
            </select>

            <select
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              className="rounded-xl border border-slate-300 px-3 py-2 font-bold"
            >
              {curriculumSubjects.map((s) => (
                <option key={s.code} value={s.name}>
                  {s.name}
                </option>
              ))}
            </select>

            <button
              type="button"
              onClick={generateNewExam}
              className="px-4 py-2 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-extrabold shadow-sm"
            >
              + Generate New Mock Paper
            </button>
          </div>
        </div>
      </div>

      {/* Active Exam Paper & Evaluation Results */}
      {activeExam && (
        <div className="eduspark-card rounded-3xl p-6 space-y-5">
          <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100">
            <div>
              <h3 className="text-lg font-extrabold text-slate-900">
                {activeExam.title}
              </h3>
              <p className="text-xs text-slate-600">
                Scheduled Slot:{' '}
                <strong>{formatTimeRange12Hour('09:30 - 11:00')}</strong> •
                Total Marks: <strong>{activeExam.total_marks}</strong> •
                Chapters: {activeExam.chapters.join(', ')}
              </p>
            </div>

            {activeExam.status === 'GENERATED' ? (
              <div className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-amber-100 text-amber-950 text-xs font-extrabold">
                <Clock className="w-4 h-4" />
                <span>Timer: {formatTimer(remainingSeconds)}</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-emerald-100 text-emerald-950 text-xs font-extrabold">
                <Trophy className="w-4 h-4" />
                <span>
                  Evaluated Score: {activeExam.score_awarded}/
                  {activeExam.total_marks} ({activeExam.score_percentage}%)
                </span>
              </div>
            )}
          </div>

          <div className="space-y-4">
            {activeExam.questions.map((q) => {
              const evalItem = activeExam.question_evaluations.find(
                (ev) => ev.question_id === q.question_id
              );
              return (
                <div
                  key={q.question_id}
                  className="p-4 rounded-2xl border border-slate-200 space-y-3 text-xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-extrabold text-sm text-slate-900">
                      Q{q.question_number}. {q.question_text}
                    </span>
                    <span className="px-2.5 py-1 rounded-lg bg-slate-100 text-slate-800 font-bold shrink-0">
                      {q.question_type.replace('_', ' ')} • {q.marks} Marks
                    </span>
                  </div>

                  {q.question_type === 'MCQ' ? (
                    <div className="grid sm:grid-cols-2 gap-2">
                      {q.options.map((opt) => (
                        <button
                          key={opt}
                          type="button"
                          disabled={activeExam.status === 'COMPLETED'}
                          onClick={() =>
                            setAnswers((prev) => ({
                              ...prev,
                              [q.question_id]: opt,
                            }))
                          }
                          className={`p-3 rounded-xl border text-left font-bold ${answers[q.question_id] === opt
                              ? 'border-2 border-[#2563EB] bg-blue-50 text-[#2563EB]'
                              : 'border-slate-200 hover:bg-slate-50'
                            }`}
                        >
                          {opt}
                        </button>
                      ))}
                    </div>
                  ) : (
                    <textarea
                      rows={2}
                      disabled={activeExam.status === 'COMPLETED'}
                      value={answers[q.question_id] || ''}
                      onChange={(e) =>
                        setAnswers((prev) => ({
                          ...prev,
                          [q.question_id]: e.target.value,
                        }))
                      }
                      placeholder="Write your step-by-step answer or formula..."
                      className="w-full rounded-xl border border-slate-300 p-3 font-medium"
                    />
                  )}

                  {evalItem && (
                    <div
                      className={`p-3.5 rounded-xl border font-semibold ${evalItem.is_correct
                          ? 'bg-emerald-50 border-emerald-200 text-emerald-950'
                          : 'bg-amber-50 border-amber-300 text-amber-950'
                        }`}
                    >
                      <div className="font-extrabold mb-1">
                        Marks Awarded: {evalItem.marks_awarded}/
                        {evalItem.max_marks}
                      </div>
                      <div>{evalItem.feedback_and_explanation}</div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {activeExam.status === 'GENERATED' ? (
            <button
              type="button"
              disabled={submitting}
              onClick={submitExam}
              className="px-6 py-3 rounded-2xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-extrabold shadow-sm"
            >
              {submitting
                ? 'Evaluating Paper...'
                : 'Submit Examination for Automatic Evaluation →'}
            </button>
          ) : (
            <div className="p-4 rounded-2xl bg-violet-50 border border-violet-200 space-y-2 text-xs">
              <div className="font-extrabold text-violet-950 text-sm">
                📈 Post-Exam Performance Report & Cross-Module Actions
              </div>
              <ul className="list-disc list-inside text-violet-900 space-y-1 font-medium">
                {activeExam.improvement_recommendations.map((rec, i) => (
                  <li key={i}>{rec}</li>
                ))}
              </ul>
              <div className="pt-2 flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => onSelectScreen('practice')}
                  className="px-4 py-2 rounded-xl bg-violet-700 text-white font-extrabold"
                >
                  Open Smart Revision Centre (Review Weak Topics) →
                </button>
                <button
                  type="button"
                  onClick={() => onSelectScreen('progress')}
                  className="px-4 py-2 rounded-xl bg-white border border-violet-300 text-violet-900 font-extrabold"
                >
                  View Updated Verified Score in Progress Dashboard →
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Agentic AI Diagnostic & Multi-Format Intelligent Assessment Lab */}
      <IntelligentAssessmentLabPanel
        studentId={onboarding.studentId}
        defaultSubject={selectedSubject}
        onSelectScreen={onSelectScreen}
      />
    </div>
  );
};

// ============================================================================
// F. SMART REVISION CENTRE VIEW (CONNECTED TO /api/students/{id}/revision)
// ============================================================================

interface RevisionCard {
  revision_id: string;
  subject: string;
  topic: string;
  front_prompt: string;
  back_explanation: string;
  active_recall_question: string;
  active_recall_options: string[];
  active_recall_answer: string;
  source_tag: string;
  interval_days: number;
  repetition_count: number;
  next_review_date: string;
  completed_today: boolean;
  mastery_level: string;
}

export const SmartRevisionCentreView: React.FC<{
  onboarding: OnboardingState;
}> = ({ onboarding }) => {
  const [cards, setCards] = React.useState<RevisionCard[]>([]);
  const [flippedIds, setFlippedIds] = React.useState<Record<string, boolean>>(
    {}
  );
  const [selectedQuizAnswers, setSelectedQuizAnswers] = React.useState<
    Record<string, string>
  >({});
  const [newTopic, setNewTopic] = React.useState<string>('');
  const [newSubject, setNewSubject] = React.useState<string>('Mathematics');

  const fetchCards = React.useCallback(async () => {
    const res = await fetch(`/api/students/${onboarding.studentId}/revision`);
    if (res.ok) {
      const data = await res.json();
      setCards(data.cards || []);
    }
  }, [onboarding.studentId]);

  React.useEffect(() => {
    fetchCards();
  }, [fetchCards]);

  const handleGenerateCard = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTopic.trim()) return;
    await fetch(`/api/students/${onboarding.studentId}/revision/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: onboarding.studentId,
        subject: newSubject,
        topic: newTopic.trim(),
      }),
    });
    setNewTopic('');
    fetchCards();
  };

  const submitSpacedReview = async (
    revisionId: string,
    quality: 'Easy' | 'Good' | 'Hard' | 'Forgot'
  ) => {
    await fetch(
      `/api/students/${onboarding.studentId}/revision/${revisionId}/review`,
      {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: onboarding.studentId,
          recall_quality: quality,
        }),
      }
    );
    fetchCards();
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Clean Smart Revision Header */}
      <RobotGuideTip
        tipId="smart_revision"
        studentId={onboarding.studentId}
        title="Sparky's Memory Boost"
        message="Flip each card to test active recall before looking at the answer, or add any tricky school topic above."
        mood="happy"
      />
      <div
        className="rounded-3xl text-white p-6 border border-[#5146E5]/30 shadow-lg space-y-4"
        style={{ background: 'linear-gradient(135deg, #101B35 0%, #232A6B 60%, #5146E5 100%)' }}
      >
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-1">
            <span className="text-[11px] font-extrabold uppercase tracking-wider text-[#35D6E8]">
              Smart Revision • Spaced Active Recall
            </span>
            <h2 className="text-xl md:text-2xl font-extrabold text-white">
              Quick recall cards for topics you need most.
            </h2>
          </div>

          <form onSubmit={handleGenerateCard} className="flex flex-wrap gap-2 text-xs">
            <select
              value={newSubject}
              onChange={(e) => setNewSubject(e.target.value)}
              className="rounded-xl border border-white/20 bg-white/10 text-white px-3 py-2 font-bold min-h-[40px]"
            >
              <option value="Mathematics" className="text-slate-900">Mathematics</option>
              <option value="General Science" className="text-slate-900">General Science</option>
              <option value="Social Science" className="text-slate-900">Social Science</option>
            </select>
            <input
              type="text"
              value={newTopic}
              onChange={(e) => setNewTopic(e.target.value)}
              placeholder="Topic to revise..."
              className="rounded-xl border border-white/20 bg-white text-[#101B35] px-3 py-2 font-semibold min-h-[40px]"
            />
            <button
              type="submit"
              className="px-4 py-2 rounded-xl bg-[#35D6E8] hover:bg-cyan-300 text-[#101B35] font-extrabold transition min-h-[40px]"
            >
              + Add Card
            </button>
          </form>
        </div>
      </div>

      {cards.length === 0 ? (
        <div className="eduspark-card rounded-3xl p-8 md:p-10 text-center space-y-5">
          <div className="flex justify-center">
            <SparkRobotMascot mood="guiding" size="lg" />
          </div>
          <div className="space-y-1.5 max-w-md mx-auto">
            <h3 className="font-display text-xl font-bold text-[#101B35]">
              Build your first Active Recall Deck
            </h3>
            <p className="text-xs sm:text-sm text-[#202943]/75 font-medium">
              SparkMinds AI turns tricky school topics and mock exam mistakes into quick spaced-repetition flashcards. Tap a topic below or add your own above.
            </p>
          </div>
          <div className="flex flex-wrap justify-center gap-2">
            {[
              { subj: 'Mathematics', topic: 'Fractions & Decimals' },
              { subj: 'General Science', topic: 'The Water Cycle' },
              { subj: 'Social Science', topic: 'Landforms & Rivers' },
            ].map((preset) => (
              <button
                key={preset.topic}
                type="button"
                onClick={async () => {
                  try {
                    await fetch(`/api/students/${onboarding.studentId}/revision/generate`, {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({
                        student_id: onboarding.studentId,
                        subject: preset.subj,
                        topic: preset.topic,
                      }),
                    });
                    fetchCards();
                  } catch {}
                }}
                className="px-4 py-2.5 rounded-xl bg-[#EEEAFE] hover:bg-[#5146E5] text-[#5146E5] hover:text-white text-xs font-extrabold transition"
              >
                + {preset.subj}: {preset.topic}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-5">
          {cards.map((card) => {
          const isFlipped = !!flippedIds[card.revision_id];
          const chosenAns = selectedQuizAnswers[card.revision_id];
          return (
            <div
              key={card.revision_id}
              className="eduspark-card eduspark-card-hover rounded-3xl p-5 space-y-4 text-xs"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="font-extrabold text-sm text-slate-900">
                  {card.subject}: {card.topic}
                </span>
                <div className="flex items-center gap-1.5">
                  <span
                    className={`px-2.5 py-0.5 rounded-full font-extrabold ${card.source_tag === 'Mock Exam Mistake' ||
                        card.source_tag === 'Tutor Misconception'
                        ? 'bg-red-100 text-red-800'
                        : card.source_tag === 'Forgotten Topic'
                          ? 'bg-amber-100 text-amber-900'
                          : 'bg-blue-100 text-blue-900'
                      }`}
                  >
                    {card.source_tag}
                  </span>
                  <span className="px-2 py-0.5 rounded-md bg-slate-100 font-bold text-slate-700">
                    Interval: {card.interval_days}d (Next:{' '}
                    {formatRevisionSchedule12Hour(
                      card.next_review_date,
                      '17:30'
                    )}
                    )
                  </span>
                </div>
              </div>

              {/* Interactive Flip Flashcard */}
              <div
                onClick={() =>
                  setFlippedIds((p) => ({
                    ...p,
                    [card.revision_id]: !isFlipped,
                  }))
                }
                className={`p-4 rounded-2xl border-2 cursor-pointer transition ${isFlipped
                    ? 'border-emerald-300 bg-emerald-50 text-emerald-950'
                    : 'border-blue-200 bg-blue-50/60 text-slate-900'
                  }`}
              >
                <div className="font-extrabold uppercase text-[11px] text-blue-700 mb-1">
                  {isFlipped
                    ? '✓ Back of Flashcard (Step-by-Step Explanation)'
                    : '📇 Front of Flashcard (Click to Flip)'}
                </div>
                <div className="font-semibold whitespace-pre-line text-sm">
                  {isFlipped ? card.back_explanation : card.front_prompt}
                </div>
              </div>

              {/* Active Recall Mini-Quiz */}
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                <div className="font-extrabold text-slate-900">
                  ⚡ Active Recall Check: {card.active_recall_question}
                </div>
                <div className="grid grid-cols-1 gap-1.5">
                  {card.active_recall_options.map((opt) => {
                    const isSelected = chosenAns === opt;
                    const isCorrect = opt === card.active_recall_answer;
                    return (
                      <button
                        key={opt}
                        type="button"
                        onClick={() =>
                          setSelectedQuizAnswers((p) => ({
                            ...p,
                            [card.revision_id]: opt,
                          }))
                        }
                        className={`p-2 rounded-xl border text-left font-bold ${isSelected
                            ? isCorrect
                              ? 'border-emerald-500 bg-emerald-100 text-emerald-950'
                              : 'border-red-400 bg-red-100 text-red-950'
                            : 'border-slate-200 bg-white hover:bg-slate-100'
                          }`}
                      >
                        {opt}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Spaced Repetition Rating Buttons */}
              <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
                <span className="font-bold text-slate-600">
                  Rate Recall to Schedule Next Spaced Repetition:
                </span>
                <div className="flex gap-1.5">
                  {(['Forgot', 'Hard', 'Good', 'Easy'] as const).map((q) => (
                    <button
                      key={q}
                      type="button"
                      onClick={() => submitSpacedReview(card.revision_id, q)}
                      className={`px-2.5 py-1 rounded-lg font-extrabold ${q === 'Easy' || q === 'Good'
                          ? 'bg-emerald-600 text-white'
                          : q === 'Hard'
                            ? 'bg-amber-100 text-amber-900'
                            : 'bg-red-100 text-red-900'
                        }`}
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      )}
    </div>
  );
};

// ============================================================================
// G. ACADEMIC PROGRESS DASHBOARD & SUBJECT LEARNING EXPLORER
// ============================================================================

export const AcademicProgressDashboardView: React.FC<{
  onboarding: OnboardingState;
}> = ({ onboarding }) => {
  const [report, setReport] = React.useState<{
    subject_wise_progress: {
      subject: string;
      overall_mastery_percentage: number;
      verified_assessment_average: number | null;
      homework_practice_average: number | null;
      student_reported_exam_average?: number | null;
      self_reported_confidence: string;
      needs_additional_attention?: boolean;
    }[];
    subjects_requiring_attention?: string[];
    exam_marks_history?: ExamMarkRecordUI[];
    homework_completion_rate: number;
    separated_evidence: {
      ACTUAL_ASSESSMENT: {
        record_id: string;
        subject_name: string;
        topic_name: string;
        score_percentage: number | null;
        trend_indicator: string;
        notes: string;
      }[];
      HOMEWORK_PRACTICE: {
        record_id: string;
        subject_name: string;
        topic_name: string;
        score_percentage: number | null;
        trend_indicator: string;
        notes: string;
      }[];
      STUDENT_SELF_REPORT: {
        record_id: string;
        subject_name: string;
        topic_name: string;
        qualitative_rating: string | null;
        notes: string;
      }[];
    };
    unresolved_learning_gaps: string[];
    resolved_learning_gaps: string[];
  } | null>(null);

  React.useEffect(() => {
    fetch(`/api/students/${onboarding.studentId}/progress`)
      .then((r) => r.json())
      .then((d) => setReport(d))
      .catch(() => { });
  }, [onboarding.studentId]);

  if (!report) {
    return (
      <div className="p-6 rounded-3xl bg-white border border-slate-200 text-xs font-bold">
        Loading Evidence-Separated Academic Progress Report...
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Midnight-Indigo Progress Header */}
      <RobotGuideTip
        tipId="academic_progress"
        studentId={onboarding.studentId}
        title="Sparky's Real Progress Insights"
        message="Every score here reflects genuine completed quizzes, homework, and lessons — zero inflated numbers."
        mood="guiding"
      />
      <div
        className="rounded-3xl text-white p-6 border border-[#5146E5]/30 shadow-lg flex flex-wrap items-center justify-between gap-4"
        style={{ background: 'linear-gradient(135deg, #101B35 0%, #232A6B 60%, #5146E5 100%)' }}
      >
        <div className="space-y-1">
          <span className="text-[11px] font-extrabold uppercase tracking-wider text-[#35D6E8]">
            Academic Progress & Real Analytics
          </span>
          <h2 className="text-xl md:text-2xl font-extrabold text-white">
            Your real mastery, streaks, and learning gaps.
          </h2>
        </div>
        {report.subjects_requiring_attention &&
          report.subjects_requiring_attention.length > 0 && (
            <span className="px-3.5 py-2 rounded-xl bg-rose-500/20 text-rose-200 text-xs font-extrabold border border-rose-400/30">
              Focus Needed: {report.subjects_requiring_attention.join(', ')}
            </span>
          )}
      </div>

      <div className="eduspark-card rounded-3xl p-6 space-y-5">
        <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs">
          {report.subject_wise_progress.map((s) => (
            <div
              key={s.subject}
              className={`p-4 rounded-2xl border space-y-2 ${s.needs_additional_attention
                  ? 'border-rose-300 bg-rose-50/40'
                  : 'border-slate-200 bg-white'
                }`}
            >
              <div className="flex items-center justify-between">
                <div className="font-extrabold text-sm text-[#101B35]">
                  {s.subject}
                </div>
                {s.needs_additional_attention && (
                  <span className="px-2 py-0.5 rounded-full bg-rose-600 text-white text-[10px] font-extrabold">
                    Focus
                  </span>
                )}
              </div>
              <div className="text-2xl font-extrabold text-[#101B35]">
                {s.overall_mastery_percentage}%
              </div>
              <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden">
                <div
                  className={`h-full rounded-full ${s.needs_additional_attention ? 'bg-rose-500' : 'bg-[#5146E5]'
                    }`}
                  style={{ width: `${Math.min(100, s.overall_mastery_percentage)}%` }}
                />
              </div>
              <div className="text-slate-600 space-y-0.5">
                <div>
                  Verified Exam Avg:{' '}
                  <strong>
                    {s.verified_assessment_average !== null
                      ? `${s.verified_assessment_average}%`
                      : 'Pending Exam'}
                  </strong>
                </div>
                <div>
                  Practice Avg:{' '}
                  <strong>
                    {s.homework_practice_average !== null
                      ? `${s.homework_practice_average}%`
                      : 'N/A'}
                  </strong>
                </div>
                {s.student_reported_exam_average !== undefined &&
                  s.student_reported_exam_average !== null && (
                    <div>
                      Student-Reported Exam Avg:{' '}
                      <strong className="text-amber-800">
                        {s.student_reported_exam_average}% (STUDENT_REPORTED)
                      </strong>
                    </div>
                  )}
                <div>
                  Self-Report: <strong>{s.self_reported_confidence}</strong>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Exam-Wise Results & Progress Chart */}
        {report.exam_marks_history && report.exam_marks_history.length > 0 && (
          <div className="pt-4 border-t border-slate-100 space-y-3 text-xs">
            <h3 className="text-sm font-extrabold text-slate-900">
              📊 Exam-Wise Results & Performance Progress Chart
            </h3>
            <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3">
              {report.exam_marks_history.map((mk) => (
                <div
                  key={mk.mark_id}
                  className="p-3.5 rounded-2xl border border-slate-200 bg-slate-50/70 space-y-1.5"
                >
                  <div className="flex items-center justify-between font-extrabold text-slate-900">
                    <span>
                      {mk.subject} — {mk.exam_name}
                    </span>
                    <span className="text-blue-700">{mk.percentage}%</span>
                  </div>
                  <div className="w-full h-2.5 rounded-full bg-slate-200 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${mk.percentage < 65
                          ? 'bg-rose-500'
                          : mk.percentage >= 80
                            ? 'bg-emerald-500'
                            : 'bg-blue-600'
                        }`}
                      style={{ width: `${Math.min(100, mk.percentage)}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-600">
                    <span>
                      Marks: {mk.marks_obtained}/{mk.maximum_marks} ({mk.exam_date})
                    </span>
                    <span className="font-bold text-amber-900">
                      {mk.trend} • {mk.verification_status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 3-Column Strict Separation of Evidence Sources */}
      <div className="grid md:grid-cols-3 gap-4 text-xs">
        <div className="bg-white border-2 border-emerald-200 rounded-3xl p-5 space-y-3">
          <div className="font-extrabold text-sm text-emerald-900">
            1. Verified Assessments (ACTUAL_ASSESSMENT)
          </div>
          {report.separated_evidence.ACTUAL_ASSESSMENT.map((ev) => (
            <div
              key={ev.record_id}
              className="p-3 rounded-2xl bg-emerald-50/70 border border-emerald-200 space-y-1"
            >
              <div className="font-extrabold text-slate-900">
                {ev.subject_name}: {ev.topic_name} ({ev.score_percentage}%)
              </div>
              <div className="text-slate-600">{ev.notes}</div>
            </div>
          ))}
        </div>

        <div className="bg-white border-2 border-blue-200 rounded-3xl p-5 space-y-3">
          <div className="font-extrabold text-sm text-blue-900">
            2. Guided Homework & Tutor Practice (HOMEWORK_PRACTICE)
          </div>
          {report.separated_evidence.HOMEWORK_PRACTICE.map((ev) => (
            <div
              key={ev.record_id}
              className="p-3 rounded-2xl bg-blue-50/70 border border-blue-200 space-y-1"
            >
              <div className="font-extrabold text-slate-900">
                {ev.subject_name}: {ev.topic_name} ({ev.score_percentage}%)
              </div>
              <div className="text-slate-600">{ev.notes}</div>
            </div>
          ))}
        </div>

        <div className="bg-white border-2 border-amber-200 rounded-3xl p-5 space-y-3">
          <div className="font-extrabold text-sm text-amber-900">
            3. Student Self-Reports (Never Treated as Verified Scores)
          </div>
          {report.separated_evidence.STUDENT_SELF_REPORT.map((ev) => (
            <div
              key={ev.record_id}
              className="p-3 rounded-2xl bg-amber-50/70 border border-amber-200 space-y-1"
            >
              <div className="font-extrabold text-slate-900">
                {ev.subject_name}: {ev.topic_name}
              </div>
              <div className="font-bold text-amber-900">
                Self-Reported Confidence: &quot;{ev.qualitative_rating}&quot;
              </div>
              <div className="text-slate-600">{ev.notes}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Agentic Learning Gap Analyzer, Connected Cycle & Real Gamification */}
      <LearningGapsAndGamificationPanel studentId={onboarding.studentId} />
    </div>
  );
};

// ============================================================================
// I. SCHOOL PROJECT & CREATIVITY LAB VIEW (CONNECTED TO /api/students/{id}/projects)
// ============================================================================

interface ProjectItem {
  project_id: string;
  subject: string;
  chapter_or_theme: string;
  project_type: string;
  title: string;
  learning_objective: string;
  materials_needed: string[];
  milestones: {
    step: number;
    title: string;
    guidance: string;
    completed: boolean;
  }[];
  research_guidance_prompts: string[];
  presentation_slide_outline: string[];
  socratic_creativity_challenge: string;
  student_notes: string;
  student_creativity_response: string;
  progress_percentage: number;
}

export const SchoolProjectCreativityLabView: React.FC<{
  onboarding: OnboardingState;
}> = ({ onboarding }) => {
  const curriculumSubjects = React.useMemo(
    () =>
      getCurriculumSubjects(
        onboarding.grade,
        onboarding.board,
        onboarding.stateName
      ),
    [onboarding.grade, onboarding.board, onboarding.stateName]
  );

  const [projects, setProjects] = React.useState<ProjectItem[]>([]);
  const [subject, setSubject] = React.useState<string>(
    curriculumSubjects[1]?.name || 'General Science'
  );
  const [theme, setTheme] = React.useState<string>('Acids, Bases & Salts');
  const [projectType, setProjectType] = React.useState<string>(
    'Science Experiment'
  );

  const fetchProjects = React.useCallback(async () => {
    const res = await fetch(`/api/students/${onboarding.studentId}/projects`);
    if (res.ok) {
      const data = await res.json();
      setProjects(data.projects || []);
    }
  }, [onboarding.studentId]);

  React.useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const generateProject = async () => {
    await fetch(`/api/students/${onboarding.studentId}/projects/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: onboarding.studentId,
        subject,
        chapter_or_theme: theme,
        project_type: projectType,
      }),
    });
    fetchProjects();
  };

  const updateMilestone = async (
    projId: string,
    idx: number,
    completed: boolean
  ) => {
    await fetch(`/api/students/${onboarding.studentId}/projects/${projId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: onboarding.studentId,
        milestone_index: idx,
        completed,
      }),
    });
    fetchProjects();
  };

  const saveStudentNotes = async (
    projId: string,
    notes: string,
    creativity: string
  ) => {
    await fetch(`/api/students/${onboarding.studentId}/projects/${projId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: onboarding.studentId,
        student_notes: notes,
        student_creativity_response: creativity,
      }),
    });
    fetchProjects();
  };

  return (
    <div className="space-y-6">
      <div className="eduspark-card rounded-3xl p-6 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <span className="text-xs font-extrabold uppercase text-emerald-700">
              Guided Project Mentorship • We Guide You to Build & Understand
            </span>
            <h2 className="text-xl font-extrabold text-slate-900">
              School Project & Creativity Lab (Grade {onboarding.grade})
            </h2>
          </div>

          <div className="flex flex-wrap gap-2 text-xs">
            <select
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="rounded-xl border border-slate-300 px-3 py-2 font-bold"
            >
              {curriculumSubjects.map((s) => (
                <option key={s.code} value={s.name}>
                  {s.name}
                </option>
              ))}
            </select>
            <input
              type="text"
              value={theme}
              onChange={(e) => setTheme(e.target.value)}
              placeholder="Chapter or project theme..."
              className="rounded-xl border border-slate-300 px-3 py-2 font-semibold"
            />
            <select
              value={projectType}
              onChange={(e) => setProjectType(e.target.value)}
              className="rounded-xl border border-slate-300 px-3 py-2 font-bold"
            >
              <option value="Science Experiment">Science Experiment</option>
              <option value="Working Model">Working Model</option>
              <option value="Research & Survey">Research & Survey</option>
              <option value="Creative Poster / Presentation">
                Creative Presentation
              </option>
            </select>
            <button
              type="button"
              onClick={generateProject}
              className="px-4 py-2 rounded-xl bg-[#2563EB] text-white font-extrabold"
            >
              + Generate Guided Project Plan
            </button>
          </div>
        </div>
      </div>

      {projects.map((proj) => (
        <div
          key={proj.project_id}
          className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm space-y-5 text-xs"
        >
          <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-100">
            <div>
              <span className="font-extrabold uppercase text-blue-600">
                {proj.project_type} • {proj.subject} ({proj.chapter_or_theme})
              </span>
              <h3 className="text-lg font-extrabold text-slate-900">
                {proj.title}
              </h3>
              <p className="text-slate-600 mt-0.5">{proj.learning_objective}</p>
            </div>
            <span className="px-3.5 py-1.5 rounded-full bg-emerald-100 text-emerald-900 font-extrabold">
              Milestone Progress: {proj.progress_percentage}%
            </span>
          </div>

          <div className="grid md:grid-cols-2 gap-5">
            {/* Step-by-Step Milestones */}
            <div className="space-y-2.5">
              <h4 className="font-extrabold text-slate-900 uppercase">
                Step-by-Step Build & Research Milestones
              </h4>
              {proj.milestones.map((m, idx) => (
                <div
                  key={m.step}
                  onClick={() =>
                    updateMilestone(proj.project_id, idx, !m.completed)
                  }
                  className={`p-3.5 rounded-2xl border cursor-pointer flex items-start gap-2.5 ${m.completed
                      ? 'bg-emerald-50 border-emerald-300 text-emerald-950'
                      : 'bg-slate-50 border-slate-200'
                    }`}
                >
                  <input
                    type="checkbox"
                    checked={m.completed}
                    readOnly
                    className="mt-0.5 w-4 h-4"
                  />
                  <div>
                    <div className="font-extrabold">
                      Step {m.step}: {m.title}
                    </div>
                    <div className="text-slate-600 mt-0.5">{m.guidance}</div>
                  </div>
                </div>
              ))}
            </div>

            {/* Materials, Presentation Slide Outline & Creativity Challenge */}
            <div className="space-y-4">
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-1.5">
                <div className="font-extrabold text-slate-900">
                  🧰 Materials Needed
                </div>
                <ul className="list-disc list-inside text-slate-700 space-y-1">
                  {proj.materials_needed.map((mat, i) => (
                    <li key={i}>{mat}</li>
                  ))}
                </ul>
              </div>

              <div className="p-4 rounded-2xl bg-blue-50/60 border border-blue-200 space-y-1.5">
                <div className="font-extrabold text-blue-950">
                  🖥️ Presentation Outline (Build in Your Own Words)
                </div>
                <ul className="list-disc list-inside text-blue-900 space-y-1">
                  {proj.presentation_slide_outline.map((sl, i) => (
                    <li key={i}>{sl}</li>
                  ))}
                </ul>
              </div>

              <div className="p-4 rounded-2xl bg-amber-50 border border-amber-300 space-y-2">
                <div className="font-extrabold text-amber-950">
                  {proj.socratic_creativity_challenge}
                </div>
                <textarea
                  rows={2}
                  defaultValue={proj.student_creativity_response}
                  onBlur={(e) =>
                    saveStudentNotes(
                      proj.project_id,
                      proj.student_notes,
                      e.target.value
                    )
                  }
                  placeholder="Write your original creative analogy or observation log here (auto-saves on blur)..."
                  className="w-full rounded-xl border border-amber-300 bg-white p-2.5 font-medium"
                />
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

// ============================================================================
// SUBJECT LEARNING EXPLORER VIEW (SCREEN 7: subjects)
// ============================================================================

export const SubjectLearningExplorerView: React.FC<{
  onboarding: OnboardingState;
  onOpenBuddyWithQuestion: (q: string, subject: string) => void;
  onSelectScreen: (s: ScreenId) => void;
}> = ({ onboarding, onOpenBuddyWithQuestion, onSelectScreen }) => {
  const subjects = getCurriculumSubjects(
    onboarding.grade,
    onboarding.board,
    onboarding.stateName
  );

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Duolingo-Inspired Step-by-Step Interactive Lesson Studio */}
      <GuidedInteractiveLesson
        onboarding={onboarding}
        onAskBuddy={onOpenBuddyWithQuestion}
      />

      {/* Full Grade Curriculum Explorer */}
      <div className="eduspark-card rounded-3xl p-6 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-100">
          <div>
            <span className="text-xs font-extrabold uppercase text-[#5146E5]">
              Grade {onboarding.grade} • {onboarding.board} Syllabus
            </span>
            <h2 className="text-lg font-extrabold text-[#101B35]">
              All Chapters & Quick AI Explanations
            </h2>
          </div>
          <button
            type="button"
            onClick={() => onSelectScreen('exams')}
            className="px-4 py-2 rounded-xl bg-[#101B35] hover:bg-[#1B2654] text-[#35D6E8] text-xs font-extrabold transition"
          >
            Practice Quiz →
          </button>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          {subjects.map((sub) => {
            const isFocus = onboarding.subjectsToImprove.includes(sub.code);
            return (
              <div
                key={sub.code}
                className={`p-5 rounded-2xl border space-y-3 ${
                  isFocus
                    ? 'border-[#5146E5]/60 bg-cyan-50/30'
                    : 'border-slate-200 bg-white'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-extrabold text-sm text-[#101B35]">
                    {sub.name}
                  </span>
                  {isFocus && (
                    <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-[#101B35] text-[#35D6E8] font-bold">
                      Focus Subject
                    </span>
                  )}
                </div>

                <div className="space-y-2">
                  {sub.topics.map((topic) => (
                    <div
                      key={topic}
                      className="p-3 rounded-xl bg-white border border-slate-200 flex flex-wrap items-center justify-between gap-2 text-xs"
                    >
                      <span className="font-bold text-slate-800">{topic}</span>
                      <button
                        type="button"
                        onClick={() =>
                          onOpenBuddyWithQuestion(
                            `Explain the core concepts of ${topic} in ${sub.name} with a real-world example and ask me one check question.`,
                            sub.name
                          )
                        }
                        className="px-3 py-1.5 rounded-lg bg-[#101B35] hover:bg-[#1B2654] text-[#35D6E8] font-extrabold transition"
                      >
                        Ask Buddy →
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Document Learning & Grounded RAG Study Assistant */}
      <DocumentStudyRAGPanel studentId={onboarding.studentId} />
    </div>
  );
};
