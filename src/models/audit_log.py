"""Audit log model for governance and compliance."""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, JSON, Text
from sqlalchemy.sql import func

from src.store.sqlite import Base


class AuditEventType(str, Enum):
    """Types of audit events."""
    INGESTION = "ingestion"
    NORMALIZATION = "normalization"
    REASONING = "reasoning"
    DECISION = "decision"
    ACTION_APPROVED = "action_approved"
    ACTION_EXECUTED = "action_executed"
    ACTION_FAILED = "action_failed"
    RECONCILIATION = "reconciliation"


class AuditLog(Base):
    """Immutable audit trail for all backend decisions and actions."""
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True)
    event_type = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    
    # Context
    user_id = Column(String(255), nullable=True)  # Who triggered this (if applicable)
    system_name = Column(String(255), nullable=False, index=True)
    environment = Column(String(50), nullable=False, index=True)
    
    # Event details
    event_data = Column(JSON, nullable=False)  # Full event payload
    decision = Column(Text, nullable=True)  # Decision made (if applicable)
    rationale = Column(Text, nullable=True)  # Why the decision was made
    
    # Related entities
    related_event_id = Column(String(36), nullable=True)  # Link to CI event
    related_report_id = Column(String(36), nullable=True)  # Link to health report
    
    # Immutability marker
    immutable = Column(String, default="true")  # Always true, never updated
    
    def __repr__(self):
        return f"<AuditLog id={self.id} event_type={self.event_type}>"
