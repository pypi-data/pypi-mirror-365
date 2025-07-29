"""
ConfigFactory Demo - Showcasing the Unified Factory Pattern

This demo illustrates the new ConfigFactory that combines dependency injection,
lazy instantiation, caching, and runtime overrides into a single elegant interface.
"""

import os
import sys
from pathlib import Path

from pydantic import Field
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

sys.path.insert(0, str(Path(__file__).parent.parent))

from frostbound.pydanticonf import ConfigFactory, DynamicConfig

console = Console()


# ========================================================================
# Mock Classes for Demonstration
# ========================================================================


class Database:
    """Mock database connection."""

    def __init__(self, host: str, port: int = 5432, pool_size: int = 10):
        self.host = host
        self.port = port
        self.pool_size = pool_size
        self._connected = False

    def connect(self):
        self._connected = True
        return f"Connected to {self.host}:{self.port}"

    def __repr__(self):
        return f"Database({self.host}:{self.port}, pool={self.pool_size})"


class Logger:
    """Mock logger."""

    def __init__(self, name: str, level: str = "INFO"):
        self.name = name
        self.level = level

    def log(self, message: str):
        return f"[{self.level}] {self.name}: {message}"

    def __repr__(self):
        return f"Logger({self.name}, level={self.level})"


class MetricsClient:
    """Mock metrics client."""

    def __init__(self, endpoint: str = "localhost:8125"):
        self.endpoint = endpoint

    def track(self, metric: str, value: float):
        return f"Tracked {metric}={value} to {self.endpoint}"

    def __repr__(self):
        return f"MetricsClient({self.endpoint})"


class CacheService:
    """Mock cache service."""

    def __init__(self, host: str = "localhost", port: int = 6379, ttl: int = 3600):
        self.host = host
        self.port = port
        self.ttl = ttl

    def __repr__(self):
        return f"CacheService({self.host}:{self.port}, ttl={self.ttl}s)"


class UserService:
    """Mock user service with dependencies."""

    def __init__(
        self,
        name: str,
        database: Database,
        cache: CacheService,
        logger: Logger | None = None,
        metrics: MetricsClient | None = None,
    ):
        self.name = name
        self.database = database
        self.cache = cache
        self.logger = logger
        self.metrics = metrics

    def get_user(self, user_id: int):
        if self.logger:
            self.logger.log(f"Getting user {user_id}")
        if self.metrics:
            self.metrics.track("user.get", 1)
        return f"User#{user_id} from {self.database}"

    def __repr__(self):
        return f"UserService({self.name}, db={self.database.host}, cache={self.cache.host})"


class MLModel:
    """Mock ML model with expensive initialization."""

    def __init__(self, checkpoint: str, device: str = "cpu", precision: str = "fp32"):
        self.checkpoint = checkpoint
        self.device = device
        self.precision = precision
        # Simulate expensive loading
        console.print(f"   💾 Loading model from {checkpoint} on {device} with {precision}...")

    def predict(self, input_data: str):
        return f"Prediction for '{input_data}' using {self.checkpoint}"

    def __repr__(self):
        return f"MLModel({self.checkpoint}, {self.device}, {self.precision})"


# ========================================================================
# Configuration Classes
# ========================================================================


class DatabaseConfig(DynamicConfig[Database]):
    """Configuration for database connections."""

    target_: str = Field(default="__main__.Database", alias="_target_")
    host: str = "localhost"
    port: int = 5432
    pool_size: int = 10


class CacheConfig(DynamicConfig[CacheService]):
    """Configuration for cache service."""

    target_: str = Field(default="__main__.CacheService", alias="_target_")
    host: str = "localhost"
    port: int = 6379
    ttl: int = 3600


class ServiceConfig(DynamicConfig[UserService]):
    """Configuration for user service."""

    target_: str = Field(default="__main__.UserService", alias="_target_")
    name: str
    database: DatabaseConfig
    cache: CacheConfig


class ModelConfig(DynamicConfig[MLModel]):
    """Configuration for ML models."""

    target_: str = Field(default="__main__.MLModel", alias="_target_")
    checkpoint: str
    device: str = "cpu"
    precision: str = "fp32"


# ========================================================================
# Demo Functions
# ========================================================================


def demo_basic_usage():
    """Demo 1: Basic ConfigFactory Usage"""
    console.print(
        Panel.fit(
            "🎯 Basic ConfigFactory Usage\n\n"
            "Demonstrating core features:\n"
            "• 🔧 Creating a factory with caching enabled\n"
            "• 📦 Registering shared dependencies\n"
            "• 📋 Registering named configurations\n"
            "• 🚀 Creating instances with lazy loading\n\n"
            "Simple yet powerful!",
            title="Demo 1: Basic Usage",
            style="bold cyan",
        )
    )

    # Create factory
    console.print("\n🏭 Creating ConfigFactory for UserService:")
    factory = ConfigFactory[UserService](cache=True)
    console.print("   ✅ Factory created with caching enabled")

    # Register dependencies
    console.print("\n🔗 Registering shared dependencies:")
    logger = Logger("app", level="DEBUG")
    metrics = MetricsClient("metrics.server:8125")

    factory.register_dependency("logger", logger)
    factory.register_dependency("metrics", metrics)
    console.print(f"   ✅ Registered logger: {logger}")
    console.print(f"   ✅ Registered metrics: {metrics}")

    # Register configurations
    console.print("\n📋 Registering named configurations:")

    default_config = ServiceConfig(
        name="UserService",
        database=DatabaseConfig(host="localhost", port=5432),
        cache=CacheConfig(host="localhost", port=6379),
    )

    prod_config = ServiceConfig(
        name="UserServiceProd",
        database=DatabaseConfig(host="prod.db.server", port=5432, pool_size=50),
        cache=CacheConfig(host="prod.cache.server", port=6379, ttl=7200),
    )

    factory.register_config("default", default_config)
    factory.register_config("prod", prod_config)
    console.print("   ✅ Registered 'default' configuration")
    console.print("   ✅ Registered 'prod' configuration")

    # Get instances (with caching)
    console.print("\n🚀 Getting instances (lazy + cached):")

    service1 = factory.get("default")
    console.print(f"   ✅ Created: {service1}")

    service2 = factory.get("default")
    console.print(f"   ✅ Retrieved from cache: {service2}")
    console.print(f"   ✅ Same instance: {service1 is service2}")

    # Test the service
    console.print("\n🧪 Testing service:")
    result = service1.get_user(123)
    console.print(f"   └─ {result}")


def demo_runtime_overrides():
    """Demo 2: Runtime Configuration Overrides"""
    console.print(
        Panel.fit(
            "🔄 Runtime Configuration Overrides\n\n"
            "Advanced override patterns:\n"
            "• 🎯 Simple parameter overrides\n"
            "• 🪆 Nested configuration overrides\n"
            "• 🏗️ Direct creation without caching\n"
            "• 📦 Override caching behavior\n\n"
            "Maximum flexibility!",
            title="Demo 2: Runtime Overrides",
            style="bold yellow",
        )
    )

    factory = ConfigFactory[UserService]()

    # Register base configuration
    base_config = ServiceConfig(
        name="BaseService", database=DatabaseConfig(host="localhost"), cache=CacheConfig(host="localhost")
    )
    factory.register_config("base", base_config)

    # Override at different levels
    console.print("\n🎯 Creating services with overrides:")

    # Simple override
    dev_service = factory.get("base", name="DevService")
    console.print(f"   ✅ With name override: {dev_service}")

    # Nested override using double underscore
    staging_service = factory.get(
        "base", name="StagingService", database__host="staging.db.server", database__pool_size=25, cache__ttl=1800
    )
    console.print(f"   ✅ With nested overrides: {staging_service}")

    # Direct creation (no caching)
    console.print("\n🏗️ Direct creation without caching:")
    custom_service = factory.create(
        ServiceConfig(
            name="CustomService", database=DatabaseConfig(host="custom.db"), cache=CacheConfig(host="custom.cache")
        ),
        database__pool_size=100,
    )
    console.print(f"   ✅ Created: {custom_service}")


def demo_lazy_ml_models():
    """Demo 3: Lazy Loading ML Models"""
    console.print(
        Panel.fit(
            "🤖 Lazy Loading ML Models\n\n"
            "Efficient resource management:\n"
            "• 💾 Expensive models loaded on-demand\n"
            "• 🔄 Cached for subsequent use\n"
            "• 🎯 Multiple model variants\n"
            "• 🚀 Runtime device selection\n\n"
            "Perfect for ML pipelines!",
            title="Demo 3: ML Model Factory",
            style="bold green",
        )
    )

    # Create model factory
    console.print("\n🏭 Creating ML Model Factory:")
    model_factory = ConfigFactory[MLModel](cache=True)

    # Register different model configurations
    console.print("\n📋 Registering model configurations:")

    model_factory.register_config("small", ModelConfig(checkpoint="models/small.ckpt", device="cpu"))

    model_factory.register_config("large", ModelConfig(checkpoint="models/large.ckpt", device="cuda"))

    model_factory.register_config(
        "xlarge", ModelConfig(checkpoint="models/xlarge.ckpt", device="cuda", precision="fp16")
    )

    console.print("   ✅ Registered: small, large, xlarge")

    # Models are created only when requested
    console.print("\n🤖 Loading models on demand:")

    # First request - loads the model
    console.print("\n📦 First request for 'small' model:")
    small_model = model_factory.get("small")
    console.print(f"   ✅ Loaded: {small_model}")

    # Second request - returns cached instance
    console.print("\n📦 Second request for 'small' model:")
    small_model_cached = model_factory.get("small")
    console.print(f"   ✅ From cache: {small_model_cached}")
    console.print(f"   ✅ Same instance: {small_model is small_model_cached}")

    # Override device at runtime
    console.print("\n🔄 Override device at runtime:")
    small_gpu = model_factory.get("small", device="cuda")
    console.print(f"   ✅ New instance with GPU: {small_gpu}")

    # List available models
    console.print("\n📊 Available models:")
    models_table = Table(show_header=True, header_style="bold magenta")
    models_table.add_column("Model", style="cyan")
    models_table.add_column("Checkpoint", style="yellow")
    models_table.add_column("Default Device", style="green")

    for name in model_factory.list_configs():
        config = model_factory._configs[name]
        models_table.add_row(name, config.checkpoint, config.device)

    console.print(models_table)


def demo_batch_creation():
    """Demo 4: Batch Creation with Common Overrides"""
    console.print(
        Panel.fit(
            "📦 Batch Creation\n\n"
            "Creating multiple instances efficiently:\n"
            "• 🎯 Multiple configurations at once\n"
            "• 🔄 Common overrides for all\n"
            "• 🏗️ Consistent initialization\n"
            "• 📊 Perfect for microservices\n\n"
            "Scale with ease!",
            title="Demo 4: Batch Creation",
            style="bold magenta",
        )
    )

    # Create factory for databases
    factory = ConfigFactory[Database]()

    # Create multiple database configurations
    console.print("\n📋 Creating database configurations:")

    configs = [
        DatabaseConfig(host="users.db.server", port=5432),
        DatabaseConfig(host="orders.db.server", port=5432),
        DatabaseConfig(host="analytics.db.server", port=5433),
        DatabaseConfig(host="cache.db.server", port=5434),
    ]

    # Create all with common overrides
    console.print("\n🏗️ Creating all databases with common settings:")
    databases = factory.create_multiple(
        configs,
        pool_size=30,  # Common override for all
    )

    # Display results
    console.print("\n📊 Created databases:")
    db_table = Table(show_header=True, header_style="bold white")
    db_table.add_column("#", style="dim")
    db_table.add_column("Host", style="cyan")
    db_table.add_column("Port", style="yellow")
    db_table.add_column("Pool Size", style="green")

    for i, db in enumerate(databases):
        db_table.add_row(str(i), db.host, str(db.port), str(db.pool_size))

    console.print(db_table)

    # Connect all databases
    console.print("\n🔌 Connecting all databases:")
    for db in databases:
        result = db.connect()
        console.print(f"   ✅ {result}")


def demo_cache_management():
    """Demo 5: Cache Management"""
    console.print(
        Panel.fit(
            "💾 Cache Management\n\n"
            "Controlling instance caching:\n"
            "• 🔄 Enable/disable caching\n"
            "• 🧹 Clear cache selectively\n"
            "• 📊 Memory-efficient design\n"
            "• 🎯 Fine-grained control\n\n"
            "Optimize memory usage!",
            title="Demo 5: Cache Management",
            style="bold red",
        )
    )

    # Factory with caching
    console.print("\n🏭 Factory with caching enabled:")
    cached_factory = ConfigFactory[Database](cache=True)

    config = DatabaseConfig(host="test.db")
    cached_factory.register_config("test", config)

    # Multiple gets return same instance
    db1 = cached_factory.get("test")
    db2 = cached_factory.get("test")
    console.print(f"   ✅ Cached: db1 is db2 = {db1 is db2}")

    # Factory without caching
    console.print("\n🏭 Factory with caching disabled:")
    no_cache_factory = ConfigFactory[Database](cache=False)
    no_cache_factory.register_config("test", config)

    # Multiple gets return different instances
    db3 = no_cache_factory.get("test")
    db4 = no_cache_factory.get("test")
    console.print(f"   ✅ Not cached: db3 is db4 = {db3 is db4}")

    # Cache management
    console.print("\n🧹 Cache management:")

    # Create multiple cached instances
    cached_factory.register_config("dev", DatabaseConfig(host="dev.db"))
    cached_factory.register_config("prod", DatabaseConfig(host="prod.db"))

    cached_factory.get("test")
    dev_db = cached_factory.get("dev")
    cached_factory.get("prod")

    console.print("   ✅ Created 3 cached instances")

    # Clear specific cache entry
    cached_factory.clear_cache("dev")
    console.print("   ✅ Cleared 'dev' from cache")

    # New instance created for dev
    new_dev_db = cached_factory.get("dev")
    console.print(f"   ✅ New dev instance: {dev_db is new_dev_db}")

    # Clear all cache
    cached_factory.clear_cache()
    console.print("   ✅ Cleared entire cache")


def main():
    """Run all ConfigFactory demos."""
    console.print(
        Panel.fit(
            "🚀 ConfigFactory Demo Suite\n\n"
            "Welcome to the unified factory pattern showcase!\n\n"
            "ConfigFactory combines the best of all worlds:\n"
            "• 🔗 Dependency injection\n"
            "• 💾 Smart caching with weak references\n"
            "• 🎯 Lazy instantiation\n"
            "• 🔄 Runtime overrides\n"
            "• 🏭 Production-ready patterns\n\n"
            "Let's explore the features!",
            title="ConfigFactory Demo",
            style="bold blue",
            border_style="bright_blue",
        )
    )

    try:
        # Change to demo directory
        os.chdir(Path(__file__).parent)

        demo_basic_usage()
        demo_runtime_overrides()
        demo_lazy_ml_models()
        demo_batch_creation()
        demo_cache_management()

        console.print(
            Panel.fit(
                "🎉 All Demos Completed Successfully!\n\n"
                "ConfigFactory provides a unified interface for:\n"
                "• ✅ Dependency injection\n"
                "• ✅ Lazy loading with caching\n"
                "• ✅ Runtime configuration overrides\n"
                "• ✅ Batch instantiation\n"
                "• ✅ Memory-efficient caching\n\n"
                "Use ConfigFactory for elegant, type-safe\n"
                "configuration management in your applications!",
                title="✨ Summary",
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
