"""Remediation suggestion model."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, DateTime, JSON, Integer, Text, Float, ForeignKey, Boolean
from sqlalchemy.sql import func

from src.store.sqlite import Base


class SuggestionSeverity(str, Enum):
    """Severity of suggested action."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SuggestionStatus(str, Enum):
    """Status of a suggestion."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"


class RemediationSuggestion(Base):
    """Model for remediation suggestions from the reasoning engine."""
    __tablename__ = "remediation_suggestions"

    id = Column(String(36), primary_key=True)
    health_report_id = Column(String(36), ForeignKey("health_reports.id"), nullable=False, index=True)
    
    # Suggestion details
    action = Column(Text, nullable=False)  # What to do
    rationale = Column(Text, nullable=False)  # Why we recommend it
    severity = Column(String(50), nullable=False)  # low, medium, high, critical
    
    # Confidence and impact
    confidence = Column(Float, nullable=False)  # 0.0 - 1.0
    estimated_impact = Column(JSON, nullable=True)  # Expected outcome metrics
    
    # Governance and safety
    governance_check = Column(String(50), default="pending")  # approved, denied, pending
    safety_risk = Column(JSON, nullable=True)  # Potential risks
    requires_approval = Column(Boolean, default=True)  # Whether human approval is required
    
    # Execution tracking
    status = Column(String(50), default="pending")  # pending, approved, rejected, executed, failed
    executed_at = Column(DateTime, nullable=True)
    execution_result = Column(JSON, nullable=True)  # Result of execution
    
    # Environment context
    environment = Column(String(50), nullable=False, index=True)
    system_name = Column(String(255), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<RemediationSuggestion id={self.id} severity={self.severity} status={self.status}>"
