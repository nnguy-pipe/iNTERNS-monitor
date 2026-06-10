"""CI Event model for telemetry ingestion."""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, JSON, Integer, Text
from sqlalchemy.sql import func

from src.store.sqlite import Base


class EventSource(str, Enum):
    """Telemetry source types."""
    OBSERVABILITY = "observability"  # Prometheus, DataDog, New Relic, etc.
    WORKFLOW = "workflow"  # GitHub Actions, Jenkins, etc.
    BATCH = "batch"  # Airflow, Luigi, etc.
    BUSINESS = "business"  # Custom business events


class EventType(str, Enum):
    """Event type classifications."""
    METRIC = "metric"
    LOG = "log"
    TRACE = "trace"
    BUSINESS_EVENT = "business_event"


class CIEvent(Base):
    """Model for ingested CI/telemetry events."""
    __tablename__ = "ci_events"

    id = Column(String(36), primary_key=True)
    source = Column(String(50), nullable=False)  # Source type (observability, workflow, batch)
    source_id = Column(String(255), nullable=False)  # External ID from source system
    event_type = Column(String(50), nullable=False)  # metric, log, trace, business_event
    timestamp = Column(DateTime, nullable=False, index=True)  # When event occurred
    received_at = Column(DateTime, server_default=func.now(), nullable=False)  # When we ingested it
    environment = Column(String(50), nullable=False, index=True)  # ci, staging, production
    
    # Event payload
    data = Column(JSON, nullable=False)  # Raw event data
    
    # Normalization metadata
    normalized = Column(JSON, nullable=True)  # Normalized form
    normalization_status = Column(String(50), default="pending")  # pending, normalized, failed
    normalization_error = Column(Text, nullable=True)
    
    # Lineage tracking
    lineage = Column(JSON, nullable=True)  # Metadata about event origin
    
    # Indexing for correlation
    system_name = Column(String(255), nullable=True, index=True)  # System being monitored
    correlation_id = Column(String(255), nullable=True, index=True)  # Cross-event correlation
    
    # Audit trail
    ingestion_attempt = Column(Integer, default=1)  # Number of ingestion attempts
    deduplicated = Column(String, default="false")  # Whether this is a duplicate
    
    def __repr__(self):
        return f"<CIEvent id={self.id} source={self.source} type={self.event_type}>"
