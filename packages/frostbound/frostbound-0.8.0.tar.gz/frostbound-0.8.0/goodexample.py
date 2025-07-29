"""
Complete Example: E-commerce Application Configuration

Let's say you're building an e-commerce application with multiple services. Instead of hardcoding everything, you define it all in YAML:

config.yaml:
# Database configuration
database:
  _target_: "myapp.database.PostgreSQLDatabase"
  host: "${DB_HOST:localhost}"
  port: ${DB_PORT:5432}
  database: "ecommerce"
  pool_size: 20

# Cache configuration
cache:
  _target_: "myapp.cache.RedisCache"
  host: "${REDIS_HOST:localhost}"
  port: ${REDIS_PORT:6379}
  ttl: 3600

# Services that depend on database and cache
services:
  user_service:
    _target_: "myapp.services.UserService"
    # database and cache will be injected automatically

  order_service:
    _target_: "myapp.services.OrderService"
    # database will be injected automatically
    payment_processor:
      _target_: "myapp.payments.StripeProcessor"
      api_key: "${STRIPE_API_KEY}"

  notification_service:
    _target_: "myapp.services.NotificationService"
    email_backend:
      _target_: "myapp.email.SMTPBackend"
      host: "smtp.gmail.com"
      port: 587
      username: "${EMAIL_USER}"
      password: "${EMAIL_PASS}"

Python code:
from frostbound.pydanticonf import BaseSettingsWithInstantiation, instantiate, register_dependency
from pydantic_settings import SettingsConfigDict

# Your application classes
class PostgreSQLDatabase:
    def __init__(self, host: str, port: int, database: str, pool_size: int = 10):
        self.host = host
        self.port = port
        self.database = database
        self.pool_size = pool_size
        print(f"Connected to PostgreSQL: {host}:{port}/{database}")

class RedisCache:
    def __init__(self, host: str, port: int, ttl: int = 3600):
        self.host = host
        self.port = port
        self.ttl = ttl
        print(f"Connected to Redis: {host}:{port}")

class UserService:
    def __init__(self, database: PostgreSQLDatabase, cache: RedisCache):
        self.database = database
        self.cache = cache
        print("UserService initialized with database and cache")

class OrderService:
    def __init__(self, database: PostgreSQLDatabase, payment_processor):
        self.database = database
        self.payment_processor = payment_processor
        print("OrderService initialized")

# Settings class that loads and instantiates everything
class AppSettings(BaseSettingsWithInstantiation):
    model_config = SettingsConfigDict(
        yaml_file="config.yaml",
        env_nested_delimiter="__"
    )

    database: PostgreSQLDatabase
    cache: RedisCache
    services: dict

# Usage
def main():
    # Load configuration from YAML + environment variables
    settings = AppSettings()

    # Manually instantiate the main components first
    db = instantiate(settings.database)
    cache = instantiate(settings.cache)

    # Register them as dependencies for automatic injection
    register_dependency("database", db)
    register_dependency("cache", cache)

    # Now instantiate services - they'll automatically get db/cache injected
    user_service = instantiate(settings.services["user_service"])
    order_service = instantiate(settings.services["order_service"])
    notification_service = instantiate(settings.services["notification_service"])

    print(f"User service DB: {user_service.database.host}")
    print(f"Order service DB: {order_service.database.host}")
    print(f"Same database instance: {user_service.database is order_service.database}")

if __name__ == "__main__":
    main()

What happens when you run this:

1. Configuration Loading: The YAML file is loaded, environment variables like ${DB_HOST} are resolved
2. Manual Instantiation: You create the shared database and cache instances first
3. Dependency Registration: You register these shared instances so they can be auto-injected
4. Service Creation: When you instantiate services, the system automatically injects the shared database/cache
5. Recursive Processing: Nested configs like payment_processor and email_backend are automatically instantiated too

Output:
Connected to PostgreSQL: localhost:5432/ecommerce
Connected to Redis: localhost:6379
UserService initialized with database and cache
OrderService initialized
User service DB: localhost
Order service DB: localhost
Same database instance: True

Key Benefits Demonstrated:

1. Configuration-Driven: Your entire app structure is defined in YAML, not Python code
2. Environment Flexibility: Different configs for dev/staging/prod using environment variables
3. Dependency Injection: Shared resources (database, cache) are automatically provided
4. Recursive Instantiation: Complex nested objects are created automatically
5. Type Safety: With DynamicConfig, you get full type checking

This pattern is incredibly powerful for microservices, complex applications, or any scenario where you need flexible, environment-specific configuration without hardcoding dependencies.
"""
