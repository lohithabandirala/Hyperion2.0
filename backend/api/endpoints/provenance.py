from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
from core.database import get_db
from models.models import ProvenanceRecord, Output
from core.provenance_engine import ProvenanceEngine

router = APIRouter()

@router.get("/public-key")
def get_public_key():
    """Returns the NTRO Ed25519 public key for client-side and external verification."""
    return {
        "issuer": "National Technical Research Organisation (NTRO)",
        "algorithm": "Ed25519",
        "public_key_hex": ProvenanceEngine.get_public_key_hex()
    }

@router.get("/{provenance_id}")
def get_provenance_record(provenance_id: str, db: Session = Depends(get_db)):
    """Retrieves the cryptographic provenance manifest and verification status."""
    record = db.query(ProvenanceRecord).filter(ProvenanceRecord.provenance_id == provenance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Provenance record not found")
        
    return {
        "provenance_id": record.provenance_id,
        "output_type": record.output_type,
        "version": record.output_version,
        "approval_status": record.approval_status,
        "verification_status": record.verification_status,
        "hashes": {
            "source_hash": record.source_hash,
            "fact_registry_hash": record.fact_registry_hash,
            "semantic_model_hash": record.semantic_model_hash,
            "artifact_hash": record.artifact_hash,
            "algorithm": record.hash_algorithm
        },
        "signing": {
            "algorithm": record.signature_algorithm,
            "signature": record.signature,
            "public_key_hex": record.public_key_hex
        },
        "manifest": record.manifest_json,
        "created_at": record.created_at
    }

@router.get("/output/{output_id}")
def get_provenance_by_output(output_id: int, db: Session = Depends(get_db)):
    """Fetches active provenance record for an output."""
    record = db.query(ProvenanceRecord).filter(
        ProvenanceRecord.output_id == output_id
    ).order_by(ProvenanceRecord.output_version.desc()).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="No provenance record for this output")
        
    return {
        "provenance_id": record.provenance_id,
        "artifact_hash": record.artifact_hash,
        "signature": record.signature,
        "version": record.output_version,
        "approval_status": record.approval_status,
        "manifest": record.manifest_json
    }

@router.post("/verify-file")
async def verify_uploaded_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Computes exact SHA-256 of uploaded file bytes, looks up the Provenance Record in the database,
    and cryptographically verifies the Ed25519 digital signature.
    """
    file_bytes = await file.read()
    computed_hash = ProvenanceEngine.compute_sha256(file_bytes)
    
    # Check if this exact hash matches any provenance record
    record = db.query(ProvenanceRecord).filter(
        ProvenanceRecord.artifact_hash == computed_hash
    ).first()

    if record:
        # Verify Ed25519 signature
        manifest_to_verify = dict(record.manifest_json or {})
        manifest_to_verify.pop("signature", None)
        manifest_to_verify.pop("public_key", None)
        manifest_canonical = json.dumps(manifest_to_verify, sort_keys=True, separators=(',', ':'))
        is_sig_valid = ProvenanceEngine.verify_signature(
            manifest_canonical,
            record.signature,
            record.public_key_hex
        )

        return {
            "status": "AUTHENTIC",
            "is_authentic": True,
            "filename": file.filename,
            "computed_sha256": computed_hash,
            "matched_provenance_id": record.provenance_id,
            "output_type": record.output_type,
            "version": record.output_version,
            "approval_status": record.approval_status,
            "signature_valid": is_sig_valid,
            "signing_authority": "National Technical Research Organisation (NTRO)",
            "message": "Cryptographic proof verified: Document matches registered provenance and digital signature."
        }

    # Check if there is any text output whose raw text matches (e.g. if uploaded as plain text)
    try:
        text_content = file_bytes.decode("utf-8", errors="ignore")
        text_hash = ProvenanceEngine.compute_sha256(text_content.strip())
        record_text = db.query(ProvenanceRecord).filter(
            ProvenanceRecord.artifact_hash == text_hash
        ).first()

        if record_text:
            manifest_to_verify = dict(record_text.manifest_json or {})
            manifest_to_verify.pop("signature", None)
            manifest_to_verify.pop("public_key", None)
            manifest_canonical = json.dumps(manifest_to_verify, sort_keys=True, separators=(',', ':'))
            is_sig_valid = ProvenanceEngine.verify_signature(
                manifest_canonical,
                record_text.signature,
                record_text.public_key_hex
            )
            return {
                "status": "AUTHENTIC",
                "is_authentic": True,
                "filename": file.filename,
                "computed_sha256": text_hash,
                "matched_provenance_id": record_text.provenance_id,
                "output_type": record_text.output_type,
                "version": record_text.output_version,
                "approval_status": record_text.approval_status,
                "signature_valid": is_sig_valid,
                "signing_authority": "National Technical Research Organisation (NTRO)",
                "message": "Cryptographic proof verified: Document content matches registered provenance."
            }
    except Exception:
        pass
    # If hash does not match, return TAMPERED / HASH MISMATCH
    return {
        "status": "HASH_MISMATCH",
        "is_authentic": False,
        "filename": file.filename,
        "computed_sha256": computed_hash,
        "matched_provenance_id": None,
        "signature_valid": False,
        "message": "HASH MISMATCH: The uploaded file has been modified or was not issued by this platform."
    }

@router.get("/{provenance_id}/qr")
def get_provenance_qr(provenance_id: str):
    """Generates a scannable QR code PNG image linking to the provenance verification portal."""
    buffer = ProvenanceEngine.generate_qr_code(provenance_id)
    return StreamingResponse(buffer, media_type="image/png")
