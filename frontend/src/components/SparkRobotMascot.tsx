import React from 'react';

export type RobotMood =
  | 'welcome'
  | 'happy'
  | 'thinking'
  | 'celebrating'
  | 'encouraging'
  | 'guiding';

export type RobotSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

interface SparkRobotMascotProps {
  mood?: RobotMood;
  size?: RobotSize;
  animated?: boolean;
  className?: string;
  label?: string;
}

const SIZE_CLASSES: Record<RobotSize, string> = {
  xs: 'w-9 h-9',
  sm: 'w-12 h-12',
  md: 'w-16 h-16',
  lg: 'w-24 h-24',
  xl: 'w-32 h-32 sm:w-36 sm:h-36',
};

/**
 * Sparky — Original SparkMinds AI Robot Mascot & Tutor Companion
 * Designed natively for SparkMinds AI in Deep Midnight Blue (#101B35),
 * Rich Indigo (#5146E5), Bright Aqua (#35D6E8), Soft Lavender (#EEEAFE), and Crisp White (#FFFFFF).
 * Respects prefers-reduced-motion via CSS media queries in index.css.
 */
export const SparkRobotMascot: React.FC<SparkRobotMascotProps> = ({
  mood = 'happy',
  size = 'md',
  animated = true,
  className = '',
  label = 'Sparky, your SparkMinds AI Robot Companion',
}) => {
  const uid = React.useId().replace(/:/g, '');
  const isWaving = animated && (mood === 'welcome' || mood === 'celebrating' || mood === 'guiding');
  const isFloating = animated;

  return (
    <div
      className={`relative inline-flex items-center justify-center shrink-0 select-none ${SIZE_CLASSES[size]} ${
        isFloating ? 'animate-float-slow' : ''
      } ${className}`}
      role="img"
      aria-label={label}
    >
      <svg viewBox="0 0 120 128" fill="none" className="w-full h-full drop-shadow-md">
        <defs>
          <linearGradient id={`bodyGrad-${uid}`} x1="28" y1="26" x2="92" y2="112" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#FFFFFF" />
            <stop offset="65%" stopColor="#EEEAFE" />
            <stop offset="100%" stopColor="#D7DCFA" />
          </linearGradient>
          <linearGradient id={`visorGrad-${uid}`} x1="34" y1="42" x2="86" y2="76" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#101B35" />
            <stop offset="100%" stopColor="#1E2C5C" />
          </linearGradient>
          <linearGradient id={`indigoGrad-${uid}`} x1="20" y1="20" x2="100" y2="108" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#5146E5" />
            <stop offset="100%" stopColor="#3B32B3" />
          </linearGradient>
          <linearGradient id={`aquaGlow-${uid}`} x1="0" y1="0" x2="120" y2="120" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#35D6E8" />
            <stop offset="100%" stopColor="#5146E5" />
          </linearGradient>
          <radialGradient id={`halo-${uid}`} cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#35D6E8" stopOpacity="0.34" />
            <stop offset="70%" stopColor="#5146E5" stopOpacity="0.1" />
            <stop offset="100%" stopColor="#5146E5" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* Soft Luminous Aura */}
        <circle cx="60" cy="66" r="52" fill={`url(#halo-${uid})`} />

        {/* Subtle Hover Shadow */}
        <ellipse cx="60" cy="119" rx="22" ry="4.5" fill="#101B35" fillOpacity="0.16" />

        {/* Antenna Stem & Glowing Spark Star */}
        <line x1="60" y1="25" x2="60" y2="13" stroke="#5146E5" strokeWidth="3.2" strokeLinecap="round" />
        <g className={animated ? 'animate-antenna-spark' : ''}>
          <circle cx="60" cy="11" r="6.5" fill="#35D6E8" fillOpacity="0.28" />
          <path
            d="M60 4.5L62.1 9.1L66.8 11.2L62.1 13.3L60 17.9L57.9 13.3L53.2 11.2L57.9 9.1L60 4.5Z"
            fill="#35D6E8"
            stroke="#FFFFFF"
            strokeWidth="1"
            strokeLinejoin="round"
          />
        </g>

        {/* Left Ear / Audio Pod */}
        <rect x="19" y="51" width="9" height="19" rx="4.5" fill={`url(#indigoGrad-${uid})`} />
        <rect x="21.5" y="55" width="3" height="11" rx="1.5" fill="#35D6E8" />

        {/* Right Ear / Audio Pod */}
        <rect x="92" y="51" width="9" height="19" rx="4.5" fill={`url(#indigoGrad-${uid})`} />
        <rect x="95.5" y="55" width="3" height="11" rx="1.5" fill="#35D6E8" />

        {/* Left Arm */}
        <path
          d="M32 88C23 89 19 96 22 103C24 107 29 107 32 102"
          stroke={`url(#indigoGrad-${uid})`}
          strokeWidth="7"
          strokeLinecap="round"
        />
        <circle cx="22.5" cy="102.5" r="4" fill="#35D6E8" />

        {/* Right Arm (Waves smoothly in welcome / celebrating / guiding moods) */}
        <g className={isWaving ? 'animate-robot-wave' : ''}>
          {mood === 'welcome' || mood === 'celebrating' ? (
            <>
              <path
                d="M88 87C97 82 104 74 103 65"
                stroke={`url(#indigoGrad-${uid})`}
                strokeWidth="7"
                strokeLinecap="round"
              />
              <circle cx="103" cy="63" r="4.8" fill="#35D6E8" stroke="#FFFFFF" strokeWidth="1.2" />
            </>
          ) : (
            <>
              <path
                d="M88 88C97 89 101 96 98 103C96 107 91 107 88 102"
                stroke={`url(#indigoGrad-${uid})`}
                strokeWidth="7"
                strokeLinecap="round"
              />
              <circle cx="97.5" cy="102.5" r="4" fill="#35D6E8" />
            </>
          )}
        </g>

        {/* Rounded Robot Torso */}
        <rect
          x="36"
          y="80"
          width="48"
          height="32"
          rx="15"
          fill={`url(#bodyGrad-${uid})`}
          stroke="#5146E5"
          strokeWidth="2.2"
        />
        {/* Chest Knowledge Core Emblem */}
        <rect x="46" y="88" width="28" height="15" rx="7.5" fill="#101B35" />
        <circle cx="53.5" cy="95.5" r="2.7" fill="#35D6E8" />
        <rect x="59" y="93.5" width="10.5" height="4" rx="2" fill="#5146E5" />
        <rect x="61" y="94.5" width="5" height="2" rx="1" fill="#35D6E8" />

        {/* Neck Ring */}
        <rect x="50" y="75" width="20" height="7" rx="3.5" fill="#5146E5" />

        {/* Sleek Rounded Robot Helmet */}
        <rect
          x="26"
          y="25"
          width="68"
          height="54"
          rx="24"
          fill={`url(#bodyGrad-${uid})`}
          stroke="#5146E5"
          strokeWidth="2.4"
        />
        {/* Top Helmet Specular Accent */}
        <path
          d="M42 32C50 29 70 29 78 32"
          stroke="#FFFFFF"
          strokeWidth="3"
          strokeLinecap="round"
          strokeOpacity="0.9"
        />

        {/* Luminous Midnight Visor Screen */}
        <rect
          x="33"
          y="37"
          width="54"
          height="34"
          rx="14"
          fill={`url(#visorGrad-${uid})`}
          stroke="#35D6E8"
          strokeWidth="1.5"
          strokeOpacity="0.7"
        />

        {/* Expressive Animated Eyes & Mouth per Mood */}
        <g className={animated && mood !== 'celebrating' ? 'animate-robot-blink' : ''}>
          {mood === 'celebrating' ? (
            <>
              {/* Joyful curved happy eyes */}
              <path
                d="M43 54C45.5 48.5 51.5 48.5 54 54"
                stroke="#35D6E8"
                strokeWidth="3.5"
                strokeLinecap="round"
              />
              <path
                d="M66 54C68.5 48.5 74.5 48.5 77 54"
                stroke="#35D6E8"
                strokeWidth="3.5"
                strokeLinecap="round"
              />
            </>
          ) : mood === 'thinking' ? (
            <>
              {/* Curious focused thinking eyes */}
              <circle cx="48.5" cy="52" r="5.2" fill="#35D6E8" />
              <circle cx="50.2" cy="50.3" r="1.8" fill="#FFFFFF" />
              <ellipse cx="71.5" cy="52.5" rx="5.2" ry="3.6" fill="#35D6E8" />
              <circle cx="72.8" cy="51.2" r="1.5" fill="#FFFFFF" />
            </>
          ) : (
            <>
              {/* Warm intelligent luminous eyes */}
              <ellipse cx="48.5" cy="52.5" rx="5.4" ry="6" fill="#35D6E8" />
              <circle cx="50.3" cy="50.2" r="2" fill="#FFFFFF" />
              <ellipse cx="71.5" cy="52.5" rx="5.4" ry="6" fill="#35D6E8" />
              <circle cx="73.3" cy="50.2" r="2" fill="#FFFFFF" />
            </>
          )}
        </g>

        {/* Subtle Cheek Glow */}
        <ellipse cx="41" cy="60.5" rx="3.2" ry="1.8" fill="#5146E5" fillOpacity="0.6" />
        <ellipse cx="79" cy="60.5" rx="3.2" ry="1.8" fill="#5146E5" fillOpacity="0.6" />

        {/* Friendly Smile / Expression Line */}
        {mood === 'thinking' ? (
          <g>
            <circle cx="54" cy="63" r="1.6" fill="#35D6E8" />
            <circle cx="60" cy="63" r="1.6" fill="#35D6E8" />
            <circle cx="66" cy="63" r="1.6" fill="#35D6E8" />
          </g>
        ) : mood === 'celebrating' ? (
          <path
            d="M52 60.5C55 66 65 66 68 60.5"
            stroke="#35D6E8"
            strokeWidth="2.8"
            strokeLinecap="round"
          />
        ) : (
          <path
            d="M53.5 61.5C56.5 65 63.5 65 66.5 61.5"
            stroke="#35D6E8"
            strokeWidth="2.5"
            strokeLinecap="round"
          />
        )}

        {/* Celebration Sparkles */}
        {mood === 'celebrating' && (
          <g className={animated ? 'animate-antenna-spark' : ''}>
            <path d="M18 30L20 34L24 36L20 38L18 42L16 38L12 36L16 34L18 30Z" fill="#35D6E8" />
            <path d="M104 28L105.6 31.4L109 33L105.6 34.6L104 38L102.4 34.6L99 33L102.4 31.4L104 28Z" fill="#5146E5" />
          </g>
        )}

        {/* Thinking Spark Bubble */}
        {mood === 'thinking' && (
          <g>
            <circle cx="98" cy="28" r="2.2" fill="#35D6E8" />
            <circle cx="105" cy="21" r="3.6" fill="#5146E5" stroke="#35D6E8" strokeWidth="1" />
          </g>
        )}
      </svg>
    </div>
  );
};
