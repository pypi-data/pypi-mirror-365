from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Annotated, Any, Generic, Literal, TypeVar, overload

from instructor import AsyncInstructor, Instructor
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, Field, computed_field, model_validator

from frostbound.pydanticonf import DynamicConfig, instantiate
from frostbound.wrappers.instructor import CompletionTrace, ahook_instructor, hook_instructor

MODEL_UNSUPPORTED_PARAMETERS = {
    # OpenAI reasoning models
    "o3-mini": {"temperature": None, "top_p": None},
    "o3": {"temperature": None, "top_p": None},
    "o4-mini": {"temperature": None, "top_p": None},
    # Claude with extended thinking
    "claude-4-sonnet-thinking": {"temperature": None, "top_p": None, "top_k": None},
}


class ModelFilterMixin(BaseModel):
    @model_validator(mode="before")
    def filter_unsupported_parameters(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Filter out unsupported parameters for the model."""
        model = values.get("model")
        if model and model in MODEL_UNSUPPORTED_PARAMETERS:
            for param in MODEL_UNSUPPORTED_PARAMETERS[model]:
                values.pop(param, None)
        return values


class BaseModelConfig(ModelFilterMixin):
    """Base configuration for all model providers."""

    model: str

    def to_params(self) -> dict[str, Any]:
        """Convert config to parameters dict, excluding provider field."""
        return self.model_dump(exclude={"provider"}, exclude_none=True)


class OpenAIConfig(BaseModelConfig):
    """Configuration specific to OpenAI models."""

    provider: Literal["openai"] = "openai"
    temperature: float | None = None
    top_p: float | None = None
    # max_completion_tokens: int | None = None
    # frequency_penalty: float | None = Field(default=None, ge=-2.0, le=2.0)
    # presence_penalty: float | None = Field(default=None, ge=-2.0, le=2.0)


class AnthropicConfig(BaseModelConfig):
    """Configuration specific to Anthropic models."""

    provider: Literal["anthropic"] = "anthropic"
    # Anthropic thinking models don't support temperature
    max_tokens: int | None = None
    top_k: int | None = None
    top_p: float | None = Field(default=None, ge=0.0, le=1.0)
    metadata: dict[str, Any] | None = None


ModelConfig = Annotated[OpenAIConfig | AnthropicConfig, Field(discriminator="provider")]


# ============================================================================
# New Config System using pydanticonf
# ============================================================================


class InstructorClientConfig(BaseModel):
    """Configuration for instructor client creation."""

    mode: str | None = Field(default=None)
    """Instructor mode (e.g., 'TOOLS', 'JSON', 'JSON_SCHEMA', 'TOOLS_STRICT')."""

    timeout: float | None = Field(default=None, gt=0)
    """Default timeout for all requests in seconds."""

    max_retries: int = Field(default=3, ge=0, le=10)
    """Default max retries for failed requests."""

    strict: bool = Field(default=False)
    """Default strict mode for structured output."""


class CompletionConfig(BaseModel):
    """Runtime configuration for completion requests."""

    max_retries: int | None = Field(default=None, ge=0, le=10)
    """Override max retries for this specific request."""

    timeout: float | None = Field(default=None, gt=0)
    """Override timeout for this specific request."""

    strict: bool | None = Field(default=None)
    """Override strict mode for this specific request."""

    def to_params(self) -> dict[str, Any]:
        """Convert to parameters dict, excluding None values."""
        return self.model_dump(exclude_none=True)


class ProviderConfig(DynamicConfig[BaseModel]):
    """Dynamic provider configuration that can instantiate any provider config.

    Example:
        # OpenAI config
        provider_config = ProviderConfig(
            _target_="canonical.OpenAIConfig",
            model="gpt-4o-mini",
            temperature=0.0
        )

        # Anthropic config
        provider_config = ProviderConfig(
            _target_="canonical.AnthropicConfig",
            model="claude-sonnet-4-20250514",
            max_tokens=4096
        )
    """

    def get_provider_params(self) -> dict[str, Any]:
        """Instantiate and get provider parameters."""
        provider_instance = instantiate(self)
        if hasattr(provider_instance, "to_params"):
            return provider_instance.to_params()
        return provider_instance.model_dump(exclude_none=True)


class VerifierConfig(BaseModel):
    """Unified configuration for verifiers with clear separation of concerns."""

    provider: ProviderConfig
    """Provider-specific configuration (model, temperature, etc.)."""

    instructor_client: InstructorClientConfig = Field(default_factory=InstructorClientConfig)
    """Configuration for instructor client creation."""

    completion: CompletionConfig = Field(default_factory=CompletionConfig)
    """Runtime configuration for completion requests."""

    def get_client_params(self) -> dict[str, Any]:
        """Get parameters for instructor client creation."""
        return self.instructor_client.model_dump(exclude_none=True)

    def get_completion_params(self) -> dict[str, Any]:
        """Get combined parameters for completion requests."""
        provider_params = self.provider.get_provider_params()
        completion_params = self.completion.to_params()

        # Completion params override provider params
        return {**provider_params, **completion_params}


class InstructorConfig(BaseModel):
    """Configuration for instructor-specific parameters."""

    max_retries: int = Field(default=3, ge=0, le=10)
    """Maximum number of retries for failed requests."""

    mode: str | None = Field(default=None)
    """Instructor mode (e.g., 'JSON', 'JSON_SCHEMA', 'TOOLS')."""

    timeout: float | None = Field(default=None, gt=0)
    """Request timeout in seconds."""

    strict: bool = Field(default=False)
    """Whether to use strict mode for structured output."""

    def to_params(self) -> dict[str, Any]:
        """Convert config to parameters dict."""
        return self.model_dump(exclude_none=True)


class VerificationCandidate(BaseModel):
    """Base class for all verification candidates with minimal required fields."""

    is_aligned: bool
    """A boolean indicating whether the candidate is aligned with the source text."""

    chain_of_thought: list[str]
    """A list of strings representing the chain of thought from the verifier."""

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
    )
    """A float between 0.0 and 1.0 indicating the confidence level in the alignment assessment."""

    @computed_field
    @property
    def reasoning(self) -> str:
        """A string representing the chain of thought from the verifier."""
        return "\n".join(self.chain_of_thought) if self.chain_of_thought else ""


VerificationCandidateT = TypeVar("VerificationCandidateT", bound=VerificationCandidate)


class VerificationMethod(str, Enum):
    CANONICAL = "canonical"
    SELF_VERIFY = "self_verify"
    CHAIN = "chain"
    BACKWARD = "backward"
    ENSEMBLE = "ensemble"


class CanonicalVerifierConfig(BaseModel):
    """Configuration specific to CanonicalVerifier

    This class maintains backward compatibility while internally using the new config system.
    """

    llm_config: ModelConfig
    instructor_config: InstructorConfig = Field(default_factory=InstructorConfig)

    def merge_params(self) -> dict[str, Any]:
        """Get combined parameters from both llm and instructor configs."""
        return {**self.llm_config.to_params(), **self.instructor_config.to_params()}

    def to_verifier_config(self) -> VerifierConfig:
        """Convert to new VerifierConfig format."""
        # Determine provider target based on discriminator
        if self.llm_config.provider == "openai":
            provider_target = "canonical.OpenAIConfig"
        else:
            provider_target = "canonical.AnthropicConfig"

        # Create ProviderConfig with the appropriate target
        provider_config = ProviderConfig(
            _target_=provider_target, **self.llm_config.model_dump(exclude={"provider"}, exclude_none=True)
        )

        # Map instructor config to new format
        instructor_client_config = InstructorClientConfig(
            mode=self.instructor_config.mode,
            timeout=self.instructor_config.timeout,
            max_retries=self.instructor_config.max_retries,
            strict=self.instructor_config.strict,
        )

        # Create completion config from instructor config
        completion_config = CompletionConfig(
            max_retries=self.instructor_config.max_retries,
            timeout=self.instructor_config.timeout,
            strict=self.instructor_config.strict,
        )

        return VerifierConfig(
            provider=provider_config, instructor_client=instructor_client_config, completion=completion_config
        )


VerifierConfigT = TypeVar("VerifierConfigT", bound=BaseModel)


# ============================================================================
# Instructor Client Factory
# ============================================================================


class InstructorClientFactory:
    """Factory for creating instructor clients with provider-specific configuration."""

    @staticmethod
    def create_sync_client(verifier_config: VerifierConfig, **override_client_params: Any) -> Instructor:
        """Create a synchronous instructor client based on configuration.

        Args:
            verifier_config: The verifier configuration containing provider and client settings
            **override_client_params: Override parameters for client creation

        Returns:
            Configured Instructor client
        """
        # Get provider instance
        provider_instance = instantiate(verifier_config.provider)

        # Merge client params with overrides
        client_params = {**verifier_config.get_client_params(), **override_client_params}

        # Create appropriate client based on provider type
        if hasattr(provider_instance, "provider") and provider_instance.provider == "openai":
            import os

            import openai

            base_client = openai.OpenAI(api_key=os.getenv("OPENAI_CREDENTIALS__API_KEY"))
            return instructor.from_openai(base_client, **client_params)
        elif hasattr(provider_instance, "provider") and provider_instance.provider == "anthropic":
            import os

            import anthropic

            base_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_CREDENTIALS__API_KEY"))
            return instructor.from_anthropic(base_client, **client_params)
        else:
            raise ValueError(f"Unsupported provider: {provider_instance}")

    @staticmethod
    async def create_async_client(verifier_config: VerifierConfig, **override_client_params: Any) -> AsyncInstructor:
        """Create an asynchronous instructor client based on configuration.

        Args:
            verifier_config: The verifier configuration containing provider and client settings
            **override_client_params: Override parameters for client creation

        Returns:
            Configured AsyncInstructor client
        """
        # Get provider instance
        provider_instance = instantiate(verifier_config.provider)

        # Merge client params with overrides
        client_params = {**verifier_config.get_client_params(), **override_client_params}

        # Create appropriate client based on provider type
        if hasattr(provider_instance, "provider") and provider_instance.provider == "openai":
            import os

            import openai

            base_client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_CREDENTIALS__API_KEY"))
            return instructor.from_openai(base_client, **client_params)
        elif hasattr(provider_instance, "provider") and provider_instance.provider == "anthropic":
            import os

            import anthropic

            base_client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_CREDENTIALS__API_KEY"))
            return instructor.from_anthropic(base_client, **client_params)
        else:
            raise ValueError(f"Unsupported provider: {provider_instance}")


class CanonicalVerificationCandidate(VerificationCandidate):
    chain_of_thought: list[str] = Field(
        ...,
        description=(
            """
            Step-by-step reasoning in pointers described below to verify alignment of veterinary pharmaceutical QRD
            documents (e.g., SmPCs, Package Leaflets, Annexes) between source and target texts in EU
            and LATAM jurisdictions. Review each candidate translation against the following
            criteria, illustrating with concrete examples.

            1. **Completeness**: Has any critical information been added or lost?

                - Example 1:
                    - Source: "Canine oral suspension, **100 mg/mL**"
                    - Target: "Suspension zum Einnehmen für Hunde,"
                    - Result: **incomplete** (the strength **100 mg/mL** is missing from the
                    target).
                - Example 2:
                    - Source: "Canine oral suspension,"
                    - Target: "Suspension zum Einnehmen für Hunde, **100 mg/ml**,"
                    - Result: **incomplete** (the strength **100 mg/ml** is missing from the
                    source).

            2. **Semantic equivalence**: Is the scientific meaning preserved for the
            intended species and context?

                - Example:
                    - Source: "For **prevention** of bovine mastitis"
                    - Target: "Para **prevenir** mastitis en vacas"
                    - Result: correctly conveys indication and species.

            3. **Regulatory terminology & template compliance**: Does the target follow
            region-specific QRD headings and required phrases (EMA, ANVISA, ANMAT,
            INVIMA…)? Current QRD version is 9.1.

                - Example:
                    - Heading in English QRD: "**4.8 Undesirable effects**"
                    - Spanish QRD must appear as "**4.8 Reacciones adversas**" (exact
                    template term).

            4. **Domain-specific terminology**: Are pharmacological terms, units, and
            routes rendered accurately?

                - Example:
                    - Source: "**Intramammary infusion**"
                    - Target: "**Infusión intramamaria**" (route preserved).
                - Example:
                    - Source: "Dose: 2 mg/kg bw"
                    - Target: "Dosis: 2 mg/kg pv" (kg peso vivo) - unit abbreviations
                    adjusted to Spanish convention.

            5. **Cultural & linguistic conventions**: Dates, decimals, register, and
            legal tone adapted to locale.

                - Example:
                    - Spanish-LATAM numeric date: Source "2025-06-10"
                    - Target: "**10/06/2025**".
                - Example:
                    - French date with month name: Source "2025-06-10"
                    - Target: "**10 juin 2025**" (placeholder in QRD: **"JJ/MM/AAAA"**).
                - Example:
                    - Portuguese-BR decimals: Source "0.25 mg/mL"
                    - Target: "0,25 mg/mL" (comma decimal separator).

            6. **Equivalence vs. paraphrase**: Does the paraphrased text retain all
            regulatory intent and legal scope?

                - Example:
                    - Source: "**Withdrawal period: 7 days**"
                    - Target: "**Período de carencia: 7 días**" - acceptable paraphrase.

            7. **Common pitfalls & false cognates**: Some false positives are not
            acceptable.

                - Example:
                    - Source: "**Withdrawal period**"
                    - Target (de): "**Wartezeiten**"
                    - Result: This should be a match but often LLM thinks Wartezeiten is
                    Waiting times in english.
            """
        ),
    )

    is_aligned: bool = Field(
        ...,
        description="Whether the candidate is aligned with the source text based on the chain of thought.",
    )
    confidence: float = Field(
        ...,
        description="Confidence level in the alignment assessment (0.0-1.0).",
    )
    violations: (
        list[
            Literal[
                "incomplete",
                "semantic_equivalence",
                "regulatory_terminology",
                "domain_specific_terminology",
                "cultural_linguistic_conventions",
                "equivalence_vs_paraphrase",
            ]
        ]
        | None
    ) = Field(
        description="REQUIRED when `is_aligned` is `False`. Must contain at least one violation type explaining why the alignment failed. Leave as None only when `is_aligned` is `True`.",
        default=None,
    )


class VerificationResult(BaseModel, Generic[VerificationCandidateT]):
    candidate: VerificationCandidateT
    calibrated: bool = Field(
        ...,
        description="Whether the candidate is calibrated/ensembled with other verifiers.",
    )
    calibrated_confidence: float | None = Field(
        default=None,
        description="Overall calibrated/ensembled confidence score for this verification result (0.0-1.0). Represents the verifier's certainty in the alignment decision.",
    )
    verification_method: VerificationMethod


class BaseVerifier(BaseModel, ABC, Generic[VerifierConfigT]):
    """Base class for all verifiers with common overload patterns."""

    config: VerifierConfigT

    @property
    @abstractmethod
    def supports_calibration(self) -> bool:
        """Whether this verifier supports calibration/ensembling."""

    @abstractmethod
    def _assemble(
        self, candidate: VerificationCandidateT, captured: CompletionTrace | None = None, with_hook: bool = False
    ) -> (
        VerificationResult[VerificationCandidateT] | tuple[VerificationResult[VerificationCandidateT], CompletionTrace]
    ):
        """Finalize the response by creating a VerificationResult and optionally attaching hook capture data."""

    @overload
    @abstractmethod
    async def averify(
        self,
        client: AsyncInstructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: Literal[False] = False,
        **kwargs: Any,
    ) -> VerificationResult[VerificationCandidateT]: ...

    @overload
    @abstractmethod
    async def averify(
        self,
        client: AsyncInstructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: Literal[True],
        **kwargs: Any,
    ) -> tuple[VerificationResult[VerificationCandidateT], CompletionTrace]: ...

    @overload
    @abstractmethod
    async def averify(
        self,
        client: AsyncInstructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: bool,
        **kwargs: Any,
    ) -> (
        VerificationResult[VerificationCandidateT] | tuple[VerificationResult[VerificationCandidateT], CompletionTrace]
    ): ...

    @abstractmethod
    async def averify(
        self,
        client: AsyncInstructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: bool = False,
        **kwargs: Any,
    ) -> (
        VerificationResult[VerificationCandidateT] | tuple[VerificationResult[VerificationCandidateT], CompletionTrace]
    ): ...

    @overload
    @abstractmethod
    def verify(
        self,
        client: Instructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: Literal[False] = False,
        **kwargs: Any,
    ) -> VerificationResult[VerificationCandidateT]: ...

    @overload
    @abstractmethod
    def verify(
        self,
        client: Instructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: Literal[True],
        **kwargs: Any,
    ) -> tuple[VerificationResult[VerificationCandidateT], CompletionTrace]: ...

    @overload
    @abstractmethod
    def verify(
        self,
        client: Instructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: bool,
        **kwargs: Any,
    ) -> (
        VerificationResult[VerificationCandidateT] | tuple[VerificationResult[VerificationCandidateT], CompletionTrace]
    ): ...

    @abstractmethod
    def verify(
        self,
        client: Instructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: bool = False,
        **kwargs: Any,
    ) -> (
        VerificationResult[VerificationCandidateT] | tuple[VerificationResult[VerificationCandidateT], CompletionTrace]
    ): ...


class CanonicalVerifier(BaseVerifier[CanonicalVerifierConfig]):
    config: CanonicalVerifierConfig
    _verifier_config: VerifierConfig | None = None

    @property
    def supports_calibration(self) -> Literal[False]:
        """CanonicalVerifier does not support calibration - it's a single-shot verifier."""
        return False

    @property
    def verifier_config(self) -> VerifierConfig:
        """Get the verifier config, converting from old format if needed."""
        if self._verifier_config is None:
            self._verifier_config = self.config.to_verifier_config()
        return self._verifier_config

    def _assemble(
        self, candidate: VerificationCandidateT, captured: CompletionTrace | None = None, with_hook: bool = False
    ) -> (
        VerificationResult[VerificationCandidateT] | tuple[VerificationResult[VerificationCandidateT], CompletionTrace]
    ):
        """Finalize the response by creating a VerificationResult and optionally attaching hook capture data."""
        result = VerificationResult[VerificationCandidateT](
            candidate=candidate,
            verification_method=VerificationMethod.CANONICAL,
            calibrated=self.supports_calibration,
            calibrated_confidence=None if not self.supports_calibration else candidate.confidence,
        )

        if with_hook and captured is not None:
            captured.parsed_result = candidate
            return result, captured
        return result

    @overload
    async def averify(
        self,
        client: AsyncInstructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: Literal[False] = False,
        **kwargs: Any,
    ) -> VerificationResult[VerificationCandidateT]: ...

    @overload
    async def averify(
        self,
        client: AsyncInstructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: Literal[True],
        **kwargs: Any,
    ) -> tuple[VerificationResult[VerificationCandidateT], CompletionTrace]: ...

    @overload
    async def averify(
        self,
        client: AsyncInstructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: bool,
        **kwargs: Any,
    ) -> (
        VerificationResult[VerificationCandidateT] | tuple[VerificationResult[VerificationCandidateT], CompletionTrace]
    ): ...

    async def averify(
        self,
        client: AsyncInstructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: bool = False,
        **kwargs: Any,
    ) -> (
        VerificationResult[VerificationCandidateT] | tuple[VerificationResult[VerificationCandidateT], CompletionTrace]
    ):
        merged = {**self.config.merge_params(), **kwargs}

        async with ahook_instructor(client, enable=with_hook) as captured:
            candidate = await client.chat.completions.create(
                messages=messages,
                response_model=response_model,
                **merged,
            )
            return self._assemble(candidate, captured, with_hook=with_hook)

    @overload
    def verify(
        self,
        client: Instructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: Literal[False] = False,
        **kwargs: Any,
    ) -> VerificationResult[VerificationCandidateT]: ...

    @overload
    def verify(
        self,
        client: Instructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: Literal[True],
        **kwargs: Any,
    ) -> tuple[VerificationResult[VerificationCandidateT], CompletionTrace]: ...

    @overload
    def verify(
        self,
        client: Instructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: bool,
        **kwargs: Any,
    ) -> (
        VerificationResult[VerificationCandidateT] | tuple[VerificationResult[VerificationCandidateT], CompletionTrace]
    ): ...

    def verify(
        self,
        client: Instructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: bool = False,
        **kwargs: Any,
    ) -> (
        VerificationResult[VerificationCandidateT] | tuple[VerificationResult[VerificationCandidateT], CompletionTrace]
    ):
        merged = {**self.config.merge_params(), **kwargs}

        with hook_instructor(client, enable=with_hook) as captured:
            candidate = client.chat.completions.create(
                messages=messages,
                response_model=response_model,
                **merged,
            )
            return self._assemble(candidate, captured, with_hook=with_hook)


class ModernCanonicalVerifier(BaseVerifier[VerifierConfig]):
    """Modern CanonicalVerifier that uses the new config system directly."""

    config: VerifierConfig

    @property
    def supports_calibration(self) -> Literal[False]:
        """CanonicalVerifier does not support calibration - it's a single-shot verifier."""
        return False

    def _assemble(
        self, candidate: VerificationCandidateT, captured: CompletionTrace | None = None, with_hook: bool = False
    ) -> (
        VerificationResult[VerificationCandidateT] | tuple[VerificationResult[VerificationCandidateT], CompletionTrace]
    ):
        """Finalize the response by creating a VerificationResult and optionally attaching hook capture data."""
        result = VerificationResult[VerificationCandidateT](
            candidate=candidate,
            verification_method=VerificationMethod.CANONICAL,
            calibrated=self.supports_calibration,
            calibrated_confidence=None if not self.supports_calibration else candidate.confidence,
        )

        if with_hook and captured is not None:
            captured.parsed_result = candidate
            return result, captured
        return result

    @overload
    async def averify(
        self,
        client: AsyncInstructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: Literal[False] = False,
        **kwargs: Any,
    ) -> VerificationResult[VerificationCandidateT]: ...

    @overload
    async def averify(
        self,
        client: AsyncInstructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: Literal[True],
        **kwargs: Any,
    ) -> tuple[VerificationResult[VerificationCandidateT], CompletionTrace]: ...

    @overload
    async def averify(
        self,
        client: AsyncInstructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: bool,
        **kwargs: Any,
    ) -> (
        VerificationResult[VerificationCandidateT] | tuple[VerificationResult[VerificationCandidateT], CompletionTrace]
    ): ...

    async def averify(
        self,
        client: AsyncInstructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: bool = False,
        **kwargs: Any,
    ) -> (
        VerificationResult[VerificationCandidateT] | tuple[VerificationResult[VerificationCandidateT], CompletionTrace]
    ):
        # Get completion parameters
        completion_params = self.config.get_completion_params()
        merged = {**completion_params, **kwargs}

        async with ahook_instructor(client, enable=with_hook) as captured:
            candidate = await client.chat.completions.create(
                messages=messages,
                response_model=response_model,
                **merged,
            )
            return self._assemble(candidate, captured, with_hook=with_hook)

    @overload
    def verify(
        self,
        client: Instructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: Literal[False] = False,
        **kwargs: Any,
    ) -> VerificationResult[VerificationCandidateT]: ...

    @overload
    def verify(
        self,
        client: Instructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: Literal[True],
        **kwargs: Any,
    ) -> tuple[VerificationResult[VerificationCandidateT], CompletionTrace]: ...

    @overload
    def verify(
        self,
        client: Instructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: bool,
        **kwargs: Any,
    ) -> (
        VerificationResult[VerificationCandidateT] | tuple[VerificationResult[VerificationCandidateT], CompletionTrace]
    ): ...

    def verify(
        self,
        client: Instructor,
        messages: list[ChatCompletionMessageParam],
        response_model: type[VerificationCandidateT],
        *,
        with_hook: bool = False,
        **kwargs: Any,
    ) -> (
        VerificationResult[VerificationCandidateT] | tuple[VerificationResult[VerificationCandidateT], CompletionTrace]
    ):
        # Get completion parameters
        completion_params = self.config.get_completion_params()
        merged = {**completion_params, **kwargs}

        with hook_instructor(client, enable=with_hook) as captured:
            candidate = client.chat.completions.create(
                messages=messages,
                response_model=response_model,
                **merged,
            )
            return self._assemble(candidate, captured, with_hook=with_hook)


"""Example usage of CanonicalVerifier with sync and async versions."""

if __name__ == "__main__":
    import os

    # import anthropic
    import instructor
    import openai
    from dotenv import load_dotenv
    from openai.types.chat import ChatCompletionMessageParam
    from rich.pretty import pprint

    from canonical import (
        CanonicalVerificationCandidate,
        CanonicalVerifier,
        CanonicalVerifierConfig,
        CompletionConfig,
        InstructorClientConfig,
        InstructorClientFactory,
        InstructorConfig,
        ModernCanonicalVerifier,
        OpenAIConfig,
        ProviderConfig,
        VerifierConfig,
    )

    load_dotenv()

    # Example 1: Legacy approach (backward compatible)
    legacy_verifier = CanonicalVerifier(
        config=CanonicalVerifierConfig(
            llm_config=OpenAIConfig(model="gpt-4o-mini", temperature=0.0),
            instructor_config=InstructorConfig(max_retries=3),
        )
    )

    # Example 2: Modern approach with new config system
    modern_verifier = ModernCanonicalVerifier(
        config=VerifierConfig(
            provider=ProviderConfig(_target_="canonical.OpenAIConfig", model="gpt-4o-mini", temperature=0.0),
            instructor_client=InstructorClientConfig(mode="TOOLS_STRICT", max_retries=3, timeout=60.0),
            completion=CompletionConfig(strict=True),
        )
    )

    # Example 3: Easy provider swapping with dynamic config
    def create_verifier_from_yaml_config(provider_config: dict) -> ModernCanonicalVerifier:
        """Create verifier from YAML-like config structure."""
        # This could come from a YAML file:
        # provider:
        #   _target_: canonical.AnthropicConfig
        #   model: claude-sonnet-4-20250514
        #   max_tokens: 4096
        return ModernCanonicalVerifier(
            config=VerifierConfig(
                provider=ProviderConfig(**provider_config),
                instructor_client=InstructorClientConfig(max_retries=3),
                completion=CompletionConfig(),
            )
        )

    # Example 4: Using factory pattern for client creation
    verifier_config = VerifierConfig(
        provider=ProviderConfig(_target_="canonical.OpenAIConfig", model="gpt-4o-mini", temperature=0.0),
        instructor_client=InstructorClientConfig(mode="TOOLS_STRICT"),
        completion=CompletionConfig(),
    )

    # Create client using factory
    sync_client = InstructorClientFactory.create_sync_client(verifier_config)

    print("Legacy config:")
    pprint(legacy_verifier.config.llm_config)
    print("\nModern config:")
    pprint(modern_verifier.config)

    SYSTEM_PROMPT = """You are an expert translation alignment verifier specializing in {{ domain }} documents.
    Analyze whether these segments are correctly aligned translations between {{ source_lang }} and {{ target_lang }}.

    CRITICAL: For veterinary/medical contexts, "Withdrawal periods" correctly translates to "Wartezeiten".
    Focus on medical semantics, not literal word-for-word translation."""

    USER_PROMPT = """Source ({{ source_lang }}): {{ source_text }} -> Target ({{ target_lang }}): {{ target_text }}"""

    # Synchronous example
    def sync_example():
        # Example 1: Using legacy verifier with manual client creation
        client = instructor.from_openai(
            openai.OpenAI(api_key=os.getenv("OPENAI_CREDENTIALS__API_KEY")), mode=instructor.Mode.TOOLS_STRICT
        )

        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT},
        ]

        # Legacy approach
        result, trace = legacy_verifier.verify(
            client=client,
            messages=messages,
            response_model=CanonicalVerificationCandidate,
            with_hook=True,
            context={
                "domain": "veterinary pharmaceutical QRD documents",
                "source_lang": "en",
                "target_lang": "de",
                "source_text": "Excipients:",
                "target_text": "Sonstige Bestandteile:",
            },
        )
        print("\nLegacy verifier result:")
        pprint(result)

        # Example 2: Using modern verifier with factory-created client
        modern_client = InstructorClientFactory.create_sync_client(
            modern_verifier.config,
            # Can override client params here if needed
        )

        result2, trace2 = modern_verifier.verify(
            client=modern_client,
            messages=messages,
            response_model=CanonicalVerificationCandidate,
            with_hook=True,
            context={
                "domain": "veterinary pharmaceutical QRD documents",
                "source_lang": "en",
                "target_lang": "de",
                "source_text": "3.6 Adverse events",
                "target_text": "3.6 Nebenwirkungen",
            },
            # Can override completion params here
            temperature=0.1,  # This overrides the config temperature
        )
        print("\nModern verifier result:")
        pprint(result2)

    # Async example with provider swapping
    async def async_example_with_provider_swap():
        # Create verifier with Anthropic provider
        anthropic_verifier = ModernCanonicalVerifier(
            config=VerifierConfig(
                provider=ProviderConfig(
                    _target_="canonical.AnthropicConfig", model="claude-sonnet-4-20250514", max_tokens=4096
                ),
                instructor_client=InstructorClientConfig(max_retries=2, timeout=30.0),
                completion=CompletionConfig(),
            )
        )

        # Create async client
        async_client = await InstructorClientFactory.create_async_client(anthropic_verifier.config)

        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT},
        ]

        result = await anthropic_verifier.averify(
            client=async_client,
            messages=messages,
            response_model=CanonicalVerificationCandidate,
            context={
                "domain": "veterinary pharmaceutical QRD documents",
                "source_lang": "en",
                "target_lang": "fr",
                "source_text": "Withdrawal period:",
                "target_text": "Temps d'attente:",
            },
        )
        print("\nAnthropic verifier result:")
        pprint(result)

    sync_example()
