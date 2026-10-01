# Architecture & System Design — NTRO PS 26154

## 1. Executive Summary
The NTRO Gen AI Platform for Automated Content Transformation provides an end-to-end pipeline that transforms unstructured intelligence, reports, and multimodal media into synchronized communication artefacts.

```text
                         OPERATOR
                            │
                            ↓
                    NEXT.JS DASHBOARD
                            │
                            ↓
                       FASTAPI API
                            │
                            ↓
                TRANSFORMATION ORCHESTRATOR
                            │
             ┌──────────────┼──────────────┐
             ↓              ↓              ↓
          INGESTION     UNDERSTANDING    STORAGE
             │              │              │
       ┌─────┼─────┐        ↓              ↓
       ↓     ↓     ↓    FACT REGISTRY   SQLite / PostgreSQL
     TEXT  DOC   MEDIA      │
             │     │        ↓
           (PDF/  (OCR/  SEMANTIC MODEL
           DOCX)  ASR)      │
       └─────┴─────┴────────┘
                            ↓
                    TRANSFORMATION JOBS
                            │
       ┌────────┬───────────┼──────────┬───────────┐
       ↓        ↓           ↓          ↓           ↓
   LinkedIn     X       Advisory   Summary   Infographic
       │        │           │          │           │
       └────────┴───────────┼──────────┴───────────┘
                            ↓
                      Presentation (PPTX)
                            ↓
                      Video Package
                            ↓
                    QUALITY ENGINE
                            ↓
                  FACT CONSISTENCY ENGINE
                            ↓
                     HUMAN REVIEW
                            ↓
                       VERSIONING
                            ↓
                         EXPORT
```

---

## 2. Key Architectural Components

### A. Ingestion Service (`backend/pipelines/ingestion.py`)
- **PDF Extraction**: Extracts page-by-page text and tables via `PyPDF2`.
- **DOCX Extraction**: Extracts formatted paragraphs and tabular matrices via `python-docx`.
- **Image OCR**: Inspects headers, visual layout, and optical character data via `Pillow` and `OCRProvider`.
- **Video & Audio Transcription**: Transcribes audio tracks into timestamped sentences with language and confidence metadata via `SpeechToTextProvider`.
- **URL Fetching**: Asynchronous client protected by strict SSRF guards, private IP address blocking (`127.0.0.1`, `10.0.0.0/8`, `192.168.0.0/16`, `172.16.0.0/12`), and HTML sanitization.

### B. Understanding & Semantic Model (`backend/agents/understanding.py`)
Extracts global thematic posture:
- `topic`: Operational subject matter.
- `core_message`: Central takeaway statement.
- `entities`: Named facilities, agencies, protocols, systems.
- `timeline`: Chronological time-coded events.
- `risks` and `recommended_actions`.

### C. Canonical Fact Registry (`backend/agents/fact_registry.py`)
**The Single Source of Truth**. Every atomic claim extracted from the source receives:
- `fact_id`: Deterministic identifier (`F001`, `F002`, etc.).
- `fact_type`: Typed categorization (`DATE`, `NUMBER`, `PERCENTAGE`, `ENTITY`, `LOCATION`, `EVENT`, `STATISTIC`, `CLAIM`).
- `source_reference`: Section and paragraph locator.
- `confidence`: Confidence score (0.0 to 1.0).
- `entities`: Associated named entities.

### D. Transformation Engine (`backend/agents/generators.py`)
Consumes the **Semantic Model + Canonical Facts**. All generators receive the exact same factual baseline, preventing cross-channel contradictions.
1. **Strategic Advisory**: Executive format with Executive Summary, Situation, Facts, Assessment, Actions.
2. **Executive Summary**: High-density briefing for leadership.
3. **LinkedIn Post**: Hook, paragraph breakdown, takeaways, hashtags.
4. **X Thread**: Numbered sequence under 280 characters per tweet.
5. **Infographic**: Structured JSON rendered dynamically via React visual cards.
6. **Presentation**: Slide-by-slide structure with speaker notes exported to **real `.pptx` presentations**.
7. **Video Package**: Scene storyboard, camera direction, voiceover narration, and SRT subtitles.

### E. Fact Consistency Engine (`backend/agents/fact_consistency.py`)
Performs automated verification by comparing output claims against canonical facts. Detects:
- `VERIFIED`: Faithfully grounded claims.
- `CONFLICTING`: Mutated dates, numbers, or casualty counts.
- `UNSUPPORTED`: Claims not present in ground truth.
- `MODIFIED`: Altered phrasing.

### F. Quality Engine (`backend/agents/quality_engine.py`)
Evaluates multi-dimensional quality metrics:
- Factual consistency score
- Relevance score
- Tone adherence
- Completeness
- Audience fit

### G. Human-in-the-Loop Review & Versioning (`backend/models/models.py`, `backend/api/endpoints/outputs.py`)
- **Review States**: `DRAFT` → `UNDER_REVIEW` → `APPROVED` / `REJECTED`.
- **Versioning**: Every manual edit or targeted regeneration increments `current_version` and stores an `OutputVersion` record with rollback capability.

### H. Multi-Format Exporters (`backend/providers/export_provider.py`)
- **PPTX**: Generates 16:9 widescreen `.pptx` decks with titles, subtitles, formatted bullet points, and speaker notes via `python-pptx`.
- **DOCX**: Generates executive `.docx` files with headers, divider rules, and bullet styles via `python-docx`.
- **PDF**: Generates print-ready PDFs with custom typography via `reportlab`.
- **Markdown & JSON**: Raw export formats.

---

## 3. Security Architecture
- **No Secret Leakage**: All keys (`GEMINI_API_KEY`, `SECRET_KEY`) reside exclusively in server-side environment variables and are never bundled into client-side code.
- **SSRF Defense**: Strict URL parser blocks loopback, link-local, and RFC 1918 private subnets.
- **Local Fallback**: Full deterministic `MockLLMProvider` ensures sensitive air-gapped deployments and automated test suites operate securely without cloud dependencies.
