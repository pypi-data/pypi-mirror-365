# Understanding Frostbound's Dynamic Instantiation System

## Table of Contents

1. [Overview](#overview)
2. [Type Safety Analysis](#type-safety-analysis)
3. [Architecture Overview](#architecture-overview)
4. [Core Concepts](#core-concepts)
5. [Dependency Injection](#dependency-injection)
6. [Code Examples](#code-examples)
7. [Error Handling](#error-handling)
8. [Design Patterns](#design-patterns)

## Overview

The `_instantiate.py` module is the heart of Frostbound's configuration-driven
object creation system. It enables you to define complex object hierarchies in
YAML/JSON configuration files and instantiate them dynamically at runtime.

### Key Features

-   Dynamic object creation from configuration
-   Recursive instantiation of nested configurations
-   Automatic dependency injection
-   Circular dependency detection
-   Type-safe when using `DynamicConfig[T]`
-   Comprehensive error handling

## Type Safety Analysis

### Why Returning `Any` is Appropriate

The module uses sophisticated typing that balances safety with Python's dynamic
nature:

```python
@overload
def instantiate(config: DynamicConfig[InstanceT], ...) -> InstanceT: ...

@overload
def instantiate(config: InstantiableConfig, ...) -> Any: ...
```

**Key Points:**

1. **Type-safe overloads**: When using `DynamicConfig[T]`, you get full type
   safety with return type `T`
2. **Dynamic nature**: When instantiating from dictionaries like
   `{"_target_": "pathlib.Path"}`, the actual type cannot be determined at
   compile time
3. **Honest typing**: Returning `Any` for dictionary configs is the most
   accurate representation of what can be guaranteed

## Architecture Overview

### 1. Core Instantiation Flow

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────┐
│   Config Dict   │ ──────> │   instantiate()  │ ──────> │   Object    │
│ {"_target_":    │         │                  │         │  Instance   │
│  "myapp.Class"} │         │ 1. Import class  │         │             │
└─────────────────┘         │ 2. Inject deps   │         └─────────────┘
                            │ 3. Create object │
                            └──────────────────┘
```

### 2. Dependency Injection Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   DependencyResolver                      │
├─────────────────────────────────────────────────────────┤
│  Strategies:                                             │
│  ┌─────────────────────────┐  ┌──────────────────────┐ │
│  │ NameBasedInjection      │  │ TypeBasedInjection   │ │
│  │ ┌─────────────────────┐ │  │ ┌──────────────────┐ │ │
│  │ │ _name_dependency_    │ │  │ │ _type_dependency_ │ │ │
│  │ │ store:               │ │  │ │ store:            │ │ │
│  │ │ {"database": db_obj} │ │  │ │ {Database: db_obj}│ │ │
│  │ └─────────────────────┘ │  │ └──────────────────┘ │ │
│  └─────────────────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 3. Detailed Instantiation Flow

```
instantiate(config)
    │
    ├─> Extract control parameters (_target_, _recursive_, _partial_)
    │
    ├─> Check circular dependencies (using _instantiation_stack)
    │
    ├─> Route to appropriate handler:
    │   ├─> _instantiate_from_dict()
    │   └─> _instantiate_from_dynamic_config()
    │
    └─> Common flow:
        ├─> Process values recursively (if _recursive_=True)
        │   └─> Nested configs are instantiated
        │
        ├─> Import target class (_import_class)
        │
        ├─> Inject dependencies (_dependency_resolver.inject_dependencies)
        │   ├─> Check constructor signature
        │   ├─> Apply injection strategies
        │   └─> Add missing dependencies to kwargs
        │
        └─> Create object or partial
```

## Core Concepts

### 1. Configuration Structure

Configurations can be dictionaries or `DynamicConfig` objects with these special
keys:

-   `_target_`: The fully qualified path to the class/function to instantiate
-   `_recursive_`: Whether to recursively instantiate nested configs (default:
    True)
-   `_partial_`: Return a `functools.partial` instead of calling the target
-   `_args_`: Positional arguments to pass to the target

### 2. Recursive Processing

When `_recursive_=True`, the system automatically instantiates nested
configurations:

```python
# Input configuration:
config = {
    "_target_": "myapp.Service",
    "name": "UserService",
    "database": {  # Nested config - will be instantiated
        "_target_": "myapp.Database",
        "host": "localhost"
    },
    "cache": {     # Another nested config
        "_target_": "myapp.Cache",
        "ttl": 3600
    }
}

# Result:
Service(
    name="UserService",
    database=Database(host="localhost"),  # Automatically created
    cache=Cache(ttl=3600)                 # Automatically created
)
```

### 3. Circular Dependency Detection

The system tracks the instantiation stack to prevent infinite loops:

```
_instantiation_stack = [
    "myapp.Service",      # Currently instantiating
    "myapp.Database",     # Which needs
    "myapp.Service"       # Circular reference detected!
]
```

## Dependency Injection

### How It Works

The dependency injection system automatically provides required constructor
parameters:

```python
# 1. Register dependencies
register_dependency("database", shared_db)
register_dependency(Logger, shared_logger)

# 2. Define a class that needs these dependencies
class Service:
    def __init__(self, name: str, database: Database, logger: Logger):
        self.name = name
        self.database = database
        self.logger = logger

# 3. Instantiate without specifying dependencies
service = instantiate({
    "_target_": "myapp.Service",
    "name": "UserService"
    # database and logger are automatically injected!
})
```

### Injection Process Visualization

```
Constructor Signature Analysis:
┌────────────────────┐
│ Service.__init__   │
├────────────────────┤
│ Parameters:        │
│ - name: str ✗      │ (provided in config)
│ - database: DB ✓   │ (injected by name)
│ - logger: Logger ✓ │ (injected by type)
└────────────────────┘
```

### Injection Strategies

1. **Name-based injection**: Matches parameter names

    ```python
    register_dependency("database", db_instance)
    # Injects into any parameter named "database"
    ```

2. **Type-based injection**: Matches parameter type annotations
    ```python
    register_dependency(Database, db_instance)
    # Injects into any parameter typed as Database
    ```

### Type Matching Safety

The `_types_match_semantically` function ensures safe type matching:

```python
# Safe matches (same class, different imports):
collections.Counter == Counter  # True

# Dangerous matches prevented:
psycopg2.Connection != asyncpg.Connection  # False (different libraries!)
```

## Code Examples

### Basic Instantiation

```python
from frostbound.pydanticonf import instantiate

# Simple object creation
config = {
    "_target_": "pathlib.Path",
    "path": "/tmp/example"
}
path_obj = instantiate(config)
print(type(path_obj))  # <class 'pathlib.Path'>
```

### Using DynamicConfig for Type Safety

```python
from frostbound.pydanticonf import DynamicConfig

class Database:
    def __init__(self, host: str, port: int = 5432):
        self.host = host
        self.port = port

class DatabaseConfig(DynamicConfig[Database]):
    host: str
    port: int = 5432

# Type-safe instantiation
config = DatabaseConfig(
    _target_="myapp.Database",
    host="localhost",
    port=3306
)
db = instantiate(config)  # Return type is Database
```

### Complex Nested Configuration

```python
# Define your classes
class Logger:
    def __init__(self, name: str, level: str = "INFO"):
        self.name = name
        self.level = level

class Database:
    def __init__(self, host: str, port: int = 5432):
        self.host = host
        self.port = port

class Service:
    def __init__(self, name: str, database: Database, logger: Logger):
        self.name = name
        self.database = database
        self.logger = logger

# Configuration with nested objects
service_config = {
    "_target_": "myapp.Service",
    "name": "UserService",
    "database": {
        "_target_": "myapp.Database",
        "host": "db.example.com",
        "port": 3306
    },
    "logger": {
        "_target_": "myapp.Logger",
        "name": "service_logger",
        "level": "DEBUG"
    }
}

# Instantiate - all nested objects are created automatically
service = instantiate(service_config)
print(f"Service: {service.name}")
print(f"DB: {service.database.host}:{service.database.port}")
print(f"Logger: {service.logger.name} ({service.logger.level})")
```

### Dependency Injection Example

```python
from frostbound.pydanticonf import register_dependency, instantiate

# Setup shared resources
shared_db = Database("prod.server", 5432)
app_logger = Logger("app", "INFO")

register_dependency("database", shared_db)
register_dependency("logger", app_logger)

# Multiple services can share the same dependencies
user_service = instantiate({
    "_target_": "myapp.Service",
    "name": "UserService"
    # database and logger are automatically injected
})

order_service = instantiate({
    "_target_": "myapp.Service",
    "name": "OrderService"
    # Same database and logger instances are injected
})

# Verify they share the same instances
assert user_service.database is order_service.database
assert user_service.logger is order_service.logger
```

### Partial Instantiation (Factory Pattern)

```python
# Create a factory function using _partial_
logger_factory = instantiate({
    "_target_": "myapp.Logger",
    "_partial_": True,
    "level": "ERROR"  # Default level for all loggers
})

# Use the factory to create multiple instances
app_logger = logger_factory(name="app")
db_logger = logger_factory(name="database")
api_logger = logger_factory(name="api")

# All have the same default level
assert app_logger.level == "ERROR"
assert db_logger.level == "ERROR"
```

### Using Positional Arguments

```python
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

# Using _args_ for positional arguments
point = instantiate({
    "_target_": "myapp.Point",
    "_args_": [3.14, 2.71]
})
print(f"Point: ({point.x}, {point.y})")  # Point: (3.14, 2.71)
```

### Integration with YAML Configuration

```yaml
# config.yaml
app:
    _target_: "myapp.Service"
    name: "WebService"
    database:
        _target_: "myapp.Database"
        host: "${DB_HOST:localhost}"
        port: ${DB_PORT:5432}
    logger:
        _target_: "myapp.Logger"
        name: "web_logger"
        level: "${LOG_LEVEL:INFO}"
```

```python
from frostbound.pydanticonf import ConfigLoader, YamlConfigSource, instantiate
import os

# Set environment variables
os.environ.update({
    "DB_HOST": "prod.server",
    "LOG_LEVEL": "DEBUG"
})

# Load and instantiate from YAML
loader = ConfigLoader([YamlConfigSource("config.yaml")])
config_data = loader.load()
app = instantiate(config_data["app"])

print(f"App: {app.name}")              # App: WebService
print(f"DB: {app.database.host}")      # DB: prod.server
print(f"Logger: {app.logger.level}")   # Logger: DEBUG
```

## Error Handling

The system provides comprehensive error handling with `InstantiationError`:

```
InstantiationError
├── message: Human-readable error description
├── target: "myapp.Class" (what failed to instantiate)
├── config_path: "services.database" (location in config hierarchy)
└── original_error: ImportError(...) (underlying cause)
```

### Common Error Scenarios

```python
# Missing _target_
try:
    instantiate({"host": "localhost"})
except InstantiationError as e:
    print(e)  # Error: No _target_ specified in configuration

# Invalid target
try:
    instantiate({"_target_": "nonexistent.module.Class"})
except InstantiationError as e:
    print(e)  # Error: Failed to import nonexistent.module.Class

# Circular dependency
try:
    instantiate({
        "_target_": "myapp.A",
        "b": {"_target_": "myapp.B", "a": {"_target_": "myapp.A"}}
    })
except InstantiationError as e:
    print(e)  # Error: Circular dependency detected: myapp.A -> myapp.B -> myapp.A
```

## Design Patterns

The module implements several sophisticated design patterns:

### 1. Strategy Pattern

-   `DependencyResolver` uses injection strategies
-   Allows different algorithms for dependency resolution

### 2. Factory Pattern

-   Dynamic object creation based on configuration
-   Support for partial functions as factories

### 3. Chain of Responsibility

-   Injection strategies are tried in order
-   First successful strategy wins

### 4. Context Pattern

-   `_instantiation_stack` tracks current context
-   Enables circular dependency detection

### 5. Facade Pattern

-   Simple `instantiate()` function hides complexity
-   Clean API for users

## Best Practices

1. **Use DynamicConfig for type safety** when you know the target type at
   compile time
2. **Register shared dependencies by name** for better reliability
3. **Keep configurations simple** - deeply nested configs can be hard to debug
4. **Use environment variables** for environment-specific values
5. **Clear dependencies in tests** to avoid pollution between test cases

## Summary

The Frostbound instantiation system provides a powerful, type-safe way to create
complex object graphs from configuration. It combines the flexibility of dynamic
languages with the safety of static typing where possible, making it ideal for
building configurable applications.

The thoughtful design handles edge cases like circular dependencies and type
mismatches while providing clear error messages to help developers debug issues
quickly.
