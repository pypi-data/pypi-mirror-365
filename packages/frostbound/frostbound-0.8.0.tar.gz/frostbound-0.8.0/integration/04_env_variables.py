"""
Demo 04: Environment Variables
==============================

Using environment variables and .env files for configuration.

Key concepts:
- Loading from .env files
- Environment variable overrides
- Nested environment variables (e.g., APP_DATABASE__HOST)
- Secrets management
"""

import os
import sys
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import SettingsConfigDict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

sys.path.insert(0, str(Path(__file__).parent.parent))

from frostbound.pydanticonf import BaseSettingsWithInstantiation, DynamicConfig

console = Console()


# Domain classes
class Database:
    """Database connection with credentials."""

    def __init__(self, host: str, port: int, username: str, password: str, database: str = "app_db"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database

    def get_connection_string(self):
        # Hide password in connection string
        return f"postgresql://{self.username}:***@{self.host}:{self.port}/{self.database}"

    def __repr__(self):
        return f"Database({self.get_connection_string()})"


class APIClient:
    """API client with authentication."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout

    def __repr__(self):
        # Hide API key
        masked_key = f"{self.api_key[:4]}..." if len(self.api_key) > 4 else "***"
        return f"APIClient(url={self.base_url}, key={masked_key})"


# Configuration models
class DatabaseConfig(DynamicConfig[Database]):
    """Database configuration with environment override support."""

    target_: str = Field(default="__main__.Database", alias="_target_")
    host: str = "localhost"
    port: int = 5432
    username: str = "user"
    password: SecretStr = SecretStr("")  # Secure password handling
    database: str = "app_db"


class APIConfig(DynamicConfig[APIClient]):
    """API client configuration."""

    target_: str = Field(default="__main__.APIClient", alias="_target_")
    base_url: str = "https://api.example.com"
    api_key: SecretStr = SecretStr("default-key")
    timeout: int = 30


# Settings with environment support
class Settings(BaseSettingsWithInstantiation):
    """Settings with environment variable support."""

    model_config = SettingsConfigDict(
        # Load from both YAML and .env file
        yaml_file=str(Path(__file__).parent / "config" / "04_env_variables.yaml"),
        env_file=str(Path(__file__).parent / "envs" / ".env.04_env_variables"),
        env_prefix="APP_",
        env_nested_delimiter="__",  # Allows APP_DATABASE__HOST syntax
        case_sensitive=False,
    )

    # Basic settings
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # Service configurations
    database: DatabaseConfig
    api: APIConfig


def main():
    """Run the environment variables demo."""
    console.print(
        Panel.fit(
            "🌍 Environment Variables & .env Files\n\n"
            "Flexible configuration sources:\n"
            "• Load from .env files\n"
            "• Override with environment variables\n"
            "• Nested variable support (DB__HOST)\n"
            "• Secure secrets handling\n\n"
            "Production-ready configuration!",
            title="Demo 04: Environment Variables",
            style="bold blue",
        )
    )

    # Show current environment
    console.print("\n🌍 Environment Setup:")
    console.print(f"Current environment: {os.getenv('APP_ENVIRONMENT', 'not set')}")
    console.print(f"Working directory: {Path.cwd()}")

    # Load settings
    console.print("\n📄 Loading configuration...")
    settings = Settings()

    # Display configuration sources
    console.print("\n🔍 Configuration values and sources:")

    config_table = Table(show_header=True, header_style="bold magenta")
    config_table.add_column("Setting", style="cyan", no_wrap=True)
    config_table.add_column("Value", style="green")
    config_table.add_column("Source", style="yellow")

    # Basic settings
    config_table.add_row("environment", settings.environment, "YAML or .env")
    config_table.add_row("debug", str(settings.debug), "YAML or .env")
    config_table.add_row("log_level", settings.log_level, "YAML or .env")

    # Database settings
    config_table.add_row("database.host", settings.database.host, "Check .env file")
    config_table.add_row("database.port", str(settings.database.port), "Default or override")
    config_table.add_row("database.username", settings.database.username, "Config file")
    config_table.add_row("database.password", "***hidden***", "SecretStr from .env")

    # API settings
    config_table.add_row("api.base_url", settings.api.base_url, "Config file")
    config_table.add_row("api.api_key", "***hidden***", "SecretStr from .env")

    console.print(config_table)

    # Example 1: Override with environment variable
    console.print("\n📦 Example 1: Environment variable override")

    # Set an environment variable
    os.environ["APP_LOG_LEVEL"] = "DEBUG"
    os.environ["APP_DATABASE__HOST"] = "prod.database.server"

    # Reload settings
    overridden_settings = Settings()
    console.print(f"Original log_level: {settings.log_level}")
    console.print(f"Overridden log_level: {overridden_settings.log_level}")
    console.print(f"Original database.host: {settings.database.host}")
    console.print(f"Overridden database.host: {overridden_settings.database.host}")

    # Example 2: Instantiate with secrets
    console.print("\n📦 Example 2: Using secure configurations")

    database = overridden_settings.instantiate_field("database")
    console.print(f"Database instance: {database}")
    console.print(f"Connection string: {database.get_connection_string()}")

    api_client = overridden_settings.instantiate_field("api")
    console.print(f"API client: {api_client}")

    # Example 3: Show precedence
    console.print("\n📦 Example 3: Configuration precedence")
    console.print("Priority order (highest to lowest):")
    console.print("1. Environment variables (APP_*)")
    console.print("2. .env file")
    console.print("3. YAML configuration file")
    console.print("4. Default values in code")

    # Clean up
    if "APP_LOG_LEVEL" in os.environ:
        del os.environ["APP_LOG_LEVEL"]
    if "APP_DATABASE__HOST" in os.environ:
        del os.environ["APP_DATABASE__HOST"]

    # Summary
    console.print(
        Panel.fit(
            "✅ Key Takeaways:\n\n"
            "1. Use .env files for local development\n"
            "2. Override with environment variables in production\n"
            "3. Nested variables with __ delimiter\n"
            "4. SecretStr for sensitive data\n"
            "5. Clear precedence rules\n\n"
            "Next: Understanding configuration precedence →",
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
