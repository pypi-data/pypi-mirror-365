"""Unit tests for the settings module.

This module tests the BaseSettingsWithInstantiation functionality including:
- Automatic field instantiation
- YAML configuration loading
- Environment variable handling
- Manual instantiation methods
"""

from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest
from pydantic import Field
from pydantic_settings import SettingsConfigDict

from frostbound.pydanticonf import DynamicConfig
from frostbound.pydanticonf.settings import BaseSettingsWithInstantiation


class MockDatabase:
    """Mock database for testing."""

    def __init__(self, host: str, port: int = 5432) -> None:
        self.host = host
        self.port = port
        self.connected = False

    def connect(self) -> None:
        self.connected = True


class MockCache:
    """Mock cache for testing."""

    def __init__(self, ttl: int = 3600) -> None:
        self.ttl = ttl


class DatabaseConfig(DynamicConfig[MockDatabase]):
    """Type-safe database configuration."""

    host: str = "localhost"
    port: int = 5432


class CacheConfig(DynamicConfig[MockCache]):
    """Type-safe cache configuration."""

    ttl: int = 3600


class Service:
    """Mock service for testing."""

    def __init__(self, name: str, database: Any, cache: Any) -> None:
        self.name = name
        self.database = database
        self.cache = cache


class FailingClass:
    """Class that fails during initialization."""

    def __init__(self) -> None:
        raise RuntimeError("Instantiation failed")


class TestBaseSettingsWithInstantiation:
    """Test basic BaseSettingsWithInstantiation functionality."""

    def test_settings_without_auto_instantiate(self) -> None:
        """Verify settings creation without automatic instantiation.

        Tests
        -----
        Fields remain as configuration objects when auto_instantiate=False.
        """

        class TestSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict()
            auto_instantiate: bool = False

            database: DatabaseConfig = DatabaseConfig(_target_="tests.unit.test_settings.MockDatabase", host="test.db")

        settings = TestSettings()

        assert isinstance(settings.database, DatabaseConfig)
        assert settings.database.host == "test.db"
        assert settings.database.target_ == "tests.unit.test_settings.MockDatabase"

    def test_settings_with_auto_instantiate(self) -> None:
        """Verify automatic instantiation when enabled.

        Tests
        -----
        Fields are automatically instantiated when auto_instantiate=True.
        """

        class TestSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict()
            auto_instantiate: bool = True

            database: DatabaseConfig = DatabaseConfig(_target_="tests.unit.test_settings.MockDatabase", host="test.db")

        settings = TestSettings()

        assert isinstance(settings.database, MockDatabase)
        assert settings.database.host == "test.db"
        assert hasattr(settings.database, "connected")

    def test_instantiate_field_method(self) -> None:
        """Verify manual field instantiation with instantiate_field.

        Tests
        -----
        Individual fields can be instantiated on demand.
        """

        class TestSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict()
            auto_instantiate: bool = False

            database: DatabaseConfig = DatabaseConfig(
                _target_="tests.unit.test_settings.MockDatabase", host="test.db", port=5432
            )

        settings = TestSettings()
        db = settings.instantiate_field("database")

        assert isinstance(db, MockDatabase)
        assert db.host == "test.db"
        assert db.port == 5432

    def test_instantiate_field_with_overrides(self) -> None:
        """Verify field instantiation with parameter overrides.

        Tests
        -----
        Runtime overrides can be provided during instantiation.
        """

        class TestSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict()
            auto_instantiate: bool = False

            database: DatabaseConfig = DatabaseConfig(
                _target_="tests.unit.test_settings.MockDatabase", host="original.db", port=5432
            )

        settings = TestSettings()
        db = settings.instantiate_field("database", host="overridden.db", port=3306)

        assert db.host == "overridden.db"
        assert db.port == 3306

    def test_instantiate_field_nonexistent_field_error(self) -> None:
        """Verify error when instantiating non-existent field.

        Tests
        -----
        Clear error message for invalid field names.
        """

        class TestSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict()

        settings = TestSettings()

        with pytest.raises(AttributeError, match="Field 'nonexistent' does not exist"):
            settings.instantiate_field("nonexistent")

    def test_instantiate_field_none_value_error(self) -> None:
        """Verify error when instantiating None field.

        Tests
        -----
        Fields with None value cannot be instantiated.
        """

        class TestSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict()
            database: Any = None

        settings = TestSettings()

        with pytest.raises(ValueError, match="Field 'database' is None"):
            settings.instantiate_field("database")

    def test_instantiate_all_method(self) -> None:
        """Verify instantiate_all creates all eligible fields.

        Tests
        -----
        All fields with instantiatable configurations are processed.
        """

        class TestSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict()
            auto_instantiate: bool = False

            database: DatabaseConfig = DatabaseConfig(
                _target_="tests.unit.test_settings.MockDatabase", host="db.server"
            )
            cache: CacheConfig = CacheConfig(_target_="tests.unit.test_settings.MockCache", ttl=7200)
            regular_field: str = "not instantiatable"

        settings = TestSettings()
        instances = settings.instantiate_all()

        assert hasattr(instances, "database")
        assert hasattr(instances, "cache")
        assert not hasattr(instances, "regular_field")
        assert isinstance(instances.database, MockDatabase)
        assert isinstance(instances.cache, MockCache)
        assert instances.cache.ttl == 7200

    def test_instantiate_fields_selective(self) -> None:
        """Verify selective field instantiation with instantiate_fields.

        Tests
        -----
        Only specified fields are instantiated.
        """

        class TestSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict()
            auto_instantiate: bool = False

            database: DatabaseConfig = DatabaseConfig(_target_="tests.unit.test_settings.MockDatabase")
            cache: CacheConfig = CacheConfig(_target_="tests.unit.test_settings.MockCache")
            logger: Any = {"_target_": "logging.Logger", "name": "test"}

        settings = TestSettings()
        # Only instantiate database and cache
        instances = settings.instantiate_fields("database", "cache")

        assert hasattr(instances, "database")
        assert hasattr(instances, "cache")
        assert not hasattr(instances, "logger")


class TestDynamicConfigDetection:
    """Test detection of instantiatable fields."""

    def test_detect_dynamic_config_instance(self) -> None:
        """Verify DynamicConfig instances are detected for instantiation.

        Tests
        -----
        Fields containing DynamicConfig objects are identified.
        """

        class TestSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict()
            auto_instantiate: bool = True

            config_field: Any = DatabaseConfig(_target_="tests.unit.test_settings.MockDatabase")

        settings = TestSettings()

        assert isinstance(settings.config_field, MockDatabase)

    def test_detect_dict_with_target(self) -> None:
        """Verify dicts with _target_ are detected for instantiation.

        Tests
        -----
        Plain dictionaries with _target_ key are instantiated.
        """

        class TestSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict()
            auto_instantiate: bool = True

            dict_field: Any = {
                "_target_": "tests.unit.test_settings.MockDatabase",
                "host": "dict.db",
            }

        settings = TestSettings()

        assert isinstance(settings.dict_field, MockDatabase)
        assert settings.dict_field.host == "dict.db"

    def test_detect_typed_dynamic_config_field(self) -> None:
        """Verify fields typed as DynamicConfig subclasses are detected.

        Tests
        -----
        Type annotations guide instantiation behavior.
        """

        class TestSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict()
            auto_instantiate: bool = True

            # Field is typed as DatabaseConfig
            database: DatabaseConfig = Field(
                default_factory=lambda: DatabaseConfig(_target_="tests.unit.test_settings.MockDatabase")
            )

        settings = TestSettings()

        assert isinstance(settings.database, MockDatabase)

    def test_skip_regular_fields(self) -> None:
        """Verify non-instantiatable fields are skipped.

        Tests
        -----
        Regular fields without _target_ are left unchanged.
        """

        class TestSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict()
            auto_instantiate: bool = True

            regular_dict: dict[str, Any] = {"key": "value"}
            regular_string: str = "test"
            regular_number: int = 42

        settings = TestSettings()

        assert settings.regular_dict == {"key": "value"}
        assert settings.regular_string == "test"
        assert settings.regular_number == 42


class TestYAMLIntegration:
    """Test YAML configuration source integration."""

    @patch("pydantic_settings.sources.YamlConfigSettingsSource")
    def test_yaml_source_single_file(self, mock_yaml_source: MagicMock) -> None:
        """Verify single YAML file configuration.

        Tests
        -----
        YAML source is created with correct parameters for single file.
        """

        class TestSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(yaml_file="config.yaml")

        # Access the customized sources
        TestSettings.settings_customise_sources(
            TestSettings,
            Mock(),  # init_settings
            Mock(),  # env_settings
            Mock(),  # dotenv_settings
            Mock(),  # file_secret_settings
        )

        # Verify YAML source was created
        mock_yaml_source.assert_called_once()
        call_kwargs = mock_yaml_source.call_args.kwargs
        assert call_kwargs["yaml_file"] == "config.yaml"
        assert call_kwargs["yaml_file_encoding"] == "utf-8"

    @patch("pydantic_settings.sources.YamlConfigSettingsSource")
    def test_yaml_source_multiple_files(self, mock_yaml_source: MagicMock) -> None:
        """Verify multiple YAML file configuration.

        Tests
        -----
        YAML source handles list of files for merging.
        """

        class TestSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict(yaml_file=["base.yaml", "override.yaml"])

        TestSettings.settings_customise_sources(TestSettings, Mock(), Mock(), Mock(), Mock())

        mock_yaml_source.assert_called_once()
        call_kwargs = mock_yaml_source.call_args.kwargs
        assert call_kwargs["yaml_file"] == ["base.yaml", "override.yaml"]

    def test_no_yaml_preserves_default_sources(self) -> None:
        """Verify source order is preserved when no YAML configured.

        Tests
        -----
        Default pydantic-settings behavior when YAML not used.
        """

        class TestSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict()

        init_mock = Mock()
        env_mock = Mock()
        dotenv_mock = Mock()
        secret_mock = Mock()

        sources = TestSettings.settings_customise_sources(TestSettings, init_mock, env_mock, dotenv_mock, secret_mock)

        assert sources == (init_mock, env_mock, dotenv_mock, secret_mock)


class TestComplexScenarios:
    """Test complex real-world scenarios."""

    def test_nested_instantiation_with_auto(self) -> None:
        """Verify deeply nested configurations are instantiated.

        Tests
        -----
        Recursive instantiation works with nested structures.
        """

        class TestSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict()
            auto_instantiate: bool = True

            service: Any = {
                "_target_": "tests.unit.test_settings.Service",
                "name": "MainService",
                "database": {
                    "_target_": "tests.unit.test_settings.MockDatabase",
                    "host": "nested.db",
                },
                "cache": {"_target_": "tests.unit.test_settings.MockCache", "ttl": 1800},
            }

        settings = TestSettings()

        assert isinstance(settings.service, Service)
        assert settings.service.name == "MainService"
        assert isinstance(settings.service.database, MockDatabase)
        assert settings.service.database.host == "nested.db"
        assert isinstance(settings.service.cache, MockCache)
        assert settings.service.cache.ttl == 1800

    def test_mixed_config_types(self) -> None:
        """Verify mixing DynamicConfig and dict configurations.

        Tests
        -----
        Different configuration styles can be mixed in same settings.
        """

        class TestSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict()
            auto_instantiate: bool = True

            # DynamicConfig style
            database: DatabaseConfig = DatabaseConfig(_target_="tests.unit.test_settings.MockDatabase", host="typed.db")

            # Dict style
            cache: Any = {"_target_": "tests.unit.test_settings.MockCache", "ttl": 2400}

            # Regular field
            app_name: str = "TestApp"

        settings = TestSettings()

        assert isinstance(settings.database, MockDatabase)
        assert settings.database.host == "typed.db"
        assert isinstance(settings.cache, MockCache)
        assert settings.cache.ttl == 2400
        assert settings.app_name == "TestApp"

    def test_error_handling_during_instantiation(self) -> None:
        """Verify errors during instantiation are properly reported.

        Tests
        -----
        Clear error messages with field context.
        """

        class TestSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict()
            auto_instantiate: bool = True

            failing_field: Any = {"_target_": "tests.unit.test_settings.FailingClass"}

        with pytest.raises(ValueError) as exc_info:
            TestSettings()

        assert "Failed to instantiate field 'failing_field'" in str(exc_info.value)

    @pytest.mark.parametrize(
        ("field_type", "field_value", "should_instantiate"),
        [
            (
                DatabaseConfig,
                DatabaseConfig(_target_="tests.unit.test_settings.MockDatabase"),
                True,
            ),
            (Any, {"_target_": "tests.unit.test_settings.MockCache"}, True),
            (dict[str, Any], {"key": "value"}, False),
            (str, "regular string", False),
            (Any, {"no_target": "present"}, False),
        ],
    )
    def test_instantiation_detection_matrix(
        self, field_type: type[Any], field_value: Any, should_instantiate: bool
    ) -> None:
        """Verify various field type and value combinations.

        Parameters
        ----------
        field_type : type[Any]
            The field's type annotation.
        field_value : Any
            The field's value.
        should_instantiate : bool
            Whether the field should be instantiated.

        Tests
        -----
        Comprehensive matrix of field detection scenarios.
        """

        class TestSettings(BaseSettingsWithInstantiation):
            model_config = SettingsConfigDict()
            auto_instantiate: bool = True
            test_field: field_type = field_value  # type: ignore[valid-type]

        settings = TestSettings()

        if should_instantiate:
            # Should be instantiated to the target class
            assert not isinstance(settings.test_field, dict | DynamicConfig)
        else:
            # Should remain as original value
            assert settings.test_field == field_value
