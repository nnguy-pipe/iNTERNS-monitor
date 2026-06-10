"""Tests for orchestration and governance."""

import pytest
from src.services.orchestrator import Orchestrator, ActionStatus
from src.services.governance import GovernanceEngine


@pytest.mark.unit
def test_create_action():
    """Test action creation."""
    action = Orchestrator.create_action(
        system_name="api-gateway",
        environment="production",
        action="scale-up-instances",
        rationale="High CPU detected",
        severity="high",
    )
    
    assert action["system_name"] == "api-gateway"
    assert action["status"] == "pending"
    assert "id" in action


@pytest.mark.unit
def test_approve_action():
    """Test action approval."""
    action = Orchestrator.create_action(
        system_name="api-gateway",
        environment="ci",
        action="restart-service",
        rationale="Service crashed",
        severity="high",
    )
    
    result = Orchestrator.approve_action(action, approver_id="admin")
    assert result["approved"] == True
    assert action["status"] == "approved"


@pytest.mark.unit
def test_execute_action():
    """Test action execution."""
    action = Orchestrator.create_action(
        system_name="api-gateway",
        environment="ci",
        action="clear-cache",
        rationale="Cache stale",
        severity="low",
    )
    
    Orchestrator.approve_action(action, approver_id="admin")
    result = Orchestrator.execute_action(action)
    
    assert result["executed"] == True
    assert action["status"] in ["completed", "failed"]


@pytest.mark.unit
def test_governance_ci_permissive():
    """Test CI environment has permissive governance."""
    can_approve, reason = GovernanceEngine.can_auto_approve(
        environment="ci",
        severity="medium",
        action="restart-service"
    )
    assert can_approve == True


@pytest.mark.unit
def test_governance_production_strict():
    """Test production environment has strict governance."""
    can_approve, reason = GovernanceEngine.can_auto_approve(
        environment="production",
        severity="high",
        action="restart-service"
    )
    assert can_approve == False


@pytest.mark.unit
def test_governance_blocked_actions():
    """Test that dangerous actions are blocked."""
    is_safe, warning = GovernanceEngine.check_safety(
        action="delete all users",
        environment="production"
    )
    assert is_safe == False


@pytest.mark.unit
def test_approval_requirements():
    """Test approval requirements generation."""
    reqs = GovernanceEngine.generate_approval_requirements(
        environment="production",
        severity="critical",
        action="scale-up-db"
    )
    
    assert reqs["requires_human_approval"] == True
    assert "production" in reqs["policy_description"]
