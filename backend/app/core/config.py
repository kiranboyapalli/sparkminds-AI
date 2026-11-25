"""
SparkMinds AI — Core Configuration & Language / Curriculum Constants
"""
import os
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv

# Load .env from backend directory and project root if present
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(_BACKEND_DIR / ".env")
load_dotenv(_BACKEND_DIR.parent / ".env")
load_dotenv()


class Settings:
    PROJECT_NAME: str = "SparkMinds AI"
    TAGLINE: str = "Dream Beyond Limits. Learn With Fire. Lead With Power!"
    POSITIONING: str = "Your Intelligent Learning Buddy"
    VERSION: str = "1.0.0-production"
    ENV: str = os.getenv("SPARKMINDS_ENV", os.getenv("EDUSPARK_ENV", "development"))
    DATABASE_URL: str = (
        os.getenv("DATABASE_URL", "").strip()
        or os.getenv("POSTGRES_URL", "").strip()
    )
    GEMINI_API_KEY: str = (
        os.getenv("GEMINI_API_KEY", "").strip()
        or os.getenv("GOOGLE_API_KEY", "").strip()
    )
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000,http://127.0.0.1:8000,capacitor://localhost,http://localhost",
        ).split(",")
        if origin.strip()
    ]


settings = Settings()

# All 22 Languages in the Eighth Schedule of the Constitution of India + English
SUPPORTED_LANGUAGES: List[Dict[str, object]] = [
    {"code": "en", "name": "English", "native_name": "English", "tier": 1, "verified": True},
    {"code": "te", "name": "Telugu", "native_name": "తెలుగు", "tier": 1, "verified": True},
    {"code": "hi", "name": "Hindi", "native_name": "हिन्दी", "tier": 1, "verified": True},
    {"code": "ta", "name": "Tamil", "native_name": "தமிழ்", "tier": 1, "verified": True},
    {"code": "kn", "name": "Kannada", "native_name": "ಕನ್ನಡ", "tier": 1, "verified": True},
    {"code": "as", "name": "Assamese", "native_name": "অসমীয়া", "tier": 2, "verified": False},
    {"code": "bn", "name": "Bengali", "native_name": "বাংলা", "tier": 2, "verified": False},
    {"code": "brx", "name": "Bodo", "native_name": "बड़ो", "tier": 2, "verified": False},
    {"code": "doi", "name": "Dogri", "native_name": "डोगरी", "tier": 2, "verified": False},
    {"code": "gu", "name": "Gujarati", "native_name": "ગુજરાતી", "tier": 2, "verified": False},
    {"code": "ks", "name": "Kashmiri", "native_name": "कॉशुर / کٲشُر", "tier": 2, "verified": False},
    {"code": "gom", "name": "Konkani", "native_name": "कोंकणी", "tier": 2, "verified": False},
    {"code": "mai", "name": "Maithili", "native_name": "मैथिली", "tier": 2, "verified": False},
    {"code": "ml", "name": "Malayalam", "native_name": "മലയാളം", "tier": 2, "verified": False},
    {"code": "mni", "name": "Manipuri (Meitei)", "native_name": "মৈতৈলোন্", "tier": 2, "verified": False},
    {"code": "mr", "name": "Marathi", "native_name": "मराठी", "tier": 2, "verified": False},
    {"code": "ne", "name": "Nepali", "native_name": "नेपाली", "tier": 2, "verified": False},
    {"code": "or", "name": "Odia", "native_name": "ଓଡ଼ିଆ", "tier": 2, "verified": False},
    {"code": "pa", "name": "Punjabi", "native_name": "ਪੰਜਾਬੀ", "tier": 2, "verified": False},
    {"code": "sa", "name": "Sanskrit", "native_name": "संस्कृतम्", "tier": 2, "verified": False},
    {"code": "sat", "name": "Santali", "native_name": "ᱥᱟᱱᱛᱟᱲᱤ", "tier": 2, "verified": False},
    {"code": "sd", "name": "Sindhi", "native_name": "सिन्धी / سنڌي", "tier": 2, "verified": False},
    {"code": "ur", "name": "Urdu", "native_name": "اردو", "tier": 2, "verified": False},
]
