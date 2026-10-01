from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from core.database import get_db
from models.models import Project, Source, Fact

router = APIRouter()

DEMO_INCIDENT_TEXT = """NATIONAL INFRASTRUCTURE COMMISSION | EMERGENCY ADVISORY
INCIDENT REPORT: SUBSTATION-4 AUTOMATED TRIP CONTAINMENT
Date of Event: 15 September 2026, 04:30 IST
Location: Northern Corridor Sector 4 Distribution Hub

1. EXECUTIVE SUMMARY
At 04:30 IST on 15 September 2026, automated circuit protection sensors registered a thermal overcurrent spike at Substation-4 in the Northern Corridor. In accordance with State Emergency Protocol Alpha, automated isolators decoupled the affected high-voltage circuits within 180 milliseconds, containing potential equipment damage. 

2. SCOPE & IMPACT
The isolation temporarily affected power distribution across 3 major industrial sectors in the Northern Corridor. Zero civilian casualties, zero worker injuries, and zero structural fires were reported. All primary telemetry links to the Central Load Dispatch Center remained 100% operational throughout the event.

3. RESTORATION & REMEDIATION
Emergency engineering response teams deployed auxiliary mobile power units. By 05:15 IST (45 minutes post-incident), 12 Megawatts (MW) of auxiliary power were successfully energized, restoring core industrial monitoring and essential services. Scheduled switchover to the redundant primary transformer network is projected for 18:00 IST.

4. PRELIMINARY ROOT CAUSE & INTEGRITY
Preliminary telemetry points to mechanical fatigue in relay assembly R-41. Physical security checks confirmed zero unauthorized intrusion attempts and zero cyber telemetry anomalies. 

5. DIRECTIVES & ACTIONS
- Industrial operators in Sector 4 are advised to maintain backup generator readiness until 18:00 IST.
- Field crews must complete secondary harmonic analysis on transformer bank T-02.
- A final forensic status update will be delivered at 12:00 IST to the Ministry of Power and NTRO oversight."""

@router.post("/load")
def load_demo_data(db: Session = Depends(get_db)):
    """Loads a realistic fictional NTRO infrastructure emergency scenario for instant 1-click testing."""
    # Create or fetch Demo Project
    project = db.query(Project).filter(Project.title == "DEMO: Northern Corridor Infrastructure Incident").first()
    if not project:
        project = Project(
            title="DEMO: Northern Corridor Infrastructure Incident",
            description="Official incident briefing & multi-channel transformation scenario (Non-sensitive demo data)"
        )
        db.add(project)
        db.commit()
        db.refresh(project)

    # Create Source
    source = Source(
        project_id=project.id,
        type="demo",
        filename="DEMO_Substation4_Emergency_Report.txt",
        content=DEMO_INCIDENT_TEXT,
        metadata_json={
            "words_count": len(DEMO_INCIDENT_TEXT.split()),
            "format": "OFFICIAL_REPORT",
            "is_demo": True
        }
    )
    db.add(source)
    db.commit()
    db.refresh(source)

    # Pre-populate canonical facts
    demo_facts = [
        ("F001", "Incident occurred at Substation-4 on 15 September 2026 at 04:30 IST", "DATE", "Section 1", ["Substation-4", "Northern Corridor"]),
        ("F002", "Automated isolators decoupled circuits within 180 milliseconds under Protocol Alpha", "STATISTIC", "Section 1", ["Protocol Alpha"]),
        ("F003", "Power isolation temporarily impacted 3 industrial sectors with zero casualties", "NUMBER", "Section 2", ["3 industrial sectors"]),
        ("F004", "12 MW of auxiliary power was restored within 45 minutes (by 05:15 IST)", "STATISTIC", "Section 3", ["12 MW", "45 minutes"]),
        ("F005", "Telemetry confirms zero cyber-physical intrusion anomalies or security breach", "CLAIM", "Section 4", ["Central Load Dispatch"]),
        ("F006", "Scheduled full network normalization projected for 18:00 IST", "DATE", "Section 3", ["18:00 IST"])
    ]

    for fid, claim, ftype, ref, ents in demo_facts:
        f = Fact(
            source_id=source.id,
            fact_id=fid,
            claim=claim,
            fact_type=ftype,
            confidence=0.99,
            source_reference=ref,
            entities=ents
        )
        db.add(f)
    db.commit()

    return {
        "status": "success",
        "project_id": project.id,
        "source_id": source.id,
        "title": project.title,
        "filename": source.filename,
        "content_preview": DEMO_INCIDENT_TEXT[:200] + "..."
    }
