"""Health Report model for reasoning outputs."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, DateTime, JSON, Integer, Text, Float, ForeignKey, Boolean
from sqlalchemy.sql import func

from src.store.sqlite import Base


class HealthStatus(str, Enum):
    """Health status classifications."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class CIVerdict(str, Enum):
    """CI evaluation verdicts."""
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


class HealthReport(Base):
    """Model for health assessment reports."""
    __tablename__ = "health_reports"

    id = Column(String(36), primary_key=True)
    system_name = Column(String(255), nullable=False, index=True)  # System being assessed
    environment = Column(String(50), nullable=False, index=True)  # ci, staging, production
    
    # Health assessment
    status = Column(String(50), nullable=False)  # healthy, warning, critical, unknown
    health_score = Column(Float, nullable=False)  # 0.0 - 1.0
    
    # Objective findings (what was detected)
    primary_issue = Column(Text, nullable=True)  # Main problem identified
    issues = Column(JSON, nullable=True)  # List of detected issues with severity
    
    # Reasoning (why we made that assessment)
    reasoning = Column(JSON, nullable=True)  # Detailed reasoning chain
    
    # Suggestions and confidence
    suggestions = Column(JSON, nullable=True)  # Array of remediation suggestions
    confidence = Column(Float, nullable=True)  # Confidence in suggestions (0.0 - 1.0)
    
    # CI verdict (for deployment gating)
    ci_verdict = Column(String(50), nullable=True)  # pass, warn, fail
    verdict_rationale = Column(JSON, nullable=True)  # Machine-readable explanation
    
    # Correlation and anomalies
    correlated_events = Column(JSON, nullable=True)  # IDs of related events
    anomalies_detected = Column(JSON, nullable=True)  # List of detected anomalies
    
    # Governance and orchestration
    recommended_actions = Column(JSON, nullable=True)  # Actions to take
    governance_check = Column(String(50), nullable=True)  # approved, denied, pending
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Audit trail
    audit_notes = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<HealthReport id={self.id} system={self.system_name} status={self.status}>"
