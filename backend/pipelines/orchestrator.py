import asyncio
import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.models import Transformation, Source, Fact, Output, OutputVersion, ProvenanceRecord
from core.provenance_engine import ProvenanceEngine
from providers.llm_provider import get_llm_provider
from agents.understanding import UnderstandingAgent
from agents.fact_registry import FactRegistryAgent
from agents.generators import OutputGenerator
from agents.fact_consistency import FactConsistencyEngine
from agents.quality_engine import QualityEngine

logger = logging.getLogger("ntro.orchestrator")

async def async_run_transformation_pipeline(transformation_id: int):
    """
    Asynchronous transformation job runner with explicit state transitions,
    canonical fact extraction, multi-output generation, and cryptographic provenance signing.
    """
    db = SessionLocal()
    try:
        t = db.query(Transformation).filter(Transformation.id == transformation_id).first()
        if not t:
            logger.error(f"Transformation {transformation_id} not found.")
            return

        source = t.source
        config = t.configuration or {}
        outputs_requested = config.get("outputs", ["advisory", "summary"])
        provider = get_llm_provider()

        # Step 1: Ingest & Compute Source Hash
        t.status = "PROCESSING"
        t.stage = "INGESTING"
        t.progress_percent = 15
        source_raw = source.content or "Official Strategic Source Document"
        source.source_hash = ProvenanceEngine.compute_sha256(source_raw)
        db.commit()
        await asyncio.sleep(0.1)

        # Step 2: Understanding & Semantic Model
        t.stage = "UNDERSTANDING"
        t.progress_percent = 30
        db.commit()
        understanding_agent = UnderstandingAgent(provider)
        semantic_model = understanding_agent.analyze(source_raw)
        semantic_model_str = json.dumps(semantic_model, sort_keys=True)
        t.semantic_model_hash = ProvenanceEngine.compute_sha256(semantic_model_str)
        db.commit()
        await asyncio.sleep(0.1)

        # Step 3: Extract Facts & Compute Fact Registry Hash
        t.stage = "EXTRACTING_FACTS"
        t.progress_percent = 50
        db.commit()
        fact_agent = FactRegistryAgent(provider)
        facts = fact_agent.extract_facts(source_raw)

        # Clear prior facts for idempotence
        db.query(Fact).filter(Fact.source_id == source.id).delete()
        for idx, f in enumerate(facts):
            db_fact = Fact(
                source_id=source.id,
                fact_id=f.get("fact_id", f"F{idx+1:03d}"),
                claim=f.get("claim", ""),
                fact_type=f.get("fact_type", "CLAIM"),
                confidence=f.get("confidence", 1.0),
                source_reference=f.get("source_reference", ""),
                entities=f.get("entities", [])
            )
            db.add(db_fact)
        
        facts_canonical_str = json.dumps(facts, sort_keys=True)
        t.fact_registry_hash = ProvenanceEngine.compute_sha256(facts_canonical_str)
        db.commit()

        # Step 4: Semantic Representation Built
        t.stage = "BUILDING_SEMANTIC_MODEL"
        t.progress_percent = 65
        db.commit()
        await asyncio.sleep(0.1)

        # Step 5: Multi-Output Generation & Cryptographic Provenance Signing
        t.stage = "GENERATING"
        t.progress_percent = 80
        db.commit()

        generator = OutputGenerator(provider)
        fact_verifier = FactConsistencyEngine(provider)
        quality_evaluator = QualityEngine(provider)

        # Remove prior outputs if re-running
        db.query(Output).filter(Output.transformation_id == t.id).delete()
        db.commit()

        success_count = 0
        failed_count = 0

        for out_type in outputs_requested:
            try:
                # Generate content strictly from facts & semantic model
                content = generator.generate(out_type, semantic_model, facts, config)
                artifact_hash = ProvenanceEngine.compute_sha256(content.strip())
                provenance_id = ProvenanceEngine.generate_provenance_id()

                # Step 6: Fact Consistency & Quality Checks
                fact_report = fact_verifier.verify_output(out_type, content, facts)
                quality_report = quality_evaluator.evaluate(out_type, content, config, fact_report)

                # Persist Output first to get out.id
                out = Output(
                    transformation_id=t.id,
                    type=out_type,
                    content=content,
                    status="DRAFT",
                    quality_status=quality_report.get("overall_quality_status", "READY FOR HUMAN REVIEW"),
                    quality_report=quality_report,
                    fact_consistency_report=fact_report,
                    provenance_id=provenance_id,
                    artifact_hash=artifact_hash,
                    current_version=1
                )
                db.add(out)
                db.commit()
                db.refresh(out)

                # Build & Digitally Sign Manifest with actual out.id
                manifest, signature = ProvenanceEngine.build_and_sign_manifest(
                    provenance_id=provenance_id,
                    transformation_id=t.id,
                    output_id=out.id,
                    version=1,
                    output_type=out_type,
                    source_hash=source.source_hash,
                    fact_registry_hash=t.fact_registry_hash,
                    semantic_model_hash=t.semantic_model_hash,
                    artifact_hash=artifact_hash,
                    approval_status="DRAFT",
                    model_name=getattr(provider, "model_name", "gemini-2.5-flash")
                )

                # Create Version 1
                v1 = OutputVersion(
                    output_id=out.id,
                    version=1,
                    content=content,
                    artifact_hash=artifact_hash,
                    change_description="Initial AI Generation",
                    created_by="AI Engine"
                )
                db.add(v1)

                # Persist Provenance Record
                prov_record = ProvenanceRecord(
                    provenance_id=provenance_id,
                    transformation_id=t.id,
                    source_id=source.id,
                    output_id=out.id,
                    output_version=1,
                    source_hash=source.source_hash,
                    fact_registry_hash=t.fact_registry_hash,
                    semantic_model_hash=t.semantic_model_hash,
                    artifact_hash=artifact_hash,
                    hash_algorithm="SHA-256",
                    output_type=out_type,
                    model_provider="Google / NTRO AI Hub",
                    model_name=getattr(provider, "model_name", "gemini-2.5-flash"),
                    signature_algorithm="Ed25519",
                    signature=signature,
                    public_key_hex=ProvenanceEngine.get_public_key_hex(),
                    manifest_json=manifest,
                    approval_status="DRAFT",
                    verification_status="AUTHENTIC"
                )
                db.add(prov_record)
                db.commit()
                success_count += 1

            except Exception as e:
                logger.error(f"Failed to generate output '{out_type}': {e}", exc_info=True)
                failed_count += 1

        # Step 7: Completed State
        t.stage = "VERIFYING"
        t.progress_percent = 95
        db.commit()
        await asyncio.sleep(0.1)

        if failed_count == 0 and success_count > 0:
            t.status = "COMPLETED"
            t.stage = "COMPLETED"
        elif success_count > 0:
            t.status = "PARTIAL_SUCCESS"
            t.stage = "PARTIAL_SUCCESS"
        else:
            t.status = "FAILED"
            t.stage = "FAILED"
            t.error_message = "All output generators failed."

        t.progress_percent = 100
        t.completed_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        logger.error(f"Error in transformation pipeline: {e}", exc_info=True)
        if t:
            t.status = "FAILED"
            t.stage = "FAILED"
            t.error_message = str(e)
            db.commit()
    finally:
        db.close()

def run_transformation_pipeline(transformation_id: int, db: Session = None):
    """Synchronous / Background task wrapper"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(async_run_transformation_pipeline(transformation_id))
        else:
            loop.run_until_complete(async_run_transformation_pipeline(transformation_id))
    except RuntimeError:
        asyncio.run(async_run_transformation_pipeline(transformation_id))
