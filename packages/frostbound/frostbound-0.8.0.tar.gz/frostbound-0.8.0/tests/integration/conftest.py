"""Integration test fixtures and utilities for pydanticonf module.

This module provides shared fixtures for integration testing, including
temporary file management, environment variable isolation, and registry
cleanup to ensure test independence.
"""

from __future__ import annotations

import os
import sys
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any, TypeVar

import pytest
import yaml
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


# Test helper classes that are shared across tests
class MemoryCache:
    """Simple in-memory cache implementation."""

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache: dict[str, Any] = {}

    def get(self, key: str) -> Any:
        return self.cache.get(key)

    def set(self, key: str, value: Any) -> None:
        if len(self.cache) >= self.max_size:
            # Simple eviction: remove first item
            first_key = next(iter(self.cache))
            del self.cache[first_key]
        self.cache[key] = value


class SimpleService:
    """A simple service class for testing."""

    def __init__(self, name: str, port: int = 8080):
        self.name = name
        self.port = port
        self.running = False

    def start(self) -> None:
        self.running = True


class DatabaseClient:
    """A database client class for testing dependency injection."""

    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connected = False

    def connect(self) -> None:
        self.connected = True


class ConfigurablePlugin:
    """A plugin class that accepts variable configuration."""

    def __init__(self, plugin_name: str, **options: Any):
        self.plugin_name = plugin_name
        self.options = options
        self.initialized = True


class NestedComponent:
    """A component that contains other components."""

    def __init__(self, name: str, sub_components: list[Any] | None = None):
        self.name = name
        self.sub_components = sub_components or []


class ServiceWithDependencies:
    """Service that accepts various injected dependencies."""

    def __init__(
        self,
        service_name: str,
        database: Any | None = None,
        cache: Any | None = None,
        logger: Any | None = None,
        config: dict | None = None,
        api_key: str | None = None,
        max_retries: int = 3,
        failing_dep: Any | None = None,
        db_client: Any | None = None,
        cache_client: Any | None = None,
        metrics_client: Any | None = None,
    ):
        self.service_name = service_name
        self.database = database
        self.cache = cache
        self.logger = logger
        self.config = config or {}
        self.api_key = api_key
        self.max_retries = max_retries
        self.failing_dep = failing_dep
        self.db_client = db_client
        self.cache_client = cache_client
        self.metrics_client = metrics_client
        self.initialized = True


class CacheUser:
    """A class that uses a cache."""

    def __init__(self, cache: Any | None = None):
        self.cache = cache


class ServiceA:
    """Service A for circular dependency testing."""

    def __init__(self, service_b: Any | None = None):
        self.service_b = service_b


class ServiceB:
    """Service B for circular dependency testing."""

    def __init__(self, service_a: Any | None = None):
        self.service_a = service_a


@pytest.fixture(autouse=True)
def clean_registries() -> Generator[None]:
    """Clean all registries before and after each test to ensure isolation.

    This fixture automatically runs for every test, ensuring that:
    - Dependencies are cleared
    - No cross-test contamination occurs

    Yields
    ------
    None
        Control flow returns to test execution.
    """
    # Import here to avoid circular dependencies
    from frostbound.pydanticonf import clear_dependencies

    # Clear before test
    clear_dependencies()

    yield

    # Clear after test
    clear_dependencies()


@pytest.fixture
def temp_yaml_file() -> Generator[Path]:
    """Create a temporary YAML file that is automatically cleaned up.

    Yields
    ------
    Path
        Path object pointing to the temporary file.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        temp_path = Path(f.name)

    try:
        yield temp_path
    finally:
        if temp_path.exists():
            temp_path.unlink()


@pytest.fixture
def create_yaml_file() -> Generator[callable]:
    """Factory fixture for creating YAML files with content.

    Yields
    ------
    callable
        Function that accepts content dict and returns Path to created file.
    """
    created_files: list[Path] = []

    def _create_file(content: dict[str, Any], filename: str | None = None) -> Path:
        """Create a YAML file with given content.

        Parameters
        ----------
        content : dict[str, Any]
            Dictionary to serialize as YAML.
        filename : str | None
            Optional filename. If not provided, a random name is used.

        Returns
        -------
        Path
            Path to the created file.
        """
        if filename:
            path = Path(tempfile.gettempdir()) / filename
        else:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                path = Path(f.name)

        with open(path, "w") as f:
            yaml.safe_dump(content, f)

        created_files.append(path)
        return path

    yield _create_file

    # Cleanup all created files
    for path in created_files:
        if path.exists():
            path.unlink()


@pytest.fixture
def env_vars() -> Generator[dict[str, str]]:
    """Temporarily set environment variables for testing.

    Yields
    ------
    dict[str, str]
        Dictionary for setting environment variables. Any changes
        are automatically reverted after the test.
    """
    original_env = os.environ.copy()

    class EnvVarsDict(dict):
        """Dict subclass that updates os.environ when modified."""

        def __setitem__(self, key: str, value: str) -> None:
            super().__setitem__(key, value)
            os.environ[key] = value

        def update(self, *args, **kwargs) -> None:
            super().update(*args, **kwargs)
            # Also update os.environ
            if args and isinstance(args[0], dict):
                os.environ.update(args[0])
            os.environ.update(kwargs)

    test_env = EnvVarsDict()

    yield test_env

    # Ensure environment is restored
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def sample_database_config() -> dict[str, Any]:
    """Sample database configuration for testing.

    Returns
    -------
    dict[str, Any]
        Database configuration with nested structure.
    """
    return {
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "testdb",
            "user": "testuser",
            "password": "testpass",
            "pool": {"min_size": 10, "max_size": 20, "timeout": 30.0},
        }
    }


@pytest.fixture
def sample_logging_config() -> dict[str, Any]:
    """Sample logging configuration for testing.

    Returns
    -------
    dict[str, Any]
        Logging configuration with handlers and formatters.
    """
    return {
        "logging": {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}},
            "handlers": {
                "console": {
                    "_target_": "logging.StreamHandler",
                    "level": "INFO",
                    "formatter": "standard",
                    "stream": "ext://sys.stdout",
                },
                "file": {
                    "_target_": "logging.FileHandler",
                    "level": "DEBUG",
                    "formatter": "standard",
                    "filename": "app.log",
                },
            },
            "root": {"level": "INFO", "handlers": ["console", "file"]},
        }
    }


@pytest.fixture
def sample_dependency_objects() -> dict[str, Any]:
    """Common dependency objects for injection tests.

    Returns
    -------
    dict[str, Any]
        Dictionary of sample objects that can be used as dependencies.
    """

    class DatabaseConnection:
        """Mock database connection for testing."""

        def __init__(self, host: str, port: int):
            self.host = host
            self.port = port
            self.connected = True

    class Logger:
        """Mock logger for testing."""

        def __init__(self, name: str):
            self.name = name
            self.logs: list[str] = []

        def log(self, message: str) -> None:
            self.logs.append(message)

    class CacheClient:
        """Mock cache client for testing."""

        def __init__(self, ttl: int = 300):
            self.ttl = ttl
            self.cache: dict[str, Any] = {}

    return {
        "db_connection": DatabaseConnection("localhost", 5432),
        "logger": Logger("test_logger"),
        "cache": CacheClient(ttl=600),
        "api_key": "test-api-key-12345",
        "base_url": "https://api.example.com",
    }


@pytest.fixture
def complex_nested_config() -> dict[str, Any]:
    """Complex nested configuration for advanced testing.

    Returns
    -------
    dict[str, Any]
        Multi-level nested configuration with various patterns.
    """
    return {
        "app": {
            "name": "TestApp",
            "version": "1.0.0",
            "services": [
                {
                    "_target_": "frostbound.pydanticonf.DynamicConfig",
                    "target_": "tests.fixtures.Service",
                    "name": "auth_service",
                    "config": {"secret_key": "auth-secret", "token_expiry": 3600},
                },
                {
                    "_target_": "frostbound.pydanticonf.DynamicConfig",
                    "target_": "tests.fixtures.Service",
                    "name": "data_service",
                    "config": {"batch_size": 100, "retry_count": 3},
                },
            ],
            "database": {
                "_target_": "frostbound.pydanticonf.DynamicConfig",
                "target_": "tests.fixtures.Database",
                "connection_string": "postgresql://localhost/test",
                "pool_config": {
                    "_target_": "frostbound.pydanticonf.DynamicConfig",
                    "target_": "tests.fixtures.PoolConfig",
                    "min_connections": 5,
                    "max_connections": 20,
                },
            },
        }
    }


@pytest.fixture
def assert_configs_equal():
    """Fixture providing a helper function for deep config comparison.

    Returns
    -------
    callable
        Function that compares two config objects/dicts recursively.
    """

    def _assert_equal(actual: Any, expected: Any, path: str = "") -> None:
        """Assert deep equality of configuration objects.

        Parameters
        ----------
        actual : Any
            The actual configuration value.
        expected : Any
            The expected configuration value.
        path : str
            Current path in the configuration tree (for error messages).
        """
        if isinstance(expected, dict):
            assert isinstance(actual, dict), f"At {path}: expected dict, got {type(actual)}"
            assert set(actual.keys()) == set(expected.keys()), (
                f"At {path}: keys mismatch. Actual: {set(actual.keys())}, Expected: {set(expected.keys())}"
            )

            for key in expected:
                _assert_equal(actual[key], expected[key], f"{path}.{key}" if path else key)

        elif isinstance(expected, list):
            assert isinstance(actual, list), f"At {path}: expected list, got {type(actual)}"
            assert len(actual) == len(expected), (
                f"At {path}: list length mismatch. Actual: {len(actual)}, Expected: {len(expected)}"
            )

            for i, (actual_item, expected_item) in enumerate(zip(actual, expected, strict=False)):
                _assert_equal(actual_item, expected_item, f"{path}[{i}]")

        else:
            assert actual == expected, f"At {path}: {actual} != {expected}"

    return _assert_equal


@pytest.fixture(scope="session")
def test_module_path() -> Path:
    """Path to the test fixtures module directory.

    Returns
    -------
    Path
        Path to the integration test fixtures directory.
    """
    return Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def add_test_fixtures_to_path(test_module_path: Path) -> Generator[None]:
    """Add test fixtures directory to Python path for dynamic imports.

    Parameters
    ----------
    test_module_path : Path
        Path to the test fixtures directory.

    Yields
    ------
    None
        Control flow returns to test execution.
    """

    str_path = str(test_module_path.parent)  # Add parent of fixtures dir
    if str_path not in sys.path:
        sys.path.insert(0, str_path)

    yield

    if str_path in sys.path:
        sys.path.remove(str_path)
