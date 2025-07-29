from __future__ import annotations

import functools
import inspect
from typing import (
    Any,
    Callable,
    NotRequired,
    Protocol,
    TypeAlias,
    TypedDict,
    TypeVar,
)

from pydantic import BaseModel
from pydantic_settings import BaseSettings

T = TypeVar("T")
FactoryT = TypeVar("FactoryT", bound=BaseModel)
SettingsT = TypeVar("SettingsT", bound=BaseSettings)
InstanceT = TypeVar("InstanceT", bound=BaseModel)


class ConfigDict(TypedDict, total=False):
    """Structured configuration dictionary."""

    _target_: str
    _args_: NotRequired[list[Any]]
    _partial_: NotRequired[bool]
    _recursive_: NotRequired[bool]


ConfigData: TypeAlias = ConfigDict | dict[str, Any]
InitKwargs: TypeAlias = dict[str, Any]
MergeableDict: TypeAlias = dict[str, Any]

ModulePath: TypeAlias = str
ClassName: TypeAlias = str
ModuleClassPair: TypeAlias = tuple[ModulePath, ClassName]
PositionalArgs: TypeAlias = tuple[Any, ...]

TypeKeyDependencyStore: TypeAlias = dict[type[Any], Any]
NameKeyDependencyStore: TypeAlias = dict[str, Any]

InstantiableConfig: TypeAlias = BaseModel | ConfigDict
CallableTarget: TypeAlias = type[Any] | Callable[..., Any]
InjectionCandidate: TypeAlias = tuple[bool, Any]


class InjectionStrategy(Protocol):
    """Protocol for dependency injection strategies."""

    def resolve(
        self, param_name: str, param: inspect.Parameter, available_args: dict[str, Any]
    ) -> InjectionCandidate: ...


# TypedPartial is just functools.partial - we use it for clarity
TypedPartial = functools.partial

# Error message constants
ERROR_INVALID_TARGET_FORMAT = "Invalid target format: '{}'"
ERROR_INVALID_CALLABLE_TARGET = "'_target_' must be a callable object, got: {}"
ERROR_INVALID_CONFIG_TYPE = "Config must be a ConfigDict, BaseModel, or dict, got: {}"
ERROR_INSTANTIATION_FAILED = "Failed to instantiate '{}': {}"
ERROR_MODULE_NOT_FOUND = "Module '{}' not found"
ERROR_CLASS_NOT_FOUND = "Class '{}' not found in module '{}'"
ERROR_INVALID_ARGS_PARTIAL = "Cannot use both '_args_' and '_partial_=True'"
ERROR_MISSING_TARGET = "Config is missing required '_target_' field"
ERROR_INJECTION_FAILED = "Failed to inject dependency: {}"

# Constants for configuration
DEFAULT_MIN_LENGTH_TARGET = 1
DEFAULT_CACHE_ENABLED = True
