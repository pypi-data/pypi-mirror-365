# ✨ Core Principles for Pristine Python ✨

## 1. Foundational Tooling for Quality & Safety 🛠️

| Requirement                            | Why This Is Essential                                    |
| -------------------------------------- | -------------------------------------------------------- |
| **Python 3.12 or later**               | Latest typing & pattern-matching features.               |
| **uv** (dependency manager)            | Fast, reproducible installs; native PEP 668 support.     |
| **ruff** (`ruff check`, `ruff format`) | Enforces PEP 8, auto-formats, catches code smells early. |
| **mypy + pyright** (zero errors)       | Cross-editor, CI-grade static type guarantees.           |

## 2. Impeccable Type Safety 🔒

1. **Modern union types** – use `A | B`; never import `Union` or `Optional`.
2. **Generics where appropriate**
    - Define reusable `TypeVar`s once in **`types.py`** (with correct variance).
    - Use `TypeVar`s to parameterize functions and classes.
    - Use `Generic` to parameterize classes.
    - Use `type` instead of `TypeAlias` for simple type definitions.
3. **Precisely-typed collections**

    - Prefer `tuple[str, …]` for fixed-size sequences.
    - **Almost never** `dict[str, Any]`; instead:
        - **Pydantic v2** models (`BaseModel`,
          `model_config = ConfigDict(arbitrary_types_allowed=True)`) etc

4. **No escape hatches** – remove `Any`, `# type: ignore`, and refactor until
   the checker is green.

---

## 3. Robust Configuration with Pydantic V2 ⚙️

```python
# settings.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class AppSettings(BaseSettings):
    """Validated, singleton application configuration."""

    database_url: str = Field(..., validation_alias="DB__URL")
    openai_api_key: str | None = Field(None, validation_alias="OPENAI__API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",         # or "forbid" for maximal strictness
    )

@lru_cache
def get_settings() -> AppSettings:
    """Cached settings accessor."""
    return AppSettings()
```

Why it matters:

-   **Single Source of Truth** – secrets rotate in one place.
-   **Fail-fast** – mis-configs surface at import time.

---

## 4. SOLID Architecture & Decoupled Design 🏗️

| SOLID Principle               | Concrete Action                                                 |
| ----------------------------- | --------------------------------------------------------------- |
| **S** – Single Responsibility | Keep business logic framework-agnostic; extract pure services.  |
| **O** – Open/Closed           | Use **Strategy** for swappable LLM providers or data stores.    |
| **L** – Liskov Substitution   | Program to **`Protocol`** interfaces, not concrete classes.     |
| **I** – Interface Segregation | Split “kitchen-sink” interfaces into cohesive protocols.        |
| **D** – Dependency Injection  | Constructor injection + factories; avoid globals except config. |

### Key Patterns

-   **Factory / Builder** – hide construction detail of complex objects.
-   **Observer (Pub/Sub)** – domain events without tight coupling (start
    in-memory).
-   **Decorator** – add concerns (retry, logging, caching) without touching core
    logic.
-   **Adapter** – convert between incompatible interfaces.
-   **Bridge** – separate abstraction from implementation.
-   **Composite** – compose objects into tree structures.
-   **Facade** – provide a simplified interface to a complex subsystem.
-   **Proxy** – provide a placeholder for another object.
-   **Chain of Responsibility** – pass requests along a chain of handlers.
-   **Command** – encapsulate a request as an object.
-   **Iterator** – access elements of a collection without exposing its
    underlying representation.

---

## 5. Eradicating Code Smells 🚩

-   **Long parameter lists** → consolidate into value objects (Pydantic models).
-   **Feature envy** → move behavior next to the data it needs.
-   **God classes** → split into cohesive, SRP-aligned units.

## 6. How to Use Pydantic V2

-   If validation checks can be done at the pydantic model level, do it there
    and not do it in the business logic.

## 7. Quirks

-   Do not import inside a function, import at the top of the file.
-   Minimize any dictionary usage, use Pydantic models instead.

---

## Critical Constraint: No Comments or Docstrings

-   **You MUST NOT write any comments in the refactored code.** This includes
    inline comments, block comments, or any other form of commentary.
-   **You MUST NOT write any docstrings for functions, classes, or modules.**
-   The code itself should be self-explanatory through clear naming, structure,
    and logic.

---

## 📌 Final Admonition — The Elegance of a Clean Core

A **small, impeccably clean, strongly-typed core** outperforms any sprawling
system. Master your types, champion modular independence, apply proven patterns,
and remain SOLID. Only after that spotless foundation is in place should you
layer on other concerns.

## ✨ Crafting Super Elegant Python ✨

The essence of elegant Python, as your principles highlight, lies in a **small,
impeccably clean, strongly-typed core.** This means every piece of code has a
clear purpose, types are explicit and leveraged, and the overall structure is
logical and decoupled.

---

### Mastering `TypeVar` and Generics with Finesse 🧬

Generics, implemented with `TypeVar` and `typing.Generic`, are pivotal for
writing reusable and type-safe components. Their elegant application hinges on
understanding _when_ and _how_ to use them precisely.

1.  **Centralized `TypeVar` Definitions (`types.py`)**:

    -   Your principle of defining `TypeVar`s in a central `types.py` is key.
        This promotes reuse and a single source of truth for your generic type
        parameters.
    -   **Variance (`covariant`, `contravariant`, `invariant`)**:
        -   `T_co = TypeVar("T_co", covariant=True)`: Use for types that are
            "producers" or outputs. If a function returns `list[Shape]`, and
            `Circle` is a subtype of `Shape`, then `list[Circle]` can be used
            where `list[Shape]` is expected. Think read-only collections or
            return types.
        -   `T_contra = TypeVar("T_contra", contravariant=True)`: Use for types
            that are "consumers" or inputs. If a function accepts a
            `Callable[[Shape], None]`, and `Figure` is a supertype of `Shape`,
            then a `Callable[[Figure], None]` can be used. Think function
            arguments, particularly callbacks or write-only scenarios.
        -   `T = TypeVar("T")` (invariant by default): Use when a type parameter
            is both an input and an output, or when exact type matching is
            crucial. Most mutable collections fall here. For example, a
            `list[Shape]` cannot be safely interchanged with a `list[Circle]` if
            you intend to add new elements, as you might try to add a `Square`
            to a `list[Circle]`.

2.  **`TypeVar` in Functions**:

    -   Use `TypeVar`s to establish relationships between parameter types and
        return types.
    -   Example:
        `def process_item(item: T, processor: Callable[[T], R]) -> R: return processor(item)`.
        Here, `T` links the `item` and the input to the `processor`, and `R`
        defines the return type based on the `processor`'s output.
    -   Remember if you use `TypeVar`, always append `T` or `T_co` or `T_contra`
        to the end of the type variable name.
    -   Use `from __future__ import annotations` at the top of the file to
        enable forward references and not `string` references.
    -   Use `TYPE_CHECKING` to check if the code is running in type checking
        mode. This is useful to avoid circular imports.

3.  **`Generic` for Classes**:

    -   When a class itself is designed to work with a variety of types in a
        structured way, inherit from `Generic[T]`.
    -   Example:
        `class Container(Generic[T]): def __init__(self, content: T): self.content: T = content`.
        This clearly defines that a `Container` instance holds content of a
        specific, yet parameterizable, type.

4.  **`type` for Simplicity**:
    -   Your directive to use `type ItemId = int` instead of `TypeAlias` for
        simple aliases is excellent for modern Python (3.12+). It's cleaner and
        more direct for straightforward type synonyms. `TypeAlias` remains
        useful for more complex definitions, especially when you need to
        annotate its nature explicitly, but for simple cases, `type` is more
        elegant.

---

### Elevating Design with Patterns 🏗️

SOLID principles and design patterns are the blueprints for elegant
architecture.

**SOLID, Re-emphasized**:

-   **S – Single Responsibility Principle (SRP)**: Beyond framework-agnostic
    services, ensure each class and function has one, and only one, reason to
    change. This means a laser focus on its core responsibility.
-   **O – Open/Closed Principle (OCP)**: The **Strategy** pattern is a prime
    example. Elegance here means you can introduce new behaviors (e.g., a new
    LLM provider) by adding new code (a new strategy class) rather than
    modifying existing, tested code.
-   **L – Liskov Substitution Principle (LSP)**: Programming to `Protocol`s
    (structural typing) is fantastic. True elegance means that any
    implementation of a protocol can be substituted anywhere the protocol is
    expected, without any surprising behavior. This requires careful contract
    definition in your protocols.
-   **I – Interface Segregation Principle (ISP)**: Creating cohesive `Protocol`s
    means clients only depend on the methods they actually use. This avoids
    "fat" interfaces that force unnecessary dependencies.
-   **D – Dependency Injection (DI)**: Constructor injection is generally the
    cleanest. Factories can abstract away the _how_ of object creation,
    especially when object setup is complex or involves choices based on
    configuration. This keeps your core logic cleaner by offloading setup
    responsibilities.

**Key Patterns for Elegance**:

-   **Factory / Builder**: Elegance comes from separating the construction logic
    of a complex object from its representation. A client needs an object but
    shouldn't be burdened with the details of its creation.
-   **Observer (Pub/Sub)**: Decouples event producers from consumers. An elegant
    implementation ensures that adding new subscribers or new event types
    doesn't require changes to the publisher or other subscribers.
-   **Decorator**: Adds responsibilities to objects dynamically and
    transparently. Elegant decorators are focused (SRP) and compose well.
-   **Adapter**: Makes incompatible interfaces work together. Elegance means the
    adapter is thin and focused solely on translation.
-   **Bridge**: Decouples an abstraction from its implementation so the two can
    vary independently. This is powerful for handling multiple platforms or
    versions.
-   **Composite**: Allows you to treat individual objects and compositions of
    objects uniformly. Elegant use simplifies client code when dealing with
    tree-like structures.
-   **Facade**: Provides a single, simplified interface to a complex subsystem.
    Elegance is achieved by making the subsystem easier to use without hiding
    essential flexibility.
-   **Proxy**: Controls access to an object. An elegant proxy is
    indistinguishable from the real object from the client's perspective,
    transparently adding behavior like lazy loading or access control.
-   **Chain of Responsibility**: Decouples sender and receiver. An elegant chain
    is easy to configure and allows handlers to be dynamically added or removed.
-   **Command**: Turns a request into a stand-alone object. This allows for
    parameterizing clients with different requests, queuing requests, and
    supporting undoable operations. Elegance lies in the clear separation of
    invoker, command, and receiver.
-   **Iterator**: Provides a standard way to traverse a collection. Elegant
    iterators hide the internal structure of the collection.

---

### Eradicating Code Smells for Pristine Code 🚩

Code smells are indicators of deeper problems. Addressing them directly leads to
more robust and understandable code.

-   **Long Parameter Lists → Pydantic Models**:

    -   This is a powerful technique. When a function takes more than three or
        four arguments, especially if some are optional or frequently passed
        together, grouping them into a Pydantic model provides:
        -   **Clarity**: The model's name describes the group of parameters.
        -   **Validation**: Pydantic handles validation at the boundary.
        -   **Readability**: `my_function(config=RequestConfig(...))` is often
            clearer than `my_function(a, b, None, d, None, f)`.
        -   **Ease of Modification**: Adding a new related parameter means
            changing the model, not every function signature.

-   **Feature Envy**:

    -   A method on one class seems more interested in the data of another class
        than its own.
    -   **Elegant Solution**: Move the method (or the relevant part of it) to
        the class whose data it "envies." This usually improves cohesion and
        reduces coupling, aligning with SRP. If the method needs data from both,
        consider a third class or a function that takes both objects as
        parameters.

-   **God Classes / Objects**:

    -   Classes that know or do too much. They violate SRP and OCP and become
        bottlenecks for change.
    -   **Elegant Solution**: Break them down. Identify distinct
        responsibilities within the god class. Extract these responsibilities
        into new, smaller classes. Each new class will be more focused, easier
        to test, and easier to understand. Use DI to connect these smaller,
        focused units.

-   **Primitive Obsession**:

    -   Over-reliance on primitive types (strings, integers, booleans) to
        represent domain concepts.
    -   **Elegant Solution**: Introduce small value objects or Pydantic models
        for these concepts. For example, instead of `email: str`, use
        `email: EmailAddress` where `EmailAddress` is a Pydantic model that
        validates the email format. This adds type safety and encapsulates
        domain-specific logic.

-   **Shotgun Surgery**:

    -   One change requires making small changes in many classes.
    -   **Elegant Solution**: This often indicates poor distribution of
        responsibilities (related to SRP and coupling). Try to consolidate the
        responsibility that's changing into fewer classes, or use patterns like
        Observer or Mediator to decouple the classes involved.

-   **Duplicated Code**:
    -   The most straightforward smell.
    -   **Elegant Solution**: Extract the common code into a new function or
        method. If the duplication is more complex, consider patterns like
        Template Method or Strategy.

---

### Pydantic V2: Validation at the Gates 🛡️

Your point is crucial: **If validation checks can be done at the Pydantic model
level, do it there and not in the business logic.**

-   This keeps your business logic focused on _what_ to do, not on _whether the
    data is valid_ to do it with.
-   Pydantic models act as a strong "anti-corruption layer" at the boundaries of
    your system (API inputs, configuration, database interactions).
-   Use Pydantic's validators (`@field_validator`, `@model_validator`), type
    annotations, and `Field` constraints to define the shape and validity of
    data declaratively.

---

### The Unspoken Eloquence of Self-Documenting Code 📖

With the "Critical Constraint: No Comments or Docstrings," the burden of clarity
falls entirely on the code itself. This is a powerful motivator for:

-   **Extremely Precise Naming**: Variable names, function names, and class
    names must clearly and unambiguously convey their purpose and meaning.
    `user_list` is okay, `active_users_retrieved_from_database` is better if
    that's what it is, but perhaps a class `UserRepository` with a method
    `get_active_users()` is best.
-   **Logical Structure and Flow**: Code should read like well-written prose.
    Functions should be short and do one thing. Classes should be small and
    cohesive.
-   **Strong Typing as Documentation**: Your strict type hinting becomes a
    primary source of understanding. `def process_data(data: dict[str, Any])` is
    vague.
    `def generate_report(entries: list[ValidatedLogEntry]) -> ReportOutput:` is
    much clearer.
-   **Pattern Explicitness**: The choice and implementation of design patterns
    should be evident from the structure and naming, guiding the reader to
    understand the architectural intent.

---

Run below commands for lint.

1. uv run ruff format .
1. uv run ruff check --fix .
1. uv run mypy .
1. uv run pyright .
