import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.models import Source, Project
from schemas.schemas import SourceResponse, SourceCreateText, SourceCreateURL
from pipelines.ingestion import (
    extract_pdf_content,
    extract_docx_content,
    extract_image_content,
    extract_video_content,
    fetch_url_content
)

router = APIRouter()

@router.post("/upload", response_model=SourceResponse)
async def upload_source(
    project_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        # Create default project if missing
        project = Project(title="Default Ingestion Project", description="Auto-created for upload")
        db.add(project)
        db.commit()
        db.refresh(project)
        project_id = project.id

    filename = file.filename or "unknown_file"
    ext = filename.lower().split(".")[-1] if "." in filename else ""
    content_bytes = await file.read()
    
    if len(content_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    content = ""
    metadata = {}
    source_type = "upload"

    try:
        if ext == "pdf" or content_bytes.startswith(b"%PDF"):
            source_type = "pdf"
            content, metadata = extract_pdf_content(content_bytes)
        elif ext in ["docx", "doc"] or content_bytes.startswith(b"PK\x03\x04"):
            source_type = "docx"
            try:
                content, metadata = extract_docx_content(content_bytes)
            except Exception:
                text_raw = content_bytes.decode("utf-8", errors="ignore")
                clean_text = "".join([c for c in text_raw if c.isprintable() or c in "\n\r\t"])
                content = clean_text.strip()
                metadata = {"words_count": len(content.split()), "format": "TEXT_FALLBACK"}
        elif ext in ["png", "jpg", "jpeg", "webp"]:
            source_type = "image"
            content, metadata = extract_image_content(content_bytes, filename)
        elif ext in ["mp4", "mov", "webm", "avi", "mkv"]:
            source_type = "video"
            content, metadata = extract_video_content(content_bytes, filename)
        else:
            source_type = "txt"
            text_raw = content_bytes.decode("utf-8", errors="ignore")
            if text_raw.startswith("PK\x03\x04"):
                try:
                    content, metadata = extract_docx_content(content_bytes)
                    source_type = "docx"
                except Exception:
                    clean_text = "".join([c for c in text_raw if c.isprintable() or c in "\n\r\t"])
                    content = clean_text.strip()
                    metadata = {"words_count": len(content.split()), "format": "TEXT"}
            else:
                content = text_raw.strip()
                metadata = {"words_count": len(content.split()), "format": "TEXT"}
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to process {ext.upper()} file: {str(e)}")

    db_source = Source(
        project_id=project_id,
        type=source_type,
        filename=filename,
        content=content,
        metadata_json=metadata
    )
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

@router.post("/text", response_model=SourceResponse)
def create_text_source(req: SourceCreateText, db: Session = Depends(get_db)):
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty.")
        
    db_source = Source(
        project_id=req.project_id,
        type="text",
        filename=req.title,
        content=req.content,
        metadata_json={"words_count": len(req.content.split()), "format": "RAW_TEXT"}
    )
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

@router.post("/url", response_model=SourceResponse)
async def create_url_source(req: SourceCreateURL, db: Session = Depends(get_db)):
    try:
        content, metadata = await fetch_url_content(req.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch URL: {str(e)}")

    db_source = Source(
        project_id=req.project_id,
        type="url",
        filename=req.url,
        content=content,
        metadata_json=metadata
    )
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

@router.get("/{id}", response_model=SourceResponse)
def get_source(id: int, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.id == id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source
