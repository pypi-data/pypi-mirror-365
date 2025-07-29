"""Unit tests for utility functions.

This module tests the utility functions provided by pydanticonf,
particularly the deep_merge function.
"""

from typing import Any

import pytest

from frostbound.pydanticonf.utils import deep_merge


class TestDeepMerge:
    """Test the deep_merge utility function."""

    def test_deep_merge_simple_dicts(self) -> None:
        """Verify basic dictionary merging.

        Tests
        -----
        Non-overlapping keys are combined from both dictionaries.
        """
        base = {"a": 1, "b": 2}
        override = {"c": 3, "d": 4}

        result = deep_merge(base, override)

        assert result == {"a": 1, "b": 2, "c": 3, "d": 4}

    def test_deep_merge_override_precedence(self) -> None:
        """Verify override values take precedence.

        Tests
        -----
        When keys conflict, override dictionary values win.
        """
        base = {"a": 1, "b": 2, "c": 3}
        override = {"b": 20, "c": 30, "d": 40}

        result = deep_merge(base, override)

        assert result == {"a": 1, "b": 20, "c": 30, "d": 40}

    def test_deep_merge_nested_dicts(self) -> None:
        """Verify recursive merging of nested dictionaries.

        Tests
        -----
        Nested dictionaries are merged recursively, not replaced.
        """
        base = {"config": {"host": "localhost", "port": 5432, "timeout": 30}}
        override = {"config": {"port": 3306, "ssl": True}}

        result = deep_merge(base, override)

        assert result == {"config": {"host": "localhost", "port": 3306, "timeout": 30, "ssl": True}}

    def test_deep_merge_deeply_nested(self) -> None:
        """Verify merging of deeply nested structures.

        Tests
        -----
        Multiple levels of nesting are handled correctly.
        """
        base = {
            "level1": {
                "level2": {"level3": {"a": 1, "b": 2}, "x": 10},
                "y": 20,
            }
        }
        override = {"level1": {"level2": {"level3": {"b": 200, "c": 300}}}}

        result = deep_merge(base, override)

        assert result == {
            "level1": {
                "level2": {"level3": {"a": 1, "b": 200, "c": 300}, "x": 10},
                "y": 20,
            }
        }

    def test_deep_merge_override_with_non_dict(self) -> None:
        """Verify non-dict values replace entire dict values.

        Tests
        -----
        When override has non-dict value for a key with dict in base.
        """
        base = {"config": {"host": "localhost", "port": 5432}}
        override = {"config": "simple_string"}

        result = deep_merge(base, override)

        assert result == {"config": "simple_string"}

    def test_deep_merge_base_non_dict_replaced(self) -> None:
        """Verify dict values replace non-dict values.

        Tests
        -----
        When base has non-dict value and override has dict.
        """
        base = {"config": "simple_string"}
        override = {"config": {"host": "localhost", "port": 5432}}

        result = deep_merge(base, override)

        assert result == {"config": {"host": "localhost", "port": 5432}}

    def test_deep_merge_empty_dicts(self) -> None:
        """Verify handling of empty dictionaries.

        Tests
        -----
        Empty dictionaries are handled correctly.
        """
        # Empty base
        result1 = deep_merge({}, {"a": 1})
        assert result1 == {"a": 1}

        # Empty override
        result2 = deep_merge({"a": 1}, {})
        assert result2 == {"a": 1}

        # Both empty
        result3 = deep_merge({}, {})
        assert result3 == {}

    def test_deep_merge_none_values(self) -> None:
        """Verify None values in override replace existing values.

        Tests
        -----
        None is a valid override value, not ignored.
        """
        base = {"a": 1, "b": 2, "c": {"x": 10}}
        override = {"b": None, "c": None}

        result = deep_merge(base, override)

        assert result == {"a": 1, "b": None, "c": None}

    def test_deep_merge_does_not_modify_inputs(self) -> None:
        """Verify input dictionaries are not modified.

        Tests
        -----
        Deep merge creates new dictionary without modifying inputs.
        """
        base = {"a": 1, "b": {"x": 10}}
        override = {"b": {"y": 20}, "c": 3}

        base_copy = base.copy()
        override_copy = override.copy()

        result = deep_merge(base, override)

        # Verify inputs unchanged
        assert base == base_copy
        assert override == override_copy
        # Verify result is correct
        assert result == {"a": 1, "b": {"x": 10, "y": 20}, "c": 3}

    def test_deep_merge_list_values(self) -> None:
        """Verify list values are replaced, not merged.

        Tests
        -----
        Lists are treated as atomic values, not merged.
        """
        base = {"items": [1, 2, 3], "config": {"values": ["a", "b"]}}
        override = {"items": [4, 5], "config": {"values": ["c", "d", "e"]}}

        result = deep_merge(base, override)

        assert result == {"items": [4, 5], "config": {"values": ["c", "d", "e"]}}

    def test_deep_merge_mixed_types(self) -> None:
        """Verify handling of mixed value types.

        Tests
        -----
        Various Python types are handled correctly.
        """
        base = {
            "string": "hello",
            "number": 42,
            "float": 3.14,
            "bool": True,
            "list": [1, 2, 3],
            "dict": {"nested": True},
            "none": None,
        }
        override = {
            "string": "world",
            "number": 100,
            "new_key": "new_value",
            "dict": {"nested": False, "extra": "data"},
        }

        result = deep_merge(base, override)

        assert result == {
            "string": "world",
            "number": 100,
            "float": 3.14,
            "bool": True,
            "list": [1, 2, 3],
            "dict": {"nested": False, "extra": "data"},
            "none": None,
            "new_key": "new_value",
        }

    @pytest.mark.parametrize(
        ("base", "override", "expected"),
        [
            # Simple cases
            ({"a": 1}, {"b": 2}, {"a": 1, "b": 2}),
            ({"a": 1}, {"a": 2}, {"a": 2}),
            # Nested cases
            (
                {"x": {"y": 1}},
                {"x": {"z": 2}},
                {"x": {"y": 1, "z": 2}},
            ),
            # Type replacement
            ({"x": [1, 2]}, {"x": {"a": 1}}, {"x": {"a": 1}}),
            ({"x": "string"}, {"x": 123}, {"x": 123}),
            # Empty nested dicts
            ({"x": {"y": 1}}, {"x": {}}, {"x": {"y": 1}}),
            ({"x": {}}, {"x": {"y": 1}}, {"x": {"y": 1}}),
        ],
    )
    def test_deep_merge_parametrized(
        self,
        base: dict[str, Any],
        override: dict[str, Any],
        expected: dict[str, Any],
    ) -> None:
        """Verify various merge scenarios with parametrized tests.

        Parameters
        ----------
        base : dict[str, Any]
            Base dictionary.
        override : dict[str, Any]
            Override dictionary.
        expected : dict[str, Any]
            Expected merged result.

        Tests
        -----
        Comprehensive coverage of merge scenarios.
        """
        result = deep_merge(base, override)
        assert result == expected

    def test_deep_merge_complex_real_world_scenario(self) -> None:
        """Verify merging in a complex real-world configuration scenario.

        Tests
        -----
        Realistic configuration merging with multiple levels and types.
        """
        base_config = {
            "app": {
                "name": "MyApp",
                "version": "1.0.0",
                "debug": False,
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "credentials": {"username": "user", "password": "pass"},
                "options": {
                    "pool_size": 10,
                    "timeout": 30,
                    "retry": {"attempts": 3, "delay": 1},
                },
            },
            "features": {
                "auth": True,
                "api": True,
                "admin": False,
            },
            "servers": ["server1", "server2"],
        }

        prod_overrides = {
            "app": {"debug": False, "environment": "production"},
            "database": {
                "host": "prod.db.server",
                "credentials": {"username": "prod_user", "password": "prod_pass"},
                "options": {
                    "pool_size": 50,
                    "ssl": True,
                    "retry": {"attempts": 5},
                },
            },
            "features": {"admin": True, "monitoring": True},
            "servers": ["prod1", "prod2", "prod3"],
        }

        result = deep_merge(base_config, prod_overrides)

        expected = {
            "app": {
                "name": "MyApp",
                "version": "1.0.0",
                "debug": False,
                "environment": "production",
            },
            "database": {
                "host": "prod.db.server",
                "port": 5432,
                "credentials": {"username": "prod_user", "password": "prod_pass"},
                "options": {
                    "pool_size": 50,
                    "timeout": 30,
                    "ssl": True,
                    "retry": {"attempts": 5, "delay": 1},
                },
            },
            "features": {
                "auth": True,
                "api": True,
                "admin": True,
                "monitoring": True,
            },
            "servers": ["prod1", "prod2", "prod3"],
        }

        assert result == expected
