"""Telemetry ingestion harness."""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Configure debug logging for pipeline tracing
_debug_logger = logging.getLogger(f"{__name__}.debug")
_debug_logger.setLevel(logging.DEBUG)


class IngestionHarness:
    """
    Base class for telemetry ingestion from various sources.
    
    Responsible for:
    - Receiving telemetry from different source types (observability, workflow, batch)
    - Validating payload schema
    - Tagging with source and lineage metadata
    - Passing to normalization pipeline
    """

    @staticmethod
    def validate_event_payload(payload: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate incoming event payload.
        
        Returns: (is_valid, error_message)
        """
        _debug_logger.debug(f"[INGEST] Validating event payload: source={payload.get('source')}, event_type={payload.get('event_type')}, data_keys={list(payload.get('data', {}).keys())}")
        
        required_fields = ["source", "source_id", "event_type", "timestamp", "environment", "data"]
        
        for field in required_fields:
            if field not in payload:
                _debug_logger.warning(f"[INGEST] Validation failed: Missing required field: {field}")
                return False, f"Missing required field: {field}"
        
        # Validate field values
        valid_sources = ["observability", "workflow", "batch", "business"]
        if payload.get("source") not in valid_sources:
            _debug_logger.warning(f"[INGEST] Validation failed: Invalid source: {payload.get('source')}")
            return False, f"Invalid source: {payload.get('source')}"
        
        valid_event_types = ["metric", "log", "trace", "business_event"]
        if payload.get("event_type") not in valid_event_types:
            _debug_logger.warning(f"[INGEST] Validation failed: Invalid event_type: {payload.get('event_type')}")
            return False, f"Invalid event_type: {payload.get('event_type')}"
        
        valid_environments = ["ci", "staging", "production"]
        if payload.get("environment") not in valid_environments:
            _debug_logger.warning(f"[INGEST] Validation failed: Invalid environment: {payload.get('environment')}")
            return False, f"Invalid environment: {payload.get('environment')}"
        
        try:
            datetime.fromisoformat(payload.get("timestamp"))
        except (ValueError, TypeError):
            _debug_logger.warning(f"[INGEST] Validation failed: Invalid timestamp format: {payload.get('timestamp')}")
            return False, f"Invalid timestamp format: {payload.get('timestamp')}"
        
        _debug_logger.debug(f"[INGEST] Event payload validation passed")
        return True, None

    @staticmethod
    def tag_with_lineage(
        payload: Dict[str, Any],
        source: str,
        environment: str,
    ) -> Dict[str, Any]:
        """
        Add lineage metadata to event for traceability.
        """
        return {
            "source": source,
            "environment": environment,
            "ingested_at": datetime.utcnow().isoformat(),
            "schema_version": "1.0",
            "original_payload": payload,
        }

    @staticmethod
    def deduplicate_check(
        event_id: str,
        source: str,
        existing_events: list = None,
    ) -> bool:
        """
        Check if this event is a duplicate.
        
        Returns: True if duplicate, False if unique
        """
        if not existing_events:
            return False
        
        for existing in existing_events:
            if existing.get("source_id") == event_id and existing.get("source") == source:
                logger.warning(f"Duplicate event detected: {source}/{event_id}")
                return True
        
        return False


class IngestionConfig:
    """Configuration for different ingestion sources."""

    # Observability sources
    OBSERVABILITY_CONNECTORS = {
        "prometheus": {"method": "pull", "endpoint": "/metrics"},
        "datadog": {"method": "push", "webhook": "/datadog/webhook"},
        "newrelic": {"method": "push", "webhook": "/newrelic/webhook"},
    }

    # Workflow sources
    WORKFLOW_CONNECTORS = {
        "github_actions": {"method": "webhook", "endpoint": "/github/webhook"},
        "jenkins": {"method": "webhook", "endpoint": "/jenkins/webhook"},
        "circleci": {"method": "webhook", "endpoint": "/circleci/webhook"},
    }

    # Batch processing sources
    BATCH_CONNECTORS = {
        "airflow": {"method": "pull", "endpoint": "/airflow/api"},
        "luigi": {"method": "push", "webhook": "/luigi/webhook"},
    }

    @classmethod
    def get_connector_config(cls, source: str, connector_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific connector."""
        if source == "observability":
            return cls.OBSERVABILITY_CONNECTORS.get(connector_id)
        elif source == "workflow":
            return cls.WORKFLOW_CONNECTORS.get(connector_id)
        elif source == "batch":
            return cls.BATCH_CONNECTORS.get(connector_id)
        return None
