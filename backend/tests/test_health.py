import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client: TestClient):
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["data_source"] in {"DEMO provider", "BETPAWA Uganda"}


def test_leagues_after_seed(client: TestClient):
    r = client.get("/api/leagues")
    assert r.status_code == 200
    leagues = r.json()
    assert len(leagues) >= 4
    expected_demo = settings.data_provider.lower() != "betpawa"
    assert all(l["is_demo"] == expected_demo for l in leagues)
