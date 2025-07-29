"""
Demo 01: Basic Instantiation
============================

The simplest example of using PydantiConf to create objects from configuration.

Key concepts:
- Using instantiate() to create objects from dictionaries
- Understanding the _target_ field
- Basic parameter passing
"""

import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

sys.path.insert(0, str(Path(__file__).parent.parent))

from frostbound.pydanticonf import instantiate

console = Console()


# Simple classes to demonstrate instantiation
class Greeter:
    """A simple greeter class."""

    def __init__(self, name: str, greeting: str = "Hello"):
        self.name = name
        self.greeting = greeting

    def greet(self) -> str:
        return f"{self.greeting}, {self.name}!"

    def __repr__(self):
        return f"Greeter(name='{self.name}', greeting='{self.greeting}')"


class Calculator:
    """A simple calculator class."""

    def __init__(self, precision: int = 2):
        self.precision = precision

    def add(self, a: float, b: float) -> float:
        return round(a + b, self.precision)

    def __repr__(self):
        return f"Calculator(precision={self.precision})"


def main():
    """Run the basic instantiation demo."""
    console.print(
        Panel.fit(
            "🎯 Basic Instantiation with PydantiConf\n\n"
            "Learn the fundamentals:\n"
            "• Create objects from configuration dictionaries\n"
            "• Use _target_ to specify the class\n"
            "• Pass constructor parameters\n\n"
            "The simplest way to get started!",
            title="Demo 01: Basic Instantiation",
            style="bold blue",
        )
    )

    # Example 1: Basic instantiation
    console.print("\n📦 Example 1: Basic object creation")
    console.print("Configuration:")

    greeter_config = {"_target_": "__main__.Greeter", "name": "World", "greeting": "Hi"}
    console.print(f"  {greeter_config}")

    greeter = instantiate(greeter_config)
    console.print(f"\nCreated object: {greeter}")
    console.print(f"Result: {greeter.greet()}")

    # Example 2: With default values
    console.print("\n📦 Example 2: Using default values")
    console.print("Configuration (no greeting specified):")

    simple_config = {"_target_": "__main__.Greeter", "name": "Python"}
    console.print(f"  {simple_config}")

    simple_greeter = instantiate(simple_config)
    console.print(f"\nCreated object: {simple_greeter}")
    console.print(f"Result: {simple_greeter.greet()}")

    # Example 3: Different class
    console.print("\n📦 Example 3: Instantiating different classes")
    console.print("Configuration:")

    calc_config = {"_target_": "__main__.Calculator", "precision": 4}
    console.print(f"  {calc_config}")

    calculator = instantiate(calc_config)
    console.print(f"\nCreated object: {calculator}")
    console.print(f"Result of 1.2345 + 2.3456: {calculator.add(1.2345, 2.3456)}")

    # Summary
    console.print(
        Panel.fit(
            "✅ Key Takeaways:\n\n"
            "1. instantiate() creates objects from config dicts\n"
            "2. _target_ specifies the class/function to call\n"
            "3. Other keys become constructor parameters\n"
            "4. Default values are respected\n\n"
            "Next: Learn about type-safe configurations →",
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
