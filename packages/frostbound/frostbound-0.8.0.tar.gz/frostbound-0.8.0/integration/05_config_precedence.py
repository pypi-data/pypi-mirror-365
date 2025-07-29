"""
Demo 05: Configuration Precedence
=================================

Understanding how different configuration sources override each other.

Key concepts:
- Configuration source priority
- Override rules
- Debugging configuration values
- Best practices for different environments
"""

import os
import sys
from pathlib import Path

from pydantic import Field
from pydantic_settings import SettingsConfigDict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

sys.path.insert(0, str(Path(__file__).parent.parent))

from frostbound.pydanticonf import BaseSettingsWithInstantiation, DynamicConfig

console = Console()


# Simple service class
class Service:
    """A generic service."""

    def __init__(self, name: str, host: str, port: int, enabled: bool = True):
        self.name = name
        self.host = host
        self.port = port
        self.enabled = enabled

    def __repr__(self):
        status = "enabled" if self.enabled else "disabled"
        return f"Service({self.name} @ {self.host}:{self.port}, {status})"


# Configuration
class ServiceConfig(DynamicConfig[Service]):
    """Service configuration."""

    target_: str = Field(default="__main__.Service", alias="_target_")
    name: str = "default_service"
    host: str = "localhost"
    port: int = 8080
    enabled: bool = True


class Settings(BaseSettingsWithInstantiation):
    """Settings demonstrating precedence."""

    model_config = SettingsConfigDict(
        yaml_file=str(Path(__file__).parent / "config" / "05_precedence.yaml"),
        env_file=str(Path(__file__).parent / "envs" / ".env.05_precedence"),
        env_prefix="DEMO_",
        env_nested_delimiter="__",
    )

    # These will be set from different sources
    app_name: str = "DefaultApp"  # Default in code
    environment: str = "local"  # Default in code
    debug: bool = False  # Default in code
    timeout: int = 30  # Default in code

    # Service configuration
    service: ServiceConfig


def demonstrate_precedence():
    """Show configuration precedence in action."""
    console.print("\n🔍 Configuration Precedence Demonstration")

    # Track where each value comes from
    sources = {}

    # 1. Default values (lowest priority)
    console.print("\n1️⃣ Default values in code:")
    settings_defaults = Settings()
    sources["defaults"] = {
        "app_name": settings_defaults.app_name,
        "environment": settings_defaults.environment,
        "debug": settings_defaults.debug,
        "timeout": settings_defaults.timeout,
        "service.host": settings_defaults.service.host,
        "service.port": settings_defaults.service.port,
    }
    for key, value in sources["defaults"].items():
        console.print(f"   {key}: {value}")

    # 2. After YAML loading
    console.print("\n2️⃣ After YAML file loading (overrides defaults):")
    # YAML is already loaded in the Settings instance
    sources["yaml"] = {
        "app_name": settings_defaults.app_name,
        "environment": settings_defaults.environment,
        "debug": settings_defaults.debug,
        "timeout": settings_defaults.timeout,
        "service.host": settings_defaults.service.host,
        "service.port": settings_defaults.service.port,
    }

    # 3. After .env file
    console.print("\n3️⃣ After .env file loading (overrides YAML):")
    # .env is also already loaded
    sources["env_file"] = sources["yaml"].copy()

    # 4. Set environment variables (highest priority)
    console.print("\n4️⃣ Setting environment variables (highest priority):")
    os.environ["DEMO_APP_NAME"] = "EnvVarApp"
    os.environ["DEMO_DEBUG"] = "true"
    os.environ["DEMO_SERVICE__HOST"] = "production.server"
    os.environ["DEMO_SERVICE__PORT"] = "9000"

    # Create new instance to pick up env vars
    settings_with_env = Settings()
    sources["env_vars"] = {
        "app_name": settings_with_env.app_name,
        "environment": settings_with_env.environment,
        "debug": settings_with_env.debug,
        "timeout": settings_with_env.timeout,
        "service.host": settings_with_env.service.host,
        "service.port": settings_with_env.service.port,
    }

    # Display comparison table
    console.print("\n📊 Configuration Source Comparison:")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Default", style="dim")
    table.add_column("YAML", style="yellow")
    table.add_column(".env", style="green")
    table.add_column("Env Var", style="bold green")
    table.add_column("Final", style="bold white")

    # Compare each setting
    for key in ["app_name", "environment", "debug", "timeout", "service.host", "service.port"]:
        default_val = sources["defaults"][key]
        final_val = sources["env_vars"][key]

        # Highlight changes
        yaml_val = sources["yaml"][key]
        yaml_display = f"[bold]{yaml_val}[/bold]" if yaml_val != default_val else str(yaml_val)

        env_file_val = sources["env_file"][key]
        env_file_display = f"[bold]{env_file_val}[/bold]" if env_file_val != yaml_val else str(env_file_val)

        env_var_val = sources["env_vars"][key]
        env_var_display = f"[bold]{env_var_val}[/bold]" if env_var_val != env_file_val else str(env_var_val)

        table.add_row(key, str(default_val), yaml_display, env_file_display, env_var_display, str(final_val))

    console.print(table)

    # Clean up
    for key in ["DEMO_APP_NAME", "DEMO_DEBUG", "DEMO_SERVICE__HOST", "DEMO_SERVICE__PORT"]:
        if key in os.environ:
            del os.environ[key]

    return settings_with_env


def main():
    """Run the configuration precedence demo."""
    console.print(
        Panel.fit(
            "📊 Configuration Precedence Rules\n\n"
            "Understanding override priority:\n"
            "• Default values (lowest priority)\n"
            "• YAML configuration files\n"
            "• .env files\n"
            "• Environment variables (highest priority)\n\n"
            "Know exactly where your config comes from!",
            title="Demo 05: Configuration Precedence",
            style="bold blue",
        )
    )

    # Run the demonstration
    final_settings = demonstrate_precedence()

    # Show practical example
    console.print("\n📦 Practical Example:")
    console.print("Using this precedence for different environments:")

    env_table = Table(show_header=True, header_style="bold white")
    env_table.add_column("Environment", style="cyan")
    env_table.add_column("Configuration Strategy", style="yellow")

    env_table.add_row("Development", "Defaults + YAML for base config\n.env file for local overrides")
    env_table.add_row("Testing", "YAML for test config\nEnvironment vars for CI/CD")
    env_table.add_row(
        "Production", "YAML for base config\nEnvironment vars for secrets\nand deployment-specific values"
    )

    console.print(env_table)

    # Instantiate service with final config
    console.print("\n🚀 Final instantiated service:")
    service = final_settings.instantiate_field("service")
    console.print(f"Service: {service}")

    # Summary
    console.print(
        Panel.fit(
            "✅ Key Takeaways:\n\n"
            "1. Environment variables always win\n"
            "2. .env files override YAML\n"
            "3. YAML overrides code defaults\n"
            "4. Use appropriate source for each environment\n"
            "5. Document your precedence rules\n\n"
            "Next: Lazy vs eager instantiation →",
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
