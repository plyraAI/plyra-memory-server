"""Test fixtures for plyra-memory-server."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from memory_server.config import ServerConfig
from memory_server.router import build_app


class _MockEmbedder:
    """
    Fixed-vector embedder for tests.
    Returns deterministic 384-dim vectors without loading any model.
    Same approach as plyra-memory's own test suite.
    """

    _dim = 384

    async def embed(self, text: str) -> list[float]:
        # Deterministic but text-dependent vector (not random)
        seed = sum(ord(c) for c in text) % 10000
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(self._dim).tolist()
        # Normalize
        norm = sum(x**2 for x in vec) ** 0.5
        return [x / norm for x in vec] if norm > 0 else vec

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [await self.embed(t) for t in texts]

    @property
    def dim(self) -> int:
        return self._dim


@pytest.fixture(autouse=True, scope="function")
def mock_embedder():
    """
    Auto-use fixture: patches sentence-transformers embedder in ALL server tests.
    Prevents any HuggingFace network calls during testing.
    """
    mock = _MockEmbedder()

    # Module-level patch — works even for lifespan-initialized components
    with (
        patch(
            "plyra_memory.embedders.sentence_transformers.SentenceTransformerEmbedder._load"
        ) as mock_load,
        patch(
            "plyra_memory.embedders.sentence_transformers.SentenceTransformerEmbedder.embed",
            new=mock.embed,
        ),
        patch(
            "plyra_memory.embedders.sentence_transformers.SentenceTransformerEmbedder.embed_batch",
            new=mock.embed_batch,
        ),
        patch(
            "plyra_memory.embedders.sentence_transformers.SentenceTransformerEmbedder.dim",
            new_callable=lambda: property(lambda self: 384),
        ),
    ):
        # Mock _load to prevent model download
        def mock_load_impl(self):
            self._model = MagicMock()
            self._model.encode = lambda texts, **kwargs: np.array(
                [[0.1] * 384 for _ in (texts if isinstance(texts, list) else [texts])]
            )

        mock_load.side_effect = mock_load_impl
        yield mock


@pytest.fixture
def config(tmp_path):
    return ServerConfig(
        admin_api_key="plm_admin_test_key",
        key_store_url=str(tmp_path / "test_keys.db"),
        store_url=str(tmp_path / "test_memory.db"),
        vectors_url=str(tmp_path / "test_vectors"),
        env="local",
    )


@pytest_asyncio.fixture
async def app(config):
    application = build_app(config)

    # Manually trigger lifespan startup
    async with application.router.lifespan_context(application) as _:
        yield application


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


@pytest_asyncio.fixture
async def api_key(client, config):
    """Create a test API key and return its plaintext value."""
    resp = await client.post(
        "/admin/keys",
        json={"workspace_id": "test-workspace", "label": "test", "env": "test"},
        headers={"Authorization": f"Bearer {config.admin_api_key}"},
    )
    assert resp.status_code == 200
    return resp.json()["key"]


@pytest_asyncio.fixture
async def auth_headers(api_key):
    return {"Authorization": f"Bearer {api_key}"}
