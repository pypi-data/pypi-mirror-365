"""
Demo 02: Type-Safe Configurations
=================================

Using DynamicConfig for type safety and better developer experience.

Key concepts:
- DynamicConfig[T] for type-safe configurations
- Automatic target inference from generic type
- IDE support and type checking
- Pydantic validation
"""

import sys
from pathlib import Path

from pydantic import Field
from rich.console import Console
from rich.panel import Panel

sys.path.insert(0, str(Path(__file__).parent.parent))

from frostbound.pydanticonf import DynamicConfig, instantiate

console = Console()


# Domain classes
class Database:
    """A database connection."""

    def __init__(self, host: str, port: int = 5432, timeout: int = 30):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.connected = False

    def connect(self):
        self.connected = True
        return f"Connected to {self.host}:{self.port}"

    def __repr__(self):
        status = "connected" if self.connected else "disconnected"
        return f"Database({self.host}:{self.port}, {status})"


class EmailService:
    """An email service."""

    def __init__(self, smtp_host: str, smtp_port: int = 587, use_tls: bool = True):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.use_tls = use_tls

    def send(self, to: str, subject: str):
        return f"Email sent to {to}: {subject}"

    def __repr__(self):
        return f"EmailService({self.smtp_host}:{self.smtp_port}, TLS={self.use_tls})"


# Type-safe configuration classes
class DatabaseConfig(DynamicConfig[Database]):
    """Type-safe configuration for Database.

    Notice: No need to specify _target_ - it's inferred from Database type!
    """

    host: str = "localhost"
    port: int = Field(default=5432, ge=1, le=65535)  # With validation!
    timeout: int = Field(default=30, ge=1)


class EmailConfig(DynamicConfig[EmailService]):
    """Type-safe configuration for EmailService."""

    smtp_host: str
    smtp_port: int = Field(default=587, ge=1, le=65535)
    use_tls: bool = True


def main():
    """Run the type-safe configuration demo."""
    console.print(
        Panel.fit(
            "🛡️ Type-Safe Configurations with DynamicConfig\n\n"
            "Advanced features:\n"
            "• Generic types for compile-time safety\n"
            "• Automatic target inference\n"
            "• Pydantic validation\n"
            "• IDE autocomplete support\n\n"
            "Write safer, cleaner configuration code!",
            title="Demo 02: Type-Safe Configurations",
            style="bold blue",
        )
    )

    # Example 1: Basic type-safe config
    console.print("\n📦 Example 1: Type-safe database config")

    # Create config with automatic target inference
    db_config = DatabaseConfig(host="prod.db.server", port=5432, timeout=60)

    console.print("Configuration object:")
    console.print(f"  Type: {type(db_config).__name__}")
    console.print(f"  Target: {db_config.target_} (auto-inferred!)")
    console.print(f"  Config: {db_config.model_dump()}")

    # Instantiate
    database = instantiate(db_config)
    console.print(f"\nCreated object: {database}")
    console.print(f"Type verification: {type(database).__name__} ✓")

    # Example 2: Validation in action
    console.print("\n📦 Example 2: Pydantic validation")

    try:
        # This will fail validation
        bad_config = DatabaseConfig(
            host="localhost",
            port=99999,  # Invalid port!
            timeout=60,
        )
    except Exception as e:
        console.print(f"Validation error caught: {type(e).__name__}")
        console.print(f"Message: {e}")

    # Example 3: Default values
    console.print("\n📦 Example 3: Using defaults")

    minimal_config = DatabaseConfig(host="minimal.db")
    console.print(f"Minimal config: {minimal_config.model_dump()}")

    db = instantiate(minimal_config)
    console.print(f"Created with defaults: {db}")

    # Example 4: Email service config
    console.print("\n📦 Example 4: Email service configuration")

    email_config = EmailConfig(smtp_host="smtp.gmail.com", smtp_port=587, use_tls=True)

    email_service = instantiate(email_config)
    console.print(f"Email service: {email_service}")
    result = email_service.send("user@example.com", "Test Email")
    console.print(f"Test send: {result}")

    # Summary
    console.print(
        Panel.fit(
            "✅ Key Takeaways:\n\n"
            "1. DynamicConfig[T] provides type safety\n"
            "2. Target is automatically inferred from generic type\n"
            "3. Full Pydantic validation support\n"
            "4. IDE knows the return type of instantiate()\n"
            "5. Cleaner, safer configuration code\n\n"
            "Next: Learn about YAML configuration loading →",
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
