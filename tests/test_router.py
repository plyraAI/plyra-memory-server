"""Tests for HTTP routes."""

import pytest


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "uptime_seconds" in data


@pytest.mark.asyncio
async def test_remember_returns_entry_ids(client, auth_headers):
    resp = await client.post(
        "/v1/remember",
        json={"content": "user is debugging a LangGraph pipeline", "importance": 0.8},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["working_entry_id"] is not None
    assert data["episode_id"] is not None
    assert data["facts_queued"] is True
    assert data["latency_ms"] >= 0


@pytest.mark.asyncio
async def test_remember_with_user_and_agent(client, auth_headers):
    resp = await client.post(
        "/v1/remember",
        json={
            "content": "user prefers Python",
            "user_id": "user_123",
            "agent_id": "support-agent",
            "importance": 0.9,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_recall_returns_results(client, auth_headers):
    # Write first
    await client.post(
        "/v1/remember",
        json={"content": "user loves TypeScript and async patterns"},
        headers=auth_headers,
    )
    # Recall
    resp = await client.post(
        "/v1/recall",
        json={"query": "what does the user prefer?", "top_k": 5},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert "total_found" in data
    assert data["latency_ms"] >= 0


@pytest.mark.asyncio
async def test_context_returns_string(client, auth_headers):
    await client.post(
        "/v1/remember",
        json={"content": "user is building a RAG pipeline with LangChain"},
        headers=auth_headers,
    )
    resp = await client.post(
        "/v1/context",
        json={"query": "what is the user working on?", "token_budget": 512},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["content"], str)
    assert data["token_count"] <= data["token_budget"]


@pytest.mark.asyncio
async def test_stats(client, auth_headers):
    resp = await client.get("/v1/stats", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "working" in data
    assert "episodic" in data
    assert "semantic" in data
    assert "workspace_id" in data


@pytest.mark.asyncio
async def test_workspace_isolation(client, config):
    """Two different workspaces must not see each other's memory."""
    # Create two keys for different workspaces
    r1 = await client.post(
        "/admin/keys",
        json={"workspace_id": "workspace-alpha", "env": "test"},
        headers={"Authorization": f"Bearer {config.admin_api_key}"},
    )
    r2 = await client.post(
        "/admin/keys",
        json={"workspace_id": "workspace-beta", "env": "test"},
        headers={"Authorization": f"Bearer {config.admin_api_key}"},
    )
    key_alpha = r1.json()["key"]
    key_beta = r2.json()["key"]

    # Write to alpha
    await client.post(
        "/v1/remember",
        json={"content": "alpha workspace secret data"},
        headers={"Authorization": f"Bearer {key_alpha}"},
    )

    # Beta should not see it
    resp = await client.post(
        "/v1/recall",
        json={"query": "alpha workspace secret"},
        headers={"Authorization": f"Bearer {key_beta}"},
    )
    data = resp.json()
    # Results should be empty for beta
    assert data["total_found"] == 0


@pytest.mark.asyncio
async def test_invalid_layer_returns_400(client, auth_headers):
    resp = await client.post(
        "/v1/recall",
        json={"query": "test", "layers": ["invalid_layer"]},
        headers=auth_headers,
    )
    assert resp.status_code == 400
