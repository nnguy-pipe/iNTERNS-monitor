"""Action orchestration for remediation workflows."""

import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ActionStatus(str, Enum):
    """Status of remediation action."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class Orchestrator:
    """
    MVP orchestration engine for remediation actions.
    
    Handles:
    - Action approval workflows
    - Safe execution with rollback
    - Governance checks
    - Execution tracking
    """

    @staticmethod
    def create_action(
        system_name: str,
        environment: str,
        action: str,
        rationale: str,
        severity: str,
        requires_approval: bool = True,
    ) -> Dict[str, Any]:
        """
        Create a remediation action.
        
        Returns action with status=pending and ID for tracking.
        """
        return {
            "id": str(uuid.uuid4()),
            "system_name": system_name,
            "environment": environment,
            "action": action,
            "rationale": rationale,
            "severity": severity,
            "status": ActionStatus.PENDING.value,
            "requires_approval": requires_approval,
            "created_at": datetime.utcnow().isoformat(),
            "approved_at": None,
            "executed_at": None,
            "result": None,
        }

    @staticmethod
    def approve_action(
        action: Dict[str, Any],
        approver_id: str,
        approval_notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Approve an action for execution.
        
        Governance check: verify action is allowed in this environment.
        """
        environment = action.get("environment")
        
        # Governance rules for different environments
        if environment == "production":
            # Production requires high-severity justification
            if action.get("severity") not in ["critical", "high"]:
                return {
                    "approved": False,
                    "reason": "Low-severity actions not auto-approved in production",
                }
        
        # Approve action
        action["status"] = ActionStatus.APPROVED.value
        action["approved_at"] = datetime.utcnow().isoformat()
        action["approval_notes"] = approval_notes or f"Approved by {approver_id}"
        
        logger.info(f"Action approved: {action.get('id')} in {environment}")
        return {
            "approved": True,
            "action_id": action.get("id"),
            "status": action.get("status"),
        }

    @staticmethod
    def reject_action(
        action: Dict[str, Any],
        rejection_reason: str,
    ) -> Dict[str, Any]:
        """
        Reject an action.
        """
        action["status"] = ActionStatus.REJECTED.value
        action["rejection_reason"] = rejection_reason
        
        logger.info(f"Action rejected: {action.get('id')} - {rejection_reason}")
        return {
            "approved": False,
            "action_id": action.get("id"),
            "reason": rejection_reason,
        }

    @staticmethod
    def execute_action(action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an approved action.
        
        MVP: simulates execution. Real implementation would call actual remediation.
        """
        if action.get("status") != ActionStatus.APPROVED.value:
            return {
                "executed": False,
                "reason": f"Action not approved (status: {action.get('status')})",
            }
        
        # Mark as executing
        action["status"] = ActionStatus.EXECUTING.value
        action["executed_at"] = datetime.utcnow().isoformat()
        
        # MVP: simulate execution result
        success = True  # In production: call actual remediation API
        
        if success:
            action["status"] = ActionStatus.COMPLETED.value
            action["result"] = {"outcome": "success", "details": "Action executed successfully"}
        else:
            action["status"] = ActionStatus.FAILED.value
            action["result"] = {"outcome": "failure", "details": "Action execution failed"}
        
        logger.info(f"Action executed: {action.get('id')} - {action.get('status')}")
        return {
            "executed": True,
            "action_id": action.get("id"),
            "status": action.get("status"),
            "result": action.get("result"),
        }

    @staticmethod
    def rollback_action(action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rollback an executed action.
        """
        if action.get("status") not in [ActionStatus.COMPLETED.value, ActionStatus.FAILED.value]:
            return {
                "rolled_back": False,
                "reason": "Cannot rollback action in state: " + action.get("status"),
            }
        
        action["status"] = ActionStatus.ROLLED_BACK.value
        action["rolled_back_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Action rolled back: {action.get('id')}")
        return {
            "rolled_back": True,
            "action_id": action.get("id"),
            "status": action.get("status"),
        }
