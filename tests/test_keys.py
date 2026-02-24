"""Tests for API key generation and validation."""

import pytest

from memory_server.keys import generate_api_key, hash_key, key_prefix


def test_generate_live_key():
    key, key_hash = generate_api_key("live")
    assert key.startswith("plm_live_")
    assert len(key) > 20
    assert len(key_hash) == 64  # SHA-256 hex


def test_generate_test_key():
    key, key_hash = generate_api_key("test")
    assert key.startswith("plm_test_")


def test_keys_are_unique():
    keys = [generate_api_key()[0] for _ in range(100)]
    assert len(set(keys)) == 100  # all unique


def test_hash_is_deterministic():
    key = "plm_live_testkey123"
    assert hash_key(key) == hash_key(key)


def test_different_keys_different_hashes():
    k1, h1 = generate_api_key()
    k2, h2 = generate_api_key()
    assert h1 != h2


def test_key_prefix_format():
    key = "plm_live_abc123def456"
    prefix = key_prefix(key)
    assert prefix.endswith("...")
    assert len(prefix) > 5


@pytest.mark.asyncio
async def test_create_and_validate_key(tmp_path):
    from memory_server.storage.sqlite import SQLiteKeyStore

    store = SQLiteKeyStore(str(tmp_path / "keys.db"))
    await store.initialize()

    key, key_hash = generate_api_key("live")
    prefix = key_prefix(key)

    info = await store.create_key(
        key_hash=key_hash,
        key_prefix=prefix,
        workspace_id="test-ws",
        label="Test Key",
        env="live",
        rate_limit_rpm=600,
    )
    assert info.workspace_id == "test-ws"
    assert info.is_active is True

    # Validate
    auth = await store.validate_key(key_hash)
    assert auth is not None
    assert auth.workspace_id == "test-ws"

    # Revoke
    await store.revoke_key(info.key_id)
    auth2 = await store.validate_key(key_hash)
    assert auth2 is None

    await store.close()
