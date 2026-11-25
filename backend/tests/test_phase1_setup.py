"""
Phase 1 Automated Tests: Verify FastAPI health & 23 supported Indian languages configuration
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["product"] == "SparkMinds AI"
    assert data["tagline"] == "Dream Beyond Limits. Learn With Fire. Lead With Power!"
    assert data["supported_languages_count"] == 23
    assert "Telugu" in data["tier1_priority_languages"]
    assert len(data["agents_configured"]) == 4


def test_supported_languages_endpoint():
    response = client.get("/api/meta/languages")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 23
    codes = {lang["code"] for lang in data["languages"]}
    assert {"en", "te", "hi", "ta", "kn"}.issubset(codes)

