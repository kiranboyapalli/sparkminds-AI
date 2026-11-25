import React from 'react';
import { X } from 'lucide-react';
import { SparkRobotMascot, RobotMood } from './SparkRobotMascot';

interface RobotGuideTipProps {
  tipId: string;
  studentId: string;
  title: string;
  message: string;
  mood?: RobotMood;
  actionLabel?: string;
  onAction?: () => void;
}

const tipKey = (studentId: string, tipId: string) =>
  `sparkminds_robot_tip_dismissed_${studentId}_${tipId}`;

/**
 * Part 12 — Contextual, Dismissible Sparky Robot Guide
 * Provides concise 1-sentence guidance inside each feature screen without cluttering
 * or blocking workflow. Dismissals persist per student and can be reset from Settings.
 */
export const RobotGuideTip: React.FC<RobotGuideTipProps> = ({
  tipId,
  studentId,
  title,
  message,
  mood = 'guiding',
  actionLabel,
  onAction,
}) => {
  const [dismissed, setDismissed] = React.useState<boolean>(() => {
    try {
      return window.localStorage.getItem(tipKey(studentId, tipId)) === 'true';
    } catch {
      return false;
    }
  });

  React.useEffect(() => {
    const sync = () => {
      try {
        setDismissed(window.localStorage.getItem(tipKey(studentId, tipId)) === 'true');
      } catch {
        setDismissed(false);
      }
    };
    sync();
    window.addEventListener('sparkminds-reset-tips', sync);
    return () => window.removeEventListener('sparkminds-reset-tips', sync);
  }, [studentId, tipId]);

  if (dismissed) return null;

  const handleDismiss = () => {
    setDismissed(true);
    try {
      window.localStorage.setItem(tipKey(studentId, tipId), 'true');
    } catch {
      // ignore storage errors
    }
  };

  return (
    <div className="rounded-2xl bg-[#EEEAFE]/85 border border-[#5146E5]/20 px-4 py-3 flex items-center justify-between gap-3 animate-fade-in">
      <div className="flex items-center gap-3 min-w-0">
        <SparkRobotMascot mood={mood} size="xs" />
        <div className="min-w-0">
          <div className="text-[11px] font-extrabold text-[#5146E5]">{title}</div>
          <p className="text-xs font-semibold text-[#202943] leading-snug">{message}</p>
        </div>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        {actionLabel && onAction && (
          <button
            type="button"
            onClick={onAction}
            className="px-3 py-1.5 rounded-xl bg-[#5146E5] hover:bg-[#4338CA] text-white text-[11px] font-extrabold transition"
          >
            {actionLabel}
          </button>
        )}
        <button
          type="button"
          onClick={handleDismiss}
          aria-label="Dismiss tip"
          title="Dismiss tip"
          className="p-1.5 rounded-lg hover:bg-white/80 text-[#202943]/60 hover:text-[#101B35] transition"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
