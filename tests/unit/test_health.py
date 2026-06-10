"""Tests for the health check endpoint."""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.store.sqlite import init_db, drop_db


@pytest.fixture
def client():
    """Create a test client."""
    # Initialize fresh database for tests
    init_db()
    yield TestClient(app)
    # Cleanup
    drop_db()


@pytest.mark.unit
def test_health_check_ok(client):
    """Test that the health check endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "ok"


@pytest.mark.unit
def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data
    assert "health" in data
