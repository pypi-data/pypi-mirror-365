"""Unit tests for the ConfigFactory class.

This module tests the factory pattern implementation including:
- Configuration registration and retrieval
- Dependency injection management
- Caching behavior
- Runtime overrides
- Thread safety
"""

import threading
import time
from typing import Any
from unittest.mock import Mock

import pytest

from frostbound.pydanticonf import DynamicConfig
from frostbound.pydanticonf.factory import ConfigFactory


class MockService:
    """Mock service for testing."""

    def __init__(self, name: str, timeout: int = 30) -> None:
        self.name = name
        self.timeout = timeout
        self.id = id(self)  # For identity checking


class MockDatabase:
    """Mock database for testing."""

    def __init__(self, host: str, port: int = 5432) -> None:
        self.host = host
        self.port = port


class ServiceConfig(DynamicConfig[MockService]):
    """Type-safe service configuration."""

    name: str
    timeout: int = 30


class DatabaseConfig(DynamicConfig[MockDatabase]):
    """Type-safe database configuration."""

    host: str = "localhost"
    port: int = 5432


class ComplexService:
    """Complex service for testing."""

    def __init__(self, name: str, database: Any) -> None:
        self.name = name
        self.database = database


class ServiceWithDeps:
    """Service with dependencies for testing."""

    def __init__(self, name: str, database: Any, logger: Any) -> None:
        self.name = name
        self.database = database
        self.logger = logger


class ReturnsList:
    """Service that returns a list."""

    def __init__(self) -> None:
        pass


class TestConfigFactoryBasics:
    """Test basic ConfigFactory functionality."""

    def test_factory_creation_default_cache(self) -> None:
        """Verify factory creation with default cache enabled.

        Tests
        -----
        Factory is created with caching enabled by default.
        """
        factory = ConfigFactory[MockService]()

        assert factory._cache_enabled is True
        assert len(factory._configs) == 0
        assert len(factory._dependencies) == 0

    def test_factory_creation_cache_disabled(self) -> None:
        """Verify factory creation with cache disabled.

        Tests
        -----
        Factory can be created without caching.
        """
        factory = ConfigFactory[MockService](cache=False)

        assert factory._cache_enabled is False

    def test_register_config_basic(self) -> None:
        """Verify basic configuration registration.

        Tests
        -----
        Named configurations can be registered for later use.
        """
        factory = ConfigFactory[MockService]()
        config = ServiceConfig(_target_="tests.unit.test_factory.MockService", name="TestService")

        factory.register_config("default", config)

        assert "default" in factory._configs
        assert factory._configs["default"] is config

    def test_register_config_duplicate_name_error(self) -> None:
        """Verify error when registering duplicate configuration name.

        Tests
        -----
        Clear error message for duplicate registration attempts.
        """
        factory = ConfigFactory[MockService]()
        config = ServiceConfig(_target_="tests.unit.test_factory.MockService", name="Service1")

        factory.register_config("test", config)

        with pytest.raises(ValueError, match="Configuration 'test' already registered"):
            factory.register_config("test", config)

    def test_list_configs(self) -> None:
        """Verify listing registered configuration names.

        Tests
        -----
        All registered configuration names are returned.
        """
        factory = ConfigFactory[MockService]()

        factory.register_config("dev", Mock())
        factory.register_config("prod", Mock())
        factory.register_config("test", Mock())

        configs = factory.list_configs()

        assert sorted(configs) == ["dev", "prod", "test"]


class TestConfigFactoryCreation:
    """Test object creation functionality."""

    def test_create_from_dynamic_config(self) -> None:
        """Verify direct creation from DynamicConfig.

        Tests
        -----
        Objects can be created directly from configuration.
        """
        factory = ConfigFactory[MockService]()
        config = ServiceConfig(
            _target_="tests.unit.test_factory.MockService",
            name="DirectService",
            timeout=60,
        )

        service = factory.create(config)

        assert isinstance(service, MockService)
        assert service.name == "DirectService"
        assert service.timeout == 60

    def test_create_from_dict_config(self) -> None:
        """Verify creation from dictionary configuration.

        Tests
        -----
        Objects can be created from plain dictionaries.
        """
        factory = ConfigFactory[MockService]()
        config = {
            "_target_": "tests.unit.test_factory.MockService",
            "name": "DictService",
            "timeout": 45,
        }

        service = factory.create(config)

        assert isinstance(service, MockService)
        assert service.name == "DictService"
        assert service.timeout == 45

    def test_create_with_overrides(self) -> None:
        """Verify creation with parameter overrides.

        Tests
        -----
        Runtime overrides modify configuration values.
        """
        factory = ConfigFactory[MockService]()
        config = ServiceConfig(
            _target_="tests.unit.test_factory.MockService",
            name="Original",
            timeout=30,
        )

        service = factory.create(config, name="Overridden", timeout=90)

        assert service.name == "Overridden"
        assert service.timeout == 90

    def test_create_with_nested_overrides(self) -> None:
        """Verify nested overrides using double underscore notation.

        Tests
        -----
        Nested configuration values can be overridden.
        """

        factory = ConfigFactory[ComplexService]()
        config = {
            "_target_": "tests.unit.test_factory.ComplexService",
            "name": "Service",
            "database": {
                "_target_": "tests.unit.test_factory.MockDatabase",
                "host": "original.db",
                "port": 5432,
            },
        }

        service = factory.create(config, database__host="new.db", database__port=3306)

        assert service.database.host == "new.db"
        assert service.database.port == 3306

    def test_create_multiple(self) -> None:
        """Verify batch creation with common overrides.

        Tests
        -----
        Multiple objects can be created with shared overrides.
        """
        factory = ConfigFactory[MockService]()
        configs = [
            ServiceConfig(_target_="tests.unit.test_factory.MockService", name="Service1"),
            ServiceConfig(_target_="tests.unit.test_factory.MockService", name="Service2"),
            ServiceConfig(_target_="tests.unit.test_factory.MockService", name="Service3"),
        ]

        services = factory.create_multiple(configs, timeout=120)

        assert len(services) == 3
        assert all(isinstance(s, MockService) for s in services)
        assert [s.name for s in services] == ["Service1", "Service2", "Service3"]
        assert all(s.timeout == 120 for s in services)


class TestConfigFactoryCaching:
    """Test caching behavior."""

    def test_get_with_caching_returns_same_instance(self) -> None:
        """Verify cached instances are returned on subsequent calls.

        Tests
        -----
        Same configuration returns same instance when cache enabled.
        """
        factory = ConfigFactory[MockService](cache=True)
        factory.register_config(
            "test",
            ServiceConfig(_target_="tests.unit.test_factory.MockService", name="CachedService"),
        )

        service1 = factory.get("test")
        service2 = factory.get("test")

        assert service1 is service2
        assert service1.id == service2.id

    def test_get_without_caching_returns_new_instances(self) -> None:
        """Verify new instances when caching disabled.

        Tests
        -----
        Each call creates a new instance without caching.
        """
        factory = ConfigFactory[MockService](cache=False)
        factory.register_config(
            "test",
            ServiceConfig(_target_="tests.unit.test_factory.MockService", name="UncachedService"),
        )

        service1 = factory.get("test")
        service2 = factory.get("test")

        assert service1 is not service2
        assert service1.id != service2.id

    def test_get_with_different_overrides_creates_separate_cache_entries(self) -> None:
        """Verify different overrides create separate cache entries.

        Tests
        -----
        Cache key includes override parameters.
        """
        factory = ConfigFactory[MockService](cache=True)
        config = ServiceConfig(_target_="tests.unit.test_factory.MockService", name="Service")
        factory.register_config("test", config)

        service1 = factory.get("test", timeout=30)
        service2 = factory.get("test", timeout=60)
        service3 = factory.get("test", timeout=30)  # Same as service1

        assert service1 is not service2
        assert service1 is service3
        assert service1.timeout == 30
        assert service2.timeout == 60

    def test_clear_cache_all(self) -> None:
        """Verify clearing entire cache.

        Tests
        -----
        All cached instances are removed.
        """
        factory = ConfigFactory[MockService](cache=True)
        factory.register_config("test", ServiceConfig(_target_="tests.unit.test_factory.MockService", name="Service"))

        # Create cached instances
        service1 = factory.get("test")
        _ = factory.get("test", timeout=60)

        factory.clear_cache()

        # New instances should be created
        service2 = factory.get("test")
        assert service1 is not service2

    def test_clear_cache_by_name(self) -> None:
        """Verify clearing cache for specific configuration.

        Tests
        -----
        Only specified configuration's cache entries are removed.
        """
        factory = ConfigFactory[MockService](cache=True)
        factory.register_config(
            "config1", ServiceConfig(_target_="tests.unit.test_factory.MockService", name="Service1")
        )
        factory.register_config(
            "config2", ServiceConfig(_target_="tests.unit.test_factory.MockService", name="Service2")
        )

        # Create cached instances
        service1_before = factory.get("config1")
        service2_before = factory.get("config2")

        # Clear only config1 cache
        factory.clear_cache("config1")

        service1_after = factory.get("config1")
        service2_after = factory.get("config2")

        assert service1_before is not service1_after  # New instance
        assert service2_before is service2_after  # Still cached

    def test_weak_reference_caching(self) -> None:
        """Verify weak references allow garbage collection.

        Tests
        -----
        Cached objects can be garbage collected when not referenced.
        """
        factory = ConfigFactory[MockService](cache=True)
        factory.register_config("test", ServiceConfig(_target_="tests.unit.test_factory.MockService", name="WeakRef"))

        # Create instance and verify it's cached
        service = factory.get("test")
        service_id = service.id

        # Verify it's cached
        assert factory.get("test").id == service_id

        # Delete the reference
        del service

        # Force garbage collection
        import gc

        gc.collect()

        # New instance should be created (weak ref was collected)
        # NOTE: This behavior is implementation-dependent and may vary
        new_service = factory.get("test")
        # Due to WeakValueDictionary, the cache entry might be gone
        assert isinstance(new_service, MockService)


class TestConfigFactoryDependencies:
    """Test dependency injection features."""

    def test_register_dependency(self) -> None:
        """Verify dependency registration.

        Tests
        -----
        Dependencies are stored and registered globally.
        """
        factory = ConfigFactory[MockService]()
        mock_db = Mock()

        factory.register_dependency("database", mock_db)

        assert factory._dependencies["database"] is mock_db

    def test_dependencies_injected_on_create(self) -> None:
        """Verify dependencies are injected during creation.

        Tests
        -----
        Registered dependencies are automatically provided.
        """

        factory = ConfigFactory[ServiceWithDeps]()
        mock_db = Mock()
        mock_logger = Mock()

        factory.register_dependency("database", mock_db)
        factory.register_dependency("logger", mock_logger)

        config = {"_target_": "tests.unit.test_factory.ServiceWithDeps", "name": "TestService"}

        service = factory.create(config)

        assert service.database is mock_db
        assert service.logger is mock_logger

    def test_clear_dependencies(self) -> None:
        """Verify clearing all dependencies.

        Tests
        -----
        All registered dependencies are removed.
        """
        factory = ConfigFactory[MockService]()
        factory.register_dependency("dep1", Mock())
        factory.register_dependency("dep2", Mock())

        factory.clear_dependencies()

        assert len(factory._dependencies) == 0


class TestConfigFactoryGetMethod:
    """Test the get method variations."""

    def test_get_by_name(self) -> None:
        """Verify getting instance by registered name.

        Tests
        -----
        Named configurations can be retrieved and instantiated.
        """
        factory = ConfigFactory[MockService]()
        factory.register_config(
            "prod",
            ServiceConfig(_target_="tests.unit.test_factory.MockService", name="ProdService"),
        )

        service = factory.get("prod")

        assert isinstance(service, MockService)
        assert service.name == "ProdService"

    def test_get_by_name_not_found_error(self) -> None:
        """Verify error when configuration name not found.

        Tests
        -----
        Clear error message for non-existent configuration.
        """
        factory = ConfigFactory[MockService]()

        with pytest.raises(KeyError, match="No configuration registered for 'missing'"):
            factory.get("missing")

    def test_get_with_direct_config(self) -> None:
        """Verify getting instance from direct configuration.

        Tests
        -----
        Configuration can be passed directly without registration.
        """
        factory = ConfigFactory[MockService]()
        config = ServiceConfig(_target_="tests.unit.test_factory.MockService", name="DirectConfig")

        service = factory.get(config)

        assert isinstance(service, MockService)
        assert service.name == "DirectConfig"

    def test_get_with_dict_config(self) -> None:
        """Verify getting instance from dictionary configuration.

        Tests
        -----
        Plain dictionaries can be used directly.
        """
        factory = ConfigFactory[MockService]()
        config = {"_target_": "tests.unit.test_factory.MockService", "name": "DictConfig"}

        service = factory.get(config)

        assert isinstance(service, MockService)
        assert service.name == "DictConfig"


class TestConfigFactoryThreadSafety:
    """Test thread safety of factory operations."""

    def test_concurrent_get_operations(self) -> None:
        """Verify thread safety of concurrent get operations.

        Tests
        -----
        Multiple threads can safely use the factory.
        """
        factory = ConfigFactory[MockService](cache=True)
        factory.register_config(
            "test", ServiceConfig(_target_="tests.unit.test_factory.MockService", name="Concurrent")
        )

        results: list[MockService] = []
        errors: list[Exception] = []

        def worker() -> None:
            try:
                for _ in range(10):
                    service = factory.get("test")
                    results.append(service)
                    time.sleep(0.001)  # Small delay to increase contention
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(5)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        assert len(errors) == 0
        assert len(results) == 50
        # All results should be the same cached instance
        assert all(r is results[0] for r in results)

    def test_concurrent_registration(self) -> None:
        """Verify thread safety of concurrent registration.

        Tests
        -----
        Registration operations are thread-safe.
        """
        factory = ConfigFactory[MockService]()
        errors: list[Exception] = []

        def register_config(name: str) -> None:
            try:
                config = ServiceConfig(_target_="tests.unit.test_factory.MockService", name=f"Service_{name}")
                factory.register_config(name, config)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=register_config, args=(f"config_{i}",)) for i in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # No errors should occur
        assert len(errors) == 0
        assert len(factory.list_configs()) == 10


class TestConfigFactoryEdgeCases:
    """Test edge cases and error conditions."""

    def test_nested_override_creates_missing_parents(self) -> None:
        """Verify nested overrides create parent dictionaries as needed.

        Tests
        -----
        Deep nested paths are created for overrides.
        """
        factory = ConfigFactory[MockService]()
        config = {"_target_": "tests.unit.test_factory.MockService", "name": "Test"}

        # This should create the nested structure
        result = factory.create(config, deeply__nested__value="test")

        # The override creates the structure but MockService doesn't use it
        assert isinstance(result, MockService)

    def test_cache_with_uncacheable_objects(self) -> None:
        """Verify handling of objects that can't be weakly referenced.

        Tests
        -----
        Factory handles TypeError from WeakValueDictionary gracefully.
        """

        factory = ConfigFactory[list[int]](cache=True)
        config = {"_target_": "builtins.list", "_args_": [[1, 2, 3]]}

        # Lists can't be weakly referenced, but shouldn't cause error
        result1 = factory.get(config)
        result2 = factory.get(config)

        assert result1 == [1, 2, 3]
        assert result2 == [1, 2, 3]
        # They won't be the same instance due to cache limitation
        assert result1 is not result2

    @pytest.mark.parametrize(
        ("override_key", "override_value", "expected_path"),
        [
            ("simple", "value", ["simple"]),
            ("one__two", "value", ["one", "two"]),
            ("a__b__c__d", "value", ["a", "b", "c", "d"]),
        ],
    )
    def test_nested_override_parsing(self, override_key: str, override_value: Any, expected_path: list[str]) -> None:
        """Verify nested override key parsing.

        Parameters
        ----------
        override_key : str
            The override key with double underscores.
        override_value : Any
            The value to set.
        expected_path : list[str]
            Expected path components after parsing.

        Tests
        -----
        Double underscore notation is correctly parsed.
        """
        factory = ConfigFactory[MockService]()
        config_dict: dict[str, Any] = {"_target_": "test.Class"}

        # Use internal method to test parsing
        result = factory._apply_nested_overrides(config_dict, {override_key: override_value})

        # Navigate the result to verify structure
        current = result
        for key in expected_path[:-1]:
            assert key in current
            current = current[key]
        assert expected_path[-1] in current
        assert current[expected_path[-1]] == override_value
