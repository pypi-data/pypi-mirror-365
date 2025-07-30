# Alloy DSL

Agent-first programming for Python. A clean, Pythonic API for AI agents with first-class support for:

- **Agents as first-class citizens** with multi-provider support
- **Structured output** with automatic parsing and validation  
- **Tool calling** and autonomous agentic behavior
- **Pipeline operations** with clean error handling
- **Design-by-contract** patterns
- **Natural language commands** as reusable templates

## Quick Start

### 1. Installation

```bash
# Clone and set up development environment
git clone <repo-url>
cd alloy-ai
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### 2. Set up API Keys

Create a `.env` file:

```bash
# .env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
```

### 3. Basic Usage

```python
from alloy import Agent
from dataclasses import dataclass

# Agentic by default - autonomous reasoning and tool use
agent = Agent("gpt-4o", tools=[calculate_area, get_weather])
response = await agent("What's the area of a 5x3 room?")
print(response.value)  # Agent autonomously uses calculate_area tool

# Simple chat mode (bypasses agentic reasoning)  
response = await agent.async_chat("What's the capital of France?")
print(response.value)  # Direct LLM response: "Paris"

# Synchronous usage
response = agent.sync("What's the area of a 5x3 room?")
print(response.value)  # Blocks until completion

# Structured output works in both modes
@dataclass
class WeatherInfo:
    location: str
    temperature: int
    condition: str

weather_agent = Agent("gpt-4o", output_schema=WeatherInfo)
result = await weather_agent("Get weather for Paris: 22°C, sunny")  # Agentic mode
weather = result.value  # Automatically parsed WeatherInfo object
print(f"{weather.location}: {weather.temperature}°C, {weather.condition}")
```

### 4. Multi-Provider Support

```python
# Automatic provider detection
openai_agent = Agent("gpt-4o")                    # Uses OpenAI
claude_agent = Agent("claude-3.5-sonnet")         # Uses Anthropic  
router_agent = Agent("anthropic/claude-3.5-sonnet")  # Uses OpenRouter

# All agents have the same interface
for agent in [openai_agent, claude_agent, router_agent]:
    result = await agent("Hello!")
    print(result.value)
```

### 5. Autonomous Agent Behavior

```python
# Define tools as regular Python functions
def calculate_area(length: float, width: float) -> float:
    """Calculate the area of a rectangle."""
    return length * width

def get_current_weather(location: str) -> str:
    """Get the current weather for a location."""
    return f"The weather in {location} is sunny and 22°C"

# Agent automatically becomes agentic when given tools
agent = Agent("gpt-4o", tools=[calculate_area, get_current_weather])

# Agent autonomously reasons and uses tools as needed
result = await agent("What's the area of a 5x3 meter room and the weather in Paris?")
print(result.value)  
# Agent will:
# 1. Use calculate_area(5, 3) → 15
# 2. Use get_current_weather("Paris") → "sunny and 22°C"  
# 3. Synthesize: "The area is 15 square meters and the weather in Paris is sunny and 22°C"
```

## Provider Support

| Provider | Models | Function Calling | Structured Output | Status |
|----------|--------|-----------------|-------------------|---------|
| **OpenAI** | GPT-4o, GPT-4.1, GPT-3.5+ | ✅ | ✅ JSON Schema | ✅ Ready |
| **Anthropic** | Claude 3+, Claude 4 | ✅ | ✅ Tool-based | ✅ Ready |
| **OpenRouter** | 50+ models | ✅ Variable* | ✅ Variable* | ✅ Ready |
| **xAI** | Grok models | ✅ | ✅ | 🚧 Stub |
| **Gemini** | Gemini Pro+ | ✅ | ✅ | 🚧 Stub |
| **Ollama** | Local models | ⚠️ Limited | ⚠️ Limited | 🚧 Stub |

*Variable support depends on the underlying model

## Development

### Running Tests

```bash
# Quick smoke tests
make test-quick

# All integration tests (requires API keys)
make test

# Specific test categories
make test-basic        # Provider basics
make test-structured   # Structured output
make test-agentic     # Autonomous agents

# Provider-specific tests
make test-openai
make test-anthropic
make test-openrouter
```

### Code Quality

```bash
make format      # Format code with black/isort
make lint        # Check with ruff
make type-check  # Run mypy
```

### Using pytest directly

```bash
# Run all integration tests
pytest tests/ -m requires_api_key -v

# Run specific tests
pytest tests/test_providers_integration.py::TestProviderBasics -v
pytest tests/ -k "openai and basic" -v
```

See [TESTING.md](TESTING.md) for comprehensive testing documentation.

## Architecture

```
src/alloy/
├── core/              # Core DSL components
│   ├── agent.py       # Agent class with dual interface
│   ├── result.py      # Result monad for error handling
│   ├── memory.py      # Conversation & explicit memory
│   ├── command.py     # Natural language commands
│   ├── agentic_loop.py # Autonomous agent behavior
│   └── contracts.py   # Design-by-contract (TODO)
├── providers/         # Multi-provider system
│   ├── base.py        # Abstract provider interface
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   ├── openrouter_provider.py
│   └── registry.py    # Provider auto-detection
└── utilities/         # Helper utilities
```

## Roadmap

- ✅ Multi-provider system with capability detection
- ✅ Structured output with dataclass parsing
- ✅ Agentic loop with tool calling
- ✅ Memory system and conversation history  
- 🚧 Design-by-contract decorators (`@require`, `@ensure`, `@invariant`)
- 🚧 Pipeline system with `>>` operator
- 🚧 Complete xAI, Gemini, Ollama providers
- 🚧 Full Alloy language parser/interpreter
- 🚧 Claude Code integration
- 🚧 Advanced agent patterns (ReAct, multi-agent coordination)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run the test suite: `make test`
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.