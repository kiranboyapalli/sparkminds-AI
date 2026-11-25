/**
 * SparkMinds AI — Frontend Indian Curriculum, 22 Scheduled Languages + English,
 * and Representative Multi-Year Student State Store (Synced with FastAPI Backend).
 */

export interface LanguageItem {
  code: string;
  name: string;
  nativeName: string;
  tier: 1 | 2;
  verified: boolean;
}

export const ALL_23_INDIAN_LANGUAGES: LanguageItem[] = [
  { code: 'en', name: 'English', nativeName: 'English', tier: 1, verified: true },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు', tier: 1, verified: true },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी', tier: 1, verified: true },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்', tier: 1, verified: true },
  { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ', tier: 1, verified: true },
  { code: 'as', name: 'Assamese', nativeName: 'অসমীয়া', tier: 2, verified: false },
  { code: 'bn', name: 'Bengali', nativeName: 'বাংলা', tier: 2, verified: false },
  { code: 'brx', name: 'Bodo', nativeName: 'बड़ो', tier: 2, verified: false },
  { code: 'doi', name: 'Dogri', nativeName: 'डोगरी', tier: 2, verified: false },
  { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી', tier: 2, verified: false },
  { code: 'ks', name: 'Kashmiri', nativeName: 'कॉशुर / کٲشُر', tier: 2, verified: false },
  { code: 'gom', name: 'Konkani', nativeName: 'कोंकणी', tier: 2, verified: false },
  { code: 'mai', name: 'Maithili', nativeName: 'मैथिली', tier: 2, verified: false },
  { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം', tier: 2, verified: false },
  { code: 'mni', name: 'Manipuri (Meitei)', nativeName: 'মৈতৈলোন্', tier: 2, verified: false },
  { code: 'mr', name: 'Marathi', nativeName: 'मराठी', tier: 2, verified: false },
  { code: 'ne', name: 'Nepali', nativeName: 'नेपाली', tier: 2, verified: false },
  { code: 'or', name: 'Odia', nativeName: 'ଓଡ଼ିଆ', tier: 2, verified: false },
  { code: 'pa', name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ', tier: 2, verified: false },
  { code: 'sa', name: 'Sanskrit', nativeName: 'संस्कृतम्', tier: 2, verified: false },
  { code: 'sat', name: 'Santali', nativeName: 'ᱥᱟᱱᱛᱟᱲᱤ', tier: 2, verified: false },
  { code: 'sd', name: 'Sindhi', nativeName: 'सिन्धी / سنڌي', tier: 2, verified: false },
  { code: 'ur', name: 'Urdu', nativeName: 'اردو', tier: 2, verified: false },
];

export const INDIAN_STATES_LIST = [
  'Telangana',
  'Andhra Pradesh',
  'Tamil Nadu',
  'Karnataka',
  'Maharashtra',
  'Kerala',
  'Delhi (NCT)',
  'Gujarat',
  'Uttar Pradesh',
  'West Bengal',
  'Rajasthan',
  'Punjab',
  'Odisha',
  'Assam',
  'Bihar',
  'Madhya Pradesh',
];

export const STEP5_14_CHALLENGES = [
  "I don't understand some concepts.",
  'I forget what I studied.',
  'I find it difficult to remember answers.',
  "I don't know how to start studying.",
  'I take too much time to complete homework.',
  'I get distracted while studying.',
  'I make mistakes even when I know the answer.',
  'I find textbook questions difficult to understand.',
  'I struggle with application-based questions.',
  'I cannot manage homework and exam preparation together.',
  'I find it difficult to revise regularly.',
  'I hesitate to ask teachers or others for help.',
  'I struggle to complete school projects.',
  'I feel nervous before exams.',
];

export const STEP6_9_GOALS = [
  { id: 'g1', label: 'Improve my marks.' },
  { id: 'g2', label: 'Understand difficult concepts.' },
  { id: 'g3', label: 'Complete homework on time.' },
  { id: 'g4', label: 'Prepare for examinations.' },
  { id: 'g5', label: 'Improve memory and revision.' },
  { id: 'g6', label: 'Improve time management.' },
  { id: 'g7', label: 'Develop problem-solving skills.' },
  { id: 'g8', label: 'Complete school projects.' },
  { id: 'g9', label: 'Build confidence and become an independent learner.' },
];

export interface SubjectOption {
  code: string;
  name: string;
  topics: string[];
}

export function getSubjectsForGradeAndBoardFrontend(
  grade: number,
  board: string,
  state?: string
): SubjectOption[] {
  const b = (board || 'CBSE').toUpperCase();
  const stateLabel = state || 'State';

  if (grade <= 2) {
    const list: SubjectOption[] = [
      { code: `G${grade}_ENG`, name: 'English', topics: ['Alphabets & Phonics', 'Simple Action Words', 'Picture Stories'] },
      { code: `G${grade}_MATH`, name: 'Mathematics', topics: ['Numbers 1 to 100', 'Addition & Subtraction', 'Basic Shapes & Patterns', 'Money & Time Basics'] },
      { code: `G${grade}_HINDI`, name: 'Hindi (हिन्दी)', topics: ['Varnamala (वर्णमाला)', 'Simple Words', 'Short Rhymes'] },
      { code: `G${grade}_EVS`, name: 'World Around Us (EVS)', topics: ['My Family & Home', 'Plants & Animals Around Us', 'Good Habits & Safety'] },
    ];
    if (b === 'STATE') {
      list.unshift({
        code: `G${grade}_REG`,
        name: `First Language (${stateLabel} Medium/Regional)`,
        topics: ['Basic Letters', 'Spoken & Reading Practice'],
      });
    }
    return list;
  }

  if (grade <= 5) {
    return [
      { code: `G${grade}_MATH`, name: 'Mathematics', topics: ['Large Numbers & Place Value', 'Multiplication & Division', 'Fractions Introduction', 'Geometry & Measurement', 'Word Problems'] },
      { code: `G${grade}_EVS`, name: b === 'ICSE' ? 'Science & Social Studies (ICSE)' : 'Environmental Studies (EVS)', topics: ['Living & Non-Living Things', 'Food, Water & Shelter', 'Our Country India', 'Plants, Animals & Habitats'] },
      { code: `G${grade}_ENG`, name: 'English Language & Literature', topics: ['Reading Comprehension', 'Nouns, Verbs & Tenses', 'Paragraph & Story Writing'] },
      { code: `G${grade}_LANG2`, name: b === 'STATE' ? `Regional Language (${stateLabel})` : 'Hindi / Second Language', topics: ['Vyakaran / Grammar', 'Comprehension', 'Short Essays'] },
      { code: `G${grade}_COMP`, name: 'Computer Studies', topics: ['Parts of a Computer', 'Logical Thinking', 'Basic Formatting'] },
    ];
  }

  if (grade <= 8) {
    const sciSubjects: SubjectOption[] =
      b === 'ICSE'
        ? [
            { code: `G${grade}_PHY`, name: 'Physics (ICSE)', topics: ['Force & Pressure', 'Energy', 'Light & Electricity'] },
            { code: `G${grade}_CHEM`, name: 'Chemistry (ICSE)', topics: ['Matter & Elements', 'Atomic Structure', 'Chemical Reactions'] },
            { code: `G${grade}_BIO`, name: 'Biology (ICSE)', topics: ['Plant & Animal Tissues', 'Photosynthesis', 'Human Body Systems'] },
          ]
        : [
            { code: `G${grade}_SCI`, name: 'General Science', topics: ['Nutrition in Plants & Animals', 'Heat, Motion & Time', 'Acids, Bases & Salts', 'Electric Current & Light', 'Microorganisms & Cells'] },
          ];

    return [
      { code: `G${grade}_MATH`, name: 'Mathematics', topics: ['Integers & Rational Numbers', 'Fractions & Decimals', 'Algebraic Expressions & Linear Equations', 'Ratio, Proportion & Percentage', 'Geometry, Mensuration & Data Handling'] },
      ...sciSubjects,
      { code: `G${grade}_SST`, name: 'Social Science (History, Civics, Geography)', topics: ['Ancient, Medieval & Modern Indian History', 'Our Environment & Resources', 'Indian Constitution & Democracy'] },
      { code: `G${grade}_ENG`, name: 'English', topics: ['Grammar, Active/Passive Voice & Direct/Indirect Speech', 'Reading Comprehension', 'Formal Letters & Creative Writing'] },
      { code: `G${grade}_LANG2`, name: b === 'STATE' ? `Second Language (${stateLabel})` : 'Hindi / Regional Language', topics: ['Grammar', 'Unseen Passages', 'Essay Writing'] },
      { code: `G${grade}_COMP`, name: 'Computer Science & AI', topics: ['Algorithms & Flowcharts', 'Coding Basics (Python/HTML)', 'Cyber Safety'] },
    ];
  }

  if (grade <= 10) {
    const sciSubjects: SubjectOption[] =
      b === 'STATE' && (state === 'Telangana' || state === 'Andhra Pradesh')
        ? [
            { code: `G${grade}_PSCI`, name: 'Physical Science (Physics & Chemistry)', topics: ['Reflection & Refraction', 'Acids, Bases & Salts', 'Chemical Equations', 'Electric Current'] },
            { code: `G${grade}_BSCI`, name: 'Biological Science', topics: ['Life Processes', 'Control & Coordination', 'Heredity & Environment'] },
          ]
        : b === 'ICSE'
        ? [
            { code: `G${grade}_PHY`, name: 'Physics (ICSE)', topics: ['Force, Work & Power', 'Light & Sound', 'Current Electricity', 'Calorimetry'] },
            { code: `G${grade}_CHEM`, name: 'Chemistry (ICSE)', topics: ['Periodic Table & Bonding', 'Mole Concept', 'Organic Chemistry'] },
            { code: `G${grade}_BIO`, name: 'Biology (ICSE)', topics: ['Genetics', 'Plant Physiology', 'Human Anatomy'] },
          ]
        : [
            { code: `G${grade}_SCI`, name: 'Science (Physics, Chemistry, Biology)', topics: ['Chemical Reactions, Acids & Carbon Compounds', 'Life Processes, Control & Heredity', 'Light: Reflection & Refraction', 'Electricity & Magnetic Effects', 'Laws of Motion & Gravitation'] },
          ];

    return [
      { code: `G${grade}_MATH`, name: 'Mathematics (Board Standard)', topics: ['Real Numbers & Polynomials', 'Quadratic Equations & Arithmetic Progressions', 'Triangles & Coordinate Geometry', 'Trigonometry & Applications', 'Statistics & Probability'] },
      ...sciSubjects,
      { code: `G${grade}_SST`, name: 'Social Science (History, Geography, Polity, Economics)', topics: ['Nationalism in India & Contemporary World', 'Resources, Agriculture & Manufacturing', 'Power Sharing, Federalism & Political Parties', 'Development, Sectors of Indian Economy & Money/Credit'] },
      { code: `G${grade}_ENG`, name: 'English Language & Literature', topics: ['Analytical Paragraphs & Formal Letters', 'Grammar: Modals, Determiners & Reported Speech', 'Literature Prose & Poetry Analysis'] },
      { code: `G${grade}_LANG2`, name: 'Second Language (Hindi / Telugu / Tamil / Kannada / Sanskrit)', topics: ['Grammar', 'Comprehension', 'Composition'] },
    ];
  }

  return [
    { code: `G${grade}_PHY`, name: 'Physics', topics: ['Mechanics & Rotational Motion', 'Thermodynamics & Kinetic Theory', 'Electrostatics, Current & Magnetism', 'Optics, Dual Nature & Semiconductor Electronics'] },
    { code: `G${grade}_CHEM`, name: 'Chemistry', topics: ['Chemical Bonding, Equilibrium & Thermodynamics', 'Solutions, Electrochemistry & Chemical Kinetics', 'd/f Block & Coordination Compounds', 'Organic Chemistry (Haloalkanes to Biomolecules)'] },
    { code: `G${grade}_MATH`, name: 'Mathematics (Core)', topics: ['Sets, Relations & Functions', 'Calculus (Limits, Derivatives, Integrals, Differential Equations)', 'Vectors, 3D Geometry & Linear Programming', 'Probability, Matrices & Determinants'] },
    { code: `G${grade}_BIO`, name: 'Biology', topics: ['Cell Structure & Plant/Human Physiology', 'Reproduction, Genetics & Evolution', 'Biotechnology & Ecology'] },
    { code: `G${grade}_CS`, name: 'Computer Science (Python & SQL)', topics: ['Python Programming & Data Structures', 'File Handling & Exception Handling', 'Relational Databases & SQL', 'Computer Networks'] },
    { code: `G${grade}_ACCT`, name: 'Accountancy', topics: ['Financial Accounting & Ledger', 'Partnership & Company Accounts', 'Financial Statement Analysis & Cash Flow'] },
    { code: `G${grade}_ECON`, name: 'Economics', topics: ['Microeconomics & Consumer Equilibrium', 'Macroeconomics: National Income, Money & Banking', 'Indian Economic Development'] },
    { code: `G${grade}_ENG`, name: 'English Core', topics: ['Unseen Comprehension & Note Making', 'Notice, Article & Report Writing', 'Literature Textual & Extrapolative Questions'] },
  ];
}

