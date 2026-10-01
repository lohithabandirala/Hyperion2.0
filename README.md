# NTRO Gen AI Platform for Automated Content Transformation
**Problem Statement ID:** 26154  
**Organization:** National Technical Research Organisation (NTRO)  
**Title:** Gen AI Platform for Automated Content Transformation

---

## 1. Product Overview
The **NTRO Gen AI Platform for Automated Content Transformation** transforms a common source of information into synchronized, factually grounded, and verified communication artefacts requested by operators.

Unlike simple chatbots or static prompt wrappers, this platform enforces a **Canonical Fact Registry** and **Semantic Model** layer between source analysis and transformation. The exact same canonical facts drive every communication channel, ensuring zero hallucinated discrepancies across formats.

---

## 2. Core Architecture Pipeline
```text
INPUT (Text / PDF / DOCX / Image OCR / Video ASR / URL)
  ↓
CONTENT INGESTION & PARSING
  ↓
CONTENT UNDERSTANDING & TOPIC EXTRACTION
  ↓
CANONICAL FACT REGISTRY (Single Source of Truth)
  ↓
INTERMEDIATE SEMANTIC MODEL
  ↓
TRANSFORMATION ENGINE (Parallel Generation)
  ├── Strategic Incident Advisory (DOCX/PDF/MD)
  ├── Executive Summary Briefing
  ├── LinkedIn Post & Hashtags
  ├── X / Twitter Multi-Tweet Thread
  ├── Visual Infographic (Interactive / SVG / Metrics)
  ├── Presentation Deck (Editable PPTX / Speaker Notes)
  └── Video Package & Storyboard (Scenes, Voiceover, Subtitles)
  ↓
FACT CONSISTENCY VERIFICATION ENGINE
  ↓
QUALITY REVIEW ENGINE
  ↓
HUMAN-IN-THE-LOOP (Edit / Regenerate / Versions / Rollback)
  ↓
MULTI-FORMAT EXPORT (PPTX, DOCX, PDF, MD, JSON)
```

---

## 3. Supported Input Formats
- **Text**: Pasted raw intelligence briefings, emergency updates, advisories.
- **Documents**: `.pdf` (via `PyPDF2`), `.docx` (via `python-docx`).
- **Images**: `.png`, `.jpg`, `.jpeg`, `.webp` (via `OCRProvider`).
- **Video & Audio**: `.mp4`, `.mov`, `.webm` (via `SpeechToTextProvider`).
- **Web URLs**: Public press releases / websites with strict SSRF and private IP blocking.
- **Demo Mode**: 1-Click Load for the *Public Infrastructure Emergency Incident Announcement* scenario.

---

## 4. Supported Output Artefacts
1. **Strategic Incident Advisory**: Official directive with Situation, Facts, Assessment, Actions.
2. **Executive Summary**: High-density decision-maker briefing with impact and implications.
3. **LinkedIn Post**: Structured hook, body, key takeaways, and strategic hashtags.
4. **X / Twitter Thread**: Numbered multi-tweet series under 280 characters.
5. **Visual Infographic**: Headline, key metrics, visual section hierarchy, and key takeaway.
6. **Presentation Slide Deck**: Slide titles, subtitles, bullet points, visual recommendations, and speaker notes exported to **real `.pptx` files**.
7. **Video Package**: Scene-by-scene storyboard, camera direction, voiceover narration, and SRT subtitle cues.

---

## 5. Technology Stack
- **Frontend**: Next.js 15, React 19, Tailwind CSS v4, Axios, Lucide Icons.
- **Backend API**: Python 3.10+, FastAPI, SQLAlchemy, Pydantic v2.
- **Database**: SQLite (local development) / PostgreSQL (production).
- **Document & Presentation Builders**: `python-pptx`, `python-docx`, `reportlab`, `PyPDF2`.
- **Media & OCR**: `Pillow`, `SpeechToTextProvider`, `OCRProvider`.
- **AI Models**: Google Gemini 2.5 Flash via `google-generativeai` with deterministic local `MockLLMProvider` fallback for offline testing.
- **Deployment**: Docker & Docker Compose.

---

## 6. Getting Started & Running

### Prerequisites
- Node.js 18+ & npm
- Python 3.10+
- Git

### A. Run Backend API
```powershell
cd c:\gen\project\backend
# Create & activate virtualenv
python -m venv venv
.\venv\Scripts\activate
# Install dependencies
pip install -r requirements.txt
# Run FastAPI server
python run.py
```
*API & OpenAPI docs will be live at: `http://localhost:8000/docs`*

### B. Run Frontend Dashboard
In a separate terminal:
```powershell
cd c:\gen\project\frontend
npm install
npm run dev
```
*Web dashboard will be live at: `http://localhost:3000`*

### C. Run via Docker Compose
```bash
cd c:\gen\project
docker compose up --build
```

---

## 7. Running Automated Tests
```powershell
cd c:\gen\project\backend
.\venv\Scripts\python.exe -m pytest -v
```

---

## 8. Step-by-Step Demo Flow
1. Open the web dashboard at `http://localhost:3000`.
2. Click **"⚡ Load Demo Scenario"** to load the Northern Corridor Infrastructure Incident report.
3. View the extracted preview and 6 canonical facts.
4. Keep all 7 communication artefacts selected.
5. Configure target parameters (Audience: Executive, Tone: Professional, Detail: Medium).
6. Click **"🚀 TRANSFORM CONTENT"**.
7. Observe live multi-stage progress (*Ingest -> Understand -> Facts -> Semantic -> Generate -> Verified*).
8. Inspect the **Canonical Fact Registry** tab and each generated artefact tab.
9. Verify fact consistency in the right-hand **Fact Verification Inspector**.
10. Click **"✏️ Edit"** to modify text and create **Version 2**.
11. Click **"✓ Approve"** to transition output to approved state.
12. Click **Export** to download `.pptx`, `.docx`, `.pdf`, or `.md` files.
13. View historical transformations on the **/history** page.
