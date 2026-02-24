"""Tests for authentication middleware."""

import pytest


@pytest.mark.asyncio
async def test_no_auth_returns_401(client):
    resp = await client.post("/v1/remember", json={"content": "test"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_invalid_key_returns_401(client):
    resp = await client.post(
        "/v1/remember",
        json={"content": "test"},
        headers={"Authorization": "Bearer plm_live_invalid_key_000"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_wrong_key_format_returns_401(client):
    resp = await client.post(
        "/v1/remember",
        json={"content": "test"},
        headers={"Authorization": "Bearer not_a_plyra_key"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_valid_key_returns_200(client, auth_headers):
    resp = await client.post(
        "/v1/remember",
        json={"content": "hello world"},
        headers=auth_headers,
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_admin_route_requires_admin_key(client, api_key):
    # Regular API key can't access admin routes
    resp = await client.post(
        "/admin/keys",
        json={"workspace_id": "other"},
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_revoked_key_returns_401(client, config, api_key):
    # First use works
    resp = await client.post(
        "/v1/remember",
        json={"content": "test"},
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert resp.status_code == 200

    # Get key_id and revoke
    keys_resp = await client.get(
        "/admin/keys/test-workspace",
        headers={"Authorization": f"Bearer {config.admin_api_key}"},
    )
    key_id = keys_resp.json()[0]["key_id"]
    await client.delete(
        f"/admin/keys/{key_id}",
        headers={"Authorization": f"Bearer {config.admin_api_key}"},
    )

    # Now rejected
    resp2 = await client.post(
        "/v1/remember",
        json={"content": "test"},
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert resp2.status_code == 401
