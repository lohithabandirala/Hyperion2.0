# Repository Merge Audit & Integration Matrix

## Reference Repositories Inspected
1. `samayita34/Gen-AI-Content-Transformer` (Content transformation patterns)
2. `JugalGajjar/Multimodal-AI-Intelligence-Platform` (Multimodal ingestion & async workers)
3. `aws-samples/sample-c2pa-text-provenance-bedrock` (SHA-256 hashing, signed manifests, digital signatures)
4. `richardwooding/c2pa` (C2PA media provenance bindings & boxes)
5. `contentauth/c2pa-conformance-tool` (Manifest conformance & validation rules)

---

## Merge Matrix

| Requirement | Existing Implementation | GitHub Reference | Decision | Reason |
| :--- | :--- | :--- | :--- | :--- |
| **PDF Ingestion** | PyPDF2 text & page extraction | Repo 1 (`Gen-AI-Content-Transformer`) | **Keep & Enhance** | Existing `PyPDF2` extraction works smoothly; add page numbering metadata. |
| **DOCX Ingestion** | python-docx paragraphs & tables | Repo 1 (`Gen-AI-Content-Transformer`) | **Keep & Harden** | Retains tabular matrix representation for intelligence tables. |
| **Image OCR** | Pillow + OCRProvider abstraction | Repo 2 (`Multimodal-AI-Intelligence-Platform`) | **Keep & Adapt** | Provider abstraction allows cloud vision or local OCR without frontend exposure. |
| **Audio / Video ASR** | SpeechToTextProvider with timestamps | Repo 2 (`Multimodal-AI-Intelligence-Platform`) | **Keep & Adapt** | Generates timestamped subtitle segments and speaker confidence. |
| **Async Worker** | BackgroundTasks with stage stepper | Repo 2 (`Multimodal-AI-Intelligence-Platform`) | **Keep & Adapt** | Real 6-stage lifecycle (`INGESTING` → `UNDERSTANDING` → `FACTS` → `SEMANTIC` → `GENERATING` → `VERIFYING` → `COMPLETED`). |
| **Fact Verification** | FactConsistencyEngine (claims matching) | Repo 1 (`Gen-AI-Content-Transformer`) | **Keep & Harden** | Verified against Canonical Fact Registry ground truth. |
| **SHA-256 Hash Chain** | None (New Requirement) | Repo 3 (`sample-c2pa-text-provenance-bedrock`) | **Adapt & Implement** | Cryptographic hash of source, facts, semantic model, and exact artifact bytes. |
| **Digital Signatures** | None (New Requirement) | Repo 3 (`sample-c2pa-text-provenance-bedrock`) | **Adapt & Implement** | Asymmetric Ed25519 signing with server-side private key & public verification. |
| **Signed Manifest** | None (New Requirement) | Repo 3 & Repo 4 (`c2pa`) | **Implement** | Canonical JSON manifest containing Provenance ID, Hashes, Model metadata, and Signature. |
| **Verification API & UI** | None (New Requirement) | Repo 3 & Repo 5 (`c2pa-conformance-tool`) | **Implement** | Dedicated `/api/provenance/verify-file` and `/provenance` frontend page for instant drag-and-drop validation. |
| **QR Code Verification** | None (New Requirement) | NTRO Specification | **Implement** | Embeds cryptographic verification QR codes on exported PDF and DOCX files. |
| **C2PA Integration** | None (New Requirement) | Repo 4 (`c2pa`) & Repo 5 (`c2pa-conformance-tool`) | **Implement Manifest Layer** | Structured C2PA-compatible ingredient assertions and cryptographic claim bindings. |
