# Fastal LangGraph Toolkit

[![CI](https://github.com/FastalGroup/fastal-langgraph-toolkit/actions/workflows/test.yml/badge.svg)](https://github.com/FastalGroup/fastal-langgraph-toolkit/actions/workflows/test.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/fastal-langgraph-toolkit.svg)](https://badge.fury.io/py/fastal-langgraph-toolkit)

**Production-ready toolkit for building enterprise LangGraph agents with multi-provider support and intelligent conversation management.**

## 🏢 About

The Fastal LangGraph Toolkit was originally developed internally by the **Fastal Group** to support enterprise-grade agentic application implementations across multiple client projects. After proving its effectiveness in production environments, we've open-sourced this toolkit to contribute to the broader LangGraph community.

### Why This Toolkit?

Building production LangGraph agents involves solving common challenges in advanced research and development projects:
- **Multi-provider Management**: Support for multiple LLM/embedding providers with seamless switching
- **Context Management**: Intelligent conversation summarization for long-running sessions
- **Memory Optimization**: Token-efficient context handling for cost control
- **Type Safety**: Proper state management with TypedDict integration
- **Configuration Injection**: Clean separation between business logic and framework concerns

This toolkit provides battle-tested solutions for these challenges, extracted from real enterprise implementations.

## ✨ Features

### 🔄 Multi-Provider Model Factory (Chat LLM & Embeddings)
The current version of the model factory supports the following providers, more providers will be added in future versions.

- **LLM Support**: OpenAI, Anthropic, Ollama, AWS Bedrock
- **Embeddings Support**: OpenAI, Ollama, AWS Bedrock  

Main fetures:
- **Configuration Injection**: Clean provider abstraction
- **Provider Health Checks**: Availability validation
- **Seamless Switching**: Change providers without code changes

### 🧠 Intelligent Conversation Summarization

The LangChain/LangGraph framework provides good support for managing both short-term and long-term memory in agents through the LangMem module. However, we found that automated summarization based solely on token counting is not a sufficient approach for most real and complex agents. The solution included in this kit offers an alternative and more sophisticated method, based on the structure of the conversation and a focus on the object and content of the discussions.

Features:
- **Ready-to-Use LangGraph Node**: `summary_node()` method provides instant integration
- **Conversation Pair Counting**: Smart Human+AI message pair detection
- **ReAct Tool Filtering**: Automatic exclusion of tool calls from summaries
- **Configurable Thresholds**: Customizable trigger points for summarization
- **Context Preservation**: Keep recent conversations for continuity
- **Custom Prompts**: Domain-specific summarization templates
- **State Auto-Injection**: Seamless integration with existing states
- **Token Optimization**: Reduce context length for cost efficiency
- **Built-in Error Handling**: Robust error management with optional logging

### 💾 Memory Management
- **`SummarizableState`**: Type-safe base class for summary-enabled states
- **Automatic State Management**: No manual field initialization required
- **LangGraph Integration**: Native compatibility with LangGraph checkpointing
- **Clean Architecture**: Separation of concerns between summary and business logic

## 📦 Installation

### From PyPI (Recommended)
```bash
# Using uv (recommended)
uv add fastal-langgraph-toolkit

# Using pip
pip install fastal-langgraph-toolkit
```

### Development Installation
```bash
# Clone the repository
git clone https://github.com/fastal/langgraph-toolkit.git
cd fastal-langgraph-toolkit

# Install in editable mode with uv
uv add --editable .

# Or with pip
pip install -e .
```

### Requirements
- **Python**: 3.10+ 
- **LangChain**: Core components for LLM integration
- **LangGraph**: State management and agent workflows
- **Pydantic**: Type validation and settings management

## 🚀 Quick Start

### Multi-Provider Model Factory

```python
from fastal.langgraph.toolkit import ModelFactory
from types import SimpleNamespace

# Configuration using SimpleNamespace (required)
config = SimpleNamespace(
    api_key="your-api-key",
    temperature=0.7,
    streaming=True  # Enable streaming for real-time responses
)

# Create LLM with different providers
openai_llm = ModelFactory.create_llm("openai", "gpt-4o", config)
claude_llm = ModelFactory.create_llm("anthropic", "claude-3-sonnet-20240229", config)
local_llm = ModelFactory.create_llm("ollama", "llama2", config)

# Create embeddings
embeddings = ModelFactory.create_embeddings("openai", "text-embedding-3-small", config)

# Check what's available in your environment
providers = ModelFactory.get_available_providers()
print(f"Available LLM providers: {providers['llm']}")
print(f"Available embedding providers: {providers['embeddings']}")
```

### Intelligent Conversation Summarization

#### Basic Setup
```python
from fastal.langgraph.toolkit import SummaryManager, SummaryConfig, SummarizableState
from langchain_core.messages import HumanMessage, AIMessage
from typing import Annotated
from langgraph.graph.message import add_messages

# 1. Define your state using SummarizableState (recommended)
class MyAgentState(SummarizableState):
    """Your agent state with automatic summary support"""
    messages: Annotated[list, add_messages]
    thread_id: str
    # summary and last_summarized_index are automatically provided

# 2. Create summary manager with default settings
llm = ModelFactory.create_llm("openai", "gpt-4o", config)
summary_manager = SummaryManager(llm)

# 3. Use ready-to-use summary node in your LangGraph workflow
from langgraph.graph import StateGraph
import logging

# Optional: Configure logging for summary operations
logger = logging.getLogger(__name__)
summary_manager.set_logger(logger)

# Add to your workflow
workflow = StateGraph(MyAgentState)
workflow.add_node("summary_check", summary_manager.summary_node)  # Ready-to-use!
workflow.set_entry_point("summary_check")
```

#### Advanced Configuration
```python
# Custom configuration for domain-specific needs
custom_config = SummaryConfig(
    pairs_threshold=20,  # Trigger summary after 20 conversation pairs
    recent_pairs_to_preserve=5,  # Keep last 5 pairs in full context
    max_summary_length=500,  # Max words in summary
    
    # Custom prompts for your domain
    new_summary_prompt="""
    Analyze this customer support conversation and create a concise summary focusing on:
    - Customer's main issue or request
    - Actions taken by the agent
    - Current status of the resolution
    - Any pending items or next steps
    
    Conversation to summarize:
    {messages_text}
    """,
    
    combine_summary_prompt="""
    Update the existing summary with new information from the recent conversation.
    
    Previous summary:
    {existing_summary}
    
    New conversation:
    {messages_text}
    
    Provide an updated comprehensive summary:
    """
)

summary_manager = SummaryManager(llm, custom_config)
```

#### Complete LangGraph Integration Example

**Simple Approach (Recommended):**
```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import logging

logger = logging.getLogger(__name__)

class CustomerSupportAgent:
    def __init__(self):
        self.llm = ModelFactory.create_llm("openai", "gpt-4o", config)
        self.summary_manager = SummaryManager(self.llm, custom_config)
        # Optional: Configure logging for summary operations
        self.summary_manager.set_logger(logger)
        self.graph = self._create_graph()
    
    async def _agent_node(self, state: MyAgentState) -> dict:
        """Main agent logic with optimized context"""
        messages = state["messages"]
        last_idx = state.get("last_summarized_index", 0)
        summary = state.get("summary")
        
        # Use only recent messages + summary for context efficiency
        recent_messages = messages[last_idx:]
        
        if summary:
            system_msg = f"Previous conversation summary: {summary}\n\nContinue the conversation:"
            context = [SystemMessage(content=system_msg)] + recent_messages
        else:
            context = recent_messages
        
        response = await self.llm.ainvoke(context)
        return {"messages": [response]}
    
    def _create_graph(self):
        workflow = StateGraph(MyAgentState)
        
        # Use ready-to-use summary node from toolkit
        workflow.add_node("summary_check", self.summary_manager.summary_node)
        workflow.add_node("agent", self._agent_node)
        
        workflow.set_entry_point("summary_check")
        workflow.add_edge("summary_check", "agent")
        workflow.add_edge("agent", "__end__")
        
        return workflow
    
    async def process_message(self, message: str, thread_id: str):
        """Process user message with automatic summarization"""
        async with AsyncPostgresSaver.from_conn_string(db_url) as checkpointer:
            app = self.graph.compile(checkpointer=checkpointer)
            
            config = {"configurable": {"thread_id": thread_id}}
            input_state = {"messages": [HumanMessage(content=message)]}
            
            result = await app.ainvoke(input_state, config=config)
            return result["messages"][-1].content
```

**Advanced Approach (Custom Implementation):**
```python
# If you need custom logic in your summary node
class AdvancedCustomerSupportAgent:
    def __init__(self):
        self.llm = ModelFactory.create_llm("openai", "gpt-4o", config)
        self.summary_manager = SummaryManager(self.llm, custom_config)
        self.graph = self._create_graph()
    
    async def _custom_summary_node(self, state: MyAgentState) -> dict:
        """Custom summary node with additional business logic"""
        thread_id = state.get("thread_id", "")
        
        # Custom business logic before summarization
        if self._should_skip_summary(state):
            return {}
        
        # Use summary manager for the actual summarization
        if await self.summary_manager.should_create_summary(state):
            result = await self.summary_manager.process_summary(state)
            
            # Custom logging or analytics
            if result:
                logger.info(f"Summary created for customer thread {thread_id}")
                self._track_summary_analytics(state, result)
            
            return result
        
        return {}
    
    def _should_skip_summary(self, state):
        """Custom business logic to skip summarization"""
        # Example: Skip for priority customers or short sessions
        return False
    
    def _track_summary_analytics(self, state, result):
        """Custom analytics tracking"""
        pass
```

## 📋 API Reference

### ModelFactory

Main factory class for creating LLM and embedding instances across multiple providers.

#### `ModelFactory.create_llm(provider: str, model: str, config: SimpleNamespace) -> BaseChatModel`

Creates an LLM instance for the specified provider.

**Parameters:**
- `provider`: Provider name (`"openai"`, `"anthropic"`, `"ollama"`, `"bedrock"`)
- `model`: Model name (e.g., `"gpt-4o"`, `"claude-3-sonnet-20240229"`)
- `config`: Configuration object with provider-specific settings

**Returns:** LangChain `BaseChatModel` instance

**Example:**
```python
from types import SimpleNamespace
from fastal.langgraph.toolkit import ModelFactory

config = SimpleNamespace(api_key="sk-...", temperature=0.7, streaming=True)
llm = ModelFactory.create_llm("openai", "gpt-4o", config)
```

#### `ModelFactory.create_embeddings(provider: str, model: str, config: SimpleNamespace) -> Embeddings`

Creates an embeddings instance for the specified provider.

**Parameters:**
- `provider`: Provider name (`"openai"`, `"ollama"`, `"bedrock"`)
- `model`: Model name (e.g., `"text-embedding-3-small"`)
- `config`: Configuration object with provider-specific settings

**Returns:** LangChain `Embeddings` instance

#### `ModelFactory.get_available_providers() -> dict`

Returns available providers in the current environment.

**Returns:** Dictionary with `"llm"` and `"embeddings"` keys containing available provider lists

### SummaryManager

Manages intelligent conversation summarization with configurable thresholds and custom prompts.

#### `SummaryManager(llm: BaseChatModel, config: SummaryConfig | None = None)`

Initialize summary manager with LLM and optional configuration.

**Parameters:**
- `llm`: LangChain LLM instance for generating summaries
- `config`: Optional `SummaryConfig` instance (uses defaults if None)

#### `async should_create_summary(state: dict) -> bool`

Determines if summarization is needed based on conversation pairs threshold.

**Parameters:**
- `state`: Current agent state containing messages and summary info

**Returns:** `True` if summary should be created, `False` otherwise

#### `async process_summary(state: dict) -> dict`

Creates or updates conversation summary and returns state updates.

**Parameters:**
- `state`: Current agent state

**Returns:** Dictionary with `summary` and `last_summarized_index` fields

#### `count_conversation_pairs(messages: list, start_index: int = 0) -> int`

Counts Human+AI conversation pairs, excluding tool calls.

**Parameters:**
- `messages`: List of LangChain messages
- `start_index`: Starting index for counting (default: 0)

**Returns:** Number of complete conversation pairs

#### `async summary_node(state: dict) -> dict`

**Ready-to-use LangGraph node for conversation summarization.**

This method provides a complete LangGraph node that can be directly added to workflows. It handles the entire summary workflow internally and provides optional logging.

**Parameters:**
- `state`: LangGraph state (will be auto-injected with summary fields if missing)

**Returns:** Empty dict if no summary needed, or dict with summary fields if created

**Example:**
```python
# In your LangGraph workflow
summary_manager = SummaryManager(llm, config)
summary_manager.set_logger(logger)  # Optional logging

workflow.add_node("summary_check", summary_manager.summary_node)
workflow.set_entry_point("summary_check")
```

#### `set_logger(logger)`

Set logger for summary_node logging (optional).

**Parameters:**
- `logger`: Logger instance for summary_node operations

**Note:** When a logger is configured, `summary_node()` will automatically log when summaries are created.

### SummaryConfig

Configuration class for customizing summarization behavior.

#### `SummaryConfig(**kwargs)`

**Parameters:**
- `pairs_threshold: int = 10` - Trigger summary after N conversation pairs
- `recent_pairs_to_preserve: int = 3` - Keep N recent pairs in context
- `max_summary_length: int = 200` - Maximum words in summary
- `new_summary_prompt: str` - Template for creating new summaries
- `combine_summary_prompt: str` - Template for updating existing summaries

**Default Prompts:**
```python
# Default new summary prompt
new_summary_prompt = """
Analyze the conversation and create a concise summary highlighting:
- Main topics discussed
- Key decisions or conclusions
- Important context for future interactions

Conversation:
{messages_text}

Summary:
"""

# Default combine summary prompt  
combine_summary_prompt = """
Existing Summary: {existing_summary}

New Conversation: {messages_text}

Create an updated summary that combines the essential information:
"""
```

### SummarizableState

Base TypedDict class for states that support automatic summarization.

#### Inheritance Usage
```python
from fastal.langgraph.toolkit import SummarizableState
from typing import Annotated
from langgraph.graph.message import add_messages

class MyAgentState(SummarizableState):
    """Your custom state with summary support"""
    messages: Annotated[list, add_messages]
    thread_id: str
    # summary: str | None - automatically provided
    # last_summarized_index: int - automatically provided
```

**Provided Fields:**
- `summary: str | None` - Current conversation summary
- `last_summarized_index: int` - Index of first message NOT in last summary

## ⚙️ Configuration

### SimpleNamespace Requirement

The toolkit requires configuration objects (not dictionaries) for type safety and dot notation access:

```python
from types import SimpleNamespace

# ✅ Correct - SimpleNamespace
config = SimpleNamespace(
    api_key="sk-...",
    base_url="https://api.openai.com/v1",  # Optional
    temperature=0.7,                        # Optional
    streaming=True                          # Optional
)

# ❌ Incorrect - Dictionary
config = {"api_key": "sk-...", "temperature": 0.7}
```

### Provider-Specific Configuration

#### OpenAI
```python
openai_config = SimpleNamespace(
    api_key="sk-...",              # Required (or set OPENAI_API_KEY)
    base_url="https://api.openai.com/v1",  # Optional
    organization="org-...",         # Optional
    temperature=0.7,               # Optional
    streaming=True,                # Optional
    max_tokens=1000                # Optional
)
```

#### Anthropic
```python
anthropic_config = SimpleNamespace(
    api_key="sk-ant-...",          # Required (or set ANTHROPIC_API_KEY)
    temperature=0.7,               # Optional
    streaming=True,                # Optional
    max_tokens=1000                # Optional
)
```

#### Ollama (Local)
```python
ollama_config = SimpleNamespace(
    base_url="http://localhost:11434",  # Optional (default)
    temperature=0.7,                    # Optional
    streaming=True                      # Optional
)
```

#### AWS Bedrock
```python
bedrock_config = SimpleNamespace(
    region="us-east-1",            # Optional (uses AWS config)
    aws_access_key_id="...",       # Optional (uses AWS config)
    aws_secret_access_key="...",   # Optional (uses AWS config)
    temperature=0.7,               # Optional
    streaming=True                 # Optional
)
```

### Environment Variables Helper

```python
from fastal.langgraph.toolkit.models.config import get_default_config

# Automatically uses environment variables
openai_config = get_default_config("openai")     # Uses OPENAI_API_KEY
anthropic_config = get_default_config("anthropic") # Uses ANTHROPIC_API_KEY
```

## 🎯 Advanced Examples

### Enterprise Multi-Provider Setup

```python
from fastal.langgraph.toolkit import ModelFactory
from types import SimpleNamespace
import os

class EnterpriseAgentConfig:
    """Enterprise configuration with fallback providers"""
    
    def __init__(self):
        self.primary_llm = self._setup_primary_llm()
        self.fallback_llm = self._setup_fallback_llm()
        self.embeddings = self._setup_embeddings()
    
    def _setup_primary_llm(self):
        """Primary: OpenAI GPT-4"""
        if os.getenv("OPENAI_API_KEY"):
            config = SimpleNamespace(
                api_key=os.getenv("OPENAI_API_KEY"),
                temperature=0.1,
                streaming=True,
                max_tokens=2000
            )
            return ModelFactory.create_llm("openai", "gpt-4o", config)
        return None
    
    def _setup_fallback_llm(self):
        """Fallback: Anthropic Claude"""
        if os.getenv("ANTHROPIC_API_KEY"):
            config = SimpleNamespace(
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                temperature=0.1,
                streaming=True,
                max_tokens=2000
            )
            return ModelFactory.create_llm("anthropic", "claude-3-sonnet-20240229", config)
        return None
    
    def _setup_embeddings(self):
        """Embeddings with local fallback"""
        # Try OpenAI first
        if os.getenv("OPENAI_API_KEY"):
            config = SimpleNamespace(api_key=os.getenv("OPENAI_API_KEY"))
            return ModelFactory.create_embeddings("openai", "text-embedding-3-small", config)
        
        # Fallback to local Ollama
        config = SimpleNamespace(base_url="http://localhost:11434")
        return ModelFactory.create_embeddings("ollama", "nomic-embed-text", config)
    
    def get_llm(self):
        """Get available LLM with fallback logic"""
        return self.primary_llm or self.fallback_llm
```

### Domain-Specific Summarization

```python
from fastal.langgraph.toolkit import SummaryManager, SummaryConfig

class CustomerServiceSummaryManager:
    """Specialized summary manager for customer service conversations"""
    
    def __init__(self, llm):
        # Customer service specific configuration
        self.config = SummaryConfig(
            pairs_threshold=8,  # Shorter conversations in support
            recent_pairs_to_preserve=3,
            max_summary_length=400,
            
            new_summary_prompt="""
            Analyze this customer service conversation and create a structured summary:

            **Customer Information:**
            - Name/Contact: [Extract if mentioned]
            - Account/Order: [Extract if mentioned]

            **Issue Summary:**
            - Problem: [Main issue described]
            - Category: [Technical/Billing/General/etc.]
            - Urgency: [High/Medium/Low based on language]

            **Actions Taken:**
            - Solutions attempted: [List what agent tried]
            - Information provided: [Key info given to customer]

            **Current Status:**
            - Resolution status: [Resolved/Pending/Escalated]
            - Next steps: [What needs to happen next]

            **Conversation:**
            {messages_text}

            **Structured Summary:**
            """,
            
            combine_summary_prompt="""
            Update the customer service summary with new conversation information:

            **Previous Summary:**
            {existing_summary}

            **New Conversation:**
            {messages_text}

            **Updated Summary:**
            Merge the information, updating status and adding new actions/developments:
            """
        )
        
        self.summary_manager = SummaryManager(llm, self.config)
    
    async def process_summary(self, state):
        """Process with customer service specific logic"""
        return await self.summary_manager.process_summary(state)
```

### Memory-Optimized Long Conversations

```python
from fastal.langgraph.toolkit import SummarizableState, SummaryManager
from typing import Annotated
from langgraph.graph.message import add_messages

class OptimizedConversationState(SummarizableState):
    """State optimized for very long conversations"""
    messages: Annotated[list, add_messages]
    thread_id: str
    user_context: dict = {}  # Additional user context
    conversation_metadata: dict = {}  # Metadata for analytics

class LongConversationAgent:
    """Agent optimized for handling very long conversations"""
    
    def __init__(self, llm):
        # Aggressive summarization for memory efficiency
        config = SummaryConfig(
            pairs_threshold=5,    # Frequent summarization
            recent_pairs_to_preserve=2,  # Minimal recent context
            max_summary_length=600,  # Comprehensive summaries
        )
        
        self.summary_manager = SummaryManager(llm, config)
        self.llm = llm
    
    async def process_with_optimization(self, state: OptimizedConversationState):
        """Process message with aggressive memory optimization"""
        
        # Always check for summarization opportunities
        if await self.summary_manager.should_create_summary(state):
            # Create summary to optimize memory
            summary_update = await self.summary_manager.process_summary(state)
            state.update(summary_update)
        
        # Use only recent context + summary for LLM call
        messages = state["messages"]
        last_idx = state.get("last_summarized_index", 0)
        summary = state.get("summary")
        
        # Ultra-minimal context for cost efficiency
        recent_messages = messages[last_idx:]
        
        if summary:
            context = f"Context: {summary}\n\nContinue conversation:"
            context_msg = SystemMessage(content=context)
            llm_input = [context_msg] + recent_messages[-2:]  # Only last exchange
        else:
            llm_input = recent_messages[-4:]  # Minimal fallback
        
        response = await self.llm.ainvoke(llm_input)
        return {"messages": [response]}
```

### Token Usage Analytics

```python
import tiktoken
from collections import defaultdict

class TokenOptimizedSummaryManager:
    """Summary manager with token usage tracking and optimization"""
    
    def __init__(self, llm, config=None):
        self.summary_manager = SummaryManager(llm, config)
        self.tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT-4 tokenizer
        self.token_stats = defaultdict(int)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))
    
    async def process_with_analytics(self, state):
        """Process summary with token usage analytics"""
        messages = state["messages"]
        
        # Count tokens before summarization
        total_tokens_before = sum(
            self.count_tokens(str(msg.content)) for msg in messages
        )
        
        # Process summary
        result = await self.summary_manager.process_summary(state)
        
        if result:  # Summary was created
            summary = result.get("summary", "")
            last_idx = result.get("last_summarized_index", 0)
            
            # Count tokens after summarization
            remaining_messages = messages[last_idx:]
            remaining_tokens = sum(
                self.count_tokens(str(msg.content)) for msg in remaining_messages
            )
            summary_tokens = self.count_tokens(summary)
            total_tokens_after = remaining_tokens + summary_tokens
            
            # Track savings
            tokens_saved = total_tokens_before - total_tokens_after
            self.token_stats["tokens_saved"] += tokens_saved
            self.token_stats["summaries_created"] += 1
            
            print(f"💰 Token optimization: {tokens_saved} tokens saved "
                  f"({total_tokens_before} → {total_tokens_after})")
        
        return result
    
    def get_analytics(self):
        """Get token usage analytics"""
        return dict(self.token_stats)
```

## 🔧 Best Practices

### 1. State Design
```python
# ✅ Use SummarizableState for automatic summary support
class MyAgentState(SummarizableState):
    messages: Annotated[list, add_messages]
    thread_id: str

# ❌ Don't manually define summary fields
class BadAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    thread_id: str
    summary: str | None  # Manual definition not needed
    last_summarized_index: int  # Manual definition not needed
```

### 2. Graph Architecture
```python
# ✅ Use ready-to-use summary node (Recommended)
summary_manager = SummaryManager(llm, config)
summary_manager.set_logger(logger)  # Optional logging

workflow.add_node("summary_check", summary_manager.summary_node)
workflow.set_entry_point("summary_check")  # Always check summary first
workflow.add_edge("summary_check", "agent")  # Then process
workflow.add_edge("tools", "agent")  # Tools return to agent, not summary

# ✅ Alternative: Custom summary node (if you need custom logic)
async def custom_summary_node(state):
    if await summary_manager.should_create_summary(state):
        return await summary_manager.process_summary(state)
    return {}

workflow.add_node("summary_check", custom_summary_node)

# ❌ Don't create summaries mid-conversation
# This would create summaries during tool execution
workflow.add_edge("tools", "summary_check")  # Wrong!
```

### 3. Configuration Management
```python
# ✅ Environment-based configuration
class ProductionConfig:
    def __init__(self):
        self.llm_config = SimpleNamespace(
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.1,  # Conservative for production
            streaming=True
        )
        
        self.summary_config = SummaryConfig(
            pairs_threshold=12,  # Longer thresholds for production
            recent_pairs_to_preserve=4,
            max_summary_length=300
        )

# ❌ Don't hardcode credentials
bad_config = SimpleNamespace(api_key="sk-hardcoded-key")  # Never do this!
```

### 4. Error Handling
```python
# ✅ Use built-in error handling (Recommended)
# The summary_node() method already includes robust error handling
summary_manager = SummaryManager(llm, config)
summary_manager.set_logger(logger)  # Automatic error logging

workflow.add_node("summary_check", summary_manager.summary_node)

# ✅ Custom error handling (if needed)
async def robust_summary_node(state):
    """Custom summary node with additional error handling"""
    try:
        if await summary_manager.should_create_summary(state):
            return await summary_manager.process_summary(state)
        return {}
    except Exception as e:
        logger.error(f"Summary creation failed: {e}")
        # Continue without summary rather than failing
        return {}
```

### 5. Performance Monitoring
```python
import time
from functools import wraps

# ✅ Built-in monitoring (Recommended)
# The summary_node() automatically logs performance when logger is configured
summary_manager = SummaryManager(llm, config)
summary_manager.set_logger(logger)  # Automatic performance logging

workflow.add_node("summary_check", summary_manager.summary_node)

# ✅ Custom performance monitoring (if needed)
def monitor_performance(func):
    """Decorator to monitor summary performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start_time
        
        if result:  # Summary was created
            logger.info(f"Summary created in {duration:.2f}s")
        
        return result
    return wrapper

# Usage with custom node
@monitor_performance
async def monitored_summary_node(state):
    return await summary_manager.process_summary(state)
```

## 📊 Performance Considerations

### Token Efficiency
- **Without summarization**: ~50,000 tokens for 50-message conversation
- **With summarization**: ~8,000 tokens (84% reduction)
- **Cost savings**: Proportional to token reduction

### Response Time
- **Summary creation**: 2-5 seconds additional latency
- **Context processing**: 50-80% faster with summarized context
- **Overall impact**: Net positive for conversations >15 messages

### Memory Usage
- **State size**: Reduced by 70-90% with active summarization
- **Checkpointer storage**: Significantly smaller state objects
- **Database impact**: Reduced checkpoint table growth

## 🛠️ Troubleshooting

### Common Issues

#### 1. "SimpleNamespace required" Error
```python
# ❌ Cause: Using dictionary instead of SimpleNamespace
config = {"api_key": "sk-..."}

# ✅ Solution: Use SimpleNamespace
from types import SimpleNamespace
config = SimpleNamespace(api_key="sk-...")
```

#### 2. Summary Not Created
```python
# Check if threshold is reached
pairs = summary_manager.count_conversation_pairs(state["messages"])
print(f"Current pairs: {pairs}, Threshold: {config.pairs_threshold}")

# Check message types
for i, msg in enumerate(state["messages"]):
    print(f"{i}: {type(msg).__name__} - {hasattr(msg, 'tool_calls')}")
```

#### 3. Provider Not Available
```python
# Check available providers
providers = ModelFactory.get_available_providers()
print(f"Available: {providers}")

# Verify environment variables
import os
print(f"OpenAI key set: {bool(os.getenv('OPENAI_API_KEY'))}")
```

### Debug Mode
```python
# Enable debug logging for detailed output
import logging
logging.getLogger("fastal.langgraph.toolkit").setLevel(logging.DEBUG)
```

## License

MIT License