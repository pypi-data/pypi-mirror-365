import os
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.pretty import pprint
from rich.table import Table
from rich.tree import Tree

from frostbound.pydanticonf import instantiate, register_dependency
from integration.config_models import AlignerConfig, MultiEnvSettings, Settings
from integration.mocks import AlignmentStrategy

console = Console()


def demo_lazy_configuration():
    """Demo 1: Configuration-as-Data (Lazy Mode)"""
    console.print(
        Panel.fit(
            "📋 Configuration-as-Data (Lazy Mode)\n\n"
            "This demo showcases lazy configuration loading:\n"
            "• 📄 YAML files are loaded and merged\n"
            "• 🌍 Environment variables are processed\n"
            "• 🛡️  Configuration is validated\n"
            "• ⏸️  NO instantiation occurs - configs remain as data\n\n"
            "Perfect for configuration inspection and modification!",
            title="🚀 Demo 1: Lazy Configuration",
            style="bold cyan",
        )
    )

    # Change to demo directory
    os.chdir(Path(__file__).parent)

    # Initialize with lazy instantiation enabled
    console.print("\n📋 Step 1: Loading configuration in lazy mode...")
    settings = Settings()  # auto_instantiate=False in model_config

    console.print("\n✨ Configuration Loading Summary:")
    console.print("   ✅ YAML files loaded and merged")
    console.print("   ✅ Environment files loaded (.env.dev)")
    console.print("   ✅ Environment variables processed (DEV_DATABASE__PASSWORD → database.password)")
    console.print("   ✅ Configuration validation and type checking completed")
    console.print("   ❌ NO object instantiation has occurred - configs remain as data")

    # Access configuration values (still config objects, not instances)
    console.print("\n🔍 Configuration Values:")
    config_table = Table(show_header=True, header_style="bold magenta")
    config_table.add_column("Configuration", style="cyan", no_wrap=True)
    config_table.add_column("Value", style="green")
    config_table.add_column("Type", style="yellow")

    config_table.add_row("settings.debug", str(settings.debug), "from .env.dev")
    config_table.add_row("settings.database.password", "***" if settings.database.password else "None", "from .env.dev")
    config_table.add_row("settings.optimizer.algo", str(settings.optimizer.algo), "from YAML")
    config_table.add_row("settings.optimizer.lr", str(settings.optimizer.lr), "from YAML")
    config_table.add_row("type(settings.optimizer)", type(settings.optimizer).__name__, "Config object")

    console.print(config_table)

    # Configuration introspection and modification
    console.print("\n🔧 Configuration Modification:")
    console.print("   Modifying optimizer.lr before instantiation...")
    settings.optimizer.lr = 0.001
    console.print(f"   └─ New lr: [bold green]{settings.optimizer.lr}[/bold green]")

    # Alignment config inspection
    console.print("\n🎯 Alignment Configuration:")
    console.print(f"   Number of aligners: [bold cyan]{len(settings.alignment_config.aligners)}[/bold cyan]")

    aligner_tree = Tree("📦 Available Aligners")
    for i, aligner in enumerate(settings.alignment_config.aligners):
        status_icon = "✅" if aligner.enabled else "❌"
        aligner_tree.add(f"{status_icon} [{i}] {aligner.target_} (enabled: {aligner.enabled})")

    console.print(aligner_tree)


def demo_selective_instantiation():
    """Demo 2: Selective Instantiation"""
    console.print(
        Panel.fit(
            "🔧 Selective Instantiation\n\n"
            "This demo shows different instantiation patterns:\n"
            "• 🎯 Direct instantiation with instantiate()\n"
            "• 🔄 Runtime parameter overrides\n"
            "• 🏗️  Multiple instantiation approaches\n"
            "• 📦 On-demand object creation\n\n"
            "Build only what you need, when you need it!",
            title="🚀 Demo 2: Selective Instantiation",
            style="bold yellow",
        )
    )

    settings = Settings()

    # Option A: Direct instantiation with standalone function
    console.print("\n🎯 Option A: Direct instantiation")
    console.print(f" type(settings.optimizer) = [bold cyan]{type(settings.optimizer).__name__}[/bold cyan]")
    optimizer = instantiate(settings.optimizer)
    console.print(f"   └─ type(optimizer) = [bold cyan]{type(optimizer).__name__}[/bold cyan]")
    console.print("   └─ optimizer:")
    pprint(optimizer, indent_guides=True)

    # Option B: Instantiate with runtime parameter overrides
    console.print("\n🔄 Option B: Runtime overrides")
    optimizer2 = instantiate(settings.optimizer, lr=0.002)
    console.print("   └─ optimizer2 (with lr=0.002):")
    pprint(optimizer2, indent_guides=True)

    # Option C: Use settings methods
    console.print("\n🏗️  Option C: Using settings methods but OpenAI is not a DynamicConfig so type is not inferred")
    openai = instantiate(settings.openai)
    console.print("   └─ openai client:")
    pprint(openai, indent_guides=True)

    # Instantiate aligners
    console.print("\n📦 Instantiating Aligners:")
    aligner_table = Table(show_header=True, header_style="bold magenta")
    aligner_table.add_column("Aligner Type", style="cyan")
    aligner_table.add_column("Instance", style="green")

    for aligner_config in settings.alignment_config.aligners:
        if aligner_config.enabled:
            aligner = instantiate(aligner_config)
            pprint(aligner, indent_guides=True)
            pprint(type(aligner), indent_guides=True)
            aligner_table.add_row(type(aligner).__name__, str(aligner))

    console.print(aligner_table)


def demo_factory_pattern():
    """Demo 3: Factory Pattern with Dependency Injection"""
    console.print(
        Panel.fit(
            "🏭 Factory Pattern with Dependency Injection\n\n"
            "Advanced patterns for production systems:\n"
            "• 🔗 Dependency injection for shared resources\n"
            "• 🏭 Factory pattern for object creation\n"
            "• 🎯 Configuration-driven instantiation\n"
            "• 🔄 Automatic parameter injection\n\n"
            "Enterprise-grade object management!",
            title="🚀 Demo 3: Factory Pattern",
            style="bold green",
        )
    )

    settings = Settings()

    # This matches the AlignerFactory pattern from tmpppp.md
    class AlignerFactory:
        def __init__(
            self,
            *,
            source_language: str,
            target_language: str,
        ) -> None:
            # Register shared dependencies for injection
            register_dependency("source_language", source_language)
            register_dependency("target_language", target_language)

        def create_aligner(self, config: AlignerConfig) -> AlignmentStrategy:
            return instantiate(config)

        def create_aligners_from_config(self, settings: Settings) -> list[AlignmentStrategy]:
            aligners = []
            for aligner_config in settings.alignment_config.aligners:
                if aligner_config.enabled:
                    aligner = self.create_aligner(aligner_config)
                    aligners.append(aligner)
            return aligners

    # Use the factory
    console.print("\n🏭 Creating Aligner Factory:")
    console.print(f"   └─ Source Language: [bold cyan]{settings.source_lang}[/bold cyan]")
    console.print(f"   └─ Target Language: [bold cyan]{settings.target_lang}[/bold cyan]")

    factory = AlignerFactory(source_language=str(settings.source_lang), target_language=str(settings.target_lang))

    aligners = factory.create_aligners_from_config(settings)

    console.print(f"\n📦 Created {len(aligners)} aligners with dependency injection:")

    # Create a results table
    results_table = Table(show_header=True, header_style="bold magenta")
    results_table.add_column("Aligner", style="cyan", no_wrap=True)
    results_table.add_column("Type", style="yellow")
    results_table.add_column("Test Alignment", style="green")

    for aligner in aligners:
        # Test alignment
        result = aligner.align("Hello", "Hallo")
        results_table.add_row(str(aligner), type(aligner).__name__, f"Hello → Hallo: {result.confidence:.2f}")

    console.print(results_table)


def demo_multi_environment():
    """Demo 4: Multi-Environment Configuration"""
    console.print(
        Panel.fit(
            "🌍 Multi-Environment Configuration\n\n"
            "Managing configurations across environments:\n"
            "• 🚧 Development settings with debug enabled\n"
            "• 🚀 Production settings with optimizations\n"
            "• 🔄 Environment-specific overrides\n"
            "• 🛡️  Secure credential management\n\n"
            "One codebase, multiple deployments!",
            title="🚀 Demo 4: Multi-Environment",
            style="bold magenta",
        )
    )

    # Test development environment
    console.print("\n🚧 Development Environment:")
    os.environ["ENV"] = "dev"
    dev_settings = MultiEnvSettings()

    dev_tree = Tree("📋 Dev Configuration")
    dev_tree.add(f"Debug: [bold green]{dev_settings.debug}[/bold green]")
    dev_tree.add(f"Database host: [cyan]{dev_settings.database.host}[/cyan]")
    dev_tree.add(f"Database password: [red]{'***' if dev_settings.database.password else 'None'}[/red]")
    dev_tree.add(f"Optimizer algo: [yellow]{dev_settings.optimizer.algo}[/yellow]")
    dev_tree.add(f"Optimizer lr: [yellow]{dev_settings.optimizer.lr}[/yellow]")
    dev_tree.add(f"Aligners: [cyan]{len(dev_settings.alignment_config.aligners)}[/cyan]")

    console.print(dev_tree)

    # Test production environment
    console.print("\n🚀 Production Environment:")
    os.environ["ENV"] = "prod"
    prod_settings = MultiEnvSettings()

    prod_tree = Tree("📋 Prod Configuration")
    prod_tree.add(f"Debug: [bold red]{prod_settings.debug}[/bold red]")
    prod_tree.add(f"Database host: [cyan]{prod_settings.database.host}[/cyan]")
    prod_tree.add(f"Database password: [red]{'***' if prod_settings.database.password else 'None'}[/red]")
    prod_tree.add(f"Optimizer algo: [yellow]{prod_settings.optimizer.algo}[/yellow]")
    prod_tree.add(f"Optimizer lr: [yellow]{prod_settings.optimizer.lr}[/yellow]")
    prod_tree.add(f"Aligners: [cyan]{len(prod_settings.alignment_config.aligners)}[/cyan]")

    console.print(prod_tree)

    # Create comparison table
    console.print("\n📊 Environment Comparison:")

    compare_table = Table(show_header=True, header_style="bold white")
    compare_table.add_column("Setting", style="cyan")
    compare_table.add_column("Development", style="green")
    compare_table.add_column("Production", style="yellow")

    compare_table.add_row("Debug Mode", str(dev_settings.debug), str(prod_settings.debug))
    compare_table.add_row("Database Host", dev_settings.database.host, prod_settings.database.host)
    compare_table.add_row("Optimizer Algorithm", dev_settings.optimizer.algo, prod_settings.optimizer.algo)
    compare_table.add_row("Learning Rate", str(dev_settings.optimizer.lr), str(prod_settings.optimizer.lr))

    console.print(compare_table)


def demo_nested_instantiation():
    """Demo 5: Nested Instantiation with SmartNeighborhoodAligner"""
    console.print(
        Panel.fit(
            "🧩 Nested Instantiation\n\n"
            "Complex object composition patterns:\n"
            "• 🪆 Recursive nested instantiation\n"
            "• 🎯 SmartNeighborhoodAligner with sub-aligners\n"
            "• 🔗 Automatic dependency resolution\n"
            "• 🏗️  Deep object hierarchies\n\n"
            "Build complex systems from simple configs!",
            title="🚀 Demo 5: Nested Instantiation",
            style="bold red",
        )
    )

    settings = Settings()

    # Find the SmartNeighborhoodAligner config
    smart_aligner_config = None
    for config in settings.alignment_config.aligners:
        if "SmartNeighborhoodAligner" in config.target_:
            smart_aligner_config = config
            break

    if smart_aligner_config:
        console.print("\n🧩 SmartNeighborhoodAligner Configuration:")

        config_tree = Tree("📋 Configuration Details")
        config_tree.add(
            f"Enabled: [{'green' if smart_aligner_config.enabled else 'red'}]{smart_aligner_config.enabled}[/]"
        )
        config_tree.add(f"Min anchor confidence: [yellow]{smart_aligner_config.min_anchor_confidence}[/yellow]")
        config_tree.add(f"Anchor segment types: [cyan]{smart_aligner_config.anchor_segment_types}[/cyan]")
        config_tree.add(f"Max neighborhood size: [magenta]{smart_aligner_config.max_neighborhood_size}[/magenta]")

        console.print(config_tree)

        # Enable it for testing
        smart_aligner_config.enabled = True
        console.print("\n✅ Enabled SmartNeighborhoodAligner for testing")

        # Instantiate with nested configurations
        console.print("\n🏗️  Instantiating nested structure...")
        smart_aligner = instantiate(smart_aligner_config)

        console.print("\n🎯 Instantiation Result:")
        pprint(smart_aligner, indent_guides=True)

        console.print("\n📊 Nested Components:")
        components_table = Table(show_header=True, header_style="bold magenta")
        components_table.add_column("Component", style="cyan")
        components_table.add_column("Type", style="yellow")
        components_table.add_column("Details", style="green")

        components_table.add_row(
            "Anchor Aligner", type(smart_aligner.anchor_aligner).__name__, "Primary alignment strategy"
        )
        components_table.add_row(
            "Content Aligners", f"{len(smart_aligner.content_aligners)} aligners", "Secondary alignment strategies"
        )

        console.print(components_table)

        # Test alignment
        console.print("\n🧪 Testing nested aligner:")
        result = smart_aligner.align("Test", "Test")
        console.print(f"   └─ Alignment result: [bold green]{result}[/bold green]")


def main():
    """Run all demos."""
    console.print(
        Panel.fit(
            "🎯 Frostbound PydantiConf - Comprehensive Demo\n\n"
            "Welcome to the feature showcase!\n"
            "This demo demonstrates the full power of PydantiConf:\n\n"
            "• 📋 Lazy configuration loading\n"
            "• 🔧 Selective instantiation\n"
            "• 🏭 Factory patterns\n"
            "• 🌍 Multi-environment support\n"
            "• 🧩 Nested object composition\n\n"
            "Let's explore each feature in detail!",
            title="🚀 Frostbound PydantiConf Demo",
            style="bold blue",
            border_style="bright_blue",
        )
    )

    try:
        demo_lazy_configuration()
        demo_selective_instantiation()
        demo_factory_pattern()
        demo_multi_environment()
        demo_nested_instantiation()

        console.print(
            Panel.fit(
                "🎉 All Demos Completed Successfully!\n\n"
                "What we demonstrated:\n"
                "• ✅ Configuration-as-data with lazy loading\n"
                "• ✅ Flexible object instantiation patterns\n"
                "• ✅ Dependency injection system\n"
                "• ✅ Multi-environment configuration\n"
                "• ✅ Complex nested object hierarchies\n\n"
                "You're now ready to build sophisticated,\n"
                "configuration-driven applications with Frostbound!",
                title="🎯 Demo Summary",
                style="bold green",
                border_style="bright_green",
            )
        )

    except Exception as e:
        console.print(f"\n[bold red]❌ Error:[/bold red] {e}")
        import traceback

        console.print("[red]" + traceback.format_exc() + "[/red]")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
