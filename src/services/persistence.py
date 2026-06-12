"""Persistence service layer for database operations."""

import uuid
from datetime import datetime
from typing import List, Optional, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.models.ci_event import CIEvent, EventSource, EventType
from src.models.health_report import HealthReport, HealthStatus, CIVerdict
from src.models.remediation import RemediationSuggestion, SuggestionStatus
from src.models.audit_log import AuditLog, AuditEventType


class PersistenceService:
    """Service for all database persistence operations."""

    @staticmethod
    def create_ci_event(
        db: Session,
        source: str,
        source_id: str,
        event_type: str,
        timestamp: datetime,
        environment: str,
        data: Dict[str, Any],
        system_name: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> CIEvent:
        """Create and persist a new CI event."""
        event = CIEvent(
            id=str(uuid.uuid4()),
            source=source,
            source_id=source_id,
            event_type=event_type,
            timestamp=timestamp,
            environment=environment,
            data=data,
            system_name=system_name,
            correlation_id=correlation_id,
            lineage={"ingested_at": datetime.utcnow().isoformat()},
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def update_ci_event_normalization(
        db: Session,
        event_id: str,
        normalized_data: Dict[str, Any],
        status: str = "normalized",
        error: Optional[str] = None,
    ) -> CIEvent:
        """Update event with normalized data."""
        event = db.query(CIEvent).filter(CIEvent.id == event_id).first()
        if event:
            event.normalized = normalized_data
            event.normalization_status = status
            if error:
                event.normalization_error = error
            db.commit()
            db.refresh(event)
        return event

    @staticmethod
    def get_ci_events(
        db: Session,
        system_name: Optional[str] = None,
        environment: Optional[str] = None,
        limit: int = 100,
    ) -> List[CIEvent]:
        """Retrieve CI events with optional filtering."""
        query = db.query(CIEvent)
        if system_name:
            query = query.filter(CIEvent.system_name == system_name)
        if environment:
            query = query.filter(CIEvent.environment == environment)
        return query.order_by(desc(CIEvent.received_at)).limit(limit).all()

    @staticmethod
    def create_health_report(
        db: Session,
        system_name: str,
        environment: str,
        status: str,
        health_score: float,
        primary_issue: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
        score_breakdown: Optional[List[Dict[str, Any]]] = None,
    ) -> HealthReport:
        """Create and persist a health report."""
        report = HealthReport(
            id=str(uuid.uuid4()),
            system_name=system_name,
            environment=environment,
            status=status,
            health_score=health_score,
            primary_issue=primary_issue,
            suggestions=suggestions or [],
            issues=score_breakdown or [],  # Store breakdown in issues field
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def get_latest_health_report(
        db: Session,
        system_name: str,
        environment: str,
    ) -> Optional[HealthReport]:
        """Get the most recent health report for a system."""
        return (
            db.query(HealthReport)
            .filter(HealthReport.system_name == system_name)
            .filter(HealthReport.environment == environment)
            .order_by(desc(HealthReport.created_at))
            .first()
        )

    @staticmethod
    def create_remediation_suggestion(
        db: Session,
        health_report_id: str,
        action: str,
        rationale: str,
        severity: str,
        confidence: float,
        environment: str,
        system_name: str,
    ) -> RemediationSuggestion:
        """Create and persist a remediation suggestion."""
        suggestion = RemediationSuggestion(
            id=str(uuid.uuid4()),
            health_report_id=health_report_id,
            action=action,
            rationale=rationale,
            severity=severity,
            confidence=confidence,
            environment=environment,
            system_name=system_name,
        )
        db.add(suggestion)
        db.commit()
        db.refresh(suggestion)
        return suggestion

    @staticmethod
    def log_audit_event(
        db: Session,
        event_type: str,
        system_name: str,
        environment: str,
        event_data: Dict[str, Any],
        decision: Optional[str] = None,
        rationale: Optional[str] = None,
        related_event_id: Optional[str] = None,
        related_report_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> AuditLog:
        """Create and persist an audit log entry."""
        log = AuditLog(
            id=str(uuid.uuid4()),
            event_type=event_type,
            system_name=system_name,
            environment=environment,
            event_data=event_data,
            decision=decision,
            rationale=rationale,
            related_event_id=related_event_id,
            related_report_id=related_report_id,
            user_id=user_id,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def get_audit_logs(
        db: Session,
        system_name: Optional[str] = None,
        limit: int = 100,
    ) -> List[AuditLog]:
        """Retrieve audit logs."""
        query = db.query(AuditLog)
        if system_name:
            query = query.filter(AuditLog.system_name == system_name)
        return query.order_by(desc(AuditLog.timestamp)).limit(limit).all()
