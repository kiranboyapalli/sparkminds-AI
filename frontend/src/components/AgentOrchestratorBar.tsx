import React from 'react';
import {
  Compass,
  Brain,
  GraduationCap,
  Award,
  CheckCircle2,
  AlertCircle,
  Clock,
  Sparkles,
} from 'lucide-react';

export interface BackendAgentExecutionLog {
  agent_name:
    | 'UnderstandingAgent'
    | 'LearningDiagnosisAgent'
    | 'TeachingAgent'
    | 'AssessmentAgent';
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'AWAITING_STUDENT' | 'FAILED';
  started_at: string;
  completed_at?: string | null;
  summary_for_ui: string;
  internal_reasoning_trace?: string | null;
  error_detail?: string | null;
}

export interface AgentStatusItem {
  id: 'understanding' | 'diagnosis' | 'teaching' | 'assessment';
  backendName: BackendAgentExecutionLog['agent_name'];
  name: string;
  role: string;
  status: 'COMPLETED' | 'RUNNING' | 'AWAITING_STUDENT' | 'PENDING' | 'FAILED';
  summary: string;
}

const BASE_FOUR_AGENTS: Omit<AgentStatusItem, 'status' | 'summary'>[] = [
  {
    id: 'understanding',
    backendName: 'UnderstandingAgent',
    name: '1. Understanding',
    role: 'Curriculum & Question Analysis',
  },
  {
    id: 'diagnosis',
    backendName: 'LearningDiagnosisAgent',
    name: '2. Diagnosis',
    role: 'Prerequisite & Gap Check',
  },
  {
    id: 'teaching',
    backendName: 'TeachingAgent',
    name: '3. Guided Teaching',
    role: 'Multilingual Socratic Guidance',
  },
  {
    id: 'assessment',
    backendName: 'AssessmentAgent',
    name: '4. Mastery Check',
    role: 'Step Verification & Feedback',
  },
];

interface AgentOrchestratorBarProps {
  executionLogs?: BackendAgentExecutionLog[];
  currentNode?: string;
  conditionalRouteTaken?: string;
  studentResponseRequired?: boolean;
  errorState?: string | null;
}

const NODE_DISPLAY_NAMES: Record<string, string> = {
  IDLE_READY: 'Ready for Your Question',
  AWAITING_STUDENT_STEP_ATTEMPT: 'Guided Step-by-Step Coaching Active',
  AWAITING_CLARIFICATION: 'Clarifying Question Details',
  SESSION_COMPLETED: 'Concept Mastery Verified',
};

/**
 * SparkMinds AI Multi-Agent Reasoning Engine Status Bar.
 * Reflects real-time backend agent state across the 4-stage Socratic tutoring pipeline.
 */
export const AgentOrchestratorBar: React.FC<AgentOrchestratorBarProps> = ({
  executionLogs = [],
  currentNode = 'IDLE_READY',
  conditionalRouteTaken,
  studentResponseRequired = false,
  errorState = null,
}) => {
  const agents: AgentStatusItem[] = BASE_FOUR_AGENTS.map((base) => {
    const matchingLogs = executionLogs.filter(
      (log) => log.agent_name === base.backendName
    );
    const latestLog =
      matchingLogs.length > 0 ? matchingLogs[matchingLogs.length - 1] : null;

    if (!latestLog) {
      return {
        ...base,
        status: 'PENDING',
        summary:
          'Ready to analyse your question, syllabus context, and preferred explanation language.',
      };
    }

    return {
      ...base,
      status: latestLog.status,
      summary: latestLog.error_detail
        ? `Issue: ${latestLog.error_detail}`
        : latestLog.summary_for_ui,
    };
  });

  const getIcon = (id: AgentStatusItem['id']) => {
    switch (id) {
      case 'understanding':
        return <Compass className="w-4 h-4" />;
      case 'diagnosis':
        return <Brain className="w-4 h-4" />;
      case 'teaching':
        return <GraduationCap className="w-4 h-4" />;
      case 'assessment':
        return <Award className="w-4 h-4" />;
    }
  };

  const getStatusBadge = (status: AgentStatusItem['status']) => {
    switch (status) {
      case 'COMPLETED':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-800 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
            <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Complete
          </span>
        );
      case 'RUNNING':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold text-cyan-950 bg-cyan-100 px-2.5 py-0.5 rounded-full border border-cyan-300 animate-pulse">
            <Sparkles className="w-3 h-3 text-cyan-700" /> Processing
          </span>
        );
      case 'AWAITING_STUDENT':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold text-amber-900 bg-amber-50 px-2.5 py-0.5 rounded-full border border-amber-300">
            <Clock className="w-3 h-3 text-amber-600" /> Your Turn
          </span>
        );
      case 'FAILED':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold text-red-800 bg-red-50 px-2.5 py-0.5 rounded-full border border-red-200">
            <AlertCircle className="w-3 h-3 text-red-600" /> Attention
          </span>
        );
      default:
        return (
          <span className="text-[11px] font-semibold text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded-full">
            Standby
          </span>
        );
    }
  };

  const readableStage =
    NODE_DISPLAY_NAMES[currentNode] ||
    currentNode.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());

  return (
    <div className="eduspark-card rounded-2xl p-4 md:p-5 relative overflow-hidden">
      <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-[#0A192F] via-[#1E3A8A] to-[#00E5FF]" />

      <div className="flex flex-wrap items-center justify-between gap-2 mb-3.5">
        <div className="flex items-center gap-2.5">
          <span className="inline-flex items-center justify-center w-6 h-6 rounded-lg bg-[#0A192F] text-[#00E5FF] shadow-sm">
            <Sparkles className="w-3.5 h-3.5" />
          </span>
          <div>
            <span className="text-xs font-extrabold uppercase tracking-wider text-slate-900">
              SparkMinds AI Reasoning Pipeline
            </span>
            <span className="hidden sm:inline text-xs text-slate-500 ml-2">
              • 4-Stage Socratic Learning Architecture
            </span>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="px-2.5 py-1 rounded-lg bg-slate-100 text-slate-800 font-bold border border-slate-200/80">
            Stage: {readableStage}
          </span>
          {conditionalRouteTaken && (
            <span className="px-2.5 py-1 rounded-lg bg-cyan-50 text-cyan-950 font-bold border border-cyan-200">
              Path: {conditionalRouteTaken.replace(/_/g, ' ')}
            </span>
          )}
          {studentResponseRequired && (
            <span className="px-2.5 py-1 rounded-lg bg-amber-50 text-amber-900 font-extrabold border border-amber-200">
              Awaiting Your Step Attempt
            </span>
          )}
        </div>
      </div>

      {errorState && (
        <div className="mb-3 p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-800 font-semibold">
          Connection Notice: {errorState}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className={`rounded-xl p-3.5 border transition-all duration-200 ${
              agent.status === 'RUNNING' || agent.status === 'AWAITING_STUDENT'
                ? 'border-[#0284C7] bg-gradient-to-br from-cyan-50/60 via-white to-blue-50/40 shadow-sm'
                : agent.status === 'COMPLETED'
                  ? 'border-emerald-200/90 bg-emerald-50/25'
                  : agent.status === 'FAILED'
                    ? 'border-red-300 bg-red-50/40'
                    : 'border-slate-200/90 bg-slate-50/50'
            }`}
          >
            <div className="flex items-center justify-between gap-1 mb-1.5">
              <div className="flex items-center gap-1.5 font-extrabold text-xs text-slate-900">
                <span className="p-1.5 rounded-lg bg-[#0A192F] text-[#00E5FF]">
                  {getIcon(agent.id)}
                </span>
                <span>{agent.name}</span>
              </div>
              {getStatusBadge(agent.status)}
            </div>
            <div className="text-[11px] font-semibold text-slate-500 mb-1">
              {agent.role}
            </div>
            <p className="text-xs text-slate-700 leading-snug">{agent.summary}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
