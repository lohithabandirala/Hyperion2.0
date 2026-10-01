# Reference Analysis

## Repositories Inspected

### ContentGoldMine
- **Architecture**: Streamlit frontend, Python backend
- **Important components**: Content repurposing logic, platform-specific generation (LinkedIn, Twitter), batch generation.
- **Useful implementation**: Tone/persona management, multi-platform prompt structures.
- **Dependencies**: Streamlit, LangChain, OpenAI.
- **What we reused/adapted**: The prompt structures for LinkedIn and Twitter generation, tone configuration approach.
- **What we rejected**: Streamlit UI.
- **Reason for rejection**: Does not meet the requirements of a modern, responsive enterprise dashboard. Next.js is preferred.

### Content-Repurposing-Pipeline
- **Architecture**: FastAPI backend, Next.js frontend, PostgreSQL.
- **Important components**: Async processing, job tracking, content pipeline architecture.
- **Useful implementation**: API separation, job queueing.
- **Dependencies**: FastAPI, SQLAlchemy, PostgreSQL, Celery/Redis.
- **What we reused/adapted**: Backend directory structure (FastAPI + SQLAlchemy), async job processing flow.
- **What we rejected**: Specific UI design.
- **Reason for rejection**: Needs to be customized for NTRO specific outputs.

### NovaClip
- **Architecture**: Next.js, FastAPI, Tauri.
- **Important components**: Video processing, multimodal content workflows.
- **Useful implementation**: Media ingestion, video processing queues.
- **What we reused/adapted**: Video abstraction and metadata extraction.
- **What we rejected**: Desktop app wrapper (Tauri).
- **Reason for rejection**: We are building a web-based enterprise platform.

### Recast
- **Architecture**: Next.js
- **Important components**: Multimodal analysis, video understanding, modern AI frontend.
- **What we reused/adapted**: Visual direction prompts, UI design patterns.
- **What we rejected**: Direct client-side AI calls.
- **Reason for rejection**: Security and centralized processing require backend orchestration.

### Clawvisual
- **Architecture**: Next.js.
- **Important components**: Infographic/carousel generation, asynchronous jobs.
- **What we reused/adapted**: Structured infographic JSON generation prompts and schema.
- **What we rejected**: Specialized Next.js specific logic for specific API routes.
- **Reason for rejection**: Moving logic to the unified FastAPI backend.

### OpenShorts
- **Architecture**: Media pipeline (FFmpeg, voiceover, etc.)
- **Important components**: Video assembly, FFmpeg scripts.
- **What we reused/adapted**: Concepts for video package generation (Script -> Storyboard).
- **What we rejected**: Complete auto-generation of B-roll.
- **Reason for rejection**: Provider abstraction is preferred, we will generate the structured video package first.

### Video Content Agent
- **Architecture**: Agent workflow.
- **Important components**: State transitions, approval workflow, human-in-the-loop.
- **What we reused/adapted**: The state machine for approval (DRAFT -> REVIEW -> APPROVED).

### SocialForge
- **Architecture**: Content management system.
- **Important components**: Compliance, approval workflows.
- **What we reused/adapted**: Versioning and output management schema.

## Feature Matrix

| Capability | Reference | Existing Code | Final Approach |
| --- | --- | --- | --- |
| Text ingestion | ContentGoldMine | None | FastAPI unified ingestion endpoint |
| PDF extraction | Content-Repurposing | None | PyPDF2 / pdfminer in FastAPI |
| OCR | Clawvisual | None | Tesseract / Cloud Vision abstraction |
| Video transcription | NovaClip / OpenShorts | None | Whisper integration / Abstraction |
| Content understanding | Recast | None | LLM extraction to Semantic Model |
| Social generation | ContentGoldMine | None | LLM structured output |
| Advisory | N/A | None | Custom prompt & structured output |
| Infographic | Clawvisual | None | Structured JSON to React components |
| Presentation | N/A | None | Structured JSON / PPTX builder |
| Video | OpenShorts | None | Video Package script/storyboard generation |
| Fact verification | N/A | None | Custom Fact Consistency Engine (LLM comparing output vs canonical facts) |
| Human review | Video Content Agent | None | UI state machine & database status |
| Versioning | SocialForge | None | Database versions table |
| Export | Content-Repurposing | None | FastAPI endpoints for PDF/DOCX/TXT |
