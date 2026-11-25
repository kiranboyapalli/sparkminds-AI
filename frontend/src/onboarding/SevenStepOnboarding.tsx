import React from 'react';
import {
    CheckCircle2,
    ArrowLeft,
    ArrowRight,
    Sparkles,
    Edit3,
    PlusCircle,
    ShieldCheck,
} from 'lucide-react';
import {
    ALL_23_INDIAN_LANGUAGES,
    INDIAN_STATES_LIST,
    STEP5_14_CHALLENGES,
    STEP6_9_GOALS,
    getSubjectsForGradeAndBoardFrontend,
} from '../curriculum/curriculumData';
import { GradeNumber } from '../design-system/tokens';

export interface OnboardingState {
    studentId: string;
    studentName: string;
    age: number;
    grade: GradeNumber;
    board: 'CBSE' | 'ICSE' | 'STATE' | 'OTHER';
    stateName: string;
    otherBoardText: string;
    schoolMedium: string;
    preferredExplanationLanguage: string;
    secondaryExplanationLanguage: string;
    interfaceDisplayLanguage: string;
    selectedSubjects: string[];
    showOtherSubjectInput: boolean;
    otherSubjectText: string;
    helpWithAllSubjects: boolean;
    subjectsToImprove: string[];
    subjectConfidence: Record<string, 'Strong' | 'Okay' | 'Need help' | 'Difficult'>;
    difficultTopicsBySubject: Record<string, string[]>;
    mainImprovementPriority: string;
    selectedChallenges: string[];
    showOtherChallengeInput: boolean;
    otherChallengeText: string;
    whenNeedMostHelp: string[];
    challengeFrequency: 'Almost every day' | 'Often' | 'Sometimes' | 'Rarely';
    everythingGoalSelected: boolean;
    selectedGoals: string[];
    primaryGoal: string;
}

interface SevenStepOnboardingProps {
    onboarding: OnboardingState;
    setOnboarding: React.Dispatch<React.SetStateAction<OnboardingState>>;
    onComplete: (cloudSyncBundle?: any) => void;
}

export const SevenStepOnboarding: React.FC<SevenStepOnboardingProps> = ({
    onboarding,
    setOnboarding,
    onComplete,
}) => {
    const [step, setStep] = React.useState<number>(1);
    const [saveBanner, setSaveBanner] = React.useState<string>('Auto-saved');
    const [isSubmitting, setIsSubmitting] = React.useState<boolean>(false);
    const [submitError, setSubmitError] = React.useState<string | null>(null);

    React.useEffect(() => {
        setStep(1);
        setSubmitError(null);
        setIsSubmitting(false);
    }, [onboarding.studentId]);

    const availableSubjects = React.useMemo(
        () =>
            getSubjectsForGradeAndBoardFrontend(
                onboarding.grade,
                onboarding.board,
                onboarding.stateName
            ),
        [onboarding.grade, onboarding.board, onboarding.stateName]
    );

    // Keep selectedSubjects, subjectsToImprove, and subjectConfidence strictly synchronized
    // whenever grade, board, or state changes so stale cross-grade/board codes never cause 422 errors.
    React.useEffect(() => {
        const validCodes = availableSubjects.map((s) => s.code);
        if (validCodes.length === 0) return;

        setOnboarding((prev) => {
            const validSelected = prev.selectedSubjects.filter((c) => validCodes.includes(c));
            const nextSelected =
                validSelected.length > 0
                    ? validSelected
                    : validCodes.slice(0, Math.min(4, validCodes.length));

            const validImprove = prev.subjectsToImprove.filter((c) => nextSelected.includes(c));
            const nextImprove = prev.helpWithAllSubjects
                ? [...nextSelected]
                : validImprove.length > 0
                  ? validImprove
                  : nextSelected.slice(0, Math.min(2, nextSelected.length));

            const nextConf: Record<string, 'Strong' | 'Okay' | 'Need help' | 'Difficult'> = {};
            let confChanged =
                Object.keys(prev.subjectConfidence || {}).length !== nextSelected.length;
            nextSelected.forEach((c, idx) => {
                const existing = prev.subjectConfidence?.[c];
                nextConf[c] = existing || (idx === 0 ? 'Need help' : 'Okay');
                if (prev.subjectConfidence?.[c] !== nextConf[c]) {
                    confChanged = true;
                }
            });

            const selectedSame =
                nextSelected.length === prev.selectedSubjects.length &&
                nextSelected.every((c, i) => c === prev.selectedSubjects[i]);
            const improveSame =
                nextImprove.length === prev.subjectsToImprove.length &&
                nextImprove.every((c, i) => c === prev.subjectsToImprove[i]);

            if (selectedSame && improveSame && !confChanged) {
                return prev;
            }
            return {
                ...prev,
                selectedSubjects: nextSelected,
                subjectsToImprove: nextImprove,
                subjectConfidence: nextConf,
            };
        });
    }, [availableSubjects, setOnboarding]);

    const triggerAutoSave = (label: string) => {
        setSaveBanner(`Auto-saved: ${label}`);
    };

    // Toggle Step 6 "Everything" synchronization rule (Section 7 Step 6)
    const handleToggleEverythingGoal = () => {
        setOnboarding((prev) => {
            const nextEverything = !prev.everythingGoalSelected;
            const allIds = STEP6_9_GOALS.map((g) => g.id);
            triggerAutoSave('Learning Goals');
            return {
                ...prev,
                everythingGoalSelected: nextEverything,
                selectedGoals: nextEverything ? allIds : ['g1'],
            };
        });
    };

    const handleToggleSingleGoal = (goalId: string) => {
        setOnboarding((prev) => {
            const exists = prev.selectedGoals.includes(goalId);
            const nextGoals = exists
                ? prev.selectedGoals.filter((id) => id !== goalId)
                : [...prev.selectedGoals, goalId];
            const allSelected = nextGoals.length === STEP6_9_GOALS.length;
            triggerAutoSave('Learning Goals');
            return {
                ...prev,
                selectedGoals: nextGoals,
                everythingGoalSelected: allSelected,
            };
        });
    };

    // Validation preventing progression when mandatory selections are missing
    const canProceedCurrentStep = (): boolean => {
        if (step === 1) {
            if (!onboarding.preferredExplanationLanguage) return false;
            if (!onboarding.schoolMedium) return false;
            if (onboarding.board === 'STATE' && !onboarding.stateName) return false;
            return true;
        }
        if (step === 2) return onboarding.selectedSubjects.length > 0;
        if (step === 3) return onboarding.subjectsToImprove.length > 0;
        if (step === 4) return onboarding.selectedSubjects.length > 0;
        if (step === 5)
            return (
                onboarding.selectedChallenges.length > 0 &&
                onboarding.whenNeedMostHelp.length > 0
            );
        if (step === 6) return onboarding.selectedGoals.length > 0;
        return true;
    };

    return (
        <div className="eduspark-card rounded-3xl p-6 md:p-8 space-y-6 relative overflow-hidden animate-fade-in">
            {/* Clean SparkMinds Navy + Cyan Accent Bar */}
            <div className="absolute top-0 inset-x-0 h-1.5 bg-[#101B35]" />

            {/* Progress Bar & Step Indicator */}
            <div className="space-y-4 pb-5 border-b border-slate-100">
                <div className="flex flex-wrap items-center justify-between gap-4">
                    <div>
                        <div className="flex flex-wrap items-center gap-2">
                            <span className="text-xs font-extrabold uppercase tracking-wider px-3 py-1 rounded-full bg-[#101B35] text-[#35D6E8]">
                                Step {step} of 7
                            </span>
                            <span className="text-xs font-bold text-emerald-800 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full">
                                ✓ {saveBanner}
                            </span>
                        </div>
                        <h2 className="text-xl md:text-2xl font-extrabold text-[#101B35] mt-2 tracking-tight">
                            {step === 1 && "Welcome! Let's personalize your learning."}
                            {step === 2 && 'Now, choose your subjects.'}
                            {step === 3 && 'Which subjects would you like extra help with?'}
                            {step === 4 && 'How confident do you feel in each subject?'}
                            {step === 5 && 'Where do you usually need the most help?'}
                            {step === 6 && 'What are your learning goals?'}
                            {step === 7 && "Great job! You're ready to start."}
                        </h2>
                    </div>

                    <div className="flex items-center gap-1.5">
                        {[1, 2, 3, 4, 5, 6, 7].map((s) => (
                            <button
                                key={s}
                                type="button"
                                onClick={() => {
                                    if (s > step && !canProceedCurrentStep()) return;
                                    setSubmitError(null);
                                    setStep(s);
                                }}
                                className={`w-9 h-9 rounded-xl text-xs font-extrabold transition-all duration-200 ${step === s
                                    ? 'bg-[#101B35] text-[#35D6E8] shadow-sm scale-105'
                                    : s < step
                                        ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                                    }`}
                            >
                                {s < step ? '✓' : s}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Smooth Visual Step Progress Bar */}
                <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden">
                    <div
                        className="h-full rounded-full bg-[#5146E5] transition-all duration-300"
                        style={{ width: `${(step / 7) * 100}%` }}
                    />
                </div>
            </div>

            {/* STEP 1: ABOUT YOU */}
            {step === 1 && (
                <div className="space-y-6">
                    <div className="p-5 rounded-2xl bg-gradient-to-r from-blue-50 via-indigo-50/70 to-violet-50 border border-blue-200/80 flex flex-wrap items-center justify-between gap-3 shadow-sm">
                        <div className="flex items-center gap-3.5">
                            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#2563EB] to-[#7C3AED] text-white font-extrabold text-lg flex items-center justify-center shadow-md">
                                {onboarding.studentName.charAt(0)}
                            </div>
                            <div>
                                <span className="text-xs font-extrabold uppercase tracking-wider text-blue-700">
                                    Active Student Profile • Guided Card Selection
                                </span>
                                <div className="text-lg font-extrabold text-slate-900">
                                    {onboarding.studentName}
                                </div>
                            </div>
                        </div>
                        <span className="text-xs font-extrabold px-3.5 py-1.5 rounded-full bg-white text-indigo-800 border border-indigo-200 shadow-sm">
                            ✨ Interactive Selection Cards
                        </span>
                    </div>

                    {/* Age Selection */}
                    <div>
                        <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                            <label className="block text-sm font-extrabold text-slate-800">
                                1. Select or Enter Your Age
                            </label>
                            <div className="flex items-center gap-2">
                                <span className="text-xs text-slate-600 font-semibold">Exact Age:</span>
                                <input
                                    type="number"
                                    min={4}
                                    max={20}
                                    value={onboarding.age}
                                    onChange={(e) => {
                                        const raw = e.target.value;
                                        if (raw === '') {
                                            setOnboarding((p) => ({ ...p, age: 0 }));
                                            return;
                                        }
                                        const val = parseInt(raw, 10);
                                        if (!isNaN(val)) {
                                            setOnboarding((p) => ({ ...p, age: val }));
                                            if (val >= 4 && val <= 20) {
                                                triggerAutoSave(`Age ${val}`);
                                            }
                                        }
                                    }}
                                    onBlur={() => {
                                        const safe = Math.max(4, Math.min(20, onboarding.age || 12));
                                        setOnboarding((p) => ({ ...p, age: safe }));
                                        triggerAutoSave(`Age ${safe}`);
                                    }}
                                    className="w-20 px-2.5 py-1 text-sm font-bold rounded-lg border border-slate-300 text-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    placeholder="Age"
                                    title="Enter student age in years"
                                />
                                <span className="text-xs font-bold text-slate-500">years</span>
                            </div>
                        </div>
                        <div className="grid grid-cols-5 sm:grid-cols-7 md:grid-cols-15 gap-2">
                            {[4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18].map((ageVal) => (
                                <button
                                    key={ageVal}
                                    type="button"
                                    onClick={() => {
                                        setOnboarding((p) => ({ ...p, age: ageVal }));
                                        triggerAutoSave(`Age ${ageVal}`);
                                    }}
                                    className={`py-2.5 px-2 rounded-xl border text-xs font-bold transition ${onboarding.age === ageVal
                                        ? 'border-2 border-[#2563EB] bg-blue-50 text-[#2563EB]'
                                        : 'border-slate-200 hover:border-blue-300 text-slate-700'
                                        }`}
                                >
                                    {ageVal} yrs
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Grade Selection */}
                    <div>
                        <label className="block text-sm font-extrabold text-slate-800 mb-2">
                            2. Select Your Current Grade (Grade 1 to Grade 12)
                        </label>
                        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-2.5">
                            {([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] as GradeNumber[]).map((g) => (
                                <button
                                    key={g}
                                    type="button"
                                    onClick={() => {
                                        setOnboarding((p) => ({ ...p, grade: g }));
                                        triggerAutoSave(`Grade ${g}`);
                                    }}
                                    className={`p-3 rounded-2xl border text-left transition ${onboarding.grade === g
                                        ? 'border-2 border-[#2563EB] bg-blue-50 text-[#2563EB] font-extrabold'
                                        : 'border-slate-200 hover:border-blue-300 text-slate-700 font-semibold'
                                        }`}
                                >
                                    <div className="text-xs opacity-75">Class</div>
                                    <div className="text-sm font-extrabold">Grade {g}</div>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* School Board Selection */}
                    <div>
                        <label className="block text-sm font-extrabold text-slate-800 mb-2">
                            3. Select Your Indian School Board
                        </label>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                            {(
                                [
                                    { id: 'CBSE', label: 'CBSE', sub: 'Central Board' },
                                    { id: 'ICSE', label: 'ICSE / ISC', sub: 'CISCE Board' },
                                    { id: 'STATE', label: 'State Board', sub: 'Select Indian State' },
                                    { id: 'OTHER', label: 'Other Board', sub: 'IB / IGCSE / NIOS' },
                                ] as const
                            ).map((b) => (
                                <button
                                    key={b.id}
                                    type="button"
                                    onClick={() => {
                                        setOnboarding((p) => ({ ...p, board: b.id }));
                                        triggerAutoSave(`Board ${b.label}`);
                                    }}
                                    className={`p-3.5 rounded-2xl border text-left transition ${onboarding.board === b.id
                                        ? 'border-2 border-[#2563EB] bg-blue-50 text-[#2563EB]'
                                        : 'border-slate-200 hover:border-blue-300'
                                        }`}
                                >
                                    <div className="font-extrabold text-sm">{b.label}</div>
                                    <div className="text-xs text-slate-500">{b.sub}</div>
                                </button>
                            ))}
                        </div>

                        {onboarding.board === 'STATE' && (
                            <div className="mt-3 p-4 rounded-2xl bg-slate-50 border border-slate-200">
                                <label className="block text-xs font-extrabold text-slate-700 mb-2">
                                    Select Your State (State-Wise Curriculum Configuration):
                                </label>
                                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                                    {INDIAN_STATES_LIST.map((st) => (
                                        <button
                                            key={st}
                                            type="button"
                                            onClick={() => {
                                                setOnboarding((p) => ({ ...p, stateName: st }));
                                                triggerAutoSave(`State ${st}`);
                                            }}
                                            className={`p-2 rounded-xl border text-xs font-bold transition ${onboarding.stateName === st
                                                ? 'border-2 border-[#2563EB] bg-blue-50 text-[#2563EB]'
                                                : 'border-slate-200 bg-white'
                                                }`}
                                        >
                                            {st}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* School Medium of Instruction (Stored Separately) */}
                    <div>
                        <label className="block text-sm font-extrabold text-slate-800 mb-1">
                            4. School Medium of Instruction (Stored Separately from Explanation Language)
                        </label>
                        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-2">
                            {[
                                'English',
                                'Telugu',
                                'Hindi',
                                'Tamil',
                                'Kannada',
                                'Malayalam',
                                'Marathi',
                                'Bengali',
                                'Gujarati',
                                'Punjabi',
                                'Odia',
                                'Urdu',
                            ].map((med) => (
                                <button
                                    key={med}
                                    type="button"
                                    onClick={() => {
                                        setOnboarding((p) => ({ ...p, schoolMedium: med }));
                                        triggerAutoSave(`Medium: ${med}`);
                                    }}
                                    className={`p-2.5 rounded-xl border text-xs font-bold transition ${onboarding.schoolMedium === med
                                        ? 'border-2 border-[#2563EB] bg-blue-50 text-[#2563EB]'
                                        : 'border-slate-200 hover:border-blue-300'
                                        }`}
                                >
                                    {med} Medium
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Mandatory Preferred Explanation Language */}
                    <div className="p-4 rounded-2xl border-2 border-violet-300 bg-violet-50/50 space-y-4">
                        <div>
                            <span className="text-xs font-extrabold uppercase tracking-wider text-violet-700">
                                Multilingual Learning • 22 Scheduled Indian Languages + English
                            </span>
                            <h3 className="text-base font-extrabold text-slate-900 mt-0.5">
                                "Which language would you like SparkMinds AI to use when explaining your lessons?"
                            </h3>
                        </div>

                        <div>
                            <label className="block text-xs font-bold text-slate-700 mb-2">
                                Primary Explanation Language (Required):
                            </label>
                            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-2">
                                {ALL_23_INDIAN_LANGUAGES.map((lang) => (
                                    <button
                                        key={lang.code}
                                        type="button"
                                        onClick={() => {
                                            setOnboarding((p) => ({
                                                ...p,
                                                preferredExplanationLanguage: lang.name,
                                            }));
                                            triggerAutoSave(`Explain in ${lang.name}`);
                                        }}
                                        className={`p-2.5 rounded-xl border text-left text-xs transition ${onboarding.preferredExplanationLanguage === lang.name
                                            ? 'border-2 border-[#7C3AED] bg-violet-100 text-violet-950 font-extrabold'
                                            : 'border-slate-200 bg-white hover:border-violet-300'
                                            }`}
                                    >
                                        <div className="font-bold">{lang.name}</div>
                                        <div className="text-slate-500">{lang.nativeName}</div>
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs font-bold text-slate-700 mb-2">
                                Optional Secondary Language for Bilingual Explanations (e.g., Telugu + English):
                            </label>
                            <div className="flex flex-wrap gap-2">
                                {['None (Single Language)', 'English', 'Telugu', 'Hindi', 'Tamil', 'Kannada'].map(
                                    (sec) => {
                                        const val = sec === 'None (Single Language)' ? '' : sec;
                                        return (
                                            <button
                                                key={sec}
                                                type="button"
                                                onClick={() => {
                                                    setOnboarding((p) => ({
                                                        ...p,
                                                        secondaryExplanationLanguage: val,
                                                    }));
                                                    triggerAutoSave('Bilingual Preference');
                                                }}
                                                className={`px-3 py-1.5 rounded-xl border text-xs font-bold transition ${onboarding.secondaryExplanationLanguage === val
                                                    ? 'border-2 border-[#2563EB] bg-blue-50 text-[#2563EB]'
                                                    : 'border-slate-200 bg-white'
                                                    }`}
                                            >
                                                {sec}
                                            </button>
                                        );
                                    }
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* STEP 2: SELECT YOUR SUBJECTS */}
            {step === 2 && (
                <div className="space-y-4">
                    <p className="text-xs text-slate-600">
                        Showing dynamic curriculum subjects configured for{' '}
                        <strong>
                            Grade {onboarding.grade} • {onboarding.board}
                            {onboarding.board === 'STATE' ? ` (${onboarding.stateName})` : ''}
                        </strong>
                        . Select all subjects you study at school:
                    </p>
                    <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3">
                        {availableSubjects.map((sub) => {
                            const isSelected = onboarding.selectedSubjects.includes(sub.code);
                            return (
                                <button
                                    key={sub.code}
                                    type="button"
                                    onClick={() => {
                                        setOnboarding((prev) => {
                                            const next = isSelected
                                                ? prev.selectedSubjects.filter((c) => c !== sub.code)
                                                : [...prev.selectedSubjects, sub.code];
                                            return {
                                                ...prev,
                                                selectedSubjects: next,
                                                subjectsToImprove: prev.helpWithAllSubjects
                                                    ? next
                                                    : prev.subjectsToImprove.filter((c) => next.includes(c)),
                                            };
                                        });
                                        triggerAutoSave(sub.name);
                                    }}
                                    className={`p-4 rounded-2xl border text-left transition ${isSelected
                                        ? 'border-2 border-[#2563EB] bg-blue-50/70'
                                        : 'border-slate-200 hover:border-blue-300'
                                        }`}
                                >
                                    <div className="flex items-center justify-between">
                                        <span className="font-extrabold text-sm text-slate-900">{sub.name}</span>
                                        {isSelected && <CheckCircle2 className="w-4 h-4 text-[#2563EB]" />}
                                    </div>
                                    <p className="text-xs text-slate-500 mt-1">
                                        Topics: {sub.topics.slice(0, 3).join(', ')}
                                    </p>
                                </button>
                            );
                        })}

                        {/* Optional Other Subject Card (Rule 6.2 Free-Text Exception) */}
                        <button
                            type="button"
                            onClick={() =>
                                setOnboarding((p) => ({
                                    ...p,
                                    showOtherSubjectInput: !p.showOtherSubjectInput,
                                }))
                            }
                            className="p-4 rounded-2xl border border-dashed border-slate-300 text-left flex items-center gap-2 text-xs font-bold text-slate-600 hover:border-blue-400"
                        >
                            <PlusCircle className="w-4 h-4 text-blue-600" />
                            <span>Other Subject (Optional)</span>
                        </button>
                    </div>

                    {onboarding.showOtherSubjectInput && (
                        <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 max-w-md">
                            <label className="block text-xs font-bold text-slate-700 mb-1">
                                Optional: Enter additional subject name (only shown because "Other" was selected):
                            </label>
                            <input
                                type="text"
                                value={onboarding.otherSubjectText}
                                onChange={(e) =>
                                    setOnboarding((p) => ({ ...p, otherSubjectText: e.target.value }))
                                }
                                placeholder="Custom Subject Name"
                                className="w-full rounded-lg border border-slate-300 px-3 py-1.5 text-xs"
                            />
                        </div>
                    )}
                </div>
            )}

            {/* STEP 3: SELECT SUBJECTS TO IMPROVE */}
            {step === 3 && (
                <div className="space-y-4">
                    <button
                        type="button"
                        onClick={() => {
                            setOnboarding((prev) => {
                                const nextAll = !prev.helpWithAllSubjects;
                                return {
                                    ...prev,
                                    helpWithAllSubjects: nextAll,
                                    subjectsToImprove: nextAll
                                        ? [...prev.selectedSubjects]
                                        : prev.selectedSubjects.slice(0, 1),
                                };
                            });
                            triggerAutoSave('Help with all subjects toggle');
                        }}
                        className={`w-full p-4 rounded-2xl border text-left flex items-center justify-between transition ${onboarding.helpWithAllSubjects
                            ? 'border-2 border-amber-500 bg-amber-50'
                            : 'border-slate-200 hover:border-amber-400'
                            }`}
                    >
                        <div>
                            <div className="font-extrabold text-sm text-slate-900">
                                ✨ "I want help with all my subjects."
                            </div>
                            <div className="text-xs text-slate-600">
                                Automatically selects all subjects you chose in Step 2.
                            </div>
                        </div>
                        <span className="px-3 py-1 rounded-full text-xs font-extrabold bg-amber-400 text-slate-950">
                            {onboarding.helpWithAllSubjects ? 'Selected ✓' : 'Select All'}
                        </span>
                    </button>

                    <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3">
                        {availableSubjects
                            .filter((s) => onboarding.selectedSubjects.includes(s.code))
                            .map((sub) => {
                                const isImp = onboarding.subjectsToImprove.includes(sub.code);
                                return (
                                    <button
                                        key={sub.code}
                                        type="button"
                                        onClick={() => {
                                            setOnboarding((prev) => {
                                                const next = isImp
                                                    ? prev.subjectsToImprove.filter((c) => c !== sub.code)
                                                    : [...prev.subjectsToImprove, sub.code];
                                                return {
                                                    ...prev,
                                                    subjectsToImprove: next,
                                                    helpWithAllSubjects:
                                                        next.length === prev.selectedSubjects.length,
                                                };
                                            });
                                        }}
                                        className={`p-4 rounded-2xl border text-left transition ${isImp
                                            ? 'border-2 border-[#2563EB] bg-blue-50'
                                            : 'border-slate-200'
                                            }`}
                                    >
                                        <div className="font-extrabold text-sm">{sub.name}</div>
                                        <div className="text-xs text-blue-700 font-semibold mt-1">
                                            {isImp ? 'Targeted for Improvement ✓' : 'Click to include'}
                                        </div>
                                    </button>
                                );
                            })}
                    </div>
                </div>
            )}

            {/* STEP 4: LEARNING STRENGTHS & WEAKNESSES */}
            {step === 4 && (
                <div className="space-y-4">
                    <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 font-medium">
                        <strong>Self-Reported Confidence Note:</strong> Your confidence selections help SparkMinds AI tailor your study plan and explanations, and are tracked separately from your school and practice test scores.
                    </div>

                    <div className="space-y-3">
                        {availableSubjects
                            .filter((s) => onboarding.selectedSubjects.includes(s.code))
                            .map((sub) => {
                                const currentLevel =
                                    onboarding.subjectConfidence[sub.code] || 'Okay';
                                return (
                                    <div
                                        key={sub.code}
                                        className="p-4 rounded-2xl border border-slate-200 space-y-2.5"
                                    >
                                        <div className="font-extrabold text-sm text-slate-900">
                                            How confident do you feel in {sub.name}?
                                        </div>
                                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                                            {(['Strong', 'Okay', 'Need help', 'Difficult'] as const).map(
                                                (lvl) => (
                                                    <button
                                                        key={lvl}
                                                        type="button"
                                                        onClick={() => {
                                                            setOnboarding((prev) => ({
                                                                ...prev,
                                                                subjectConfidence: {
                                                                    ...prev.subjectConfidence,
                                                                    [sub.code]: lvl,
                                                                },
                                                            }));
                                                            triggerAutoSave(`${sub.name}: ${lvl}`);
                                                        }}
                                                        className={`py-2 px-3 rounded-xl border text-xs font-bold transition ${currentLevel === lvl
                                                            ? 'border-2 border-[#2563EB] bg-blue-50 text-[#2563EB]'
                                                            : 'border-slate-200'
                                                            }`}
                                                    >
                                                        {lvl}
                                                    </button>
                                                )
                                            )}
                                        </div>
                                    </div>
                                );
                            })}
                    </div>
                </div>
            )}

            {/* STEP 5: LEARNING CHALLENGES (14 Exact Challenges) */}
            {step === 5 && (
                <div className="space-y-5">
                    <div>
                        <label className="block text-sm font-extrabold text-slate-900 mb-2">
                            1. What challenges do you face while studying? (Select all that apply)
                        </label>
                        <div className="grid sm:grid-cols-2 gap-2.5">
                            {STEP5_14_CHALLENGES.map((ch, idx) => {
                                const isSel = onboarding.selectedChallenges.includes(ch);
                                return (
                                    <button
                                        key={ch}
                                        type="button"
                                        onClick={() => {
                                            setOnboarding((prev) => ({
                                                ...prev,
                                                selectedChallenges: isSel
                                                    ? prev.selectedChallenges.filter((x) => x !== ch)
                                                    : [...prev.selectedChallenges, ch],
                                            }));
                                            triggerAutoSave('Study Challenges');
                                        }}
                                        className={`p-3 rounded-xl border text-left text-xs font-semibold transition ${isSel
                                            ? 'border-2 border-[#2563EB] bg-blue-50 text-[#2563EB] font-bold'
                                            : 'border-slate-200 hover:border-blue-300'
                                            }`}
                                    >
                                        {idx + 1}. {ch} {isSel ? '✓' : ''}
                                    </button>
                                );
                            })}
                        </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-xs font-extrabold text-slate-800 mb-2">
                                2. When do you need the most help? (Multi-Select)
                            </label>
                            <div className="grid grid-cols-2 gap-2">
                                {[
                                    'Before starting homework',
                                    'While understanding concepts',
                                    'While solving questions',
                                    'During revision',
                                    'Before examinations',
                                    'During school projects',
                                ].map((wh) => {
                                    const isSel = onboarding.whenNeedMostHelp.includes(wh);
                                    return (
                                        <button
                                            key={wh}
                                            type="button"
                                            onClick={() =>
                                                setOnboarding((p) => ({
                                                    ...p,
                                                    whenNeedMostHelp: isSel
                                                        ? p.whenNeedMostHelp.filter((x) => x !== wh)
                                                        : [...p.whenNeedMostHelp, wh],
                                                }))
                                            }
                                            className={`p-2.5 rounded-xl border text-xs font-bold ${isSel
                                                ? 'border-2 border-[#2563EB] bg-blue-50 text-[#2563EB]'
                                                : 'border-slate-200'
                                                }`}
                                        >
                                            {wh}
                                        </button>
                                    );
                                })}
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs font-extrabold text-slate-800 mb-2">
                                3. How often do you face these challenges? (Single-Choice)
                            </label>
                            <div className="grid grid-cols-2 gap-2">
                                {(['Almost every day', 'Often', 'Sometimes', 'Rarely'] as const).map(
                                    (freq) => (
                                        <button
                                            key={freq}
                                            type="button"
                                            onClick={() =>
                                                setOnboarding((p) => ({ ...p, challengeFrequency: freq }))
                                            }
                                            className={`p-2.5 rounded-xl border text-xs font-bold ${onboarding.challengeFrequency === freq
                                                ? 'border-2 border-[#2563EB] bg-blue-50 text-[#2563EB]'
                                                : 'border-slate-200'
                                                }`}
                                        >
                                            {freq}
                                        </button>
                                    )
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* STEP 6: LEARNING GOALS & SPECIAL EVERYTHING OPTION */}
            {step === 6 && (
                <div className="space-y-4">
                    <button
                        type="button"
                        onClick={handleToggleEverythingGoal}
                        className={`w-full p-5 rounded-2xl border-2 text-left flex flex-wrap items-center justify-between gap-3 transition ${onboarding.everythingGoalSelected
                            ? 'border-amber-500 bg-amber-50/80'
                            : 'border-slate-200 hover:border-amber-400'
                            }`}
                    >
                        <div>
                            <div className="flex items-center gap-2">
                                <Sparkles className="w-5 h-5 text-amber-600" />
                                <span className="font-extrabold text-base text-slate-900">
                                    Everything — "I want SparkMinds AI to help me improve in all areas."
                                </span>
                            </div>
                            <p className="text-xs text-slate-600 mt-1">
                                Selecting Everything automatically selects all 9 goals below. Deselecting any single goal automatically unselects Everything.
                            </p>
                        </div>
                        <span className="px-3.5 py-1.5 rounded-full text-xs font-extrabold bg-amber-400 text-slate-950">
                            {onboarding.everythingGoalSelected
                                ? 'EVERYTHING SELECTED ✓'
                                : `${onboarding.selectedGoals.length} of 9 Selected`}
                        </span>
                    </button>

                    <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3">
                        {STEP6_9_GOALS.map((g, index) => {
                            const isSel = onboarding.selectedGoals.includes(g.id);
                            return (
                                <button
                                    key={g.id}
                                    type="button"
                                    onClick={() => handleToggleSingleGoal(g.id)}
                                    className={`p-3.5 rounded-2xl border text-left text-xs font-bold transition ${isSel
                                        ? 'border-2 border-[#2563EB] bg-blue-50 text-[#2563EB]'
                                        : 'border-slate-200 hover:border-blue-300'
                                        }`}
                                >
                                    {index + 1}. {g.label} {isSel ? '✓' : ''}
                                </button>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* STEP 7: AUTO-GENERATED PERSONAL LEARNING PROFILE */}
            {step === 7 && (
                <div className="space-y-5">
                    <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-center justify-between">
                        <div className="flex items-center gap-2.5">
                            <ShieldCheck className="w-5 h-5 text-emerald-700" />
                            <div>
                                <div className="font-extrabold text-sm text-emerald-950">
                                    Personal Learning Profile Generated Automatically
                                </div>
                                <div className="text-xs text-emerald-800">
                                    Every section below has a quick Edit button. Self-reported strengths are clearly separated from verified diagnostic mastery.
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4 text-xs">
                        <div className="p-4 rounded-2xl border border-slate-200 space-y-1.5">
                            <div className="flex justify-between items-center">
                                <span className="font-extrabold text-blue-600 uppercase">
                                    1. Student & Curriculum
                                </span>
                                <button
                                    onClick={() => setStep(1)}
                                    className="inline-flex items-center gap-1 text-blue-600 font-bold"
                                >
                                    <Edit3 className="w-3.5 h-3.5" /> Edit
                                </button>
                            </div>
                            <div>
                                <strong>Name:</strong> {onboarding.studentName} (Age {onboarding.age})
                            </div>
                            <div>
                                <strong>Grade & Board:</strong> Grade {onboarding.grade} • {onboarding.board}{' '}
                                {onboarding.board === 'STATE' ? `(${onboarding.stateName})` : ''}
                            </div>
                            <div>
                                <strong>4 Separate Language Settings:</strong>
                                <ul className="list-disc list-inside mt-1 text-slate-600">
                                    <li>School Medium: <strong>{onboarding.schoolMedium}</strong></li>
                                    <li>Preferred Explanation: <strong>{onboarding.preferredExplanationLanguage}</strong></li>
                                    <li>Secondary Bilingual: <strong>{onboarding.secondaryExplanationLanguage || 'None'}</strong></li>
                                    <li>Interface Display: <strong>{onboarding.interfaceDisplayLanguage}</strong></li>
                                </ul>
                            </div>
                        </div>

                        <div className="p-4 rounded-2xl border border-slate-200 space-y-1.5">
                            <div className="flex justify-between items-center">
                                <span className="font-extrabold text-violet-600 uppercase">
                                    2. Subjects & Improvement Priorities
                                </span>
                                <button
                                    onClick={() => setStep(2)}
                                    className="inline-flex items-center gap-1 text-blue-600 font-bold"
                                >
                                    <Edit3 className="w-3.5 h-3.5" /> Edit
                                </button>
                            </div>
                            <div>
                                <strong>Subjects Studied ({onboarding.selectedSubjects.length}):</strong>{' '}
                                {onboarding.selectedSubjects.join(', ')}
                            </div>
                            <div>
                                <strong>Subjects to Improve ({onboarding.subjectsToImprove.length}):</strong>{' '}
                                {onboarding.subjectsToImprove.join(', ')}
                            </div>
                            <div>
                                <strong>Learning Goals:</strong>{' '}
                                {onboarding.everythingGoalSelected
                                    ? '🌟 Everything (All 9 Areas Selected)'
                                    : `${onboarding.selectedGoals.length} Goals Selected`}
                            </div>
                            <div className="pt-1 text-amber-800 font-semibold">
                                Recommended First Action: Take a 3-question diagnostic check with the AI Learning Buddy in{' '}
                                {onboarding.preferredExplanationLanguage}.
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {submitError && (
                <div
                    role="alert"
                    className="p-3.5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-extrabold"
                >
                    {submitError}
                </div>
            )}

            {/* Footer Navigation Buttons */}
            <div className="pt-5 border-t border-slate-100 flex items-center justify-between">
                <button
                    type="button"
                    disabled={step === 1 || isSubmitting}
                    onClick={() => {
                        setSubmitError(null);
                        setStep((s) => Math.max(1, s - 1));
                    }}
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-2xl border border-slate-200 bg-white hover:bg-slate-50 text-xs font-extrabold text-slate-700 disabled:opacity-40 transition-all shadow-sm"
                >
                    <ArrowLeft className="w-4 h-4" /> Previous Step
                </button>

                {step < 7 ? (
                    <button
                        type="button"
                        disabled={!canProceedCurrentStep()}
                        onClick={() => {
                            setSubmitError(null);
                            setStep((s) => Math.min(7, s + 1));
                        }}
                        className="inline-flex items-center gap-2 px-6 py-3 rounded-2xl bg-gradient-to-r from-[#2563EB] via-[#4F46E5] to-[#7C3AED] hover:opacity-95 text-white text-xs font-extrabold disabled:opacity-40 shadow-md shadow-blue-500/25 transition-all"
                    >
                        Continue to Step {step + 1} <ArrowRight className="w-4 h-4" />
                    </button>
                ) : (
                    <button
                        type="button"
                        disabled={isSubmitting}
                        onClick={async () => {
                            if (isSubmitting) return;
                            setSubmitError(null);
                            setIsSubmitting(true);
                            try {
                                const validCodes = availableSubjects.map((s) => s.code);
                                const cleanSelected = onboarding.selectedSubjects.filter((c) =>
                                    validCodes.includes(c)
                                );
                                const finalSelectedSubjects =
                                    cleanSelected.length > 0
                                        ? cleanSelected
                                        : validCodes.slice(0, Math.min(4, validCodes.length));
                                const cleanImprove = onboarding.subjectsToImprove.filter((c) =>
                                    finalSelectedSubjects.includes(c)
                                );
                                const finalSubjectsToImprove = onboarding.helpWithAllSubjects
                                    ? [...finalSelectedSubjects]
                                    : cleanImprove.length > 0
                                      ? cleanImprove
                                      : finalSelectedSubjects.slice(
                                            0,
                                            Math.min(2, finalSelectedSubjects.length)
                                        );
                                const safeAge = Math.max(4, Math.min(20, Number(onboarding.age) || 12));

                                const subjectConfidencePayload = finalSelectedSubjects.map((code) => {
                                    const found = availableSubjects.find((s) => s.code === code);
                                    return {
                                        subject_code: code,
                                        subject_name: found ? found.name : code,
                                        confidence_level: onboarding.subjectConfidence[code] || 'Okay',
                                        difficult_topics: onboarding.difficultTopicsBySubject[code] || [],
                                    };
                                });

                                const res = await fetch('/api/onboarding/submit', {
                                    method: 'POST',
                                    credentials: 'include',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({
                                        student_id: onboarding.studentId,
                                        academic_year_label: '2026-2027',
                                        step1: {
                                            age: safeAge,
                                            grade: onboarding.grade,
                                            school_board: onboarding.board,
                                            state_name:
                                                onboarding.board === 'STATE'
                                                    ? onboarding.stateName || 'Telangana'
                                                    : onboarding.stateName,
                                            other_board_name: onboarding.otherBoardText || null,
                                            school_medium: onboarding.schoolMedium || 'English',
                                            preferred_explanation_language:
                                                onboarding.preferredExplanationLanguage || 'English',
                                            secondary_explanation_language:
                                                onboarding.secondaryExplanationLanguage || null,
                                            interface_display_language:
                                                onboarding.interfaceDisplayLanguage || 'English',
                                        },
                                        selected_subjects: finalSelectedSubjects,
                                        other_subject_optional: onboarding.otherSubjectText || null,
                                        help_with_all_subjects: onboarding.helpWithAllSubjects,
                                        subjects_to_improve: finalSubjectsToImprove,
                                        subject_confidence: subjectConfidencePayload,
                                        main_improvement_priority:
                                            onboarding.mainImprovementPriority ||
                                            'Understand difficult concepts',
                                        learning_challenges:
                                            onboarding.selectedChallenges.length > 0
                                                ? onboarding.selectedChallenges
                                                : ["I don't understand some concepts."],
                                        other_challenge_optional: onboarding.otherChallengeText || null,
                                        when_need_most_help:
                                            onboarding.whenNeedMostHelp.length > 0
                                                ? onboarding.whenNeedMostHelp
                                                : ['While understanding concepts'],
                                        challenge_frequency: onboarding.challengeFrequency || 'Often',
                                        everything_goal_selected: onboarding.everythingGoalSelected,
                                        selected_goals:
                                            onboarding.selectedGoals.length > 0
                                                ? onboarding.selectedGoals
                                                : ['g1'],
                                        primary_goal: onboarding.primaryGoal || 'g1',
                                    }),
                                });

                                const data = await res.json().catch(() => null);
                                if (!res.ok) {
                                    const detail =
                                        typeof data?.detail === 'string'
                                            ? data.detail
                                            : 'Could not save your onboarding profile to the database. Please check your selections and try again.';
                                    setSubmitError(detail);
                                    setIsSubmitting(false);
                                    return;
                                }

                                const syncedBundle = data?.cloud_sync_bundle;
                                const confirmedCompleted = Boolean(
                                    data?.student?.onboarding_completed ||
                                        syncedBundle?.student?.onboarding_completed
                                );
                                if (!confirmedCompleted) {
                                    setSubmitError(
                                        'Your onboarding completion could not be confirmed by the server. Please try saving again.'
                                    );
                                    setIsSubmitting(false);
                                    return;
                                }

                                onComplete(syncedBundle);
                            } catch {
                                setSubmitError(
                                    'Unable to reach the server to save your onboarding profile. Please check your connection and try again.'
                                );
                            } finally {
                                setIsSubmitting(false);
                            }
                        }}
                        className="inline-flex items-center gap-2 px-7 py-3.5 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:opacity-95 disabled:opacity-60 text-white text-xs font-extrabold shadow-lg shadow-emerald-500/25 transition-all"
                    >
                        {isSubmitting
                            ? 'Saving Profile...'
                            : 'Save Profile & Launch Student Dashboard ✓'}
                    </button>
                )}
            </div>
        </div>
    );
};

