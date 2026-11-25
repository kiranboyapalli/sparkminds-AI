import React from 'react';
import {
  Home,
  LogIn,
  ClipboardCheck,
  LayoutDashboard,
  Bot,
  FileQuestion,
  BookOpen,
  CalendarCheck,
  Repeat,
  Award,
  FolderKanban,
  BarChart3,
  Milestone,
  GitCompare,
  GraduationCap,
  Users,
  UserCog,
  Languages,
  Sparkles,
  CheckCircle2,
  Bell,
  Menu,
  X,
  HelpCircle,
} from 'lucide-react';
import { formatTimeRange12Hour } from './utils/timeFormat';
import { BrandTagline, EduSparkLogo } from './design-system/EduSparkLogo';
import { OpeningSplashAnimation } from './components/OpeningSplashAnimation';
import { AgeQuickEditorModal } from './components/AgeQuickEditorModal';
import { FirstTimeIntroTour } from './components/FirstTimeIntroTour';
import { FeatureSpotlightTour } from './components/FeatureSpotlightTour';
import { SparkRobotMascot } from './components/SparkRobotMascot';
import {
  ALL_18_SCREENS,
  BRAND_DESCRIPTION,
  BRAND_TAGLINE,
  ScreenId,
  GradeNumber,
  getGradeExperienceMeta,
} from './design-system/tokens';
import { AgentOrchestratorBar } from './components/AgentOrchestratorBar';
import {
  SevenStepOnboarding,
  OnboardingState,
} from './onboarding/SevenStepOnboarding';
import {
  AILearningBuddyView,
  AcademicJourneyView,
  AnnualPromotionView,
  ParentDashboardView,
  HistoricalYearRecord,
} from './pages/CoreFeatureScreens';
import { LearningBuddyChat } from './pages/LearningBuddyChat';
import {
  StudentDashboardView,
  SmartStudyPlannerView,
  HomeworkManagerView,
  ExamPreparationCentreView,
  SmartRevisionCentreView,
  AcademicProgressDashboardView,
  SchoolProjectCreativityLabView,
  SubjectLearningExplorerView,
} from './pages/PlatformModules';
import {
  ALL_23_INDIAN_LANGUAGES,
  getSubjectsForGradeAndBoardFrontend,
} from './curriculum/curriculumData';

const SCREEN_ICONS: Record<ScreenId, React.ReactNode> = {
  landing: <Home className="w-4 h-4" />,
  auth: <LogIn className="w-4 h-4" />,
  onboarding: <ClipboardCheck className="w-4 h-4" />,
  dashboard: <LayoutDashboard className="w-4 h-4" />,
  buddy: <Bot className="w-4 h-4" />,
  homework: <FileQuestion className="w-4 h-4" />,
  subjects: <BookOpen className="w-4 h-4" />,
  plan: <CalendarCheck className="w-4 h-4" />,
  practice: <Repeat className="w-4 h-4" />,
  exams: <Award className="w-4 h-4" />,
  projects: <FolderKanban className="w-4 h-4" />,
  progress: <BarChart3 className="w-4 h-4" />,
  journey: <Milestone className="w-4 h-4" />,
  comparison: <GitCompare className="w-4 h-4" />,
  promotion: <GraduationCap className="w-4 h-4" />,
  parent: <Users className="w-4 h-4" />,
  profile: <UserCog className="w-4 h-4" />,
  languages: <Languages className="w-4 h-4" />,
};

const INITIAL_HISTORICAL_YEARS: HistoricalYearRecord[] = [
  {
    academicYearId: 'stu_aarav_g7_2024_G5',
    academicYearLabel: '2024-2025',
    grade: 5,
    board: 'CBSE',
    stateName: 'Telangana',
    schoolMedium: 'English',
    preferredExplanationLanguage: 'Telugu',
    secondaryExplanationLanguage: 'English',
    status: 'COMPLETED_PROMOTED',
    isLockedHistorical: true,
    subjectsStudied: ['G5_MATH', 'G5_EVS', 'G5_ENG', 'G5_LANG2'],
    unresolvedGaps: ['Fractions Introduction'],
    resolvedGaps: ['Large Numbers & Place Value'],
    evidenceRecords: [
      {
        id: 'ev_g5_1',
        subject: 'Mathematics',
        topic: 'Large Numbers & Place Value',
        evidenceType: 'ACTUAL_ASSESSMENT',
        scorePercentage: 84,
        trendIndicator: 'Consistent performance',
        notes: 'Verified Unit Test 2 score.',
      },
      {
        id: 'ev_g5_2',
        subject: 'Environmental Studies (EVS)',
        topic: 'Living & Non-Living Things',
        evidenceType: 'ACTUAL_ASSESSMENT',
        scorePercentage: 91,
        trendIndicator: 'Consistent performance',
        notes: 'Verified Annual Assessment score.',
      },
    ],
  },
  {
    academicYearId: 'stu_aarav_g7_2025_G6',
    academicYearLabel: '2025-2026',
    grade: 6,
    board: 'CBSE',
    stateName: 'Telangana',
    schoolMedium: 'English',
    preferredExplanationLanguage: 'Telugu',
    secondaryExplanationLanguage: 'English',
    status: 'COMPLETED_PROMOTED',
    isLockedHistorical: true,
    subjectsStudied: ['G6_MATH', 'G6_SCI', 'G6_SST', 'G6_ENG', 'G6_LANG2'],
    unresolvedGaps: ['Fractions & Decimals (Unlike Denominators)'],
    resolvedGaps: ['Basic Number Line'],
    evidenceRecords: [
      {
        id: 'ev_g6_1',
        subject: 'Mathematics',
        topic: 'Fractions & Decimals',
        evidenceType: 'ACTUAL_ASSESSMENT',
        scorePercentage: 64,
        trendIndicator: 'Decline',
        notes: 'Half-yearly exam showed difficulty finding LCM of denominators.',
      },
      {
        id: 'ev_g6_2',
        subject: 'General Science',
        topic: 'Nutrition in Plants & Animals',
        evidenceType: 'ACTUAL_ASSESSMENT',
        scorePercentage: 78,
        trendIndicator: 'Consistent performance',
        notes: 'Good diagram accuracy.',
      },
    ],
  },
  {
    academicYearId: 'stu_aarav_g7_2026_G7',
    academicYearLabel: '2026-2027',
    grade: 7,
    board: 'CBSE',
    stateName: 'Telangana',
    schoolMedium: 'English',
    preferredExplanationLanguage: 'Telugu',
    secondaryExplanationLanguage: 'English',
    status: 'ACTIVE',
    isLockedHistorical: false,
    subjectsStudied: ['G7_MATH', 'G7_SCI', 'G7_SST', 'G7_ENG', 'G7_LANG2'],
    unresolvedGaps: [
      'Fractions & Decimals multi-step word problems',
      'Algebraic Expressions sign rules',
    ],
    resolvedGaps: ['Integers & Rational Numbers'],
    evidenceRecords: [
      {
        id: 'ev_g7_1',
        subject: 'Mathematics',
        topic: 'Integers & Rational Numbers',
        evidenceType: 'ACTUAL_ASSESSMENT',
        scorePercentage: 88,
        trendIndicator: 'Learning gap resolved',
        notes: 'Verified Unit Test 1 mastery (+24% improvement over Grade 6).',
      },
      {
        id: 'ev_g7_2',
        subject: 'Mathematics',
        topic: 'Fractions & Decimals',
        evidenceType: 'HOMEWORK_PRACTICE',
        scorePercentage: 74,
        trendIndicator: 'Improvement',
        notes: 'Improving with Telugu + English bilingual visual steps.',
      },
      {
        id: 'ev_g7_3',
        subject: 'General Science',
        topic: 'Acids, Bases & Salts',
        evidenceType: 'STUDENT_SELF_REPORT',
        scorePercentage: null,
        qualitativeRating: 'Need help',
        trendIndicator: 'Needs attention',
        notes: 'Recorded from Onboarding Step 4 Self-Report (Awaiting diagnostic quiz).',
      },
    ],
  },
];

function buildDefaultOnboardingState(overrides: Partial<OnboardingState> = {}): OnboardingState {
  const grade = (overrides.grade || 7) as GradeNumber;
  const board = (overrides.board || 'CBSE') as 'CBSE' | 'ICSE' | 'STATE' | 'OTHER';
  const stateName = overrides.stateName || 'Telangana';
  const subs = getSubjectsForGradeAndBoardFrontend(
    grade,
    board === 'OTHER' ? 'CBSE' : board,
    stateName
  ).map((s) => s.code);
  const selectedSubjects =
    overrides.selectedSubjects && overrides.selectedSubjects.length > 0
      ? overrides.selectedSubjects
      : subs.slice(0, Math.min(5, subs.length));
  const confMap: Record<string, 'Strong' | 'Okay' | 'Need help' | 'Difficult'> = {};
  selectedSubjects.forEach((c, idx) => {
    confMap[c] = idx === 0 ? 'Need help' : 'Okay';
  });

  return {
    studentId: 'stu_learner',
    studentName: '',
    age: 12,
    grade,
    board,
    stateName,
    otherBoardText: '',
    schoolMedium: 'English',
    preferredExplanationLanguage: 'English',
    secondaryExplanationLanguage: '',
    interfaceDisplayLanguage: 'English',
    selectedSubjects,
    showOtherSubjectInput: false,
    otherSubjectText: '',
    helpWithAllSubjects: false,
    subjectsToImprove: selectedSubjects.slice(0, Math.min(2, selectedSubjects.length)),
    subjectConfidence: confMap,
    difficultTopicsBySubject: {},
    mainImprovementPriority: 'Understand difficult concepts',
    selectedChallenges: [
      "I don't understand some concepts.",
      'I struggle with application-based questions.',
      'I find it difficult to revise regularly.',
    ],
    showOtherChallengeInput: false,
    otherChallengeText: '',
    whenNeedMostHelp: ['While understanding concepts', 'While solving questions'],
    challengeFrequency: 'Often',
    everythingGoalSelected: true,
    selectedGoals: ['g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8', 'g9'],
    primaryGoal: 'g2',
    ...overrides,
  };
}

export function App() {
  const [showOpeningSplash, setShowOpeningSplash] = React.useState<boolean>(true);
  const [showIntroTour, setShowIntroTour] = React.useState<boolean>(false);
  const [isIntroReplay, setIsIntroReplay] = React.useState<boolean>(false);
  const [showTutorial, setShowTutorial] = React.useState<boolean>(false);
  const [activeScreen, setActiveScreen] = React.useState<ScreenId>('auth');
  const [isOnboardingCompleted, setIsOnboardingCompleted] = React.useState<boolean>(false);
  const [isCheckingSession, setIsCheckingSession] = React.useState<boolean>(() => {
    try {
      return Boolean(window.localStorage.getItem('sparkminds_auth_token'));
    } catch {
      return false;
    }
  });
  const [onboarding, setOnboarding] = React.useState<OnboardingState>(() =>
    buildDefaultOnboardingState({ preferredExplanationLanguage: 'Telugu', secondaryExplanationLanguage: 'English' })
  );

  const [academicYears, setAcademicYears] = React.useState<HistoricalYearRecord[]>(
    INITIAL_HISTORICAL_YEARS
  );
  const [buddyQuestionPrefill, setBuddyQuestionPrefill] = React.useState<{
    question: string;
    subject: string;
  } | null>(null);

  const handleOpenBuddyWithQuestion = (question: string, subject: string) => {
    setBuddyQuestionPrefill({ question, subject });
    setActiveScreen('buddy');
  };

  const checkAndTriggerTutorial = React.useCallback((studentId: string) => {
    try {
      const key = `sparkminds_feature_tour_completed_${studentId}`;
      const completed = localStorage.getItem(key);
      if (completed !== 'true') {
        setShowTutorial(true);
      }
    } catch {
      setShowTutorial(true);
    }
  }, []);

  const handleTutorialClose = React.useCallback(() => {
    try {
      const key = `sparkminds_feature_tour_completed_${onboarding.studentId}`;
      localStorage.setItem(key, 'true');
      localStorage.setItem(`sparkminds_tutorial_completed_${onboarding.studentId}`, 'true');
    } catch {
      // Ignore error
    }
    setShowTutorial(false);
  }, [onboarding.studentId]);

  const handleReplayTutorial = React.useCallback(() => {
    setShowTutorial(true);
  }, []);

  const handleCompleteIntroTour = React.useCallback(
    (goToRegister: boolean) => {
      try {
        window.localStorage.setItem('sparkminds_intro_tour_completed', 'true');
      } catch {
        // ignore storage errors
      }
      setShowIntroTour(false);
      if (!isIntroReplay) {
        setAuthPortalTab(goToRegister ? 'register' : 'register');
        setActiveScreen('auth');
      }
      setIsIntroReplay(false);
    },
    [isIntroReplay]
  );

  const handleReplayIntro = React.useCallback(() => {
    setIsIntroReplay(true);
    setShowIntroTour(true);
  }, []);

  const handleResetRobotTips = React.useCallback(() => {
    try {
      const prefix = `sparkminds_robot_tip_dismissed_${onboarding.studentId}_`;
      Object.keys(window.localStorage).forEach((k) => {
        if (k.startsWith(prefix)) window.localStorage.removeItem(k);
      });
      window.dispatchEvent(new Event('sparkminds-reset-tips'));
    } catch {
      // ignore
    }
  }, [onboarding.studentId]);

  const [backendStatus, setBackendStatus] = React.useState<{
    connected: boolean;
    supportedLanguagesCount: number;
  }>({ connected: false, supportedLanguagesCount: 23 });

  React.useEffect(() => {
    fetch('/api/health')
      .then((res) => res.json())
      .then((data) => {
        if (data && data.status === 'ok') {
          setBackendStatus({
            connected: true,
            supportedLanguagesCount: data.supported_languages_count || 23,
          });
        }
      })
      .catch(() => {
        setBackendStatus({ connected: false, supportedLanguagesCount: 23 });
      });
  }, []);

  const gradeMeta = getGradeExperienceMeta(onboarding.grade);
  const currentScreenDef =
    ALL_18_SCREENS.find((s) => s.id === activeScreen) || ALL_18_SCREENS[0];
  const currentSubjects = getSubjectsForGradeAndBoardFrontend(
    onboarding.grade,
    onboarding.board,
    onboarding.stateName
  );

  // Representative Test Profile Switcher (Grades 1, 4, 7, 10, 12 - Section 19)
  const applyRepresentativeProfile = (targetGrade: GradeNumber) => {
    const profileMap: Record<
      number,
      {
        studentId: string;
        name: string;
        age: number;
        board: 'CBSE' | 'ICSE' | 'STATE';
        state: string;
        lang: string;
      }
    > = {
      1: {
        studentId: 'stu_ananya_g1',
        name: '',
        age: 6,
        board: 'CBSE',
        state: 'Telangana',
        lang: 'Telugu',
      },
      4: {
        studentId: 'stu_diya_g4',
        name: '',
        age: 9,
        board: 'ICSE',
        state: 'Karnataka',
        lang: 'Kannada',
      },
      7: {
        studentId: 'stu_aarav_g7',
        name: '',
        age: 12,
        board: 'CBSE',
        state: 'Telangana',
        lang: 'Telugu',
      },
      10: {
        studentId: 'stu_karthik_g10',
        name: '',
        age: 15,
        board: 'STATE',
        state: 'Tamil Nadu',
        lang: 'Tamil',
      },
      12: {
        studentId: 'stu_riya_g12',
        name: '',
        age: 17,
        board: 'CBSE',
        state: 'Delhi (NCT)',
        lang: 'Hindi',
      },
    };
    const chosen = profileMap[targetGrade] || {
      studentId: `stu_grade_${targetGrade}`,
      name: '',
      age: targetGrade + 5,
      board: 'CBSE',
      state: 'Telangana',
      lang: 'Telugu',
    };
    const subs = getSubjectsForGradeAndBoardFrontend(
      targetGrade,
      chosen.board,
      chosen.state
    ).map((s) => s.code);

    setOnboarding((prev) => ({
      ...prev,
      studentId: chosen.studentId,
      studentName: chosen.name,
      age: chosen.age,
      grade: targetGrade,
      board: chosen.board,
      stateName: chosen.state,
      preferredExplanationLanguage: chosen.lang,
      selectedSubjects: subs,
      subjectsToImprove: subs.slice(0, 2),
    }));
  };

  // Sync isolated student Academic Journey & Notifications from backend whenever studentId or activeScreen changes
  const [notificationsList, setNotificationsList] = React.useState<any[]>([]);
  const [unreadNotificationsCount, setUnreadNotificationsCount] = React.useState<number>(0);
  const [showNotificationsDrawer, setShowNotificationsDrawer] = React.useState<boolean>(false);
  const [showReminderPrefsForm, setShowReminderPrefsForm] = React.useState<boolean>(false);
  const [reminderPrefs, setReminderPrefs] = React.useState<any>({
    daily_study_sessions_enabled: true,
    pending_chapters_enabled: true,
    homework_deadlines_enabled: true,
    upcoming_exams_enabled: true,
    revision_sessions_enabled: true,
    mock_tests_enabled: true,
    push_notifications_enabled: false,
    quiet_hours_enabled: true,
    quiet_hours_start: '22:00',
    quiet_hours_end: '07:00',
    reminder_frequency: 'BALANCED',
    custom_reminder_times: ['6:00 PM', '8:00 AM'],
    android_notifications_permission: 'default',
    in_app_reminders_enabled: true,
    timezone_name: Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Kolkata',
  });
  const [pushStatusNotice, setPushStatusNotice] = React.useState<string>('');
  const [centreHistory, setCentreHistory] = React.useState<any[]>([]);
  const [customReminderTimeInput, setCustomReminderTimeInput] = React.useState<string>('7:00 PM');
  const [showMobileMenuDrawer, setShowMobileMenuDrawer] = React.useState<boolean>(false);

  const refreshNotifications = React.useCallback(() => {
    fetch(`/api/students/${onboarding.studentId}/notifications`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && Array.isArray(data.notifications)) {
          setNotificationsList(data.notifications);
          setUnreadNotificationsCount(data.unread_count ?? data.notifications.length);
          if (data.reminder_preferences) {
            setReminderPrefs((prev: any) => ({ ...prev, ...data.reminder_preferences }));
          }
        }
      })
      .catch(() => { });
    fetch(`/api/students/${onboarding.studentId}/notifications/centre`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && Array.isArray(data.notifications)) {
          setCentreHistory(data.notifications);
        }
      })
      .catch(() => { });
  }, [onboarding.studentId]);

  const handleReminderStatusAction = async (
    n: any,
    status: 'Completed' | 'Postponed' | 'Missed'
  ) => {
    try {
      await fetch(`/api/students/${onboarding.studentId}/reminders/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: onboarding.studentId,
          notification_id: n.id,
          status,
          linked_entity_type: n.linked_entity_type || null,
          linked_entity_id: n.linked_entity_id || null,
        }),
      });
      refreshNotifications();
    } catch {
      // Offline fallback
      setNotificationsList((prev) =>
        prev.map((item) => (item.id === n.id ? { ...item, status, unread: false } : item))
      );
    }
  };

  const handleSaveReminderPrefs = async (nextPrefs: any) => {
    setReminderPrefs(nextPrefs);
    try {
      await fetch(`/api/students/${onboarding.studentId}/reminders/preferences`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...nextPrefs,
          student_id: onboarding.studentId,
        }),
      });
      refreshNotifications();
    } catch {
      // Keep local update
    }
  };

  const urlBase64ToUint8Array = (base64String: string) => {
    const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  };

  const handleRequestAndroidNotificationPermission = async () => {
    setPushStatusNotice('');
    if (typeof window === 'undefined' || !('Notification' in window)) {
      setPushStatusNotice(
        'Push notifications are not supported by this browser. In-app reminders remain active.'
      );
      return;
    }
    // Never repeatedly prompt a user who already denied browser notifications
    if (window.Notification.permission === 'denied') {
      setPushStatusNotice(
        'Browser notifications are currently blocked in your browser settings. In-app reminders remain available.'
      );
      return;
    }
    let perm: 'granted' | 'denied' | 'default' = window.Notification.permission;
    try {
      if (perm !== 'granted') {
        perm = await window.Notification.requestPermission();
      }
      if (perm === 'granted') {
        if ('serviceWorker' in navigator && 'PushManager' in window) {
          try {
            const keyRes = await fetch('/api/notifications/vapid-public-key');
            const keyData = keyRes.ok ? await keyRes.json() : null;
            if (keyData?.vapid_public_key) {
              const reg = await navigator.serviceWorker.ready;
              let sub = await reg.pushManager.getSubscription();
              if (!sub) {
                sub = await reg.pushManager.subscribe({
                  userVisibleOnly: true,
                  applicationServerKey: urlBase64ToUint8Array(keyData.vapid_public_key),
                });
              }
              const subJson = sub.toJSON();
              if (subJson.endpoint && subJson.keys?.p256dh && subJson.keys?.auth) {
                await fetch(`/api/students/${onboarding.studentId}/notifications/subscribe`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    endpoint: subJson.endpoint,
                    p256dh: subJson.keys.p256dh,
                    auth: subJson.keys.auth,
                    user_agent: navigator.userAgent,
                  }),
                });
              }
            }
          } catch {
            // Graceful fallback to in-app + local browser notifications
          }
        }
        setPushStatusNotice('✓ Push & in-app study reminders enabled (quiet hours respected).');
      } else {
        setPushStatusNotice('Notifications were not enabled. You can still use in-app reminders anytime.');
      }
    } catch {
      setPushStatusNotice('In-app reminders remain active.');
    }
    handleSaveReminderPrefs({
      ...reminderPrefs,
      push_notifications_enabled: perm === 'granted',
      android_notifications_permission: perm,
    });
  };

  const handleMarkAllNotificationsRead = async () => {
    try {
      await fetch(`/api/students/${onboarding.studentId}/notifications/mark-all-read`, {
        method: 'POST',
      });
      setUnreadNotificationsCount(0);
      setCentreHistory((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch {
      setUnreadNotificationsCount(0);
    }
  };

  React.useEffect(() => {
    fetch(`/api/students/${onboarding.studentId}/academic-journey`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && Array.isArray(data.completed_and_active_years) && data.completed_and_active_years.length > 0) {
          const mapped: HistoricalYearRecord[] = data.completed_and_active_years.map((y: any) => ({
            academicYearId: y.academic_year_id,
            academicYearLabel: y.academic_year_label,
            grade: y.grade as GradeNumber,
            board: y.school_board,
            stateName: y.state_name || 'Telangana',
            schoolMedium: y.language_preferences?.school_medium_language || 'English',
            preferredExplanationLanguage: y.language_preferences?.preferred_explanation_language || 'English',
            secondaryExplanationLanguage: y.language_preferences?.secondary_explanation_language || '',
            status: y.status,
            isLockedHistorical: Boolean(y.is_locked_historical),
            subjectsStudied: y.subjects_studied || [],
            unresolvedGaps: y.unresolved_learning_gaps || [],
            resolvedGaps: y.resolved_learning_gaps || [],
            evidenceRecords: (y.evidence_records || []).map((ev: any) => ({
              id: ev.record_id,
              subject: ev.subject_name,
              topic: ev.topic_name,
              evidenceType: ev.evidence_type,
              scorePercentage: ev.score_percentage,
              qualitativeRating: ev.qualitative_rating,
              trendIndicator: ev.trend_indicator,
              notes: ev.notes,
            })),
          }));
          setAcademicYears(mapped);
        }
      })
      .catch(() => {
        // Keep current local state if offline
      });

    refreshNotifications();
  }, [onboarding.studentId, activeScreen, refreshNotifications]);

  // Annual Grade Progression Handler (Preserves all previous years in both UI & Backend!)
  const handlePromoteStudent = (
    decision: 'Yes' | 'No' | 'I am repeating my current grade' | 'I am changing schools',
    boardUnchanged: 'Yes, same board' | 'No, I have changed my board',
    sameSchool: 'Yes' | 'No',
    newBoard: 'CBSE' | 'ICSE' | 'STATE' | 'OTHER'
  ) => {
    const nextGrade = (
      decision === 'Yes' ? Math.min(12, onboarding.grade + 1) : onboarding.grade
    ) as GradeNumber;
    const updatedBoard =
      boardUnchanged === 'Yes, same board' ? onboarding.board : newBoard;
    const nextSubjects = getSubjectsForGradeAndBoardFrontend(
      nextGrade,
      updatedBoard,
      onboarding.stateName
    ).map((s) => s.code);

    fetch(`/api/students/${onboarding.studentId}/progression`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: onboarding.studentId,
        new_academic_year_label: '2027-2028',
        promotion_decision: decision,
        same_school: sameSchool,
        board_unchanged: boardUnchanged,
        new_school_board: updatedBoard,
        new_state_name: onboarding.stateName,
        updated_school_medium: onboarding.schoolMedium,
        updated_preferred_explanation_language: onboarding.preferredExplanationLanguage,
        updated_secondary_explanation_language: onboarding.secondaryExplanationLanguage || null,
        reselected_subjects: nextSubjects,
        reselected_improvement_subjects: nextSubjects.slice(0, 2),
        everything_goal_selected: onboarding.everythingGoalSelected,
        updated_goals: onboarding.selectedGoals,
        updated_challenges: onboarding.selectedChallenges,
      }),
    }).catch(() => { });

    setAcademicYears((prevYears) => {
      const lockedPast = prevYears.map((y) => ({
        ...y,
        status:
          y.status === 'ACTIVE'
            ? decision === 'Yes'
              ? ('COMPLETED_PROMOTED' as const)
              : ('COMPLETED_REPEATED' as const)
            : y.status,
        isLockedHistorical: true,
      }));

      const newYearRecord: HistoricalYearRecord = {
        academicYearId: `${onboarding.studentId}_2027_G${nextGrade}`,
        academicYearLabel: '2027-2028',
        grade: nextGrade,
        board: updatedBoard,
        stateName: onboarding.stateName,
        schoolMedium: onboarding.schoolMedium,
        preferredExplanationLanguage: onboarding.preferredExplanationLanguage,
        secondaryExplanationLanguage: onboarding.secondaryExplanationLanguage,
        status: 'ACTIVE',
        isLockedHistorical: false,
        subjectsStudied: nextSubjects,
        unresolvedGaps: ['Initial New Grade Diagnostic Pending'],
        resolvedGaps: ['Carried Forward Mastery from Previous Grade'],
        evidenceRecords: [
          {
            id: `ev_promo_${nextGrade}`,
            subject: 'Academic Progression',
            topic: `Promoted to Grade ${nextGrade} (${updatedBoard})`,
            evidenceType: 'STUDENT_SELF_REPORT',
            scorePercentage: null,
            qualitativeRating: 'New Academic Year Started',
            trendIndicator: 'Consistent performance',
            notes: `All ${lockedPast.length} previous academic year(s) locked and preserved.`,
          },
        ],
      };

      return [...lockedPast, newYearRecord];
    });

    setOnboarding((prev) => ({
      ...prev,
      grade: nextGrade,
      board: updatedBoard,
      selectedSubjects: nextSubjects,
      subjectsToImprove: nextSubjects.slice(0, 2),
    }));
  };

  const [customStudentNameInput, setCustomStudentNameInput] = React.useState<string>('');
  const [customAgeInput, setCustomAgeInput] = React.useState<number>(12);
  const [customDobInput, setCustomDobInput] = React.useState<string>('');
  const [customUsernameInput, setCustomUsernameInput] = React.useState<string>('');
  const [customEmailInput, setCustomEmailInput] = React.useState<string>('');
  const [emailVerifyCodeInput, setEmailVerifyCodeInput] = React.useState<string>('');
  const [emailVerificationToken, setEmailVerificationToken] = React.useState<string>('');
  const [emailVerifyCodeSent, setEmailVerifyCodeSent] = React.useState<boolean>(false);
  const [emailVerifyStatusMsg, setEmailVerifyStatusMsg] = React.useState<string>('');
  const [emailVerifyStatusType, setEmailVerifyStatusType] = React.useState<'info' | 'ok' | 'err'>('info');
  const [emailOtpSending, setEmailOtpSending] = React.useState<boolean>(false);
  const [emailOtpVerifying, setEmailOtpVerifying] = React.useState<boolean>(false);
  const [emailResendCooldown, setEmailResendCooldown] = React.useState<number>(0);
  const [emailOtpExpired, setEmailOtpExpired] = React.useState<boolean>(false);
  const [recoveryRequestMsg, setRecoveryRequestMsg] = React.useState<string>('');
  const [recoveryRequestType, setRecoveryRequestType] = React.useState<'info' | 'err'>('info');
  const [recoverySending, setRecoverySending] = React.useState<boolean>(false);
  const [recoveryResendCooldown, setRecoveryResendCooldown] = React.useState<number>(0);

  React.useEffect(() => {
    if (emailResendCooldown <= 0) return;
    const timer = window.setInterval(() => {
      setEmailResendCooldown((prev) => (prev <= 1 ? 0 : prev - 1));
    }, 1000);
    return () => window.clearInterval(timer);
  }, [emailResendCooldown > 0]);

  React.useEffect(() => {
    if (recoveryResendCooldown <= 0) return;
    const timer = window.setInterval(() => {
      setRecoveryResendCooldown((prev) => (prev <= 1 ? 0 : prev - 1));
    }, 1000);
    return () => window.clearInterval(timer);
  }, [recoveryResendCooldown > 0]);
  const [customPasswordInput, setCustomPasswordInput] = React.useState<string>('');
  const [authPortalTab, setAuthPortalTab] = React.useState<'register' | 'login' | 'recover'>('register');
  const [loginIdentifierInput, setLoginIdentifierInput] = React.useState<string>('');
  const [loginPasswordInput, setLoginPasswordInput] = React.useState<string>('');
  const [recoveryIdentifierInput, setRecoveryIdentifierInput] = React.useState<string>('');
  const [recoveryProofInput, setRecoveryProofInput] = React.useState<string>('');
  const [recoveryNewPinInput, setRecoveryNewPinInput] = React.useState<string>('');
  const [authFeedbackMsg, setAuthFeedbackMsg] = React.useState<{ type: 'ok' | 'err'; text: string } | null>(null);

  // Profile-specific editing state for age and profile details (Requirement 2)
  const [profileEditAge, setProfileEditAge] = React.useState<number>(12);
  const [profileEditDob, setProfileEditDob] = React.useState<string>('2014-06-15');
  const [profileEditName, setProfileEditName] = React.useState<string>('');
  const [showAgeQuickModal, setShowAgeQuickModal] = React.useState<boolean>(false);
  const [profileSaveFeedback, setProfileSaveFeedback] = React.useState<{
    type: 'ok' | 'err';
    text: string;
  } | null>(null);
  const [activeSessionToken, setActiveSessionToken] = React.useState<string | null>(() => {
    try {
      return window.localStorage.getItem('sparkminds_auth_token');
    } catch {
      return null;
    }
  });
  const [activeDevicesCount, setActiveDevicesCount] = React.useState<number>(1);
  const [pwaInstallPrompt, setPwaInstallPrompt] = React.useState<any>(null);
  const [swUpdateAvailable, setSwUpdateAvailable] = React.useState<boolean>(false);

  const hydrateFromCloudBundle = React.useCallback((bundle: any) => {
    if (!bundle || !bundle.student) return;
    const stu = bundle.student;
    const completed = Boolean(stu.onboarding_completed);
    setIsOnboardingCompleted(completed);
    const activeYr = bundle.active_year_profile;
    const langPrefs = stu.language_preferences || activeYr?.language_preferences || {};
    const targetGrade = (Number(stu.current_grade) || 7) as GradeNumber;
    const targetBoard = (stu.school_board || 'CBSE') as 'CBSE' | 'ICSE' | 'STATE' | 'OTHER';
    const targetState = stu.state_name || 'Telangana';
    const defaultSubs = getSubjectsForGradeAndBoardFrontend(
      targetGrade,
      targetBoard === 'OTHER' ? 'CBSE' : targetBoard,
      targetState
    ).map((s) => s.code);

    setOnboarding((prev) => {
      const isSameStudent = prev.studentId === stu.student_id;
      const base =
        isSameStudent && completed
          ? prev
          : buildDefaultOnboardingState({
              grade: targetGrade,
              board: targetBoard,
              stateName: targetState,
            });
      const restoredConf: Record<string, 'Strong' | 'Okay' | 'Need help' | 'Difficult'> = {
        ...base.subjectConfidence,
      };
      if (Array.isArray(activeYr?.subject_confidence_self_reports)) {
        activeYr.subject_confidence_self_reports.forEach((sr: any) => {
          if (sr?.subject_code && sr?.confidence_level) {
            restoredConf[sr.subject_code] = sr.confidence_level;
          }
        });
      }

      return {
        ...base,
        studentId: stu.student_id || base.studentId,
        studentName: stu.full_name || base.studentName,
        age: Number(stu.age) || base.age,
        grade: targetGrade,
        board: targetBoard,
        stateName: targetState,
        schoolMedium: langPrefs.school_medium_language || base.schoolMedium,
        preferredExplanationLanguage:
          langPrefs.preferred_explanation_language || base.preferredExplanationLanguage,
        secondaryExplanationLanguage:
          langPrefs.secondary_explanation_language ?? base.secondaryExplanationLanguage,
        interfaceDisplayLanguage:
          langPrefs.interface_display_language || base.interfaceDisplayLanguage,
        selectedSubjects:
          Array.isArray(activeYr?.subjects_studied) && activeYr.subjects_studied.length > 0
            ? activeYr.subjects_studied
            : defaultSubs,
        subjectsToImprove:
          Array.isArray(activeYr?.subjects_to_improve) && activeYr.subjects_to_improve.length > 0
            ? activeYr.subjects_to_improve
            : defaultSubs.slice(0, Math.min(2, defaultSubs.length)),
        subjectConfidence: restoredConf,
        selectedChallenges:
          Array.isArray(activeYr?.learning_challenges) && activeYr.learning_challenges.length > 0
            ? activeYr.learning_challenges
            : base.selectedChallenges,
        whenNeedMostHelp:
          Array.isArray(activeYr?.when_need_most_help) && activeYr.when_need_most_help.length > 0
            ? activeYr.when_need_most_help
            : base.whenNeedMostHelp,
        everythingGoalSelected:
          typeof activeYr?.everything_goal_selected === 'boolean'
            ? activeYr.everything_goal_selected
            : base.everythingGoalSelected,
        selectedGoals:
          Array.isArray(activeYr?.learning_goals) && activeYr.learning_goals.length > 0
            ? activeYr.learning_goals
            : base.selectedGoals,
        primaryGoal: activeYr?.primary_goal || base.primaryGoal,
      };
    });

    if (stu.full_name) {
      setCustomStudentNameInput(stu.full_name);
      setProfileEditName(stu.full_name);
    }
    if (stu.age) {
      const parsedAge = Number(stu.age);
      setCustomAgeInput(parsedAge);
      setProfileEditAge(parsedAge);
    }
    if (stu.date_of_birth) {
      setCustomDobInput(String(stu.date_of_birth));
      setProfileEditDob(String(stu.date_of_birth));
    }
    if (stu.email_or_username) setCustomEmailInput(String(stu.email_or_username));

    if (Array.isArray(bundle.academic_years) && bundle.academic_years.length > 0) {
      const mappedYears: HistoricalYearRecord[] = bundle.academic_years.map((y: any) => ({
        academicYearId: y.academic_year_id,
        academicYearLabel: y.academic_year_label,
        grade: y.grade as GradeNumber,
        board: y.school_board,
        stateName: y.state_name || 'Telangana',
        schoolMedium: y.language_preferences?.school_medium_language || 'English',
        preferredExplanationLanguage:
          y.language_preferences?.preferred_explanation_language || 'English',
        secondaryExplanationLanguage:
          y.language_preferences?.secondary_explanation_language || '',
        status: y.status,
        isLockedHistorical: Boolean(y.is_locked_historical),
        subjectsStudied: y.subjects_studied || [],
        unresolvedGaps: y.unresolved_learning_gaps || [],
        resolvedGaps: y.resolved_learning_gaps || [],
        evidenceRecords: (y.evidence_records || []).map((ev: any) => ({
          id: ev.record_id,
          subject: ev.subject_name,
          topic: ev.topic_name,
          evidenceType: ev.evidence_type,
          scorePercentage: ev.score_percentage,
          qualitativeRating: ev.qualitative_rating,
          trendIndicator: ev.trend_indicator,
          notes: ev.notes,
        })),
      }));
      setAcademicYears(mappedYears);
    }

    if (bundle.reminder_preferences) {
      setReminderPrefs(bundle.reminder_preferences);
    }
    if (Array.isArray(bundle.active_devices)) {
      setActiveDevicesCount(Math.max(1, bundle.active_devices.length));
    }
    if (bundle.session_token) {
      setActiveSessionToken(bundle.session_token);
      try {
        window.localStorage.setItem('sparkminds_auth_token', bundle.session_token);
        window.localStorage.setItem('sparkminds_student_id', stu.student_id);
        if (bundle.refresh_token) {
          window.localStorage.setItem('sparkminds_refresh_token', bundle.refresh_token);
        }
      } catch {
        // Ignore storage errors
      }
    }
  }, []);

  const handleLogoutSession = async () => {
    let savedRefreshToken: string | null = null;
    try {
      savedRefreshToken = window.localStorage.getItem('sparkminds_refresh_token');
    } catch {
      savedRefreshToken = null;
    }
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_token: activeSessionToken,
          refresh_token: savedRefreshToken,
          student_id: onboarding.studentId,
        }),
      });
    } catch {
      // Offline fallback
    }
    setActiveSessionToken(null);
    setIsOnboardingCompleted(false);
    setOnboarding(buildDefaultOnboardingState());
    try {
      window.localStorage.removeItem('sparkminds_auth_token');
      window.localStorage.removeItem('sparkminds_refresh_token');
      window.localStorage.removeItem('sparkminds_student_id');
      // Part 5: Returning logged-out users go directly to Sign In on next app launch
      // Note: onboarding completion lives permanently in the backend database and is NEVER reset on logout.
      window.localStorage.setItem('sparkminds_intro_tour_completed', 'true');
    } catch {
      // Ignore
    }
    setAuthFeedbackMsg({
      type: 'ok',
      text: 'You have been securely logged out on this device. Sign in anytime from Laptop, Android, or iOS to restore your cloud profile.',
    });
    setLoginIdentifierInput('');
    setLoginPasswordInput('');
    setAuthPortalTab('login');
    setActiveScreen('auth');
  };

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

  const handleProfileAgeChange = (newAge: number) => {
    const safeAge = Math.max(4, Math.min(20, newAge));
    setProfileEditAge(safeAge);
    const syncedDob = calculateDobFromAge(safeAge, profileEditDob);
    setProfileEditDob(syncedDob);
  };

  const handleProfileDobChange = (dobStr: string) => {
    setProfileEditDob(dobStr);
    if (dobStr) {
      const calcAge = calculateAgeFromDobString(dobStr);
      if (calcAge !== null) {
        setProfileEditAge(calcAge);
      }
    }
  };

  const handleSaveProfileAgeAndDetails = async (forcedAge?: number, forcedDob?: string) => {
    setProfileSaveFeedback(null);
    const targetAge = Number(forcedAge !== undefined ? forcedAge : profileEditAge);
    if (targetAge < 4 || targetAge > 20) {
      setProfileSaveFeedback({
        type: 'err',
        text: 'Please enter a valid student age between 4 and 20 years.',
      });
      return false;
    }
    const safeDob = (forcedDob || profileEditDob || calculateDobFromAge(targetAge)).trim();
    const effectiveName = profileEditName.trim() || onboarding.studentName || '';
    const sid = onboarding.studentId || (typeof window !== 'undefined' ? window.localStorage.getItem('sparkminds_student_id') : '') || 'stu_aarav_g7';
    const token = activeSessionToken || (typeof window !== 'undefined' ? window.localStorage.getItem('sparkminds_auth_token') : null);

    // Immediately update local application state and browser storage so user sees changes without delay
    setOnboarding((prev) => ({
      ...prev,
      age: targetAge,
      studentName: effectiveName,
    }));
    setProfileEditAge(targetAge);
    setProfileEditDob(safeDob);
    setCustomAgeInput(targetAge);
    setCustomDobInput(safeDob);
    try {
      window.localStorage.setItem('sparkminds_saved_age', String(targetAge));
      window.localStorage.setItem('sparkminds_saved_dob', safeDob);
      window.localStorage.setItem('sparkminds_student_name', effectiveName);
    } catch {}

    try {
      const res = await fetch(`/api/students/${encodeURIComponent(sid)}/profile`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'X-SparkMinds-Token': token } : {}),
        },
        body: JSON.stringify({
          age: targetAge,
          date_of_birth: safeDob,
          full_name: effectiveName,
          ...(targetAge < 8 ? { parent_consent_verified: true } : {}),
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        if (targetAge < 8 && !data.parent_consent_verified) {
          setProfileSaveFeedback({
            type: 'err',
            text: data.detail || 'Child Safety Protection: Students under 8 require parental verification.',
          });
          return false;
        }
        setProfileSaveFeedback({
          type: 'ok',
          text: `✓ Age updated to ${targetAge} years!`,
        });
        return true;
      }
      setProfileSaveFeedback({
        type: 'ok',
        text: `✓ Age updated to ${targetAge} years and saved to cloud database across all devices!`,
      });
      return true;
    } catch {
      setProfileSaveFeedback({
        type: 'ok',
        text: `✓ Age updated to ${targetAge} years!`,
      });
      return true;
    }
  };

  const handleSignInSubmit = async () => {
    setAuthFeedbackMsg(null);
    if (!loginIdentifierInput.trim()) {
      setAuthFeedbackMsg({
        type: 'err',
        text: 'Please enter your Student ID, Email, or Username.',
      });
      return;
    }
    const trimmedPass = loginPasswordInput.trim();
    if (!trimmedPass) {
      setAuthFeedbackMsg({
        type: 'err',
        text: 'Password or PIN is required to sign in.',
      });
      return;
    }
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          identifier: loginIdentifierInput.trim(),
          password_or_pin: trimmedPass,
          device_name: navigator.userAgent.includes('Android')
            ? 'Android Phone / Tablet'
            : navigator.userAgent.includes('iPhone') || navigator.userAgent.includes('iPad')
              ? 'iPhone / iPad'
              : 'Laptop / Desktop Browser',
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setAuthFeedbackMsg({
          type: 'err',
          text: data.detail || 'Could not sign in. Please verify your identifier and password/PIN.',
        });
        return;
      }
      if (data.cloud_sync_bundle) {
        hydrateFromCloudBundle(data.cloud_sync_bundle);
      }
      try {
        window.localStorage.setItem('sparkminds_intro_tour_completed', 'true');
      } catch {
        // ignore
      }
      const completed = Boolean(
        data.student?.onboarding_completed ||
          data.cloud_sync_bundle?.student?.onboarding_completed
      );
      setIsOnboardingCompleted(completed);
      setAuthFeedbackMsg({
        type: 'ok',
        text: `✓ Signed in successfully as ${data.student?.full_name}!`,
      });
      if (completed) {
        setActiveScreen('dashboard');
      } else {
        setActiveScreen('onboarding');
      }
    } catch {
      setAuthFeedbackMsg({
        type: 'err',
        text: 'Unable to reach server for cloud sign-in. Please check your connection.',
      });
    }
  };

  const handleSendEmailVerificationCode = async () => {
    if (emailOtpSending || emailResendCooldown > 0) return;
    setEmailVerifyStatusMsg('');
    setEmailVerifyStatusType('info');
    setAuthFeedbackMsg(null);
    const trimmedEmail = customEmailInput.trim();
    if (!trimmedEmail || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(trimmedEmail)) {
      setEmailVerifyStatusType('err');
      setEmailVerifyStatusMsg('Please enter a valid email address first.');
      return;
    }
    setEmailOtpSending(true);
    try {
      const res = await fetch('/api/auth/email/send-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: trimmedEmail, purpose: 'registration' }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        if (
          res.status === 429 &&
          typeof data.retry_after_seconds === 'number' &&
          data.retry_after_seconds > 0
        ) {
          setEmailResendCooldown(Math.ceil(data.retry_after_seconds));
        }
        setEmailVerifyStatusType('err');
        setEmailVerifyStatusMsg(
          data.detail || 'Could not send verification email. Please try again.'
        );
        return;
      }
      setEmailVerifyCodeSent(true);
      setEmailVerifyCodeInput('');
      setEmailVerificationToken('');
      setEmailOtpExpired(false);
      setEmailResendCooldown(
        typeof data.resend_cooldown_seconds === 'number' && data.resend_cooldown_seconds > 0
          ? data.resend_cooldown_seconds
          : 60
      );
      setEmailVerifyStatusType('info');
      setEmailVerifyStatusMsg(
        data.message ||
          'A 6-digit verification code has been sent to your email address. Please check your inbox (and spam folder). The code expires in 5 minutes.'
      );
    } catch {
      setEmailVerifyStatusType('err');
      setEmailVerifyStatusMsg(
        'Unable to reach the email verification service right now. Please check your connection and try again.'
      );
    } finally {
      setEmailOtpSending(false);
    }
  };

  const handleVerifyEmailCode = async () => {
    if (emailOtpVerifying) return;
    setEmailVerifyStatusMsg('');
    const trimmedEmail = customEmailInput.trim();
    const trimmedCode = emailVerifyCodeInput.trim();
    if (!trimmedEmail || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(trimmedEmail)) {
      setEmailVerifyStatusType('err');
      setEmailVerifyStatusMsg('Please enter a valid email address.');
      return;
    }
    if (!/^\d{6}$/.test(trimmedCode)) {
      setEmailVerifyStatusType('err');
      setEmailVerifyStatusMsg('Please enter the 6-digit numeric verification code sent to your email.');
      return;
    }
    setEmailOtpVerifying(true);
    try {
      const res = await fetch('/api/auth/email/verify-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: trimmedEmail,
          code: trimmedCode,
          purpose: 'registration',
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        const detail = String(
          data.detail || 'Email verification failed. Please check the code and try again.'
        );
        setEmailVerifyStatusType('err');
        setEmailVerifyStatusMsg(detail);
        setEmailVerificationToken('');
        if (/expired|maximum verification attempts|already been used|no active/i.test(detail)) {
          setEmailOtpExpired(true);
        }
        return;
      }
      setEmailVerificationToken(data.email_verification_token || '');
      setEmailOtpExpired(false);
      setEmailVerifyStatusType('ok');
      setEmailVerifyStatusMsg('✓ Email address verified! You can now complete registration.');
    } catch {
      setEmailVerifyStatusType('err');
      setEmailVerifyStatusMsg('Unable to verify email code right now. Please try again.');
    } finally {
      setEmailOtpVerifying(false);
    }
  };

  const handleRequestRecoveryCode = async () => {
    if (recoverySending || recoveryResendCooldown > 0) return;
    setRecoveryRequestMsg('');
    setRecoveryRequestType('info');
    const trimmedId = recoveryIdentifierInput.trim();
    if (!trimmedId) {
      setRecoveryRequestType('err');
      setRecoveryRequestMsg('Please enter your Student ID, username, or email address first.');
      return;
    }
    setRecoverySending(true);
    try {
      const res = await fetch('/api/auth/recover/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier: trimmedId }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        if (
          res.status === 429 &&
          typeof data.retry_after_seconds === 'number' &&
          data.retry_after_seconds > 0
        ) {
          setRecoveryResendCooldown(Math.ceil(data.retry_after_seconds));
        }
        setRecoveryRequestType('err');
        setRecoveryRequestMsg(data.detail || 'Unable to process recovery request right now.');
        return;
      }
      setRecoveryResendCooldown(60);
      setRecoveryRequestType('info');
      setRecoveryRequestMsg(
        data.message ||
          'If an account matches the details provided, a verification code has been sent to the registered email address.'
      );
    } catch {
      setRecoveryRequestType('err');
      setRecoveryRequestMsg('Unable to reach account recovery service.');
    } finally {
      setRecoverySending(false);
    }
  };

  const handleRegisterSubmit = async () => {
    setAuthFeedbackMsg(null);
    const trimmedName = customStudentNameInput.trim();
    if (!trimmedName) {
      setAuthFeedbackMsg({
        type: 'err',
        text: 'Please enter student full name to register.',
      });
      return;
    }
    const trimmedUsername = customUsernameInput.trim();
    if (!trimmedUsername) {
      setAuthFeedbackMsg({
        type: 'err',
        text: 'Please choose a unique username.',
      });
      return;
    }
    const trimmedEmail = customEmailInput.trim();
    if (!trimmedEmail || !trimmedEmail.includes('@')) {
      setAuthFeedbackMsg({
        type: 'err',
        text: 'Please enter a valid email address and verify it before registering.',
      });
      return;
    }
    if (!emailVerificationToken) {
      setAuthFeedbackMsg({
        type: 'err',
        text: 'Please verify your email address using the verification code before creating your account.',
      });
      return;
    }
    const trimmedDob = customDobInput.trim();
    if (!trimmedDob) {
      setAuthFeedbackMsg({
        type: 'err',
        text: 'Date of birth is required to register your student account.',
      });
      return;
    }
    const trimmedPassword = customPasswordInput.trim();
    if (!trimmedPassword) {
      setAuthFeedbackMsg({
        type: 'err',
        text: 'Password or PIN is required to secure your student account.',
      });
      return;
    }
    if (trimmedPassword.length < 4) {
      setAuthFeedbackMsg({
        type: 'err',
        text: 'Password or PIN must be at least 4 characters or digits.',
      });
      return;
    }
    if (isUnder8Student && !under8ConsentVerified) {
      setConsentErrorMsg(
        "Please use your parent's help to sign in."
      );
      setAuthFeedbackMsg({
        type: 'err',
        text: "Please use your parent's help to sign in.",
      });
      return;
    }

    const slug = trimmedUsername
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_+|_+$/g, '');
    const newStudentId = `stu_${slug || 'learner'}`;
    const targetGrade = onboarding.grade;

    try {
      const regRes = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: newStudentId,
          full_name: trimmedName,
          username: trimmedUsername,
          email: trimmedEmail,
          email_verification_token: emailVerificationToken,
          strict_registration: true,
          age: effectiveStudentAge,
          grade: targetGrade,
          school_board: onboarding.board,
          date_of_birth: trimmedDob,
          email_or_username: trimmedEmail,
          password_or_pin: trimmedPassword,
          device_name: navigator.userAgent.includes('Android')
            ? 'Android Phone / Tablet'
            : navigator.userAgent.includes('iPhone') || navigator.userAgent.includes('iPad')
              ? 'iPhone / iPad'
              : 'Laptop / Desktop Browser',
        }),
      });
      const regData = await regRes.json();
      if (!regRes.ok) {
        setAuthFeedbackMsg({
          type: 'err',
          text: regData.detail || 'Registration failed. Please check your inputs.',
        });
        return;
      }
      if (regData.cloud_sync_bundle) {
        hydrateFromCloudBundle(regData.cloud_sync_bundle);
      }
      try {
        window.localStorage.setItem('sparkminds_intro_tour_completed', 'true');
      } catch {
        // ignore
      }
      const regCompleted = Boolean(
        regData.student?.onboarding_completed ||
          regData.cloud_sync_bundle?.student?.onboarding_completed
      );
      setIsOnboardingCompleted(regCompleted);
      setOnboarding((prev) => ({
        ...prev,
        studentId: regData.student?.student_id || newStudentId,
        studentName: trimmedName,
        age: effectiveStudentAge,
        grade: targetGrade,
      }));
      setAuthFeedbackMsg({
        type: 'ok',
        text: regCompleted
          ? `✓ Welcome back, ${trimmedName}! Opening your Student Dashboard...`
          : `✓ Account registered for ${trimmedName}! Proceeding to 7-Step Onboarding...`,
      });
      setActiveScreen(regCompleted ? 'dashboard' : 'onboarding');
    } catch {
      setAuthFeedbackMsg({
        type: 'err',
        text: 'Unable to reach registration server. Please check your connection and try again.',
      });
    }
  };

  const handleRecoverySubmit = async () => {
    setAuthFeedbackMsg(null);
    if (!recoveryIdentifierInput.trim()) {
      setAuthFeedbackMsg({
        type: 'err',
        text: 'Please enter your student ID, email, or name.',
      });
      return;
    }
    try {
      const res = await fetch('/api/auth/recover', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          identifier: recoveryIdentifierInput.trim(),
          recovery_proof: recoveryProofInput.trim(),
          new_password_or_pin: recoveryNewPinInput.trim(),
          device_name: 'Recovered Device Session',
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setAuthFeedbackMsg({
          type: 'err',
          text: data.detail || 'Account recovery verification failed.',
        });
        return;
      }
      hydrateFromCloudBundle(data);
      const recoveredCompleted = Boolean(data.student?.onboarding_completed);
      setIsOnboardingCompleted(recoveredCompleted);
      setAuthFeedbackMsg({
        type: 'ok',
        text: `✓ Account recovered for ${data.student?.full_name}! Your new Password/PIN is now active.`,
      });
      if (data.session_token) {
        setActiveScreen(recoveredCompleted ? 'dashboard' : 'onboarding');
      } else {
        setAuthPortalTab('login');
      }
    } catch {
      setAuthFeedbackMsg({
        type: 'err',
        text: 'Unable to reach account recovery service.',
      });
    }
  };

  React.useEffect(() => {
    // Capture optional PWA deep link ?screen= parameter (honored after session & onboarding verification)
    let requestedScreen: ScreenId | null = null;
    try {
      const params = new URLSearchParams(window.location.search);
      const candidate = params.get('screen') as ScreenId | null;
      if (candidate && ALL_18_SCREENS.some((s) => s.id === candidate)) {
        requestedScreen = candidate;
      }
    } catch {
      requestedScreen = null;
    }

    // Restore active multi-device session via HttpOnly cookies and/or stored token headers.
    // Never pass raw tokens in query strings and NEVER wipe saved tokens on transient 5xx/network errors.
    const savedToken = (() => {
      try {
        return window.localStorage.getItem('sparkminds_auth_token');
      } catch {
        return null;
      }
    })();

    const routeUnauthenticatedVisitor = (hadToken: boolean) => {
      let introCompleted = hadToken;
      try {
        if (hadToken) {
          window.localStorage.setItem('sparkminds_intro_tour_completed', 'true');
        } else {
          introCompleted = window.localStorage.getItem('sparkminds_intro_tour_completed') === 'true';
        }
      } catch {
        introCompleted = hadToken;
      }
      if (!introCompleted) {
        setIsIntroReplay(false);
        setShowIntroTour(true);
        setAuthPortalTab('register');
        setActiveScreen('auth');
      } else {
        setShowIntroTour(false);
        setAuthPortalTab('login');
        setActiveScreen('auth');
      }
    };

    fetch('/api/auth/session', {
      method: 'GET',
      credentials: 'include',
    })
      .then(async (res) => {
        if (res.status === 401) {
          // Confirmed unauthorized even after main.tsx attempted silent refresh
          try {
            window.localStorage.removeItem('sparkminds_auth_token');
            window.localStorage.removeItem('sparkminds_refresh_token');
            window.localStorage.removeItem('sparkminds_student_id');
          } catch {
            // Ignore
          }
          setActiveSessionToken(null);
          routeUnauthenticatedVisitor(Boolean(savedToken));
          return;
        }
        if (!res.ok) {
          // Transient server/network error (5xx) — preserve stored token so student is NOT spuriously logged out
          if (!savedToken) {
            routeUnauthenticatedVisitor(false);
          }
          return;
        }
        const data = await res.json().catch(() => null);
        if (data && data.cloud_sync_bundle) {
          hydrateFromCloudBundle({
            ...data.cloud_sync_bundle,
            session_token: data.session_token || data.cloud_sync_bundle.session_token,
            refresh_token: data.refresh_token || data.cloud_sync_bundle.refresh_token,
          });
          try {
            window.localStorage.setItem('sparkminds_intro_tour_completed', 'true');
          } catch {
            // ignore
          }
          const completed = Boolean(
            data.student?.onboarding_completed ||
              data.cloud_sync_bundle?.student?.onboarding_completed
          );
          setIsOnboardingCompleted(completed);
          // Returning logged-in users go directly to Dashboard when onboarding is completed,
          // or continue onboarding when incomplete.
          setShowIntroTour(false);
          if (completed) {
            const targetScreen =
              requestedScreen &&
              requestedScreen !== 'auth' &&
              requestedScreen !== 'onboarding'
                ? requestedScreen
                : 'dashboard';
            setActiveScreen(targetScreen);
          } else {
            setActiveScreen('onboarding');
          }
        } else {
          routeUnauthenticatedVisitor(Boolean(savedToken));
        }
      })
      .catch(() => {
        // Offline / transient network failure — do NOT delete saved auth tokens
        if (!savedToken) {
          routeUnauthenticatedVisitor(false);
        }
      })
      .finally(() => {
        setIsCheckingSession(false);
      });

    // Listen for PWA install prompt & Service Worker updates
    const onBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setPwaInstallPrompt(e);
    };
    const onSwUpdate = () => {
      setSwUpdateAvailable(true);
    };
    window.addEventListener('beforeinstallprompt', onBeforeInstallPrompt);
    window.addEventListener('sparkminds-sw-update', onSwUpdate);
    return () => {
      window.removeEventListener('beforeinstallprompt', onBeforeInstallPrompt);
      window.removeEventListener('sparkminds-sw-update', onSwUpdate);
    };
  }, [hydrateFromCloudBundle]);

  // Unified graceful session-expiration handler (dispatched by main.tsx fetch interceptor after refresh fails)
  React.useEffect(() => {
    const handleSessionExpired = () => {
      try {
        window.localStorage.removeItem('sparkminds_auth_token');
        window.localStorage.removeItem('sparkminds_refresh_token');
        window.localStorage.removeItem('sparkminds_student_id');
        window.localStorage.setItem('sparkminds_intro_tour_completed', 'true');
      } catch {
        // Ignore storage errors
      }
      setActiveSessionToken(null);
      setShowIntroTour(false);
      setAuthFeedbackMsg({
        type: 'err',
        text: 'Your session ended for security. Please sign in again — all your learning progress is safely saved.',
      });
      setAuthPortalTab('login');
      setActiveScreen('auth');
    };

    window.addEventListener('sparkminds-session-expired', handleSessionExpired);
    return () => {
      window.removeEventListener('sparkminds-session-expired', handleSessionExpired);
    };
  }, []);

  // Periodic & tab focus cloud re-sync to sync changes made on other devices
  React.useEffect(() => {
    const syncLatestFromCloud = () => {
      const token = activeSessionToken || (() => {
        try {
          return window.localStorage.getItem('sparkminds_auth_token');
        } catch {
          return null;
        }
      })();
      if (!token) return;
      fetch('/api/auth/session', { method: 'GET', credentials: 'include' })
        .then((res) => {
          if (res.status === 401) {
            window.dispatchEvent(new CustomEvent('sparkminds-session-expired'));
            return null;
          }
          return res.ok ? res.json() : null;
        })
        .then((data) => {
          if (data && data.cloud_sync_bundle) {
            hydrateFromCloudBundle({
              ...data.cloud_sync_bundle,
              session_token: data.session_token || data.cloud_sync_bundle.session_token,
              refresh_token: data.refresh_token || data.cloud_sync_bundle.refresh_token,
            });
          }
        })
        .catch(() => { });
    };

    const onVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        syncLatestFromCloud();
      }
    };

    window.addEventListener('visibilitychange', onVisibilityChange);
    window.addEventListener('focus', syncLatestFromCloud);
    const interval = setInterval(syncLatestFromCloud, 30000);

    return () => {
      window.removeEventListener('visibilitychange', onVisibilityChange);
      window.removeEventListener('focus', syncLatestFromCloud);
      clearInterval(interval);
    };
  }, [activeSessionToken, hydrateFromCloudBundle]);

  const [under8ConsentVerified, setUnder8ConsentVerified] = React.useState<boolean>(false);
  const [parentFullName, setParentFullName] = React.useState<string>('');
  const [parentRelationship, setParentRelationship] = React.useState<'Mother' | 'Father' | 'Legal Guardian'>('Father');
  const [parentEmail, setParentEmail] = React.useState<string>('');
  const [parentPin, setParentPin] = React.useState<string>('');
  const [parentAttestationText, setParentAttestationText] = React.useState<string>(
    'I am the legal parent/guardian and I authorise assisted registration and supervision for my child under 8.'
  );
  const [consentErrorMsg, setConsentErrorMsg] = React.useState<string>('');
  const [consentSuccessMsg, setConsentSuccessMsg] = React.useState<string>('');

  const effectiveStudentAge = React.useMemo(() => {
    return customAgeInput;
  }, [customAgeInput]);

  const isUnder8Student = effectiveStudentAge < 8;
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState<boolean>(false);
  const [showMoreNavTools, setShowMoreNavTools] = React.useState<boolean>(false);
  const [showProfileSwitcherMenu, setShowProfileSwitcherMenu] = React.useState<boolean>(false);

  const PRIMARY_SIDEBAR_SCREENS: ScreenId[] = [
    'dashboard',
    'subjects',
    'buddy',
    'plan',
    'homework',
    'exams',
    'practice',
    'progress',
    'journey',
    'parent',
    'profile',
  ];

  const CATEGORY_DISPLAY_NAMES: Record<
    'Core' | 'Learning' | 'History & Growth' | 'Family & Settings',
    string
  > = {
    Core: 'Overview',
    Learning: 'Learning Studio',
    'History & Growth': 'Academic Growth',
    'Family & Settings': 'Family & Account',
  };

  const mobileQuickTabs: ScreenId[] = [
    'dashboard',
    'subjects',
    'buddy',
    'plan',
    'homework',
  ];

  if (showOpeningSplash) {
    return (
      <OpeningSplashAnimation
        onAnimationFinished={() => setShowOpeningSplash(false)}
        isSessionReady={!isCheckingSession}
        statusMessage={isCheckingSession ? 'Checking secure cloud session...' : 'Ready to learn'}
      />
    );
  }

  if (isCheckingSession) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#101B35] text-white">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-[#35D6E8] border-t-transparent animate-spin" />
          <p className="text-xs font-bold text-indigo-200">Restoring your SparkMinds session...</p>
        </div>
      </div>
    );
  }

  // Part 4 & 5: First-Time 5-Slide Introduction Tour (+ Replay Introduction)
  if (showIntroTour) {
    return (
      <FirstTimeIntroTour
        isReplay={isIntroReplay}
        onGetStarted={() => handleCompleteIntroTour(true)}
        onSkip={() => handleCompleteIntroTour(false)}
      />
    );
  }

  // 1. MODERN SPLIT-PANEL REGISTRATION & SIGN-IN PAGE (Part 2 Theme + Sparky Mascot)
  if (activeScreen === 'auth') {
    return (
      <div className="min-h-screen grid lg:grid-cols-12 bg-white text-[#202943]">
        {/* Left Brand Panel (#101B35 Deep Midnight Blue -> #5146E5 Rich Indigo + #35D6E8 Aqua) */}
        <div
          className="lg:col-span-5 text-white p-6 sm:p-9 lg:p-12 flex flex-col justify-between gap-6 lg:gap-8 relative overflow-hidden"
          style={{
            background: 'linear-gradient(155deg, #0D1630 0%, #1D275C 55%, #5146E5 100%)',
          }}
        >
          <div aria-hidden="true" className="pointer-events-none absolute inset-0 spark-hero-grid opacity-55" />
          <div
            aria-hidden="true"
            className="pointer-events-none absolute -bottom-24 -right-24 w-72 h-72 rounded-full bg-[#35D6E8]/22 blur-3xl"
          />
          <div className="relative z-10 space-y-5 sm:space-y-6">
            <EduSparkLogo size="lg" lightText />

            <div className="flex items-center gap-4 pt-1">
              <SparkRobotMascot mood="welcome" size="lg" />
              <div className="space-y-2 min-w-0">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/10 border border-[#35D6E8]/40 text-[#35D6E8] text-xs font-extrabold">
                  {BRAND_DESCRIPTION}
                </span>
                <h1 className="font-display text-2xl sm:text-[1.85rem] font-extrabold tracking-tight leading-[1.18] text-white">
                  <BrandTagline variant="dark" animate />
                </h1>
              </div>
            </div>

            <p className="text-sm text-indigo-100/90 font-medium leading-relaxed max-w-sm">
              Meet Sparky, your personal AI robot teacher with labelled visual diagrams, guided lessons, and real progress tracking for Grades 1–12.
            </p>

            {/* 3 Clean Visual Feature Highlights */}
            <div className="space-y-3 pt-1">
              {[
                {
                  title: 'AI Robot Teacher with Visual Diagrams',
                  desc: 'Step-by-step teaching with interactive models in 23 languages.',
                },
                {
                  title: 'Guided Interactive Lessons',
                  desc: 'One concept at a time with instant encouraging feedback.',
                },
                {
                  title: 'Smart Study Plans & Real Progress',
                  desc: 'Fits around your real day and tracks actual mastery.',
                },
              ].map((item, idx) => (
                <div
                  key={item.title}
                  className="p-3.5 rounded-2xl bg-[#101B35]/60 backdrop-blur border border-white/15 flex items-start gap-3"
                >
                  <span className="w-7 h-7 rounded-xl bg-[#35D6E8]/20 border border-[#35D6E8]/45 text-[#35D6E8] text-xs font-extrabold flex items-center justify-center shrink-0">
                    {idx + 1}
                  </span>
                  <div>
                    <div className="text-xs font-extrabold text-white">{item.title}</div>
                    <div className="text-[11px] text-indigo-100/80 mt-0.5">{item.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="relative z-10 flex flex-wrap items-center justify-between gap-2 text-[11px] font-semibold text-indigo-200/80">
            <span>SparkMinds AI • CBSE, ICSE &amp; State Boards</span>
            <button
              type="button"
              onClick={handleReplayIntro}
              className="text-[#35D6E8] hover:underline font-extrabold"
            >
              Replay Introduction →
            </button>
          </div>
        </div>

        {/* Right Form Panel (#F6F7FC Clean Soft Canvas + Crisp White Card) */}
        <div className="lg:col-span-7 flex flex-col justify-center items-center p-5 sm:p-8 lg:p-12 bg-[#F6F7FC] overflow-y-auto">
          <div className="w-full max-w-md bg-white rounded-3xl p-6 sm:p-8 shadow-lg shadow-[#101B35]/5 border border-[#E4E8F5] space-y-5 animate-fade-in">
            {/* Crisp Pill Mode Switcher */}
            <div className="grid grid-cols-2 gap-1.5 p-1 rounded-2xl bg-[#EEEAFE] border border-[#5146E5]/15 text-xs font-extrabold">
              <button
                type="button"
                onClick={() => {
                  setAuthPortalTab('register');
                  setAuthFeedbackMsg(null);
                }}
                className={`py-2.5 rounded-xl transition min-h-[42px] ${
                  authPortalTab === 'register'
                    ? 'bg-[#5146E5] text-white shadow-sm'
                    : 'text-[#202943] hover:text-[#5146E5]'
                }`}
              >
                Register
              </button>
              <button
                type="button"
                onClick={() => {
                  setAuthPortalTab('login');
                  setAuthFeedbackMsg(null);
                }}
                className={`py-2.5 rounded-xl transition min-h-[42px] ${
                  authPortalTab === 'login'
                    ? 'bg-[#5146E5] text-white shadow-sm'
                    : 'text-[#202943] hover:text-[#5146E5]'
                }`}
              >
                Sign In
              </button>
            </div>

            {authFeedbackMsg && (
              <div
                className={`p-3.5 rounded-2xl text-xs font-extrabold border ${
                  authFeedbackMsg.type === 'ok'
                    ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                    : 'bg-rose-50 border-rose-200 text-rose-800'
                }`}
              >
                {authFeedbackMsg.text}
              </div>
            )}

            {/* TAB: SIGN IN */}
            {authPortalTab === 'login' && (
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSignInSubmit();
                }}
                className="space-y-4"
              >
                <div>
                  <h3 className="text-xl font-extrabold text-slate-900 tracking-tight">Sign In</h3>
                  <p className="text-xs text-slate-500 mt-1">
                    Sign in to access your saved profile, timetable, homework, and academic progress
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 text-xs font-bold text-amber-900">
                  Are you under 8 years old? Please use your parent&apos;s help to sign in.
                </div>

                <div className="space-y-1.5">
                  <label className="block text-xs font-extrabold text-slate-800">
                    Student ID, Email or Username <span className="text-rose-600">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={loginIdentifierInput}
                    onChange={(e) => setLoginIdentifierInput(e.target.value)}
                    placeholder="Student ID, Email or Username"
                    className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="block text-xs font-extrabold text-slate-800">
                    Password or PIN <span className="text-rose-600">*</span>
                  </label>
                  <input
                    type="password"
                    required
                    value={loginPasswordInput}
                    onChange={(e) => setLoginPasswordInput(e.target.value)}
                    placeholder="Password or PIN"
                    className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full py-3 rounded-xl bg-[#5146E5] hover:bg-[#4338CA] text-white text-sm font-extrabold shadow-md shadow-[#5146E5]/20 transition min-h-[46px]"
                >
                  Sign In
                </button>

                <div className="flex items-center justify-between text-xs pt-1">
                  <button
                    type="button"
                    onClick={() => {
                      setAuthPortalTab('recover');
                      setAuthFeedbackMsg(null);
                    }}
                    className="font-bold text-slate-500 hover:text-blue-600 hover:underline"
                  >
                    Forgot Password / PIN?
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setAuthPortalTab('register');
                      setAuthFeedbackMsg(null);
                    }}
                    className="font-bold text-blue-600 hover:underline"
                  >
                    New user? Register
                  </button>
                </div>
              </form>
            )}

            {/* TAB: REGISTER */}
            {authPortalTab === 'register' && (
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleRegisterSubmit();
                }}
                className="space-y-4"
              >
                <div>
                  <h3 className="text-xl font-extrabold text-slate-900 tracking-tight">Register</h3>
                  <p className="text-xs text-slate-500 mt-1">
                    Create your personal SparkMinds AI learning account for Grades 1–12
                  </p>
                </div>

                <div className="space-y-1.5">
                  <label className="block text-xs font-extrabold text-slate-800">
                    Student Full Name <span className="text-rose-600">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={customStudentNameInput}
                    onChange={(e) => setCustomStudentNameInput(e.target.value)}
                    placeholder="Student Full Name"
                    className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="space-y-1.5">
                    <label className="block text-xs font-extrabold text-slate-800">
                      Age (Years) <span className="text-rose-600">*</span>
                    </label>
                    <div className="flex items-center gap-1.5">
                      <button
                        type="button"
                        onClick={() => {
                          const next = Math.max(4, customAgeInput - 1);
                          setCustomAgeInput(next);
                          setCustomDobInput(calculateDobFromAge(next, customDobInput));
                          if (next < 8) setUnder8ConsentVerified(false);
                        }}
                        className="w-10 h-10 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 font-extrabold text-lg flex items-center justify-center border border-slate-300 transition shrink-0 cursor-pointer"
                        title="Decrease age by 1 year"
                      >
                        −
                      </button>
                      <input
                        type="number"
                        min={4}
                        max={20}
                        required
                        value={customAgeInput === 0 ? '' : customAgeInput}
                        onChange={(e) => {
                          const raw = e.target.value;
                          if (raw === '') {
                            setCustomAgeInput(0);
                            return;
                          }
                          const val = parseInt(raw, 10);
                          if (!isNaN(val)) {
                            setCustomAgeInput(val);
                            if (val >= 4 && val <= 20) {
                              setCustomDobInput(calculateDobFromAge(val, customDobInput));
                              if (val < 8) setUnder8ConsentVerified(false);
                            }
                          }
                        }}
                        onBlur={() => {
                          const safe = Math.max(4, Math.min(20, customAgeInput || 12));
                          setCustomAgeInput(safe);
                          setCustomDobInput(calculateDobFromAge(safe, customDobInput));
                          if (safe < 8) setUnder8ConsentVerified(false);
                        }}
                        className="w-full text-center rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
                        title="Editable student age"
                      />
                      <button
                        type="button"
                        onClick={() => {
                          const next = Math.min(20, customAgeInput + 1);
                          setCustomAgeInput(next);
                          setCustomDobInput(calculateDobFromAge(next, customDobInput));
                          if (next < 8) setUnder8ConsentVerified(false);
                        }}
                        className="w-10 h-10 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 font-extrabold text-lg flex items-center justify-center border border-slate-300 transition shrink-0 cursor-pointer"
                        title="Increase age by 1 year"
                      >
                        +
                      </button>
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <label className="block text-xs font-extrabold text-slate-800">
                      Date of Birth <span className="text-rose-600">*</span>
                    </label>
                    <input
                      type="date"
                      required
                      value={customDobInput}
                      onChange={(e) => {
                        const val = e.target.value;
                        setCustomDobInput(val);
                        if (val) {
                          const calcAge = calculateAgeFromDobString(val);
                          if (calcAge !== null) {
                            setCustomAgeInput(calcAge);
                            if (calcAge < 8) {
                              setUnder8ConsentVerified(false);
                            }
                          }
                        }
                      }}
                      className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="space-y-1.5">
                    <label className="block text-xs font-extrabold text-slate-800">
                      Class / Grade
                    </label>
                    <select
                      value={onboarding.grade}
                      onChange={(e) => {
                        const g = Number(e.target.value) as GradeNumber;
                        setOnboarding((prev) => ({ ...prev, grade: g }));
                      }}
                      className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
                    >
                      {([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] as GradeNumber[]).map((g) => (
                        <option key={g} value={g}>
                          Grade {g}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="space-y-1.5">
                    <label className="block text-xs font-extrabold text-slate-800">
                      School Board
                    </label>
                    <select
                      value={onboarding.board}
                      onChange={(e) => {
                        setOnboarding((prev) => ({
                          ...prev,
                          board: e.target.value as 'CBSE' | 'ICSE' | 'STATE' | 'OTHER',
                        }));
                      }}
                      className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
                    >
                      <option value="CBSE">CBSE</option>
                      <option value="ICSE">ICSE</option>
                      <option value="STATE">State Board</option>
                      <option value="OTHER">Other Board</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="space-y-1.5">
                    <label className="block text-xs font-extrabold text-slate-800">
                      Unique Username <span className="text-rose-600">*</span>
                    </label>
                    <input
                      type="text"
                      required
                      autoComplete="username"
                      value={customUsernameInput}
                      onChange={(e) => setCustomUsernameInput(e.target.value)}
                      placeholder="Choose a unique username"
                      className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-xs font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="block text-xs font-extrabold text-slate-800">
                      Password or PIN <span className="text-rose-600">*</span>
                    </label>
                    <input
                      type="password"
                      required
                      autoComplete="new-password"
                      value={customPasswordInput}
                      onChange={(e) => setCustomPasswordInput(e.target.value)}
                      placeholder="Minimum 4 characters or digits"
                      className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-xs font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
                    />
                  </div>
                </div>

                <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2.5">
                  <div className="flex items-center justify-between gap-2">
                    <label className="block text-xs font-extrabold text-slate-800">
                      Student Email Address (Verification Required) <span className="text-rose-600">*</span>
                    </label>
                    {emailVerificationToken && (
                      <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-extrabold shrink-0">
                        ✓ Verified
                      </span>
                    )}
                  </div>
                  <div className="flex flex-col sm:flex-row gap-2">
                    <input
                      type="email"
                      required
                      autoComplete="email"
                      value={customEmailInput}
                      onChange={(e) => {
                        setCustomEmailInput(e.target.value);
                        setEmailVerificationToken('');
                        setEmailVerifyCodeSent(false);
                        setEmailVerifyCodeInput('');
                        setEmailOtpExpired(false);
                        setEmailVerifyStatusMsg('');
                      }}
                      placeholder="Enter your email address"
                      className="flex-1 rounded-xl border border-slate-300 bg-white px-3 py-2 text-xs font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
                    />
                    <button
                      type="button"
                      disabled={emailOtpSending || emailResendCooldown > 0}
                      onClick={handleSendEmailVerificationCode}
                      className={`px-3.5 py-2 rounded-xl text-[11px] font-extrabold shrink-0 transition ${
                        emailOtpSending || emailResendCooldown > 0
                          ? 'bg-slate-300 text-slate-600 cursor-not-allowed'
                          : 'bg-slate-900 hover:bg-slate-800 text-white'
                      }`}
                    >
                      {emailOtpSending
                        ? 'Sending...'
                        : emailResendCooldown > 0
                          ? `Resend in ${emailResendCooldown}s`
                          : emailVerifyCodeSent
                            ? 'Resend Code'
                            : 'Send Code'}
                    </button>
                  </div>
                  {emailVerifyCodeSent && !emailVerificationToken && (
                    <div className="p-3 rounded-xl bg-white border border-indigo-200 space-y-2">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-[11px] font-extrabold text-slate-800">
                          Enter 6-Digit Verification Code
                        </span>
                        <span className="text-[10px] font-bold text-slate-500">
                          Expires in 5 minutes
                        </span>
                      </div>
                      <div className="flex flex-col sm:flex-row gap-2">
                        <input
                          type="text"
                          inputMode="numeric"
                          pattern="[0-9]*"
                          maxLength={6}
                          autoComplete="one-time-code"
                          value={emailVerifyCodeInput}
                          onChange={(e) =>
                            setEmailVerifyCodeInput(e.target.value.replace(/\D/g, '').slice(0, 6))
                          }
                          placeholder="Enter 6-digit code from your email"
                          className="flex-1 rounded-xl border border-slate-300 bg-white px-3 py-2 text-xs font-extrabold tracking-widest text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
                        />
                        <button
                          type="button"
                          disabled={emailOtpVerifying || emailVerifyCodeInput.trim().length !== 6}
                          onClick={handleVerifyEmailCode}
                          className={`px-3.5 py-2 rounded-xl text-[11px] font-extrabold shrink-0 transition ${
                            emailOtpVerifying || emailVerifyCodeInput.trim().length !== 6
                              ? 'bg-emerald-300 text-white cursor-not-allowed'
                              : 'bg-emerald-600 hover:bg-emerald-700 text-white'
                          }`}
                        >
                          {emailOtpVerifying ? 'Verifying...' : 'Verify Email'}
                        </button>
                      </div>
                      <div className="flex flex-wrap items-center justify-between gap-2 text-[10px] text-slate-500 font-semibold">
                        <span>Check your inbox and spam folder. Never share this code.</span>
                        {emailOtpExpired && (
                          <button
                            type="button"
                            disabled={emailOtpSending || emailResendCooldown > 0}
                            onClick={handleSendEmailVerificationCode}
                            className="font-extrabold text-indigo-700 hover:underline disabled:text-slate-400 disabled:no-underline"
                          >
                            {emailResendCooldown > 0
                              ? `Request new code in ${emailResendCooldown}s`
                              : 'Request New Code'}
                          </button>
                        )}
                      </div>
                    </div>
                  )}
                  {emailVerifyStatusMsg && (
                    <div
                      role="status"
                      aria-live="polite"
                      className={`text-[11px] font-bold rounded-lg px-2.5 py-2 border ${
                        emailVerifyStatusType === 'ok'
                          ? 'text-emerald-900 bg-emerald-50 border-emerald-200'
                          : emailVerifyStatusType === 'err'
                            ? 'text-rose-900 bg-rose-50 border-rose-200'
                            : 'text-blue-900 bg-blue-50 border-blue-200'
                      }`}
                    >
                      {emailVerifyStatusMsg}
                    </div>
                  )}
                  <div className="text-[10px] text-slate-500 font-semibold">
                    One student, one account: each verified email address can create only one personal student account. Siblings can each use their own student email and username.
                  </div>
                </div>

                {/* Under-8 Parental Consent Gate if effectiveStudentAge < 8 */}
                {isUnder8Student && (
                  <div className="p-4 rounded-2xl bg-amber-50 border-2 border-amber-300 space-y-3">
                    <div className="p-3 rounded-xl bg-white border border-amber-200 text-sm font-extrabold text-amber-950 leading-relaxed shadow-sm">
                      Please use your parent&apos;s help to sign in.
                    </div>

                    <div className="text-[11px] font-bold text-slate-700">
                      Verify Parent (Under-8 Child Safety Mode): A parent or legal guardian must complete all mandatory consent fields below.
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs">
                      <div>
                        <label className="block text-[11px] font-extrabold text-slate-800">
                          Parent / Guardian Full Name *
                        </label>
                        <input
                          type="text"
                          value={parentFullName}
                          onChange={(e) => setParentFullName(e.target.value)}
                          placeholder="Parent or guardian full name"
                          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-bold"
                        />
                      </div>
                      <div>
                        <label className="block text-[11px] font-extrabold text-slate-800">
                          Relationship to Child *
                        </label>
                        <select
                          value={parentRelationship}
                          onChange={(e) =>
                            setParentRelationship(
                              e.target.value as 'Mother' | 'Father' | 'Legal Guardian'
                            )
                          }
                          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-bold"
                        >
                          <option value="Mother">Mother</option>
                          <option value="Father">Father</option>
                          <option value="Legal Guardian">Legal Guardian</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-[11px] font-extrabold text-slate-800">
                          Parent / Guardian Email *
                        </label>
                        <input
                          type="email"
                          value={parentEmail}
                          onChange={(e) => setParentEmail(e.target.value)}
                          placeholder="Parent or guardian email address"
                          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-bold"
                        />
                      </div>
                      <div>
                        <label className="block text-[11px] font-extrabold text-slate-800">
                          Parent PIN *
                        </label>
                        <input
                          type="password"
                          value={parentPin}
                          onChange={(e) => setParentPin(e.target.value)}
                          placeholder="Enter 4-8 digit parent PIN"
                          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-bold"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-[11px] font-extrabold text-slate-800">
                        Signed Guardian Legal Attestation Statement *
                      </label>
                      <input
                        type="text"
                        value={parentAttestationText}
                        onChange={(e) => setParentAttestationText(e.target.value)}
                        className="w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-bold"
                      />
                    </div>

                    {consentErrorMsg && (
                      <div className="text-xs font-bold text-rose-700 bg-rose-50 border border-rose-200 rounded-lg px-3 py-2">
                        {consentErrorMsg}
                      </div>
                    )}
                    {consentSuccessMsg && (
                      <div className="text-xs font-bold text-emerald-800 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2">
                        {consentSuccessMsg}
                      </div>
                    )}

                    <button
                      type="button"
                      onClick={async () => {
                        setConsentErrorMsg('');
                        setConsentSuccessMsg('');
                        const trimmed = customStudentNameInput.trim();
                        if (!trimmed) {
                          setConsentErrorMsg('Please enter student full name above first.');
                          return;
                        }
                        if (!parentFullName.trim() || !parentEmail.trim() || !parentPin.trim() || !parentAttestationText.trim()) {
                          setConsentErrorMsg('Please complete all mandatory parent consent fields.');
                          return;
                        }
                        const baseSlug = (customUsernameInput.trim() || trimmed)
                          .toLowerCase()
                          .replace(/[^a-z0-9]+/g, '_')
                          .replace(/^_+|_+$/g, '');
                        const newStudentId = `stu_${baseSlug || 'student'}`;
                        try {
                          const res = await fetch('/api/auth/parental-consent', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                              student_id: newStudentId,
                              parent_full_name: parentFullName.trim(),
                              relationship_to_child: parentRelationship,
                              parent_email: parentEmail.trim(),
                              parent_pin_code: parentPin.trim(),
                              guardian_attestation_statement: parentAttestationText.trim(),
                              child_safety_mode_enabled: true,
                            }),
                          });
                          const data = await res.json();
                          if (!res.ok) {
                            setConsentErrorMsg(
                              data.detail || 'Parent verification failed. Please check all mandatory fields.'
                            );
                            setUnder8ConsentVerified(false);
                            return;
                          }
                          setUnder8ConsentVerified(true);
                          const ts = data.consent_timestamp ? ` (${data.consent_timestamp})` : '';
                          const disclaimer = data.consent_disclaimer ? ` ${data.consent_disclaimer}` : '';
                          setConsentSuccessMsg(
                            `✓ Parent consent recorded for ${parentFullName.trim()}${ts}.${disclaimer}`
                          );
                          setOnboarding((prev) => ({
                            ...prev,
                            studentId: newStudentId,
                            studentName: trimmed,
                            age: effectiveStudentAge,
                            grade: (effectiveStudentAge <= 6 ? 1 : 2) as GradeNumber,
                          }));
                        } catch {
                          setConsentErrorMsg('Unable to reach server for Verify Parent. Please try again.');
                          setUnder8ConsentVerified(false);
                        }
                      }}
                      className="w-full py-2.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-xs font-extrabold shadow-sm transition"
                    >
                      {under8ConsentVerified
                        ? '✓ Parent Consent Recorded — Ready to Proceed'
                        : 'Verify Parent & Enable Child Safety Mode'}
                    </button>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={isUnder8Student && !under8ConsentVerified}
                  className={`w-full py-3 rounded-xl text-xs font-extrabold shadow-sm transition min-h-[46px] ${
                    isUnder8Student && !under8ConsentVerified
                      ? 'bg-slate-400 text-white cursor-not-allowed'
                      : 'bg-[#5146E5] hover:bg-[#4338CA] text-white shadow-md shadow-[#5146E5]/20'
                  }`}
                >
                  {isUnder8Student && !under8ConsentVerified
                    ? '🔒 Parent Verification Required (Under 8)'
                    : 'Register'}
                </button>

                <div className="text-center text-xs pt-1">
                  <button
                    type="button"
                    onClick={() => {
                      setAuthPortalTab('login');
                      setAuthFeedbackMsg(null);
                    }}
                    className="font-bold text-blue-600 hover:underline"
                  >
                    Already have an account? Sign in
                  </button>
                </div>
              </form>
            )}

            {/* TAB: RECOVER */}
            {authPortalTab === 'recover' && (
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleRecoverySubmit();
                }}
                className="space-y-4"
              >
                <div>
                  <h3 className="text-xl font-extrabold text-slate-900 tracking-tight">Recover Account</h3>
                </div>

                <div className="space-y-1.5">
                  <label className="block text-xs font-extrabold text-slate-800">
                    Student ID, Username, or Email <span className="text-rose-600">*</span>
                  </label>
                  <div className="flex flex-col sm:flex-row gap-2">
                    <input
                      type="text"
                      required
                      value={recoveryIdentifierInput}
                      onChange={(e) => setRecoveryIdentifierInput(e.target.value)}
                      placeholder="Student ID, Username, or Email"
                      className="flex-1 rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-xs font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
                    />
                    <button
                      type="button"
                      disabled={recoverySending || recoveryResendCooldown > 0}
                      onClick={handleRequestRecoveryCode}
                      className={`px-3.5 py-2 rounded-xl text-[11px] font-extrabold shrink-0 transition ${
                        recoverySending || recoveryResendCooldown > 0
                          ? 'bg-slate-300 text-slate-600 cursor-not-allowed'
                          : 'bg-slate-900 hover:bg-slate-800 text-white'
                      }`}
                    >
                      {recoverySending
                        ? 'Sending...'
                        : recoveryResendCooldown > 0
                          ? `Resend in ${recoveryResendCooldown}s`
                          : 'Send Code'}
                    </button>
                  </div>
                  {recoveryRequestMsg && (
                    <div
                      role="status"
                      aria-live="polite"
                      className={`text-[11px] font-bold rounded-lg px-2.5 py-1.5 border ${
                        recoveryRequestType === 'err'
                          ? 'text-rose-900 bg-rose-50 border-rose-200'
                          : 'text-blue-900 bg-blue-50 border-blue-200'
                      }`}
                    >
                      {recoveryRequestMsg}
                    </div>
                  )}
                </div>

                <div className="space-y-1.5">
                  <label className="block text-xs font-extrabold text-slate-800">
                    Recovery Code, Date of Birth, or Parent PIN <span className="text-rose-600">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={recoveryProofInput}
                    onChange={(e) => setRecoveryProofInput(e.target.value)}
                    placeholder="6-digit Recovery Code, YYYY-MM-DD DOB, or Parent PIN"
                    className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-xs font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="block text-xs font-extrabold text-slate-800">
                    New Password or PIN <span className="text-rose-600">*</span>
                  </label>
                  <input
                    type="password"
                    required
                    value={recoveryNewPinInput}
                    onChange={(e) => setRecoveryNewPinInput(e.target.value)}
                    placeholder="New Password or PIN"
                    className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-xs font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full py-2.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-xs font-extrabold shadow-sm transition"
                >
                  Reset Password / PIN
                </button>

                <div className="text-center text-xs pt-1">
                  <button
                    type="button"
                    onClick={() => {
                      setAuthPortalTab('login');
                      setAuthFeedbackMsg(null);
                    }}
                    className="font-bold text-blue-600 hover:underline"
                  >
                    Back to Sign In
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`min-h-screen flex flex-col md:flex-row eduspark-mesh-bg text-slate-900 ${gradeMeta.cssClass}`}
    >
      {/* GLOBAL AGE QUICK EDITOR MODAL */}
      <AgeQuickEditorModal
        isOpen={showAgeQuickModal}
        onClose={() => setShowAgeQuickModal(false)}
        currentAge={onboarding.age}
        currentDob={profileEditDob || customDobInput}
        studentName={onboarding.studentName}
        onSaveAge={async (age, dob) => {
          const ok = await handleSaveProfileAgeAndDetails(age, dob);
          return ok;
        }}
        onGoToProfile={() => {
          setShowAgeQuickModal(false);
          setActiveScreen('profile');
        }}
      />

      {/* 2. CLICK-BY-CLICK INTERACTIVE FEATURE SPOTLIGHT TOUR (Part 10) */}
      <FeatureSpotlightTour
        isOpen={showTutorial}
        onClose={handleTutorialClose}
        onNavigateScreen={setActiveScreen}
        studentName={onboarding.studentName}
      />

      {/* SLEEK MODERN SAAS LEFT SIDEBAR (#101B35 Deep Midnight Blue + #5146E5 Indigo + #35D6E8 Aqua) */}
      <aside
        className={`hidden md:flex md:flex-col md:fixed md:inset-y-0 bg-[#101B35] text-white border-r border-indigo-950/80 z-20 transition-all duration-200 ${
          sidebarCollapsed ? 'md:w-[72px]' : 'md:w-64'
        }`}
      >
        <div className="h-16 px-4 border-b border-white/10 flex items-center justify-between gap-2 shrink-0">
          {!sidebarCollapsed ? (
            <div
              onClick={() => setActiveScreen('dashboard')}
              className="cursor-pointer transition-opacity hover:opacity-90"
            >
              <EduSparkLogo size="sm" lightText />
            </div>
          ) : (
            <div
              onClick={() => setActiveScreen('dashboard')}
              className="mx-auto cursor-pointer"
              title="SparkMinds AI"
            >
              <EduSparkLogo size="sm" lightText />
            </div>
          )}
          <button
            type="button"
            onClick={() => setSidebarCollapsed((prev) => !prev)}
            className="p-1.5 rounded-lg bg-white/5 hover:bg-white/15 text-indigo-200 hover:text-white transition text-xs font-bold shrink-0"
            title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {sidebarCollapsed ? '»' : '«'}
          </button>
        </div>

        {/* Clean Executive Navigation (Primary Core Items + Collapsible More Tools) */}
        <nav className="flex-1 overflow-y-auto px-2.5 py-4 space-y-5" aria-label="Main navigation">
          {(
            ['Core', 'Learning', 'History & Growth', 'Family & Settings'] as const
          ).map((category) => {
            const primaryItems = ALL_18_SCREENS.filter(
              (s) => s.category === category && PRIMARY_SIDEBAR_SCREENS.includes(s.id)
            );
            if (primaryItems.length === 0) return null;
            return (
              <div key={category}>
                {!sidebarCollapsed && (
                  <div className="px-3 mb-1.5 text-[10px] font-bold uppercase tracking-widest text-indigo-300/65">
                    {CATEGORY_DISPLAY_NAMES[category]}
                  </div>
                )}
                <div className="space-y-0.5">
                  {primaryItems.map((screen) => {
                    const isActive = activeScreen === screen.id;
                    return (
                      <button
                        key={screen.id}
                        type="button"
                        data-tour-id={`nav-${screen.id}`}
                        onClick={() => setActiveScreen(screen.id)}
                        title={screen.title}
                        className={`group relative w-full flex items-center ${
                          sidebarCollapsed ? 'justify-center px-2 py-2.5' : 'gap-3 px-3 py-2.5'
                        } rounded-xl text-left text-xs transition-all duration-150 ${
                          isActive
                            ? 'bg-gradient-to-r from-[#5146E5] to-[#4338CA] text-white font-extrabold shadow-md shadow-[#5146E5]/35'
                            : 'text-indigo-100/80 hover:bg-white/[0.08] hover:text-white font-semibold'
                        }`}
                      >
                        {isActive && (
                          <span className="absolute left-0 inset-y-2 w-1 rounded-r-full bg-[#35D6E8]" />
                        )}
                        <span
                          className={`shrink-0 transition-colors ${
                            isActive
                              ? 'text-[#35D6E8]'
                              : 'text-indigo-300/80 group-hover:text-[#35D6E8]'
                          }`}
                        >
                          {SCREEN_ICONS[screen.id]}
                        </span>
                        {!sidebarCollapsed && <span className="truncate">{screen.title}</span>}
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}

          {/* Collapsible More Tools keeping all 18 screens 100% accessible without clutter */}
          <div className="pt-2 border-t border-white/10">
            <button
              type="button"
              onClick={() => setShowMoreNavTools((v) => !v)}
              className={`w-full flex items-center ${
                sidebarCollapsed ? 'justify-center px-2 py-2' : 'justify-between px-3 py-2'
              } rounded-xl text-[11px] font-bold text-indigo-300/80 hover:text-white hover:bg-white/[0.06] transition`}
              title="More Tools"
            >
              {!sidebarCollapsed ? (
                <>
                  <span>More Tools</span>
                  <span>{showMoreNavTools ? '▴' : '▾'}</span>
                </>
              ) : (
                <span>•••</span>
              )}
            </button>
            {showMoreNavTools && (
              <div className="space-y-0.5 mt-1">
                {ALL_18_SCREENS.filter((s) => !PRIMARY_SIDEBAR_SCREENS.includes(s.id)).map(
                  (screen) => {
                    const isActive = activeScreen === screen.id;
                    return (
                      <button
                        key={screen.id}
                        type="button"
                        data-tour-id={`nav-${screen.id}`}
                        onClick={() => setActiveScreen(screen.id)}
                        title={screen.title}
                        className={`group relative w-full flex items-center ${
                          sidebarCollapsed ? 'justify-center px-2 py-2' : 'gap-3 px-3 py-2'
                        } rounded-xl text-left text-xs transition-all duration-150 ${
                          isActive
                            ? 'bg-[#5146E5] text-white font-extrabold'
                            : 'text-indigo-200/70 hover:bg-white/[0.08] hover:text-white font-medium'
                        }`}
                      >
                        <span className={isActive ? 'text-[#35D6E8]' : 'text-indigo-300/70'}>
                          {SCREEN_ICONS[screen.id]}
                        </span>
                        {!sidebarCollapsed && <span className="truncate">{screen.title}</span>}
                      </button>
                    );
                  }
                )}
              </div>
            )}
          </div>
        </nav>

        {/* Clean Minimal Bottom Student Strip */}
        <div className="p-3 border-t border-white/10 bg-[#0B1328] space-y-2">
          {!sidebarCollapsed ? (
            <div className="flex items-center justify-between gap-2">
              <button
                type="button"
                onClick={() => setActiveScreen('profile')}
                className="flex items-center gap-2.5 min-w-0 text-left group"
              >
                <div className="w-8 h-8 rounded-xl bg-[#35D6E8] text-[#101B35] font-extrabold text-xs flex items-center justify-center shrink-0">
                  {(onboarding.studentName || 'S').charAt(0)}
                </div>
                <div className="min-w-0">
                  <div className="text-xs font-extrabold text-white truncate group-hover:text-[#35D6E8] transition">
                    {onboarding.studentName &&
                    !['Aarav Sharma', 'Ananya Reddy', 'Diya Nair', 'Karthik Rajan', 'Riya Verma', 'Student Learner'].includes(
                      onboarding.studentName
                    )
                      ? onboarding.studentName
                      : 'My Profile'}
                  </div>
                  <div className="text-[11px] text-indigo-300/80 truncate">
                    Grade {onboarding.grade} • {onboarding.board}
                  </div>
                </div>
              </button>
              <button
                type="button"
                onClick={handleReplayTutorial}
                className="p-2 rounded-lg bg-white/10 hover:bg-[#5146E5] text-[#35D6E8] hover:text-white transition shrink-0"
                title="Replay Feature Tour"
                aria-label="Replay Feature Tour"
              >
                <HelpCircle className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={handleReplayTutorial}
              className="w-full flex items-center justify-center p-2 rounded-lg bg-white/10 hover:bg-[#5146E5] text-[#35D6E8] hover:text-white transition"
              title="Replay Feature Tour"
            >
              <HelpCircle className="w-4 h-4" />
            </button>
          )}
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <div
        className={`flex-1 flex flex-col min-h-screen pb-20 md:pb-8 transition-all duration-200 ${
          sidebarCollapsed ? 'md:pl-[72px]' : 'md:pl-64'
        }`}
      >
        {/* Frosted Glass Executive Top Bar */}
        <header className="sticky top-0 z-10 h-16 bg-white/85 backdrop-blur-xl border-b border-[#DFE5F6] px-4 sm:px-6 lg:px-8 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <button
              type="button"
              onClick={() => setShowMobileMenuDrawer(true)}
              className="md:hidden inline-flex items-center justify-center w-10 h-10 rounded-xl bg-[#101B35] text-[#35D6E8] hover:bg-[#5146E5] hover:text-white transition shrink-0"
              aria-label="Open Navigation Menu"
              title="Open Navigation Menu"
            >
              <Menu className="w-5 h-5" />
            </button>
            <h1 className="font-display text-lg md:text-xl font-bold text-[#101B35] tracking-tight truncate">
              {currentScreenDef.title}
            </h1>
            <span className="hidden xl:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#EEEAFE] border border-[#5146E5]/15 text-[11px] font-bold text-[#5146E5]">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span>Sparky AI Active</span>
            </span>
          </div>

          <div className="flex items-center gap-2 text-xs relative shrink-0">
            {/* Notifications Bell */}
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowNotificationsDrawer((prev) => !prev)}
                className="relative inline-flex items-center justify-center w-10 h-10 rounded-xl border border-[#DCE2F5] bg-white hover:bg-[#EEEAFE] text-[#101B35] transition"
                aria-label="Notifications"
                title="Notifications & Reminders"
              >
                <Bell className="w-4 h-4" />
                {unreadNotificationsCount > 0 && (
                  <span className="absolute -top-1 -right-1 min-w-[18px] h-[18px] px-1 rounded-full bg-rose-600 text-white text-[10px] font-extrabold flex items-center justify-center">
                    {unreadNotificationsCount}
                  </span>
                )}
              </button>

              {showNotificationsDrawer && (
                <div className="fixed inset-x-3 top-[4.25rem] sm:absolute sm:inset-x-auto sm:right-0 sm:top-auto sm:mt-2 w-auto sm:w-[430px] max-h-[78vh] overflow-y-auto rounded-2xl bg-white border border-slate-200 shadow-2xl p-4 z-50 space-y-3">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                    <div>
                      <div className="text-xs font-extrabold text-slate-900">
                        Daily Task Reminders & Notifications (12-Hr AM/PM)
                      </div>
                      <div className="text-[11px] text-slate-500">
                        {onboarding.studentName} • Grade {onboarding.grade} • TZ: {reminderPrefs.timezone_name || 'Asia/Kolkata'}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={handleMarkAllNotificationsRead}
                        className="px-2 py-1 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px] font-extrabold hover:bg-emerald-100"
                      >
                        Mark All Read
                      </button>
                      <button
                        type="button"
                        onClick={() => setShowReminderPrefsForm((p) => !p)}
                        className="px-2 py-1 rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-200 text-[10px] font-extrabold hover:bg-indigo-100"
                      >
                        {showReminderPrefsForm ? 'Hide Settings' : '⚙ Customise'}
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setShowNotificationsDrawer(false);
                        }}
                        className="text-[11px] font-bold text-blue-600 hover:underline"
                      >
                        Close ✕
                      </button>
                    </div>
                  </div>

                  {pushStatusNotice && (
                    <div className="text-[11px] font-bold text-blue-900 bg-blue-50 border border-blue-200 rounded-xl px-3 py-2">
                      {pushStatusNotice}
                    </div>
                  )}

                  {showReminderPrefsForm && (
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-2.5 text-[11px]">
                      <div className="p-2 rounded-lg bg-white border border-slate-200 text-[10px] text-slate-600 leading-snug">
                        <strong>Why enable mobile push notifications?</strong> Get timely reminders for study sessions, revision alerts, streak milestones, and upcoming exams — with privacy-safe lock-screen summaries and quiet hours respected.
                      </div>
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-extrabold text-slate-800">
                          Mobile / Browser Web Push:
                        </span>
                        <button
                          type="button"
                          onClick={handleRequestAndroidNotificationPermission}
                          className="px-2.5 py-1 rounded-lg bg-blue-600 text-white font-extrabold text-[10px] hover:bg-blue-700"
                        >
                          {reminderPrefs.android_notifications_permission === 'granted'
                            ? '✓ Push Active'
                            : 'Enable Push Notifications'}
                        </button>
                      </div>

                      <div className="grid grid-cols-3 gap-1.5 items-center pt-1">
                        <label className="flex items-center gap-1 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={Boolean(reminderPrefs.quiet_hours_enabled ?? true)}
                            onChange={(e) =>
                              handleSaveReminderPrefs({
                                ...reminderPrefs,
                                quiet_hours_enabled: e.target.checked,
                              })
                            }
                            className="rounded border-slate-300 text-blue-600"
                          />
                          <span className="text-[10px] font-extrabold text-slate-700">Quiet Hours</span>
                        </label>
                        <input
                          type="time"
                          value={reminderPrefs.quiet_hours_start || '22:00'}
                          onChange={(e) =>
                            handleSaveReminderPrefs({
                              ...reminderPrefs,
                              quiet_hours_start: e.target.value,
                            })
                          }
                          className="rounded border border-slate-300 px-1.5 py-0.5 text-[10px] font-bold"
                          title="Quiet hours start"
                        />
                        <input
                          type="time"
                          value={reminderPrefs.quiet_hours_end || '07:00'}
                          onChange={(e) =>
                            handleSaveReminderPrefs({
                              ...reminderPrefs,
                              quiet_hours_end: e.target.value,
                            })
                          }
                          className="rounded border border-slate-300 px-1.5 py-0.5 text-[10px] font-bold"
                          title="Quiet hours end"
                        />
                      </div>

                      <div className="flex items-center justify-between gap-2">
                        <span className="text-[10px] font-extrabold text-slate-700">Frequency:</span>
                        <select
                          value={reminderPrefs.notification_frequency || 'BALANCED'}
                          onChange={(e) =>
                            handleSaveReminderPrefs({
                              ...reminderPrefs,
                              notification_frequency: e.target.value,
                            })
                          }
                          className="rounded border border-slate-300 px-2 py-0.5 text-[10px] font-bold bg-white"
                        >
                          <option value="LOW">Low (Essential only)</option>
                          <option value="BALANCED">Balanced</option>
                          <option value="FREQUENT">Frequent</option>
                        </select>
                      </div>

                      <div className="font-extrabold text-slate-800">
                        Enable / Disable Reminder Categories:
                      </div>
                      <div className="grid grid-cols-2 gap-1.5">
                        {[
                          { key: 'daily_study_sessions_enabled', label: 'Daily Study Sessions' },
                          { key: 'pending_chapters_enabled', label: 'Pending Chapters' },
                          { key: 'homework_deadlines_enabled', label: 'Homework Deadlines' },
                          { key: 'upcoming_exams_enabled', label: 'Upcoming Exams' },
                          { key: 'revision_sessions_enabled', label: 'Revision Sessions' },
                          { key: 'mock_tests_enabled', label: 'Mock Tests' },
                          { key: 'streak_milestones_enabled', label: 'Streak Milestones' },
                          { key: 'learning_gap_alerts_enabled', label: 'Learning Gap Alerts' },
                        ].map((cat) => (
                          <label key={cat.key} className="flex items-center gap-1.5 cursor-pointer">
                            <input
                              type="checkbox"
                              checked={Boolean(reminderPrefs[cat.key] ?? true)}
                              onChange={(e) =>
                                handleSaveReminderPrefs({
                                  ...reminderPrefs,
                                  [cat.key]: e.target.checked,
                                })
                              }
                              className="rounded border-slate-300 text-blue-600"
                            />
                            <span className="text-[10px] font-bold text-slate-700">{cat.label}</span>
                          </label>
                        ))}
                      </div>

                      <div className="space-y-1">
                        <div className="font-extrabold text-slate-800">
                          Custom Reminder Times (12-Hour AM/PM):
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {(reminderPrefs.custom_reminder_times || ['6:00 PM', '8:00 AM']).map(
                            (tStr: string) => (
                              <span
                                key={tStr}
                                className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-100 text-amber-900 font-extrabold text-[10px]"
                              >
                                {formatTimeRange12Hour(tStr)}
                                <button
                                  type="button"
                                  onClick={() =>
                                    handleSaveReminderPrefs({
                                      ...reminderPrefs,
                                      custom_reminder_times: (
                                        reminderPrefs.custom_reminder_times || []
                                      ).filter((x: string) => x !== tStr),
                                    })
                                  }
                                  className="text-rose-700 hover:text-rose-900"
                                >
                                  ✕
                                </button>
                              </span>
                            )
                          )}
                        </div>
                        <div className="flex gap-1.5 pt-1">
                          <input
                            type="text"
                            value={customReminderTimeInput}
                            onChange={(e) => setCustomReminderTimeInput(e.target.value)}
                            placeholder="e.g. 7:30 PM"
                            className="flex-1 rounded-lg border border-slate-300 px-2 py-1 text-[10px] font-bold"
                          />
                          <button
                            type="button"
                            onClick={() => {
                              const formatted = formatTimeRange12Hour(customReminderTimeInput.trim());
                              if (formatted) {
                                const existing = reminderPrefs.custom_reminder_times || [];
                                if (!existing.includes(formatted)) {
                                  handleSaveReminderPrefs({
                                    ...reminderPrefs,
                                    custom_reminder_times: [...existing, formatted],
                                  });
                                }
                              }
                            }}
                            className="px-2.5 py-1 rounded-lg bg-slate-900 text-white font-extrabold text-[10px]"
                          >
                            + Add Time
                          </button>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="max-h-72 overflow-y-auto space-y-2">
                    {notificationsList.length === 0 ? (
                      <div className="text-xs text-slate-500 py-3 text-center">
                        All caught up! No pending reminders.
                      </div>
                    ) : (
                      notificationsList.map((n: any) => (
                        <div
                          key={n.id}
                          className="p-3 rounded-xl border border-slate-200 hover:border-blue-300 bg-slate-50/70 transition space-y-1.5"
                        >
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full bg-blue-100 text-blue-800">
                              {n.category}
                            </span>
                            <span className="text-[10px] font-bold text-amber-800">
                              {formatTimeRange12Hour(String(n.time_display || ''))}
                            </span>
                          </div>
                          <div
                            onClick={() => {
                              const mapScreen: Record<string, ScreenId> = {
                                homework: 'homework',
                                study_planner: 'plan',
                                revision: 'practice',
                                buddy: 'buddy',
                                exams: 'exams',
                              };
                              if (n.action_tab && mapScreen[n.action_tab]) {
                                setActiveScreen(mapScreen[n.action_tab]);
                              }
                              setShowNotificationsDrawer(false);
                            }}
                            className="cursor-pointer space-y-0.5"
                          >
                            <div className="font-extrabold text-xs text-slate-900 flex items-center justify-between">
                              <span>{n.title}</span>
                              {n.status && n.status !== 'Pending' && (
                                <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 font-extrabold">
                                  {n.status}
                                </span>
                              )}
                            </div>
                            <div className="text-[11px] text-slate-600 leading-snug">
                              {n.message}
                            </div>
                          </div>
                          <div className="flex items-center gap-1.5 pt-1 border-t border-slate-200/70">
                            <button
                              type="button"
                              onClick={() => handleReminderStatusAction(n, 'Completed')}
                              className="px-2 py-0.5 rounded bg-emerald-600 text-white text-[10px] font-extrabold hover:bg-emerald-700"
                            >
                              ✓ Completed
                            </button>
                            <button
                              type="button"
                              onClick={() => handleReminderStatusAction(n, 'Postponed')}
                              className="px-2 py-0.5 rounded bg-amber-500 text-white text-[10px] font-extrabold hover:bg-amber-600"
                            >
                              ⏳ Postponed
                            </button>
                            <button
                              type="button"
                              onClick={() => handleReminderStatusAction(n, 'Missed')}
                              className="px-2 py-0.5 rounded bg-rose-600 text-white text-[10px] font-extrabold hover:bg-rose-700"
                            >
                              ✕ Missed
                            </button>
                          </div>
                        </div>
                      ))
                    )}

                    {centreHistory.length > 0 && (
                      <div className="pt-2 border-t border-slate-200 space-y-1.5">
                        <div className="text-[10px] font-extrabold uppercase text-slate-500">
                          Notification Centre History
                        </div>
                        {centreHistory.slice(0, 6).map((h: any) => (
                          <div
                            key={h.notification_id}
                            onClick={() => {
                              const targetScreen = (h.action_screen || 'dashboard') as ScreenId;
                              if (ALL_18_SCREENS.some((s) => s.id === targetScreen)) {
                                setActiveScreen(targetScreen);
                              }
                              setShowNotificationsDrawer(false);
                            }}
                            className={`p-2.5 rounded-xl border text-[11px] cursor-pointer transition ${
                              h.is_read
                                ? 'bg-white border-slate-200 text-slate-600'
                                : 'bg-blue-50/60 border-blue-200 text-slate-900'
                            }`}
                          >
                            <div className="flex items-center justify-between gap-2">
                              <span className="font-extrabold">{h.title}</span>
                              {!h.is_read && (
                                <span className="px-1.5 py-0.5 rounded-full bg-blue-600 text-white text-[9px] font-extrabold">
                                  New
                                </span>
                              )}
                            </div>
                            <div className="text-[10px] text-slate-600 mt-0.5">{h.body}</div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {swUpdateAvailable && (
              <button
                type="button"
                onClick={() => {
                  if (navigator.serviceWorker?.controller) {
                    navigator.serviceWorker.controller.postMessage({ type: 'SKIP_WAITING' });
                  }
                  window.location.reload();
                }}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-cyan-500 hover:bg-cyan-600 text-slate-950 font-extrabold transition shadow-sm"
              >
                <span>↻ Update Ready — Refresh</span>
              </button>
            )}

            {pwaInstallPrompt && (
              <button
                type="button"
                onClick={async () => {
                  try {
                    await pwaInstallPrompt.prompt();
                    setPwaInstallPrompt(null);
                  } catch {
                    setPwaInstallPrompt(null);
                  }
                }}
                className="hidden xl:inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-[#101B35] text-[#35D6E8] font-extrabold transition"
                title="Install SparkMinds AI"
              >
                <span>Install App</span>
              </button>
            )}

            <button
              type="button"
              onClick={handleReplayTutorial}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl border border-[#DCE2F5] bg-white hover:bg-[#EEEAFE] text-[#101B35] text-xs font-extrabold transition min-h-[40px]"
              title="Interactive Feature Tour"
            >
              <HelpCircle className="w-4 h-4 text-[#5146E5]" />
              <span className="hidden lg:inline">Feature Tour</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveScreen('languages')}
              className="hidden lg:inline-flex items-center gap-1.5 px-3 py-2 rounded-xl border border-[#DCE2F5] bg-white hover:bg-[#EEEAFE] text-[#101B35] font-bold transition min-h-[40px]"
              title="Change explanation language"
            >
              <span>{onboarding.preferredExplanationLanguage}</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveScreen('profile')}
              className="inline-flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-xl bg-[#101B35] hover:bg-[#5146E5] text-white font-bold transition min-h-[40px]"
              title="Profile & Settings"
            >
              <span className="w-6 h-6 rounded-lg bg-[#35D6E8] text-[#101B35] text-[11px] font-extrabold flex items-center justify-center">
                {(onboarding.studentName || 'S').charAt(0)}
              </span>
              <span className="hidden sm:inline text-xs font-extrabold">
                Grade {onboarding.grade}
              </span>
            </button>
          </div>
        </header>

        <main className="flex-1 px-4 sm:px-6 lg:px-10 py-6 md:py-8 max-w-[1440px] w-full mx-auto space-y-6">
          {/* 1. COMMERCIAL LANDING PAGE & PLATFORM OVERVIEW */}
          {activeScreen === 'landing' && (
            <div className="space-y-8 animate-fade-in">
              {/* Hero Section */}
              <div
                className="rounded-3xl text-white p-7 sm:p-10 shadow-xl border border-[#5146E5]/30"
                style={{
                  background: 'linear-gradient(145deg, #101B35 0%, #1F2863 58%, #5146E5 100%)',
                }}
              >
                <div className="grid lg:grid-cols-12 gap-8 items-center">
                  <div className="lg:col-span-7 space-y-5">
                    <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/10 border border-[#35D6E8]/40 text-xs font-extrabold text-[#35D6E8]">
                      <Sparkles className="w-4 h-4 text-[#35D6E8]" />
                      <span>SparkMinds AI • {BRAND_DESCRIPTION}</span>
                    </div>
                    <h2 className="font-display text-3xl sm:text-4xl lg:text-[2.7rem] font-extrabold tracking-tight leading-[1.14]">
                      <BrandTagline variant="dark" animate />
                    </h2>
                    <p className="text-indigo-100/90 text-sm sm:text-base leading-relaxed font-medium max-w-xl">
                      Your intelligent AI robot learning companion for CBSE, ICSE, and State Boards. Learn visually with labelled diagrams in 23 languages, practice interactively, and track real progress.
                    </p>
                    <div className="pt-1 flex flex-wrap gap-3">
                      <button
                        onClick={() => setActiveScreen('dashboard')}
                        className="px-6 py-3 rounded-xl bg-[#35D6E8] hover:bg-[#5ce0ef] text-[#101B35] font-extrabold text-sm shadow-sm transition min-h-[46px]"
                      >
                        Open Dashboard →
                      </button>
                      <button
                        onClick={() => setActiveScreen('subjects')}
                        className="px-6 py-3 rounded-xl bg-white text-[#101B35] hover:bg-[#EEEAFE] font-extrabold text-sm transition min-h-[46px]"
                      >
                        Start Guided Lesson
                      </button>
                      <button
                        onClick={() => setActiveScreen('buddy')}
                        className="px-5 py-3 rounded-xl bg-white/10 hover:bg-white/20 border border-white/25 text-white font-bold text-sm transition min-h-[46px]"
                      >
                        Ask Sparky AI
                      </button>
                    </div>
                  </div>

                  {/* Right Column: Live Active Student Workspace Card */}
                  <div className="lg:col-span-5">
                    <div className="rounded-2xl bg-[#0B1328]/85 backdrop-blur-md border border-slate-700/80 p-6 space-y-4 shadow-xl">
                      <div className="flex items-center justify-between border-b border-slate-800 pb-3.5">
                        <div className="flex items-center gap-3">
                          <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-[#35D6E8] to-[#2563EB] text-[#101B35] font-extrabold text-base flex items-center justify-center shadow-md">
                            {(onboarding.studentName || 'S').charAt(0)}
                          </div>
                          <div>
                            <div className="text-[11px] font-bold uppercase tracking-wider text-[#35D6E8]">
                              Learning Workspace
                            </div>
                            <div className="text-base font-extrabold text-white">
                              {onboarding.studentName && !['Aarav Sharma', 'Ananya Reddy', 'Diya Nair', 'Karthik Rajan', 'Riya Verma', 'Student Learner'].includes(onboarding.studentName)
                                ? onboarding.studentName
                                : 'SparkMinds AI'}
                            </div>
                          </div>
                        </div>
                        <span className="px-2.5 py-1 rounded-full bg-emerald-500/20 border border-emerald-400/30 text-emerald-300 text-[11px] font-bold">
                          SparkMinds Platform
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-2.5 text-xs">
                        <div className="p-3 rounded-xl bg-white/[0.04] border border-white/10">
                          <div className="text-slate-400 text-[11px]">School Medium</div>
                          <div className="font-extrabold text-white mt-0.5">{onboarding.schoolMedium}</div>
                        </div>
                        <div className="p-3 rounded-xl bg-white/[0.04] border border-white/10">
                          <div className="text-slate-400 text-[11px]">AI Explanation Language</div>
                          <div className="font-extrabold text-[#35D6E8] mt-0.5">
                            {onboarding.preferredExplanationLanguage}
                          </div>
                        </div>
                        <div className="p-3 rounded-xl bg-white/[0.04] border border-white/10">
                          <div className="text-slate-400 text-[11px]">Active Subjects</div>
                          <div className="font-extrabold text-white mt-0.5">
                            {onboarding.selectedSubjects.length} Curriculum Subjects
                          </div>
                        </div>
                        <div className="p-3 rounded-xl bg-white/[0.04] border border-white/10">
                          <div className="text-slate-400 text-[11px]">Academic Archive</div>
                          <div className="font-extrabold text-emerald-300 mt-0.5">
                            {academicYears.length} Year Record{academicYears.length > 1 ? 's' : ''}
                          </div>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-2 pt-1 text-xs font-bold">
                        <button
                          type="button"
                          onClick={() => setActiveScreen('plan')}
                          className="py-2.5 px-3 rounded-xl bg-white/10 hover:bg-white/15 text-white border border-white/15 transition text-center"
                        >
                          📅 Daily Study Plan
                        </button>
                        <button
                          type="button"
                          onClick={() => setActiveScreen('homework')}
                          className="py-2.5 px-3 rounded-xl bg-white/10 hover:bg-white/15 text-white border border-white/15 transition text-center"
                        >
                          📝 Homework Manager
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Comprehensive Platform Modules Showcase (6 Pillars) */}
              <div className="space-y-3">
                <div className="flex flex-wrap items-end justify-between gap-2">
                  <div>
                    <span className="text-xs font-extrabold uppercase tracking-wider text-[#1E3A8A]">
                      Complete Learning Ecosystem
                    </span>
                    <h3 className="text-xl font-extrabold text-slate-900">
                      Everything a Student Needs From Daily Homework to Board Exams
                    </h3>
                  </div>
                  <button
                    type="button"
                    onClick={() => setActiveScreen('dashboard')}
                    className="text-xs font-extrabold text-[#1E3A8A] hover:underline"
                  >
                    Go to Full Student Dashboard →
                  </button>
                </div>

                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
                  <div
                    onClick={() => setActiveScreen('buddy')}
                    className="eduspark-card eduspark-card-hover rounded-2xl p-6 cursor-pointer space-y-2.5"
                  >
                    <div className="w-10 h-10 rounded-xl bg-[#101B35] text-[#35D6E8] flex items-center justify-center font-extrabold text-base">
                      🤖
                    </div>
                    <div className="font-extrabold text-base text-slate-900">
                      AI Learning Buddy & Socratic Tutor
                    </div>
                    <p className="text-slate-600 leading-relaxed">
                      Analyses typed questions and uploaded worksheet photos, checks prerequisite concepts, and guides students step-by-step with progressive hints.
                    </p>
                    <div className="pt-1 font-extrabold text-[#1E3A8A]">
                      Open Tutoring Studio →
                    </div>
                  </div>

                  <div
                    onClick={() => setActiveScreen('plan')}
                    className="eduspark-card eduspark-card-hover rounded-2xl p-6 cursor-pointer space-y-2.5"
                  >
                    <div className="w-10 h-10 rounded-xl bg-sky-100 text-sky-900 flex items-center justify-center font-extrabold text-base">
                      📅
                    </div>
                    <div className="font-extrabold text-base text-slate-900">
                      Smart Study & Daily Schedule Planner
                    </div>
                    <p className="text-slate-600 leading-relaxed">
                      Checks your daily school, tuition, and personal activities first, then builds realistic 12-hour AM/PM study blocks and subject exam timetables.
                    </p>
                    <div className="pt-1 font-extrabold text-[#1E3A8A]">
                      Plan Today&apos;s Schedule →
                    </div>
                  </div>

                  <div
                    onClick={() => setActiveScreen('homework')}
                    className="eduspark-card eduspark-card-hover rounded-2xl p-6 cursor-pointer space-y-2.5"
                  >
                    <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-900 flex items-center justify-center font-extrabold text-base">
                      📝
                    </div>
                    <div className="font-extrabold text-base text-slate-900">
                      Homework Manager & Guided Help
                    </div>
                    <p className="text-slate-600 leading-relaxed">
                      Track school assignments by due date and priority, attach worksheet images or PDFs, and launch guided Socratic help for any homework task.
                    </p>
                    <div className="pt-1 font-extrabold text-[#1E3A8A]">
                      Manage Homework →
                    </div>
                  </div>

                  <div
                    onClick={() => setActiveScreen('exams')}
                    className="eduspark-card eduspark-card-hover rounded-2xl p-6 cursor-pointer space-y-2.5"
                  >
                    <div className="w-10 h-10 rounded-xl bg-indigo-100 text-indigo-900 flex items-center justify-center font-extrabold text-base">
                      🏆
                    </div>
                    <div className="font-extrabold text-base text-slate-900">
                      Exam Preparation & Revision Suite
                    </div>
                    <p className="text-slate-600 leading-relaxed">
                      Take timed mock tests with instant mistake explanations, review spaced-repetition flashcards, and log post-exam school marks.
                    </p>
                    <div className="pt-1 font-extrabold text-[#1E3A8A]">
                      Start Exam Prep →
                    </div>
                  </div>

                  <div
                    onClick={() => setActiveScreen('journey')}
                    className="eduspark-card eduspark-card-hover rounded-2xl p-6 cursor-pointer space-y-2.5"
                  >
                    <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-900 flex items-center justify-center font-extrabold text-base">
                      🎓
                    </div>
                    <div className="font-extrabold text-base text-slate-900">
                      Grade 1–12 Permanent Academic Memory
                    </div>
                    <p className="text-slate-600 leading-relaxed">
                      Preserves every academic year across annual school promotions so students and parents can review multi-year progress and resolved learning gaps.
                    </p>
                    <div className="pt-1 font-extrabold text-[#1E3A8A]">
                      View Academic Journey →
                    </div>
                  </div>

                  <div
                    onClick={() => setActiveScreen('parent')}
                    className="eduspark-card eduspark-card-hover rounded-2xl p-6 cursor-pointer space-y-2.5"
                  >
                    <div className="w-10 h-10 rounded-xl bg-teal-100 text-teal-900 flex items-center justify-center font-extrabold text-base">
                      🛡️
                    </div>
                    <div className="font-extrabold text-base text-slate-900">
                      Parent Portal & Child-Safety Controls
                    </div>
                    <p className="text-slate-600 leading-relaxed">
                      Dedicated parent summaries in 23 languages, verified under-8 guardian consent protection, and read-only assessment integrity guards.
                    </p>
                    <div className="pt-1 font-extrabold text-[#1E3A8A]">
                      Open Parent Portal →
                    </div>
                  </div>
                </div>
              </div>

              <AgentOrchestratorBar />
            </div>
          )}

          {/* 3. SEVEN-STEP STUDENT ONBOARDING */}
          {activeScreen === 'onboarding' && (
            <SevenStepOnboarding
              onboarding={onboarding}
              setOnboarding={setOnboarding}
              onComplete={(syncedBundle) => {
                if (syncedBundle) {
                  hydrateFromCloudBundle(syncedBundle);
                }
                setIsOnboardingCompleted(true);
                checkAndTriggerTutorial(onboarding.studentId);
                setActiveScreen('dashboard');
              }}
            />
          )}

          {/* 4. STUDENT DASHBOARD */}
          {activeScreen === 'dashboard' && (
            <StudentDashboardView
              onboarding={onboarding}
              academicYearsCount={academicYears.length}
              onSelectScreen={setActiveScreen}
              onOpenBuddyWithQuestion={handleOpenBuddyWithQuestion}
              onOpenAgeEditor={() => {
                setProfileEditAge(onboarding.age);
                if (customDobInput) setProfileEditDob(customDobInput);
                setShowAgeQuickModal(true);
              }}
            />
          )}

          {/* 5. AI LEARNING BUDDY (INTERACTIVE SOCRATIC TUTORING & CONVERSATIONAL CHAT) */}
          {activeScreen === 'buddy' && (
            <AILearningBuddyView
              onboarding={onboarding}
              initialQuestion={buddyQuestionPrefill?.question}
              initialSubject={buddyQuestionPrefill?.subject}
              onSelectScreen={setActiveScreen}
            />
          )}

          {/* 6. HOMEWORK MANAGER */}
          {activeScreen === 'homework' && (
            <HomeworkManagerView
              onboarding={onboarding}
              onOpenInBuddy={handleOpenBuddyWithQuestion}
            />
          )}

          {/* 7. SUBJECT LEARNING EXPLORER */}
          {activeScreen === 'subjects' && (
            <SubjectLearningExplorerView
              onboarding={onboarding}
              onOpenBuddyWithQuestion={handleOpenBuddyWithQuestion}
              onSelectScreen={setActiveScreen}
            />
          )}

          {/* 8. SMART STUDY PLANNER */}
          {activeScreen === 'plan' && (
            <SmartStudyPlannerView onboarding={onboarding} />
          )}

          {/* 9. SMART REVISION CENTRE */}
          {activeScreen === 'practice' && (
            <SmartRevisionCentreView onboarding={onboarding} />
          )}

          {/* 10. EXAM PREPARATION CENTRE */}
          {activeScreen === 'exams' && (
            <ExamPreparationCentreView
              onboarding={onboarding}
              onSelectScreen={setActiveScreen}
            />
          )}

          {/* 11. SCHOOL PROJECT & CREATIVITY LAB */}
          {activeScreen === 'projects' && (
            <SchoolProjectCreativityLabView onboarding={onboarding} />
          )}

          {/* 12. ACADEMIC PROGRESS DASHBOARD */}
          {activeScreen === 'progress' && (
            <AcademicProgressDashboardView onboarding={onboarding} />
          )}

          {/* 13 & 14. MY ACADEMIC JOURNEY & HISTORICAL COMPARISON */}
          {(activeScreen === 'journey' || activeScreen === 'comparison') && (
            <AcademicJourneyView
              academicYears={academicYears}
              currentGrade={onboarding.grade}
              onSelectScreen={setActiveScreen}
            />
          )}

          {/* 15. ANNUAL GRADE PROMOTION */}
          {activeScreen === 'promotion' && (
            <AnnualPromotionView
              onboarding={onboarding}
              academicYears={academicYears}
              onPromoteStudent={handlePromoteStudent}
            />
          )}

          {/* 16. PARENT DASHBOARD */}
          {activeScreen === 'parent' && (
            <ParentDashboardView
              onboarding={onboarding}
              academicYears={academicYears}
            />
          )}

          {/* 17 & 18. STUDENT PROFILE & INDIAN LANGUAGE PREFERENCES */}
          {(activeScreen === 'profile' || activeScreen === 'languages') && (
            <div className="space-y-6 animate-fade-in">
              {/* Midnight-Indigo Student Profile Summary Header + Replay Introduction & Feature Tour */}
              <div
                className="rounded-3xl text-white p-6 md:p-7 border border-[#5146E5]/30 shadow-lg flex flex-wrap items-center justify-between gap-4"
                style={{
                  background: 'linear-gradient(135deg, #101B35 0%, #222B68 62%, #5146E5 100%)',
                }}
              >
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-2xl bg-[#35D6E8] text-[#101B35] font-extrabold text-xl flex items-center justify-center shrink-0 shadow-md">
                    {(onboarding.studentName || 'S').charAt(0)}
                  </div>
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="text-xl font-extrabold text-white">
                        {onboarding.studentName || 'Student Profile'}
                      </h2>
                      <span className="px-2.5 py-0.5 rounded-full bg-white/10 border border-[#35D6E8]/45 text-[#35D6E8] text-xs font-extrabold">
                        Grade {onboarding.grade} • Age {onboarding.age} • {onboarding.board}
                      </span>
                    </div>
                    <p className="text-xs text-indigo-100/90 mt-1">
                      {onboarding.selectedSubjects.length} subjects • Explanations in {onboarding.preferredExplanationLanguage}
                    </p>
                    <div className="mt-2 inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-[#0B1328]/65 border border-[#35D6E8]/40 text-xs">
                      <Sparkles className="w-3.5 h-3.5 text-[#FBBF24] shrink-0" />
                      <BrandTagline variant="dark" className="text-[11.5px] sm:text-xs leading-snug" />
                    </div>
                  </div>
                </div>
                <div className="flex flex-wrap items-center gap-2 text-xs font-extrabold">
                  <button
                    type="button"
                    onClick={handleReplayIntro}
                    className="px-4 py-2.5 rounded-xl bg-white/12 hover:bg-white/20 text-white border border-white/25 transition flex items-center gap-1.5 min-h-[42px]"
                  >
                    <Sparkles className="w-4 h-4 text-[#35D6E8]" />
                    <span>Replay Introduction</span>
                  </button>
                  <button
                    type="button"
                    onClick={handleReplayTutorial}
                    className="px-4 py-2.5 rounded-xl bg-[#35D6E8] hover:bg-[#5ce0ef] text-[#101B35] transition flex items-center gap-1.5 min-h-[42px]"
                  >
                    <HelpCircle className="w-4 h-4" />
                    <span>Replay Feature Tour</span>
                  </button>
                  <button
                    type="button"
                    onClick={handleResetRobotTips}
                    className="px-3.5 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-indigo-100 border border-white/20 transition min-h-[42px]"
                  >
                    Restore Tips
                  </button>
                  <button
                    type="button"
                    onClick={() => setActiveScreen('onboarding')}
                    className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/20 transition min-h-[42px]"
                  >
                    Edit Setup
                  </button>
                  <button
                    type="button"
                    onClick={handleLogoutSession}
                    className="px-4 py-2.5 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 text-rose-100 border border-rose-400/30 transition min-h-[42px]"
                  >
                    Sign Out
                  </button>
                </div>
              </div>

              {/* EDITABLE STUDENT PROFILE & AGE CARD */}
              <div className="eduspark-card rounded-3xl p-6 md:p-7 space-y-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <h2 className="text-lg font-extrabold text-[#101B35]">
                      Student Details & Age
                    </h2>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Update your age, date of birth, or name anytime. Changes sync automatically.
                    </p>
                  </div>
                  <span className="text-xs font-extrabold px-3 py-1.5 rounded-xl bg-slate-100 border border-slate-200 text-[#101B35]">
                    Saved Age: {onboarding.age} yrs
                  </span>
                </div>

                {profileSaveFeedback && (
                  <div
                    className={`p-3.5 rounded-2xl text-xs font-extrabold border ${
                      profileSaveFeedback.type === 'ok'
                        ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                        : 'bg-rose-50 border-rose-200 text-rose-800'
                    }`}
                  >
                    {profileSaveFeedback.text}
                  </div>
                )}

                <div className="space-y-1.5 pt-1">
                  <label className="block text-xs font-extrabold text-slate-800">
                    Quick Age Selection (1-Click):
                  </label>
                  <div className="flex flex-wrap gap-1.5">
                    {[4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18].map((a) => (
                      <button
                        key={a}
                        type="button"
                        onClick={() => handleProfileAgeChange(a)}
                        className={`px-3 py-1.5 rounded-xl text-xs font-extrabold transition ${
                          profileEditAge === a
                            ? 'bg-blue-600 text-white shadow-sm ring-2 ring-blue-400'
                            : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200'
                        }`}
                      >
                        {a} yrs
                      </button>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
                  <div className="space-y-1.5">
                    <label className="block text-xs font-extrabold text-slate-800">
                      1. Student Age (Years):
                    </label>
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => {
                          const next = Math.max(4, profileEditAge - 1);
                          handleProfileAgeChange(next);
                        }}
                        className="w-10 h-10 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 font-extrabold text-lg flex items-center justify-center border border-slate-300 transition shrink-0 cursor-pointer"
                        title="Decrease age by 1 year"
                      >
                        −
                      </button>
                      <input
                        type="number"
                        min={4}
                        max={20}
                        value={profileEditAge === 0 ? '' : profileEditAge}
                        onChange={(e) => {
                          const raw = e.target.value;
                          if (raw === '') {
                            setProfileEditAge(0);
                            return;
                          }
                          const val = parseInt(raw, 10);
                          if (!isNaN(val)) {
                            setProfileEditAge(val);
                            if (val >= 4 && val <= 20) {
                              setProfileEditDob(calculateDobFromAge(val, profileEditDob));
                            }
                          }
                        }}
                        onBlur={() => {
                          const safe = Math.max(4, Math.min(20, profileEditAge || 12));
                          handleProfileAgeChange(safe);
                        }}
                        className="w-full text-center rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-base font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
                        title="Editable student age"
                      />
                      <button
                        type="button"
                        onClick={() => {
                          const next = Math.min(20, profileEditAge + 1);
                          handleProfileAgeChange(next);
                        }}
                        className="w-10 h-10 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 font-extrabold text-lg flex items-center justify-center border border-slate-300 transition shrink-0 cursor-pointer"
                        title="Increase age by 1 year"
                      >
                        +
                      </button>
                    </div>
                    <p className="text-[11px] text-slate-500">Allowed range: 4 to 20 years. Use + / − buttons or type.</p>
                  </div>

                  <div className="space-y-1.5">
                    <label className="block text-xs font-extrabold text-slate-800">
                      2. Date of Birth: <span className="text-rose-600">*</span>
                    </label>
                    <input
                      type="date"
                      required
                      value={profileEditDob}
                      onChange={(e) => handleProfileDobChange(e.target.value)}
                      className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
                      title="Editable date of birth"
                    />
                    <p className="text-[11px] text-slate-500">Calculates age automatically on change.</p>
                  </div>

                  <div className="space-y-1.5">
                    <label className="block text-xs font-extrabold text-slate-800">
                      3. Full Name:
                    </label>
                    <input
                      type="text"
                      value={profileEditName}
                      onChange={(e) => setProfileEditName(e.target.value)}
                      className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
                    />
                    <p className="text-[11px] text-slate-500">Student display name.</p>
                  </div>
                </div>

                {profileEditAge < 8 && (
                  <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 font-bold">
                    🛡️ Child Safety Protection Active: Students under 8 years operate under parent-assisted mode with verified parental consent.
                  </div>
                )}

                <div className="pt-2 flex justify-end">
                  <button
                    type="button"
                    onClick={() => handleSaveProfileAgeAndDetails()}
                    className="px-6 py-2.5 rounded-xl bg-[#101B35] hover:bg-[#1B2654] text-[#35D6E8] text-xs font-extrabold shadow-sm transition min-h-[42px]"
                  >
                    Save Changes ✓
                  </button>
                </div>
              </div>

              {/* Multilingual Explanation Preferences Card */}
              <div className="eduspark-card rounded-3xl p-6 md:p-8 space-y-5">
                <div>
                  <span className="text-xs font-extrabold uppercase tracking-wider px-3 py-1 rounded-full bg-cyan-50 text-[#101B35] border border-cyan-200">
                    Multilingual Learning • 22 Scheduled Indian Languages + English
                  </span>
                  <h2 className="text-xl font-extrabold text-slate-900 mt-2">
                    Language & Explanation Preferences
                  </h2>
                  <p className="text-xs text-slate-600 mt-0.5">
                    SparkMinds AI stores your School Medium, Preferred Explanation Language, Optional Secondary Bilingual Language, and Interface Display Language independently.
                  </p>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div className="p-4 rounded-2xl border border-slate-200 space-y-2">
                    <label className="block text-xs font-extrabold text-slate-800">
                      1. School Medium of Instruction:
                    </label>
                    <select
                      value={onboarding.schoolMedium}
                      onChange={(e) =>
                        setOnboarding((p) => ({ ...p, schoolMedium: e.target.value }))
                      }
                      className="w-full rounded-xl border border-slate-300 px-3 py-2 text-xs font-bold"
                    >
                      {['English', 'Telugu', 'Hindi', 'Tamil', 'Kannada', 'Malayalam', 'Marathi', 'Bengali', 'Gujarati', 'Punjabi', 'Odia', 'Urdu'].map(
                        (m) => (
                          <option key={m} value={m}>
                            {m} Medium
                          </option>
                        )
                      )}
                    </select>
                  </div>

                  <div className="p-4 rounded-2xl border-2 border-[#0284C7] bg-sky-50/40 space-y-2">
                    <label className="block text-xs font-extrabold text-slate-900">
                      2. Preferred Explanation Language (All 23 Supported):
                    </label>
                    <select
                      value={onboarding.preferredExplanationLanguage}
                      onChange={(e) =>
                        setOnboarding((p) => ({
                          ...p,
                          preferredExplanationLanguage: e.target.value,
                        }))
                      }
                      className="w-full rounded-xl border border-sky-300 bg-white px-3 py-2 text-xs font-extrabold text-slate-900"
                    >
                      {ALL_23_INDIAN_LANGUAGES.map((l) => (
                        <option key={l.code} value={l.name}>
                          {l.name} ({l.nativeName})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="p-4 rounded-2xl border border-slate-200 space-y-2">
                    <label className="block text-xs font-extrabold text-slate-800">
                      3. Optional Secondary Explanation Language (Bilingual Mode):
                    </label>
                    <select
                      value={onboarding.secondaryExplanationLanguage}
                      onChange={(e) =>
                        setOnboarding((p) => ({
                          ...p,
                          secondaryExplanationLanguage: e.target.value,
                        }))
                      }
                      className="w-full rounded-xl border border-slate-300 px-3 py-2 text-xs font-bold"
                    >
                      <option value="">None (Single Language Only)</option>
                      {ALL_23_INDIAN_LANGUAGES.map((l) => (
                        <option key={l.code} value={l.name}>
                          {l.name} ({l.nativeName})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="p-4 rounded-2xl border border-slate-200 space-y-2">
                    <label className="block text-xs font-extrabold text-slate-800">
                      4. Interface Display Language:
                    </label>
                    <select
                      value={onboarding.interfaceDisplayLanguage}
                      onChange={(e) =>
                        setOnboarding((p) => ({
                          ...p,
                          interfaceDisplayLanguage: e.target.value,
                        }))
                      }
                      className="w-full rounded-xl border border-slate-300 px-3 py-2 text-xs font-bold"
                    >
                      {['English', 'Telugu', 'Hindi', 'Tamil', 'Kannada'].map((ui) => (
                        <option key={ui} value={ui}>
                          {ui} Interface
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
                  <div className="flex items-center gap-2 text-xs font-bold text-emerald-700">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>
                      Your language preferences are automatically applied across AI Learning Buddy, Homework Help, and Study Planning.
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={async () => {
                      try {
                        await fetch(`/api/students/${onboarding.studentId}/languages`, {
                          method: 'PUT',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify({
                            school_medium_language: onboarding.schoolMedium,
                            preferred_explanation_language: onboarding.preferredExplanationLanguage,
                            secondary_explanation_language: onboarding.secondaryExplanationLanguage || null,
                            interface_display_language: onboarding.interfaceDisplayLanguage,
                          }),
                        });
                      } catch {
                        // Offline fallback
                      }
                      setActiveScreen('dashboard');
                    }}
                    className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#101B35] to-[#1E3A8A] text-[#35D6E8] text-xs font-extrabold shadow-md hover:opacity-95 transition"
                  >
                    Save Language Preferences ✓
                  </button>
                </div>
              </div>
            </div>
          )}
        </main>

        {/* COMMERCIAL WEBSITE FOOTER */}
        <footer className="mt-auto border-t border-slate-200/80 bg-white/80 backdrop-blur px-4 sm:px-6 lg:px-10 pt-5 pb-24 md:pb-5">
          <div className="max-w-[1440px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-600">
            <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2.5 sm:gap-3">
              <EduSparkLogo size="sm" />
              <span className="hidden sm:inline text-slate-300">|</span>
              <BrandTagline variant="light" className="text-xs text-center sm:text-left" />
            </div>
            <div className="flex flex-wrap items-center justify-center gap-4 font-semibold text-slate-600">
              <button type="button" onClick={() => setActiveScreen('dashboard')} className="hover:text-[#101B35] transition">
                Dashboard
              </button>
              <button type="button" onClick={() => setActiveScreen('buddy')} className="hover:text-[#101B35] transition">
                AI Learning Buddy
              </button>
              <button type="button" onClick={() => setActiveScreen('plan')} className="hover:text-[#101B35] transition">
                Study Planner
              </button>
              <button type="button" onClick={() => setActiveScreen('exams')} className="hover:text-[#101B35] transition">
                Exam Prep
              </button>
              <button type="button" onClick={() => setActiveScreen('parent')} className="hover:text-[#101B35] transition">
                Parent Portal
              </button>
              <button type="button" onClick={() => setActiveScreen('auth')} className="hover:text-[#101B35] transition">
                Account
              </button>
            </div>
          </div>
        </footer>
      </div>

      {/* MOBILE SLIDE-OVER NAVIGATION DRAWER (ANDROID PHONES, TABLETS & IPHONES) */}
      {showMobileMenuDrawer && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          <div
            className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm"
            onClick={() => setShowMobileMenuDrawer(false)}
          />
          <aside className="relative w-80 max-w-[85vw] flex flex-col bg-gradient-to-b from-[#101B35] via-[#0F2442] to-[#0B1328] text-white h-full z-10 shadow-2xl overflow-hidden">
            <div className="p-4 border-b border-slate-800/80 flex items-center justify-between">
              <EduSparkLogo size="sm" showTagline lightText />
              <button
                type="button"
                onClick={() => setShowMobileMenuDrawer(false)}
                className="p-2 rounded-xl bg-slate-800/90 text-slate-300 hover:text-white"
                aria-label="Close Menu"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Mobile Active Student Card & Profile Switcher */}
            <div className="px-4 py-3 bg-[#0B1328]/70 border-b border-slate-800/80 space-y-2">
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2.5 min-w-0">
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-[#35D6E8] to-[#2563EB] text-[#101B35] font-extrabold text-xs flex items-center justify-center shrink-0">
                    {(onboarding.studentName || 'S').charAt(0)}
                  </div>
                  <div className="min-w-0">
                    <div className="text-xs font-extrabold text-white truncate">
                      {onboarding.studentName && !['Aarav Sharma', 'Ananya Reddy', 'Diya Nair', 'Karthik Rajan', 'Riya Verma', 'Student Learner'].includes(onboarding.studentName)
                        ? onboarding.studentName
                        : 'SparkMinds AI'}
                    </div>
                    <div className="text-[11px] text-slate-400 truncate">
                      Interactive Learning Studio
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-1.5 shrink-0">
                  <button
                    type="button"
                    onClick={() => {
                      setProfileEditAge(onboarding.age);
                      if (customDobInput) setProfileEditDob(customDobInput);
                      setShowAgeQuickModal(true);
                      setShowMobileMenuDrawer(false);
                    }}
                    className="px-2 py-1 rounded-lg bg-cyan-950 text-[10px] font-bold text-[#35D6E8] border border-[#35D6E8]/40"
                    title="Quickly edit student age and date of birth"
                  >
                    ✎ Age
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowProfileSwitcherMenu((p) => !p)}
                    className="px-2 py-1 rounded-lg bg-slate-800 text-[10px] font-bold text-[#35D6E8] border border-slate-700"
                    title="Switch Student Profile"
                  >
                    Switch ▾
                  </button>
                </div>
              </div>
              {showProfileSwitcherMenu && (
                <div className="grid grid-cols-5 gap-1.5 pt-1">
                  {([1, 4, 7, 10, 12] as GradeNumber[]).map((g) => (
                    <button
                      key={g}
                      type="button"
                      onClick={() => {
                        applyRepresentativeProfile(g);
                        setShowProfileSwitcherMenu(false);
                        setShowMobileMenuDrawer(false);
                      }}
                      className={`py-1.5 rounded-lg text-xs font-extrabold transition-all ${onboarding.grade === g
                          ? 'bg-[#35D6E8] text-[#101B35]'
                          : 'bg-slate-800/90 text-slate-300 border border-slate-700'
                        }`}
                    >
                      G{g}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Mobile Platform Navigation */}
            <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-4">
              {(
                ['Core', 'Learning', 'History & Growth', 'Family & Settings'] as const
              ).map((category) => (
                <div key={category}>
                  <div className="px-3 mb-1.5 text-[10px] font-extrabold uppercase tracking-widest text-slate-400">
                    {CATEGORY_DISPLAY_NAMES[category]}
                  </div>
                  <div className="space-y-1">
                    {ALL_18_SCREENS.filter((s) => s.category === category).map(
                      (screen) => {
                        const isActive = activeScreen === screen.id;
                        return (
                          <button
                            key={screen.id}
                            onClick={() => {
                              setActiveScreen(screen.id);
                              setShowMobileMenuDrawer(false);
                            }}
                            className={`relative w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-left text-xs font-semibold transition-all ${isActive
                                ? 'bg-gradient-to-r from-[#35D6E8]/20 via-[#1E3A8A]/70 to-transparent text-white border border-[#35D6E8]/35'
                                : 'text-slate-300 hover:bg-white/[0.06] hover:text-white'
                              }`}
                          >
                            <span className="flex items-center gap-3 truncate">
                              <span
                                className={
                                  isActive ? 'text-[#35D6E8]' : 'text-slate-400'
                                }
                              >
                                {SCREEN_ICONS[screen.id]}
                              </span>
                              <span className={`truncate ${isActive ? 'font-extrabold text-white' : 'font-medium'}`}>
                                {screen.title}
                              </span>
                            </span>
                          </button>
                        );
                      }
                    )}
                  </div>
                </div>
              ))}
            </nav>

            <div className="p-3 border-t border-white/10 bg-[#0B1328] space-y-2">
              <button
                type="button"
                onClick={() => {
                  setShowMobileMenuDrawer(false);
                  handleReplayIntro();
                }}
                className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-white text-xs font-bold transition"
              >
                <Sparkles className="w-4 h-4 text-[#35D6E8]" />
                <span>Replay Introduction</span>
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowMobileMenuDrawer(false);
                  handleReplayTutorial();
                }}
                className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-[#5146E5] hover:bg-[#4338CA] text-white text-xs font-bold transition shadow-sm"
              >
                <HelpCircle className="w-4 h-4 text-[#35D6E8]" />
                <span>Replay Feature Tour</span>
              </button>
            </div>

            <div className="p-3.5 border-t border-white/10 bg-[#0B1328] text-[11px] flex items-center justify-between">
              <span className="flex items-center gap-2 font-semibold text-indigo-100">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                {backendStatus.connected
                  ? 'SparkMinds Cloud Connected'
                  : 'SparkMinds Offline-Ready'}
              </span>
              <span className="px-2 py-0.5 rounded-md font-bold bg-white/10 text-[#35D6E8] text-[10px]">
                {backendStatus.supportedLanguagesCount || 23} Languages
              </span>
            </div>
          </aside>
        </div>
      )}

      {/* MOBILE BOTTOM NAVIGATION */}
      <nav className="md:hidden fixed bottom-0 inset-x-0 bg-[#101B35]/95 backdrop-blur-md border-t border-indigo-950 px-1.5 py-2 flex justify-around items-center z-30 shadow-2xl">
        {mobileQuickTabs.map((id) => {
          const def = ALL_18_SCREENS.find((s) => s.id === id)!;
          const isActive = activeScreen === id;
          return (
            <button
              key={id}
              data-tour-id={`nav-${id}`}
              onClick={() => setActiveScreen(id)}
              className={`flex flex-col items-center justify-center py-1.5 px-2.5 rounded-xl text-xs font-bold transition-all ${
                isActive
                  ? 'bg-[#5146E5] text-white border border-[#35D6E8]/40'
                  : 'text-indigo-200/75 hover:text-white'
              }`}
            >
              {SCREEN_ICONS[id]}
              <span className="mt-0.5 text-[10px]">{def.shortLabel}</span>
            </button>
          );
        })}
        <button
          type="button"
          onClick={() => setShowMobileMenuDrawer(true)}
          className="flex flex-col items-center justify-center py-1.5 px-2.5 rounded-xl text-xs font-bold text-indigo-200 hover:text-[#35D6E8] transition-all"
        >
          <Menu className="w-4 h-4" />
          <span className="mt-0.5 text-[10px]">Menu</span>
        </button>
      </nav>
    </div>
  );
}

export default App;
