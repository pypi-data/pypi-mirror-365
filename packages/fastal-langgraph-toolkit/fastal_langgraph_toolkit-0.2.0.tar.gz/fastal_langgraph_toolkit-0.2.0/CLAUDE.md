# Fastal LangGraph Toolkit - Claude Code Context

## Project Overview

The **Fastal LangGraph Toolkit** is a production-ready Python package developed by the Fastal Group to provide common utilities and tools for building enterprise-grade LangGraph agents. Originally developed internally for client projects, this toolkit has been open-sourced to support the broader LangGraph community.

**PyPI Package**: `fastal-langgraph-toolkit`  
**Current Version**: v0.1.1 (Latest with critical bug fixes)  
**Development**: Uses `uv` (not pip) for dependency management  
**License**: MIT  
**Target**: Python 3.10+

## Core Architecture

### Main Modules

1. **ModelFactory** (`src/fastal/langgraph/toolkit/models/`)
   - Multi-provider LLM and embedding factory
   - Supports: OpenAI, Anthropic, Ollama, AWS Bedrock
   - Provider availability detection
   - Configuration abstraction

2. **Memory Management** (`src/fastal/langgraph/toolkit/memory/`)
   - `SummaryManager`: Intelligent conversation summarization
   - `SummaryConfig`: Configurable summarization behavior
   - `SummarizableState`: TypedDict base class for summary-enabled states

3. **Providers** (`src/fastal/langgraph/toolkit/models/providers/`)
   - LLM providers: `llm/anthropic.py`, `llm/bedrock.py`, `llm/ollama.py`, `llm/openai.py`
   - Embedding providers: `embeddings/bedrock.py`, `embeddings/ollama.py`, `embeddings/openai.py`

## Key Features

### 1. Multi-Provider Model Factory
- **Unified API**: Single interface for all LLM/embedding providers
- **Configuration Injection**: Clean separation of concerns
- **Provider Health Checks**: Automatic availability detection
- **Seamless Switching**: Change providers without code changes

```python
from fastal.langgraph.toolkit import ModelFactory
from types import SimpleNamespace

config = SimpleNamespace(api_key="your-key", temperature=0.7)
llm = ModelFactory.create_llm("openai", "gpt-4o", config)
embeddings = ModelFactory.create_embeddings("openai", "text-embedding-3-small", config)
```

### 2. Intelligent Conversation Summarization
- **Ready-to-Use LangGraph Node**: `summary_node()` method provides instant integration
- **Conversation Pair Counting**: Smart Human+AI message pair detection
- **ReAct Tool Filtering**: Automatic exclusion of tool calls from summaries
- **Configurable Thresholds**: Customizable trigger points
- **Context Preservation**: Keep recent conversations for continuity
- **Custom Prompts**: Domain-specific summarization templates
- **State Auto-Injection**: Works with existing states
- **Built-in Error Handling**: Robust error management with optional logging

```python
from fastal.langgraph.toolkit import SummaryManager, SummarizableState
from langgraph.graph import StateGraph
import logging

class MyAgentState(SummarizableState):
    messages: Annotated[list, add_messages]
    thread_id: str
    # summary and last_summarized_index automatically provided

summary_manager = SummaryManager(llm)

# Optional: Configure logging for summary operations
logger = logging.getLogger(__name__)
summary_manager.set_logger(logger)

# Add ready-to-use summary node to your workflow
workflow = StateGraph(MyAgentState)
workflow.add_node("summary_check", summary_manager.summary_node)
workflow.set_entry_point("summary_check")
```

### 3. Memory Optimization
- **Token Efficiency**: 70-90% reduction in context size
- **Cost Control**: Significant reduction in API costs for long conversations
- **State Management**: Clean integration with LangGraph checkpointing

## Development Commands

### Build System
- **Package Manager**: `uv` (modern, fast Python package manager)
- **Build Backend**: `hatchling`
- **Test Framework**: Basic test suite in `tests/`

### Essential Commands
```bash
# Install dependencies
uv sync

# Run tests (with async support)
uv run pytest

# Build package
uv build

# Install in development mode
uv add --editable .

# Type checking (if configured)
uv run mypy src/

# Linting (if configured)
uv run ruff check src/
uv run ruff format src/

# Publish to PyPI (automated via GitHub Actions)
uv run twine upload dist/* --skip-existing
```

### Development Dependencies
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **twine**: PyPI publishing

## Configuration Requirements

### Provider Configuration
The toolkit requires `SimpleNamespace` objects (not dictionaries) for type safety:

```python
from types import SimpleNamespace

# ✅ Correct
config = SimpleNamespace(
    api_key="sk-...",
    temperature=0.7,
    streaming=True
)

# ❌ Wrong - Don't use dictionaries
config = {"api_key": "sk-...", "temperature": 0.7}
```

### Environment Variables
Common environment variables:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`

## Production Usage Patterns

### Enterprise Multi-Provider Setup
```python
import logging

class EnterpriseAgent:
    def __init__(self):
        # Primary: OpenAI, Fallback: Anthropic
        self.primary_llm = self._get_openai_llm()
        self.fallback_llm = self._get_anthropic_llm()
        self.summary_manager = SummaryManager(self.get_llm())
        
        # Configure logging for summary operations
        logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.summary_manager.set_logger(logger)
```

### Memory-Optimized Long Conversations
```python
# Aggressive summarization for cost efficiency
config = SummaryConfig(
    pairs_threshold=5,    # Frequent summarization
    recent_pairs_to_preserve=2,  # Minimal recent context
    max_summary_length=600
)
```

### Domain-Specific Summarization with Ready-to-Use Node
```python
# Customer service example with ready-to-use summary node
config = SummaryConfig(
    pairs_threshold=8,
    new_summary_prompt="""
    Create structured customer service summary:
    - Customer Information
    - Issue Summary  
    - Actions Taken
    - Current Status
    """
)

summary_manager = SummaryManager(llm, config)
summary_manager.set_logger(logger)  # Optional logging

# Use in LangGraph workflow
workflow.add_node("summary_check", summary_manager.summary_node)
```

## Testing and Quality

### Test Structure
- `tests/test_factory.py`: Model factory tests
- `tests/test_summary.py`: Summarization tests
- Basic unit test coverage for core functionality

### Performance Considerations
- **Token Efficiency**: ~84% reduction for 50-message conversations
- **Response Time**: 2-5s overhead for summary creation, 50-80% faster processing
- **Memory Usage**: 70-90% reduction in state size

## PyPI Publishing

### Package Configuration
- **Name**: `fastal-langgraph-toolkit`
- **Version**: `0.1.0` (Development status: Alpha)
- **Homepage**: `https://github.com/FastalGroup/fastal-langgraph-toolkit`
- **Dependencies**: LangChain Core, LangGraph, Pydantic

### Optional Dependencies
```toml
[project.optional-dependencies]
openai = ["langchain-openai>=0.1"]
anthropic = ["langchain-anthropic>=0.1"]
ollama = ["langchain-ollama>=0.1"]
bedrock = ["langchain-aws>=0.1", "boto3>=1.26"]
all = [all providers]
```

## Release Management

### Versioning Strategy
- **v0.1.0**: Initial release (had TYPE_CHECKING import issues)
- **v0.1.1**: Current stable - Critical bug fixes for import compatibility

### GitHub Actions Workflow
- **Automated PyPI Publishing**: Triggered on GitHub releases
- **CI/CD Pipeline**: Syntax checking and testing
- **Secret Management**: PYPI_API_TOKEN configured for auto-publishing

### Release Process
1. Update version in `pyproject.toml` and `__init__.py`
2. Commit changes and create Git tag: `git tag v0.x.x`
3. Push tag: `git push origin v0.x.x`
4. Create GitHub release with `gh release create`
5. GitHub Actions automatically publishes to PyPI

## Critical Bug Fixes (v0.1.1)

### TYPE_CHECKING Import Resolution
**Problem**: v0.1.0 had import errors when optional dependencies weren't installed
```python
# v0.1.0 - PROBLEMATIC
def _create_model(self) -> OpenAIEmbeddings:  # Evaluated at import!

# v0.1.1 - FIXED
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from langchain_openai import OpenAIEmbeddings

def _create_model(self) -> "OpenAIEmbeddings":  # String annotation
```

**Solution**: Use TYPE_CHECKING for conditional imports and string type annotations

## Best Practices for Claude Code

1. **Use uv for all package operations** - This project uses uv, not pip
2. **Always use latest version** - Install with `pip install fastal-langgraph-toolkit` (gets v0.1.1)
3. **Understand the provider system** - Check available providers before use
4. **Focus on the two main modules** - ModelFactory and SummaryManager
5. **Test with SimpleNamespace configs** - Required for proper operation
6. **Consider memory optimization** - The summarization system is the key differentiator
7. **Use ready-to-use summary_node()** - Prefer `summary_manager.summary_node` over custom implementations
8. **Configure logging** - Use `set_logger()` for automatic summary operation logging
9. **Follow the existing patterns** - Enterprise-grade, production-ready code style

## Common Issues & Solutions

1. **"SimpleNamespace required" Error**: Use `types.SimpleNamespace` not dict
2. **Import errors without optional deps**: Upgrade to v0.1.1 (has TYPE_CHECKING fixes)
3. **Provider not available**: Check optional dependencies are installed
4. **Summary not created**: Verify conversation pair threshold is reached
5. **Memory usage**: Adjust `pairs_threshold` and `recent_pairs_to_preserve`
6. **Summary node errors**: Use built-in `summary_manager.summary_node` with error handling
7. **Missing summary logs**: Configure logger with `summary_manager.set_logger(logger)`

## Testing Strategy

### Environment Isolation
- **Development**: Full environment with all optional dependencies
- **CI**: Clean environment testing for import compatibility
- **Production Testing**: Multi-environment validation before release

### Test Coverage
- Unit tests for core functionality
- Integration tests for provider compatibility
- Async test support with pytest-asyncio
- Import testing without optional dependencies

This toolkit represents battle-tested patterns from real enterprise implementations, extracted into a reusable package for the LangGraph community.