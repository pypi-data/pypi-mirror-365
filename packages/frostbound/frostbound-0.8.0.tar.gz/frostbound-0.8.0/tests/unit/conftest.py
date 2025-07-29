"""Shared fixtures for unit tests.

This module provides common fixtures and mocks used across unit tests
for the pydanticonf package.
"""

from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, Mock

import pytest
from pytest_mock import MockerFixture


@pytest.fixture
def mock_module(mocker: MockerFixture) -> MagicMock:
    """Mock module for testing dynamic imports.

    Parameters
    ----------
    mocker : MockerFixture
        The pytest-mock mocker fixture.

    Returns
    -------
    MagicMock
        A mock module with configurable attributes.
    """
    return mocker.MagicMock(spec=["TestClass", "TestFunction"])


@pytest.fixture
def simple_class() -> type[Any]:
    """A simple test class for instantiation tests.

    Returns
    -------
    type[Any]
        A basic class with simple constructor.
    """

    class SimpleClass:
        def __init__(self, name: str, value: int = 42) -> None:
            self.name = name
            self.value = value

    return SimpleClass


@pytest.fixture
def complex_class() -> type[Any]:
    """A complex test class with dependencies for injection tests.

    Returns
    -------
    type[Any]
        A class with multiple dependencies in constructor.
    """

    class ComplexClass:
        def __init__(self, name: str, database: Any, logger: Any, cache: Any | None = None) -> None:
            self.name = name
            self.database = database
            self.logger = logger
            self.cache = cache

    return ComplexClass


@pytest.fixture
def mock_database() -> Mock:
    """Mock database instance for dependency injection tests.

    Returns
    -------
    Mock
        A mock database object.
    """
    db = Mock()
    db.host = "test.db"
    db.port = 5432
    return db


@pytest.fixture
def mock_logger() -> Mock:
    """Mock logger instance for dependency injection tests.

    Returns
    -------
    Mock
        A mock logger object.
    """
    logger = Mock()
    logger.level = "INFO"
    return logger


@pytest.fixture
def mock_cache() -> Mock:
    """Mock cache instance for dependency injection tests.

    Returns
    -------
    Mock
        A mock cache object.
    """
    cache = Mock()
    cache.ttl = 3600
    return cache


@pytest.fixture(autouse=True)
def clean_dependencies() -> Generator[None]:
    """Automatically clean up dependencies after each test.

    This fixture ensures that the global dependency stores are
    cleared after each test to prevent test pollution.

    Yields
    ------
    None
        Control returns to test after setup.
    """
    yield
    # Clean up after test
    from frostbound.pydanticonf._instantiate import clear_dependencies

    clear_dependencies()


@pytest.fixture
def sample_yaml_content() -> str:
    """Sample YAML content for configuration tests.

    Returns
    -------
    str
        A YAML string with nested configuration.
    """
    return """
database:
  _target_: tests.mocks.MockDatabase
  host: localhost
  port: 5432

cache:
  _target_: tests.mocks.MockCache
  ttl: 3600

services:
  user_service:
    _target_: tests.mocks.MockService
    name: UserService
    database: ${database}
"""
