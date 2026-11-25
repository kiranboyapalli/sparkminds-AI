import React from 'react';
import { BrandTagline } from '../design-system/EduSparkLogo';
import { BRAND_DESCRIPTION, BRAND_TAGLINE } from '../design-system/tokens';
import { SparkRobotMascot } from './SparkRobotMascot';

interface OpeningSplashAnimationProps {
  onAnimationFinished: () => void;
  isSessionReady: boolean;
  statusMessage?: string;
}

/**
 * Part 3 — Cinematic Opening Animation (Plays EVERY Time App Launches)
 * Premium international launch stage with architectural grid, glowing orbital halo,
 * animated Sparky mascot, official tagline reveal, and sleek progress bar.
 */
export const OpeningSplashAnimation: React.FC<OpeningSplashAnimationProps> = ({
  onAnimationFinished,
  isSessionReady,
  statusMessage = 'Preparing your learning studio...',
}) => {
  const [stage, setStage] = React.useState<'logo' | 'robot' | 'tagline' | 'exit'>('logo');
  const [minTimerDone, setMinTimerDone] = React.useState<boolean>(false);

  const prefersReducedMotion = React.useMemo(() => {
    try {
      return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    } catch {
      return false;
    }
  }, []);

  React.useEffect(() => {
    if (prefersReducedMotion) {
      setStage('tagline');
      const quick = setTimeout(() => setMinTimerDone(true), 220);
      return () => clearTimeout(quick);
    }

    const t1 = setTimeout(() => setStage('robot'), 240);
    const t2 = setTimeout(() => setStage('tagline'), 580);
    const t3 = setTimeout(() => setMinTimerDone(true), 1550);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, [prefersReducedMotion]);

  React.useEffect(() => {
    if (minTimerDone && isSessionReady && stage !== 'exit') {
      setStage('exit');
      const exitTimer = setTimeout(
        () => onAnimationFinished(),
        prefersReducedMotion ? 50 : 320
      );
      return () => clearTimeout(exitTimer);
    }
  }, [minTimerDone, isSessionReady, stage, onAnimationFinished, prefersReducedMotion]);

  React.useEffect(() => {
    const safetyTimer = setTimeout(() => onAnimationFinished(), 3600);
    return () => clearTimeout(safetyTimer);
  }, [onAnimationFinished]);

  const progressWidth =
    stage === 'logo'
      ? '28%'
      : stage === 'robot'
        ? '62%'
        : isSessionReady
          ? '100%'
          : '86%';

  return (
    <div
      role="status"
      aria-live="polite"
      data-testid="opening-splash"
      className={`fixed inset-0 z-[100] flex flex-col items-center justify-center text-white transition-opacity duration-300 select-none overflow-hidden px-6 ${
        stage === 'exit' ? 'opacity-0 pointer-events-none' : 'opacity-100'
      }`}
      style={{
        background:
          'radial-gradient(ellipse 80% 60% at 50% 24%, #252E73 0%, #101B35 58%, #070D1D 100%)',
      }}
    >
      {/* Subtle Architectural Grid Overlay */}
      <div aria-hidden="true" className="pointer-events-none absolute inset-0 spark-hero-grid opacity-55" />

      {/* Luminous Indigo & Aqua Ambient Orbs */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -top-28 left-1/2 -translate-x-1/2 w-[36rem] h-[36rem] rounded-full bg-[#5146E5]/25 blur-[110px]"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -bottom-28 left-1/2 -translate-x-1/2 w-[30rem] h-[30rem] rounded-full bg-[#35D6E8]/20 blur-[100px]"
      />

      <div className="relative z-10 flex flex-col items-center max-w-xl w-full text-center space-y-6">
        {/* Glass Eyebrow Pill */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-white/[0.07] border border-white/15 backdrop-blur-md text-[11px] font-bold tracking-wider uppercase text-indigo-100 animate-fade-in">
          <span className="w-2 h-2 rounded-full bg-[#35D6E8] animate-pulse" />
          <span>{BRAND_DESCRIPTION}</span>
        </div>

        {/* 1. SparkMinds AI Crest & Wordmark */}
        <div className="flex items-center justify-center gap-3.5 animate-spark-celebrate">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-[#5146E5] via-[#2D2C7A] to-[#101B35] border border-[#35D6E8]/70 p-2.5 shadow-[0_0_32px_rgba(53,214,232,0.3)] flex items-center justify-center">
            <svg className="w-full h-full" viewBox="0 0 48 48" fill="none" aria-hidden="true">
              <path
                d="M8 18C8 15.8 9.8 14 12 14H22.2V37.5H12C9.8 37.5 8 35.7 8 33.5V18Z"
                fill="#35D6E8"
                fillOpacity="0.24"
                stroke="#FFFFFF"
                strokeWidth="2.3"
                strokeLinejoin="round"
              />
              <path
                d="M40 18C40 15.8 38.2 14 36 14H25.8V37.5H36C38.2 37.5 40 35.7 40 33.5V18Z"
                fill="#EEEAFE"
                fillOpacity="0.2"
                stroke="#FFFFFF"
                strokeWidth="2.3"
                strokeLinejoin="round"
              />
              <path
                d="M24 3.5L27.4 13.1L37 16.5L27.4 19.9L24 29.5L20.6 19.9L11 16.5L20.6 13.1L24 3.5Z"
                fill="#35D6E8"
                stroke="#FFFFFF"
                strokeWidth="1.6"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <div className="flex items-center gap-2.5">
            <h1 className="font-display text-4xl sm:text-5xl font-bold tracking-tight text-white">
              SparkMinds
            </h1>
            <span className="text-sm font-extrabold px-3 py-1 rounded-xl bg-gradient-to-r from-[#35D6E8] to-[#7BE9F5] text-[#101B35] shadow-md shadow-[#35D6E8]/30">
              AI
            </span>
          </div>
        </div>

        {/* 2. Animated Sparky AI Robot Mascot with Orbital Halo Rings */}
        <div
          className={`relative flex items-center justify-center py-2 transition-all duration-500 ease-out ${
            stage === 'logo'
              ? 'opacity-0 translate-y-4 scale-90'
              : 'opacity-100 translate-y-0 scale-100'
          }`}
        >
          <div
            aria-hidden="true"
            className="absolute w-44 h-44 rounded-full border border-dashed border-[#35D6E8]/30 animate-orbit-slow"
          />
          <div
            aria-hidden="true"
            className="absolute w-36 h-36 rounded-full border border-[#5146E5]/45"
          />
          <SparkRobotMascot mood="welcome" size="xl" animated={!prefersReducedMotion} />
        </div>

        {/* 3. Official Tagline Reveal */}
        <div
          className={`space-y-2 transition-all duration-500 ${
            stage === 'tagline' || stage === 'exit'
              ? 'opacity-100 animate-tagline-reveal'
              : 'opacity-0 translate-y-3'
          }`}
        >
          <p
            aria-label={BRAND_TAGLINE}
            className="text-lg sm:text-2xl leading-snug drop-shadow-[0_2px_16px_rgba(53,214,232,0.3)]"
          >
            <BrandTagline variant="dark" />
          </p>
        </div>

        {/* 4. Sleek Gradient Progress Indicator */}
        <div className="w-64 space-y-2 pt-1">
          <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden border border-white/10">
            <div
              className="h-full rounded-full bg-gradient-to-r from-[#5146E5] via-[#35D6E8] to-[#A5F3FC] transition-all duration-500 ease-out shadow-[0_0_12px_rgba(53,214,232,0.8)]"
              style={{ width: progressWidth }}
            />
          </div>
          <p className="text-[11px] font-semibold text-indigo-200/80 tracking-wide">
            {isSessionReady ? 'Launching your personal AI studio...' : statusMessage}
          </p>
        </div>
      </div>
    </div>
  );
};
