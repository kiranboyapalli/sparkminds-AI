/**
 * SparkMinds AI — Design System Tokens & Adaptive Grade-Band Experience Modes
 * Brand Identity:
 * - App Name: SparkMinds AI
 * - Tagline: Dream Beyond Limits. Learn With Fire. Lead With Power!
 * - Product Description: Your Intelligent Learning Buddy
 * - Global Colour Theme: Deep Midnight Blue (#101B35), Rich Indigo (#5146E5),
 *   Bright Aqua (#35D6E8), Soft Lavender (#EEEAFE), Clean White (#FFFFFF),
 *   Light Background (#F6F7FC), Dark Readable Text (#202943)
 * - Dashboard Bluish Palette: Main (#EAF0FF), Secondary (#DCE6FA), Card (#F7F9FF),
 *   Deep Navy Text (#172554), Indigo Accent (#4F46E5), Aqua Highlight (#35D6E8)
 */

export const BRAND_NAME = 'SparkMinds AI';
export const BRAND_TAGLINE = 'Dream Beyond Limits. Learn With Fire. Lead With Power!';
export const BRAND_TAGLINE_PARTS = {
  first: 'Dream Beyond Limits.',
  second: 'Learn With Fire.',
  third: 'Lead With Power!',
} as const;
export const BRAND_DESCRIPTION = 'Your Intelligent Learning Buddy';

export const BRAND_PALETTE = {
  midnightBlue: '#101B35',
  indigo: '#5146E5',
  aqua: '#35D6E8',
  softLavender: '#EEEAFE',
  white: '#FFFFFF',
  lightBg: '#F6F7FC',
  darkText: '#202943',
  dashboardBgMain: '#EAF0FF',
  dashboardBgSecondary: '#DCE6FA',
  dashboardCard: '#F7F9FF',
  dashboardNavyText: '#172554',
  dashboardIndigoAccent: '#4F46E5',
  dashboardAquaHighlight: '#35D6E8',
} as const;

export type GradeNumber = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12;

export type GradeExperienceBand =
  | 'EARLY_PRIMARY_G1_G3'
  | 'UPPER_PRIMARY_G4_G5'
  | 'MIDDLE_SCHOOL_G6_G8'
  | 'SECONDARY_SENIOR_G9_G12';

export interface GradeBandMetadata {
  band: GradeExperienceBand;
  label: string;
  gradeRangeText: string;
  modeName: string;
  description: string;
  cssClass: string;
  accentGradient: string;
  badgeBg: string;
  cardPadding: string;
  buttonSize: string;
  buttonSizeClass: string;
  requiresParentAssistedNotice: boolean;
}

export function getGradeExperienceMeta(grade: number): GradeBandMetadata {
  if (grade <= 3) {
    return {
      band: 'EARLY_PRIMARY_G1_G3',
      label: 'Grades 1–3',
      gradeRangeText: 'Class 1 to Class 3',
      modeName: 'Foundational Explorer Mode',
      description:
        'Visual story cards, gentle voice-friendly prompts, and parent-assisted learning.',
      cssClass: 'grade-band-early',
      accentGradient: 'from-[#101B35] via-[#312E81] to-[#5146E5]',
      badgeBg: 'bg-[#EEEAFE] text-[#101B35] border-[#5146E5]/25',
      cardPadding: 'p-6',
      buttonSize: 'py-3 px-5 text-sm',
      buttonSizeClass: 'py-3.5 px-6 text-base font-bold rounded-2xl',
      requiresParentAssistedNotice: true,
    };
  }
  if (grade <= 5) {
    return {
      band: 'UPPER_PRIMARY_G4_G5',
      label: 'Grades 4–5',
      gradeRangeText: 'Class 4 to Class 5',
      modeName: 'Guided Discovery Mode',
      description:
        'Interactive concept builders, visual chapter maps, and encouraging daily milestones.',
      cssClass: 'grade-band-upper-primary',
      accentGradient: 'from-[#101B35] via-[#3730A3] to-[#5146E5]',
      badgeBg: 'bg-[#EEEAFE] text-[#101B35] border-[#5146E5]/25',
      cardPadding: 'p-5',
      buttonSize: 'py-2.5 px-4 text-xs',
      buttonSizeClass: 'py-3 px-5 text-sm font-bold rounded-xl',
      requiresParentAssistedNotice: false,
    };
  }
  if (grade <= 8) {
    return {
      band: 'MIDDLE_SCHOOL_G6_G8',
      label: 'Grades 6–8',
      gradeRangeText: 'Class 6 to Class 8',
      modeName: 'Concept Mastery Mode',
      description:
        'Visual step-by-step tutoring, smart daily schedules, and real topic mastery tracking.',
      cssClass: 'grade-band-middle',
      accentGradient: 'from-[#101B35] via-[#262A63] to-[#5146E5]',
      badgeBg: 'bg-[#EEEAFE] text-[#202943] border-[#5146E5]/25',
      cardPadding: 'p-5',
      buttonSize: 'py-2.5 px-4 text-xs',
      buttonSizeClass: 'py-2.5 px-4 text-sm font-semibold rounded-xl',
      requiresParentAssistedNotice: false,
    };
  }
  return {
    band: 'SECONDARY_SENIOR_G9_G12',
    label: 'Grades 9–12',
    gradeRangeText: 'Class 9 to Class 12 (Board Exam Focus)',
    modeName: 'Academic Excellence Mode',
    description:
      'High-focus board exam analytics, timed mock papers, revision schedules, and historical trend tracking.',
    cssClass: 'grade-band-senior',
    accentGradient: 'from-[#101B35] via-[#1B264F] to-[#4F46E5]',
    badgeBg: 'bg-[#EEEAFE] text-[#101B35] border-[#5146E5]/25',
    cardPadding: 'p-5',
    buttonSize: 'py-2 px-3.5 text-xs',
    buttonSizeClass: 'py-2.5 px-4 text-xs font-semibold rounded-lg',
    requiresParentAssistedNotice: false,
  };
}

export type ScreenId =
  | 'landing'
  | 'auth'
  | 'onboarding'
  | 'dashboard'
  | 'buddy'
  | 'homework'
  | 'subjects'
  | 'plan'
  | 'practice'
  | 'exams'
  | 'projects'
  | 'progress'
  | 'journey'
  | 'comparison'
  | 'promotion'
  | 'parent'
  | 'profile'
  | 'languages';

export interface ScreenDefinition {
  id: ScreenId;
  number: number;
  title: string;
  shortLabel: string;
  category: 'Core' | 'Learning' | 'History & Growth' | 'Family & Settings';
}

export const ALL_18_SCREENS: ScreenDefinition[] = [
  { id: 'landing', number: 1, title: 'Home', shortLabel: 'Home', category: 'Core' },
  { id: 'auth', number: 2, title: 'Account', shortLabel: 'Account', category: 'Core' },
  { id: 'onboarding', number: 3, title: 'Setup', shortLabel: 'Setup', category: 'Core' },
  { id: 'dashboard', number: 4, title: 'Dashboard', shortLabel: 'Home', category: 'Core' },
  { id: 'subjects', number: 5, title: 'Guided Lessons', shortLabel: 'Lessons', category: 'Learning' },
  { id: 'buddy', number: 6, title: 'AI Learning Buddy', shortLabel: 'AI Buddy', category: 'Learning' },
  { id: 'plan', number: 7, title: 'Study Planner', shortLabel: 'Plan', category: 'Learning' },
  { id: 'homework', number: 8, title: 'Homework', shortLabel: 'Homework', category: 'Learning' },
  { id: 'exams', number: 9, title: 'Exam Prep', shortLabel: 'Exams', category: 'Learning' },
  { id: 'practice', number: 10, title: 'Smart Revision', shortLabel: 'Revision', category: 'Learning' },
  { id: 'projects', number: 11, title: 'Projects', shortLabel: 'Projects', category: 'Learning' },
  { id: 'progress', number: 12, title: 'Progress', shortLabel: 'Progress', category: 'History & Growth' },
  { id: 'journey', number: 13, title: 'Academic Journey', shortLabel: 'Journey', category: 'History & Growth' },
  { id: 'comparison', number: 14, title: 'Year Compare', shortLabel: 'Compare', category: 'History & Growth' },
  { id: 'promotion', number: 15, title: 'Grade Promotion', shortLabel: 'Promotion', category: 'History & Growth' },
  { id: 'parent', number: 16, title: 'Parent Portal', shortLabel: 'Parent', category: 'Family & Settings' },
  { id: 'profile', number: 17, title: 'Settings', shortLabel: 'Settings', category: 'Family & Settings' },
  { id: 'languages', number: 18, title: 'Languages', shortLabel: 'Languages', category: 'Family & Settings' },
];
