import React from 'react';
import {
  Send,
  RefreshCw,
  Plus,
  Upload,
  AlertTriangle,
  Languages,
  X,
  Eye,
  Copy,
  Check,
} from 'lucide-react';
import { ALL_23_INDIAN_LANGUAGES } from '../curriculum/curriculumData';
import { OnboardingState } from '../onboarding/SevenStepOnboarding';
import { HelpTip } from '../components/HelpTip';
import { ScreenId } from '../design-system/tokens';
import { SparkRobotMascot, RobotMood } from '../components/SparkRobotMascot';
import { VisualTeachingCanvas, VisualAidPayload } from '../components/VisualTeachingCanvas';
import { RobotGuideTip } from '../components/RobotGuideTip';
import { RichMathMarkdown, cleanMathText } from '../utils/formatMathText';

/**
 * SparkMinds AI — Real Multi-Turn AI Robot Teacher (Sparky) & Visual AI Learning Buddy.
 * Every student message is sent to POST /api/tutor/chat (real Gemini model + conversation memory
 * + real Visual AI Teaching Engine). No fake or hardcoded replies are ever generated.
 */

interface ChatMessage {
  id: string;
  role: 'student' | 'assistant' | 'error';
  content: string;
  model?: string;
  imageName?: string;
  visualAid?: VisualAidPayload | null;
  retryPayload?: { message: string; imageBase64?: string; imageMime?: string; imageName?: string };
}

interface LearningBuddyChatProps {
  onboarding: OnboardingState;
  initialQuestion?: string;
  initialSubject?: string;
  onSelectScreen?: (s: ScreenId) => void;
}

const storageKey = (studentId: string) => `sparkminds_chat_${studentId}`;

// Clean rich math & markdown renderer (converts LaTeX, fixes broken math symbols, preserves prices)
const MarkdownText: React.FC<{ text: string }> = ({ text }) => (
  <RichMathMarkdown text={text} />
);

export const LearningBuddyChat: React.FC<LearningBuddyChatProps> = ({
  onboarding,
  initialQuestion,
  initialSubject,
  onSelectScreen,
}) => {
  const [messages, setMessages] = React.useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = React.useState<string | null>(null);
  const [input, setInput] = React.useState<string>('');
  const [isSending, setIsSending] = React.useState<boolean>(false);
  const [robotMood, setRobotMood] = React.useState<RobotMood>('welcome');
  const [selectedLang, setSelectedLang] = React.useState<string>(
    onboarding.preferredExplanationLanguage
  );
  const [selectedSubject, setSelectedSubject] = React.useState<string>(
    initialSubject || 'All Subjects'
  );
  const [providerConfigured, setProviderConfigured] = React.useState<boolean | null>(null);
  const [copiedMsgId, setCopiedMsgId] = React.useState<string | null>(null);
  const [attachedImage, setAttachedImage] = React.useState<{
    b64: string;
    mime: string;
    name: string;
  } | null>(null);
  const sendingRef = React.useRef(false);
  const scrollRef = React.useRef<HTMLDivElement>(null);
  const inputRef = React.useRef<HTMLTextAreaElement>(null);

  // Restore this student's conversation (per-student isolation)
  React.useEffect(() => {
    try {
      const raw = window.localStorage.getItem(storageKey(onboarding.studentId));
      if (raw) {
        const saved = JSON.parse(raw);
        setMessages(Array.isArray(saved.messages) ? saved.messages : []);
        setConversationId(saved.conversationId || null);
      } else {
        setMessages([]);
        setConversationId(null);
      }
    } catch {
      setMessages([]);
      setConversationId(null);
    }
  }, [onboarding.studentId]);

  React.useEffect(() => {
    try {
      window.localStorage.setItem(
        storageKey(onboarding.studentId),
        JSON.stringify({
          conversationId,
          messages: messages.filter((m) => m.role !== 'error').slice(-40),
        })
      );
    } catch {
      // ignore storage errors
    }
  }, [messages, conversationId, onboarding.studentId]);

  React.useEffect(() => {
    setSelectedLang(onboarding.preferredExplanationLanguage);
  }, [onboarding.preferredExplanationLanguage]);

  React.useEffect(() => {
    fetch('/api/tutor/chat/status')
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => setProviderConfigured(d ? Boolean(d.configured) : null))
      .catch(() => setProviderConfigured(null));
  }, []);

  React.useEffect(() => {
    if (initialQuestion) {
      setInput(initialSubject ? `(${initialSubject}) ${initialQuestion}` : initialQuestion);
      inputRef.current?.focus();
    }
  }, [initialQuestion, initialSubject]);

  React.useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, isSending]);

  const handleImage = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = '';
    if (!file) return;
    if (!/^image\/(png|jpe?g|webp|heic|heif)$/i.test(file.type)) {
      setMessages((prev) => [
        ...prev,
        {
          id: `e_${Date.now()}`,
          role: 'error',
          content: 'Please attach a PNG, JPG or WEBP photo of your homework.',
        },
      ]);
      return;
    }
    if (file.size > 6 * 1024 * 1024) {
      setMessages((prev) => [
        ...prev,
        {
          id: `e_${Date.now()}`,
          role: 'error',
          content: 'That image is larger than 6 MB. Please attach a smaller photo.',
        },
      ]);
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === 'string') {
        setAttachedImage({ b64: reader.result, mime: file.type, name: file.name });
      }
    };
    reader.readAsDataURL(file);
  };

  const sendMessage = async (
    payload?: ChatMessage['retryPayload'],
    retryOfId?: string,
    directPrompt?: string
  ) => {
    if (sendingRef.current) return;
    const rawText = payload ? payload.message : (directPrompt ?? input).trim();
    const text =
      !payload &&
      !directPrompt &&
      selectedSubject !== 'All Subjects' &&
      rawText &&
      !rawText.startsWith(`(${selectedSubject})`)
        ? `(${selectedSubject}) ${rawText}`
        : rawText;
    const img = payload
      ? payload.imageBase64
        ? {
            b64: payload.imageBase64,
            mime: payload.imageMime || 'image/png',
            name: payload.imageName || 'image',
          }
        : null
      : attachedImage;
    if (!text && !img) return;

    sendingRef.current = true;
    setIsSending(true);
    setRobotMood('thinking');

    const studentMsgId = `s_${Date.now()}`;
    setMessages((prev) => {
      const base = retryOfId ? prev.filter((m) => m.id !== retryOfId) : prev;
      if (payload) return base;
      return [
        ...base,
        {
          id: studentMsgId,
          role: 'student',
          content: text || '(Photo attached)',
          imageName: img?.name,
        },
      ];
    });
    if (!payload && !directPrompt) {
      setInput('');
      setAttachedImage(null);
    }

    try {
      const res = await fetch('/api/tutor/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: onboarding.studentId,
          message: text,
          conversation_id: conversationId,
          language_override: selectedLang,
          image_base64: img?.b64 || null,
          image_mime_type: img?.mime || null,
        }),
      });
      let data: any = null;
      try {
        data = await res.json();
      } catch {
        data = null;
      }
      if (!res.ok) {
        if (res.status === 404) setConversationId(null);
        throw new Error(
          (data && data.detail) ||
            `The server returned an error (HTTP ${res.status}). No answer was generated.`
        );
      }
      setConversationId(data.conversation_id);
      const attachedVisual = data.visual_aid || data.reply?.visual_aid || null;
      setMessages((prev) => [
        ...prev,
        {
          id: data.reply.id,
          role: 'assistant',
          content: data.reply.content,
          model: data.model_used,
          visualAid: attachedVisual,
        },
      ]);
      setRobotMood('happy');
    } catch (err: unknown) {
      const msg =
        err instanceof TypeError
          ? 'Could not reach the SparkMinds AI server. Please check your internet connection and retry.'
          : err instanceof Error
            ? err.message
            : 'Something went wrong. No answer was generated.';
      setMessages((prev) => [
        ...prev,
        {
          id: `e_${Date.now()}`,
          role: 'error',
          content: msg,
          retryPayload: {
            message: text,
            imageBase64: img?.b64,
            imageMime: img?.mime,
            imageName: img?.name,
          },
        },
      ]);
      setRobotMood('encouraging');
    } finally {
      sendingRef.current = false;
      setIsSending(false);
      inputRef.current?.focus();
    }
  };

  const startNewConversation = async () => {
    if (conversationId) {
      fetch(
        `/api/tutor/chat/${conversationId}?student_id=${encodeURIComponent(onboarding.studentId)}`,
        { method: 'DELETE' }
      ).catch(() => {});
    }
    setConversationId(null);
    setMessages([]);
    setInput('');
    setAttachedImage(null);
    setRobotMood('welcome');
    inputRef.current?.focus();
  };

  const starterQuestions = [
    {
      tag: 'MATH VISUAL',
      prompt: 'Explain fractions like 3/4 visually with equal parts',
      sub: 'Interactive equal-parts slicer',
    },
    {
      tag: 'SCIENCE LAB',
      prompt: 'How does the water cycle work step by step?',
      sub: 'Animated evaporation & clouds',
    },
    {
      tag: 'CIRCUIT LAB',
      prompt: 'Explain how an electric circuit lights a bulb',
      sub: 'Toggleable live switch circuit',
    },
    {
      tag: 'GEOMETRY',
      prompt: 'Show me how a right triangle and Pythagoras theorem work',
      sub: 'Labelled sides & formula model',
    },
  ];

  const quickFollowUps = [
    'Explain that in simpler words.',
    'Give me another real-life example.',
    'Show the steps one by one.',
    'Ask me a quick practice question on this.',
  ];

  return (
    <div className="space-y-4 animate-fade-in">
      <RobotGuideTip
        tipId="ai_learning_buddy"
        studentId={onboarding.studentId}
        title="Sparky — Visual AI Teacher"
        message="Ask any Math, Science, Geography, History, or English question. Sparky teaches step by step and adds interactive diagrams whenever visuals help!"
        mood="guiding"
      />

      <div className="eduspark-card rounded-3xl overflow-hidden flex flex-col min-h-[70vh]">
        {/* Midnight Blue & Indigo Robot Teacher Header */}
        <div
          className="px-5 py-4 text-white flex flex-wrap items-center justify-between gap-3 relative overflow-hidden"
          style={{
            background: 'linear-gradient(135deg, #0D1630 0%, #1F2963 58%, #5146E5 100%)',
          }}
        >
          <div aria-hidden="true" className="pointer-events-none absolute inset-0 spark-hero-grid opacity-45" />
          <div className="relative z-10 flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-white/10 border border-[#35D6E8]/45 flex items-center justify-center shrink-0">
              <SparkRobotMascot mood={isSending ? 'thinking' : robotMood} size="xs" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base md:text-lg font-extrabold tracking-tight text-white">
                  Sparky — AI Learning Buddy
                </h3>
                <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#35D6E8]/20 border border-[#35D6E8]/40 text-[#35D6E8] text-[10px] font-extrabold">
                  <Eye className="w-3 h-3" /> Visual Teaching
                </span>
              </div>
              <div className="text-xs text-indigo-100/90 font-medium">
                Grade {onboarding.grade} • {onboarding.board} • {selectedLang}
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <select
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              aria-label="Subject focus"
              className="rounded-xl bg-white/10 border border-white/20 px-3 py-2 text-xs font-bold text-white focus:outline-none min-h-[38px]"
            >
              {[
                'All Subjects',
                'Mathematics',
                'Science',
                'English',
                'Social Science',
                'Computer Science',
              ].map((subj) => (
                <option key={subj} value={subj} className="text-[#101B35]">
                  {subj}
                </option>
              ))}
            </select>

            <div className="flex items-center gap-1.5 bg-white/10 rounded-xl px-2.5 py-1.5 border border-white/20 min-h-[38px]">
              <Languages className="w-4 h-4 text-[#35D6E8]" />
              <select
                value={selectedLang}
                onChange={(e) => setSelectedLang(e.target.value)}
                className="bg-transparent text-xs font-bold text-white focus:outline-none"
                aria-label="Explanation language"
              >
                {ALL_23_INDIAN_LANGUAGES.map((l) => (
                  <option key={l.code} value={l.name} className="text-[#101B35]">
                    {l.name} ({l.nativeName})
                  </option>
                ))}
              </select>
            </div>

            <button
              type="button"
              onClick={startNewConversation}
              disabled={isSending}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#35D6E8] text-[#101B35] text-xs font-extrabold hover:bg-[#5ce0ef] disabled:opacity-50 transition min-h-[38px]"
            >
              <Plus className="w-3.5 h-3.5" /> New Chat
            </button>
          </div>
        </div>

        {providerConfigured === false && (
          <div className="mx-4 mt-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs font-bold text-rose-800 flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>
              The AI provider is not configured on the server yet. Please set GEMINI_API_KEY to
              enable live AI tutoring replies.
            </span>
          </div>
        )}

        {/* Messages Stream */}
        <div
          ref={scrollRef}
          className="flex-1 overflow-y-auto p-4 md:p-6 space-y-5 bg-[#F6F7FC] max-h-[62vh]"
        >
          {messages.length === 0 && !isSending && (
            <div className="text-center py-6 space-y-4">
              <div className="flex justify-center">
                <SparkRobotMascot mood="welcome" size="lg" />
              </div>
              <div className="space-y-1">
                <div className="text-lg font-extrabold text-[#101B35]">
                  Hi! I&apos;m Sparky. What would you like to learn today?
                </div>
                <p className="text-xs text-[#202943]/75 max-w-md mx-auto font-medium">
                  Ask any school question, upload a homework photo, or tap a visual topic below to
                  learn step by step with interactive diagrams.
                </p>
              </div>

              {/* Real Interactive Visual Subject Starter Cards */}
              <div className="grid sm:grid-cols-2 gap-3 max-w-2xl mx-auto pt-1 text-left">
                {starterQuestions.map((item) => (
                  <button
                    key={item.prompt}
                    type="button"
                    onClick={() => {
                      setSelectedSubject('All Subjects');
                      setInput(item.prompt);
                      inputRef.current?.focus();
                    }}
                    className="group p-3.5 rounded-2xl bg-white border border-[#DCE2F5] hover:border-[#5146E5] hover:shadow-md hover:-translate-y-0.5 transition flex flex-col gap-1.5"
                  >
                    <div className="flex items-center justify-between gap-2 w-full">
                      <span className="px-2 py-0.5 rounded-md bg-[#EEEAFE] text-[#5146E5] text-[10px] font-extrabold tracking-wider">
                        {item.tag}
                      </span>
                      <span className="text-[#5146E5] font-extrabold text-xs group-hover:translate-x-0.5 transition">
                        →
                      </span>
                    </div>
                    <span className="text-xs font-extrabold text-[#101B35] leading-snug">
                      {item.prompt}
                    </span>
                    <span className="text-[11px] font-medium text-[#202943]/65">{item.sub}</span>
                  </button>
                ))}
              </div>

              <div className="flex items-center justify-center gap-2 pt-1">
                {onSelectScreen && (
                  <button
                    type="button"
                    onClick={() => onSelectScreen('subjects')}
                    className="px-4 py-2 rounded-xl border border-[#DCE2F5] bg-white hover:border-[#5146E5] text-xs font-extrabold text-[#5146E5] transition"
                  >
                    Try a Guided Lesson →
                  </button>
                )}
                <HelpTip
                  title="Tips for Sparky AI Teacher"
                  text="Switch subjects or languages anytime without losing your chat. For visual concepts like fractions, water cycle, cells, circuits, geometry, landforms, or timelines, Sparky automatically pairs explanations with labelled interactive diagrams."
                />
              </div>
            </div>
          )}

          {messages.map((m) => {
            if (m.role === 'student') {
              return (
                <div key={m.id} className="flex flex-col items-end gap-1">
                  <span className="text-[10px] font-bold text-[#202943]/50 px-1">You</span>
                  <div className="max-w-[85%] md:max-w-2xl rounded-2xl rounded-tr-sm bg-[#5146E5] text-white px-4 py-3 shadow-sm">
                    <p className="text-sm font-medium whitespace-pre-wrap break-words">
                      {m.content}
                    </p>
                    {m.imageName && (
                      <div className="text-[11px] text-[#35D6E8] mt-1">Photo: {m.imageName}</div>
                    )}
                  </div>
                </div>
              );
            }
            if (m.role === 'error') {
              return (
                <div key={m.id} className="flex items-start gap-2.5">
                  <SparkRobotMascot mood="encouraging" size="xs" className="mt-1" />
                  <div className="max-w-[85%] md:max-w-2xl rounded-2xl bg-rose-50 border border-rose-200 px-4 py-3 text-rose-900 space-y-2">
                    <div className="flex items-start gap-2 text-sm font-semibold">
                      <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                      <span>{m.content}</span>
                    </div>
                    {m.retryPayload && (
                      <button
                        type="button"
                        disabled={isSending}
                        onClick={() => sendMessage(m.retryPayload, m.id)}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-extrabold disabled:opacity-50"
                      >
                        <RefreshCw className="w-3.5 h-3.5" /> Retry
                      </button>
                    )}
                  </div>
                </div>
              );
            }
            return (
              <div key={m.id} className="flex items-start gap-2.5">
                <div className="shrink-0 mt-4">
                  <SparkRobotMascot mood="happy" size="xs" />
                </div>
                <div className="flex flex-col items-start gap-1 max-w-[92%] md:max-w-3xl w-full">
                  <div className="w-full flex items-center justify-between gap-2 px-1">
                    <span className="text-[10px] font-extrabold text-[#5146E5]">
                      Sparky • AI Robot Teacher
                    </span>
                    <button
                      type="button"
                      onClick={() => {
                        navigator.clipboard?.writeText(cleanMathText(m.content)).catch(() => {});
                        setCopiedMsgId(m.id);
                        window.setTimeout(() => setCopiedMsgId((curr) => (curr === m.id ? null : curr)), 1800);
                      }}
                      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold text-[#202943]/60 hover:text-[#5146E5] hover:bg-[#EEEAFE] transition"
                      title="Copy explanation"
                    >
                      {copiedMsgId === m.id ? (
                        <>
                          <Check className="w-3 h-3 text-emerald-600" />
                          <span className="text-emerald-700">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          <span>Copy</span>
                        </>
                      )}
                    </button>
                  </div>
                  <div className="w-full rounded-2xl rounded-tl-sm bg-white border border-[#DCE2F5] px-4 py-3.5 sm:px-5 sm:py-4 text-[#202943] shadow-[0_4px_16px_-8px_rgba(16,27,53,0.12)] break-words">
                    <MarkdownText text={m.content} />
                    {m.visualAid && (
                      <VisualTeachingCanvas
                        visualAid={m.visualAid}
                        onAnsweredCheck={(ok) => setRobotMood(ok ? 'celebrating' : 'encouraging')}
                        onAskAnotherWay={(prompt) => sendMessage(undefined, undefined, prompt)}
                      />
                    )}
                  </div>
                </div>
              </div>
            );
          })}

          {isSending && (
            <div className="flex items-center gap-2.5">
              <SparkRobotMascot mood="thinking" size="xs" />
              <div className="rounded-2xl bg-white border border-[#DCE2F5] px-4 py-3 text-xs font-bold text-[#5146E5] flex items-center gap-2.5 shadow-sm">
                <span className="flex gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#5146E5] animate-bounce" />
                  <span className="w-1.5 h-1.5 rounded-full bg-[#35D6E8] animate-bounce [animation-delay:150ms]" />
                  <span className="w-1.5 h-1.5 rounded-full bg-[#5146E5] animate-bounce [animation-delay:300ms]" />
                </span>
                Sparky is preparing your explanation & visual...
              </div>
            </div>
          )}
        </div>

        {/* Clean Composer */}
        <div className="border-t border-[#E4E8F5] p-3 md:p-4 bg-white space-y-2.5">
          {messages.some((m) => m.role === 'assistant') && (
            <div className="flex flex-wrap gap-1.5">
              {quickFollowUps.map((q) => (
                <button
                  key={q}
                  type="button"
                  disabled={isSending}
                  onClick={() => {
                    setInput(q);
                    inputRef.current?.focus();
                  }}
                  className="px-3 py-1.5 rounded-full border border-[#DCE2F5] bg-[#F6F7FC] hover:bg-[#EEEAFE] hover:border-[#5146E5] text-[11px] font-bold text-[#202943] disabled:opacity-50 transition"
                >
                  {q}
                </button>
              ))}
            </div>
          )}
          {attachedImage && (
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#EEEAFE] border border-[#5146E5]/30 text-xs font-bold text-[#5146E5]">
              <span>Photo: {attachedImage.name}</span>
              <button
                type="button"
                onClick={() => setAttachedImage(null)}
                aria-label="Remove image"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
          <div className="flex items-end gap-2">
            <label
              className="shrink-0 inline-flex items-center justify-center w-11 h-11 rounded-xl border border-[#DCE2F5] bg-[#F6F7FC] hover:bg-[#EEEAFE] cursor-pointer transition"
              title="Attach a homework photo"
            >
              <Upload className="w-4 h-4 text-[#5146E5]" />
              <input
                type="file"
                accept="image/png,image/jpeg,image/webp"
                className="hidden"
                onChange={handleImage}
              />
            </label>
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              rows={1}
              maxLength={4000}
              placeholder="Ask Sparky anything… (Enter to send, Shift+Enter for new line)"
              className="flex-1 resize-none rounded-xl border border-[#DCE2F5] bg-[#F6F7FC] focus:bg-white px-3.5 py-3 text-sm font-medium text-[#202943] focus:outline-none focus:ring-2 focus:ring-[#5146E5] max-h-40 transition"
            />
            <button
              type="button"
              onClick={() => sendMessage()}
              disabled={isSending || (!input.trim() && !attachedImage)}
              className="shrink-0 inline-flex items-center gap-1.5 px-4 h-11 rounded-xl bg-[#5146E5] hover:bg-[#4338CA] text-white text-xs font-extrabold disabled:opacity-40 shadow-sm transition"
            >
              <Send className="w-4 h-4" />
              <span className="hidden sm:inline">{isSending ? 'Sending…' : 'Send'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
