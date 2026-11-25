import React from 'react';
import { Sparkles, ArrowRight, ShieldCheck } from 'lucide-react';
import { BrandTagline } from '../design-system/EduSparkLogo';

interface AppOpeningSplashProps {
  onComplete: () => void;
  isSessionChecking?: boolean;
}

export const AppOpeningSplash: React.FC<AppOpeningSplashProps> = ({ onComplete, isSessionChecking = false }) => {
  const [progress, setProgress] = React.useState<number>(0);
  const [phaseIndex, setPhaseIndex] = React.useState<number>(0);
  const [isFadingOut, setIsFadingOut] = React.useState<boolean>(false);

  const prefersReducedMotion = React.useMemo(() => {
    try {
      return typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    } catch {
      return false;
    }
  }, []);

  const phases = [
    { text: 'Initializing Specialist AI Socratic Core...', tag: 'Agentic Core' },
    { text: 'Connecting Class 1–12 NCERT & State Board Knowledge Base...', tag: 'Curriculum Engine' },
    { text: 'Calibrating 22 Scheduled Indian Languages + English...', tag: 'Multilingual AI' },
    { text: 'Optimizing Interactive Step Tutoring & Learning Models...', tag: 'Adaptive Canvas' },
    { text: 'Ready! Launching SparkMinds AI...', tag: 'Synchronized' },
  ];

  React.useEffect(() => {
    // If reduced motion is requested, complete quickly
    if (prefersReducedMotion) {
      const quickTimer = setTimeout(() => {
        setIsFadingOut(true);
        setTimeout(onComplete, 150);
      }, 350);
      return () => clearTimeout(quickTimer);
    }

    const startTime = Date.now();
    // 1.4s duration for optimal balance of premium feel and fast access
    const duration = 1400;

    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const pct = Math.min(100, Math.round((elapsed / duration) * 100));
      setProgress(pct);

      if (pct < 25) setPhaseIndex(0);
      else if (pct < 50) setPhaseIndex(1);
      else if (pct < 75) setPhaseIndex(2);
      else if (pct < 95) setPhaseIndex(3);
      else setPhaseIndex(4);

      if (pct >= 100) {
        clearInterval(interval);
        setIsFadingOut(true);
        setTimeout(() => {
          onComplete();
        }, 300);
      }
    }, 25);

    return () => clearInterval(interval);
  }, [onComplete, prefersReducedMotion]);

  const handleSkip = () => {
    setIsFadingOut(true);
    setTimeout(() => {
      onComplete();
    }, 150);
  };

  return (
    <div
      className={`fixed inset-0 z-50 flex flex-col items-center justify-between p-6 sm:p-10 select-none transition-opacity duration-400 ${
        isFadingOut ? 'opacity-0 pointer-events-none' : 'opacity-100'
      }`}
      style={{
        background: 'radial-gradient(ellipse at 50% 35%, #0F2D54 0%, #0A192F 70%, #060F1E 100%)',
      }}
    >
      {/* Top Bar with Skip Button */}
      <div className="w-full max-w-4xl flex items-center justify-between text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[#00E5FF] animate-pulse" />
          <span className="font-extrabold text-slate-300 tracking-wider uppercase text-[11px]">
            SparkMinds AI Education Platform
          </span>
        </div>
        <button
          type="button"
          onClick={handleSkip}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/10 hover:bg-white/20 text-slate-200 hover:text-white font-bold text-xs backdrop-blur border border-white/15 transition-all shadow-sm"
        >
          <span>Skip Intro</span>
          <ArrowRight className="w-3.5 h-3.5 text-[#00E5FF]" />
        </button>
      </div>

      {/* Center Hero: Logo, Title & Animated Tagline */}
      <div className="flex flex-col items-center text-center space-y-6 max-w-xl mx-auto my-auto animate-fade-in">
        {/* Glowing Logo Mark with Orbital Animation */}
        <div className="relative flex items-center justify-center">
          {/* Ambient Outer Halo */}
          <div className="absolute w-44 h-44 rounded-full bg-[#00E5FF]/20 blur-2xl animate-pulse" />
          
          {/* Outer Orbital Rotating Ring */}
          <div className="w-32 h-32 rounded-full border-2 border-dashed border-[#00E5FF]/40 animate-spin-slow flex items-center justify-center" />

          {/* Inner Glowing Hexagon / Shield */}
          <div className="absolute w-24 h-24 rounded-3xl bg-gradient-to-br from-[#1E3A8A] to-[#0A192F] border-2 border-[#00E5FF] shadow-[0_0_35px_rgba(0,229,255,0.45)] flex items-center justify-center transform hover:scale-105 transition-transform">
            <Sparkles className="w-12 h-12 text-[#00E5FF] animate-bounce" />
          </div>
        </div>

        {/* Brand Name */}
        <div className="space-y-2 pt-2">
          <h1 className="text-4xl sm:text-5xl font-black text-white tracking-tight flex items-center justify-center gap-2">
            <span>SparkMinds</span>
            <span className="text-[#00E5FF] drop-shadow-[0_0_15px_rgba(0,229,255,0.6)]">AI</span>
          </h1>

          {/* Official Brand Tagline */}
          <p className="text-base sm:text-xl pt-1 leading-snug">
            <BrandTagline variant="dark" animate />
          </p>

          <p className="text-xs sm:text-sm text-slate-300 font-medium max-w-md mx-auto leading-relaxed pt-1">
            Intelligent Multi-Turn Learning Buddy & Socratic Tutoring for Classes 1 to 12.
          </p>
        </div>
      </div>

      {/* Bottom Loading Bar & Phase Indicator */}
      <div className="w-full max-w-md space-y-3 pb-4">
        <div className="flex items-center justify-between text-xs font-extrabold">
          <span className="text-[#00E5FF] flex items-center gap-1.5 truncate pr-2">
            <span className="w-1.5 h-1.5 rounded-full bg-[#00E5FF]" />
            <span>{phases[phaseIndex]?.text || 'Loading...'}</span>
          </span>
          <span className="text-white font-mono shrink-0">{progress}%</span>
        </div>

        {/* Smooth Track Bar */}
        <div className="w-full h-2 rounded-full bg-slate-800/80 border border-slate-700/80 overflow-hidden p-0.5 shadow-inner">
          <div
            className="h-full rounded-full bg-gradient-to-r from-[#00E5FF] via-cyan-300 to-[#2563EB] transition-all duration-100 ease-out shadow-[0_0_12px_rgba(0,229,255,0.8)]"
            style={{ width: `${progress}%` }}
          />
        </div>

        <div className="flex items-center justify-between text-[11px] text-slate-400 font-semibold pt-1">
          <span className="flex items-center gap-1 text-slate-400">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>CBSE • ICSE • State Boards</span>
          </span>
          <span className="text-cyan-300 font-bold">22 Scheduled Indian Languages</span>
        </div>
      </div>
    </div>
  );
};
