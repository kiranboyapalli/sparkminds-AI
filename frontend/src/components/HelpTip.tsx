import React from 'react';
import { HelpCircle, X } from 'lucide-react';

interface HelpTipProps {
  title: string;
  text: string;
  label?: string;
}

/**
 * Compact optional Help button styled in SparkMinds AI's Midnight/Indigo/Aqua palette.
 */
export const HelpTip: React.FC<HelpTipProps> = ({ title, text, label = 'Help' }) => {
  const [open, setOpen] = React.useState(false);

  return (
    <div className="relative inline-block">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-label={`Help: ${title}`}
        title={title}
        className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-xl border border-[#DCE2F5] bg-white hover:bg-[#EEEAFE] text-[11px] font-bold text-[#202943] hover:text-[#5146E5] transition min-h-[32px]"
      >
        <HelpCircle className="w-3.5 h-3.5 text-[#5146E5]" />
        <span>{label}</span>
      </button>

      {open && (
        <div
          role="dialog"
          aria-label={title}
          className="absolute right-0 mt-2 w-72 sm:w-80 rounded-2xl bg-white border border-[#DCE2F5] shadow-xl p-4 z-40 text-left animate-fade-in space-y-1.5"
        >
          <div className="flex items-center justify-between gap-2">
            <span className="text-xs font-extrabold text-[#101B35]">{title}</span>
            <button
              type="button"
              onClick={() => setOpen(false)}
              aria-label="Close help"
              className="p-1 rounded-lg hover:bg-[#EEEAFE] text-[#202943]/60"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
          <p className="text-xs text-[#202943]/80 leading-relaxed font-medium">{text}</p>
        </div>
      )}
    </div>
  );
};
