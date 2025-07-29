"""Mock classes for integration tests."""

from typing import Any


class MockDatabase:
    """Mock database for integration testing."""

    def __init__(self, host: str, port: int = 5432, **kwargs: Any) -> None:
        self.host = host
        self.port = port
        self.options = kwargs


class MockCache:
    """Mock cache for integration testing."""

    def __init__(self, backend: str = "memory", ttl: int = 3600, **kwargs: Any) -> None:
        self.backend = backend
        self.ttl = ttl
        self.options = kwargs


class MockService:
    """Mock service for integration testing."""

    def __init__(self, name: str, database: Any = None, cache: Any = None) -> None:
        self.name = name
        self.database = database
        self.cache = cache
