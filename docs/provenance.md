# Cryptographic Provenance & Content Authenticity Architecture

## 1. Core Distinction
In strategic defense and intelligence organizations (such as NTRO), content authenticity must be strictly defined:
- **SHA-256 Hashing**: Tamper and integrity detection.
- **Asymmetric Digital Signatures**: Authenticity, origin verification, and non-repudiation.
- **Provenance Chain**: End-to-end traceability from raw intelligence source to published briefing.
- **C2PA Standard**: Open cryptographic binding of ingredient assertions and provenance manifests.

> **Important**: Hashing does not prevent unauthorized copying. Cryptographic provenance allows any recipient to mathematically verify the integrity, origin, and approval state of the generated artifact.

---

## 2. The Provenance Hash Chain

```text
       SOURCE DOCUMENT
             │
             ▼
     [ SHA-256: source_hash ]
             │
             ▼
   CANONICAL FACT REGISTRY
             │
             ▼
  [ SHA-256: fact_registry_hash ]
             │
             ▼
     SEMANTIC MODEL
             │
             ▼
  [ SHA-256: semantic_model_hash ]
             │
             ▼
    FINAL ARTEFACT BYTES
             │
             ▼
   [ SHA-256: artifact_hash ]
             │
             ▼
   CANONICAL PROVENANCE MANIFEST
             │
             ▼
  [ ASYMMETRIC DIGITAL SIGNATURE (Ed25519) ]
             │
             ▼
   PROVENANCE ID: NTRO-26154-OUT-YYYYMMDD-XXXXXX
```

---

## 3. Provenance Manifest Schema
```json
{
  "provenance_id": "NTRO-26154-OUT-20261001-8F31C2",
  "transformation_id": 4,
  "output_id": 12,
  "output_version": 2,
  "output_type": "strategic_advisory",
  "hashes": {
    "source_hash": "sha256:a1b2c3...",
    "fact_registry_hash": "sha256:d4e5f6...",
    "semantic_model_hash": "sha256:789abc...",
    "artifact_hash": "sha256:def123..."
  },
  "signing_authority": {
    "issuer": "National Technical Research Organisation (NTRO)",
    "key_id": "ntro-ed25519-prod-01",
    "algorithm": "Ed25519"
  },
  "approval": {
    "status": "APPROVED",
    "approved_by": "Operator #412",
    "timestamp": "2026-10-01T18:00:00Z"
  },
  "signature": "3a7b8c..."
}
```

---

## 4. Verification Workflow
1. **Recipient Uploads File**: Upload any generated PDF, PPTX, DOCX, MD, or JSON to `/provenance`.
2. **Hash Computation**: Server computes SHA-256 over exact file bytes.
3. **Database & Manifest Match**: Matches `artifact_hash` or `provenance_id`.
4. **Signature Verification**: Verifies cryptographic signature against NTRO Public Key.
5. **Result Display**:
   - **`✓ AUTHENTIC`**: Hash matched, signature valid, approval confirmed.
   - **`✗ HASH MISMATCH (MODIFIED)`**: Even a single byte alteration immediately flags the document as tampered.
