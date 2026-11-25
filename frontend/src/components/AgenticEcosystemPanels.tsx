import React from 'react';
import {
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  BookOpen,
  Upload,
  FileText,
  Trophy,
  Flame,
  Target,
  Brain,
  RefreshCw,
} from 'lucide-react';
import { ScreenId } from '../design-system/tokens';
import { RichMathMarkdown, cleanMathText } from '../utils/formatMathText';

// ============================================================================
// 1. INTELLIGENT ASSESSMENT & DIAGNOSTIC LAB (MCQ, Fill-in-Blank, T/F, Descriptive)
// ============================================================================

interface EcosystemQuestion {
  question_id: string;
  question_type: 'MCQ' | 'FILL_IN_BLANK' | 'TRUE_FALSE' | 'DESCRIPTIVE';
  topic: string;
  difficulty: string;
  prompt: string;
  options: string[];
  source_reference?: string | null;
}

interface EcosystemAssessment {
  assessment_id: string;
  assessment_kind: string;
  subject: string;
  difficulty: string;
  status: string;
  questions: EcosystemQuestion[];
}

export const IntelligentAssessmentLabPanel: React.FC<{
  studentId: string;
  defaultSubject?: string;
  onSelectScreen?: (s: ScreenId) => void;
}> = ({ studentId, defaultSubject = 'Mathematics', onSelectScreen }) => {
  const [subject, setSubject] = React.useState<string>(defaultSubject);
  const [topic, setTopic] = React.useState<string>('');
  const [kind, setKind] = React.useState<'DIAGNOSTIC' | 'QUIZ' | 'PRACTICE' | 'REVISION'>('DIAGNOSTIC');
  const [difficulty, setDifficulty] = React.useState<'Auto' | 'Easy' | 'Medium' | 'Hard'>('Auto');
  const [activeAssessment, setActiveAssessment] = React.useState<EcosystemAssessment | null>(null);
  const [answers, setAnswers] = React.useState<Record<string, string>>({});
  const [evaluation, setEvaluation] = React.useState<any>(null);
  const [loading, setLoading] = React.useState<boolean>(false);
  const [error, setError] = React.useState<string>('');

  const handleGenerate = async () => {
    setLoading(true);
    setError('');
    setEvaluation(null);
    setAnswers({});
    try {
      const res = await fetch('/api/agents/assessments/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: studentId,
          subject,
          assessment_kind: kind,
          topic: topic.trim() || null,
          difficulty: difficulty === 'Auto' ? null : difficulty,
          question_types: ['MCQ', 'FILL_IN_BLANK', 'TRUE_FALSE', 'DESCRIPTIVE'],
          question_count: 4,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || 'Could not generate assessment.');
        return;
      }
      setActiveAssessment(data);
    } catch {
      setError('Unable to reach the Assessment Agent right now.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!activeAssessment) return;
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`/api/agents/assessments/${activeAssessment.assessment_id}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_id: studentId, answers }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || 'Could not evaluate assessment.');
        return;
      }
      setEvaluation(data);
    } catch {
      setError('Unable to evaluate answers right now.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="eduspark-card rounded-3xl p-6 space-y-5 border border-[#C2D4F8] bg-gradient-to-br from-[#F7F9FF] via-white to-[#EEEAFE]/45">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#DFE5F6] pb-3.5">
        <div>
          <span className="inline-flex items-center gap-1.5 text-[11px] font-extrabold uppercase tracking-wider text-[#5146E5]">
            <Brain className="w-3.5 h-3.5" />
            <span>Diagnostic &amp; Intelligent Assessment Agent</span>
          </span>
          <h3 className="text-lg font-extrabold text-[#101B35] mt-0.5">
            Adaptive Diagnostic Checks &amp; Multi-Format Practice Quizzes
          </h3>
          <p className="text-xs text-[#202943]/75">
            Supports MCQ, Fill-in-the-Blank, True/False, and Rubric-Evaluated Descriptive questions. Results update your real Learning Gaps &amp; Study Plan automatically.
          </p>
        </div>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-3 text-xs">
        <div>
          <label className="block font-extrabold text-slate-700 mb-1">Mode</label>
          <select
            value={kind}
            onChange={(e) => setKind(e.target.value as any)}
            className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-bold"
          >
            <option value="DIAGNOSTIC">Diagnostic Check</option>
            <option value="QUIZ">Topic Quiz</option>
            <option value="PRACTICE">Practice Test</option>
            <option value="REVISION">Revision Check</option>
          </select>
        </div>
        <div>
          <label className="block font-extrabold text-slate-700 mb-1">Subject</label>
          <select
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-bold"
          >
            <option value="Mathematics">Mathematics</option>
            <option value="Science">Science</option>
            <option value="English">English</option>
            <option value="Social Studies">Social Studies</option>
          </select>
        </div>
        <div>
          <label className="block font-extrabold text-slate-700 mb-1">Topic Focus (Optional)</label>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="All core topics"
            className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-semibold"
          />
        </div>
        <div>
          <label className="block font-extrabold text-slate-700 mb-1">Difficulty</label>
          <select
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value as any)}
            className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 font-bold"
          >
            <option value="Auto">Adaptive (Auto)</option>
            <option value="Easy">Easy</option>
            <option value="Medium">Medium</option>
            <option value="Hard">Hard</option>
          </select>
        </div>
        <div className="flex items-end">
          <button
            type="button"
            disabled={loading}
            onClick={handleGenerate}
            className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-[#101B35] to-[#2563EB] text-white font-extrabold shadow-sm hover:opacity-95 disabled:opacity-50"
          >
            {loading ? 'Preparing...' : 'Start Assessment →'}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs font-bold text-rose-800">
          {error}
        </div>
      )}

      {activeAssessment && !evaluation && (
        <div className="space-y-4 pt-2">
          <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
            <span className="font-extrabold text-slate-900">
              {activeAssessment.subject} • {activeAssessment.assessment_kind} ({activeAssessment.difficulty})
            </span>
            <span className="px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-800 font-bold">
              {activeAssessment.questions.length} Questions
            </span>
          </div>

          {activeAssessment.questions.map((q, idx) => (
            <div key={q.question_id} className="p-4 rounded-2xl bg-white border border-[#DFE5F6] space-y-2.5 text-xs shadow-sm">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="font-extrabold text-[#101B35]">
                  Q{idx + 1}. {cleanMathText(q.prompt)}
                </span>
                <span className="px-2 py-0.5 rounded-md bg-[#EEEAFE] text-[#5146E5] font-bold text-[10px]">
                  {q.question_type} • {q.topic}
                </span>
              </div>

              {(q.question_type === 'MCQ' || q.question_type === 'TRUE_FALSE') && q.options.length > 0 ? (
                <div className="grid sm:grid-cols-2 gap-2">
                  {q.options.map((opt) => (
                    <button
                      key={opt}
                      type="button"
                      onClick={() => setAnswers((prev) => ({ ...prev, [q.question_id]: opt }))}
                      className={`p-2.5 rounded-xl border text-left font-bold transition ${answers[q.question_id] === opt
                        ? 'border-2 border-blue-600 bg-blue-50 text-blue-900'
                        : 'border-slate-200 hover:border-blue-300 bg-slate-50/50 text-slate-800'
                        }`}
                    >
                      {cleanMathText(opt)}
                    </button>
                  ))}
                </div>
              ) : q.question_type === 'FILL_IN_BLANK' ? (
                <input
                  type="text"
                  value={answers[q.question_id] || ''}
                  onChange={(e) => setAnswers((prev) => ({ ...prev, [q.question_id]: e.target.value }))}
                  placeholder="Type your exact answer..."
                  className="w-full rounded-xl border border-slate-300 px-3 py-2 font-semibold"
                />
              ) : (
                <textarea
                  rows={3}
                  value={answers[q.question_id] || ''}
                  onChange={(e) => setAnswers((prev) => ({ ...prev, [q.question_id]: e.target.value }))}
                  placeholder="Write your step-by-step explanation in your own words..."
                  className="w-full rounded-xl border border-slate-300 px-3 py-2 font-medium"
                />
              )}
            </div>
          ))}

          <button
            type="button"
            disabled={loading}
            onClick={handleSubmit}
            className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-extrabold shadow-md"
          >
            {loading ? 'Evaluating...' : 'Submit & Get Instant Feedback ✓'}
          </button>
        </div>
      )}

      {evaluation && (
        <div className="space-y-4 pt-2">
          <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="text-xs font-extrabold uppercase text-emerald-800">
                Assessment Evaluated &amp; Synced With Learning Gap Analyzer
              </div>
              <div className="text-xl font-extrabold text-slate-900 mt-0.5">
                Score: {evaluation.score_percentage}% • Next Recommended Level: {evaluation.next_recommended_difficulty}
              </div>
            </div>
            {onSelectScreen && (
              <button
                type="button"
                onClick={() => onSelectScreen('progress')}
                className="px-4 py-2 rounded-xl bg-[#101B35] text-[#35D6E8] text-xs font-extrabold"
              >
                View Learning Gaps &amp; Progress →
              </button>
            )}
          </div>

          <div className="space-y-2.5">
            {(evaluation.question_results || []).map((qr: any, i: number) => (
              <div
                key={qr.question_id || i}
                className={`p-3.5 rounded-2xl border text-xs space-y-1 ${qr.is_correct
                  ? 'bg-emerald-50/50 border-emerald-200'
                  : 'bg-amber-50/60 border-amber-200'
                  }`}
              >
                <div className="flex items-center justify-between font-extrabold">
                  <span className="text-slate-900">
                    Q{i + 1} ({qr.question_type}) — {qr.topic}
                  </span>
                  <span className={qr.is_correct ? 'text-emerald-700' : 'text-amber-800'}>
                    {Math.round((qr.score_fraction || 0) * 100)}%
                  </span>
                </div>
                <RichMathMarkdown text={qr.feedback} className="text-xs text-slate-700" />
                {qr.ai_uncertainty_notice && (
                  <p className="text-[11px] italic text-slate-500">{qr.ai_uncertainty_notice}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// ============================================================================
// 2. DOCUMENT STUDY & GROUNDED RAG LAB (PDF / TXT / MD)
// ============================================================================

export const DocumentStudyRAGPanel: React.FC<{ studentId: string }> = ({ studentId }) => {
  const [docs, setDocs] = React.useState<any[]>([]);
  const [selectedDocId, setSelectedDocId] = React.useState<string>('');
  const [subject, setSubject] = React.useState<string>('Science');
  const [question, setQuestion] = React.useState<string>('');
  const [answer, setAnswer] = React.useState<any>(null);
  const [docQuiz, setDocQuiz] = React.useState<any>(null);
  const [docQuizAnswers, setDocQuizAnswers] = React.useState<Record<string, string>>({});
  const [docQuizEval, setDocQuizEval] = React.useState<any>(null);
  const [statusMsg, setStatusMsg] = React.useState<string>('');
  const [errorMsg, setErrorMsg] = React.useState<string>('');
  const [busy, setBusy] = React.useState<boolean>(false);

  const loadDocs = React.useCallback(async () => {
    try {
      const res = await fetch(`/api/students/${studentId}/documents`);
      if (res.ok) {
        const data = await res.json();
        setDocs(data.documents || []);
      }
    } catch {
      // ignore offline
    }
  }, [studentId]);

  React.useEffect(() => {
    loadDocs();
  }, [loadDocs]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true);
    setErrorMsg('');
    setStatusMsg('');
    try {
      const form = new FormData();
      form.append('file', file);
      form.append('subject', subject);
      const res = await fetch(`/api/students/${studentId}/documents/upload-file`, {
        method: 'POST',
        body: form,
      });
      const data = await res.json();
      if (!res.ok) {
        setErrorMsg(data.detail || 'Unsupported or unreadable file.');
        return;
      }
      setStatusMsg(
        `Indexed "${data.document.filename}" (${data.document.page_count} page(s), ${data.document.chunk_count} searchable chunks).`
      );
      setSelectedDocId(data.document.doc_id);
      loadDocs();
    } catch {
      setErrorMsg('Failed to upload document.');
    } finally {
      setBusy(false);
      e.target.value = '';
    }
  };

  const handleAsk = async () => {
    if (!question.trim()) return;
    setBusy(true);
    setErrorMsg('');
    setAnswer(null);
    try {
      const res = await fetch(`/api/students/${studentId}/documents/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question.trim(),
          doc_id: selectedDocId || null,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setErrorMsg(data.detail || 'Could not query document.');
        return;
      }
      setAnswer(data);
    } catch {
      setErrorMsg('Unable to search documents right now.');
    } finally {
      setBusy(false);
    }
  };

  const handleGenerateDocQuiz = async (docId: string) => {
    setBusy(true);
    setErrorMsg('');
    setDocQuiz(null);
    setDocQuizAnswers({});
    setDocQuizEval(null);
    try {
      const res = await fetch(`/api/students/${studentId}/documents/${docId}/generate-quiz`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question_count: 4 }),
      });
      const data = await res.json();
      if (!res.ok) {
        setErrorMsg(data.detail || 'Could not create quiz from document.');
        return;
      }
      setDocQuiz(data);
    } catch {
      setErrorMsg('Failed to generate document quiz.');
    } finally {
      setBusy(false);
    }
  };

  const handleSubmitDocQuiz = async () => {
    if (!docQuiz?.assessment_id) return;
    setBusy(true);
    setErrorMsg('');
    try {
      const res = await fetch(`/api/agents/assessments/${docQuiz.assessment_id}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_id: studentId, answers: docQuizAnswers }),
      });
      const data = await res.json();
      if (!res.ok) {
        setErrorMsg(data.detail || 'Could not evaluate document quiz.');
        return;
      }
      setDocQuizEval(data);
    } catch {
      setErrorMsg('Unable to evaluate document quiz right now.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="eduspark-card rounded-3xl p-6 space-y-4 border-2 border-indigo-200/80">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-3">
        <div>
          <span className="inline-flex items-center gap-1.5 text-[11px] font-extrabold uppercase tracking-wider text-indigo-700">
            <BookOpen className="w-3.5 h-3.5" />
            <span>Document Learning &amp; Grounded RAG Studio</span>
          </span>
          <h3 className="text-lg font-extrabold text-slate-900 mt-0.5">
            Upload Study Notes (PDF, TXT, MD) &amp; Ask Grounded Questions
          </h3>
          <p className="text-xs text-slate-600">
            Answers strictly distinguish between content from your uploaded document and additional general AI explanation.
          </p>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3 text-xs">
        <select
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          className="rounded-xl border border-slate-300 bg-white px-3 py-2 font-bold"
        >
          <option value="Mathematics">Mathematics</option>
          <option value="Science">Science</option>
          <option value="English">English</option>
          <option value="Social Studies">Social Studies</option>
          <option value="General">General Notes</option>
        </select>

        <label className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-extrabold cursor-pointer shadow-sm">
          <Upload className="w-4 h-4" />
          <span>{busy ? 'Processing...' : 'Upload PDF / TXT / MD Notes'}</span>
          <input
            type="file"
            accept=".pdf,.txt,.md"
            onChange={handleFileUpload}
            className="hidden"
          />
        </label>
      </div>

      {statusMsg && (
        <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-800">
          ✓ {statusMsg}
        </div>
      )}
      {errorMsg && (
        <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs font-bold text-rose-800">
          {errorMsg}
        </div>
      )}

      {docs.length > 0 && (
        <div className="space-y-2">
          <div className="text-xs font-extrabold text-slate-700">
            Your Indexed Study Documents ({docs.length}):
          </div>
          <div className="grid sm:grid-cols-2 gap-2.5 text-xs">
            {docs.map((d) => (
              <div
                key={d.doc_id}
                className={`p-3 rounded-2xl border flex items-center justify-between gap-2 ${selectedDocId === d.doc_id
                  ? 'border-indigo-500 bg-indigo-50/70'
                  : 'border-slate-200 bg-slate-50/60'
                  }`}
              >
                <div
                  onClick={() => setSelectedDocId(d.doc_id === selectedDocId ? '' : d.doc_id)}
                  className="cursor-pointer min-w-0"
                >
                  <div className="font-extrabold text-slate-900 truncate flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-indigo-600 shrink-0" />
                    <span className="truncate">{d.filename}</span>
                  </div>
                  <div className="text-[11px] text-slate-500">
                    {d.subject} • {d.page_count} pg • {d.chunk_count} chunks
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => handleGenerateDocQuiz(d.doc_id)}
                  className="px-2.5 py-1.5 rounded-lg bg-white border border-indigo-200 text-indigo-700 font-extrabold text-[11px] hover:bg-indigo-50 shrink-0"
                >
                  Quiz Me
                </button>
              </div>
            ))}
          </div>

          <div className="flex flex-col sm:flex-row gap-2 pt-1">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAsk()}
              placeholder="Ask a question about your uploaded notes..."
              className="flex-1 rounded-xl border border-slate-300 px-3.5 py-2 text-xs font-semibold"
            />
            <button
              type="button"
              disabled={busy || !question.trim()}
              onClick={handleAsk}
              className="px-4 py-2 rounded-xl bg-[#101B35] text-[#35D6E8] text-xs font-extrabold disabled:opacity-50"
            >
              Ask Document →
            </button>
          </div>
        </div>
      )}

      {answer && (
        <div className="space-y-3 text-xs">
          <div className="p-4 rounded-2xl bg-emerald-50/70 border border-emerald-200 space-y-1.5">
            <div className="font-extrabold text-emerald-900">
              📄 From Your Uploaded Document
            </div>
            <RichMathMarkdown text={answer.document_grounded_answer} className="text-xs text-slate-800" />
            {answer.citations && answer.citations.length > 0 && (
              <div className="pt-1 flex flex-wrap gap-1.5">
                {answer.citations.map((c: any, idx: number) => (
                  <span
                    key={idx}
                    className="px-2 py-0.5 rounded-md bg-white border border-emerald-200 text-[10px] font-bold text-emerald-800"
                  >
                    {c.filename} • Page {c.page_number} (Chunk {c.chunk_index})
                  </span>
                ))}
              </div>
            )}
          </div>
          {answer.general_ai_explanation && (
            <div className="p-4 rounded-2xl bg-[#EAF0FF]/70 border border-[#C2D4F8] space-y-1">
              <div className="font-extrabold text-[#101B35]">
                ✨ Additional General AI Explanation
              </div>
              <RichMathMarkdown text={answer.general_ai_explanation} className="text-xs text-[#202943]" />
            </div>
          )}
        </div>
      )}

      {docQuiz && !docQuizEval && (
        <div className="p-4 rounded-2xl bg-indigo-50/60 border border-indigo-200 space-y-3 text-xs">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="font-extrabold text-indigo-950">
              Document Practice Quiz ({docQuiz.questions?.length || 0} Questions)
            </div>
            <span className="px-2 py-0.5 rounded-full bg-white border border-indigo-200 text-[10px] font-bold text-indigo-700">
              Grounded in Uploaded Notes
            </span>
          </div>
          {(docQuiz.questions || []).map((q: any, i: number) => (
            <div key={q.question_id || i} className="p-3 rounded-xl bg-white border border-indigo-100 space-y-2">
              <div className="font-extrabold text-slate-900">
                <span className="text-indigo-700 mr-1.5">Q{i + 1} [{q.question_type}]</span>
                {cleanMathText(q.prompt)}
              </div>
              {(q.question_type === 'MCQ' || q.question_type === 'TRUE_FALSE') && (q.options || []).length > 0 ? (
                <div className="grid sm:grid-cols-2 gap-1.5">
                  {q.options.map((opt: string) => (
                    <button
                      key={opt}
                      type="button"
                      onClick={() => setDocQuizAnswers((prev) => ({ ...prev, [q.question_id]: opt }))}
                      className={`p-2 rounded-lg border text-left font-bold transition ${docQuizAnswers[q.question_id] === opt
                        ? 'border-2 border-indigo-600 bg-indigo-50 text-indigo-950'
                        : 'border-slate-200 hover:border-indigo-300 bg-slate-50/60 text-slate-800'
                        }`}
                    >
                      {cleanMathText(opt)}
                    </button>
                  ))}
                </div>
              ) : q.question_type === 'FILL_IN_BLANK' ? (
                <input
                  type="text"
                  value={docQuizAnswers[q.question_id] || ''}
                  onChange={(e) => setDocQuizAnswers((prev) => ({ ...prev, [q.question_id]: e.target.value }))}
                  placeholder="Type your answer from the notes..."
                  className="w-full rounded-lg border border-slate-300 px-3 py-1.5 font-semibold"
                />
              ) : (
                <textarea
                  rows={2}
                  value={docQuizAnswers[q.question_id] || ''}
                  onChange={(e) => setDocQuizAnswers((prev) => ({ ...prev, [q.question_id]: e.target.value }))}
                  placeholder="Explain in your own words..."
                  className="w-full rounded-lg border border-slate-300 px-3 py-1.5 font-medium"
                />
              )}
            </div>
          ))}
          <button
            type="button"
            disabled={busy}
            onClick={handleSubmitDocQuiz}
            className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold shadow-sm disabled:opacity-50"
          >
            {busy ? 'Evaluating...' : 'Submit Document Quiz ✓'}
          </button>
        </div>
      )}

      {docQuizEval && (
        <div className="p-4 rounded-2xl bg-emerald-50/80 border border-emerald-200 space-y-2.5 text-xs">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="font-extrabold text-emerald-950">
              ✓ Document Quiz Score: {docQuizEval.score_percentage}% • Synced with Learning Gaps &amp; Progress
            </div>
            <button
              type="button"
              onClick={() => {
                setDocQuiz(null);
                setDocQuizEval(null);
                setDocQuizAnswers({});
              }}
              className="px-3 py-1 rounded-lg bg-white border border-emerald-300 text-emerald-800 font-extrabold"
            >
              Close
            </button>
          </div>
          {(docQuizEval.question_results || []).map((qr: any, idx: number) => (
            <div key={qr.question_id || idx} className="p-2.5 rounded-xl bg-white border border-emerald-100 space-y-1">
              <div className="flex items-center justify-between font-extrabold">
                <span>Q{idx + 1} ({qr.question_type})</span>
                <span className={qr.is_correct ? 'text-emerald-700' : 'text-amber-700'}>
                  {Math.round((qr.score_fraction || 0) * 100)}%
                </span>
              </div>
              <RichMathMarkdown text={qr.feedback} className="text-xs text-slate-700" />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ============================================================================
// 3. REAL LEARNING GAPS, GAMIFICATION, STREAKS & 6-AGENT ORCHESTRATOR PANEL
// ============================================================================

export const LearningGapsAndGamificationPanel: React.FC<{
  studentId: string;
  onSelectScreen?: (s: ScreenId) => void;
}> = ({ studentId, onSelectScreen }) => {
  const [data, setData] = React.useState<any>(null);
  const [runningCycle, setRunningCycle] = React.useState<boolean>(false);
  const [cycleMessage, setCycleMessage] = React.useState<string>('');

  const loadData = React.useCallback(async () => {
    try {
      const res = await fetch(`/api/agents/progress-recommendations/${studentId}`);
      if (res.ok) {
        setData(await res.json());
      }
    } catch {
      // ignore offline
    }
  }, [studentId]);

  React.useEffect(() => {
    loadData();
  }, [loadData]);

  const handleRunConnectedCycle = async () => {
    setRunningCycle(true);
    setCycleMessage('');
    try {
      const res = await fetch('/api/agents/workflow/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_id: studentId, subject: 'Mathematics' }),
      });
      if (res.ok) {
        const wf = await res.json();
        setCycleMessage(
          `Connected AI Ecosystem ran (${(wf.agents_executed || []).join(' → ')}). Stage: ${wf.learning_cycle_stage}.`
        );
        loadData();
      }
    } finally {
      setRunningCycle(false);
    }
  };

  if (!data) {
    return (
      <div className="eduspark-card rounded-3xl p-6 space-y-4">
        <div className="h-4 w-56 rounded-full spark-skeleton" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="h-20 rounded-2xl spark-skeleton" />
          ))}
        </div>
      </div>
    );
  }

  const gamif = data.gamification || {};
  const gaps = data.learning_gaps || {};

  return (
    <div className="space-y-5">
      {/* Real Streaks, Points, Milestones & Daily Challenges */}
      <div className="eduspark-card rounded-3xl p-6 space-y-4 border-2 border-amber-200/80 bg-gradient-to-br from-amber-50/40 via-white to-orange-50/30">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <span className="inline-flex items-center gap-1.5 text-[11px] font-extrabold uppercase tracking-wider text-amber-800">
              <Trophy className="w-3.5 h-3.5" />
              <span>Real Learning Consistency &amp; Milestones</span>
            </span>
            <h3 className="text-lg font-extrabold text-slate-900 mt-0.5">
              Your Study Streak, Learning Points &amp; Daily Challenges
            </h3>
          </div>
          <button
            type="button"
            disabled={runningCycle}
            onClick={handleRunConnectedCycle}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#101B35] text-[#35D6E8] text-xs font-extrabold shadow-sm hover:opacity-95 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${runningCycle ? 'animate-spin' : ''}`} />
            <span>{runningCycle ? 'Syncing 6 AI Agents...' : 'Sync 6-Agent Learning Cycle'}</span>
          </button>
        </div>

        {cycleMessage && (
          <div className="p-3 rounded-xl bg-cyan-50 border border-cyan-200 text-xs font-bold text-slate-900">
            ✓ {cycleMessage}
          </div>
        )}

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          <div className="p-3.5 rounded-2xl bg-white border border-amber-200">
            <div className="text-[11px] font-bold text-slate-500">Real Study Streak</div>
            <div className="text-xl font-extrabold text-amber-700 flex items-center gap-1 mt-0.5">
              <Flame className="w-5 h-5 text-orange-500" />
              <span>{gamif.current_streak_days ?? 0} day(s)</span>
            </div>
            <div className="text-[10px] text-slate-500">Longest: {gamif.longest_streak_days ?? 0} day(s)</div>
          </div>
          <div className="p-3.5 rounded-2xl bg-white border border-blue-200">
            <div className="text-[11px] font-bold text-slate-500">Learning Points</div>
            <div className="text-xl font-extrabold text-blue-700 mt-0.5">
              {gamif.total_learning_points ?? 0} pts
            </div>
            <div className="text-[10px] text-slate-500">Level {gamif.level ?? 1}</div>
          </div>
          <div className="p-3.5 rounded-2xl bg-white border border-emerald-200">
            <div className="text-[11px] font-bold text-slate-500">Completed Assessments</div>
            <div className="text-xl font-extrabold text-emerald-700 mt-0.5">
              {data.assessments_completed_count ?? 0}
            </div>
            <div className="text-[10px] text-slate-500">
              Avg: {data.verified_average_score !== null && data.verified_average_score !== undefined ? `${data.verified_average_score}%` : 'Take diagnostic'}
            </div>
          </div>
          <div className="p-3.5 rounded-2xl bg-white border border-violet-200">
            <div className="text-[11px] font-bold text-slate-500">Unlocked Badges</div>
            <div className="text-xl font-extrabold text-violet-700 mt-0.5">
              {(gamif.badges || []).length}
            </div>
            <div className="text-[10px] text-slate-500">3 / 7 / 15 / 30-day goals</div>
          </div>
        </div>

        <p className="text-xs font-semibold text-slate-700 bg-white/90 border border-amber-100 rounded-2xl p-3">
          💛 {gamif.encouragement_message}
        </p>

        {/* Streak Milestones 3, 7, 15, 30 days */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
          {(gamif.streak_milestones || []).map((m: any) => (
            <div
              key={m.badge_key}
              className={`p-2.5 rounded-xl border text-center ${m.achieved
                ? 'bg-emerald-50 border-emerald-300 text-emerald-900 font-extrabold'
                : 'bg-slate-50 border-slate-200 text-slate-500 font-bold'
                }`}
            >
              <div>{m.achieved ? '🏆' : '🎯'} {m.days}-Day Streak</div>
              <div className="text-[10px] truncate">{m.title}</div>
            </div>
          ))}
        </div>

        {/* Daily Challenges */}
        <div className="grid sm:grid-cols-3 gap-2.5 text-xs">
          {(gamif.daily_challenges || []).map((ch: any) => (
            <div
              key={ch.challenge_id}
              className={`p-3 rounded-xl border flex items-start gap-2 ${ch.completed
                ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                : 'bg-white border-slate-200 text-slate-700'
                }`}
            >
              <span>{ch.completed ? '✅' : '⭕'}</span>
              <div>
                <div className="font-bold">{ch.title}</div>
                <div className="text-[10px] font-extrabold text-blue-700">+{ch.points} pts</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Learning Gap Analyzer Output */}
      <div className="eduspark-card rounded-3xl p-6 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <span className="inline-flex items-center gap-1.5 text-[11px] font-extrabold uppercase tracking-wider text-violet-700">
              <Target className="w-3.5 h-3.5" />
              <span>Learning Gap Analyzer Agent</span>
            </span>
            <h3 className="text-lg font-extrabold text-slate-900 mt-0.5">
              Topic Understanding Map (Real Assessment Evidence)
            </h3>
            <p className="text-xs text-slate-600">{gaps.data_honesty_note}</p>
          </div>
          {onSelectScreen && (
            <button
              type="button"
              onClick={() => onSelectScreen('exams')}
              className="px-4 py-2 rounded-xl bg-blue-600 text-white text-xs font-extrabold hover:bg-blue-700"
            >
              Take Diagnostic / Quiz →
            </button>
          )}
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
          {[
            { label: 'Understood', items: gaps.understood || [], cls: 'bg-emerald-50 border-emerald-200 text-emerald-900', icon: <CheckCircle2 className="w-4 h-4 text-emerald-600" /> },
            { label: 'Partially Understood', items: gaps.partially_understood || [], cls: 'bg-blue-50 border-blue-200 text-blue-900', icon: <Sparkles className="w-4 h-4 text-blue-600" /> },
            { label: 'Needs Help', items: gaps.needs_help || [], cls: 'bg-rose-50 border-rose-200 text-rose-900', icon: <AlertTriangle className="w-4 h-4 text-rose-600" /> },
            { label: 'Needs Revision', items: gaps.needs_revision || [], cls: 'bg-amber-50 border-amber-200 text-amber-900', icon: <RefreshCw className="w-4 h-4 text-amber-600" /> },
          ].map((col) => (
            <div key={col.label} className={`p-3.5 rounded-2xl border space-y-2 ${col.cls}`}>
              <div className="font-extrabold flex items-center justify-between">
                <span className="flex items-center gap-1.5">{col.icon} {col.label}</span>
                <span>{col.items.length}</span>
              </div>
              {col.items.length === 0 ? (
                <div className="text-[11px] opacity-75">No topics in this group yet.</div>
              ) : (
                col.items.map((it: any, idx: number) => (
                  <div key={idx} className="p-2 rounded-xl bg-white/80 text-slate-800 space-y-0.5">
                    <div className="font-extrabold">{it.topic}</div>
                    <div className="text-[10px] text-slate-500">
                      {it.subject} • {it.accuracy_percentage}%
                    </div>
                  </div>
                ))
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
