# SparkMinds AI ⚡
**Discover. Understand. Achieve.**  
*Your Intelligent Learning Buddy (Grades 1–12 | India-First Educational AI Platform)*

---

## 1. Overview
SparkMinds AI is an adaptive, multilingual, multi-year AI learning companion designed for Indian school students from **Grade 1 to Grade 12** across **CBSE, ICSE, State Boards, and Other Recognised Boards**.

### Core Pillars
- **India-First Curriculum Engine:** Grade-wise, board-wise, and state-wise subject and topic configurations.
- **4 Separate Language Settings:** School Medium of Instruction, Mandatory Preferred Explanation Language, Optional Secondary Language (Bilingual Mode), and Interface Display Language across **English + all 22 Eighth-Schedule Indian Languages**.
- **Multiple-Choice-Only 7-Step Onboarding:** Zero mandatory typing during onboarding, featuring automatic "Everything" goal synchronization.
- **Four Specialist AI Agents + Central Orchestrator:**
  - 🧭 **Discovery Agent** (Understand questions, homework, images, context)
  - 🧠 **Intelligence Agent** (Identify topic gaps, compare multi-year history, separate verified scores from self-reports)
  - 🎯 **Strategy Agent** (Personalised study plans, bilingual step-by-step explanations, hints)
  - 📈 **Growth Agent** (Track progress, resolve learning gaps, detect ups & downs)
- **Permanent Academic Learning History (Grades 1–12):** Immutable yearly academic profiles (*My Academic Journey*) that are never overwritten during annual grade promotion.

---

## 2. Project Structure
- `frontend/` — React + TypeScript + Vite + Tailwind CSS + Lucide Icons (Web & Android Capacitor ready)
- `backend/` — Python 3.11 + FastAPI + Pydantic + Gemini AI Orchestrator & Automated Test Suite
- `IMPLEMENTATION_CHECKLIST.md` — Live phase-by-phase progress tracker

---

## 3. Beginner-Friendly Commands (How to Run on Windows)

### A. Start the Backend Server (FastAPI)
Open a PowerShell terminal in `d:\Agentic AI\Projects\EduSpark AI\backend`:
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```
- Backend API runs at: `http://localhost:8000`
- Interactive API Docs (Swagger UI): `http://localhost:8000/docs`

### B. Start the Frontend Application (React + TypeScript)
Open a second PowerShell terminal in `d:\Agentic AI\Projects\EduSpark AI\frontend`:
```powershell
npm.cmd install
npm.cmd run dev
```
- Frontend Web App runs at: `http://localhost:5173`

### C. Run Automated Tests
```powershell
.\backend\.venv\Scripts\python.exe -m pytest backend/tests
```

