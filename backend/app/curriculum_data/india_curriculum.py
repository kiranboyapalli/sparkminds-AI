"""
SparkMinds AI — India-First Configurable Curriculum Engine (Phase 3)
Supports CBSE, ICSE, State Boards (State-wise configuration), and Other Recognised Boards
across Grades 1 to 12. Never assumes identical subject lists for every grade and board.
"""
from typing import Dict, List, Optional

INDIAN_STATES: List[str] = [
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Delhi (NCT)",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
]

SCHOOL_BOARDS: List[Dict[str, str]] = [
    {"code": "CBSE", "name": "CBSE (Central Board of Secondary Education)"},
    {"code": "ICSE", "name": "ICSE / ISC (CISCE)"},
    {"code": "STATE", "name": "State Board (Select State)"},
    {"code": "OTHER", "name": "Other Recognised Board (IB / IGCSE / NIOS)"},
]

STATE_PRIMARY_LANGUAGES: Dict[str, str] = {
    "Telangana": "Telugu",
    "Andhra Pradesh": "Telugu",
    "Tamil Nadu": "Tamil",
    "Karnataka": "Kannada",
    "Kerala": "Malayalam",
    "Maharashtra": "Marathi",
    "Gujarat": "Gujarati",
    "West Bengal": "Bengali",
    "Punjab": "Punjabi",
    "Odisha": "Odia",
    "Assam": "Assamese",
}


def get_subjects_for_grade_and_board(
    grade: int, board: str, state: Optional[str] = None
) -> List[Dict[str, object]]:
    """
    Returns authentic, grade-appropriate and board-specific subjects with topics.
    Ensures Grade 1, Grade 4, Grade 7, Grade 10, and Grade 12 have distinct, accurate subjects.
    """
    board_upper = (board or "CBSE").upper()
    regional_lang = STATE_PRIMARY_LANGUAGES.get(state or "", "Regional Language")

    # GRADES 1–2 (Foundational Stage: Numeracy, Languages, Joyful Environmental Awareness)
    if grade in (1, 2):
        subjects = [
            {
                "code": f"G{grade}_ENG",
                "name": "English",
                "icon": "BookOpen",
                "mandatory": True,
                "topics": ["Alphabet & Phonics", "Action Words", "Picture Comprehension", "Simple Sentences"],
            },
            {
                "code": f"G{grade}_MATH",
                "name": "Mathematics",
                "icon": "Calculator",
                "mandatory": True,
                "topics": ["Numbers 1 to 100", "Addition & Subtraction", "Shapes & Patterns", "Time & Money Coins"],
            },
            {
                "code": f"G{grade}_HINDI",
                "name": "Hindi (हिन्दी)",
                "icon": "Languages",
                "mandatory": False,
                "topics": ["Varnamala (वर्णमाला)", "Matra Words", "Short Rhymes", "Reading Practice"],
            },
            {
                "code": f"G{grade}_EVS",
                "name": "World Around Us / EVS",
                "icon": "Sprout",
                "mandatory": False,
                "topics": ["My Family & Body", "Plants & Animals", "Good Habits", "Seasons & Festivals"],
            },
        ]
        if board_upper == "STATE" and state:
            subjects.insert(
                1,
                {
                    "code": f"G{grade}_STATE_LANG",
                    "name": f"First Language ({regional_lang})",
                    "icon": "Languages",
                    "mandatory": True,
                    "topics": [f"{regional_lang} Letters", "Basic Spoken & Reading Words", "Simple Stories"],
                },
            )
        return subjects

    # GRADES 3–5 (Preparatory Stage: EVS, Maths, Languages, Computer Basics)
    if grade in (3, 4, 5):
        subjects = [
            {
                "code": f"G{grade}_MATH",
                "name": "Mathematics",
                "icon": "Calculator",
                "mandatory": True,
                "topics": [
                    "Large Numbers & Place Value",
                    "Multiplication & Division",
                    "Fractions Introduction",
                    "Measurement & Geometry",
                    "Word Problems",
                ],
            },
            {
                "code": f"G{grade}_EVS",
                "name": "Environmental Studies (EVS)" if board_upper != "ICSE" else "Science & Social Studies",
                "icon": "Globe",
                "mandatory": True,
                "topics": [
                    "Living & Non-Living Things",
                    "Water, Food & Shelter",
                    "Our Country India",
                    "Human Body & Health",
                ],
            },
            {
                "code": f"G{grade}_ENG",
                "name": "English Language & Literature",
                "icon": "BookOpen",
                "mandatory": True,
                "topics": ["Reading Comprehension", "Nouns, Verbs & Tenses", "Story Writing", "Vocabulary"],
            },
            {
                "code": f"G{grade}_HINDI",
                "name": "Hindi (हिन्दी)",
                "icon": "Languages",
                "mandatory": False,
                "topics": ["Vyakaran (Grammar)", "Paragraph Writing", "Story Comprehension"],
            },
            {
                "code": f"G{grade}_COMP",
                "name": "Computer Studies",
                "icon": "Monitor",
                "mandatory": False,
                "topics": ["Parts of a Computer", "Paint & Word Processing", "Logical Thinking"],
            },
        ]
        if board_upper == "STATE" and state:
            subjects.append(
                {
                    "code": f"G{grade}_REG",
                    "name": f"{regional_lang} ({state} State Curriculum)",
                    "icon": "Languages",
                    "mandatory": True,
                    "topics": ["Reading & Comprehension", "Grammar Basics", "Poems & Moral Stories"],
                }
            )
        return subjects

    # GRADES 6–8 (Middle Stage: Integrated vs Split Sciences depending on Board)
    if grade in (6, 7, 8):
        if board_upper == "ICSE":
            science_subjects = [
                {
                    "code": f"G{grade}_PHY",
                    "name": "Physics (ICSE)",
                    "icon": "Atom",
                    "mandatory": True,
                    "topics": ["Physical Quantities & Measurement", "Force & Pressure", "Energy", "Light & Electricity"],
                },
                {
                    "code": f"G{grade}_CHEM",
                    "name": "Chemistry (ICSE)",
                    "icon": "FlaskConical",
                    "mandatory": True,
                    "topics": ["Matter & Its Composition", "Elements, Compounds & Mixtures", "Atomic Structure", "Chemical Reactions"],
                },
                {
                    "code": f"G{grade}_BIO",
                    "name": "Biology (ICSE)",
                    "icon": "Microscope",
                    "mandatory": True,
                    "topics": ["Plant & Animal Tissues", "Photosynthesis & Respiration", "Human Body Systems", "Health & Hygiene"],
                },
            ]
        else:
            science_subjects = [
                {
                    "code": f"G{grade}_SCI",
                    "name": "General Science",
                    "icon": "FlaskConical",
                    "mandatory": True,
                    "topics": [
                        "Nutrition in Plants & Animals",
                        "Heat, Motion & Time",
                        "Acids, Bases & Salts",
                        "Electric Current & Light",
                    ],
                }
            ]

        base = [
            {
                "code": f"G{grade}_MATH",
                "name": "Mathematics",
                "icon": "Calculator",
                "mandatory": True,
                "topics": [
                    "Integers & Rational Numbers",
                    "Fractions & Decimals",
                    "Algebraic Expressions & Linear Equations",
                    "Ratio, Proportion & Percentage",
                    "Triangles, Mensuration & Data Handling",
                ],
            },
            *science_subjects,
            {
                "code": f"G{grade}_SST",
                "name": "Social Science (History, Civics & Geography)",
                "icon": "Compass",
                "mandatory": True,
                "topics": [
                    "Indian History & Culture",
                    "Our Environment & Geography",
                    "Indian Constitution & Civics",
                ],
            },
            {
                "code": f"G{grade}_ENG",
                "name": "English",
                "icon": "BookOpen",
                "mandatory": True,
                "topics": ["Grammar & Tenses", "Active/Passive Voice", "Formal Letters & Essays", "Literature Analysis"],
            },
            {
                "code": f"G{grade}_LANG2",
                "name": f"Second Language ({regional_lang if board_upper == 'STATE' else 'Hindi / Regional'})",
                "icon": "Languages",
                "mandatory": True,
                "topics": ["Grammar & Sandhi/Samas", "Comprehension", "Letter & Essay Composition"],
            },
            {
                "code": f"G{grade}_LANG3",
                "name": "Third Language (Sanskrit / Regional / Hindi)",
                "icon": "BookMarked",
                "mandatory": False,
                "topics": ["Shabda Roop & Dhatu Roop", "Simple Translation", "Subhashitani"],
            },
            {
                "code": f"G{grade}_COMP",
                "name": "Computer Science / Coding & AI",
                "icon": "Code",
                "mandatory": False,
                "topics": ["Algorithms & Flowcharts", "Python / Scratch Basics", "Cyber Safety"],
            },
        ]
        return base

    # GRADES 9–10 (Secondary Board Exam Stage)
    if grade in (9, 10):
        if board_upper == "STATE" and state in ("Telangana", "Andhra Pradesh"):
            sci_list = [
                {
                    "code": f"G{grade}_PSCI",
                    "name": "Physical Science (Physics & Chemistry)",
                    "icon": "Atom",
                    "mandatory": True,
                    "topics": ["Reflection & Refraction of Light", "Acids, Bases & Salts", "Chemical Equations", "Electric Current"],
                },
                {
                    "code": f"G{grade}_BSCI",
                    "name": "Biological Science",
                    "icon": "Microscope",
                    "mandatory": True,
                    "topics": ["Life Processes (Nutrition, Respiration)", "Control & Coordination", "Heredity & Environment"],
                },
            ]
        elif board_upper == "ICSE":
            sci_list = [
                {
                    "code": f"G{grade}_PHY",
                    "name": "Physics (ICSE Paper 1)",
                    "icon": "Atom",
                    "mandatory": True,
                    "topics": ["Force, Work, Power & Energy", "Light & Sound", "Current Electricity", "Calorimetry"],
                },
                {
                    "code": f"G{grade}_CHEM",
                    "name": "Chemistry (ICSE Paper 2)",
                    "icon": "FlaskConical",
                    "mandatory": True,
                    "topics": ["Periodic Table & Chemical Bonding", "Mole Concept & Stoichiometry", "Electrolysis", "Organic Chemistry"],
                },
                {
                    "code": f"G{grade}_BIO",
                    "name": "Biology (ICSE Paper 3)",
                    "icon": "Microscope",
                    "mandatory": True,
                    "topics": ["Cell Cycle & Genetics", "Plant Physiology", "Human Anatomy & Endocrine System"],
                },
            ]
        else:
            sci_list = [
                {
                    "code": f"G{grade}_SCI",
                    "name": "Science (Physics, Chemistry, Biology)",
                    "icon": "FlaskConical",
                    "mandatory": True,
                    "topics": [
                        "Chemical Reactions & Carbon Compounds",
                        "Life Processes & Genetics",
                        "Light, Electricity & Magnetic Effects",
                        "Force, Laws of Motion & Gravitation",
                    ],
                }
            ]

        return [
            {
                "code": f"G{grade}_MATH",
                "name": "Mathematics (Standard / Applied)",
                "icon": "Calculator",
                "mandatory": True,
                "topics": [
                    "Real Numbers & Polynomials",
                    "Quadratic Equations & Arithmetic Progressions",
                    "Coordinate Geometry & Triangles",
                    "Trigonometry & Applications",
                    "Surface Areas, Volumes, Statistics & Probability",
                ],
            },
            *sci_list,
            {
                "code": f"G{grade}_SST",
                "name": "Social Science (History, Geography, Polity, Economics)",
                "icon": "Compass",
                "mandatory": True,
                "topics": [
                    "Nationalism in India & World History",
                    "Resources, Agriculture & Manufacturing",
                    "Democratic Politics & Power Sharing",
                    "Economic Development & Sectors",
                ],
            },
            {
                "code": f"G{grade}_ENG",
                "name": "English Language & Literature",
                "icon": "BookOpen",
                "mandatory": True,
                "topics": ["Analytical Paragraph & Formal Letters", "Grammar & Determiners/Modals", "Prose & Poetry Analysis"],
            },
            {
                "code": f"G{grade}_LANG2",
                "name": f"Second Language ({regional_lang if board_upper == 'STATE' else 'Hindi / Sanskrit / Regional'})",
                "icon": "Languages",
                "mandatory": True,
                "topics": ["Advanced Grammar", "Unseen Passages", "Literature & Creative Writing"],
            },
            {
                "code": f"G{grade}_IT_AI",
                "name": "Information Technology / Artificial Intelligence",
                "icon": "Cpu",
                "mandatory": False,
                "topics": ["Python Programming", "Data Science & AI Project Cycle", "Database Management (SQL)"],
            },
        ]

    # GRADES 11–12 (Senior Secondary / Junior College Stage: Science, Commerce, Humanities Streams)
    return [
        {
            "code": f"G{grade}_PHY",
            "name": "Physics",
            "icon": "Atom",
            "mandatory": False,
            "topics": ["Mechanics & Rotational Motion", "Thermodynamics", "Electrostatics & Current Electricity", "Optics & Modern Physics"],
        },
        {
            "code": f"G{grade}_CHEM",
            "name": "Chemistry",
            "icon": "FlaskConical",
            "mandatory": False,
            "topics": ["Physical Chemistry (Thermodynamics, Equilibrium, Kinetics)", "Inorganic Chemistry", "Organic Chemistry & Biomolecules"],
        },
        {
            "code": f"G{grade}_MATH",
            "name": "Mathematics",
            "icon": "Calculator",
            "mandatory": False,
            "topics": ["Sets, Relations & Functions", "Calculus (Limits, Derivatives, Integrals)", "Vectors & 3D Geometry", "Probability & Matrices"],
        },
        {
            "code": f"G{grade}_BIO",
            "name": "Biology",
            "icon": "Microscope",
            "mandatory": False,
            "topics": ["Cell Structure & Biomolecules", "Plant & Human Physiology", "Genetics & Evolution", "Biotechnology & Ecology"],
        },
        {
            "code": f"G{grade}_CS",
            "name": "Computer Science (Python & SQL)",
            "icon": "Code",
            "mandatory": False,
            "topics": ["Python Functions & Data Structures", "File Handling", "Relational Databases & SQL", "Computer Networks"],
        },
        {
            "code": f"G{grade}_ACCT",
            "name": "Accountancy",
            "icon": "Landmark",
            "mandatory": False,
            "topics": ["Journal, Ledger & Trial Balance", "Partnership Accounts", "Company Financial Statements", "Cash Flow Analysis"],
        },
        {
            "code": f"G{grade}_ECON",
            "name": "Economics",
            "icon": "TrendingUp",
            "mandatory": False,
            "topics": ["Microeconomics & Consumer Equilibrium", "Macroeconomics & National Income", "Indian Economic Development", "Statistics for Economics"],
        },
        {
            "code": f"G{grade}_BST",
            "name": "Business Studies / Commerce",
            "icon": "Briefcase",
            "mandatory": False,
            "topics": ["Principles of Management", "Business Finance & Marketing", "Entrepreneurship"],
        },
        {
            "code": f"G{grade}_HIST_POL",
            "name": "History / Political Science",
            "icon": "Globe",
            "mandatory": False,
            "topics": ["Indian & World History Themes", "Indian Constitution & Contemporary World Politics"],
        },
        {
            "code": f"G{grade}_ENG_CORE",
            "name": "English Core",
            "icon": "BookOpen",
            "mandatory": True,
            "topics": ["Reading Comprehension & Note Making", "Report, Article & Notice Writing", "Literature Text Analysis"],
        },
    ]


# Mandatory Onboarding Step 5 Options (Exact 14 Challenges from Spec)
ONBOARDING_14_CHALLENGES: List[Dict[str, str]] = [
    {"id": "c1", "label": "I don't understand some concepts."},
    {"id": "c2", "label": "I forget what I studied."},
    {"id": "c3", "label": "I find it difficult to remember answers."},
    {"id": "c4", "label": "I don't know how to start studying."},
    {"id": "c5", "label": "I take too much time to complete homework."},
    {"id": "c6", "label": "I get distracted while studying."},
    {"id": "c7", "label": "I make mistakes even when I know the answer."},
    {"id": "c8", "label": "I find textbook questions difficult to understand."},
    {"id": "c9", "label": "I struggle with application-based questions."},
    {"id": "c10", "label": "I cannot manage homework and exam preparation together."},
    {"id": "c11", "label": "I find it difficult to revise regularly."},
    {"id": "c12", "label": "I hesitate to ask teachers or others for help."},
    {"id": "c13", "label": "I struggle to complete school projects."},
    {"id": "c14", "label": "I feel nervous before exams."},
]

# Mandatory Onboarding Step 6 Goals (Exact 9 Goals + Everything synchronization rule)
ONBOARDING_9_GOALS: List[Dict[str, str]] = [
    {"id": "g1", "label": "Improve my marks."},
    {"id": "g2", "label": "Understand difficult concepts."},
    {"id": "g3", "label": "Complete homework on time."},
    {"id": "g4", "label": "Prepare for examinations."},
    {"id": "g5", "label": "Improve memory and revision."},
    {"id": "g6", "label": "Improve time management."},
    {"id": "g7", "label": "Develop problem-solving skills."},
    {"id": "g8", "label": "Complete school projects."},
    {"id": "g9", "label": "Build confidence and become an independent learner."},
]

