import React from 'react';
import {
  Send,
  Lightbulb,
  Languages,
  Upload,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Shield,
  TrendingUp,
  TrendingDown,
  BookOpen,
  RefreshCw,
  HelpCircle,
  Eye,
  Video,
  Image as ImageIcon,
  Play,
  ExternalLink,
  MessageSquare,
  Flame,
  Repeat,
} from 'lucide-react';
import { ALL_23_INDIAN_LANGUAGES } from '../curriculum/curriculumData';
import { OnboardingState } from '../onboarding/SevenStepOnboarding';
import {
  AgentOrchestratorBar,
  BackendAgentExecutionLog,
} from '../components/AgentOrchestratorBar';
import { ScreenId } from '../design-system/tokens';
import {
  formatTime12Hour,
  formatTimeRange12Hour,
  formatHomeworkDeadline12Hour,
  formatExamSchedule12Hour,
} from '../utils/timeFormat';
import { LearningBuddyChat } from './LearningBuddyChat';
export interface HistoricalYearRecord {
  academicYearId: string;
  academicYearLabel: string;
  grade: number;
  board: string;
  stateName?: string;
  schoolMedium: string;
  preferredExplanationLanguage: string;
  secondaryExplanationLanguage?: string;
  status: 'ACTIVE' | 'COMPLETED_PROMOTED' | 'COMPLETED_REPEATED';
  isLockedHistorical: boolean;
  subjectsStudied: string[];
  unresolvedGaps: string[];
  resolvedGaps: string[];
  evidenceRecords: {
    id: string;
    subject: string;
    topic: string;
    evidenceType:
    | 'ACTUAL_ASSESSMENT'
    | 'HOMEWORK_PRACTICE'
    | 'STUDENT_SELF_REPORT'
    | 'PARENT_TEACHER_FEEDBACK'
    | 'AI_ESTIMATE';
    scorePercentage: number | null;
    qualitativeRating?: string;
    trendIndicator:
    | 'Improvement'
    | 'Decline'
    | 'Needs attention'
    | 'Consistent performance'
    | 'Learning gap resolved';
    notes: string;
  }[];
}

// ============================================================================
// INTERACTIVE STATEFUL HOMEWORK TUTOR & AI LEARNING BUDDY (SECTION 4 & 8)
// ============================================================================

interface TutorSessionResponse {
  session_id: string;
  student_id: string;
  grade: number;
  school_board: string;
  preferred_explanation_language: string;
  secondary_explanation_language?: string | null;
  current_node: string;
  conditional_route_taken: string;
  student_response_required: boolean;
  extracted_question: string;
  detected_subject: string;
  detected_topic: string;
  current_step_index: number;
  total_steps: number;
  mistake_count: number;
  hint_level: number;
  student_attempts_history: string[];
  detected_misconceptions_history: string[];
  hints_provided_history: string[];
  understanding_output?: {
    extracted_question: string;
    is_question_clear: boolean;
    clarification_prompt?: string | null;
    detected_subject: string;
    detected_topic: string;
    curriculum_context: string[];
    processed_from_image: boolean;
  } | null;
  diagnosis_output?: {
    prerequisite_concepts: string[];
    missing_prerequisite_detected: boolean;
    missing_prerequisite_topic?: string | null;
    detected_historical_misconceptions: string[];
    specific_knowledge_gaps: string[];
    verified_learning_evidence: string[];
    student_self_reported_difficulties: string[];
    diagnostic_question: string;
    recommended_pedagogical_route: string;
  } | null;
  teaching_output?: {
    explanation_language: string;
    secondary_explanation_language?: string | null;
    bilingual_active: boolean;
    language_capability_notice?: string | null;
    pedagogical_mode_applied: string;
    concept_explanation: string;
    bilingual_secondary_explanation?: string | null;
    real_world_example: string;
    prerequisite_mini_lesson?: string | null;
    steps_breakdown: {
      step_number: number;
      title: string;
      instruction: string;
      why_this_step_matters?: string | null;
      step_formula_or_rule?: string | null;
      question_for_student: string;
      expected_checkpoint: string;
    }[];
    active_step_number: number;
    prompt_for_student_attempt: string;
    progressive_hints: string[];
    active_hint_shown?: string | null;
    incorrect_answer_explanation?: string | null;
    alternative_explanation?: string | null;
    full_worked_solution?: string | null;
    answer_withheld_for_guided_learning: boolean;
    similar_practice_question: {
      question: string;
      topic: string;
      expected_concept: string;
    };
    visual_diagram_svg?: string | null;
    visual_diagram_caption?: string | null;
    visual_concept_type?: string | null;
    video_explanation?: {
      title: string;
      platform: string;
      duration: string;
      youtube_embed_id?: string | null;
      search_query: string;
      recommended_timestamp?: string | null;
      key_takeaways: string[];
    } | null;
  } | null;
  assessment_output?: {
    is_attempt_correct: boolean;
    is_problem_completed: boolean;
    mistake_step_number?: number | null;
    detected_misconception?: string | null;
    why_incorrect_explanation?: string | null;
    encouraging_feedback: string;
    follow_up_verification_question?: string | null;
    conceptual_understanding_verified: boolean;
    mastery_evidence_score?: number | null;
    next_routing_action: string;
  } | null;
  execution_logs: BackendAgentExecutionLog[];
  followup_qa_history?: {
    question: string;
    answer: string;
    step: string;
    timestamp: string;
  }[];
  practice_streak?: number;
  error_state?: string | null;
}

interface AILearningBuddyViewProps {
  onboarding: OnboardingState;
  mode?: 'buddy' | 'homework';
  initialQuestion?: string;
  initialSubject?: string;
  onSelectScreen?: (s: ScreenId) => void;
}

export const AILearningBuddyView: React.FC<AILearningBuddyViewProps> = ({
  onboarding,
  mode = 'buddy',
  initialQuestion,
  initialSubject,
  onSelectScreen,
}) => {
  const [activeTab, setActiveTab] = React.useState<'interactive' | 'chat'>('chat');
  const [questionInput, setQuestionInput] = React.useState<string>(initialQuestion || '');
  const [subjectHint, setSubjectHint] = React.useState<string>(initialSubject || 'Mathematics');
  const [selectedLang, setSelectedLang] = React.useState<string>(onboarding.preferredExplanationLanguage);
  const [uploadedImageBase64, setUploadedImageBase64] = React.useState<string>('');
  const [uploadedImageName, setUploadedImageName] = React.useState<string>('');
  const [studentAttemptInput, setStudentAttemptInput] = React.useState<string>('');
  const [followupInput, setFollowupInput] = React.useState<string>('');
  const [practiceAttemptInput, setPracticeAttemptInput] = React.useState<string>('');
  const [showFollowupComposer, setShowFollowupComposer] = React.useState<boolean>(false);
  const [sessionState, setSessionState] = React.useState<TutorSessionResponse | null>(null);
  const [apiError, setApiError] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(false);

  React.useEffect(() => {
    setSelectedLang(onboarding.preferredExplanationLanguage);
  }, [onboarding.preferredExplanationLanguage]);

  React.useEffect(() => {
    if (initialQuestion) {
      setQuestionInput(initialQuestion);
    }
    if (initialSubject) {
      setSubjectHint(initialSubject);
    }
  }, [initialQuestion, initialSubject]);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadedImageName(file.name);
    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === 'string') {
        setUploadedImageBase64(reader.result);
      }
    };
    reader.readAsDataURL(file);
  };

  const startTutorSession = async (customQ?: string, customSubj?: string) => {
    const q = customQ !== undefined ? customQ : questionInput;
    if (!q.trim() && !uploadedImageBase64) return;
    setIsLoading(true);
    setApiError(null);
    try {
      const res = await fetch('/api/tutor/session/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: onboarding.studentId,
          typed_question: q,
          image_base64: uploadedImageBase64 || null,
          subject_hint: customSubj || subjectHint,
          language_override: selectedLang,
          secondary_language_override: onboarding.secondaryExplanationLanguage || null,
        }),
      });
      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`HTTP ${res.status}: ${errText}`);
      }
      const data: TutorSessionResponse = await res.json();
      setSessionState(data);
      setStudentAttemptInput('');
    } catch (err: unknown) {
      setApiError(
        err instanceof Error
          ? err.message
          : 'Failed to reach backend interactive tutoring engine.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const submitStudentTurn = async (
    actionType:
      | 'SUBMIT_STEP_ATTEMPT'
      | 'REQUEST_PROGRESSIVE_HINT'
      | 'REQUEST_ALTERNATIVE_EXPLANATION'
      | 'REQUEST_FULL_SOLUTION'
      | 'REQUEST_SIMILAR_PRACTICE'
      | 'ASK_FOLLOWUP_QUESTION'
      | 'SUBMIT_PRACTICE_ATTEMPT',
    customAttempt?: string
  ) => {
    if (!sessionState) return;
    setIsLoading(true);
    setApiError(null);
    try {
      const attemptText =
        customAttempt !== undefined
          ? customAttempt
          : actionType === 'ASK_FOLLOWUP_QUESTION'
          ? followupInput
          : actionType === 'SUBMIT_PRACTICE_ATTEMPT'
          ? practiceAttemptInput
          : studentAttemptInput;

      const res = await fetch('/api/tutor/session/turn', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionState.session_id,
          student_id: onboarding.studentId,
          action_type: actionType,
          student_attempt: attemptText,
          language_override: selectedLang,
        }),
      });
      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`HTTP ${res.status}: ${errText}`);
      }
      const data: TutorSessionResponse = await res.json();
      setSessionState(data);
      if (actionType === 'SUBMIT_STEP_ATTEMPT') {
        setStudentAttemptInput('');
      } else if (actionType === 'ASK_FOLLOWUP_QUESTION') {
        setFollowupInput('');
      } else if (actionType === 'SUBMIT_PRACTICE_ATTEMPT') {
        setPracticeAttemptInput('');
      }
    } catch (err: unknown) {
      setApiError(
        err instanceof Error ? err.message : 'Failed to process student turn.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Mode Switcher Tabs: Clean Conversational Buddy vs Step-by-Step Socratic Studio */}
      <div className="flex flex-wrap items-center justify-between bg-white rounded-2xl p-2 border border-slate-200 shadow-sm gap-2">
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => setActiveTab('chat')}
            className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-extrabold transition min-h-[42px] ${
              activeTab === 'chat'
                ? 'bg-[#101B35] text-[#35D6E8] shadow-sm'
                : 'text-slate-600 hover:text-[#101B35] hover:bg-slate-100'
            }`}
          >
            <Send className="w-4 h-4" />
            <span>AI Learning Buddy</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('interactive')}
            className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-extrabold transition min-h-[42px] ${
              activeTab === 'interactive'
                ? 'bg-[#101B35] text-[#35D6E8] shadow-sm'
                : 'text-slate-600 hover:text-[#101B35] hover:bg-slate-100'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>Step-by-Step Solver</span>
          </button>
        </div>

        {activeTab === 'interactive' && sessionState && (
          <button
            type="button"
            onClick={() => {
              setSessionState(null);
              setQuestionInput('');
              setUploadedImageBase64('');
              setUploadedImageName('');
            }}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-slate-200 text-xs font-bold text-slate-700 bg-slate-50 hover:bg-slate-100 transition"
          >
            <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
            <span>New Question</span>
          </button>
        )}
      </div>

      {/* Render AI Conversational Buddy when 'chat' tab is active */}
      {activeTab === 'chat' ? (
        <LearningBuddyChat
          onboarding={onboarding}
          initialQuestion={questionInput || initialQuestion}
          initialSubject={subjectHint || initialSubject}
          onSelectScreen={onSelectScreen}
        />
      ) : (
        /* Render Full Interactive Socratic Tutoring Suite when 'interactive' tab is active */
        <div className="space-y-6">
          {/* Real-Time Agent Execution Pipeline Bar */}
          <AgentOrchestratorBar
            executionLogs={sessionState?.execution_logs || []}
            currentNode={sessionState?.current_node || 'IDLE_READY'}
            conditionalRouteTaken={sessionState?.conditional_route_taken}
            studentResponseRequired={sessionState?.student_response_required}
            errorState={apiError || sessionState?.error_state}
          />

          {/* Interactive Tutoring Studio Header & Composer */}
          <div className="eduspark-card rounded-3xl overflow-hidden shadow-sm">
            <div className="bg-[#101B35] px-6 py-4 text-white flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-white/10 flex items-center justify-center border border-[#35D6E8]/40">
                  <Sparkles className="w-5 h-5 text-[#35D6E8]" />
                </div>
                <div>
                  <span className="text-[11px] font-extrabold uppercase tracking-wider text-[#35D6E8]">
                    {mode === 'homework' ? 'Homework Solver' : 'Step-by-Step Socratic Tutor'}
                  </span>
                  <h3 className="text-base md:text-lg font-extrabold tracking-tight text-white">
                    Work through any problem one step at a time
                  </h3>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <select
                  value={subjectHint}
                  onChange={(e) => setSubjectHint(e.target.value)}
                  className="rounded-xl border border-white/25 bg-white/15 backdrop-blur px-3 py-1.5 text-xs font-extrabold text-white focus:outline-none"
                >
                  <option value="Mathematics" className="text-slate-900">Mathematics</option>
                  <option value="Science" className="text-slate-900">Science (Physics / Chem / Bio)</option>
                  <option value="Social Science" className="text-slate-900">Social Studies (History / Geo / Civics)</option>
                  <option value="English" className="text-slate-900">English & Grammar</option>
                  <option value="Computer Science" className="text-slate-900">Computer Science & Python</option>
                  <option value="General Knowledge" className="text-slate-900">General Knowledge</option>
                </select>

                <div className="flex items-center gap-1.5 bg-white/15 backdrop-blur rounded-xl px-2.5 py-1 border border-white/25">
                  <Languages className="w-4 h-4 text-amber-300" />
                  <select
                    value={selectedLang}
                    onChange={(e) => setSelectedLang(e.target.value)}
                    className="bg-transparent text-xs font-extrabold text-white focus:outline-none"
                  >
                    {ALL_23_INDIAN_LANGUAGES.map((l) => (
                      <option key={l.code} value={l.name} className="text-slate-900">
                        {l.name} ({l.nativeName}){' '}
                        {l.verified ? '• Verified' : '• Progressive'}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            <div className="p-5 md:p-6 space-y-4 bg-gradient-to-b from-blue-50/30 to-white">
              {/* Photo Upload & Image Indicator */}
              <div className="flex flex-wrap items-center gap-2.5">
                <label className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-200 bg-white hover:bg-blue-50 hover:border-blue-300 text-xs font-extrabold text-slate-700 cursor-pointer shadow-sm transition-all">
                  <Upload className="w-4 h-4 text-blue-600" />
                  <span>Upload Homework Photo / Image</span>
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={handleImageUpload}
                  />
                </label>

                {uploadedImageName && (
                  <span className="text-xs font-extrabold text-emerald-800 bg-emerald-50 border border-emerald-200 px-3.5 py-1.5 rounded-full shadow-sm">
                    ✓ Image Ready for Vision Agent: {uploadedImageName}
                  </span>
                )}
              </div>

              {/* Question Input & Trigger Button */}
              <div className="flex flex-col sm:flex-row gap-3">
                <input
                  type="text"
                  value={questionInput}
                  onChange={(e) => setQuestionInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') startTutorSession();
                  }}
                  className="flex-1 rounded-2xl border border-slate-300 bg-white px-4 py-3.5 text-sm font-semibold text-slate-900 shadow-inner focus:outline-none focus:ring-2 focus:ring-blue-600"
                  placeholder="Type any question or concept (e.g. Solve 1/4 + 1/6, Explain Photosynthesis, Pythagorean Theorem, Indus Valley Civilization)..."
                />
                <button
                  type="button"
                  disabled={isLoading || (!questionInput.trim() && !uploadedImageBase64)}
                  onClick={() => startTutorSession()}
                  className="inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-2xl bg-gradient-to-r from-[#2563EB] via-[#4F46E5] to-[#7C3AED] hover:opacity-95 text-white text-xs font-extrabold shadow-lg shadow-blue-600/25 shrink-0 disabled:opacity-50 transition-all"
                >
                  <Send className="w-4 h-4" />
                  <span>{isLoading ? 'Running 4 Agents...' : 'Start Interactive Tutoring →'}</span>
                </button>
              </div>

              {apiError && (
                <div className="p-4 rounded-2xl bg-rose-50 border border-rose-300 text-xs text-rose-950 font-bold flex items-center justify-between gap-2 shadow-sm">
                  <span>⚠️ {apiError}</span>
                  <button
                    type="button"
                    onClick={() => startTutorSession()}
                    className="underline text-rose-800 hover:text-rose-900 font-extrabold"
                  >
                    Retry
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Unclear Question Clarification Banner */}
          {sessionState?.current_node === 'AWAITING_CLARIFICATION' &&
            sessionState.understanding_output && (
              <div className="bg-amber-50 border-2 border-amber-300 rounded-3xl p-5 text-xs space-y-2 shadow-sm">
                <div className="font-extrabold text-amber-950 text-sm">
                  🧭 Understanding Agent Needs Clarification:
                </div>
                <p className="text-amber-900 font-medium">
                  {sessionState.understanding_output.clarification_prompt}
                </p>
              </div>
            )}

          {/* Active Interactive Socratic Tutoring Session */}
          {sessionState && sessionState.teaching_output && (
            <div className="eduspark-card rounded-3xl p-6 md:p-8 space-y-6 border border-slate-200/90 shadow-sm animate-fade-in">
              {/* Agent Diagnosis & Curriculum Meta */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                <div className="p-4 rounded-2xl bg-gradient-to-br from-blue-50/80 to-white border border-blue-200/80 space-y-1.5 shadow-sm">
                  <div className="font-extrabold text-blue-900">
                    🧭 1. Understanding Agent Context
                  </div>
                  <div>
                    <strong>Question:</strong> {sessionState.extracted_question}
                  </div>
                  <div>
                    <strong>Detected Subject:</strong>{' '}
                    <span className="font-extrabold text-blue-700">
                      {sessionState.detected_subject}
                    </span>{' '}
                    • <strong>Topic:</strong> {sessionState.detected_topic}
                  </div>
                  <div className="text-slate-600">
                    <strong>Curriculum Context:</strong> Grade {sessionState.grade} ({sessionState.school_board})
                  </div>
                </div>

                {sessionState.diagnosis_output && (
                  <div className="p-4 rounded-2xl bg-gradient-to-br from-violet-50/80 to-white border border-violet-200/80 space-y-1.5 shadow-sm">
                    <div className="font-extrabold text-violet-900">
                      🧠 2. Learning Diagnosis Agent
                    </div>
                    <div>
                      <strong>Prerequisites:</strong>{' '}
                      {sessionState.diagnosis_output.prerequisite_concepts.join(' • ')}
                    </div>
                    <div>
                      <strong>Pedagogical Route:</strong>{' '}
                      <span className="font-extrabold text-violet-700">
                        {sessionState.diagnosis_output.recommended_pedagogical_route}
                      </span>
                    </div>
                    <div className="text-slate-600">
                      <strong>Diagnostic Evidence:</strong>{' '}
                      {sessionState.diagnosis_output.verified_learning_evidence.length} record(s) checked.
                    </div>
                  </div>
                )}
              </div>

              {/* Teaching Agent Guided Explanation Bubble */}
              <div className="flex items-start gap-3.5">
                <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-[#2563EB] via-[#4F46E5] to-[#7C3AED] text-white flex items-center justify-center shadow-md shrink-0">
                  <BookOpen className="w-5 h-5" />
                </div>
                <div className="flex-1 space-y-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-xs font-extrabold uppercase tracking-wider text-indigo-700">
                      🎯 3. SparkMinds Teaching Agent ({sessionState.teaching_output.explanation_language}
                      {sessionState.teaching_output.bilingual_active
                        ? ` + ${sessionState.teaching_output.secondary_explanation_language}`
                        : ''})
                    </span>
                    {sessionState.teaching_output.answer_withheld_for_guided_learning && (
                      <span className="text-xs px-3 py-1 rounded-full bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-950 font-extrabold border border-blue-200">
                        Guided Step {sessionState.current_step_index} of {sessionState.total_steps} • Answer Withheld for Active Learning
                      </span>
                    )}
                  </div>

                  {sessionState.teaching_output.prerequisite_mini_lesson && (
                    <div className="p-4 rounded-2xl bg-amber-50 border border-amber-300 text-xs font-bold text-amber-950 shadow-sm">
                      🧱 {sessionState.teaching_output.prerequisite_mini_lesson}
                    </div>
                  )}

                  <div className="p-5 rounded-3xl rounded-tl-sm bg-gradient-to-br from-[#EFF6FF] via-white to-indigo-50/40 border border-blue-200 text-sm text-slate-900 font-medium space-y-3 shadow-sm">
                    <p className="leading-relaxed whitespace-pre-line">{sessionState.teaching_output.concept_explanation}</p>
                    <div className="p-3.5 rounded-2xl bg-white/90 border border-blue-100 text-xs text-blue-950 font-bold flex items-start gap-2">
                      <span className="text-base leading-none">💡</span>
                      <span>{sessionState.teaching_output.real_world_example}</span>
                    </div>
                  </div>

                  {sessionState.teaching_output.bilingual_secondary_explanation && (
                    <div className="p-4 rounded-2xl bg-violet-50/80 border border-violet-200 text-xs text-violet-950 font-semibold shadow-sm">
                      🌐 {sessionState.teaching_output.bilingual_secondary_explanation}
                    </div>
                  )}
                </div>
              </div>

              {/* Step Breakdown Cards */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="text-xs font-extrabold uppercase tracking-wider text-slate-700 flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-blue-600" />
                    <span>Every Single Step Instructed</span>
                  </div>
                  <span className="text-[11px] font-bold text-slate-500">
                    Step {sessionState.current_step_index} of {sessionState.total_steps}
                  </span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {sessionState.teaching_output.steps_breakdown.map((step) => {
                    const isCurrent = step.step_number === sessionState.current_step_index;
                    const isCompleted = step.step_number < sessionState.current_step_index;
                    return (
                      <div
                        key={step.step_number}
                        className={`p-4 rounded-2xl border flex flex-col justify-between transition-all ${
                          isCurrent
                            ? 'border-2 border-blue-600 bg-gradient-to-b from-blue-50/90 to-white shadow-md ring-2 ring-blue-500/20'
                            : isCompleted
                              ? 'border-emerald-300 bg-emerald-50/50'
                              : 'border-slate-200 bg-slate-50/50 opacity-75'
                        }`}
                      >
                        <div className="space-y-2.5">
                          <div className="flex items-center justify-between">
                            <span
                              className={`text-[11px] font-extrabold uppercase px-2 py-0.5 rounded-md ${
                                isCurrent
                                  ? 'bg-blue-600 text-white'
                                  : isCompleted
                                    ? 'bg-emerald-600 text-white'
                                    : 'bg-slate-200 text-slate-700'
                              }`}
                            >
                              Step {step.step_number} {isCompleted ? '✓ Completed' : isCurrent ? '• Active' : ''}
                            </span>
                          </div>
                          <div className="text-xs font-extrabold text-slate-900 leading-snug">{step.title}</div>

                          {/* Thorough Step Instruction */}
                          <p className="text-[11px] text-slate-600 leading-relaxed font-medium">{step.instruction}</p>

                          {/* Why This Step Matters */}
                          {step.why_this_step_matters && (
                            <div className="p-2.5 rounded-xl bg-amber-50/90 border border-amber-200/90 text-[11px] text-amber-950">
                              <span className="text-[10px] font-extrabold uppercase tracking-wider text-amber-900 block mb-0.5">
                                💡 Why this step matters:
                              </span>
                              <p className="font-medium leading-relaxed">{step.why_this_step_matters}</p>
                            </div>
                          )}

                          {/* Key Rule or Formula */}
                          {step.step_formula_or_rule && (
                            <div className="p-2.5 rounded-xl bg-cyan-50/80 border border-cyan-200/90 text-[11px] text-cyan-950 font-mono">
                              <span className="text-[10px] font-sans font-extrabold uppercase tracking-wider text-cyan-900 block mb-0.5">
                                📐 Rule / Formula:
                              </span>
                              <p className="font-semibold leading-relaxed">{step.step_formula_or_rule}</p>
                            </div>
                          )}
                        </div>

                        {/* Question for Student */}
                        <div className="mt-3 pt-2.5 border-t border-slate-200/80 text-[11px] font-bold text-blue-950 flex items-start gap-1.5">
                          <span className="shrink-0 text-blue-600">✍️</span>
                          <span>{step.question_for_student}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>



              {/* Curated Video Explanation Module */}
              {sessionState.teaching_output.video_explanation && (
                <div className="rounded-3xl p-5 md:p-6 bg-gradient-to-br from-[#0F172A] via-[#1E1B4B] to-[#0F172A] border-2 border-indigo-500/40 text-white shadow-xl space-y-4">
                  <div className="flex flex-wrap items-center justify-between gap-3 border-b border-indigo-500/20 pb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-2xl bg-rose-500/20 border border-rose-500/30 flex items-center justify-center text-rose-400 shadow-sm">
                        <Video className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] font-extrabold uppercase tracking-wider text-rose-400">
                            Curated Video Explanation
                          </span>
                          <span className="px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 text-[10px] font-bold border border-indigo-400/30">
                            {sessionState.teaching_output.video_explanation.platform}
                          </span>
                          <span className="px-2 py-0.5 rounded-full bg-white/10 text-slate-200 text-[10px] font-bold">
                            ⏱ {sessionState.teaching_output.video_explanation.duration}
                          </span>
                        </div>
                        <h4 className="text-sm md:text-base font-extrabold text-white mt-0.5">
                          {sessionState.teaching_output.video_explanation.title}
                        </h4>
                      </div>
                    </div>

                    {sessionState.teaching_output.video_explanation.youtube_embed_id && (
                      <a
                        href={`https://www.youtube.com/watch?v=${sessionState.teaching_output.video_explanation.youtube_embed_id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold shadow-md transition-all shrink-0"
                      >
                        <Play className="w-3.5 h-3.5 fill-current" />
                        <span>Watch on YouTube</span>
                        <ExternalLink className="w-3 h-3 ml-0.5" />
                      </a>
                    )}
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-center">
                    {/* Embedded Video Player */}
                    <div className="lg:col-span-7 rounded-2xl overflow-hidden bg-black/60 border border-indigo-500/20 aspect-video shadow-inner">
                      {sessionState.teaching_output.video_explanation.youtube_embed_id ? (
                        <iframe
                          title={sessionState.teaching_output.video_explanation.title}
                          src={`https://www.youtube-nocookie.com/embed/${sessionState.teaching_output.video_explanation.youtube_embed_id}?rel=0&modestbranding=1`}
                          className="w-full h-full border-0"
                          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                          allowFullScreen
                        />
                      ) : (
                        <div className="w-full h-full flex flex-col items-center justify-center p-6 text-center text-slate-400">
                          <Video className="w-10 h-10 text-indigo-400 mb-2" />
                          <p className="text-xs font-bold text-white">Video Module Ready</p>
                          <p className="text-[11px] text-slate-400 mt-1">
                            Search: "{sessionState.teaching_output.video_explanation.search_query}"
                          </p>
                        </div>
                      )}
                    </div>

                    {/* Key Takeaways Checklist */}
                    <div className="lg:col-span-5 space-y-3 bg-white/5 backdrop-blur p-4 rounded-2xl border border-white/10">
                      <div className="text-xs font-extrabold uppercase tracking-wider text-cyan-300 flex items-center gap-1.5">
                        <CheckCircle2 className="w-4 h-4 text-cyan-400" />
                        <span>Key Video Takeaways & Checkpoints</span>
                      </div>
                      <ul className="space-y-2 text-xs">
                        {sessionState.teaching_output.video_explanation.key_takeaways.map((takeaway, idx) => (
                          <li key={idx} className="flex items-start gap-2 text-slate-200">
                            <span className="w-5 h-5 rounded-full bg-indigo-500/30 text-indigo-300 font-bold flex items-center justify-center text-[10px] shrink-0 mt-0.5">
                              {idx + 1}
                            </span>
                            <span className="font-medium leading-relaxed">{takeaway}</span>
                          </li>
                        ))}
                      </ul>
                      {sessionState.teaching_output.video_explanation.recommended_timestamp && (
                        <div className="pt-2 border-t border-white/10 text-[11px] text-amber-300 font-semibold flex items-center gap-1.5">
                          <span>⏱</span>
                          <span>Recommended start: {sessionState.teaching_output.video_explanation.recommended_timestamp}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Assessment Feedback from Agent 4 */}
              {sessionState.assessment_output && (
                <div
                  className={`p-5 rounded-3xl border-2 text-xs space-y-2 shadow-sm transition-all ${
                    sessionState.assessment_output.is_attempt_correct
                      ? 'border-emerald-400 bg-gradient-to-r from-emerald-50 to-teal-50/60 text-emerald-950'
                      : 'border-amber-400 bg-gradient-to-r from-amber-50 to-orange-50/60 text-amber-950'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="font-extrabold text-sm flex items-center gap-2">
                      {sessionState.assessment_output.is_attempt_correct ? (
                        <>
                          <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                          <span>4. Assessment Agent: Concept Check Verified ✓</span>
                        </>
                      ) : (
                        <>
                          <AlertTriangle className="w-5 h-5 text-amber-600" />
                          <span>4. Assessment Agent: Constructive Step Feedback</span>
                        </>
                      )}
                    </div>
                    {sessionState.assessment_output.mastery_evidence_score && (
                      <span className="px-3 py-1 rounded-full bg-white font-extrabold border border-emerald-300 text-emerald-700">
                        Mastery Score: {sessionState.assessment_output.mastery_evidence_score}%
                      </span>
                    )}
                  </div>
                  <p className="text-xs font-medium leading-relaxed">
                    {sessionState.assessment_output.encouraging_feedback}
                  </p>
                  {sessionState.assessment_output.follow_up_verification_question && (
                    <div className="p-3 rounded-xl bg-white/90 border border-emerald-200 font-bold text-emerald-900">
                      🎯 {sessionState.assessment_output.follow_up_verification_question}
                    </div>
                  )}
                </div>
              )}

              {/* Active Progressive Hint Card */}
              {sessionState.teaching_output.active_hint_shown && (
                <div className="p-4 rounded-2xl bg-amber-50 border-2 border-amber-300 text-xs font-bold text-amber-950 flex items-start gap-2.5 shadow-sm">
                  <Lightbulb className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                  <div>
                    <div className="font-extrabold text-amber-900 mb-0.5">
                      💡 Active Progressive Hint (Level {sessionState.hint_level}/3):
                    </div>
                    <div>{sessionState.teaching_output.active_hint_shown}</div>
                  </div>
                </div>
              )}

              {/* Alternative Visual Explanation Card */}
              {sessionState.teaching_output.alternative_explanation && (
                <div className="p-5 rounded-2xl bg-gradient-to-r from-violet-50 to-purple-50 border-2 border-violet-300 text-xs font-semibold text-violet-950 space-y-1.5 shadow-sm">
                  <div className="font-extrabold text-sm text-violet-900 flex items-center gap-2">
                    <RefreshCw className="w-4 h-4 text-violet-700" />
                    <span>Alternative Visual Teaching Strategy:</span>
                  </div>
                  <p className="leading-relaxed whitespace-pre-line">{sessionState.teaching_output.alternative_explanation}</p>
                </div>
              )}

              {/* Full Worked Solution Card */}
              {sessionState.teaching_output.full_worked_solution && (
                <div className="p-5 rounded-2xl bg-slate-900 text-cyan-200 text-xs font-mono whitespace-pre-line shadow-inner border border-slate-700">
                  <div className="font-extrabold text-white text-xs mb-2">Full Worked Solution:</div>
                  {sessionState.teaching_output.full_worked_solution}
                </div>
              )}

              {/* Similar Practice Question & Interactive Practice Arena */}
              {sessionState.teaching_output.similar_practice_question && (
                <div className="p-5 rounded-3xl bg-gradient-to-br from-emerald-50/70 via-white to-teal-50/70 border-2 border-emerald-300 shadow-sm space-y-3.5">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-emerald-200/80 pb-2.5">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-xl bg-emerald-600 text-white flex items-center justify-center shadow-sm">
                        <Repeat className="w-4 h-4" />
                      </div>
                      <div>
                        <h4 className="text-xs font-extrabold text-emerald-950 uppercase tracking-wider">
                          Interactive Practice Arena
                        </h4>
                        <p className="text-[11px] text-slate-500 font-medium">
                          Solidify your understanding by solving a similar problem independently.
                        </p>
                      </div>
                    </div>
                    <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-amber-500/15 text-amber-900 border border-amber-300 text-xs font-extrabold">
                      <Flame className="w-4 h-4 text-amber-500" />
                      <span>Streak: {sessionState.practice_streak || 0} Solved!</span>
                    </span>
                  </div>

                  <div className="p-3.5 rounded-2xl bg-white border border-emerald-200 text-xs text-slate-900 font-bold space-y-1">
                    <span className="text-[10px] uppercase font-extrabold text-emerald-700">Practice Problem:</span>
                    <p className="text-xs font-semibold">{sessionState.teaching_output.similar_practice_question.question}</p>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-2">
                    <input
                      type="text"
                      value={practiceAttemptInput}
                      onChange={(e) => setPracticeAttemptInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && practiceAttemptInput.trim()) {
                          submitStudentTurn('SUBMIT_PRACTICE_ATTEMPT');
                        }
                      }}
                      placeholder="Type your practice solution / answer here..."
                      className="flex-1 rounded-xl border border-emerald-300 bg-white px-3.5 py-2.5 text-xs font-medium text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    />
                    <button
                      type="button"
                      disabled={isLoading || !practiceAttemptInput.trim()}
                      onClick={() => submitStudentTurn('SUBMIT_PRACTICE_ATTEMPT')}
                      className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:opacity-95 text-white font-extrabold text-xs shadow-md shadow-emerald-500/20 disabled:opacity-50 transition shrink-0"
                    >
                      Check Practice Answer →
                    </button>
                  </div>
                </div>
              )}

              {/* Follow-Up Questions & Socratic Guidance */}
              <div className="p-5 rounded-3xl bg-gradient-to-br from-indigo-50/60 via-white to-blue-50/60 border-2 border-indigo-200 shadow-sm space-y-3.5">
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-indigo-100 pb-2.5">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center shadow-sm">
                      <MessageSquare className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-xs font-extrabold text-indigo-950 uppercase tracking-wider">
                        Ask Follow-Up Questions (Step {sessionState.current_step_index})
                      </h4>
                      <p className="text-[11px] text-slate-500 font-medium">
                        Have a doubt about this step? Ask the Teaching Agent in your language.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Stream of Previous Follow-Up Questions & Answers */}
                {sessionState.followup_qa_history && sessionState.followup_qa_history.length > 0 && (
                  <div className="space-y-2.5 max-h-60 overflow-y-auto pr-1">
                    {sessionState.followup_qa_history.map((qa, idx) => (
                      <div key={idx} className="p-3.5 rounded-2xl bg-white border border-indigo-100 text-xs space-y-1.5 shadow-sm">
                        <div className="flex items-center justify-between text-[10px] text-slate-500 font-bold">
                          <span className="text-indigo-700 font-extrabold">Q: {qa.question}</span>
                          <span className="px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700">Step {qa.step}</span>
                        </div>
                        <div className="text-slate-800 font-medium leading-relaxed bg-indigo-50/40 p-2.5 rounded-xl border border-indigo-100/60">
                          🎯 <strong>Teaching Agent:</strong> {qa.answer}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Quick Follow-Up Chips */}
                <div className="flex flex-wrap gap-1.5 text-[11px]">
                  {[
                    '💬 Can you explain this step more simply?',
                    '💡 Why does this rule or formula apply here?',
                    '🔍 Give another real-world Indian example',
                    '⚠️ What common mistake should I avoid?',
                  ].map((chip) => (
                    <button
                      key={chip}
                      type="button"
                      onClick={() => {
                        setFollowupInput(chip);
                        submitStudentTurn('ASK_FOLLOWUP_QUESTION', chip);
                      }}
                      className="px-2.5 py-1 rounded-lg bg-white hover:bg-indigo-50 text-slate-700 hover:text-indigo-900 border border-slate-200 font-semibold transition shadow-2xs"
                    >
                      {chip}
                    </button>
                  ))}
                </div>

                {/* Custom Follow-Up Input & Send */}
                <div className="flex flex-col sm:flex-row gap-2 pt-1">
                  <input
                    type="text"
                    value={followupInput}
                    onChange={(e) => setFollowupInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && followupInput.trim()) {
                        submitStudentTurn('ASK_FOLLOWUP_QUESTION');
                      }
                    }}
                    placeholder="Type any follow-up question about this step..."
                    className="flex-1 rounded-xl border border-indigo-200 bg-white px-3.5 py-2.5 text-xs font-medium text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                  <button
                    type="button"
                    disabled={isLoading || !followupInput.trim()}
                    onClick={() => submitStudentTurn('ASK_FOLLOWUP_QUESTION')}
                    className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-extrabold text-xs shadow-sm transition disabled:opacity-50 shrink-0"
                  >
                    Ask Follow-Up →
                  </button>
                </div>
              </div>

              {/* Interactive Step Attempt Reply Composer */}
              <div className="p-5 rounded-3xl bg-gradient-to-br from-slate-50 via-blue-50/40 to-indigo-50/40 border-2 border-blue-300/80 space-y-4 shadow-sm">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="font-extrabold text-sm text-slate-900">
                    ✍️ {sessionState.teaching_output.prompt_for_student_attempt}
                  </div>
                  <span className="text-xs font-extrabold px-3 py-1 rounded-full bg-white border border-slate-200 text-slate-600">
                    Attempts: {sessionState.student_attempts_history.length} • Mistakes: {sessionState.mistake_count}
                  </span>
                </div>

                <div className="flex flex-col sm:flex-row gap-2.5">
                  <input
                    type="text"
                    value={studentAttemptInput}
                    onChange={(e) => setStudentAttemptInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') submitStudentTurn('SUBMIT_STEP_ATTEMPT');
                    }}
                    placeholder="Type your step answer or reasoning here..."
                    className="flex-1 rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm font-semibold shadow-inner focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                  <button
                    type="button"
                    disabled={isLoading || !studentAttemptInput.trim()}
                    onClick={() => submitStudentTurn('SUBMIT_STEP_ATTEMPT')}
                    className="px-6 py-3 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:opacity-95 text-white text-xs font-extrabold shadow-md shadow-emerald-500/20 disabled:opacity-50 transition-all"
                  >
                    Submit My Step Attempt →
                  </button>
                </div>

                {/* Quick Socratic Support Action Controls */}
                <div className="flex flex-wrap gap-2 pt-1">
                  <button
                    type="button"
                    onClick={() => submitStudentTurn('REQUEST_PROGRESSIVE_HINT')}
                    className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-amber-100/90 hover:bg-amber-200 border border-amber-300/80 text-amber-950 text-xs font-extrabold transition-all shadow-sm"
                  >
                    <Lightbulb className="w-3.5 h-3.5 text-amber-700" />
                    <span>
                      Progressive Hint ({Math.min(3, sessionState.hint_level + 1)}/3)
                    </span>
                  </button>

                  <button
                    type="button"
                    onClick={() => submitStudentTurn('REQUEST_ALTERNATIVE_EXPLANATION')}
                    className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-violet-100/90 hover:bg-violet-200 border border-violet-300/80 text-violet-950 text-xs font-extrabold transition-all shadow-sm"
                  >
                    <RefreshCw className="w-3.5 h-3.5 text-violet-700" />
                    <span>Explain Differently (Visual Strategy)</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => submitStudentTurn('REQUEST_SIMILAR_PRACTICE')}
                    className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-blue-100/90 hover:bg-blue-200 border border-blue-300/80 text-blue-950 text-xs font-extrabold transition-all shadow-sm"
                  >
                    <HelpCircle className="w-3.5 h-3.5 text-blue-700" />
                    <span>Generate Similar Practice Question</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => submitStudentTurn('REQUEST_FULL_SOLUTION')}
                    className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-200/90 hover:bg-slate-300 border border-slate-300 text-slate-800 text-xs font-extrabold transition-all shadow-sm"
                  >
                    <Eye className="w-3.5 h-3.5 text-slate-700" />
                    <span>Reveal Full Worked Solution</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
// ============================================================================
// MY ACADEMIC JOURNEY & HISTORICAL COMPARISON (SCREENS 13 & 14)
// ============================================================================

interface AcademicJourneyViewProps {
  academicYears: HistoricalYearRecord[];
  currentGrade: number;
  onSelectScreen: (s: ScreenId) => void;
}

export const AcademicJourneyView: React.FC<AcademicJourneyViewProps> = ({
  academicYears,
  currentGrade,
  onSelectScreen,
}) => {
  const [selectedYearGrade, setSelectedYearGrade] = React.useState<number>(
    currentGrade
  );

  const selectedYear =
    academicYears.find((y) => y.grade === selectedYearGrade) ||
    academicYears[academicYears.length - 1];

  return (
    <div className="space-y-6">
      <div className="eduspark-card rounded-3xl p-6 space-y-4 animate-fade-in">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <span className="text-xs font-extrabold uppercase tracking-wider text-blue-600">
              Signature Feature • Permanent Multi-Year Learning Memory
            </span>
            <h2 className="text-xl font-extrabold text-slate-900">
              My Academic Journey (Grade 1 → Grade 12 Timeline)
            </h2>
            <p className="text-xs text-slate-600">
              Every completed academic year is permanently preserved and locked against overwriting. Click any completed or active grade below:
            </p>
          </div>
          <button
            onClick={() => onSelectScreen('promotion')}
            className="px-4 py-2 rounded-xl bg-[#2563EB] text-white text-xs font-extrabold shadow-sm"
          >
            Open Annual Grade Progression →
          </button>
        </div>

        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-2.5 pt-2">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((g) => {
            const record = academicYears.find((y) => y.grade === g);
            const isSelected = selectedYear?.grade === g;
            return (
              <button
                key={g}
                type="button"
                disabled={!record}
                onClick={() => record && setSelectedYearGrade(g)}
                className={`p-3 rounded-2xl border text-left transition ${isSelected
                  ? 'border-2 border-[#2563EB] bg-blue-50 shadow-sm'
                  : record
                    ? 'border-emerald-300 bg-emerald-50/50 hover:border-blue-400'
                    : 'border-slate-200 bg-slate-50 opacity-50 cursor-not-allowed'
                  }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-extrabold text-xs text-slate-900">
                    Grade {g}
                  </span>
                  {record && (
                    <span className="text-xs font-bold text-emerald-700">
                      {record.isLockedHistorical ? '🔒 Saved' : '★ Active'}
                    </span>
                  )}
                </div>
                <div className="text-xs text-slate-600 mt-1">
                  {record
                    ? `${record.academicYearLabel} (${record.board})`
                    : 'Future / Not Recorded'}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {selectedYear && (
        <div className="eduspark-card rounded-3xl p-6 space-y-5 animate-fade-in">
          <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-100">
            <div>
              <span className="text-xs font-extrabold uppercase text-violet-700">
                Academic Year Profile: {selectedYear.academicYearId}
              </span>
              <h3 className="text-lg font-extrabold text-slate-900">
                Grade {selectedYear.grade} ({selectedYear.academicYearLabel}) •{' '}
                {selectedYear.board} Board
              </h3>
            </div>
            <span
              className={`px-3 py-1 rounded-full text-xs font-extrabold ${selectedYear.isLockedHistorical
                ? 'bg-emerald-100 text-emerald-900'
                : 'bg-blue-100 text-blue-900'
                }`}
            >
              {selectedYear.isLockedHistorical
                ? 'Immutable Historical Record (Locked)'
                : 'Current Active Academic Year'}
            </span>
          </div>

          <div>
            <h4 className="text-xs font-extrabold uppercase tracking-wider text-slate-700 mb-2">
              Evidence-Based Performance & Learning Milestones
            </h4>
            <div className="space-y-2.5">
              {selectedYear.evidenceRecords.map((ev) => (
                <div
                  key={ev.id}
                  className="p-4 rounded-2xl border border-slate-200 flex flex-wrap items-center justify-between gap-3"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-extrabold text-sm text-slate-900">
                        {ev.subject}: {ev.topic}
                      </span>
                      <span className="text-xs px-2 py-0.5 rounded-md font-bold bg-slate-100 text-slate-700">
                        Source: {ev.evidenceType}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 mt-1">{ev.notes}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    {ev.scorePercentage !== null ? (
                      <span className="text-sm font-extrabold text-slate-900">
                        {ev.scorePercentage}%
                      </span>
                    ) : (
                      <span className="text-xs font-bold text-amber-800">
                        Self-Report: "{ev.qualitativeRating}"
                      </span>
                    )}
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-extrabold ${ev.trendIndicator === 'Improvement' ||
                        ev.trendIndicator === 'Learning gap resolved'
                        ? 'bg-emerald-100 text-emerald-800'
                        : ev.trendIndicator === 'Decline'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-amber-100 text-amber-900'
                        }`}
                    >
                      {ev.trendIndicator}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4 text-xs">
            <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200">
              <div className="font-extrabold text-emerald-900 mb-1 flex items-center gap-1.5">
                <TrendingUp className="w-4 h-4" /> Resolved Learning Gaps
              </div>
              <ul className="list-disc list-inside text-emerald-800 space-y-1">
                {selectedYear.resolvedGaps.length > 0 ? (
                  selectedYear.resolvedGaps.map((g, i) => <li key={i}>{g}</li>)
                ) : (
                  <li>Diagnostic verification in progress</li>
                )}
              </ul>
            </div>
            <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200">
              <div className="font-extrabold text-amber-900 mb-1 flex items-center gap-1.5">
                <TrendingDown className="w-4 h-4" /> Unresolved / Focus Topics
              </div>
              <ul className="list-disc list-inside text-amber-800 space-y-1">
                {selectedYear.unresolvedGaps.length > 0 ? (
                  selectedYear.unresolvedGaps.map((g, i) => <li key={i}>{g}</li>)
                ) : (
                  <li>No unresolved gaps flagged for this year</li>
                )}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// ============================================================================
// ANNUAL ACADEMIC PROGRESSION WORKFLOW (SCREEN 15)
// ============================================================================

interface AnnualPromotionViewProps {
  onboarding: OnboardingState;
  academicYears: HistoricalYearRecord[];
  onPromoteStudent: (
    decision: 'Yes' | 'No' | 'I am repeating my current grade' | 'I am changing schools',
    boardUnchanged: 'Yes, same board' | 'No, I have changed my board',
    sameSchool: 'Yes' | 'No',
    newBoard: 'CBSE' | 'ICSE' | 'STATE' | 'OTHER'
  ) => void;
}

export const AnnualPromotionView: React.FC<AnnualPromotionViewProps> = ({
  onboarding,
  academicYears,
  onPromoteStudent,
}) => {
  const [decision, setDecision] = React.useState<
    'Yes' | 'No' | 'I am repeating my current grade' | 'I am changing schools'
  >('Yes');
  const [boardUnchanged, setBoardUnchanged] = React.useState<
    'Yes, same board' | 'No, I have changed my board'
  >('Yes, same board');
  const [sameSchool, setSameSchool] = React.useState<'Yes' | 'No'>('Yes');
  const [newBoard, setNewBoard] = React.useState<'CBSE' | 'ICSE' | 'STATE' | 'OTHER'>(
    onboarding.board
  );
  const [promotedBanner, setPromotedBanner] = React.useState<string>('');

  const handleConfirmProgression = () => {
    onPromoteStudent(decision, boardUnchanged, sameSchool, newBoard);
    const targetGrade =
      decision === 'Yes' ? Math.min(12, onboarding.grade + 1) : onboarding.grade;
    setPromotedBanner(
      onboarding.grade >= 12 && decision === 'Yes'
        ? 'Congratulations! Grade 12 Schooling Completed. All Grade 1–12 records remain permanently preserved.'
        : `Success! Created new Academic-Year Profile for Grade ${targetGrade} while locking and preserving all ${academicYears.length} previous academic year(s).`
    );
  };

  return (
    <div className="eduspark-card rounded-3xl p-6 space-y-6 animate-fade-in">
      <div>
        <span className="text-xs font-extrabold uppercase tracking-wider text-blue-600">
          Academic Year Progression • Permanent History Protection
        </span>
        <h2 className="text-xl font-extrabold text-slate-900 mt-0.5">
          Start New Academic Year (Current: Grade {onboarding.grade})
        </h2>
        <p className="text-xs text-slate-600">
          SparkMinds AI never promotes students automatically without confirmation and never creates Grade 13. Previous academic years remain permanently preserved.
        </p>
      </div>

      {promotedBanner && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-300 text-xs font-extrabold text-emerald-900">
          ✓ {promotedBanner}
        </div>
      )}

      <div>
        <label className="block text-sm font-extrabold text-slate-900 mb-2">
          1. Have you been promoted to the next grade?
        </label>
        <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-2.5">
          {(
            [
              'Yes',
              'No',
              'I am repeating my current grade',
              'I am changing schools',
            ] as const
          ).map((opt) => (
            <button
              key={opt}
              type="button"
              onClick={() => setDecision(opt)}
              className={`p-3.5 rounded-2xl border text-left text-xs font-bold ${decision === opt
                ? 'border-2 border-[#2563EB] bg-blue-50 text-[#2563EB]'
                : 'border-slate-200'
                }`}
            >
              {opt}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-extrabold text-slate-900 mb-2">
          2. Is your school board unchanged?
        </label>
        <div className="grid sm:grid-cols-2 gap-2.5">
          {(['Yes, same board', 'No, I have changed my board'] as const).map(
            (opt) => (
              <button
                key={opt}
                type="button"
                onClick={() => setBoardUnchanged(opt)}
                className={`p-3.5 rounded-2xl border text-left text-xs font-bold ${boardUnchanged === opt
                  ? 'border-2 border-[#2563EB] bg-blue-50 text-[#2563EB]'
                  : 'border-slate-200'
                  }`}
              >
                {opt}
              </button>
            )
          )}
        </div>

        {boardUnchanged === 'No, I have changed my board' && (
          <div className="mt-3 flex gap-2">
            {(['CBSE', 'ICSE', 'STATE', 'OTHER'] as const).map((b) => (
              <button
                key={b}
                type="button"
                onClick={() => setNewBoard(b)}
                className={`px-3.5 py-2 rounded-xl border text-xs font-bold ${newBoard === b
                  ? 'border-2 border-[#2563EB] bg-blue-50 text-[#2563EB]'
                  : 'border-slate-200'
                  }`}
              >
                New Board: {b}
              </button>
            ))}
          </div>
        )}
      </div>

      <div>
        <label className="block text-sm font-extrabold text-slate-900 mb-2">
          3. Are you studying at the same school?
        </label>
        <div className="grid grid-cols-2 gap-2.5 max-w-md">
          {(['Yes', 'No'] as const).map((opt) => (
            <button
              key={opt}
              type="button"
              onClick={() => setSameSchool(opt)}
              className={`p-3 rounded-2xl border text-xs font-bold ${sameSchool === opt
                ? 'border-2 border-[#2563EB] bg-blue-50 text-[#2563EB]'
                : 'border-slate-200'
                }`}
            >
              {opt}
            </button>
          ))}
        </div>
      </div>

      <button
        type="button"
        onClick={handleConfirmProgression}
        className="px-6 py-3 rounded-2xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-extrabold shadow-md"
      >
        Confirm & Create New Academic-Year Profile (Preserve All {academicYears.length} Past Years)
      </button>
    </div>
  );
};

// ============================================================================
// PARENT DASHBOARD & SECURITY PORTAL (SCREEN 16)
// ============================================================================

interface ParentDashboardViewProps {
  onboarding: OnboardingState;
  academicYears: HistoricalYearRecord[];
}

export const ParentDashboardView: React.FC<ParentDashboardViewProps> = ({
  onboarding,
  academicYears,
}) => {
  const [parentLang, setParentLang] = React.useState<string>('Telugu');
  const [securityNotice, setSecurityNotice] = React.useState<string>('');
  const [parentData, setParentData] = React.useState<{
    parent_recommendations?: string[];
    homeworks?: {
      title: string;
      subject: string;
      status: string;
      due_date: string;
      priority?: string;
    }[];
    study_plan?: {
      exam_name: string;
      exam_date: string;
      preferred_study_time: string;
      daily_timetable: {
        task_id: string;
        time_slot: string;
        subject: string;
        chapter: string;
        session_type: string;
        duration_minutes: number;
      }[];
      mock_exam_dates: string[];
      exam_subjects?: {
        subject_name: string;
        number_of_chapters: number;
        exam_date: string;
        exam_time?: string | null;
      }[];
    };
    exam_marks?: {
      mark_id: string;
      subject: string;
      exam_name: string;
      exam_type: string;
      exam_date: string;
      marks_obtained: number;
      maximum_marks: number;
      percentage: number;
      trend: string;
      verification_status: string;
    }[];
    reminder_preferences?: {
      custom_reminder_times: string[];
      android_notifications_permission: string;
      in_app_reminders_enabled: boolean;
      timezone_name: string;
    };
    child_safety_controls?: {
      under_8_assisted_mode: boolean;
      age_tier_safety_policy: string;
      parent_consent_verified: boolean;
      verified_parent_name?: string | null;
      verified_parent_relationship?: string | null;
      strict_privacy_guard_active: boolean;
    };
    live_progress_summary?: {
      homework_completion_rate: number;
      subject_wise_progress: { subject: string; overall_mastery_percentage: number }[];
    };
    daily_schedule?: {
      date_iso: string;
      weekday_name?: string;
      checkin_completed: boolean;
      available_study_hours: number;
      unavailable_slots_summary: string[];
      activities: {
        activity_name: string;
        category: string;
        start_time: string;
        end_time: string;
        location?: string;
        recurrence_type: string;
        is_cancelled_today?: boolean;
      }[];
      generated_daily_timeline: {
        task_id: string;
        time_slot: string;
        subject: string;
        chapter: string;
        session_type: string;
        duration_minutes: number;
      }[];
    };
  } | null>(null);

  const resolveParentId = (sid: string): string => {
    const map: Record<string, string> = {
      stu_aarav_g7: 'parent_sharma_01',
      stu_ananya_g1: 'parent_reddy_01',
      stu_diya_g4: 'parent_nair_01',
      stu_karthik_g10: 'parent_rajan_01',
      stu_riya_g12: 'parent_verma_01',
    };
    return map[sid] || `parent_${sid}`;
  };

  React.useEffect(() => {
    const parentId = resolveParentId(onboarding.studentId);
    fetch(`/api/parent/${parentId}/child/${onboarding.studentId}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (d) {
          setParentData(d);
          if (d.parent_preferred_language) {
            setParentLang(d.parent_preferred_language);
          }
        }
      })
      .catch(() => { });
  }, [onboarding.studentId]);

  const handleParentLanguageUpdate = async (newLang: string) => {
    setParentLang(newLang);
    const parentId = resolveParentId(onboarding.studentId);
    await fetch(
      `/api/parent/${parentId}/child/${onboarding.studentId}/action`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          parent_id: parentId,
          action: 'UPDATE_PARENT_LANGUAGE',
          preferred_parent_language: newLang,
        }),
      }
    ).catch(() => { });
  };

  const topSubjectProgress = parentData?.live_progress_summary?.subject_wise_progress?.[0];
  const hwRate = parentData?.live_progress_summary?.homework_completion_rate;
  const activeYearObj = academicYears.find((y) => y.status === 'ACTIVE');
  const activeGapsList = activeYearObj?.unresolvedGaps || [];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Clean Navy Parent Header */}
      <div className="rounded-3xl bg-[#101B35] text-white p-6 md:p-7 border border-slate-800 shadow-lg flex flex-wrap items-center justify-between gap-4">
        <div className="space-y-1">
          <span className="text-[11px] font-extrabold uppercase tracking-wider text-[#35D6E8]">
            Parent & Guardian Overview
          </span>
          <h2 className="text-xl md:text-2xl font-extrabold text-white">
            {onboarding.studentName || 'Student'} • Grade {onboarding.grade} ({onboarding.board})
          </h2>
          <p className="text-xs text-slate-300 font-medium">
            Read-only progress summary and child-safety controls in your preferred language.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="font-bold text-slate-300">Language:</span>
          <select
            value={parentLang}
            onChange={(e) => handleParentLanguageUpdate(e.target.value)}
            aria-label="Parent summary language"
            className="rounded-xl border border-white/20 bg-white/10 px-3 py-2 font-extrabold text-white focus:outline-none min-h-[40px]"
          >
            {ALL_23_INDIAN_LANGUAGES.map((l) => (
              <option key={l.code} value={l.name} className="text-slate-900">
                {l.name} ({l.nativeName})
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="eduspark-card rounded-3xl p-6 space-y-5">
        <div className="grid md:grid-cols-3 gap-4 text-xs">
          <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
            <div className="font-extrabold text-[#101B35] text-sm">
              Verified Progress
            </div>
            <p className="text-slate-600 leading-relaxed">
              {topSubjectProgress ? (
                <>
                  Top recorded subject: <strong className="text-[#101B35]">{topSubjectProgress.subject}</strong> at{' '}
                  <strong className="text-[#101B35]">{topSubjectProgress.overall_mastery_percentage}%</strong>.
                </>
              ) : (
                'No completed assessments recorded yet.'
              )}{' '}
              {hwRate !== undefined && (
                <>
                  Homework completion: <strong className="text-[#101B35]">{hwRate}%</strong>.
                </>
              )}
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
            <div className="font-extrabold text-[#101B35] text-sm">
              Current Focus Areas
            </div>
            <p className="text-slate-600 leading-relaxed">
              {activeGapsList.length > 0
                ? `Active topics needing attention: ${activeGapsList.slice(0, 2).join(', ')}.`
                : 'No unresolved learning gaps flagged yet.'}{' '}
              Explanations set to <strong className="text-[#101B35]">{onboarding.preferredExplanationLanguage}</strong>.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2.5">
            <div className="font-extrabold text-[#101B35] text-sm flex items-center gap-1.5">
              <Shield className="w-4 h-4 text-[#5146E5]" />
              <span>Record Integrity</span>
            </div>
            <p className="text-slate-600 leading-relaxed">
              Verified test scores are read-only and cannot be silently overwritten.
            </p>
            <button
              type="button"
              onClick={() =>
                setSecurityNotice(
                  'Verified assessment results are protected and cannot be overwritten by students or parents.'
                )
              }
              className="px-3.5 py-2 rounded-xl bg-[#101B35] hover:bg-[#1B2654] text-[#35D6E8] font-extrabold transition"
            >
              Verify Protection
            </button>
          </div>
        </div>

        {parentData?.study_plan && (
          <div className="grid md:grid-cols-2 gap-4 text-xs">
            <div className="p-4 rounded-2xl bg-blue-50/60 border border-blue-200 space-y-2.5">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="font-extrabold text-blue-950">
                  📅 Child&apos;s Combined Study & Personal Schedule (12-Hour Format)
                </span>
                <span className="px-2.5 py-0.5 rounded-full bg-white border border-blue-200 font-bold text-blue-800">
                  {parentData.daily_schedule?.available_study_hours ?? 4.5} hrs Free •{' '}
                  {formatTime12Hour(parentData.study_plan.preferred_study_time)}
                </span>
              </div>
              {parentData.daily_schedule?.unavailable_slots_summary &&
                parentData.daily_schedule.unavailable_slots_summary.length > 0 && (
                  <div className="p-2 rounded-xl bg-[#101B35] text-white text-[11px] font-bold">
                    <span className="text-[#35D6E8] font-extrabold">
                      Personal Classes & Unavailable Slots Today:{' '}
                    </span>
                    {parentData.daily_schedule.unavailable_slots_summary.join(' • ')}
                  </div>
                )}
              <div className="space-y-1.5">
                {(parentData.daily_schedule?.generated_daily_timeline &&
                parentData.daily_schedule.generated_daily_timeline.length > 0
                  ? parentData.daily_schedule.generated_daily_timeline
                  : parentData.study_plan.daily_timetable
                ).map((slot) => (
                  <div
                    key={slot.task_id}
                    className={`p-2.5 rounded-xl border flex flex-wrap items-center justify-between gap-2 ${
                      slot.session_type === 'Unavailable'
                        ? 'bg-slate-900 text-white border-slate-700'
                        : 'bg-white border-blue-100'
                    }`}
                  >
                    <div>
                      <span
                        className={`font-extrabold ${
                          slot.session_type === 'Unavailable'
                            ? 'text-[#35D6E8]'
                            : 'text-blue-700'
                        }`}
                      >
                        {formatTimeRange12Hour(slot.time_slot)}
                      </span>{' '}
                      <span
                        className={`font-bold ${
                          slot.session_type === 'Unavailable'
                            ? 'text-white'
                            : 'text-slate-900'
                        }`}
                      >
                        • {slot.subject}: {slot.chapter}
                      </span>
                    </div>
                    <span
                      className={`text-[11px] font-bold px-2 py-0.5 rounded-md ${
                        slot.session_type === 'Unavailable'
                          ? 'bg-[#35D6E8]/20 text-[#35D6E8]'
                          : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {slot.session_type} ({slot.duration_minutes}m)
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-amber-50/60 border border-amber-200 space-y-2.5">
              <div className="font-extrabold text-amber-950">
                📝 Homework Deadlines, Reminders & Upcoming Exam Schedule
              </div>
              <div className="space-y-1.5">
                {(parentData.homeworks || []).slice(0, 3).map((hw, idx) => {
                  const hwTime = formatHomeworkDeadline12Hour(
                    hw.due_date,
                    hw.priority || 'High'
                  );
                  return (
                    <div
                      key={idx}
                      className="p-2.5 rounded-xl bg-white border border-amber-100 flex flex-wrap items-center justify-between gap-2"
                    >
                      <span className="font-bold text-slate-900">
                        {hw.subject}: {hw.title}
                      </span>
                      <span className="text-[11px] font-extrabold text-amber-900">
                        Due {hwTime.dueDisplay} (Reminder {hwTime.reminderDisplay})
                      </span>
                    </div>
                  );
                })}
                {parentData.study_plan.mock_exam_dates.map((dt, idx) => (
                  <div
                    key={idx}
                    className="p-2.5 rounded-xl bg-violet-50 border border-violet-200 flex flex-wrap items-center justify-between gap-2 font-bold text-violet-950"
                  >
                    <span>Scheduled Mock Test #{idx + 1}</span>
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
        )}

        {parentData?.parent_recommendations && (
          <div className="p-4 rounded-2xl bg-violet-50 border border-violet-200 space-y-1.5 text-xs">
            <div className="font-extrabold text-violet-950">
              💡 AI Recommendations for Parents ({parentLang} Summary Active)
            </div>
            <ul className="list-disc list-inside text-violet-900 space-y-1 font-medium">
              {parentData.parent_recommendations.map((rec, i) => (
                <li key={i}>{formatTime12Hour(rec)}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Exam Marks Entered by Student, Reminder Settings & Child-Safety Controls (Requirement 8) */}
        <div className="grid md:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-2xl bg-indigo-50/70 border border-indigo-200 space-y-2.5">
            <div className="font-extrabold text-indigo-950">
              🏆 Exam Marks Entered by Student & Individual Upcoming Exams
            </div>
            {parentData?.study_plan?.exam_subjects &&
              parentData.study_plan.exam_subjects.length > 0 && (
                <div className="space-y-1">
                  <div className="text-[11px] font-bold text-slate-600">
                    Individual Subject Exam Dates:
                  </div>
                  {parentData.study_plan.exam_subjects.map((es, idx) => (
                    <div
                      key={idx}
                      className="p-2 rounded-lg bg-white border border-indigo-100 flex justify-between font-bold"
                    >
                      <span>
                        {es.subject_name} ({es.number_of_chapters} ch)
                      </span>
                      <span className="text-indigo-800">
                        {es.exam_date} •{' '}
                        {formatTimeRange12Hour(es.exam_time || '9:30 AM - 12:30 PM')}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            {parentData?.exam_marks && parentData.exam_marks.length > 0 ? (
              <div className="space-y-1.5">
                {parentData.exam_marks.map((mk) => (
                  <div
                    key={mk.mark_id}
                    className="p-2.5 rounded-xl bg-white border border-indigo-100 flex flex-wrap items-center justify-between gap-2"
                  >
                    <div>
                      <span className="font-extrabold text-slate-900">
                        {mk.subject} ({mk.exam_name})
                      </span>
                      <span className="ml-2 text-slate-500">{mk.exam_date}</span>
                    </div>
                    <span className="font-extrabold text-indigo-800">
                      {mk.marks_obtained}/{mk.maximum_marks} ({mk.percentage}% •{' '}
                      {mk.trend} • {mk.verification_status})
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-slate-600 font-semibold">
                No post-exam marks entered yet for the current examination cycle.
              </div>
            )}
          </div>

          <div className="p-4 rounded-2xl bg-teal-50/70 border border-teal-200 space-y-2.5">
            <div className="font-extrabold text-teal-950">
              🛡️ Child-Safety, Privacy Controls & Reminder Settings
            </div>
            <div className="space-y-1.5 text-slate-700">
              <div className="p-2.5 rounded-xl bg-white border border-teal-100 flex justify-between">
                <span className="font-bold">Age-Tier Safety Policy:</span>
                <span className="font-extrabold text-teal-900">
                  {parentData?.child_safety_controls?.age_tier_safety_policy ||
                    'TIER_2_MIDDLE'}{' '}
                  (Consent Verified:{' '}
                  {parentData?.child_safety_controls?.parent_consent_verified
                    ? 'Yes ✓'
                    : 'Pending'}
                  )
                </span>
              </div>
              <div className="p-2.5 rounded-xl bg-white border border-teal-100 flex justify-between">
                <span className="font-bold">Under-8 Assisted Mode:</span>
                <span className="font-extrabold text-teal-900">
                  {parentData?.child_safety_controls?.under_8_assisted_mode
                    ? 'Active (Parent-Supervised)'
                    : 'Standard Age 8+ Student Mode'}
                </span>
              </div>
              <div className="p-2.5 rounded-xl bg-white border border-teal-100 flex justify-between">
                <span className="font-bold">Daily Reminder Schedule (12-Hr):</span>
                <span className="font-extrabold text-amber-900">
                  {(
                    parentData?.reminder_preferences?.custom_reminder_times || [
                      '6:00 PM',
                      '8:00 AM',
                    ]
                  )
                    .map((t) => formatTimeRange12Hour(t))
                    .join(', ')}{' '}
                  ({parentData?.reminder_preferences?.timezone_name || 'Asia/Kolkata'})
                </span>
              </div>
            </div>
          </div>
        </div>

        {securityNotice && (
          <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs font-bold text-red-900 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{securityNotice}</span>
          </div>
        )}
      </div>
    </div>
  );
};
