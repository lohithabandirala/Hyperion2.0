from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
import json
from core.database import get_db
from models.models import Output, OutputVersion, Fact, ProvenanceRecord, Transformation
from schemas.schemas import (
    OutputResponse,
    OutputEditRequest,
    OutputRegenerateRequest,
    OutputVersionResponse
)
from providers.llm_provider import get_llm_provider
from providers.export_provider import ExportProvider
from core.provenance_engine import ProvenanceEngine
from agents.generators import OutputGenerator
from agents.fact_consistency import FactConsistencyEngine
from agents.quality_engine import QualityEngine

router = APIRouter()

@router.get("/{id}", response_model=OutputResponse)
def get_output(id: int, db: Session = Depends(get_db)):
    out = db.query(Output).filter(Output.id == id).first()
    if not out:
        raise HTTPException(status_code=404, detail="Output not found")
    return out

@router.patch("/{id}", response_model=OutputResponse)
def edit_output(id: int, req: OutputEditRequest, db: Session = Depends(get_db)):
    """Edits output text, increments version, and signs a new cryptographic provenance record."""
    out = db.query(Output).filter(Output.id == id).first()
    if not out:
        raise HTTPException(status_code=404, detail="Output not found")
        
    out.content = req.content
    out.current_version += 1
    out.status = "UNDER_REVIEW"
    out.updated_at = datetime.utcnow()
    
    # Compute new artifact hash and provenance ID
    new_artifact_hash = ProvenanceEngine.compute_sha256(req.content.strip())
    new_provenance_id = ProvenanceEngine.generate_provenance_id()
    out.artifact_hash = new_artifact_hash
    out.provenance_id = new_provenance_id
    
    # Re-run fact check on edited content
    facts = db.query(Fact).filter(Fact.source_id == out.transformation.source_id).all()
    fact_dicts = [{"fact_id": f.fact_id, "claim": f.claim, "source_reference": f.source_reference} for f in facts]
    
    provider = get_llm_provider()
    fact_report = FactConsistencyEngine(provider).verify_output(out.type, out.content, fact_dicts)
    out.fact_consistency_report = fact_report
    
    # Create new version
    version_record = OutputVersion(
        output_id=out.id,
        version=out.current_version,
        content=req.content,
        artifact_hash=new_artifact_hash,
        change_description=req.change_description or "Human Edited",
        created_by="Human Operator"
    )
    db.add(version_record)

    # Create new signed Provenance Record
    t = out.transformation
    manifest, signature = ProvenanceEngine.build_and_sign_manifest(
        provenance_id=new_provenance_id,
        transformation_id=t.id,
        output_id=out.id,
        version=out.current_version,
        output_type=out.type,
        source_hash=t.source.source_hash or ProvenanceEngine.compute_sha256(t.source.content or ""),
        fact_registry_hash=t.fact_registry_hash or "sha256:default",
        semantic_model_hash=t.semantic_model_hash or "sha256:default",
        artifact_hash=new_artifact_hash,
        approval_status="UNDER_REVIEW"
    )
    prov_record = ProvenanceRecord(
        provenance_id=new_provenance_id,
        transformation_id=t.id,
        source_id=t.source_id,
        output_id=out.id,
        output_version=out.current_version,
        source_hash=t.source.source_hash or "sha256:default",
        fact_registry_hash=t.fact_registry_hash or "sha256:default",
        semantic_model_hash=t.semantic_model_hash or "sha256:default",
        artifact_hash=new_artifact_hash,
        hash_algorithm="SHA-256",
        output_type=out.type,
        signature_algorithm="Ed25519",
        signature=signature,
        public_key_hex=ProvenanceEngine.get_public_key_hex(),
        manifest_json=manifest,
        approval_status="UNDER_REVIEW",
        verification_status="AUTHENTIC"
    )
    db.add(prov_record)
    db.commit()
    db.refresh(out)
    return out

@router.post("/{id}/regenerate", response_model=OutputResponse)
def regenerate_output(id: int, req: OutputRegenerateRequest, db: Session = Depends(get_db)):
    """Targeted regeneration of single output with custom instruction / tone, creating a new provenance version."""
    out = db.query(Output).filter(Output.id == id).first()
    if not out:
        raise HTTPException(status_code=404, detail="Output not found")
        
    t = out.transformation
    source = t.source
    config = dict(t.configuration or {})
    if req.target_language:
        config["language"] = req.target_language
    if req.target_tone:
        config["tone"] = req.target_tone

    facts = db.query(Fact).filter(Fact.source_id == source.id).all()
    fact_dicts = [
        {"fact_id": f.fact_id, "claim": f.claim, "fact_type": f.fact_type, "source_reference": f.source_reference}
        for f in facts
    ]
    semantic_model = {"topic": source.filename, "core_message": source.content[:300] if source.content else ""}

    provider = get_llm_provider()
    generator = OutputGenerator(provider)
    new_content = generator.generate(out.type, semantic_model, fact_dicts, config, custom_instruction=req.instruction or "")

    # Re-evaluate quality & consistency
    fact_report = FactConsistencyEngine(provider).verify_output(out.type, new_content, fact_dicts)
    quality_report = QualityEngine(provider).evaluate(out.type, new_content, config, fact_report)

    new_artifact_hash = ProvenanceEngine.compute_sha256(new_content.strip())
    new_provenance_id = ProvenanceEngine.generate_provenance_id()

    out.content = new_content
    out.current_version += 1
    out.status = "DRAFT"
    out.artifact_hash = new_artifact_hash
    out.provenance_id = new_provenance_id
    out.fact_consistency_report = fact_report
    out.quality_report = quality_report
    out.quality_status = quality_report.get("overall_quality_status", "READY FOR HUMAN REVIEW")
    out.updated_at = datetime.utcnow()

    version_record = OutputVersion(
        output_id=out.id,
        version=out.current_version,
        content=new_content,
        artifact_hash=new_artifact_hash,
        change_description=f"Regenerated: {req.instruction or 'Targeted Prompt'}",
        created_by="AI Engine"
    )
    db.add(version_record)

    # Add Provenance Record
    manifest, signature = ProvenanceEngine.build_and_sign_manifest(
        provenance_id=new_provenance_id,
        transformation_id=t.id,
        output_id=out.id,
        version=out.current_version,
        output_type=out.type,
        source_hash=source.source_hash or "sha256:default",
        fact_registry_hash=t.fact_registry_hash or "sha256:default",
        semantic_model_hash=t.semantic_model_hash or "sha256:default",
        artifact_hash=new_artifact_hash,
        approval_status="DRAFT"
    )
    prov_record = ProvenanceRecord(
        provenance_id=new_provenance_id,
        transformation_id=t.id,
        source_id=source.id,
        output_id=out.id,
        output_version=out.current_version,
        source_hash=source.source_hash or "sha256:default",
        fact_registry_hash=t.fact_registry_hash or "sha256:default",
        semantic_model_hash=t.semantic_model_hash or "sha256:default",
        artifact_hash=new_artifact_hash,
        hash_algorithm="SHA-256",
        output_type=out.type,
        signature_algorithm="Ed25519",
        signature=signature,
        public_key_hex=ProvenanceEngine.get_public_key_hex(),
        manifest_json=manifest,
        approval_status="DRAFT",
        verification_status="AUTHENTIC"
    )
    db.add(prov_record)
    db.commit()
    db.refresh(out)
    return out

@router.post("/{id}/approve", response_model=OutputResponse)
def approve_output(id: int, db: Session = Depends(get_db)):
    out = db.query(Output).filter(Output.id == id).first()
    if not out:
        raise HTTPException(status_code=404, detail="Output not found")
    out.status = "APPROVED"
    
    # Update latest ProvenanceRecord approval status
    prov = db.query(ProvenanceRecord).filter(
        ProvenanceRecord.output_id == out.id,
        ProvenanceRecord.output_version == out.current_version
    ).first()
    if prov:
        prov.approval_status = "APPROVED"
        prov.approved_at = datetime.utcnow()
        prov.manifest_json["approval_status"] = "APPROVED"
        prov.manifest_json["approved_at"] = prov.approved_at.isoformat() + "Z"
        
    db.commit()
    db.refresh(out)
    return out

@router.post("/{id}/reject", response_model=OutputResponse)
def reject_output(id: int, db: Session = Depends(get_db)):
    out = db.query(Output).filter(Output.id == id).first()
    if not out:
        raise HTTPException(status_code=404, detail="Output not found")
    out.status = "REJECTED"
    db.commit()
    db.refresh(out)
    return out

@router.get("/{id}/versions", response_model=list[OutputVersionResponse])
def get_output_versions(id: int, db: Session = Depends(get_db)):
    return db.query(OutputVersion).filter(OutputVersion.output_id == id).order_by(OutputVersion.version.desc()).all()

@router.post("/{id}/rollback/{version_id}", response_model=OutputResponse)
def rollback_output_version(id: int, version_id: int, db: Session = Depends(get_db)):
    out = db.query(Output).filter(Output.id == id).first()
    ver = db.query(OutputVersion).filter(OutputVersion.id == version_id, OutputVersion.output_id == id).first()
    if not out or not ver:
        raise HTTPException(status_code=404, detail="Version not found")
        
    out.content = ver.content
    out.current_version += 1
    out.status = "UNDER_REVIEW"
    out.updated_at = datetime.utcnow()
    
    new_artifact_hash = ProvenanceEngine.compute_sha256(ver.content.strip())
    new_provenance_id = ProvenanceEngine.generate_provenance_id()
    out.artifact_hash = new_artifact_hash
    out.provenance_id = new_provenance_id
    
    new_ver = OutputVersion(
        output_id=out.id,
        version=out.current_version,
        content=ver.content,
        artifact_hash=new_artifact_hash,
        change_description=f"Rollback to v{ver.version}",
        created_by="Human Operator"
    )
    db.add(new_ver)
    db.commit()
    db.refresh(out)
    return out

@router.get("/{id}/export/{format}")
def export_output_format(id: int, format: str, db: Session = Depends(get_db)):
    out = db.query(Output).filter(Output.id == id).first()
    if not out:
        raise HTTPException(status_code=404, detail="Output not found")
        
    fmt = format.lower()
    title = f"NTRO_{out.type.upper()}_{out.id}"

    exported_bytes = None
    media_type = None

    if fmt == "pptx":
        buffer = ExportProvider.export_pptx(out.content, provenance_id=out.provenance_id)
        if buffer.getbuffer().nbytes == 0:
            raise HTTPException(status_code=500, detail="PPTX export buffer empty.")
        exported_bytes = buffer.getvalue()
        media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    elif fmt == "docx":
        buffer = ExportProvider.export_docx(f"{out.type.upper()} ARTEFACT", out.content, provenance_id=out.provenance_id)
        if buffer.getbuffer().nbytes == 0:
            raise HTTPException(status_code=500, detail="DOCX export buffer empty.")
        exported_bytes = buffer.getvalue()
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif fmt == "pdf":
        buffer = ExportProvider.export_pdf(f"{out.type.upper()} ARTEFACT", out.content)
        if buffer.getbuffer().nbytes == 0:
            raise HTTPException(status_code=500, detail="PDF export buffer empty.")
        exported_bytes = buffer.getvalue()
        media_type = "application/pdf"
    elif fmt in ["md", "txt"]:
        exported_bytes = out.content.encode("utf-8")
        media_type = "text/plain"
    elif fmt == "json":
        data = {
            "provenance_id": out.provenance_id,
            "artifact_sha256": out.artifact_hash,
            "output_id": out.id,
            "type": out.type,
            "version": out.current_version,
            "status": out.status,
            "quality_status": out.quality_status,
            "fact_report": out.fact_consistency_report,
            "content": out.content
        }
        exported_bytes = json.dumps(data, indent=2).encode("utf-8")
        media_type = "application/json"
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported export format: {format}")

    # Register exported artifact hash in ProvenanceRecord
    exported_hash = ProvenanceEngine.compute_sha256(exported_bytes)
    prov = db.query(ProvenanceRecord).filter(
        ProvenanceRecord.output_id == out.id,
        ProvenanceRecord.output_version == out.current_version
    ).first()
    if prov:
        prov.artifact_hash = exported_hash
        out.artifact_hash = exported_hash
        manifest, signature = ProvenanceEngine.build_and_sign_manifest(
            provenance_id=prov.provenance_id,
            transformation_id=prov.transformation_id,
            output_id=prov.output_id,
            version=prov.output_version,
            output_type=prov.output_type,
            source_hash=prov.source_hash,
            fact_registry_hash=prov.fact_registry_hash,
            semantic_model_hash=prov.semantic_model_hash,
            artifact_hash=exported_hash,
            approval_status=prov.approval_status
        )
        prov.manifest_json = manifest
        prov.signature = signature
        db.commit()

    return Response(
        content=exported_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{title}.{fmt}"'}
    )
