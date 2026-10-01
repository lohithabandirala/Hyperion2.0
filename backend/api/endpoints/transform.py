from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from core.database import get_db
from models.models import Transformation, Source, Output, Fact
from schemas.schemas import TransformRequest, TransformationStatusResponse, OutputResponse, FactResponse
from pipelines.orchestrator import async_run_transformation_pipeline
import asyncio

router = APIRouter()

@router.post("/")
def create_transformation(
    req: TransformRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    source = db.query(Source).filter(Source.id == req.source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
        
    db_transform = Transformation(
        source_id=req.source_id,
        configuration={
            "audience": req.audience,
            "tone": req.tone,
            "language": req.language,
            "detail_level": req.detail_level,
            "objective": req.objective,
            "outputs": req.outputs
        },
        status="QUEUED",
        stage="QUEUED",
        progress_percent=5
    )
    db.add(db_transform)
    db.commit()
    db.refresh(db_transform)
    
    # Launch async transformation in background task
    def run_job(transform_id: int):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(async_run_transformation_pipeline(transform_id))
            loop.close()
        except Exception as e:
            pass

    background_tasks.add_task(run_job, db_transform.id)
    
    return {
        "transformation_id": db_transform.id,
        "status": "QUEUED",
        "stage": "QUEUED",
        "progress_percent": 5,
        "message": "Transformation job queued successfully."
    }

@router.get("/{id}/status", response_model=TransformationStatusResponse)
def get_transformation_status(id: int, db: Session = Depends(get_db)):
    t = db.query(Transformation).filter(Transformation.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Transformation not found")
    return t

@router.get("/{id}")
def get_transformation(id: int, db: Session = Depends(get_db)):
    t = db.query(Transformation).filter(Transformation.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Transformation not found")
    return t

@router.get("/{id}/outputs", response_model=list[OutputResponse])
def get_transformation_outputs(id: int, db: Session = Depends(get_db)):
    return db.query(Output).filter(Output.transformation_id == id).all()

@router.get("/{id}/facts", response_model=list[FactResponse])
def get_transformation_facts(id: int, db: Session = Depends(get_db)):
    t = db.query(Transformation).filter(Transformation.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Transformation not found")
    return db.query(Fact).filter(Fact.source_id == t.source_id).all()
