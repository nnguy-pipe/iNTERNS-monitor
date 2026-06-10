from src.store.sqlite import init_db, SessionLocal
from src.services.agents import run_all_agents


def test_run_all_agents_creates_reports():
    # Ensure DB schema exists for persistence
    init_db()
    db = SessionLocal()
    try:
        results = run_all_agents(db)
        assert isinstance(results, list)
        # We expect five agents by default
        assert len(results) == 5
        for r in results:
            assert "agent" in r
            assert "status" in r
            assert "latest_finding" in r
            assert "last_checked" in r
    finally:
        db.close()
