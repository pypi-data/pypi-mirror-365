"""Unit tests for the DynamicConfig base class.

This module tests the core DynamicConfig functionality including:
- Type-safe configuration models
- Automatic target inference
- Field validation and processing
- Special field handling (_target_, _args_, etc.)
"""

from typing import Any

import pytest
from pydantic import ValidationError

from frostbound.pydanticonf.base import DynamicConfig


class MockDatabase:
    """Mock database class for testing."""

    def __init__(self, host: str, port: int = 5432) -> None:
        self.host = host
        self.port = port


class DatabaseConfig(DynamicConfig[MockDatabase]):
    """Type-safe configuration for MockDatabase."""

    host: str = "localhost"
    port: int = 5432


class TestDynamicConfigBasics:
    """Test basic DynamicConfig functionality."""

    def test_dynamic_config_creation_with_explicit_target(self) -> None:
        """Verify DynamicConfig can be created with explicit _target_.

        Tests
        -----
        Creation of a DynamicConfig instance with all required fields
        and verification of field access.
        """
        config = DynamicConfig[Any](_target_="tests.unit.test_base.MockDatabase", host="test.db", port=3306)

        assert config.target_ == "tests.unit.test_base.MockDatabase"
        assert config.args_ is None
        assert config.partial_ is False
        assert config.recursive_ is True

    def test_dynamic_config_with_positional_args(self) -> None:
        """Verify _args_ field is properly handled.

        Tests
        -----
        Configuration with positional arguments specified via _args_.
        """
        config = DynamicConfig[Any](_target_="builtins.dict", _args_=[("key1", "value1"), ("key2", "value2")])

        assert config.target_ == "builtins.dict"
        assert config.args_ == (("key1", "value1"), ("key2", "value2"))

    def test_dynamic_config_partial_flag(self) -> None:
        """Verify _partial_ flag configuration.

        Tests
        -----
        Setting partial instantiation flag.
        """
        config = DynamicConfig[Any](_target_="tests.unit.test_base.MockDatabase", _partial_=True, host="test.db")

        assert config.partial_ is True

    def test_dynamic_config_recursive_flag(self) -> None:
        """Verify _recursive_ flag configuration.

        Tests
        -----
        Disabling recursive instantiation.
        """
        config = DynamicConfig[Any](
            _target_="tests.unit.test_base.MockDatabase",
            _recursive_=False,
            host="test.db",
        )

        assert config.recursive_ is False

    def test_dynamic_config_missing_target_raises_error(self) -> None:
        """Verify ValidationError when _target_ is missing.

        Tests
        -----
        Proper validation error when required _target_ field is not provided.
        """
        with pytest.raises(ValidationError) as exc_info:
            DynamicConfig[Any](host="test.db", port=5432)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("target_",) for error in errors)

    def test_dynamic_config_empty_target_raises_error(self) -> None:
        """Verify ValidationError when _target_ is empty string.

        Tests
        -----
        Validation of minimum length constraint on _target_ field.
        """
        with pytest.raises(ValidationError) as exc_info:
            DynamicConfig[Any](_target_="", host="test.db")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("target_",) and "at least 1 character" in str(error) for error in errors)


class TestDynamicConfigTargetInference:
    """Test automatic target inference from generic types."""

    def test_target_inference_from_concrete_type(self) -> None:
        """Verify target is inferred from generic type parameter.

        Tests
        -----
        Automatic _target_ inference when using concrete class as generic parameter.
        """
        config = DatabaseConfig(host="prod.db", port=3306)

        assert config.target_ == "tests.unit.test_base.MockDatabase"
        assert config.host == "prod.db"
        assert config.port == 3306

    def test_target_inference_with_explicit_override(self) -> None:
        """Verify explicit _target_ overrides inference.

        Tests
        -----
        When _target_ is explicitly provided, it takes precedence over inference.
        """
        config = DatabaseConfig(_target_="some.other.Database", host="test.db", port=5432)

        assert config.target_ == "some.other.Database"

    def test_target_inference_with_forward_ref_requires_explicit(self) -> None:
        """Verify forward references require explicit _target_.

        Tests
        -----
        Target inference fails gracefully for forward references.
        """

        class ForwardRefConfig(DynamicConfig["SomeForwardRef"]):  # type: ignore[type-arg]
            value: str = "test"

        with pytest.raises(ValidationError) as exc_info:
            ForwardRefConfig(value="test")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("target_",) for error in errors)


class TestDynamicConfigMethods:
    """Test DynamicConfig methods and utilities."""

    def test_get_module_and_class_name_valid(self) -> None:
        """Verify module and class name extraction for valid targets.

        Tests
        -----
        Correct parsing of fully qualified class paths.
        """
        config = DynamicConfig[Any](_target_="myapp.models.Database")
        module_path, class_name = config.get_module_and_class_name()

        assert module_path == "myapp.models"
        assert class_name == "Database"

    def test_get_module_and_class_name_nested(self) -> None:
        """Verify extraction works with deeply nested modules.

        Tests
        -----
        Handling of complex module paths.
        """
        config = DynamicConfig[Any](_target_="a.b.c.d.e.ClassName")
        module_path, class_name = config.get_module_and_class_name()

        assert module_path == "a.b.c.d.e"
        assert class_name == "ClassName"

    @pytest.mark.parametrize(
        "invalid_target",
        [
            "NoDotsHere",
            ".LeadingDot",
            "TrailingDot.",
            "",
        ],
    )
    def test_get_module_and_class_name_invalid_format(self, invalid_target: str) -> None:
        """Verify error handling for invalid target formats.

        Parameters
        ----------
        invalid_target : str
            Invalid target string to test.

        Tests
        -----
        Proper error messages for various invalid formats.
        """
        if invalid_target == "":
            # Empty target won't pass validation
            return

        config = DynamicConfig[Any](_target_=invalid_target)
        with pytest.raises(ValueError, match="Invalid target format"):
            config.get_module_and_class_name()

    def test_get_init_kwargs_excludes_control_fields(self) -> None:
        """Verify get_init_kwargs excludes control fields.

        Tests
        -----
        Control fields (_target_, _args_, etc.) are not included in kwargs.
        """
        config = DynamicConfig[Any](
            _target_="test.Class",
            _args_=[1, 2, 3],
            _partial_=True,
            _recursive_=False,
            host="localhost",
            port=5432,
            timeout=30,
        )

        kwargs = config.get_init_kwargs()

        assert "target_" not in kwargs
        assert "args_" not in kwargs
        assert "partial_" not in kwargs
        assert "recursive_" not in kwargs
        assert kwargs == {"host": "localhost", "port": 5432, "timeout": 30}


class TestDynamicConfigExtraFields:
    """Test DynamicConfig with extra fields allowed."""

    def test_extra_fields_are_preserved(self) -> None:
        """Verify extra fields are preserved in configuration.

        Tests
        -----
        Extra fields beyond defined schema are kept and accessible.
        """
        config = DynamicConfig[Any](
            _target_="test.Class",
            defined_field="value",
            extra_field1="extra1",
            extra_field2="extra2",
        )

        assert hasattr(config, "extra_field1")
        assert hasattr(config, "extra_field2")
        assert config.extra_field1 == "extra1"  # type: ignore[attr-defined]
        assert config.extra_field2 == "extra2"  # type: ignore[attr-defined]

    def test_extra_fields_in_init_kwargs(self) -> None:
        """Verify extra fields are included in init kwargs.

        Tests
        -----
        Extra fields are passed to target constructor.
        """
        config = DynamicConfig[Any](
            _target_="test.Class",
            standard_param="value",
            extra_param="extra",
            another_extra=123,
        )

        kwargs = config.get_init_kwargs()

        assert "standard_param" in kwargs
        assert "extra_param" in kwargs
        assert "another_extra" in kwargs
        assert kwargs["another_extra"] == 123


class TestDynamicConfigSerialization:
    """Test DynamicConfig serialization and representation."""

    def test_model_dump_includes_all_fields(self) -> None:
        """Verify model_dump includes all configuration fields.

        Tests
        -----
        Serialization includes both standard and control fields.
        """
        config = DynamicConfig[Any](_target_="test.Class", _args_=[1, 2], host="localhost", port=5432)

        dumped = config.model_dump()

        assert dumped["target_"] == "test.Class"
        assert dumped["args_"] == [1, 2]
        assert dumped["partial_"] is False
        assert dumped["recursive_"] is True
        assert dumped["host"] == "localhost"
        assert dumped["port"] == 5432

    def test_model_dump_by_alias(self) -> None:
        """Verify model_dump with by_alias uses field aliases.

        Tests
        -----
        Serialization with aliases uses underscore prefix convention.
        """
        config = DynamicConfig[Any](_target_="test.Class", value="test")

        dumped = config.model_dump(by_alias=True)

        assert "_target_" in dumped
        assert "target_" not in dumped
        assert dumped["_target_"] == "test.Class"


class TestDynamicConfigEdgeCases:
    """Test edge cases and error conditions."""

    def test_string_strip_whitespace(self) -> None:
        """Verify string fields have whitespace stripped.

        Tests
        -----
        Configuration's str_strip_whitespace setting is applied.
        """
        config = DynamicConfig[Any](
            _target_="  test.Class  ",
            string_field="  value  ",  # type: ignore[arg-type]
        )

        assert config.target_ == "test.Class"
        assert config.string_field == "value"  # type: ignore[attr-defined]

    def test_nested_dynamic_config_as_field(self) -> None:
        """Verify DynamicConfig can contain nested DynamicConfig fields.

        Tests
        -----
        Nested configuration objects are properly handled.
        """
        nested_config = DynamicConfig[Any](_target_="nested.Class", param="value")

        parent_config = DynamicConfig[Any](_target_="parent.Class", nested=nested_config, name="parent")

        assert parent_config.nested == nested_config  # type: ignore[attr-defined]
        assert parent_config.nested.target_ == "nested.Class"  # type: ignore[attr-defined]

    def test_complex_generic_type_inference(self) -> None:
        """Verify inference with complex generic scenarios.

        Tests
        -----
        Edge cases in type inference that should fall back to explicit _target_.
        """
        from typing import Generic, TypeVar

        T = TypeVar("T")

        class ComplexGeneric(Generic[T]):
            pass

        class ComplexConfig(DynamicConfig[ComplexGeneric[str]]):
            value: str = "test"

        # Should require explicit _target_ since inference is complex
        with pytest.raises(ValidationError):
            ComplexConfig(value="test")
