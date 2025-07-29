"""Integration tests for complex instantiation scenarios.

This module tests advanced instantiation patterns including
deeply nested objects, circular references, and mixed
configuration types.
"""

from typing import Any

import pytest

from frostbound.pydanticonf import (
    BaseSettingsWithInstantiation,
    DynamicConfig,
    instantiate,
)
from frostbound.pydanticonf._instantiate import InstantiationError


class Database:
    """Mock database class."""

    def __init__(self, host: str, port: int = 5432, pool: Any = None) -> None:
        self.host = host
        self.port = port
        self.pool = pool


class ConnectionPool:
    """Mock connection pool."""

    def __init__(self, min_size: int = 5, max_size: int = 20, timeout: float = 30.0) -> None:
        self.min_size = min_size
        self.max_size = max_size
        self.timeout = timeout


class Cache:
    """Mock cache class."""

    def __init__(self, backend: str = "memory", ttl: int = 3600, servers: list[Any] = None) -> None:
        self.backend = backend
        self.ttl = ttl
        self.servers = servers or []


class CacheServer:
    """Mock cache server."""

    def __init__(self, host: str, port: int = 6379, weight: int = 1) -> None:
        self.host = host
        self.port = port
        self.weight = weight


class Service:
    """Mock service with dependencies."""

    def __init__(
        self,
        name: str,
        database: Any = None,
        cache: Any = None,
        plugins: list[Any] = None,
        config: dict[str, Any] = None,
    ) -> None:
        self.name = name
        self.database = database
        self.cache = cache
        self.plugins = plugins or []
        self.config = config or {}


class Plugin:
    """Mock plugin class."""

    def __init__(self, name: str, version: str = "1.0.0", **options: Any) -> None:
        self.name = name
        self.version = version
        self.options = options


class ConditionalService:
    """Service with conditional dependencies."""

    def __init__(self, name: str, primary_db: Any, secondary_db: Any = None, cache: Any = None) -> None:
        self.name = name
        self.primary_db = primary_db
        self.secondary_db = secondary_db
        self.cache = cache


class NetworkService:
    """Service with network endpoints."""

    def __init__(self, name: str, endpoints: list[str], timeout: int = 30) -> None:
        self.name = name
        self.endpoints = endpoints
        self.timeout = timeout


class FailingComponent:
    """Component that fails during initialization."""

    def __init__(self) -> None:
        raise ValueError("Component initialization failed")


@pytest.mark.integration
class TestComplexInstantiation:
    """Test complex instantiation scenarios."""

    def test_deeply_nested_instantiation(self) -> None:
        """Verify instantiation of deeply nested object hierarchies."""
        config = {
            "_target_": "tests.integration.test_complex_instantiation.Service",
            "name": "MainService",
            "database": {
                "_target_": "tests.integration.test_complex_instantiation.Database",
                "host": "db.server",
                "port": 5432,
                "pool": {
                    "_target_": "tests.integration.test_complex_instantiation.ConnectionPool",
                    "min_size": 10,
                    "max_size": 50,
                    "timeout": 60.0,
                },
            },
            "cache": {
                "_target_": "tests.integration.test_complex_instantiation.Cache",
                "backend": "redis",
                "ttl": 7200,
                "servers": [
                    {
                        "_target_": "tests.integration.test_complex_instantiation.CacheServer",
                        "host": "cache1.server",
                        "port": 6379,
                        "weight": 2,
                    },
                    {
                        "_target_": "tests.integration.test_complex_instantiation.CacheServer",
                        "host": "cache2.server",
                        "port": 6380,
                        "weight": 1,
                    },
                ],
            },
        }

        service = instantiate(config)

        # Verify structure
        assert isinstance(service, Service)
        assert service.name == "MainService"

        # Database with pool
        assert isinstance(service.database, Database)
        assert service.database.host == "db.server"
        assert isinstance(service.database.pool, ConnectionPool)
        assert service.database.pool.min_size == 10
        assert service.database.pool.max_size == 50

        # Cache with servers
        assert isinstance(service.cache, Cache)
        assert service.cache.backend == "redis"
        assert len(service.cache.servers) == 2
        assert all(isinstance(s, CacheServer) for s in service.cache.servers)
        assert service.cache.servers[0].host == "cache1.server"
        assert service.cache.servers[0].weight == 2

    def test_mixed_config_types(self) -> None:
        """Verify mixing DynamicConfig, dict, and regular values."""

        class DatabaseConfig(DynamicConfig[Database]):
            host: str = "localhost"
            port: int = 5432

        class Settings(BaseSettingsWithInstantiation):
            auto_instantiate = True

            # DynamicConfig instance
            primary_db: Any = DatabaseConfig(
                _target_="tests.integration.test_complex_instantiation.Database",
                host="primary.db",
            )

            # Dict with _target_
            secondary_db: Any = {
                "_target_": "tests.integration.test_complex_instantiation.Database",
                "host": "secondary.db",
                "port": 5433,
            }

            # Nested in list
            databases: list[Any] = [
                DatabaseConfig(
                    _target_="tests.integration.test_complex_instantiation.Database",
                    host="list.db1",
                ),
                {
                    "_target_": "tests.integration.test_complex_instantiation.Database",
                    "host": "list.db2",
                },
            ]

            # Regular values
            app_name: str = "TestApp"
            debug: bool = True

        settings = Settings()

        # All should be instantiated
        assert isinstance(settings.primary_db, Database)
        assert settings.primary_db.host == "primary.db"

        assert isinstance(settings.secondary_db, Database)
        assert settings.secondary_db.host == "secondary.db"

        assert len(settings.databases) == 2
        assert all(isinstance(db, Database) for db in settings.databases)
        assert settings.databases[0].host == "list.db1"
        assert settings.databases[1].host == "list.db2"

        # Regular fields unchanged
        assert settings.app_name == "TestApp"
        assert settings.debug is True

    def test_plugin_system_pattern(self) -> None:
        """Verify plugin system instantiation pattern."""
        config = {
            "_target_": "tests.integration.test_complex_instantiation.Service",
            "name": "PluginService",
            "plugins": [
                {
                    "_target_": "tests.integration.test_complex_instantiation.Plugin",
                    "name": "AuthPlugin",
                    "version": "2.0.0",
                    "secret_key": "auth-secret",
                    "token_expiry": 3600,
                },
                {
                    "_target_": "tests.integration.test_complex_instantiation.Plugin",
                    "name": "CachePlugin",
                    "version": "1.5.0",
                    "cache_backend": "redis",
                    "max_entries": 10000,
                },
                {
                    "_target_": "tests.integration.test_complex_instantiation.Plugin",
                    "name": "LogPlugin",
                    "level": "INFO",
                    "format": "json",
                },
            ],
        }

        service = instantiate(config)

        assert len(service.plugins) == 3
        assert all(isinstance(p, Plugin) for p in service.plugins)

        # Check plugin configurations
        auth_plugin = service.plugins[0]
        assert auth_plugin.name == "AuthPlugin"
        assert auth_plugin.version == "2.0.0"
        assert auth_plugin.options["secret_key"] == "auth-secret"
        assert auth_plugin.options["token_expiry"] == 3600

        cache_plugin = service.plugins[1]
        assert cache_plugin.options["cache_backend"] == "redis"
        assert cache_plugin.options["max_entries"] == 10000

    def test_conditional_instantiation(self) -> None:
        """Verify conditional instantiation based on configuration."""

        # Configuration with optional components
        config_with_all = {
            "_target_": "tests.integration.test_complex_instantiation.ConditionalService",
            "name": "FullService",
            "primary_db": {
                "_target_": "tests.integration.test_complex_instantiation.Database",
                "host": "primary.db",
            },
            "secondary_db": {
                "_target_": "tests.integration.test_complex_instantiation.Database",
                "host": "secondary.db",
            },
            "cache": {
                "_target_": "tests.integration.test_complex_instantiation.Cache",
                "backend": "redis",
            },
        }

        service_full = instantiate(config_with_all)
        assert service_full.primary_db is not None
        assert service_full.secondary_db is not None
        assert service_full.cache is not None

        # Configuration with minimal components
        config_minimal = {
            "_target_": "tests.integration.test_complex_instantiation.ConditionalService",
            "name": "MinimalService",
            "primary_db": {
                "_target_": "tests.integration.test_complex_instantiation.Database",
                "host": "primary.db",
            },
        }

        service_minimal = instantiate(config_minimal)
        assert service_minimal.primary_db is not None
        assert service_minimal.secondary_db is None
        assert service_minimal.cache is None

    def test_recursive_config_references(self) -> None:
        """Verify handling of configuration references."""

        # Shared configuration values
        shared_config = {
            "default_timeout": 60,
            "endpoints": {
                "primary": ["http://api1.example.com", "http://api2.example.com"],
                "secondary": ["http://backup1.example.com", "http://backup2.example.com"],
            },
        }

        # Service configurations referencing shared values
        config = {
            "_target_": "tests.integration.test_complex_instantiation.Service",
            "name": "MainService",
            "config": shared_config,
            "plugins": [
                {
                    "_target_": "tests.integration.test_complex_instantiation.NetworkService",
                    "name": "PrimaryAPI",
                    "endpoints": shared_config["endpoints"]["primary"],
                    "timeout": shared_config["default_timeout"],
                },
                {
                    "_target_": "tests.integration.test_complex_instantiation.NetworkService",
                    "name": "SecondaryAPI",
                    "endpoints": shared_config["endpoints"]["secondary"],
                    "timeout": shared_config["default_timeout"],
                },
            ],
        }

        service = instantiate(config)

        assert len(service.plugins) == 2
        assert service.plugins[0].endpoints == ["http://api1.example.com", "http://api2.example.com"]
        assert service.plugins[1].endpoints == ["http://backup1.example.com", "http://backup2.example.com"]
        assert all(p.timeout == 60 for p in service.plugins)

    def test_error_propagation_in_nested_instantiation(self) -> None:
        """Verify error handling in deeply nested instantiation."""

        config = {
            "_target_": "tests.integration.test_complex_instantiation.Service",
            "name": "ServiceWithError",
            "database": {
                "_target_": "tests.integration.test_complex_instantiation.Database",
                "host": "db.server",
                "pool": {"_target_": "tests.integration.test_complex_instantiation.FailingComponent"},
            },
        }

        with pytest.raises(InstantiationError) as exc_info:
            instantiate(config)

        assert "Component initialization failed" in str(exc_info.value)
        # Error should include context about where it occurred
        assert "pool" in str(exc_info.value) or "database" in str(exc_info.value)

    def test_large_scale_instantiation(self) -> None:
        """Verify performance with large configuration structures."""
        # Create a large configuration with many nested objects
        num_services = 50
        num_plugins_per_service = 5

        services = []
        for i in range(num_services):
            plugins = [
                {
                    "_target_": "tests.integration.test_complex_instantiation.Plugin",
                    "name": f"Plugin_{i}_{j}",
                    "config_value": f"value_{i}_{j}",
                }
                for j in range(num_plugins_per_service)
            ]

            services.append(
                {
                    "_target_": "tests.integration.test_complex_instantiation.Service",
                    "name": f"Service_{i}",
                    "plugins": plugins,
                    "database": {
                        "_target_": "tests.integration.test_complex_instantiation.Database",
                        "host": f"db{i}.server",
                    },
                }
            )

        # Instantiate all services
        instantiated_services = [instantiate(config) for config in services]

        assert len(instantiated_services) == num_services
        assert all(isinstance(s, Service) for s in instantiated_services)
        assert all(len(s.plugins) == num_plugins_per_service for s in instantiated_services)

        # Verify some specific instances
        assert instantiated_services[0].name == "Service_0"
        assert instantiated_services[0].plugins[0].name == "Plugin_0_0"
        assert instantiated_services[-1].database.host == f"db{num_services - 1}.server"

    @pytest.mark.parametrize(
        ("recursive_flag", "expected_type"),
        [
            (True, Database),  # With recursion, nested configs are instantiated
            (False, dict),  # Without recursion, nested configs remain as dicts
        ],
    )
    def test_recursive_flag_behavior(self, recursive_flag: bool, expected_type: type[Any]) -> None:
        """Verify _recursive_ flag controls nested instantiation.

        Parameters
        ----------
        recursive_flag : bool
            Value for _recursive_ flag.
        expected_type : type[Any]
            Expected type of nested object.
        """
        config = {
            "_target_": "tests.integration.test_complex_instantiation.Service",
            "_recursive_": recursive_flag,
            "name": "TestService",
            "database": {
                "_target_": "tests.integration.test_complex_instantiation.Database",
                "host": "test.db",
            },
        }

        service = instantiate(config)

        assert isinstance(service, Service)
        assert isinstance(service.database, expected_type)

        if isinstance(service.database, dict):
            # Verify dict structure is preserved
            assert service.database["_target_"] == "tests.integration.test_complex_instantiation.Database"
            assert service.database["host"] == "test.db"
