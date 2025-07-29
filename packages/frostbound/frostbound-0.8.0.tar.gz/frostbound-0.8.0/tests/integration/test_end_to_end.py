"""End-to-end integration tests for pydanticonf.

This module tests complete workflows from YAML configuration
to instantiated objects, including all features working together.
"""

import logging
from typing import Any

import pytest
from pydantic_settings import SettingsConfigDict

from frostbound.pydanticonf import (
    BaseSettingsWithInstantiation,
    ConfigFactory,
    DynamicConfig,
    instantiate,
    register_dependency,
)


# Application classes for testing
class Database:
    """Database connection class."""

    def __init__(
        self, host: str, port: int = 5432, username: str = "user", password: str = "pass", pool_size: int = 10
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.pool_size = pool_size
        self.connected = False

    def connect(self) -> None:
        self.connected = True
        logging.info(f"Connected to {self.host}:{self.port}")


class CacheBackend:
    """Cache backend implementation."""

    def __init__(self, host: str = "localhost", port: int = 6379, ttl: int = 3600, prefix: str = "app") -> None:
        self.host = host
        self.port = port
        self.ttl = ttl
        self.prefix = prefix
        self.data: dict[str, Any] = {}

    def get(self, key: str) -> Any:
        return self.data.get(f"{self.prefix}:{key}")

    def set(self, key: str, value: Any) -> None:
        self.data[f"{self.prefix}:{key}"] = value


class MessageQueue:
    """Message queue service."""

    def __init__(self, broker_url: str, exchange: str = "default", routing_key: str = "messages") -> None:
        self.broker_url = broker_url
        self.exchange = exchange
        self.routing_key = routing_key
        self.messages: list[Any] = []

    def publish(self, message: Any) -> None:
        self.messages.append(message)


class APIClient:
    """External API client."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 30, retry_count: int = 3) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.retry_count = retry_count


class Application:
    """Main application class."""

    def __init__(
        self,
        name: str,
        version: str,
        database: Database,
        cache: CacheBackend,
        message_queue: MessageQueue | None = None,
        api_clients: dict[str, APIClient] | None = None,
        features: dict[str, bool] | None = None,
    ) -> None:
        self.name = name
        self.version = version
        self.database = database
        self.cache = cache
        self.message_queue = message_queue
        self.api_clients = api_clients or {}
        self.features = features or {}
        self.logger = logging.getLogger(name)

    def start(self) -> None:
        self.database.connect()
        self.logger.info(f"Started {self.name} v{self.version}")


class DataService:
    """Data service with dependencies."""

    def __init__(
        self,
        name: str,
        shared_db: Database,
        shared_cache: CacheBackend,
        logger: logging.Logger,
        batch_size: int = 100,
    ) -> None:
        self.name = name
        self.db = shared_db
        self.cache = shared_cache
        self.logger = logger
        self.batch_size = batch_size


class FailingService:
    """Service that can fail during initialization."""

    def __init__(self, fail_on_init: bool = False) -> None:
        if fail_on_init:
            raise ValueError("Service initialization failed")
        self.initialized = True


class ResilientApp:
    """Application with resilient service handling."""

    def __init__(
        self,
        name: str,
        primary_service: Any,
        fallback_service: Any = None,
    ) -> None:
        self.name = name
        self.primary_service = primary_service
        self.fallback_service = fallback_service


@pytest.mark.integration
class TestEndToEnd:
    """End-to-end integration tests."""

    def test_complete_application_setup(self, create_yaml_file: Any, env_vars: dict[str, str]) -> None:
        """Test complete application setup from YAML with env overrides.

        Parameters
        ----------
        create_yaml_file : callable
            Fixture to create YAML files.
        env_vars : dict[str, str]
            Environment variable fixture.
        """
        # Create base configuration
        base_config = {
            "name": "MyApp",
            "version": "1.0.0",
            "database": {
                "_target_": "tests.integration.test_end_to_end.Database",
                "host": "localhost",
                "port": 5432,
                "username": "appuser",
                "password": "apppass",
                "pool_size": 20,
            },
            "cache": {
                "_target_": "tests.integration.test_end_to_end.CacheBackend",
                "host": "localhost",
                "port": 6379,
                "ttl": 3600,
                "prefix": "myapp",
            },
            "message_queue": {
                "_target_": "tests.integration.test_end_to_end.MessageQueue",
                "broker_url": "amqp://localhost",
                "exchange": "myapp",
            },
            "api_clients": {
                "payment": {
                    "_target_": "tests.integration.test_end_to_end.APIClient",
                    "base_url": "https://payment.api.com",
                    "api_key": "payment-key",
                    "timeout": 60,
                },
                "notification": {
                    "_target_": "tests.integration.test_end_to_end.APIClient",
                    "base_url": "https://notify.api.com",
                    "api_key": "notify-key",
                    "retry_count": 5,
                },
            },
            "features": {"auth": True, "api": True, "admin": False},
        }

        # Create environment-specific override
        prod_config = {
            "database": {"host": "prod.db.server", "port": 3306},
            "cache": {"host": "prod.cache.server", "ttl": 7200},
            "features": {"admin": True, "monitoring": True},
        }

        base_path = create_yaml_file(base_config, "base.yaml")
        prod_path = create_yaml_file(prod_config, "prod.yaml")

        # Set environment variables
        env_vars["APP_NAME"] = "MyAppProd"
        env_vars["APP_DATABASE__PASSWORD"] = "prod-secret-pass"
        env_vars["APP_API_CLIENTS__PAYMENT__API_KEY"] = "prod-payment-key"

        # Define settings class
        class AppSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(
                yaml_file=[str(base_path), str(prod_path)],
                env_prefix="APP_",
                env_nested_delimiter="__",
            )
            auto_instantiate = False  # We'll instantiate manually

            name: str
            version: str
            database: Any
            cache: Any
            message_queue: Any
            api_clients: dict[str, Any]
            features: dict[str, bool]

        # Load settings
        settings = AppSettings()

        # Manually instantiate for controlled testing
        app_config = {
            "_target_": "tests.integration.test_end_to_end.Application",
            "name": settings.name,
            "version": settings.version,
            "database": settings.database,
            "cache": settings.cache,
            "message_queue": settings.message_queue,
            "api_clients": settings.api_clients,
            "features": settings.features,
        }

        app = instantiate(app_config)

        # Verify complete setup
        assert isinstance(app, Application)
        assert app.name == "MyAppProd"  # From env var
        assert app.version == "1.0.0"

        # Database merged from files and env
        assert app.database.host == "prod.db.server"  # From prod.yaml
        assert app.database.port == 3306  # From prod.yaml
        assert app.database.password == "prod-secret-pass"  # From env var
        assert app.database.pool_size == 20  # From base.yaml

        # Cache configuration
        assert app.cache.host == "prod.cache.server"
        assert app.cache.ttl == 7200

        # API clients with env override
        assert app.api_clients["payment"].api_key == "prod-payment-key"
        assert app.api_clients["notification"].retry_count == 5

        # Features merged
        assert app.features == {
            "auth": True,
            "api": True,
            "admin": True,
            "monitoring": True,
        }

        # Test application startup
        app.start()
        assert app.database.connected

    def test_factory_pattern_workflow(self, create_yaml_file: Any) -> None:
        """Test ConfigFactory pattern for managing configurations.

        Parameters
        ----------
        create_yaml_file : callable
            Fixture to create YAML files.
        """
        # Create configuration file
        config_content = {
            "databases": {
                "primary": {
                    "_target_": "tests.integration.test_end_to_end.Database",
                    "host": "primary.db",
                    "port": 5432,
                },
                "replica": {
                    "_target_": "tests.integration.test_end_to_end.Database",
                    "host": "replica.db",
                    "port": 5433,
                },
            },
            "caches": {
                "session": {
                    "_target_": "tests.integration.test_end_to_end.CacheBackend",
                    "prefix": "session",
                    "ttl": 1800,
                },
                "api": {
                    "_target_": "tests.integration.test_end_to_end.CacheBackend",
                    "prefix": "api",
                    "ttl": 300,
                },
            },
        }

        config_path = create_yaml_file(config_content)

        class InfrastructureSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(yaml_file=str(config_path))
            auto_instantiate = False

            databases: dict[str, Any]
            caches: dict[str, Any]

        # Load settings
        settings = InfrastructureSettings()

        # Create factories for different resource types
        db_factory = ConfigFactory[Database](cache=True)
        cache_factory = ConfigFactory[CacheBackend](cache=True)

        # Register configurations
        for name, config in settings.databases.items():
            db_factory.register_config(name, config)

        for name, config in settings.caches.items():
            cache_factory.register_config(name, config)

        # Create instances on demand
        primary_db = db_factory.get("primary")
        replica_db = db_factory.get("replica")
        session_cache = cache_factory.get("session")

        # Verify instances
        assert isinstance(primary_db, Database)
        assert primary_db.host == "primary.db"
        assert isinstance(replica_db, Database)
        assert replica_db.host == "replica.db"
        assert isinstance(session_cache, CacheBackend)
        assert session_cache.prefix == "session"

        # Test caching
        same_primary = db_factory.get("primary")
        assert same_primary is primary_db  # Same instance

        # Test with runtime overrides
        debug_db = db_factory.get("primary", pool_size=50)
        assert debug_db is not primary_db  # Different instance due to override
        assert debug_db.pool_size == 50

    def test_dependency_injection_workflow(self) -> None:
        """Test complete dependency injection workflow."""
        # Setup shared dependencies
        shared_logger = logging.getLogger("shared")
        shared_db = Database("shared.db", 5432)
        shared_cache = CacheBackend("shared.cache", ttl=3600)

        register_dependency("logger", shared_logger)
        register_dependency("shared_db", shared_db)
        register_dependency("shared_cache", shared_cache)

        # Configuration only specifies service-specific params
        service_configs = [
            {
                "_target_": "tests.integration.test_end_to_end.DataService",
                "name": "UserDataService",
                "batch_size": 50,
            },
            {
                "_target_": "tests.integration.test_end_to_end.DataService",
                "name": "OrderDataService",
                "batch_size": 200,
            },
        ]

        # Create services
        services = [instantiate(config) for config in service_configs]

        # Verify all services share dependencies
        assert all(s.db is shared_db for s in services)
        assert all(s.cache is shared_cache for s in services)
        assert all(s.logger is shared_logger for s in services)

        # But have their own configurations
        assert services[0].name == "UserDataService"
        assert services[0].batch_size == 50
        assert services[1].name == "OrderDataService"
        assert services[1].batch_size == 200

    def test_error_recovery_workflow(self) -> None:
        """Test error handling and recovery in complex scenarios."""

        # Configuration with fallback pattern
        config = {
            "_target_": "tests.integration.test_end_to_end.ResilientApp",
            "name": "ResilientSystem",
            "primary_service": {
                "_target_": "tests.integration.test_end_to_end.FailingService",
                "fail_on_init": False,  # This one works
            },
            "fallback_service": {
                "_target_": "tests.integration.test_end_to_end.FailingService",
                "fail_on_init": False,  # Fallback also works
            },
        }

        app = instantiate(config)

        assert isinstance(app, ResilientApp)
        assert app.primary_service.initialized
        assert app.fallback_service.initialized

        # Test with failing primary
        failing_config = config.copy()
        failing_config["primary_service"]["fail_on_init"] = True

        with pytest.raises(Exception) as exc_info:
            instantiate(failing_config)

        assert "Service initialization failed" in str(exc_info.value)

    def test_dynamic_config_type_safety(self) -> None:
        """Test type-safe configuration with DynamicConfig."""

        class DatabaseConfig(DynamicConfig[Database]):
            host: str
            port: int = 5432
            username: str = "user"
            password: str = "pass"
            pool_size: int = 10

        class CacheConfig(DynamicConfig[CacheBackend]):
            host: str = "localhost"
            port: int = 6379
            ttl: int = 3600
            prefix: str = "app"

        class AppConfig(DynamicConfig[Application]):
            name: str
            version: str
            database: DatabaseConfig
            cache: CacheConfig
            features: dict[str, bool] = {"default": True}

        # Create typed configuration
        app_config = AppConfig(
            _target_="tests.integration.test_end_to_end.Application",
            name="TypedApp",
            version="2.0.0",
            database=DatabaseConfig(
                _target_="tests.integration.test_end_to_end.Database",
                host="typed.db",
                port=3306,
                password="typed-pass",
            ),
            cache=CacheConfig(
                _target_="tests.integration.test_end_to_end.CacheBackend",
                prefix="typed",
                ttl=7200,
            ),
            features={"typed": True, "safe": True},
        )

        # Instantiate
        app = instantiate(app_config)

        # Type checker knows these are correct types
        assert isinstance(app, Application)
        assert isinstance(app.database, Database)
        assert isinstance(app.cache, CacheBackend)

        # Verify configuration
        assert app.name == "TypedApp"
        assert app.database.host == "typed.db"
        assert app.database.password == "typed-pass"
        assert app.cache.prefix == "typed"
        assert app.features == {"typed": True, "safe": True}

    def test_settings_inheritance_pattern(self, create_yaml_file: Any) -> None:
        """Test settings inheritance for different environments.

        Parameters
        ----------
        create_yaml_file : callable
            Fixture to create YAML files.
        """
        # Base settings
        base_settings = {
            "app": {"name": "MyService", "version": "1.0.0", "debug": False},
            "database": {
                "_target_": "tests.integration.test_end_to_end.Database",
                "host": "localhost",
                "port": 5432,
                "pool_size": 10,
            },
            "features": {"auth": True, "api": True},
        }

        # Development settings
        dev_settings = {
            "app": {"debug": True},
            "database": {"host": "dev.local", "pool_size": 5},
            "features": {"debug_toolbar": True},
        }

        # Production settings
        prod_settings = {
            "database": {"host": "prod.db.cluster", "port": 3306, "pool_size": 50},
            "features": {"monitoring": True, "debug_toolbar": False},
        }

        base_path = create_yaml_file(base_settings, "base.yaml")
        dev_path = create_yaml_file(dev_settings, "dev.yaml")
        prod_path = create_yaml_file(prod_settings, "prod.yaml")

        # Base settings class
        class BaseAppSettings(BaseSettingsWithInstantiation):
            app: dict[str, Any]
            database: Any
            features: dict[str, bool]

        # Development settings
        class DevSettings(BaseAppSettings):
            model_config = SettingsConfigDict(yaml_file=[str(base_path), str(dev_path)])
            auto_instantiate = True

        # Production settings
        class ProdSettings(BaseAppSettings):
            model_config = SettingsConfigDict(yaml_file=[str(base_path), str(prod_path)])
            auto_instantiate = True

        # Load different environments
        dev = DevSettings()
        prod = ProdSettings()

        # Verify development settings
        assert dev.app["debug"] is True
        assert dev.database.host == "dev.local"
        assert dev.database.pool_size == 5
        assert dev.features["debug_toolbar"] is True

        # Verify production settings
        assert prod.app["debug"] is False  # From base
        assert prod.database.host == "prod.db.cluster"
        assert prod.database.port == 3306
        assert prod.database.pool_size == 50
        assert prod.features.get("debug_toolbar") is False
        assert prod.features["monitoring"] is True

    @pytest.mark.parametrize(
        "config_format",
        ["dict", "dynamic_config", "yaml"],
    )
    def test_multiple_config_formats(self, config_format: str, create_yaml_file: Any) -> None:
        """Test instantiation from different configuration formats.

        Parameters
        ----------
        config_format : str
            Configuration format to test.
        create_yaml_file : callable
            Fixture to create YAML files.
        """
        target_config = {
            "_target_": "tests.integration.test_end_to_end.Database",
            "host": f"{config_format}.db",
            "port": 5432,
        }

        if config_format == "dict":
            # Direct dictionary
            db = instantiate(target_config)

        elif config_format == "dynamic_config":
            # DynamicConfig object
            class DbConfig(DynamicConfig[Database]):
                host: str
                port: int = 5432

            config = DbConfig(**target_config)
            db = instantiate(config)

        else:  # yaml
            # From YAML file
            yaml_path = create_yaml_file({"database": target_config})

            class Settings(BaseSettingsWithInstantiation):
                model_config = SettingsConfigDict(yaml_file=str(yaml_path))
                auto_instantiate = True
                database: Any

            settings = Settings()
            db = settings.database

        # All formats should produce the same result
        assert isinstance(db, Database)
        assert db.host == f"{config_format}.db"
        assert db.port == 5432
