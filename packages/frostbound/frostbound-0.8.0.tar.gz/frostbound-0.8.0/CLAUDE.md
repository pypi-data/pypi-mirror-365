# Python Type System & Framework Design Guide

This guide establishes principles for building robust, type-safe Python
frameworks and libraries with emphasis on modern type system features,
architectural patterns, and tooling standards.

## Core Philosophy

Build **small, strongly-typed cores** that are:

-   Fully type-safe with zero mypy/pyright errors
-   Extensible through well-defined protocols
-   Testable without mocks or stubs
-   Self-documenting through types and structure

## 1. Type System Mastery

### TypeVar Fundamentals

#### Basic TypeVars

```python
from typing import TypeVar, Generic, Protocol, overload
from collections.abc import Callable, Iterable, Iterator

T = TypeVar('T')
T_co = TypeVar('T_co', covariant=True)
T_contra = TypeVar('T_contra', contravariant=True)

def identity(x: T) -> T:
    return x

def first(items: Iterable[T]) -> T | None:
    return next(iter(items), None)
```

#### Bounded TypeVars

```python
from typing import TypeVar
from abc import ABC, abstractmethod

class Comparable(Protocol):
    def __lt__(self, other: Self) -> bool: ...
    def __le__(self, other: Self) -> bool: ...

TComparable = TypeVar('TComparable', bound=Comparable)

def get_min(items: Iterable[TComparable]) -> TComparable | None:
    iterator = iter(items)
    try:
        minimum = next(iterator)
    except StopIteration:
        return None

    for item in iterator:
        if item < minimum:
            minimum = item
    return minimum
```

#### Constrained TypeVars

```python
from decimal import Decimal

TNumber = TypeVar('TNumber', int, float, Decimal)

def precision_sum(values: Iterable[TNumber]) -> TNumber:
    result = sum(values)
    return type(next(iter(values)))(result) if values else 0
```

### Generic Classes

#### Basic Generic Pattern

```python
from typing import Generic, TypeVar

K = TypeVar('K')
V = TypeVar('V')

class Registry(Generic[K, V]):
    def __init__(self) -> None:
        self._items: dict[K, V] = {}

    def register(self, key: K, value: V) -> None:
        self._items[key] = value

    def get(self, key: K) -> V | None:
        return self._items.get(key)

    def get_or_raise(self, key: K) -> V:
        if key not in self._items:
            raise KeyError(f"No item registered for key: {key}")
        return self._items[key]
```

#### Multiple Type Parameters

```python
from typing import Generic, TypeVar, Protocol

TInput = TypeVar('TInput', contravariant=True)
TOutput = TypeVar('TOutput', covariant=True)
TState = TypeVar('TState')

class Processor(Generic[TInput, TOutput, TState]):
    def __init__(self, initial_state: TState) -> None:
        self.state = initial_state

    def process(self, input_value: TInput) -> TOutput:
        raise NotImplementedError

    def reset(self, state: TState) -> None:
        self.state = state
```

### Protocol-Based Design

#### Defining Protocols

```python
from typing import Protocol, runtime_checkable
from collections.abc import Iterator

@runtime_checkable
class Serializable(Protocol):
    def serialize(self) -> bytes: ...

    @classmethod
    def deserialize(cls, data: bytes) -> Self: ...

class DataStore(Protocol[T]):
    def save(self, key: str, value: T) -> None: ...
    def load(self, key: str) -> T | None: ...
    def delete(self, key: str) -> bool: ...
    def list_keys(self) -> Iterator[str]: ...
```

#### Advanced Protocol Patterns

```python
from typing import Protocol, TypeVar, ContextManager
from collections.abc import Callable

TResource = TypeVar('TResource')

class ResourceManager(Protocol[TResource]):
    def acquire(self) -> TResource: ...
    def release(self, resource: TResource) -> None: ...

    def __enter__(self) -> TResource:
        return self.acquire()

    def __exit__(self, *args: object) -> None:
        self.release(self._resource)

class AsyncResourceManager(Protocol[TResource]):
    async def acquire(self) -> TResource: ...
    async def release(self, resource: TResource) -> None: ...

    async def __aenter__(self) -> TResource: ...
    async def __aexit__(self, *args: object) -> None: ...
```

### Function Overloading

#### Basic Overloads

```python
from typing import overload, Literal
from pathlib import Path

@overload
def read_data(source: str) -> str: ...

@overload
def read_data(source: Path) -> str: ...

@overload
def read_data(source: str, *, as_bytes: Literal[True]) -> bytes: ...

@overload
def read_data(source: Path, *, as_bytes: Literal[True]) -> bytes: ...

def read_data(source: str | Path, *, as_bytes: bool = False) -> str | bytes:
    path = Path(source) if isinstance(source, str) else source
    return path.read_bytes() if as_bytes else path.read_text()
```

#### Complex Overload Patterns

```python
from typing import overload, TypeVar, Type
from collections.abc import Callable

T = TypeVar('T')

@overload
def create_instance(cls: Type[T]) -> T: ...

@overload
def create_instance(cls: Type[T], *args: object) -> T: ...

@overload
def create_instance(
    cls: Type[T],
    factory: Callable[[], T]
) -> T: ...

def create_instance(
    cls: Type[T],
    *args: object,
    factory: Callable[[], T] | None = None
) -> T:
    if factory is not None:
        return factory()
    return cls(*args)
```

### Type Guards and Narrowing

```python
from typing import TypeGuard, TypeVar
from collections.abc import Iterable

T = TypeVar('T')

def is_not_none(value: T | None) -> TypeGuard[T]:
    return value is not None

def filter_none(items: Iterable[T | None]) -> list[T]:
    return [item for item in items if is_not_none(item)]

def is_string_list(value: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(item, str) for item in value)
```

### ParamSpec for Decorators

```python
from typing import ParamSpec, TypeVar, Callable
from functools import wraps
import time

P = ParamSpec('P')
R = TypeVar('R')

def timed(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

def retry(max_attempts: int = 3) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exception: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(2 ** attempt)
            raise last_exception or RuntimeError("Unexpected error")
        return wrapper
    return decorator
```

## 2. Framework Design Principles

### Plugin Architecture

```python
from typing import Protocol, TypeVar, Generic
from collections.abc import Iterator
import importlib
import pkgutil

T = TypeVar('T')

class Plugin(Protocol):
    name: str
    version: str

    def initialize(self) -> None: ...
    def cleanup(self) -> None: ...

class PluginRegistry(Generic[T]):
    def __init__(self) -> None:
        self._plugins: dict[str, T] = {}

    def register(self, plugin: T) -> None:
        if hasattr(plugin, 'name'):
            self._plugins[plugin.name] = plugin

    def get(self, name: str) -> T | None:
        return self._plugins.get(name)

    def all(self) -> Iterator[T]:
        return iter(self._plugins.values())

    def load_plugins(self, package_name: str) -> None:
        package = importlib.import_module(package_name)
        for _, module_name, _ in pkgutil.iter_modules(
            package.__path__,
            f"{package_name}."
        ):
            module = importlib.import_module(module_name)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type) and
                    issubclass(attr, Plugin) and
                    attr is not Plugin
                ):
                    self.register(attr())
```

### Dependency Injection

```python
from typing import TypeVar, Type, Any, get_type_hints
from collections.abc import Callable

T = TypeVar('T')

class Container:
    def __init__(self) -> None:
        self._services: dict[Type[Any], Any] = {}
        self._factories: dict[Type[Any], Callable[[], Any]] = {}

    def register(self, service_type: Type[T], instance: T) -> None:
        self._services[service_type] = instance

    def register_factory(
        self,
        service_type: Type[T],
        factory: Callable[[], T]
    ) -> None:
        self._factories[service_type] = factory

    def resolve(self, service_type: Type[T]) -> T:
        if service_type in self._services:
            return self._services[service_type]

        if service_type in self._factories:
            instance = self._factories[service_type]()
            self._services[service_type] = instance
            return instance

        return self._auto_resolve(service_type)

    def _auto_resolve(self, service_type: Type[T]) -> T:
        hints = get_type_hints(service_type.__init__)
        dependencies = {
            name: self.resolve(hint)
            for name, hint in hints.items()
            if name != 'return'
        }
        return service_type(**dependencies)
```

### Configuration Management

```python
from typing import TypeVar, Type, Generic
from pydantic import BaseModel, Field
from pathlib import Path
import json
import yaml

T = TypeVar('T', bound=BaseModel)

class ConfigLoader(Generic[T]):
    def __init__(self, config_class: Type[T]) -> None:
        self.config_class = config_class

    def from_file(self, path: Path) -> T:
        if path.suffix == '.json':
            data = json.loads(path.read_text())
        elif path.suffix in {'.yaml', '.yml'}:
            data = yaml.safe_load(path.read_text())
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")

        return self.config_class(**data)

    def from_env(self, prefix: str = "") -> T:
        return self.config_class(_env_prefix=prefix)

class AppConfig(BaseModel):
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    max_workers: int = Field(default=4, ge=1, le=32)

    class Config:
        env_prefix = "APP_"
```

### Error Handling Hierarchy

```python
from typing import Any, TypeVar, Generic
from collections.abc import Sequence

class FrameworkError(Exception):
    """Base exception for framework errors"""

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.context = context or {}

class ValidationError(FrameworkError):
    """Raised when validation fails"""

    def __init__(self, field: str, value: Any, message: str) -> None:
        super().__init__(
            f"Validation failed for field '{field}': {message}",
            {"field": field, "value": value}
        )

class ConfigurationError(FrameworkError):
    """Raised when configuration is invalid"""
    pass

class PluginError(FrameworkError):
    """Raised when plugin operations fail"""

    def __init__(self, plugin_name: str, message: str) -> None:
        super().__init__(
            f"Plugin '{plugin_name}' error: {message}",
            {"plugin": plugin_name}
        )

T = TypeVar('T')

class Result(Generic[T]):
    def __init__(self, value: T | None = None, error: Exception | None = None) -> None:
        self._value = value
        self._error = error

    def is_ok(self) -> bool:
        return self._error is None

    def unwrap(self) -> T:
        if self._error:
            raise self._error
        return self._value  # type: ignore

    def unwrap_or(self, default: T) -> T:
        return self._value if self.is_ok() else default
```

## 3. Modern Python Patterns

### Builder Pattern with Fluent Interface

```python
from typing import Self, TypeVar, Generic
from dataclasses import dataclass, field

T = TypeVar('T')

@dataclass
class QueryBuilder:
    _select: list[str] = field(default_factory=list)
    _from: str = ""
    _where: list[str] = field(default_factory=list)
    _order_by: list[str] = field(default_factory=list)
    _limit: int | None = None

    def select(self, *columns: str) -> Self:
        self._select.extend(columns)
        return self

    def from_(self, table: str) -> Self:
        self._from = table
        return self

    def where(self, condition: str) -> Self:
        self._where.append(condition)
        return self

    def order_by(self, column: str, desc: bool = False) -> Self:
        order = f"{column} DESC" if desc else column
        self._order_by.append(order)
        return self

    def limit(self, n: int) -> Self:
        self._limit = n
        return self

    def build(self) -> str:
        query = f"SELECT {', '.join(self._select) or '*'}"
        query += f" FROM {self._from}"

        if self._where:
            query += f" WHERE {' AND '.join(self._where)}"

        if self._order_by:
            query += f" ORDER BY {', '.join(self._order_by)}"

        if self._limit is not None:
            query += f" LIMIT {self._limit}"

        return query
```

### Context Manager Patterns

```python
from typing import TypeVar, Generic, ContextManager
from contextlib import contextmanager
import time
from pathlib import Path
import tempfile
import shutil

T = TypeVar('T')

@contextmanager
def timed_operation(name: str) -> Iterator[None]:
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"{name} took {elapsed:.4f} seconds")

@contextmanager
def temporary_directory() -> Iterator[Path]:
    temp_dir = Path(tempfile.mkdtemp())
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)

class Transaction(Generic[T]):
    def __init__(self, target: T) -> None:
        self.target = target
        self._checkpoint: Any = None

    def __enter__(self) -> T:
        if hasattr(self.target, 'save_state'):
            self._checkpoint = self.target.save_state()
        return self.target

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is not None and hasattr(self.target, 'restore_state'):
            self.target.restore_state(self._checkpoint)
```

### Descriptor Patterns

```python
from typing import TypeVar, Generic, Type, overload
from weakref import WeakKeyDictionary

T = TypeVar('T')

class Cached(Generic[T]):
    def __init__(self, func: Callable[[Any], T]) -> None:
        self.func = func
        self.cache: WeakKeyDictionary[object, T] = WeakKeyDictionary()

    @overload
    def __get__(self, obj: None, objtype: Type[Any]) -> Self: ...

    @overload
    def __get__(self, obj: object, objtype: Type[Any]) -> T: ...

    def __get__(self, obj: object | None, objtype: Type[Any]) -> Self | T:
        if obj is None:
            return self

        if obj not in self.cache:
            self.cache[obj] = self.func(obj)

        return self.cache[obj]

class Validated(Generic[T]):
    def __init__(
        self,
        validator: Callable[[T], bool],
        error_message: str = "Validation failed"
    ) -> None:
        self.validator = validator
        self.error_message = error_message
        self.values: WeakKeyDictionary[object, T] = WeakKeyDictionary()

    def __set_name__(self, owner: Type[Any], name: str) -> None:
        self.name = name

    def __get__(self, obj: object | None, objtype: Type[Any]) -> T:
        if obj is None:
            return self  # type: ignore
        return self.values.get(obj)  # type: ignore

    def __set__(self, obj: object, value: T) -> None:
        if not self.validator(value):
            raise ValueError(f"{self.name}: {self.error_message}")
        self.values[obj] = value
```

### Functional Patterns

```python
from typing import TypeVar, Callable
from functools import reduce, partial
from collections.abc import Iterable

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')

def compose(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    return lambda x: f(g(x))

def pipe(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    return reduce(compose, funcs)

def curry(func: Callable[..., T]) -> Callable[..., T | Callable[..., T]]:
    def curried(*args: Any, **kwargs: Any) -> T | Callable[..., T]:
        if len(args) + len(kwargs) >= func.__code__.co_argcount:
            return func(*args, **kwargs)
        return partial(func, *args, **kwargs)
    return curried

@curry
def map_reduce(
    mapper: Callable[[A], B],
    reducer: Callable[[B, B], B],
    items: Iterable[A]
) -> B:
    mapped = map(mapper, items)
    return reduce(reducer, mapped)
```

## 4. Code Organization

### Module Structure for Frameworks

```text
myframework/
    __init__.py          # Public API exports
    __version__.py       # Single source of version
    core/                # Core functionality
        __init__.py
        types.py        # Type definitions, protocols
        exceptions.py   # Exception hierarchy
        constants.py    # Framework constants
    api/                 # Public API
        __init__.py
        decorators.py   # Public decorators
        builders.py     # Builder interfaces
    internal/           # Internal implementation
        __init__.py
        _utils.py      # Private utilities
        _registry.py   # Internal registries
    plugins/            # Plugin system
        __init__.py
        base.py        # Plugin protocols
        loader.py      # Plugin loading
    ext/               # Optional extensions
        __init__.py
        async/         # Async support
            __init__.py
```

### Public API Design

```python
# myframework/__init__.py
from myframework.api.decorators import (
    cached,
    validated,
    timed,
)
from myframework.api.builders import (
    ConfigBuilder,
    QueryBuilder,
)
from myframework.core.types import (
    Plugin,
    Processor,
    Result,
)
from myframework.core.exceptions import (
    FrameworkError,
    ValidationError,
    ConfigurationError,
)

__all__ = [
    # Decorators
    "cached",
    "validated",
    "timed",
    # Builders
    "ConfigBuilder",
    "QueryBuilder",
    # Types
    "Plugin",
    "Processor",
    "Result",
    # Exceptions
    "FrameworkError",
    "ValidationError",
    "ConfigurationError",
]

# Version
from myframework.__version__ import __version__
```

### Internal vs External Interfaces

```python
# Public interface (myframework/api/client.py)
from typing import Protocol
from myframework.internal._client import ClientImpl

class Client(Protocol):
    def connect(self, host: str, port: int) -> None: ...
    def disconnect(self) -> None: ...
    def send(self, data: bytes) -> None: ...
    def receive(self, size: int) -> bytes: ...

def create_client() -> Client:
    return ClientImpl()

# Internal implementation (myframework/internal/_client.py)
import socket
from typing import Final

class ClientImpl:
    _BUFFER_SIZE: Final = 4096

    def __init__(self) -> None:
        self._socket: socket.socket | None = None

    def connect(self, host: str, port: int) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))

    def disconnect(self) -> None:
        if self._socket:
            self._socket.close()
            self._socket = None

    def send(self, data: bytes) -> None:
        if not self._socket:
            raise RuntimeError("Not connected")
        self._socket.sendall(data)

    def receive(self, size: int) -> bytes:
        if not self._socket:
            raise RuntimeError("Not connected")
        return self._socket.recv(min(size, self._BUFFER_SIZE))
```

## 5. Tooling Configuration

### Strict Type Checking

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

# Per-module options
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[tool.pyright]
include = ["src"]
exclude = ["**/node_modules", "**/__pycache__"]
defineConstant = { DEBUG = true }
reportMissingImports = true
reportMissingTypeStubs = false
pythonVersion = "3.12"
pythonPlatform = "Linux"
typeCheckingMode = "strict"
useLibraryCodeForTypes = true
reportUnusedImport = true
reportUnusedClass = true
reportUnusedFunction = true
reportUnusedVariable = true
reportDuplicateImport = true
reportOptionalSubscript = true
reportOptionalMemberAccess = true
reportOptionalCall = true
reportOptionalIterable = true
reportOptionalContextManager = true
reportOptionalOperand = true
reportUnnecessaryIsInstance = true
reportUnnecessaryCast = true
reportUnnecessaryComparison = true
reportAssertAlwaysTrue = true
reportSelfClsParameterName = true
reportUnusedExpression = true
reportUnnecessaryTypeIgnoreComment = true
reportMatchNotExhaustive = true
```

### Comprehensive Linting

```toml
[tool.ruff]
line-length = 88
target-version = "py312"
src = ["src"]

[tool.ruff.lint]
select = [
    "F",     # Pyflakes
    "E",     # pycodestyle errors
    "W",     # pycodestyle warnings
    "C90",   # McCabe complexity
    "I",     # isort
    "N",     # pep8-naming
    "UP",    # pyupgrade
    "YTT",   # flake8-2020
    "ANN",   # flake8-annotations
    "S",     # flake8-bandit
    "BLE",   # flake8-blind-except
    "FBT",   # flake8-boolean-trap
    "B",     # flake8-bugbear
    "A",     # flake8-builtins
    "COM",   # flake8-commas
    "C4",    # flake8-comprehensions
    "DTZ",   # flake8-datetimez
    "T10",   # flake8-debugger
    "EXE",   # flake8-executable
    "ISC",   # flake8-implicit-str-concat
    "ICN",   # flake8-import-conventions
    "G",     # flake8-logging-format
    "INP",   # flake8-no-pep420
    "PIE",   # flake8-pie
    "T20",   # flake8-print
    "PYI",   # flake8-pyi
    "PT",    # flake8-pytest-style
    "Q",     # flake8-quotes
    "RSE",   # flake8-raise
    "RET",   # flake8-return
    "SLF",   # flake8-self
    "SLOT",  # flake8-slots
    "SIM",   # flake8-simplify
    "TID",   # flake8-tidy-imports
    "TCH",   # flake8-type-checking
    "ARG",   # flake8-unused-arguments
    "PTH",   # flake8-use-pathlib
    "ERA",   # eradicate
    "PGH",   # pygrep-hooks
    "PL",    # Pylint
    "TRY",   # tryceratops
    "FLY",   # flynt
    "PERF",  # Perflint
    "FURB",  # refurb
    "LOG",   # flake8-logging
    "RUF",   # Ruff-specific rules
]
ignore = [
    "E501",   # Line length handled by formatter
    "ANN101", # Missing type annotation for self
    "ANN102", # Missing type annotation for cls
    "ANN401", # Dynamically typed expressions (Any)
    "S101",   # Use of assert detected
    "B008",   # Do not perform function calls in argument defaults
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101", "ANN", "D"]
"__init__.py" = ["F401"]

[tool.ruff.lint.pylint]
max-args = 5
max-branches = 12
max-returns = 6
max-statements = 50

[tool.ruff.lint.mccabe]
max-complexity = 10

[tool.ruff.lint.isort]
known-first-party = ["myframework"]
force-single-line = true
lines-after-imports = 2

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
```

### Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
    - repo: https://github.com/astral-sh/ruff-pre-commit
      rev: v0.8.0
      hooks:
          - id: ruff
            args: [--fix]
          - id: ruff-format

    - repo: https://github.com/pre-commit/mirrors-mypy
      rev: v1.13.0
      hooks:
          - id: mypy
            additional_dependencies: [types-all]
            args: [--strict]

    - repo: https://github.com/microsoft/pyright
      rev: v1.1.350
      hooks:
          - id: pyright

    - repo: https://github.com/pre-commit/pre-commit-hooks
      rev: v5.0.0
      hooks:
          - id: check-yaml
          - id: check-toml
          - id: check-json
          - id: end-of-file-fixer
          - id: trailing-whitespace
          - id: check-case-conflict
          - id: check-merge-conflict
          - id: detect-private-key
```

## 6. Performance & Async Patterns

### Lazy Evaluation

```python
from typing import TypeVar, Generic, Callable
from functools import cached_property

T = TypeVar('T')

class Lazy(Generic[T]):
    def __init__(self, factory: Callable[[], T]) -> None:
        self._factory = factory
        self._value: T | None = None
        self._computed = False

    def get(self) -> T:
        if not self._computed:
            self._value = self._factory()
            self._computed = True
        return self._value  # type: ignore

class LazyChain(Generic[T]):
    def __init__(self, initial: T) -> None:
        self._value = initial
        self._operations: list[Callable[[Any], Any]] = []

    def map(self, func: Callable[[T], Any]) -> Self:
        self._operations.append(func)
        return self

    def filter(self, predicate: Callable[[Any], bool]) -> Self:
        def filter_op(value: Any) -> Any:
            return value if predicate(value) else None
        self._operations.append(filter_op)
        return self

    def compute(self) -> Any:
        result = self._value
        for op in self._operations:
            result = op(result)
            if result is None:
                break
        return result
```

### Memory-Efficient Patterns

```python
from typing import Iterator, TypeVar, Iterable
from collections.abc import Generator
import sys

T = TypeVar('T')

def chunked(iterable: Iterable[T], size: int) -> Iterator[list[T]]:
    iterator = iter(iterable)
    while chunk := list(itertools.islice(iterator, size)):
        yield chunk

def sliding_window(iterable: Iterable[T], size: int) -> Iterator[tuple[T, ...]]:
    iterator = iter(iterable)
    window = tuple(itertools.islice(iterator, size))
    if len(window) == size:
        yield window
    for item in iterator:
        window = window[1:] + (item,)
        yield window

class StreamProcessor(Generic[T]):
    def __init__(self, chunk_size: int = 1000) -> None:
        self.chunk_size = chunk_size

    def process_file(
        self,
        filepath: Path,
        processor: Callable[[T], None]
    ) -> None:
        with open(filepath, 'r') as f:
            for chunk in chunked(f, self.chunk_size):
                for line in chunk:
                    processor(self._parse_line(line))

    def _parse_line(self, line: str) -> T:
        raise NotImplementedError
```

### Async Patterns Without Web Context

```python
import asyncio
from typing import TypeVar, Protocol, Coroutine
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

T = TypeVar('T')

class AsyncProcessor(Protocol[T]):
    async def process(self, item: T) -> T: ...

class Pipeline(Generic[T]):
    def __init__(self) -> None:
        self._processors: list[AsyncProcessor[T]] = []

    def add_processor(self, processor: AsyncProcessor[T]) -> Self:
        self._processors.append(processor)
        return self

    async def execute(self, items: AsyncIterator[T]) -> AsyncIterator[T]:
        async for item in items:
            result = item
            for processor in self._processors:
                result = await processor.process(result)
            yield result

@asynccontextmanager
async def managed_task_group() -> AsyncIterator[list[asyncio.Task[Any]]]:
    tasks: list[asyncio.Task[Any]] = []
    try:
        yield tasks
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

async def rate_limited(
    coros: list[Coroutine[Any, Any, T]],
    max_concurrent: int = 10
) -> list[T]:
    semaphore = asyncio.Semaphore(max_concurrent)

    async def limited_coro(coro: Coroutine[Any, Any, T]) -> T:
        async with semaphore:
            return await coro

    return await asyncio.gather(*[limited_coro(coro) for coro in coros])
```

### Caching Strategies

```python
from typing import TypeVar, Callable, Hashable
from functools import lru_cache, wraps
import time
from collections import OrderedDict
from weakref import WeakValueDictionary

K = TypeVar('K', bound=Hashable)
V = TypeVar('V')

class TTLCache(Generic[K, V]):
    def __init__(self, maxsize: int = 128, ttl: float = 600) -> None:
        self.maxsize = maxsize
        self.ttl = ttl
        self._cache: OrderedDict[K, tuple[V, float]] = OrderedDict()

    def get(self, key: K) -> V | None:
        if key not in self._cache:
            return None

        value, timestamp = self._cache[key]
        if time.time() - timestamp > self.ttl:
            del self._cache[key]
            return None

        self._cache.move_to_end(key)
        return value

    def set(self, key: K, value: V) -> None:
        self._cache[key] = (value, time.time())
        self._cache.move_to_end(key)

        if len(self._cache) > self.maxsize:
            self._cache.popitem(last=False)

def memoize_weak(func: Callable[[T], V]) -> Callable[[T], V]:
    cache: WeakValueDictionary[int, V] = WeakValueDictionary()

    @wraps(func)
    def wrapper(obj: T) -> V:
        obj_id = id(obj)
        if obj_id not in cache:
            cache[obj_id] = func(obj)
        return cache[obj_id]

    return wrapper
```

## Project Commands

### Running Type Checks

```bash
# Install dependencies
uv venv --python 3.12
source .venv/bin/activate
uv sync

# Run type checkers
uv run mypy src/
uv run pyright src/

# Run linting
uv run ruff check .
uv run ruff format .
```

### Pre-commit Setup

```bash
# Install pre-commit
uv add --dev pre-commit

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

## Summary

This guide emphasizes:

1. **Type Safety First**: Leverage Python's type system fully with zero
   tolerance for type errors
2. **Protocol-Oriented Design**: Use protocols for flexible, testable
   architectures
3. **Clean Architecture**: Separate concerns with clear boundaries between
   layers
4. **Modern Patterns**: Embrace Python 3.12+ features and patterns
5. **Strict Tooling**: Configure tools for maximum strictness to catch issues
   early
6. **Performance Awareness**: Design with performance in mind from the start

Remember: A small, perfectly typed core is worth more than a large, loosely
typed system.
