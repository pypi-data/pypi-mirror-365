from __future__ import annotations

import warnings
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_settings import SettingsConfigDict
from typing_extensions import Self

from frostbound.pydanticonf import BaseSettingsWithInstantiation, DynamicConfig
from integration.mocks import LLM, AlignmentStrategy, Optimizer


class LanguageCode(str, Enum):
    EN = "en"
    DE = "de"


class MatchingStrategy(str, Enum):
    ONE_TO_ONE = "one_to_one"
    MANY_TO_ONE = "many_to_one"


class Models(str, Enum):
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4 = "gpt-4"
    GPT_3_5_TURBO = "gpt-3.5-turbo"


class SegmentType(str, Enum):
    SECTION_HEADER = "section_header"
    CAPTION = "caption"
    PARAGRAPH = "paragraph"
    TABLE = "table"


class DatabaseConfig(BaseModel):
    host: str
    port: int
    db: str
    username: str
    password: str = ""  # Will be filled from env


# Base aligner config with custom exclusions
class BaseAlignerConfig(DynamicConfig[AlignmentStrategy]):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    # Override to exclude project-specific fields from kwargs
    _exclude_from_kwargs: ClassVar[frozenset[str]] = frozenset(
        {
            "target_",
            "args_",
            "partial_",
            "recursive_",
            "enabled",
        }
    )

    enabled: bool = Field(default=True, description="Enable this aligner")
    require_type_match: bool = Field(default=False, description="Require segment types to match")


# Concrete aligner configurations
class ExactHashAlignerConfig(BaseAlignerConfig):
    target_: str = Field(default="mock_aligners.ExactHashAligner", alias="_target_")


class BacktranslationEmbeddingConfig(BaseAlignerConfig):
    target_: str = Field(default="mock_aligners.BacktranslationEmbedding", alias="_target_")
    threshold: float = Field(default=0.75, ge=0.0, le=1.0, description="Minimum similarity threshold")
    top_k: int = Field(default=1, gt=0, description="Maximum number of target candidates")
    max_concurrent_requests: int = Field(default=8, gt=0, description="Max concurrent API requests")
    source_language: LanguageCode = Field(default=LanguageCode.EN, description="Source language code")
    target_language: LanguageCode = Field(default=LanguageCode.DE, description="Target language code")
    model: Models = Field(default=Models.GPT_4O_MINI, description="OpenAI model to use for backtranslation")
    matching_strategy: MatchingStrategy = Field(default=MatchingStrategy.MANY_TO_ONE)

    @model_validator(mode="after")
    def validate_one_to_one_threshold(self) -> Self:
        if self.matching_strategy == MatchingStrategy.ONE_TO_ONE and self.threshold > 0:
            warnings.warn(
                f"ONE_TO_ONE matching strategy ignores threshold during search phase. "
                f"Your threshold={self.threshold} will be applied after optimal assignment. "
                f"This is required for the Hungarian algorithm to find globally optimal 1-to-1 matches.",
                UserWarning,
                stacklevel=2,
            )
        return self


class MultiLinguistEmbeddingConfig(BaseAlignerConfig):
    target_: str = Field(default="mock_aligners.MultiLinguistEmbedding", alias="_target_")
    threshold: float = Field(default=0.75, ge=0.0, le=1.0, description="Minimum similarity threshold")
    top_k: int = Field(default=1, gt=0, description="Maximum number of target candidates")
    matching_strategy: MatchingStrategy = Field(default=MatchingStrategy.MANY_TO_ONE)

    @model_validator(mode="after")
    def validate_one_to_one_threshold(self) -> Self:
        if self.matching_strategy == MatchingStrategy.ONE_TO_ONE and self.threshold > 0:
            warnings.warn(
                f"ONE_TO_ONE matching strategy ignores threshold during search phase. "
                f"Your threshold={self.threshold} will be applied after optimal assignment. "
                f"This is required for the Hungarian algorithm to find globally optimal 1-to-1 matches.",
                UserWarning,
                stacklevel=2,
            )
        return self


class LanguageModelAlignerConfig(BaseAlignerConfig):
    target_: str = Field(default="mock_aligners.LanguageModelAligner", alias="_target_")
    model: Models = Field(default=Models.GPT_4O_MINI, description="OpenAI model to use for LLM-based alignment")
    source_language: LanguageCode = Field(default=LanguageCode.EN, description="Source language code")
    target_language: LanguageCode = Field(default=LanguageCode.DE, description="Target language code")
    min_confidence: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum confidence threshold")
    max_concurrent_requests: int = Field(default=8, gt=0, description="Max concurrent API requests")
    batch_size: int = Field(default=3, gt=0, description="Batch size for API requests")


class SmartNeighborhoodAlignerConfig(BaseAlignerConfig):
    target_: str = Field(default="mock_aligners.SmartNeighborhoodAligner", alias="_target_")

    anchor_aligner: dict[str, Any] = Field(..., description="Configuration for anchor aligner")
    anchor_segment_types: list[SegmentType] = Field(
        default_factory=list, description="Segment types to treat as anchors"
    )
    min_anchor_confidence: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Minimum confidence for reliable anchor alignments"
    )

    content_aligners: list[dict[str, Any]] = Field(
        ..., description="List of content aligner configurations to run sequentially"
    )

    max_neighborhood_size: int = Field(default=30, gt=0, description="Maximum size for a neighborhood before splitting")


# Discriminated union for aligner configs
AlignerConfigUnion = Union[
    ExactHashAlignerConfig,
    MultiLinguistEmbeddingConfig,
    BacktranslationEmbeddingConfig,
    LanguageModelAlignerConfig,
    SmartNeighborhoodAlignerConfig,
]

AlignerConfig = AlignerConfigUnion


class AlignmentConfig(BaseModel):
    aligners: list[AlignerConfig] = Field(
        default_factory=list, description="List of aligner configurations in execution order"
    )


# Other config models from the example
class LLMConfig(DynamicConfig[LLM]):
    target_: str = Field(default="mock_aligners.LLM", alias="_target_")
    model: str
    temperature: float
    max_tokens: int


class OptimizerConfig(DynamicConfig[Optimizer]):
    target_: str = Field(default="mock_aligners.Optimizer", alias="_target_")
    algo: str = Field(default="SGD")
    lr: float = Field(default=0.01)


class OpenAIConfig(BaseModel):
    """OpenAI config with _target_ but not a DynamicConfig - matches the example."""

    random_field: str = Field(default="random_field")
    api_key: str = Field(default="sk-1234567890", description="OpenAI API key")
    base_url: str = Field(default="https://api.openai.com/v1", description="OpenAI base URL")


CONFIG_DIR = Path(__file__).parent / "config"
ENV_DIR = Path(__file__).parent / "envs"


class Settings(BaseSettingsWithInstantiation):
    auto_instantiate: ClassVar[bool] = False  # Lazy mode - don't instantiate on init

    model_config = SettingsConfigDict(
        yaml_file=str(CONFIG_DIR / "02_simple.yaml"),
        env_file=str(ENV_DIR / ".env.02_simple"),
        env_prefix="DEV_",
        env_nested_delimiter="__",
    )

    debug: bool = Field(default=True, description="Debug mode")
    source_lang: LanguageCode = Field(default=LanguageCode.EN, description="Source language")
    target_lang: LanguageCode = Field(default=LanguageCode.DE, description="Target language")
    database: DatabaseConfig  # Uses BaseModel, not DynamicConfig
    optimizer: OptimizerConfig
    openai: OpenAIConfig  # Has _target_ but uses BaseModel
    llm: LLMConfig
    alignment_config: AlignmentConfig


# Multi-file settings example
class MultiEnvSettings(BaseSettingsWithInstantiation):
    auto_instantiate: ClassVar[bool] = False  # Enable lazy mode for config-as-data

    model_config = SettingsConfigDict(
        # Multi-layer configuration files
        yaml_file=[
            "config/base.yaml",  # Base configuration
            "config/{env}.yaml",  # Environment-specific overrides
        ],
        # Environment file
        env_file=".env.{env}",
        env_prefix="APP_",
        env_file_encoding="utf-8",
        # Environment variables
        env_nested_delimiter="__",  # APP_DATABASE__PASSWORD → database.password
        # Validation
        case_sensitive=False,
        extra="forbid",  # Fail on unknown fields
    )

    debug: bool = Field(default=True, description="Debug mode")
    source_lang: LanguageCode = Field(default=LanguageCode.EN, description="Source language")
    target_lang: LanguageCode = Field(default=LanguageCode.DE, description="Target language")
    database: DatabaseConfig
    optimizer: OptimizerConfig
    alignment_config: AlignmentConfig
