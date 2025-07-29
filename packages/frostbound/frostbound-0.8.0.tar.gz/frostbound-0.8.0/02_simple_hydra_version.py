"""
Shows how integration/02_simple.py would look with hydra_instantiate.
SPOILER: It's much worse!
"""


# Current code (lines 153-175 from 02_simple.py)
def current_factory_pattern():
    """Your current elegant factory pattern with dependency injection"""
    from frostbound.pydanticonf import instantiate, register_dependency
    from integration.config_models import AlignerConfig, Settings
    from integration.mocks import AlignmentStrategy

    settings = Settings()

    class AlignerFactory:
        def __init__(self, *, source_language: str, target_language: str) -> None:
            # Register shared dependencies - SO CLEAN!
            register_dependency("source_language", source_language)
            register_dependency("target_language", target_language)

        def create_aligner(self, config: AlignerConfig) -> AlignmentStrategy:
            # Dependencies are injected automatically!
            return instantiate(config)

    factory = AlignerFactory(source_language="en", target_language="es")
    aligners = [factory.create_aligner(cfg) for cfg in settings.alignment_config.aligners if cfg.enabled]

    print(f"Current: Created {len(aligners)} aligners with automatic dependency injection")


# How it would look with hydra_instantiate - MUCH WORSE!
def hydra_factory_pattern():
    """Same pattern but with hydra - verbose and error-prone"""
    from omegaconf import OmegaConf

    from frostbound.pydanticonf.hydra_instantiate import instantiate as hydra_instantiate
    from integration.config_models import AlignerConfig, Settings
    from integration.mocks import AlignmentStrategy

    settings = Settings()

    class AlignerFactory:
        def __init__(self, *, source_language: str, target_language: str) -> None:
            # No dependency injection - must store manually
            self.source_language = source_language
            self.target_language = target_language

        def create_aligner(self, config: AlignerConfig) -> AlignmentStrategy:
            # Convert Pydantic to dict (loses validation!)
            config_dict = config.model_dump(mode="python")

            # Manually inject dependencies for EVERY aligner type
            if "BasicWordAligner" in config_dict.get("_target_", ""):
                config_dict["source_language"] = self.source_language
                config_dict["target_language"] = self.target_language
            elif "PhoneticAligner" in config_dict.get("_target_", ""):
                config_dict["source_lang"] = self.source_language  # Different param name!
                config_dict["target_lang"] = self.target_language
            elif "SmartNeighborhoodAligner" in config_dict.get("_target_", ""):
                # Nested configs need manual handling too!
                if "anchor_aligner" in config_dict:
                    config_dict["anchor_aligner"]["source_language"] = self.source_language
                    config_dict["anchor_aligner"]["target_language"] = self.target_language
                if "content_aligners" in config_dict:
                    for aligner in config_dict["content_aligners"]:
                        aligner["source_language"] = self.source_language
                        aligner["target_language"] = self.target_language
            # ... repeat for EVERY aligner type! 😱

            # Convert to OmegaConf
            omega_config = OmegaConf.create(config_dict)

            # Finally instantiate
            return hydra_instantiate(omega_config)

    factory = AlignerFactory(source_language="en", target_language="es")
    # This is now fragile and verbose!


# Problems summary
def why_hydra_is_wrong_choice():
    """
    Why hydra_instantiate is wrong for your codebase:

    1. NO DEPENDENCY INJECTION
       - Must manually pass dependencies everywhere
       - Different classes might use different param names
       - Nested objects need manual recursive handling

    2. LOSES TYPE SAFETY
       - instantiate(config: DynamicConfig[T]) -> T  ✅ (current)
       - instantiate(config: Any) -> Any  ❌ (hydra)

    3. BREAKS PYDANTIC INTEGRATION
       - Must convert to dict, losing validation
       - Extra conversion overhead
       - Can't use model_validator or field validators

    4. REQUIRES OMEGACONF
       - Heavy dependency you don't need
       - Different configuration philosophy
       - Learning curve for team

    5. MORE FRAGILE CODE
       - Manual dependency wiring is error-prone
       - Must update factory for each new aligner type
       - Harder to maintain and test
    """

    print("""
    Your current implementation is MUCH better because:
    - Automatic dependency injection
    - Type-safe with generics
    - Clean Pydantic integration
    - No unnecessary dependencies
    - Cleaner, more maintainable code
    """)


if __name__ == "__main__":
    print("=== Comparing Factory Patterns ===\n")

    print("Your current approach:")
    current_factory_pattern()

    print("\nWith hydra_instantiate:")
    print("❌ Would require manual dependency injection")
    print("❌ Would lose type safety")
    print("❌ Would need OmegaConf dependency")
    print("❌ Would make code more complex and fragile")

    print("\n=== RECOMMENDATION ===")
    why_hydra_is_wrong_choice()
