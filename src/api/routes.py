"""API routes for ingestion, reporting, and CI evaluation."""

from typing import Dict, Any, Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.store.sqlite import get_db
from src.services.persistence import PersistenceService
from src.services.normalize import NormalizationPipeline
from src.services.ingest import IngestionHarness
from src.services.agents import run_all_agents

# Create router
router = APIRouter(prefix="/api", tags=["api"])


@router.post("/events", tags=["ingestion"])
def ingest_event(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Ingest a telemetry event from an observability, workflow, or batch system.
    
    Expected payload:
    ```json
    {
        "source": "observability|workflow|batch",
        "source_id": "external-event-id",
        "event_type": "metric|log|trace|business_event",
        "timestamp": "2026-06-10T16:17:07Z",
        "environment": "ci|staging|production",
        "system_name": "service-name",
        "data": {...}
    }
    ```
    """
    try:
        # Validate payload
        is_valid, error = IngestionHarness.validate_event_payload(payload)
        if not is_valid:
            raise ValueError(error)
        
        # Create CI event
        event = PersistenceService.create_ci_event(
            db=db,
            source=payload.get("source"),
            source_id=payload.get("source_id"),
            event_type=payload.get("event_type"),
            timestamp=datetime.fromisoformat(payload.get("timestamp", datetime.utcnow().isoformat())),
            environment=payload.get("environment"),
            data=payload.get("data", {}),
            system_name=payload.get("system_name"),
            correlation_id=payload.get("correlation_id"),
        )
        
        # Normalize event
        normalized_data = NormalizationPipeline.normalize(
            payload.get("data", {}),
            payload.get("event_type")
        )
        
        if normalized_data:
            PersistenceService.update_ci_event_normalization(
                db=db,
                event_id=event.id,
                normalized_data=normalized_data,
                status="normalized"
            )
        
        # Log audit event
        PersistenceService.log_audit_event(
            db=db,
            event_type="ingestion",
            system_name=payload.get("system_name"),
            environment=payload.get("environment"),
            event_data={"event_id": event.id, "source": payload.get("source")},
            related_event_id=event.id,
        )
        
        return {
            "status": "ingested",
            "event_id": event.id,
            "timestamp": event.timestamp.isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ingestion failed: {str(e)}")


@router.get("/events", tags=["ingestion"])
def list_events(
    system_name: Optional[str] = Query(None),
    environment: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """List ingested events."""
    events = PersistenceService.get_ci_events(
        db=db,
        system_name=system_name,
        environment=environment,
        limit=limit,
    )
    return {
        "count": len(events),
        "events": [
            {
                "id": e.id,
                "source": e.source,
                "event_type": e.event_type,
                "timestamp": e.timestamp.isoformat(),
                "environment": e.environment,
                "system_name": e.system_name,
            }
            for e in events
        ],
    }


@router.get("/reports/latest", tags=["reports"])
def get_latest_report(
    system_name: str = Query(..., description="System to retrieve report for"),
    environment: str = Query(..., description="Environment (ci, staging, production)"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get the latest health report for a system."""
    report = PersistenceService.get_latest_health_report(
        db=db,
        system_name=system_name,
        environment=environment,
    )
    if not report:
        raise HTTPException(status_code=404, detail="No report found for this system")
    
    return {
        "id": report.id,
        "system_name": report.system_name,
        "environment": report.environment,
        "status": report.status,
        "health_score": report.health_score,
        "primary_issue": report.primary_issue,
        "suggestions": report.suggestions,
        "created_at": report.created_at.isoformat(),
    }


@router.post("/reports/generate", tags=["reports"])
def generate_report(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Generate a health report for a system based on recent events.
    
    Expected payload:
    ```json
    {
        "system_name": "service-name",
        "environment": "ci|staging|production",
        "lookback_minutes": 60
    }
    ```
    """
    from src.services.reasoning import ReasoningEngine
    from src.services.correlation import CorrelationEngine
    
    system_name = payload.get("system_name")
    environment = payload.get("environment")
    lookback_minutes = payload.get("lookback_minutes", 60)
    
    if not system_name or not environment:
        raise HTTPException(status_code=400, detail="system_name and environment required")
    
    # Retrieve recent normalized events
    events = PersistenceService.get_ci_events(
        db=db,
        system_name=system_name,
        environment=environment,
        limit=100,
    )
    
    # Extract normalized data
    normalized_events = [
        e.normalized for e in events if e.normalized
    ]
    
    if not normalized_events:
        return {
            "system_name": system_name,
            "environment": environment,
            "status": "unknown",
            "health_score": 0.5,
            "primary_issue": "No recent events found",
            "suggestions": [],
            "correlations": [],
        }
    
    # Run reasoning engine
    health_score = ReasoningEngine.compute_health_score(normalized_events)
    primary_issue = ReasoningEngine.identify_primary_issue(normalized_events)
    reasoning = ReasoningEngine.generate_reasoning_narrative(normalized_events)
    suggestions = ReasoningEngine.generate_suggestions(health_score, primary_issue)
    
    # Run correlation engine
    cascades = CorrelationEngine.detect_cascading_failures(normalized_events)
    time_clusters = CorrelationEngine.correlate_by_time_window(normalized_events)
    
    # Determine status
    if health_score >= 0.8:
        status = "healthy"
    elif health_score >= 0.5:
        status = "warning"
    else:
        status = "critical"
    
    # Persist report
    report = PersistenceService.create_health_report(
        db=db,
        system_name=system_name,
        environment=environment,
        status=status,
        health_score=health_score,
        primary_issue=primary_issue,
        suggestions=[s.get("action") for s in suggestions],
    )
    
    # Log audit event
    PersistenceService.log_audit_event(
        db=db,
        event_type="reasoning",
        system_name=system_name,
        environment=environment,
        event_data={
            "score": health_score,
            "events_analyzed": len(normalized_events),
        },
        related_report_id=report.id,
    )
    
    return {
        "id": report.id,
        "system_name": system_name,
        "environment": environment,
        "status": status,
        "health_score": health_score,
        "primary_issue": primary_issue,
        "reasoning": reasoning,
        "suggestions": suggestions,
        "cascading_failures": cascades,
        "event_clusters": len(time_clusters),
        "created_at": report.created_at.isoformat(),
    }


@router.post("/ci/evaluate", tags=["ci-evaluation"])
def ci_evaluate(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Evaluate health for CI deployment gating.
    
    Expected payload:
    ```json
    {
        "system_name": "service-name",
        "environment": "ci",
        "deployment_context": {...}
    }
    ```
    
    Returns: {"verdict": "pass|warn|fail", "rationale": {...}}
    """
    system_name = payload.get("system_name")
    environment = payload.get("environment", "ci")
    
    if not system_name:
        raise HTTPException(status_code=400, detail="system_name is required")
    
    report = PersistenceService.get_latest_health_report(
        db=db,
        system_name=system_name,
        environment=environment,
    )
    
    if not report:
        verdict = "warn"
        rationale = "No health data available"
    else:
        if report.health_score >= 0.8:
            verdict = "pass"
        elif report.health_score >= 0.5:
            verdict = "warn"
        else:
            verdict = "fail"
        rationale = report.primary_issue or "Health assessment complete"
    
    return {
        "system_name": system_name,
        "environment": environment,
        "verdict": verdict,
        "rationale": rationale,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/audit/logs", tags=["audit"])
def get_audit_logs(
    system_name: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve audit logs."""
    logs = PersistenceService.get_audit_logs(
        db=db,
        system_name=system_name,
        limit=limit,
    )
    return {
        "count": len(logs),
        "logs": [
            {
                "id": l.id,
                "event_type": l.event_type,
                "timestamp": l.timestamp.isoformat(),
                "system_name": l.system_name,
                "decision": l.decision,
            }
            for l in logs
        ],
    }


@router.get("/agents/check", tags=["agents"])
def agents_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Run lightweight agent checks and return summarized results."""
    results = run_all_agents(db)
    return {"count": len(results), "agents": results}


@router.get("/hooks/report-api", tags=["hooks"])
def get_report_hook_contract() -> Dict[str, Any]:
    """
    Frontend integration hook surface.
    
    Returns the API contract and route metadata for frontend consumption.
    """
    return {
        "hook": "report-api",
        "description": "Health reporting and evaluation API for frontend integration",
        "base_path": "/api",
        "endpoints": [
            {
                "method": "POST",
                "path": "/events",
                "description": "Ingest telemetry events",
                "response": {"event_id": "string", "status": "string"},
            },
            {
                "method": "GET",
                "path": "/reports/latest",
                "description": "Retrieve latest health report",
                "query_params": {"system_name": "string", "environment": "string"},
                "response": {
                    "id": "string",
                    "status": "string",
                    "health_score": "float",
                    "primary_issue": "string",
                },
            },
            {
                "method": "POST",
                "path": "/ci/evaluate",
                "description": "CI deployment evaluation",
                "response": {"verdict": "pass|warn|fail", "rationale": "string"},
            },
        ],
        "backend_version": "0.1.0",
        "status": "scaffolded",
    }
