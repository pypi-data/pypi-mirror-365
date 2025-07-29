# PydantiConf Integration Demos

A progressive series of demos teaching PydantiConf from basics to advanced usage.

## 📚 New Progressive Demo Structure

Each demo focuses on **one key concept** and builds upon previous examples:

### Basic Concepts (01-05)
- **01_basic_instantiation.py** - Creating objects from configuration dicts
- **02_type_safe_configs.py** - Using DynamicConfig[T] for type safety
- **03_yaml_loading.py** - Loading configuration from YAML files
- **04_env_variables.py** - Environment variables and .env files
- **05_config_precedence.py** - Understanding configuration precedence

### Intermediate Features (06-10)
- **06_lazy_instantiation.py** - Lazy vs eager instantiation
- **07_runtime_overrides.py** - Runtime parameter overrides
- **08_nested_configs.py** - Nested configuration objects
- **09_dependency_injection.py** - Basic dependency injection
- **10_factory_pattern.py** - Factory pattern with _partial_

### Advanced Patterns (11-15)
- **11_config_factory.py** - Using ConfigFactory class
- **12_caching.py** - Understanding caching behavior
- **13_multi_environment.py** - Multi-environment setups
- **14_batch_operations.py** - Batch creation patterns
- **15_ml_example.py** - Real-world ML model example

## 🚀 Getting Started

1. Start with `01_basic_instantiation.py`:
   ```bash
   python integration/01_basic_instantiation.py
   ```

2. Work through each demo in order - they build on each other!

3. Each demo is self-contained with:
   - Clear explanations
   - Runnable examples
   - Key takeaways
   - Pointer to the next topic

## 📁 Directory Structure

```
integration/
├── 01_basic_instantiation.py     # Start here!
├── 02_type_safe_configs.py
├── ...
├── 15_ml_example.py
├── config/                        # YAML configuration files
│   ├── 01_basic.yaml
│   ├── 02_type_safe.yaml
│   └── ...
├── envs/                          # Environment files
│   ├── .env.04_env_variables
│   ├── .env.05_precedence
│   └── ...
└── mocks.py                       # Shared mock classes
```

---

## 📖 Original Comprehensive Examples

The following examples demonstrate advanced patterns from tmpppp.md:

### Key Patterns Demonstrated

1. **Configuration-as-Data Philosophy**: Load YAML + env files into typed Pydantic models without instantiation
2. **Lazy Instantiation**: Control when objects are created with `auto_instantiate=False`
3. **Type-Safe Configuration**: Using `DynamicConfig[T]` for instantiatable objects
4. **Discriminated Unions**: Complex configuration hierarchies with `Field(discriminator="_target_")`
5. **Multi-Environment Support**: YAML file merging with environment-specific overrides
6. **Factory Pattern**: Dependency injection with `register_dependency()`

### Original Example Files

- `config_models.py` - Configuration classes matching tmpppp.md patterns
- `mock_aligners.py` - Mock classes for demonstration
- `config.yaml` - Main configuration file with YAML anchors
- `.env` - Environment variables for sensitive data
- `config/` - Multi-environment configuration files
- `demo.py` - Complete demonstration of all features
- `complete_workflow.py` - Minimal example matching tmpppp.md

### Key Differences from Simple Examples

1. **BaseModel vs DynamicConfig**: 
   - Use `BaseModel` for non-instantiatable configs (e.g., `DatabaseConfig`)
   - Use `DynamicConfig[T]` for instantiatable objects

2. **Complex Type Hierarchies**: 
   - Base classes with custom field exclusions
   - Discriminated unions for polymorphic configurations

3. **Environment Variable Precedence**:
   - Constructor args > Environment variables > YAML > .env file > Secret files

### Running the Original Examples

```bash
# Run the complete workflow (minimal example)
python complete_workflow.py

# Run the full demonstration
python demo.py

# Test multi-environment configuration
env=dev python demo.py
env=prod python demo.py
```

## 💡 Tips

- Start with the numbered demos (01-15) for a structured learning path
- Use the original examples for advanced real-world patterns
- Each demo filename indicates its content
- Modify the examples to experiment!

Happy learning! 🚀