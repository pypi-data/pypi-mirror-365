"""
Demo 03: YAML Configuration Loading
===================================

Loading configuration from YAML files with BaseSettingsWithInstantiation.

Key concepts:
- Loading settings from YAML files
- BaseSettingsWithInstantiation class
- Combining multiple configuration sources
- Structured configuration management
"""

import sys
from pathlib import Path

from pydantic import Field
from pydantic_settings import SettingsConfigDict
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree

sys.path.insert(0, str(Path(__file__).parent.parent))

from frostbound.pydanticonf import BaseSettingsWithInstantiation, DynamicConfig

console = Console()


# Domain classes
class Logger:
    """A simple logger."""

    def __init__(self, name: str, level: str = "INFO", format: str = "json"):
        self.name = name
        self.level = level
        self.format = format

    def log(self, message: str):
        return f"[{self.level}] {self.name}: {message}"

    def __repr__(self):
        return f"Logger(name={self.name}, level={self.level}, format={self.format})"


class Cache:
    """A cache service."""

    def __init__(self, backend: str = "memory", ttl: int = 3600, max_size: int = 1000):
        self.backend = backend
        self.ttl = ttl
        self.max_size = max_size

    def __repr__(self):
        return f"Cache(backend={self.backend}, ttl={self.ttl}s, max_size={self.max_size})"


# Configuration models
class LoggerConfig(DynamicConfig[Logger]):
    """Logger configuration."""

    target_: str = Field(default="__main__.Logger", alias="_target_")
    name: str = "app"
    level: str = "INFO"
    format: str = "json"


class CacheConfig(DynamicConfig[Cache]):
    """Cache configuration."""

    target_: str = Field(default="__main__.Cache", alias="_target_")
    backend: str = "memory"
    ttl: int = 3600
    max_size: int = 1000


# Settings class that loads from YAML
class AppSettings(BaseSettingsWithInstantiation):
    """Application settings loaded from YAML."""

    model_config = SettingsConfigDict(
        yaml_file=str(Path(__file__).parent / "config" / "03_yaml_loading.yaml"),
        env_prefix="APP_",
    )

    # Configuration fields
    app_name: str = "MyApp"
    debug: bool = False
    version: str = "1.0.0"

    # DynamicConfig fields that can be instantiated
    logger: LoggerConfig
    cache: CacheConfig

    # Additional services loaded from YAML
    services: dict[str, dict] = {}


def main():
    """Run the YAML loading demo."""
    console.print(
        Panel.fit(
            "📄 YAML Configuration Loading\n\n"
            "Professional configuration management:\n"
            "• Load settings from YAML files\n"
            "• Structured configuration\n"
            "• Type validation\n"
            "• Automatic instantiation support\n\n"
            "Perfect for real applications!",
            title="Demo 03: YAML Loading",
            style="bold blue",
        )
    )

    # Load settings from YAML
    console.print("\n📄 Loading configuration from YAML...")
    settings = AppSettings()

    # Display loaded configuration
    console.print("\n🔍 Loaded configuration:")

    config_tree = Tree("AppSettings")
    config_tree.add(f"app_name: [yellow]{settings.app_name}[/yellow]")
    config_tree.add(f"debug: [yellow]{settings.debug}[/yellow]")
    config_tree.add(f"version: [yellow]{settings.version}[/yellow]")

    logger_branch = config_tree.add("logger: [cyan]LoggerConfig[/cyan]")
    logger_branch.add(f"name: {settings.logger.name}")
    logger_branch.add(f"level: {settings.logger.level}")
    logger_branch.add(f"format: {settings.logger.format}")

    cache_branch = config_tree.add("cache: [cyan]CacheConfig[/cyan]")
    cache_branch.add(f"backend: {settings.cache.backend}")
    cache_branch.add(f"ttl: {settings.cache.ttl}")
    cache_branch.add(f"max_size: {settings.cache.max_size}")

    console.print(config_tree)

    # Example 1: Access configuration values
    console.print("\n📦 Example 1: Accessing configuration")
    console.print(f"App name: {settings.app_name}")
    console.print(f"Debug mode: {settings.debug}")
    console.print(f"Logger config type: {type(settings.logger).__name__}")

    # Example 2: Instantiate services
    console.print("\n📦 Example 2: Instantiating services")

    # Note: with auto_instantiate=True (default), these would already be instances!
    # We're using lazy mode here for demonstration
    logger = settings.instantiate_field("logger")
    console.print(f"Logger instance: {logger}")
    console.print(f"Test log: {logger.log('Configuration loaded')}")

    cache = settings.instantiate_field("cache")
    console.print(f"Cache instance: {cache}")

    # Example 3: Override at instantiation
    console.print("\n📦 Example 3: Runtime overrides")

    debug_logger = settings.instantiate_field("logger", level="DEBUG", name="debug_app")
    console.print(f"Debug logger: {debug_logger}")
    console.print(f"Test log: {debug_logger.log('Debug mode active')}")

    # Example 4: Additional services from YAML
    console.print("\n📦 Example 4: Dynamic services from YAML")
    if settings.services:
        for service_name, service_config in settings.services.items():
            console.print(f"Found service config: {service_name}")
            console.print(f"  Config: {service_config}")

    # Summary
    console.print(
        Panel.fit(
            "✅ Key Takeaways:\n\n"
            "1. BaseSettingsWithInstantiation loads from YAML\n"
            "2. Supports all Pydantic validation\n"
            "3. Can mix regular fields and DynamicConfig\n"
            "4. Flexible instantiation options\n"
            "5. Professional configuration management\n\n"
            "Next: Learn about environment variables →",
            title="Summary",
            style="bold green",
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        console.print(f"\n[bold red]❌ Error:[/bold red] {e}")
        import traceback

        console.print("[red]" + traceback.format_exc() + "[/red]")
        sys.exit(1)
