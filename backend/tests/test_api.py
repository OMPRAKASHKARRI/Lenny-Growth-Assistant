import httpx
import pytest
from app.db import init_db
from app.main import app


@pytest.mark.asyncio
async def test_health_and_session_endpoints():
    await init_db()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        health = await client.get("/api/health")
        created = await client.post("/api/sessions", json={})
        loaded = await client.get(f"/api/sessions/{created.json()['id']}")
    assert health.status_code == 200
    assert health.json()["checks"]["database"] == "ok"
    assert created.status_code == 200
    assert loaded.json()["messages"] == []
