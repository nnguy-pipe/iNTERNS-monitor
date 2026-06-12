"""Audit service helpers for governance and orchestration decisions."""

from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from src.services.persistence import PersistenceService


class AuditService:
    """Convenience wrappers for structured audit ledger entries."""

    @staticmethod
    def log_decision(
        db: Session,
        system_name: str,
        environment: str,
        decision: str,
        rationale: str,
        event_data: Optional[Dict[str, Any]] = None,
        related_report_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ):
        return PersistenceService.log_audit_event(
            db=db,
            event_type="decision",
            system_name=system_name,
            environment=environment,
            event_data=event_data or {},
            decision=decision,
            rationale=rationale,
            related_report_id=related_report_id,
            user_id=user_id,
        )

    @staticmethod
    def log_action_approval(
        db: Session,
        system_name: str,
        environment: str,
        action_id: str,
        approved: bool,
        rationale: str,
        actor_id: Optional[str] = None,
    ):
        return PersistenceService.log_audit_event(
            db=db,
            event_type="action_approved" if approved else "action_failed",
            system_name=system_name,
            environment=environment,
            event_data={"action_id": action_id, "approved": approved},
            decision="approved" if approved else "rejected",
            rationale=rationale,
            user_id=actor_id,
        )

    @staticmethod
    def log_action_execution(
        db: Session,
        system_name: str,
        environment: str,
        action_id: str,
        executed: bool,
        result: Optional[Dict[str, Any]] = None,
    ):
        return PersistenceService.log_audit_event(
            db=db,
            event_type="action_executed" if executed else "action_failed",
            system_name=system_name,
            environment=environment,
            event_data={"action_id": action_id, "executed": executed, "result": result or {}},
            decision="executed" if executed else "execution_failed",
            rationale="Orchestration action execution outcome",
        )

    @staticmethod
    def log_ci_verdict(
        db: Session,
        system_name: str,
        environment: str,
        verdict: str,
        rationale: Dict[str, Any],
        related_report_id: Optional[str] = None,
    ):
        return PersistenceService.log_audit_event(
            db=db,
            event_type="decision",
            system_name=system_name,
            environment=environment,
            event_data={"ci_verdict": verdict, "rationale": rationale},
            decision=verdict,
            rationale="CI deployment gating verdict",
            related_report_id=related_report_id,
        )