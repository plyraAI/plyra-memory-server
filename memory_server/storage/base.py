from abc import ABC, abstractmethod

from ..models import APIKeyInfo, AuthContext


class KeyStore(ABC):
    """Abstract storage for API keys."""

    @abstractmethod
    async def initialize(self) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    async def create_key(
        self,
        key_hash: str,
        key_prefix: str,
        workspace_id: str,
        label: str | None,
        env: str,
        rate_limit_rpm: int,
    ) -> APIKeyInfo: ...

    @abstractmethod
    async def validate_key(self, key_hash: str) -> AuthContext | None:
        """
        Validate a key hash and return AuthContext if valid.
        Also updates last_used_at timestamp.
        Returns None if key not found or revoked.
        """
        ...

    @abstractmethod
    async def list_keys(self, workspace_id: str) -> list[APIKeyInfo]: ...

    @abstractmethod
    async def revoke_key(self, key_id: str) -> bool: ...

    @abstractmethod
    async def get_key_info(self, key_id: str) -> APIKeyInfo | None: ...
