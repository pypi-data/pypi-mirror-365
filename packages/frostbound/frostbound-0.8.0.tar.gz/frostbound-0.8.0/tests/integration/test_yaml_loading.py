"""Integration tests for YAML configuration loading.

This module tests the integration of YAML file loading with
BaseSettingsWithInstantiation, including multi-file merging
and environment variable substitution.
"""

from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic_settings import SettingsConfigDict

from frostbound.pydanticonf import BaseSettingsWithInstantiation


class MockDatabase:
    """Mock database for testing."""

    def __init__(self, host: str, port: int = 5432, **kwargs: Any) -> None:
        self.host = host
        self.port = port
        self.options = kwargs


class MockCache:
    """Mock cache for testing."""

    def __init__(self, backend: str = "memory", ttl: int = 3600, **kwargs: Any) -> None:
        self.backend = backend
        self.ttl = ttl
        self.options = kwargs


class MockService:
    """Mock service for testing."""

    def __init__(self, name: str, database: Any = None, cache: Any = None) -> None:
        self.name = name
        self.database = database
        self.cache = cache


@pytest.mark.integration
class TestYAMLLoading:
    """Test YAML file loading functionality."""

    def test_single_yaml_file_loading(self, create_yaml_file: Any) -> None:
        """Verify loading configuration from a single YAML file.

        Parameters
        ----------
        create_yaml_file : callable
            Fixture to create YAML files.
        """
        yaml_content = {
            "app_name": "TestApp",
            "debug": True,
            "database": {
                "_target_": "tests.integration.test_yaml_loading.MockDatabase",
                "host": "localhost",
                "port": 5432,
            },
        }

        yaml_path = create_yaml_file(yaml_content)

        class Settings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(yaml_file=str(yaml_path))
            auto_instantiate = True

            app_name: str
            debug: bool
            database: Any

        settings = Settings()

        assert settings.app_name == "TestApp"
        assert settings.debug is True
        assert isinstance(settings.database, MockDatabase)
        assert settings.database.host == "localhost"
        assert settings.database.port == 5432

    def test_multi_yaml_file_merging(self, create_yaml_file: Any) -> None:
        """Verify configuration merging from multiple YAML files.

        Parameters
        ----------
        create_yaml_file : callable
            Fixture to create YAML files.
        """
        # Base configuration
        base_yaml = {
            "app_name": "MyApp",
            "version": "1.0.0",
            "database": {
                "_target_": "tests.integration.test_yaml_loading.MockDatabase",
                "host": "localhost",
                "port": 5432,
            },
            "features": {"auth": True, "api": True, "admin": False},
        }

        # Development overrides
        dev_yaml = {
            "debug": True,
            "database": {"host": "dev.db.local"},
            "features": {"admin": True, "debug_toolbar": True},
        }

        # Production overrides
        prod_yaml = {
            "debug": False,
            "database": {"host": "prod.db.server", "port": 3306},
            "features": {"monitoring": True, "debug_toolbar": False},
        }

        base_path = create_yaml_file(base_yaml, "base.yaml")
        dev_path = create_yaml_file(dev_yaml, "dev.yaml")
        prod_path = create_yaml_file(prod_yaml, "prod.yaml")

        # Test development configuration
        class DevSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(yaml_file=[str(base_path), str(dev_path)])
            auto_instantiate = True

            app_name: str
            version: str
            debug: bool = False
            database: Any
            features: dict[str, bool]

        dev_settings = DevSettings()

        assert dev_settings.app_name == "MyApp"
        assert dev_settings.version == "1.0.0"
        assert dev_settings.debug is True
        assert dev_settings.database.host == "dev.db.local"
        assert dev_settings.database.port == 5432  # From base
        assert dev_settings.features == {
            "auth": True,
            "api": True,
            "admin": True,
            "debug_toolbar": True,
        }

        # Test production configuration
        class ProdSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(yaml_file=[str(base_path), str(prod_path)])
            auto_instantiate = True

            app_name: str
            version: str
            debug: bool = False
            database: Any
            features: dict[str, bool]

        prod_settings = ProdSettings()

        assert prod_settings.debug is False
        assert prod_settings.database.host == "prod.db.server"
        assert prod_settings.database.port == 3306  # Overridden
        assert prod_settings.features["monitoring"] is True
        assert prod_settings.features["debug_toolbar"] is False

    def test_yaml_with_nested_instantiation(self, create_yaml_file: Any) -> None:
        """Verify nested object instantiation from YAML.

        Parameters
        ----------
        create_yaml_file : callable
            Fixture to create YAML files.
        """
        yaml_content = {
            "service": {
                "_target_": "tests.integration.test_yaml_loading.MockService",
                "name": "MainService",
                "database": {
                    "_target_": "tests.integration.test_yaml_loading.MockDatabase",
                    "host": "db.server",
                    "port": 5432,
                },
                "cache": {
                    "_target_": "tests.integration.test_yaml_loading.MockCache",
                    "backend": "redis",
                    "ttl": 7200,
                },
            }
        }

        yaml_path = create_yaml_file(yaml_content)

        class Settings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(yaml_file=str(yaml_path))
            auto_instantiate = True

            service: Any

        settings = Settings()

        assert isinstance(settings.service, MockService)
        assert settings.service.name == "MainService"
        assert isinstance(settings.service.database, MockDatabase)
        assert settings.service.database.host == "db.server"
        assert isinstance(settings.service.cache, MockCache)
        assert settings.service.cache.backend == "redis"
        assert settings.service.cache.ttl == 7200

    def test_yaml_without_instantiation(self, create_yaml_file: Any) -> None:
        """Verify YAML loading without automatic instantiation.

        Parameters
        ----------
        create_yaml_file : callable
            Fixture to create YAML files.
        """
        yaml_content = {
            "database": {
                "_target_": "tests.integration.test_yaml_loading.MockDatabase",
                "host": "localhost",
            }
        }

        yaml_path = create_yaml_file(yaml_content)

        class Settings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(yaml_file=str(yaml_path))
            auto_instantiate = False

            database: dict[str, Any]

        settings = Settings()

        # Should remain as dictionary
        assert isinstance(settings.database, dict)
        assert settings.database["_target_"] == "tests.integration.test_yaml_loading.MockDatabase"
        assert settings.database["host"] == "localhost"

        # Can manually instantiate later
        db = settings.instantiate_field("database")
        assert isinstance(db, MockDatabase)
        assert db.host == "localhost"

    def test_yaml_with_lists_of_configs(self, create_yaml_file: Any) -> None:
        """Verify handling of lists containing instantiatable configs.

        Parameters
        ----------
        create_yaml_file : callable
            Fixture to create YAML files.
        """
        yaml_content = {
            "databases": [
                {
                    "_target_": "tests.integration.test_yaml_loading.MockDatabase",
                    "host": "primary.db",
                    "port": 5432,
                },
                {
                    "_target_": "tests.integration.test_yaml_loading.MockDatabase",
                    "host": "secondary.db",
                    "port": 5433,
                },
            ]
        }

        yaml_path = create_yaml_file(yaml_content)

        class Settings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(yaml_file=str(yaml_path))
            auto_instantiate = True

            databases: list[Any]

        settings = Settings()

        assert len(settings.databases) == 2
        assert all(isinstance(db, MockDatabase) for db in settings.databases)
        assert settings.databases[0].host == "primary.db"
        assert settings.databases[1].host == "secondary.db"
        assert settings.databases[0].port == 5432
        assert settings.databases[1].port == 5433

    def test_yaml_file_not_found_error(self) -> None:
        """Verify proper error handling for missing YAML files."""

        class Settings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(yaml_file="nonexistent.yaml")

        with pytest.raises(Exception):  # pydantic-settings will raise an error
            Settings()

    def test_invalid_yaml_syntax_error(self, tmp_path: Path) -> None:
        """Verify error handling for invalid YAML syntax.

        Parameters
        ----------
        tmp_path : Path
            Temporary directory path.
        """
        yaml_path = tmp_path / "invalid.yaml"
        yaml_path.write_text("invalid: yaml: content:\n  - no proper")

        class Settings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(yaml_file=str(yaml_path))

        with pytest.raises(Exception):  # YAML parsing error
            Settings()

    def test_yaml_encoding_options(self, tmp_path: Path) -> None:
        """Verify YAML file encoding options.

        Parameters
        ----------
        tmp_path : Path
            Temporary directory path.
        """
        yaml_content = {"message": "Hello UTF-8 世界"}
        yaml_path = tmp_path / "utf8.yaml"

        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(yaml_content, f, allow_unicode=True)

        class Settings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(yaml_file=str(yaml_path), yaml_file_encoding="utf-8")

            message: str

        settings = Settings()
        assert settings.message == "Hello UTF-8 世界"

    @pytest.mark.parametrize(
        "merge_configs",
        [
            # Two files with nested merge
            [
                {"app": {"name": "Base", "version": "1.0"}, "debug": False},
                {"app": {"version": "2.0"}, "debug": True},
            ],
            # Three files with progressive overrides
            [
                {"level": "base", "values": {"a": 1, "b": 2}},
                {"level": "dev", "values": {"b": 20, "c": 30}},
                {"level": "prod", "values": {"c": 300, "d": 400}},
            ],
        ],
    )
    def test_yaml_merge_scenarios(self, create_yaml_file: Any, merge_configs: list[dict[str, Any]]) -> None:
        """Verify various YAML merging scenarios.

        Parameters
        ----------
        create_yaml_file : callable
            Fixture to create YAML files.
        merge_configs : list[dict[str, Any]]
            List of configurations to merge.
        """
        yaml_paths = [create_yaml_file(config, f"config_{i}.yaml") for i, config in enumerate(merge_configs)]

        class Settings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(yaml_file=[str(p) for p in yaml_paths])
            extra = "allow"  # Allow extra fields

        settings = Settings()

        if len(merge_configs) == 2:
            # First scenario
            assert settings.app["name"] == "Base"  # type: ignore[attr-defined]
            assert settings.app["version"] == "2.0"  # type: ignore[attr-defined]
            assert settings.debug is True  # type: ignore[attr-defined]
        else:
            # Second scenario
            assert settings.level == "prod"  # type: ignore[attr-defined]
            assert settings.values == {"a": 1, "b": 20, "c": 300, "d": 400}  # type: ignore[attr-defined]
