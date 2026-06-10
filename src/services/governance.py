"""Governance rules and approval logic."""

import logging
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class GovernanceLevel(str, Enum):
    """Governance strictness levels."""
    PERMISSIVE = "permissive"  # CI/dev - allow more risky actions
    MODERATE = "moderate"  # Staging - balanced
    STRICT = "strict"  # Production - very careful


class GovernanceEngine:
    """
    MVP governance engine for action approval rules.
    
    Enforces environment-specific policies for remediation actions.
    """

    # Governance policies per environment
    POLICIES = {
        "ci": {
            "level": GovernanceLevel.PERMISSIVE.value,
            "max_auto_approve_severity": "medium",  # Auto-approve low, medium
            "requires_human_approval": False,  # Actions can auto-approve
            "rollback_allowed": True,
            "description": "CI environment - permissive policies",
        },
        "staging": {
            "level": GovernanceLevel.MODERATE.value,
            "max_auto_approve_severity": "low",
            "requires_human_approval": True,
            "rollback_allowed": True,
            "description": "Staging - balanced policies",
        },
        "production": {
            "level": GovernanceLevel.STRICT.value,
            "max_auto_approve_severity": None,  # Never auto-approve
            "requires_human_approval": True,
            "rollback_allowed": False,  # Never auto-rollback
            "description": "Production - strict policies",
        },
    }

    @staticmethod
    def get_policy(environment: str) -> Dict[str, Any]:
        """Get governance policy for environment."""
        return GovernanceEngine.POLICIES.get(
            environment, 
            GovernanceEngine.POLICIES["ci"]  # Default to CI
        )

    @staticmethod
    def can_auto_approve(
        environment: str,
        severity: str,
        action: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Determine if an action can be auto-approved.
        
        Returns: (can_approve, reason)
        """
        policy = GovernanceEngine.get_policy(environment)
        
        max_severity = policy.get("max_auto_approve_severity")
        
        # Severity ordering: low < medium < high < critical
        severity_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        
        action_level = severity_order.get(severity.lower(), 3)
        max_level = severity_order.get(max_severity or "critical", 3)
        
        if max_severity is None:
            return False, f"No auto-approval allowed in {environment}"
        
        if action_level > max_level:
            return False, f"Severity {severity} exceeds auto-approval threshold in {environment}"
        
        # Check action type blocklist
        blocked_actions = [
            "delete_database",
            "delete_volumes",
            "terminate_instances",
        ]
        
        if any(blocked in action.lower() for blocked in blocked_actions):
            return False, f"Action type blocked by governance"
        
        return True, None

    @staticmethod
    def check_safety(action: str, environment: str) -> Tuple[bool, Optional[str]]:
        """
        Check if action is safe to execute.
        
        Returns: (is_safe, warning_message)
        """
        policy = GovernanceEngine.get_policy(environment)
        
        # Safety checks
        if "drop" in action.lower() and "production" in environment.lower():
            return False, "DROP operations blocked in production"
        
        if "truncate" in action.lower() and "production" in environment.lower():
            return False, "TRUNCATE operations blocked in production"
        
        if "delete" in action.lower() and "all" in action.lower():
            return False, "Bulk delete operations require manual approval"
        
        return True, None

    @staticmethod
    def generate_approval_requirements(
        environment: str,
        severity: str,
        action: str,
    ) -> Dict[str, Any]:
        """
        Generate approval requirements for an action.
        """
        policy = GovernanceEngine.get_policy(environment)
        can_auto, reason = GovernanceEngine.can_auto_approve(environment, severity, action)
        is_safe, warning = GovernanceEngine.check_safety(action, environment)
        
        return {
            "environment": environment,
            "policy_level": policy.get("level"),
            "severity": severity,
            "action": action,
            "can_auto_approve": can_auto,
            "auto_approval_reason": reason,
            "is_safe": is_safe,
            "safety_warning": warning,
            "requires_human_approval": policy.get("requires_human_approval"),
            "policy_description": (policy.get("description") or "").lower(),
        }
