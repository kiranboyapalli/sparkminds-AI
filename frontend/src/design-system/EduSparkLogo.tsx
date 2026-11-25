import React from 'react';
import { BRAND_TAGLINE, BRAND_TAGLINE_PARTS } from './tokens';

export interface BrandTaglineProps {
  variant?: 'dark' | 'light';
  className?: string;
  animate?: boolean;
}

/**
 * Renders the exact official tagline:
 * "Dream Beyond Limits. Learn With Fire. Lead With Power!"
 * with clear three-phrase visual hierarchy across dark and light surfaces.
 */
export const BrandTagline: React.FC<BrandTaglineProps> = ({
  variant = 'dark',
  className = '',
  animate = false,
}) => {
  const animClass = animate ? 'animate-tagline-reveal' : '';
  if (variant === 'light') {
    return (
      <span
        aria-label={BRAND_TAGLINE}
        className={`font-display font-extrabold tracking-tight ${animClass} ${className}`.trim()}
      >
        <span className="text-[#101B35]">{BRAND_TAGLINE_PARTS.first} </span>
        <span className="bg-gradient-to-r from-[#5146E5] via-[#7C3AED] to-[#D97706] bg-clip-text text-transparent">
          {BRAND_TAGLINE_PARTS.second}
        </span>{' '}
        <span className="text-[#0EA5BE]">{BRAND_TAGLINE_PARTS.third}</span>
      </span>
    );
  }

  return (
    <span
      aria-label={BRAND_TAGLINE}
      className={`font-display font-extrabold tracking-tight ${animClass} ${className}`.trim()}
    >
      <span className="text-white">{BRAND_TAGLINE_PARTS.first} </span>
      <span className="bg-gradient-to-r from-[#FDE68A] via-[#FBBF24] to-[#FB923C] bg-clip-text text-transparent">
        {BRAND_TAGLINE_PARTS.second}
      </span>{' '}
      <span className="text-[#35D6E8]">{BRAND_TAGLINE_PARTS.third}</span>
    </span>
  );
};

interface EduSparkLogoProps {
  size?: 'sm' | 'md' | 'lg';
  showTagline?: boolean;
  lightText?: boolean;
}

/**
 * SparkMinds AI — Official Brand Identity Logo
 * - App Name: SparkMinds AI
 * - Tagline: Dream Beyond Limits. Learn With Fire. Lead With Power!
 * - Palette: Deep Midnight Blue (#101B35), Rich Indigo (#5146E5), Bright Aqua (#35D6E8), White (#FFFFFF)
 */
export const EduSparkLogo: React.FC<EduSparkLogoProps> = ({
  size = 'md',
  showTagline = false,
  lightText = false,
}) => {
  const iconDim = size === 'sm' ? 'w-9 h-9' : size === 'lg' ? 'w-14 h-14' : 'w-11 h-11';
  const textClass =
    size === 'sm'
      ? 'text-lg'
      : size === 'lg'
        ? 'text-2xl sm:text-3xl'
        : 'text-xl';

  return (
    <div className="inline-flex items-center gap-3 select-none">
      {/* SparkMinds AI Emblem — Luminous Spark & Open Knowledge Crest */}
      <div
        className={`${iconDim} rounded-2xl bg-gradient-to-br from-[#101B35] via-[#26256B] to-[#5146E5] p-2 shadow-lg flex items-center justify-center relative overflow-hidden border border-[#35D6E8]/45 shrink-0`}
        aria-hidden="true"
      >
        <svg className="w-full h-full" viewBox="0 0 48 48" fill="none">
          <defs>
            <linearGradient id="sparkCrestGrad" x1="6" y1="6" x2="42" y2="42" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#35D6E8" />
              <stop offset="100%" stopColor="#A5B4FC" />
            </linearGradient>
          </defs>
          <path
            d="M8 18C8 15.8 9.8 14 12 14H22.2V37.5H12C9.8 37.5 8 35.7 8 33.5V18Z"
            fill="#35D6E8"
            fillOpacity="0.22"
            stroke="#FFFFFF"
            strokeWidth="2.2"
            strokeLinejoin="round"
          />
          <path
            d="M40 18C40 15.8 38.2 14 36 14H25.8V37.5H36C38.2 37.5 40 35.7 40 33.5V18Z"
            fill="#EEEAFE"
            fillOpacity="0.2"
            stroke="#FFFFFF"
            strokeWidth="2.2"
            strokeLinejoin="round"
          />
          <path
            d="M24 3.5L27.4 13.1L37 16.5L27.4 19.9L24 29.5L20.6 19.9L11 16.5L20.6 13.1L24 3.5Z"
            fill="url(#sparkCrestGrad)"
            stroke="#FFFFFF"
            strokeWidth="1.6"
            strokeLinejoin="round"
          />
        </svg>
      </div>

      {/* Wordmark & Tagline */}
      <div className="flex flex-col leading-tight min-w-0">
        <div className={`font-extrabold tracking-tight flex items-center gap-1.5 ${textClass}`}>
          <span className={lightText ? 'text-white' : 'text-[#101B35]'}>SparkMinds</span>
          <span
            className={`px-2 py-0.5 rounded-lg text-[0.62em] font-extrabold tracking-wide ${
              lightText
                ? 'bg-[#35D6E8] text-[#101B35]'
                : 'bg-[#5146E5] text-white'
            }`}
          >
            AI
          </span>
        </div>
        {showTagline && (
          <BrandTagline
            variant={lightText ? 'dark' : 'light'}
            className="text-[10.5px] sm:text-[11px] mt-0.5 leading-snug"
          />
        )}
      </div>
    </div>
  );
};
