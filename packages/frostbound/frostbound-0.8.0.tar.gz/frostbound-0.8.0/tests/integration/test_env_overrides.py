"""Integration tests for environment variable overrides.

This module tests how environment variables interact with
YAML configuration and instantiation in pydanticonf.
"""

from typing import Any

import pytest
from pydantic_settings import SettingsConfigDict

from frostbound.pydanticonf import BaseSettingsWithInstantiation, DynamicConfig


class MockDatabase:
    """Mock database for testing."""

    def __init__(self, host: str, port: int = 5432, pool_size: int = 10) -> None:
        self.host = host
        self.port = port
        self.pool_size = pool_size


class MockCache:
    """Mock cache for testing."""

    def __init__(self, host: str = "localhost", port: int = 6379, ttl: int = 3600) -> None:
        self.host = host
        self.port = port
        self.ttl = ttl


class Service:
    """Service with database and cache dependencies."""

    def __init__(self, database: Any, cache: Any) -> None:
        self.database = database
        self.cache = cache


@pytest.mark.integration
class TestEnvironmentVariableOverrides:
    """Test environment variable override functionality."""

    def test_simple_env_override(self, env_vars: dict[str, str]) -> None:
        """Verify basic environment variable overrides.

        Parameters
        ----------
        env_vars : dict[str, str]
            Environment variable fixture.
        """
        env_vars["APP_NAME"] = "EnvApp"
        env_vars["APP_DEBUG"] = "true"
        env_vars["APP_VERSION"] = "2.0.0"

        class Settings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(env_prefix="APP_")

            name: str = "DefaultApp"
            debug: bool = False
            version: str = "1.0.0"

        settings = Settings()

        assert settings.name == "EnvApp"
        assert settings.debug is True
        assert settings.version == "2.0.0"

    def test_nested_env_override(self, env_vars: dict[str, str]) -> None:
        """Verify nested environment variable overrides.

        Parameters
        ----------
        env_vars : dict[str, str]
            Environment variable fixture.
        """
        env_vars["APP_DATABASE__HOST"] = "env.db.server"
        env_vars["APP_DATABASE__PORT"] = "3306"
        env_vars["APP_CACHE__TTL"] = "7200"

        class DatabaseConfig(DynamicConfig[MockDatabase]):
            host: str = "localhost"
            port: int = 5432

        class CacheConfig(DynamicConfig[MockCache]):
            ttl: int = 3600

        class Settings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(env_prefix="APP_", env_nested_delimiter="__")
            auto_instantiate = True

            database: DatabaseConfig = DatabaseConfig(_target_="tests.integration.test_env_overrides.MockDatabase")
            cache: CacheConfig = CacheConfig(_target_="tests.integration.test_env_overrides.MockCache")

        settings = Settings()

        assert isinstance(settings.database, MockDatabase)
        assert settings.database.host == "env.db.server"
        assert settings.database.port == 3306

        assert isinstance(settings.cache, MockCache)
        assert settings.cache.ttl == 7200

    def test_env_override_with_yaml(self, create_yaml_file: Any, env_vars: dict[str, str]) -> None:
        """Verify environment variables override YAML configuration.

        Parameters
        ----------
        create_yaml_file : callable
            Fixture to create YAML files.
        env_vars : dict[str, str]
            Environment variable fixture.
        """
        yaml_content = {
            "app_name": "YamlApp",
            "debug": False,
            "database": {
                "_target_": "tests.integration.test_env_overrides.MockDatabase",
                "host": "yaml.db.server",
                "port": 5432,
            },
        }

        yaml_path = create_yaml_file(yaml_content)

        # Environment overrides
        env_vars["MYAPP_APP_NAME"] = "EnvOverrideApp"
        env_vars["MYAPP_DEBUG"] = "true"
        env_vars["MYAPP_DATABASE__HOST"] = "env.override.server"

        class Settings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(
                yaml_file=str(yaml_path),
                env_prefix="MYAPP_",
                env_nested_delimiter="__",
            )
            auto_instantiate = True

            app_name: str
            debug: bool
            database: Any

        settings = Settings()

        # Env vars should override YAML
        assert settings.app_name == "EnvOverrideApp"
        assert settings.debug is True
        assert settings.database.host == "env.override.server"
        assert settings.database.port == 5432  # From YAML, not overridden

    def test_precedence_order(self, create_yaml_file: Any, env_vars: dict[str, str], tmp_path: Any) -> None:
        """Verify configuration source precedence order.

        Parameters
        ----------
        create_yaml_file : callable
            Fixture to create YAML files.
        env_vars : dict[str, str]
            Environment variable fixture.
        tmp_path : Any
            Temporary directory path.
        """
        # Create .env file
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_VALUE=from_dotenv\nTEST_PRIORITY=dotenv")

        # Create YAML file
        yaml_content = {
            "value": "from_yaml",
            "priority": "yaml",
            "yaml_only": "yaml_value",
        }
        yaml_path = create_yaml_file(yaml_content)

        # Set environment variable
        env_vars["TEST_VALUE"] = "from_env"
        env_vars["TEST_ENV_ONLY"] = "env_value"

        class Settings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(
                yaml_file=str(yaml_path),
                env_prefix="TEST_",
                env_file=str(env_file),
            )

            value: str = "default"
            priority: str = "default"
            yaml_only: str = "default"
            env_only: str = "default"

        # Constructor args have highest precedence
        settings = Settings(value="from_constructor")

        assert settings.value == "from_constructor"  # Constructor wins
        assert settings.priority == "yaml"  # YAML overrides dotenv
        assert settings.yaml_only == "yaml_value"  # From YAML
        assert settings.env_only == "env_value"  # From env var

    def test_complex_nested_env_override(self, env_vars: dict[str, str]) -> None:
        """Verify deeply nested environment variable overrides.

        Parameters
        ----------
        env_vars : dict[str, str]
            Environment variable fixture.
        """
        env_vars["APP_SERVICE__DATABASE__HOST"] = "deep.env.host"
        env_vars["APP_SERVICE__DATABASE__PORT"] = "3307"
        env_vars["APP_SERVICE__CACHE__HOST"] = "cache.env.host"

        class Settings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(env_prefix="APP_", env_nested_delimiter="__")
            auto_instantiate = True

            service: Any = {
                "_target_": "tests.integration.test_env_overrides.Service",
                "database": {
                    "_target_": "tests.integration.test_env_overrides.MockDatabase",
                    "host": "default.db",
                    "port": 5432,
                },
                "cache": {
                    "_target_": "tests.integration.test_env_overrides.MockCache",
                    "host": "default.cache",
                },
            }

        settings = Settings()

        assert isinstance(settings.service, Service)
        assert settings.service.database.host == "deep.env.host"
        assert settings.service.database.port == 3307
        assert settings.service.cache.host == "cache.env.host"

    def test_env_override_type_conversion(self, env_vars: dict[str, str]) -> None:
        """Verify type conversion for environment variable values.

        Parameters
        ----------
        env_vars : dict[str, str]
            Environment variable fixture.
        """
        env_vars["CONFIG_PORT"] = "8080"
        env_vars["CONFIG_TIMEOUT"] = "30.5"
        env_vars["CONFIG_DEBUG"] = "true"
        env_vars["CONFIG_MAX_RETRIES"] = "5"
        env_vars["CONFIG_FEATURES"] = '["auth", "api", "admin"]'  # JSON string

        class Settings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(env_prefix="CONFIG_")

            port: int = 3000
            timeout: float = 10.0
            debug: bool = False
            max_retries: int = 3
            features: list[str] = []

        settings = Settings()

        assert settings.port == 8080
        assert settings.timeout == 30.5
        assert settings.debug is True
        assert settings.max_retries == 5
        assert settings.features == ["auth", "api", "admin"]

    def test_env_override_with_instantiation(self, env_vars: dict[str, str]) -> None:
        """Verify environment overrides work with auto-instantiation.

        Parameters
        ----------
        env_vars : dict[str, str]
            Environment variable fixture.
        """
        env_vars["APP_DATABASE__POOL_SIZE"] = "50"

        class Settings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(env_prefix="APP_", env_nested_delimiter="__")
            auto_instantiate = True

            database: Any = {
                "_target_": "tests.integration.test_env_overrides.MockDatabase",
                "host": "localhost",
                "port": 5432,
                "pool_size": 10,
            }

        settings = Settings()

        assert isinstance(settings.database, MockDatabase)
        assert settings.database.host == "localhost"
        assert settings.database.port == 5432
        assert settings.database.pool_size == 50  # Overridden by env

    def test_env_prefix_isolation(self, env_vars: dict[str, str]) -> None:
        """Verify environment prefix properly isolates variables.

        Parameters
        ----------
        env_vars : dict[str, str]
            Environment variable fixture.
        """
        # Set variables with different prefixes
        env_vars["APP1_NAME"] = "App1"
        env_vars["APP2_NAME"] = "App2"
        env_vars["NAME"] = "NoPrefix"

        class Settings1(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(env_prefix="APP1_")
            name: str = "Default1"

        class Settings2(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(env_prefix="APP2_")
            name: str = "Default2"

        class Settings3(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict()  # No prefix
            name: str = "Default3"

        settings1 = Settings1()
        settings2 = Settings2()
        settings3 = Settings3()

        assert settings1.name == "App1"
        assert settings2.name == "App2"
        assert settings3.name == "NoPrefix"

    @pytest.mark.parametrize(
        ("env_value", "expected_parsed"),
        [
            ('{"key": "value"}', {"key": "value"}),
            ('["item1", "item2"]', ["item1", "item2"]),
            ("plain_string", "plain_string"),
            ("123", 123),
            ("12.34", 12.34),
            ("true", True),
            ("false", False),
        ],
    )
    def test_env_json_parsing(self, env_vars: dict[str, str], env_value: str, expected_parsed: Any) -> None:
        """Verify JSON parsing of environment variable values.

        Parameters
        ----------
        env_vars : dict[str, str]
            Environment variable fixture.
        env_value : str
            Environment variable value to test.
        expected_parsed : Any
            Expected parsed result.
        """
        env_vars["TEST_VALUE"] = env_value

        class Settings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(env_prefix="TEST_")
            value: Any = None

        settings = Settings()

        if isinstance(expected_parsed, dict | list):
            assert settings.value == expected_parsed
        elif isinstance(expected_parsed, bool):
            assert settings.value is expected_parsed
        elif isinstance(expected_parsed, int | float):
            assert settings.value == expected_parsed
        else:
            assert settings.value == expected_parsed

    def test_case_sensitivity_handling(self, env_vars: dict[str, str]) -> None:
        """Verify case sensitivity in environment variable names.

        Parameters
        ----------
        env_vars : dict[str, str]
            Environment variable fixture.
        """
        env_vars["APP_DATABASE_HOST"] = "lowercase_delimiter"
        env_vars["APP_DATABASE__PORT"] = "5433"

        class Settings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(
                env_prefix="APP_",
                env_nested_delimiter="__",
                case_sensitive=False,
            )

            database: dict[str, Any] = {"host": "default", "port": 5432}

        settings = Settings()

        # With case_sensitive=False, both should work
        assert settings.database["host"] == "lowercase_delimiter"
        assert settings.database["port"] == 5433
