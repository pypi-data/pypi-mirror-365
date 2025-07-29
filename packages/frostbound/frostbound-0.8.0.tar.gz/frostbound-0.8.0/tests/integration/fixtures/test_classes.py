"""Test classes for integration testing with dynamic configuration.

This module provides test classes that are referenced in YAML configuration
files for integration testing of dynamic instantiation functionality.
"""

from __future__ import annotations

from typing import Any


class SimpleService:
    """A simple service class for testing."""

    def __init__(self, name: str, port: int = 8080):
        self.name = name
        self.port = port
        self.running = False

    def start(self) -> None:
        self.running = True


class DatabaseClient:
    """A database client class for testing dependency injection."""

    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connected = False

    def connect(self) -> None:
        self.connected = True


class ConfigurablePlugin:
    """A plugin class that accepts variable configuration."""

    def __init__(self, plugin_name: str, **options: Any):
        self.plugin_name = plugin_name
        self.options = options
        self.initialized = True


class NestedComponent:
    """A component that contains other components."""

    def __init__(self, name: str, sub_components: list[Any] | None = None):
        self.name = name
        self.sub_components = sub_components or []


class ServiceWithDependencies:
    """Service that accepts various injected dependencies."""

    def __init__(
        self,
        service_name: str,
        database: Any | None = None,
        cache: Any | None = None,
        logger: Any | None = None,
        config: dict | None = None,
        api_key: str | None = None,
        max_retries: int = 3,
        failing_dep: Any | None = None,
        db_client: Any | None = None,
        cache_client: Any | None = None,
        metrics_client: Any | None = None,
    ):
        self.service_name = service_name
        self.database = database
        self.cache = cache
        self.logger = logger
        self.config = config or {}
        self.api_key = api_key
        self.max_retries = max_retries
        self.failing_dep = failing_dep
        self.db_client = db_client
        self.cache_client = cache_client
        self.metrics_client = metrics_client
        self.initialized = True
