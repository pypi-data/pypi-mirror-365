"""Unit tests for the instantiate module.

This module tests the core instantiation functionality including:
- Object creation from configurations
- Dependency injection
- Error handling
- Recursive instantiation
- Partial instantiation
"""

import functools
from typing import Any
from unittest.mock import Mock, patch

import pytest
from pydantic import BaseModel

from frostbound.pydanticonf._instantiate import (
    InstantiationError,
    _types_match_semantically,
    clear_dependencies,
    get_registered_dependencies,
    instantiate,
    register_dependency,
)
from frostbound.pydanticonf.base import DynamicConfig


class SimpleClass:
    """Simple test class for instantiation."""

    def __init__(self, name: str, value: int = 42) -> None:
        self.name = name
        self.value = value


class ComplexClass:
    """Test class with multiple dependencies."""

    def __init__(self, name: str, database: Any, logger: Any, cache: Any | None = None) -> None:
        self.name = name
        self.database = database
        self.logger = logger
        self.cache = cache


class NoInitClass:
    """Test class without __init__ method."""

    pass


class ListContainer:
    """Container for list items."""

    def __init__(self, items: list[Any]) -> None:
        self.items = items


class Database:
    """Mock database class."""

    pass


class Logger:
    """Mock logger class."""

    pass


class TypedClass:
    """Class with typed dependencies."""

    def __init__(self, db: Database, log: Logger) -> None:
        self.db = db
        self.log = log


class FailingClass:
    """Class that fails during initialization."""

    def __init__(self) -> None:
        raise ValueError("Constructor failed")


class ConfigModel(BaseModel):
    """Pydantic model with target configuration."""

    _target_: str = "tests.unit.test_instantiate.SimpleClass"
    name: str = "FromModel"
    value: int = 777


class TestInstantiateBasics:
    """Test basic instantiation functionality."""

    def test_instantiate_from_dict_basic(self) -> None:
        """Verify basic instantiation from dictionary configuration.

        Tests
        -----
        Object creation with simple parameters from dict config.
        """
        config = {
            "_target_": "tests.unit.test_instantiate.SimpleClass",
            "name": "TestObject",
            "value": 100,
        }

        result = instantiate(config)

        assert isinstance(result, SimpleClass)
        assert result.name == "TestObject"
        assert result.value == 100

    def test_instantiate_from_dynamic_config(self) -> None:
        """Verify instantiation from DynamicConfig object.

        Tests
        -----
        Object creation using type-safe DynamicConfig.
        """
        config = DynamicConfig[SimpleClass](
            _target_="tests.unit.test_instantiate.SimpleClass",
            name="ConfigObject",
            value=200,
        )

        result = instantiate(config)

        assert isinstance(result, SimpleClass)
        assert result.name == "ConfigObject"
        assert result.value == 200

    def test_instantiate_with_default_values(self) -> None:
        """Verify instantiation respects default parameter values.

        Tests
        -----
        Constructor default values are used when not specified in config.
        """
        config = {
            "_target_": "tests.unit.test_instantiate.SimpleClass",
            "name": "DefaultTest",
        }

        result = instantiate(config)

        assert result.name == "DefaultTest"
        assert result.value == 42  # Default value

    def test_instantiate_with_positional_args(self) -> None:
        """Verify instantiation with _args_ for positional arguments.

        Tests
        -----
        Using _args_ to pass positional arguments to constructor.
        """
        config = {
            "_target_": "builtins.dict",
            "_args_": [[("key1", "value1"), ("key2", "value2")]],
        }

        result = instantiate(config)

        assert isinstance(result, dict)
        assert result == {"key1": "value1", "key2": "value2"}

    def test_instantiate_with_kwargs_override(self) -> None:
        """Verify runtime kwargs override configuration values.

        Tests
        -----
        Parameters passed to instantiate() override config values.
        """
        config = {
            "_target_": "tests.unit.test_instantiate.SimpleClass",
            "name": "Original",
            "value": 100,
        }

        result = instantiate(config, name="Overridden", value=999)

        assert result.name == "Overridden"
        assert result.value == 999

    def test_instantiate_no_target_raises_error(self) -> None:
        """Verify InstantiationError when _target_ is missing.

        Tests
        -----
        Proper error handling for missing _target_ field.
        """
        config = {"name": "Test", "value": 42}

        with pytest.raises(InstantiationError) as exc_info:
            instantiate(config)

        assert "No _target_ specified" in str(exc_info.value)


class TestInstantiatePartial:
    """Test partial instantiation functionality."""

    def test_instantiate_partial_returns_partial(self) -> None:
        """Verify _partial_=True returns functools.partial object.

        Tests
        -----
        Partial instantiation for factory pattern usage.
        """
        config = {
            "_target_": "tests.unit.test_instantiate.SimpleClass",
            "_partial_": True,
            "name": "PartialTest",
        }

        result = instantiate(config)

        assert isinstance(result, functools.partial)
        # Complete the partial by calling it
        instance = result(value=300)
        assert isinstance(instance, SimpleClass)
        assert instance.name == "PartialTest"
        assert instance.value == 300

    def test_instantiate_partial_with_dynamic_config(self) -> None:
        """Verify partial instantiation with DynamicConfig.

        Tests
        -----
        Partial instantiation using type-safe configuration.
        """
        config = DynamicConfig[SimpleClass](
            _target_="tests.unit.test_instantiate.SimpleClass",
            _partial_=True,
            value=500,
        )

        partial_func = instantiate(config)
        instance = partial_func(name="FromPartial")

        assert instance.name == "FromPartial"
        assert instance.value == 500


class TestInstantiateRecursive:
    """Test recursive instantiation functionality."""

    def test_recursive_instantiation_nested_dict(self) -> None:
        """Verify recursive instantiation of nested configurations.

        Tests
        -----
        Nested dictionaries with _target_ are automatically instantiated.
        """
        config = {
            "_target_": "tests.unit.test_instantiate.ComplexClass",
            "name": "MainObject",
            "database": {
                "_target_": "tests.unit.test_instantiate.SimpleClass",
                "name": "Database",
                "value": 5432,
            },
            "logger": {
                "_target_": "tests.unit.test_instantiate.SimpleClass",
                "name": "Logger",
                "value": 1,
            },
        }

        result = instantiate(config)

        assert isinstance(result, ComplexClass)
        assert result.name == "MainObject"
        assert isinstance(result.database, SimpleClass)
        assert result.database.name == "Database"
        assert isinstance(result.logger, SimpleClass)
        assert result.logger.name == "Logger"

    def test_recursive_instantiation_disabled(self) -> None:
        """Verify _recursive_=False prevents nested instantiation.

        Tests
        -----
        Nested configurations remain as dicts when recursive is disabled.
        """
        config = {
            "_target_": "tests.unit.test_instantiate.ComplexClass",
            "_recursive_": False,
            "name": "NoRecursion",
            "database": {
                "_target_": "tests.unit.test_instantiate.SimpleClass",
                "name": "Database",
            },
            "logger": {"_target_": "tests.unit.test_instantiate.SimpleClass", "name": "Logger"},
        }

        result = instantiate(config)

        assert isinstance(result, ComplexClass)
        assert isinstance(result.database, dict)
        assert result.database["_target_"] == "tests.unit.test_instantiate.SimpleClass"
        assert isinstance(result.logger, dict)

    def test_recursive_instantiation_in_list(self) -> None:
        """Verify recursive instantiation works inside lists.

        Tests
        -----
        List elements with _target_ are instantiated recursively.
        """

        config = {
            "_target_": "tests.unit.test_instantiate.ListContainer",
            "items": [
                {"_target_": "tests.unit.test_instantiate.SimpleClass", "name": "Item1", "value": 1},
                {"_target_": "tests.unit.test_instantiate.SimpleClass", "name": "Item2", "value": 2},
                "regular_string",
                42,
            ],
        }

        result = instantiate(config)

        assert len(result.items) == 4
        assert isinstance(result.items[0], SimpleClass)
        assert result.items[0].name == "Item1"
        assert isinstance(result.items[1], SimpleClass)
        assert result.items[2] == "regular_string"
        assert result.items[3] == 42


class TestDependencyInjection:
    """Test dependency injection functionality."""

    def test_register_dependency_by_name(self) -> None:
        """Verify dependency registration by parameter name.

        Tests
        -----
        Dependencies registered by name are injected into matching parameters.
        """
        mock_db = Mock()
        mock_db.type = "database"
        mock_logger = Mock()
        mock_logger.type = "logger"

        register_dependency("database", mock_db)
        register_dependency("logger", mock_logger)

        config = {
            "_target_": "tests.unit.test_instantiate.ComplexClass",
            "name": "WithDependencies",
        }

        result = instantiate(config)

        assert result.database is mock_db
        assert result.logger is mock_logger
        assert result.name == "WithDependencies"

    def test_register_dependency_by_type(self) -> None:
        """Verify dependency registration by type.

        Tests
        -----
        Dependencies registered by type are injected based on type annotations.
        """

        db_instance = Database()
        logger_instance = Logger()

        register_dependency(Database, db_instance)
        register_dependency(Logger, logger_instance)

        config = {"_target_": "tests.unit.test_instantiate.TypedClass"}

        result = instantiate(config)

        assert result.db is db_instance
        assert result.log is logger_instance

    def test_config_overrides_dependency(self) -> None:
        """Verify explicit config values override injected dependencies.

        Tests
        -----
        Configuration takes precedence over dependency injection.
        """
        mock_db = Mock()
        mock_db.type = "injected"
        register_dependency("database", mock_db)

        config_db = Mock()
        config_db.type = "configured"

        config = {
            "_target_": "tests.unit.test_instantiate.ComplexClass",
            "name": "OverrideTest",
            "database": config_db,
            "logger": Mock(),
        }

        result = instantiate(config)

        assert result.database is config_db
        assert result.database.type == "configured"

    def test_dependency_not_injected_for_optional_params(self) -> None:
        """Verify dependencies are injected for optional parameters when registered by name.

        Tests
        -----
        Parameters with default values get name-based injection.
        """
        mock_cache = Mock()
        register_dependency("cache", mock_cache)

        config = {
            "_target_": "tests.unit.test_instantiate.ComplexClass",
            "name": "OptionalTest",
            "database": Mock(),
            "logger": Mock(),
        }

        result = instantiate(config)

        # cache has a default value but is registered by name, so it should be injected
        assert result.cache is mock_cache

    def test_clear_dependencies(self) -> None:
        """Verify clear_dependencies removes all registered dependencies.

        Tests
        -----
        Dependency stores are properly cleared.
        """
        register_dependency("test1", Mock())
        register_dependency(str, "test_string")

        type_deps, name_deps = get_registered_dependencies()
        assert len(type_deps) > 0 or len(name_deps) > 0

        clear_dependencies()

        type_deps, name_deps = get_registered_dependencies()
        assert len(type_deps) == 0
        assert len(name_deps) == 0


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_target_format_error(self) -> None:
        """Verify proper error for invalid target format.

        Tests
        -----
        Clear error message for malformed target strings.
        """
        config = {"_target_": "NoDotsHere"}

        with pytest.raises(InstantiationError) as exc_info:
            instantiate(config)

        assert "Invalid target format" in str(exc_info.value)

    def test_module_not_found_error(self) -> None:
        """Verify proper error when module doesn't exist.

        Tests
        -----
        Clear error message for non-existent modules.
        """
        config = {"_target_": "nonexistent.module.Class"}

        with pytest.raises(InstantiationError) as exc_info:
            instantiate(config)

        assert "Failed to import" in str(exc_info.value)
        assert "No module named" in str(exc_info.value)

    def test_class_not_found_error(self) -> None:
        """Verify proper error when class doesn't exist in module.

        Tests
        -----
        Clear error message for non-existent classes.
        """
        config = {"_target_": "builtins.NonExistentClass"}

        with pytest.raises(InstantiationError) as exc_info:
            instantiate(config)

        assert "Failed to import" in str(exc_info.value)

    def test_non_callable_target_error(self) -> None:
        """Verify proper error when target is not callable.

        Tests
        -----
        Clear error message when target cannot be instantiated.
        """
        # sys.path is a list, not callable
        config = {"_target_": "sys.path"}

        with pytest.raises(InstantiationError) as exc_info:
            instantiate(config)

        assert "not callable" in str(exc_info.value)

    def test_constructor_error_wrapped(self) -> None:
        """Verify constructor errors are wrapped in InstantiationError.

        Tests
        -----
        Original exception is preserved with additional context.
        """

        config = {"_target_": "tests.unit.test_instantiate.FailingClass"}

        with pytest.raises(InstantiationError) as exc_info:
            instantiate(config)

        assert "Failed to instantiate" in str(exc_info.value)
        assert exc_info.value.original_error is not None
        assert isinstance(exc_info.value.original_error, ValueError)

    def test_circular_dependency_detection(self) -> None:
        """Verify circular dependencies are detected and reported.

        Tests
        -----
        Clear error message showing the circular dependency chain.
        """
        config1 = {
            "_target_": "tests.unit.test_instantiate.SimpleClass",
            "name": "First",
            "value": {"_target_": "tests.unit.test_instantiate.SimpleClass", "name": "Second"},
        }

        # Simulate circular reference by patching
        with patch("frostbound.pydanticonf._instantiate._instantiation_stack") as mock_stack:
            mock_stack.get.return_value = ["tests.unit.test_instantiate.SimpleClass"]

            with pytest.raises(InstantiationError) as exc_info:
                instantiate(config1)

            assert "Circular dependency detected" in str(exc_info.value)


class TestTypesMatchFuzzy:
    """Test the fuzzy type matching function."""

    def test_exact_type_match(self) -> None:
        """Verify exact type identity returns True.

        Tests
        -----
        Same type object is recognized as matching.
        """
        assert _types_match_semantically(str, str) is True
        assert _types_match_semantically(int, int) is True

    def test_different_types_no_match(self) -> None:
        """Verify different types don't match.

        Tests
        -----
        Completely different types are not matched.
        """
        assert _types_match_semantically(str, int) is False
        assert _types_match_semantically(list, dict) is False

    def test_same_name_different_module_no_match(self) -> None:
        """Verify classes with same name from different modules don't match.

        Tests
        -----
        Prevents dangerous cross-module matching.
        """

        class Module1:
            class Connection:
                pass

        class Module2:
            class Connection:
                pass

        assert _types_match_semantically(Module1.Connection, Module2.Connection) is False

    def test_non_type_objects_no_match(self) -> None:
        """Verify non-type objects return False.

        Tests
        -----
        Function handles non-type inputs gracefully.
        """
        assert _types_match_semantically("string", str) is False
        assert _types_match_semantically(42, int) is False
        assert _types_match_semantically(str, "string") is False


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_instantiate_class_without_init(self) -> None:
        """Verify instantiation of classes without __init__ method.

        Tests
        -----
        Classes without explicit __init__ can still be instantiated.
        """
        config = {"_target_": "tests.unit.test_instantiate.NoInitClass"}

        result = instantiate(config)

        assert isinstance(result, NoInitClass)

    def test_instantiate_with_nested_dynamic_config(self) -> None:
        """Verify nested DynamicConfig objects are instantiated.

        Tests
        -----
        DynamicConfig instances in configuration are recursively instantiated.
        """
        nested_config = DynamicConfig[SimpleClass](
            _target_="tests.unit.test_instantiate.SimpleClass", name="Nested", value=999
        )

        config = {
            "_target_": "tests.unit.test_instantiate.ComplexClass",
            "name": "Parent",
            "database": nested_config,
            "logger": Mock(),
        }

        result = instantiate(config)

        assert isinstance(result.database, SimpleClass)
        assert result.database.name == "Nested"
        assert result.database.value == 999

    def test_instantiate_basemodel_with_target(self) -> None:
        """Verify instantiation from BaseModel with _target_ in model_dump.

        Tests
        -----
        Pydantic models with _target_ in their data are instantiated.
        """

        config = ConfigModel()
        result = instantiate(config)

        assert isinstance(result, SimpleClass)
        assert result.name == "FromModel"
        assert result.value == 777

    @pytest.mark.parametrize(
        ("args", "kwargs", "expected_name", "expected_value"),
        [
            (["ArgsOnly"], {}, "ArgsOnly", 42),
            (["ArgName"], {"value": 100}, "ArgName", 100),
            ([], {"name": "KwargsOnly", "value": 200}, "KwargsOnly", 200),
        ],
    )
    def test_instantiate_mixed_args_kwargs(
        self, args: list[Any], kwargs: dict[str, Any], expected_name: str, expected_value: int
    ) -> None:
        """Verify instantiation with various combinations of args and kwargs.

        Parameters
        ----------
        args : list[Any]
            Positional arguments to pass.
        kwargs : dict[str, Any]
            Keyword arguments to pass.
        expected_name : str
            Expected name attribute of result.
        expected_value : int
            Expected value attribute of result.

        Tests
        -----
        Flexible argument passing with both positional and keyword arguments.
        """
        config = {
            "_target_": "tests.unit.test_instantiate.SimpleClass",
            "_args_": args,
            **kwargs,
        }

        result = instantiate(config)

        assert result.name == expected_name
        assert result.value == expected_value
