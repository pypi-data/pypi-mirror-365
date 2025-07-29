"""Mock aligner classes matching the tmpppp.md example."""

from enum import Enum
from typing import Any, Protocol

from pydantic import BaseModel


class LanguageCode(str, Enum):
    EN = "en"
    DE = "de"
    ES = "es"
    FR = "fr"


class MatchingStrategy(str, Enum):
    ONE_TO_ONE = "one_to_one"
    MANY_TO_ONE = "many_to_one"


class AlignmentResult(BaseModel):
    """Mock alignment result."""

    source: str
    target: str
    confidence: float


class AlignmentStrategy(Protocol):
    """Protocol matching the example."""

    def align(self, source: str, target: str) -> AlignmentResult: ...


class ExactHashAligner(BaseModel):
    """Mock exact hash aligner."""

    def align(self, source: str, target: str) -> AlignmentResult:
        confidence = 1.0 if source == target else 0.0
        return AlignmentResult(source=source, target=target, confidence=confidence)


class MultiLinguistEmbedding(BaseModel):
    """Mock embedding-based aligner."""

    threshold: float = 0.75
    top_k: int = 1
    require_type_match: bool = False
    matching_strategy: str = "many_to_one"

    def align(self, source: str, target: str) -> AlignmentResult:
        confidence = 0.8 if len(source) == len(target) else 0.6
        return AlignmentResult(source=source, target=target, confidence=confidence)


class BacktranslationEmbedding(BaseModel):
    """Mock backtranslation aligner."""

    threshold: float = 0.75
    top_k: int = 1
    max_concurrent_requests: int = 8
    source_language: str = "en"
    target_language: str = "de"
    model: str = "gpt-4o-mini"
    require_type_match: bool = False
    matching_strategy: str = "many_to_one"

    def align(self, source: str, target: str) -> AlignmentResult:
        confidence = 0.85
        return AlignmentResult(source=source, target=target, confidence=confidence)


class LanguageModelAligner(BaseModel):
    """Mock LLM-based aligner."""

    model: str = "gpt-4o-mini"
    source_language: str = "en"
    target_language: str = "de"
    min_confidence: float = 0.7
    max_concurrent_requests: int = 8
    batch_size: int = 3
    require_type_match: bool = False

    def align(self, source: str, target: str) -> AlignmentResult:
        # Mock LLM confidence
        confidence = 0.9
        return AlignmentResult(source=source, target=target, confidence=confidence)


class SmartNeighborhoodAligner(BaseModel):
    """Mock smart neighborhood aligner with nested aligners."""

    anchor_aligner: Any = None
    anchor_segment_types: list[str] = []
    min_anchor_confidence: float = 0.7
    content_aligners: list[Any] = []
    max_neighborhood_size: int = 30
    require_type_match: bool = False

    def align(self, source: str, target: str) -> AlignmentResult:
        return AlignmentResult(source=source, target=target, confidence=0.75)


# Additional mock classes from the example
class Optimizer(BaseModel):
    """Mock optimizer."""

    algo: str = "SGD"
    lr: float = 0.01


class LLM(BaseModel):
    """Mock LLM."""

    model: str
    temperature: float
    max_tokens: int


class Database(BaseModel):
    """Mock database following the tmpppp.md pattern."""

    host: str
    port: int
    db: str
    username: str
    password: str = ""


class OpenAI(BaseModel):
    """Mock OpenAI client."""

    api_key: str = "sk-1234567890"
    base_url: str = "https://api.openai.com/v1"
