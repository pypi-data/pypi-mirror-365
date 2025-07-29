from __future__ import annotations

import sys
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict
from rich.console import Console
from rich.panel import Panel
from rich.pretty import pprint
from rich.table import Table
from rich.tree import Tree

from frostbound.pydanticonf import BaseSettingsWithInstantiation, DynamicConfig, instantiate

console = Console()


class Database:
    def __init__(self, host: str, port: int, db: str, username: str, password: str = ""):
        self.host = host
        self.port = port
        self.db = db
        self.username = username
        self.password = password

    def __repr__(self):
        return f"Database({self.host}:{self.port}/{self.db})"


class Optimizer(BaseModel):
    algo: str = "SGD"
    lr: float = 0.01

    def __repr__(self):
        return f"Optimizer({self.algo}, lr={self.lr})"

    def step(self, loss: float = 1.0) -> float:
        if self.algo == "SGD":
            return loss
        elif self.algo == "Adam":
            return loss * 0.9
        else:
            raise ValueError(f"Unknown optimizer: {self.algo}")


# Configuration models following tmpppp.md pattern
class DatabaseConfig(BaseModel):
    """Non-instantiatable config - just data."""

    host: str
    port: int
    db: str
    username: str
    password: str = ""


class OptimizerConfig(DynamicConfig[Optimizer]):
    """Instantiatable config with _target_."""

    target_: str = Field(default="__main__.Optimizer", alias="_target_")
    algo: str = "SGD"
    lr: float = 0.01


CONFIG_DIR = Path(__file__).parent / "config"
ENV_DIR = Path(__file__).parent / "envs"


# Settings class with lazy instantiation
class Settings(BaseSettingsWithInstantiation):
    auto_instantiate = False  # Lazy mode

    model_config = SettingsConfigDict(
        yaml_file=str(CONFIG_DIR / "01_simple.yaml"),
        env_file=str(ENV_DIR / ".env.01_simple"),
        env_prefix="APP_",
        env_nested_delimiter="__",
    )

    debug: bool = True
    database: DatabaseConfig
    optimizer: OptimizerConfig


def main():
    """Run the simple demo."""
    console.print(
        Panel.fit(
            "🎯 Simple PydantiConf Demo\n\n"
            "Learn the core concepts:\n"
            "• 📄 Configuration loading from YAML & .env\n"
            "• 🔧 Configuration priority system\n"
            "• 🎯 Lazy vs eager instantiation\n"
            "• 🔄 Runtime parameter overrides\n\n"
            "Perfect for getting started!",
            title="🚀 Welcome to PydantiConf",
            style="bold blue",
            border_style="bright_blue",
        )
    )

    # ========================================================================
    # Phase 1: Configuration Loading
    # ========================================================================

    console.print(
        Panel.fit(
            "📋 Phase 1: Configuration Loading\n\n"
            "Loading configuration from multiple sources:\n"
            "• YAML file: config/01_simple.yaml\n"
            "• Environment file: envs/.env.01_simple\n"
            "• Environment variables: APP_*\n\n"
            "Priority: ENV vars > YAML > .env file",
            title="📁 Configuration Sources",
            style="bold cyan",
        )
    )

    console.print("\n🔄 Loading configuration...")
    settings = Settings()  # type: ignore

    console.print("\n📋 Raw Settings Object:")
    pprint(settings, indent_guides=True)
    pprint(settings.model_dump(), indent_guides=True)

    console.print("\n🔍 Configuration Details:")

    # Create a configuration table
    config_table = Table(show_header=True, header_style="bold magenta")
    config_table.add_column("Setting", style="cyan", no_wrap=True)
    config_table.add_column("Value", style="green")
    config_table.add_column("Source", style="yellow")
    config_table.add_column("Type", style="blue")

    config_table.add_row("debug", str(settings.debug), "YAML overrides .env", type(settings.debug).__name__)
    config_table.add_row("database.host", settings.database.host, "from YAML", "DatabaseConfig")
    config_table.add_row("database.port", str(settings.database.port), "from YAML", "DatabaseConfig")
    config_table.add_row("database.password", str(settings.database.password), "from .env file", "str")
    config_table.add_row("optimizer.algo", settings.optimizer.algo, "from YAML", type(settings.optimizer).__name__)
    config_table.add_row("optimizer.lr", str(settings.optimizer.lr), "from YAML", "float")

    console.print(config_table)

    # Show configuration object types
    console.print("\n📊 Configuration Object Types:")

    type_tree = Tree("🔍 Type Inspection")
    type_tree.add(f"settings: [yellow]{type(settings).__name__}[/yellow]")
    type_tree.add(f"settings.database: [yellow]{type(settings.database).__name__}[/yellow] (non-instantiatable)")
    type_tree.add(f"settings.optimizer: [yellow]{type(settings.optimizer).__name__}[/yellow] (instantiatable)")

    console.print(type_tree)

    # ========================================================================
    # Phase 2: Selective Instantiation
    # ========================================================================

    console.print(
        Panel.fit(
            "🔧 Phase 2: Selective Instantiation\n\n"
            "Transform configuration into live objects:\n"
            "• 🎯 Use instantiate() function\n"
            "• 🔄 Support runtime overrides\n"
            "• 📦 Create objects on-demand\n\n"
            "Only instantiate what you need!",
            title="🏗️  Object Instantiation",
            style="bold yellow",
        )
    )

    console.print("\n🎯 Instantiating Optimizer:")

    # Instantiate optimizer
    optimizer = instantiate(settings.optimizer)
    console.print(f"   └─ Type: [bold cyan]{type(optimizer).__name__}[/bold cyan]")
    console.print("   └─ Instance:")
    pprint(optimizer, indent_guides=True)

    # Test the optimizer
    console.print("\n🧪 Testing optimizer.step():")
    loss_result = optimizer.step(loss=1.0)
    console.print(f"   └─ step(loss=1.0) → [bold green]{loss_result}[/bold green]")

    # Instantiate with overrides
    console.print("\n🔄 Instantiating with Runtime Overrides:")
    optimizer2 = instantiate(settings.optimizer, lr=0.1)
    console.print("   └─ optimizer2 (lr=0.1):")
    pprint(optimizer2, indent_guides=True)

    # Show comparison
    console.print("\n📊 Optimizer Comparison:")

    compare_table = Table(show_header=True, header_style="bold magenta")
    compare_table.add_column("Instance", style="cyan")
    compare_table.add_column("Algorithm", style="yellow")
    compare_table.add_column("Learning Rate", style="green")

    compare_table.add_row("Original", optimizer.algo, str(optimizer.lr))
    compare_table.add_row("With Override", optimizer2.algo, str(optimizer2.lr))

    console.print(compare_table)

    # ========================================================================
    # Summary
    # ========================================================================

    console.print(
        Panel.fit(
            "🎉 Demo Completed Successfully!\n\n"
            "What we learned:\n"
            "• ✅ Configuration loading with priority system\n"
            "• ✅ Lazy configuration (no auto-instantiation)\n"
            "• ✅ On-demand object creation\n"
            "• ✅ Runtime parameter overrides\n\n"
            "You now understand the core concepts!\n"
            "Ready to build configuration-driven apps 🚀",
            title="🎯 Summary",
            style="bold green",
            border_style="bright_green",
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
