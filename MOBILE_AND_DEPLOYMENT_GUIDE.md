# SparkMinds AI — Complete Public Deployment, Mobile Packaging & Future-Updates Guide

**Brand Identity:** SparkMinds AI — *Discover. Understand. Achieve.* (`Your Intelligent Learning Buddy`)

---

## 1. Public HTTPS Website Deployment (Recommended Single-Link Setup)

SparkMinds AI is configured so that a single production container ([`Dockerfile`](file:///d:/Agentic%20AI/Projects/EduSpark%20AI/Dockerfile)) compiles the React + Vite Progressive Web App (`frontend/dist`) and serves both the HTTPS website and all `/api/*` endpoints from FastAPI ([`backend/app/main.py`](file:///d:/Agentic%20AI/Projects/EduSpark%20AI/backend/app/main.py)) backed by a dual-persisted SQLite WAL + JSON database (`backend/data/sparkminds_production.db`).

### Option A: Deploy to Render (1-Click Blueprint with Persistent Disk & PR Previews)
1. Push this repository to your GitHub account.
2. Log in to [Render](https://dashboard.render.com) → **New +** → **Blueprint**.
3. Connect your GitHub repository. Render automatically detects [`render.yaml`](file:///d:/Agentic%20AI/Projects/EduSpark%20AI/render.yaml).
4. Set `GEMINI_API_KEY` (optional; the deterministic curriculum engine works even without it).
5. Click **Apply**. Your live public HTTPS URL (e.g. `https://sparkminds-ai-production.onrender.com`) will go live automatically with:
   - Persistent 2 GB disk mounted at `/app/backend/data` (student profiles, SQLite database, backups, and homework uploads survive every redeploy).
   - Automatic Pull Request Preview Environments (`prPreviewsEnabled: true`) so you can test new features with friends before merging to `main`.

### Option B: Deploy to Railway
1. Push this repository to GitHub.
2. Log in to [Railway](https://railway.app) → **New Project** → **Deploy from GitHub repo**.
3. Railway automatically detects [`railway.json`](file:///d:/Agentic%20AI/Projects/EduSpark%20AI/railway.json) and [`Dockerfile`](file:///d:/Agentic%20AI/Projects/EduSpark%20AI/Dockerfile).
4. Add a Volume mounted to `/app/backend/data` and click **Generate Domain** under Settings → Networking to get your public HTTPS website URL.

### Option C: Split Hosting (Frontend on Vercel / Netlify + Backend on Render / Railway)
1. Deploy the backend using Render or Railway and copy its HTTPS URL (e.g. `https://api-sparkminds.onrender.com`).
2. Import the repository into Vercel ([`vercel.json`](file:///d:/Agentic%20AI/Projects/EduSpark%20AI/vercel.json)) or Netlify ([`netlify.toml`](file:///d:/Agentic%20AI/Projects/EduSpark%20AI/netlify.toml)).
3. Set environment variable `VITE_API_BASE_URL=https://api-sparkminds.onrender.com`.
4. Deploy! [`frontend/src/main.tsx`](file:///d:/Agentic%20AI/Projects/EduSpark%20AI/frontend/src/main.tsx) automatically routes all `/api/*` requests to `VITE_API_BASE_URL` with Bearer session tokens attached.

---

## 2. Progressive Web App (PWA) Installation on All Devices

Once opened via the public HTTPS link (or `localhost`):
- **Android Phones & Tablets (Chrome / Edge):** Tap the **📲 Install App** button in the SparkMinds AI top bar or tap the browser menu `⋮` → **Install app / Add to Home screen**.
- **iPhones & iPads (Safari on iOS/iPadOS):** Tap the **Share** button (`⬆`) in Safari → **Add to Home Screen**. SparkMinds AI includes `apple-touch-icon.png` and `apple-mobile-web-app-capable` metadata so it launches full-screen like a native iOS app.
- **Windows Laptops & MacBooks (Chrome / Edge):** Click the **Install SparkMinds AI** icon in the address bar or the **📲 Install App** button in the header.
- **Automatic Updates:** Whenever you deploy a new version, [`frontend/public/sw.js`](file:///d:/Agentic%20AI/Projects/EduSpark%20AI/frontend/public/sw.js) detects the new Service Worker and displays a **↻ Update Ready — Refresh** pill in the top bar without caching private student `/api/*` records.

---

## 3. Android APK & Play Store AAB Build Guide

The Capacitor Android project is pre-configured in [`frontend/android`](file:///d:/Agentic%20AI/Projects/EduSpark%20AI/frontend/android) with application name `SparkMinds AI` and package ID `in.eduspark.ai`.

### Method 1: Cloud Build via GitHub Actions (No Local Android Studio Required)
Every push to `main`/`master` (or manual trigger in the **Actions** tab) runs [`.github/workflows/ci-cd-and-android-build.yml`](file:///d:/Agentic%20AI/Projects/EduSpark%20AI/.github/workflows/ci-cd-and-android-build.yml), which installs JDK 21 + Android SDK in the cloud and uploads:
- `SparkMinds-AI-Android-APK` (`app-debug.apk` for direct Android phone installation)
- `SparkMinds-AI-PlayStore-AAB` (`app-release.aab` for Google Play Console upload)

### Method 2: Local Build on Your Machine
1. Install **Java JDK 21** (Temurin) and **Android Studio** (with Android SDK Platform 34).
2. Run:
   ```powershell
   cd frontend
   npm run build
   npx cap copy android
   cd android
   .\gradlew.bat assembleDebug bundleRelease
   ```
3. Output files:
   - Debug APK: `frontend/android/app/build/outputs/apk/debug/app-debug.apk`
   - Release AAB: `frontend/android/app/build/outputs/bundle/release/app-release.aab`

---

## 4. iOS & iPadOS Native App Packaging (Xcode on macOS)

1. On a Mac with **Xcode 15+** and **CocoaPods** installed, run:
   ```bash
   cd frontend
   npm install @capacitor/ios
   npm run build
   npx cap add ios
   npx cap copy ios
   npx cap open ios
   ```
2. In Xcode, select your Apple Developer Team under **Signing & Capabilities**, choose your iPhone/iPad or **Any iOS Device (arm64)**, and click **Product → Archive** to publish to TestFlight / Apple App Store.

---

## 5. Safe Future-Updates Workflow (Development / Preview vs Production)

To add or modify features after discussing ideas with your friends without disrupting existing students:
1. **Create a feature branch (`preview` or `feat/...`):**
   ```bash
   git checkout -b feat/new-friend-idea
   ```
2. **Test locally (`http://localhost:5173` + `http://127.0.0.1:8000`):**
   - Run `pytest -v` in `backend/` to verify all existing features and student records remain intact.
   - Run `npm run build` in `frontend/` to verify zero TypeScript or layout regressions.
3. **Create a Database Backup before major migrations:**
   - Call `POST /api/admin/database/backup` (creates a timestamped `.db` + `.json` snapshot in `backend/data/backups/`).
4. **Preview with friends:**
   - Open a Pull Request on GitHub to get a dedicated Render Preview link, test with friends on laptop and phone, and merge to `main` when satisfied to update Production automatically!

