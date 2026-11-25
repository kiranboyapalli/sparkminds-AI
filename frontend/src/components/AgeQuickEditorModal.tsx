import React from 'react';

interface AgeQuickEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentAge: number;
  currentDob?: string;
  studentName?: string;
  onSaveAge: (age: number, dob: string) => Promise<boolean>;
  onGoToProfile: () => void;
}

export const AgeQuickEditorModal: React.FC<AgeQuickEditorModalProps> = ({
  isOpen,
  onClose,
  currentAge,
  currentDob = '',
  studentName = 'Student',
  onSaveAge,
  onGoToProfile,
}) => {
  const [selectedAge, setSelectedAge] = React.useState<number>(currentAge);
  const [selectedDob, setSelectedDob] = React.useState<string>(currentDob);
  const [isSaving, setIsSaving] = React.useState<boolean>(false);
  const [feedback, setFeedback] = React.useState<{ type: 'ok' | 'err'; text: string } | null>(null);

  // Sync state whenever modal opens or props update
  React.useEffect(() => {
    if (isOpen) {
      setSelectedAge(currentAge);
      if (currentDob) {
        setSelectedDob(currentDob);
      } else {
        const currentYear = new Date().getFullYear();
        setSelectedDob(`${currentYear - currentAge}-06-15`);
      }
      setFeedback(null);
    }
  }, [isOpen, currentAge, currentDob]);

  if (!isOpen) return null;

  const calculateDobFromAge = (age: number, existingDob?: string): string => {
    const today = new Date();
    const safeAge = Math.max(4, Math.min(20, age));
    const birthYear = today.getFullYear() - safeAge;
    let monthDay = '06-15';
    if (existingDob && existingDob.includes('-')) {
      const parts = existingDob.split('-');
      if (parts.length === 3 && parts[1] && parts[2]) {
        monthDay = `${parts[1]}-${parts[2]}`;
      }
    }
    return `${birthYear}-${monthDay}`;
  };

  const calculateAgeFromDobString = (dobString: string): number | null => {
    if (!dobString || !dobString.includes('-')) return null;
    const parts = dobString.split('-');
    if (parts.length !== 3) return null;
    const y = parseInt(parts[0], 10);
    const m = parseInt(parts[1], 10) - 1;
    const d = parseInt(parts[2], 10);
    if (isNaN(y) || isNaN(m) || isNaN(d)) return null;
    const today = new Date();
    let age = today.getFullYear() - y;
    const monthDiff = today.getMonth() - m;
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < d)) {
      age--;
    }
    return Math.max(4, Math.min(20, age));
  };

  const handleAgeChange = (newAge: number) => {
    const safeAge = Math.max(4, Math.min(20, newAge));
    setSelectedAge(safeAge);
    const newDob = calculateDobFromAge(safeAge, selectedDob);
    setSelectedDob(newDob);
  };

  const handleDobChange = (newDob: string) => {
    setSelectedDob(newDob);
    if (newDob) {
      const calcAge = calculateAgeFromDobString(newDob);
      if (calcAge !== null) {
        setSelectedAge(calcAge);
      }
    }
  };

  const handleSave = async () => {
    setFeedback(null);
    if (selectedAge < 4 || selectedAge > 20) {
      setFeedback({
        type: 'err',
        text: 'Please select an age between 4 and 20 years.',
      });
      return;
    }
    setIsSaving(true);
    try {
      const ok = await onSaveAge(selectedAge, selectedDob);
      if (ok) {
        setFeedback({
          type: 'ok',
          text: `✓ Age updated to ${selectedAge} years and saved to cloud database across all devices!`,
        });
        setTimeout(() => {
          onClose();
        }, 1200);
      } else {
        setFeedback({
          type: 'err',
          text: 'Unable to save age to cloud. Please try again.',
        });
      }
    } catch (err: any) {
      setFeedback({
        type: 'err',
        text: err?.message || 'Failed to save age update.',
      });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fade-in">
      <div
        className="fixed inset-0"
        onClick={() => {
          if (!isSaving) onClose();
        }}
      />
      <div className="relative w-full max-w-lg bg-white rounded-3xl p-6 sm:p-8 shadow-2xl border border-slate-200 z-10 space-y-5">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-slate-100 pb-3">
          <div>
            <span className="text-[10px] font-extrabold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
              Student Profile • Cloud Synchronised
            </span>
            <h3 className="text-xl font-extrabold text-slate-900 mt-1">
              Edit Student Age
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Updating age for <strong>{studentName}</strong>. Changes reflect across all modules and devices immediately.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            disabled={isSaving}
            className="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold flex items-center justify-center transition shrink-0"
            title="Close"
          >
            ✕
          </button>
        </div>

        {/* Feedback Message */}
        {feedback && (
          <div
            className={`p-3.5 rounded-2xl text-xs font-extrabold border ${
              feedback.type === 'ok'
                ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                : 'bg-rose-50 border-rose-200 text-rose-800'
            }`}
          >
            {feedback.text}
          </div>
        )}

        {/* Current vs Target Age Info */}
        <div className="flex items-center justify-between p-3 rounded-2xl bg-slate-50 border border-slate-200 text-xs">
          <span className="font-semibold text-slate-600">Current Saved Age:</span>
          <span className="font-extrabold text-blue-700 text-sm">
            {currentAge} years old
          </span>
        </div>

        {/* 1-Click Quick Select Pills */}
        <div className="space-y-2">
          <label className="block text-xs font-extrabold text-slate-800">
            1. Select Age (1-Click Selection):
          </label>
          <div className="grid grid-cols-5 sm:grid-cols-8 gap-1.5">
            {[4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18].map((a) => (
              <button
                key={a}
                type="button"
                onClick={() => handleAgeChange(a)}
                className={`py-2 rounded-xl text-xs font-extrabold transition ${
                  selectedAge === a
                    ? 'bg-blue-600 text-white shadow-sm ring-2 ring-blue-400'
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200'
                }`}
              >
                {a} yrs
              </button>
            ))}
          </div>
        </div>

        {/* Direct Exact Inputs */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
          <div className="space-y-1">
            <label className="block text-xs font-extrabold text-slate-800">
              Exact Age (Years):
            </label>
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={() => {
                  const next = Math.max(4, selectedAge - 1);
                  handleAgeChange(next);
                }}
                className="w-9 h-9 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 font-extrabold text-lg flex items-center justify-center border border-slate-300 transition shrink-0 cursor-pointer"
                title="Decrease age by 1 year"
              >
                −
              </button>
              <input
                type="number"
                min={4}
                max={20}
                value={selectedAge === 0 ? '' : selectedAge}
                onChange={(e) => {
                  const raw = e.target.value;
                  if (raw === '') {
                    setSelectedAge(0);
                    return;
                  }
                  const val = parseInt(raw, 10);
                  if (!isNaN(val)) {
                    setSelectedAge(val);
                    if (val >= 4 && val <= 20) {
                      setSelectedDob(calculateDobFromAge(val, selectedDob));
                    }
                  }
                }}
                onBlur={() => {
                  const safe = Math.max(4, Math.min(20, selectedAge || 12));
                  handleAgeChange(safe);
                }}
                className="w-full text-center rounded-xl border border-slate-300 bg-white px-3 py-1.5 text-sm font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
              <button
                type="button"
                onClick={() => {
                  const next = Math.min(20, selectedAge + 1);
                  handleAgeChange(next);
                }}
                className="w-9 h-9 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 font-extrabold text-lg flex items-center justify-center border border-slate-300 transition shrink-0 cursor-pointer"
                title="Increase age by 1 year"
              >
                +
              </button>
            </div>
            <p className="text-[10px] text-slate-500">Allowed range: 4 to 20 years. Use + / − buttons or type.</p>
          </div>

          <div className="space-y-1">
            <label className="block text-xs font-extrabold text-slate-800">
              Date of Birth: <span className="text-rose-600">*</span>
            </label>
            <input
              type="date"
              value={selectedDob}
              onChange={(e) => handleDobChange(e.target.value)}
              className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-sm font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
            <p className="text-[10px] text-slate-500">Auto-synchronized with age.</p>
          </div>
        </div>

        {/* Child Safety Protection Notice */}
        {selectedAge < 8 && (
          <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 font-bold">
            🛡️ Child Safety Protection Active: Students under 8 operate in parent-assisted mode.
          </div>
        )}

        {/* Footer Actions */}
        <div className="pt-2 flex items-center justify-between border-t border-slate-100 gap-3">
          <button
            type="button"
            onClick={() => {
              onClose();
              onGoToProfile();
            }}
            className="text-xs font-bold text-blue-600 hover:text-blue-800 hover:underline"
          >
            Manage Full Profile & Languages →
          </button>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              disabled={isSaving}
              className="px-4 py-2 rounded-xl border border-slate-300 hover:bg-slate-100 text-xs font-bold text-slate-700 transition"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSave}
              disabled={isSaving}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white text-xs font-extrabold shadow-sm transition disabled:opacity-50"
            >
              {isSaving ? 'Saving to Cloud...' : 'Save Updated Age ✓'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
