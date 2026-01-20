# 🤖 MCP Agent Framework

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-purple.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Enterprise-grade agent orchestration framework** implementing the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) standard. Build, deploy, and manage AI agents at scale with standardized interfaces, context management, and observability.

---

## 🌟 What is MCP?

**Model Context Protocol (MCP)** is an open standard by Anthropic that enables AI agents to:
- **Share Context** - Maintain consistent state across interactions
- **Communicate** - Exchange structured messages and data
- **Collaborate** - Work together on complex tasks
- **Integrate** - Connect with external tools and data sources

This framework provides a production-ready implementation of MCP for building sophisticated AI agent systems.

---

## ✨ Features

- 🔌 **Standardized Agent Interface** - Consistent API across all agents
- 🧠 **Context Management** - Automatic state tracking and persistence
- 🔄 **Agent Orchestration** - Sequential, parallel, and conditional workflows
- 📊 **Full Observability** - Tracing, metrics, and logging built-in
- 🛡️ **Error Recovery** - Automatic retries and graceful degradation
- ⚡ **Async-First** - Built for high-performance async execution
- 🔧 **Extensible** - Easy to add custom agents and tools

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                       MCP Agent Framework                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │                   Agent Registry                         │     │
│  │  • Agent Discovery  • Lifecycle Management  • Versioning │     │
│  └─────────────────────────────────────────────────────────┘     │
│                              ↓                                    │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │                  Agent Orchestrator                      │     │
│  │  • Workflow Execution  • Dependency Resolution  • Retry  │     │
│  └─────────────────────────────────────────────────────────┘     │
│                              ↓                                    │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │                   Context Manager                        │     │
│  │  • State Storage  • Cross-Agent Sharing  • Persistence   │     │
│  └─────────────────────────────────────────────────────────┘     │
│                              ↓                                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                  │
│  │  Agent 1   │  │  Agent 2   │  │  Agent N   │                  │
│  │(Extraction)│  │(Validation)│  │ (Custom)   │                  │
│  └────────────┘  └────────────┘  └────────────┘                  │
│                              ↓                                    │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │               Observability Layer                        │     │
│  │  • Tracing (OpenTelemetry)  • Metrics  • Structured Logs │     │
│  └─────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/yourusername/mcp-agent-framework.git
cd mcp-agent-framework
pip install -r requirements.txt
```

### Create Your First Agent

```python
from mcp_framework import BaseAgent, AgentRequest, AgentResponse
from dataclasses import dataclass

@dataclass
class GreetingRequest(AgentRequest):
    name: str

@dataclass  
class GreetingResponse(AgentResponse):
    message: str

class GreetingAgent(BaseAgent):
    """A simple greeting agent."""
    
    async def execute(self, request: GreetingRequest) -> GreetingResponse:
        return GreetingResponse(
            message=f"Hello, {request.name}!",
            success=True
        )

# Use it
agent = GreetingAgent()
response = await agent.execute(GreetingRequest(name="World"))
print(response.message)  # "Hello, World!"
```

### Orchestrate Multiple Agents

```python
from mcp_framework import AgentOrchestrator

orchestrator = AgentOrchestrator()

# Register agents
orchestrator.register("extract", ExtractionAgent())
orchestrator.register("validate", ValidationAgent())
orchestrator.register("store", StorageAgent())

# Execute workflow
result = await orchestrator.execute([
    ("extract", {"source": "document.pdf"}),
    ("validate", {}),  # Uses output from previous step
    ("store", {})
])
```

---

## 📚 Core Components

### 1. BaseAgent

The foundation for all agents:

```python
from mcp_framework import BaseAgent

class MyAgent(BaseAgent):
    async def execute(self, request):
        # Your agent logic here
        return response
    
    async def initialize(self):
        # Optional: Setup resources
        pass
    
    async def cleanup(self):
        # Optional: Cleanup resources
        pass
```

### 2. Context Manager

Share state across agents:

```python
from mcp_framework import ContextManager

context = ContextManager()

# Store context
await context.set("user_id", "12345")
await context.set("session", {"key": "value"}, ttl=3600)

# Retrieve context
user_id = await context.get("user_id")

# Context is automatically shared across agents in a workflow
```

### 3. Agent Orchestrator

Compose complex workflows:

```python
from mcp_framework import AgentOrchestrator

orchestrator = AgentOrchestrator()

# Sequential execution
result = await orchestrator.execute_sequential([agent1, agent2, agent3])

# Parallel execution
results = await orchestrator.execute_parallel([agent1, agent2, agent3])

# Conditional branching
result = await orchestrator.execute_conditional(
    condition=lambda ctx: ctx.get("type") == "premium",
    if_true=premium_agent,
    if_false=standard_agent
)
```

---

## 🤖 Built-in Agent Types

### Knowledge Graph Agents
```python
from mcp_framework.agents.kg import (
    EntityExtractionAgent,
    RelationshipDiscoveryAgent,
    KnowledgeGraphBuilder
)
```

### Retrieval Agents
```python
from mcp_framework.agents.retrieval import (
    VectorSearchAgent,
    WebContentLoaderAgent,
    DocumentReaderAgent
)
```

### Validation Agents
```python
from mcp_framework.agents.validation import (
    DataQualityAgent,
    SchemaValidationAgent,
    ContentModerationAgent
)
```

### Extraction Agents
```python
from mcp_framework.agents.extraction import (
    StructuredDataExtractor,
    JSONExtractor,
    TableExtractor
)
```

---

## 📁 Project Structure

```
mcp-agent-framework/
├── mcp_framework/
│   ├── __init__.py
│   ├── core/
│   │   ├── base_agent.py       # BaseAgent class
│   │   ├── orchestrator.py     # AgentOrchestrator
│   │   ├── context.py          # ContextManager
│   │   ├── registry.py         # Agent registry
│   │   └── protocol.py         # MCP protocol types
│   ├── agents/
│   │   ├── kg/                 # Knowledge graph agents
│   │   ├── retrieval/          # Data retrieval agents
│   │   ├── validation/         # Validation agents
│   │   └── extraction/         # Data extraction agents
│   └── integrations/
│       ├── langfuse.py         # Observability
│       ├── redis.py            # Context persistence
│       └── qdrant.py           # Vector storage
├── examples/
│   ├── basic_agent.py
│   ├── multi_agent_workflow.py
│   └── context_sharing.py
├── tests/
├── requirements.txt
└── README.md
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# Context storage (optional - defaults to in-memory)
MCP_CONTEXT_STORE=redis://localhost:6379

# Observability (optional)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...

# Tracing (optional)
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

### Agent Configuration

```yaml
# config/agents.yaml
agents:
  - name: entity_extractor
    class: mcp_framework.agents.extraction.EntityExtractor
    config:
      model: gemini-1.5-pro
      max_entities: 100
      
  - name: validator
    class: mcp_framework.agents.validation.DataValidator
    config:
      strict_mode: true
```

---

## 🔍 Observability

Built-in support for tracing and metrics:

```python
from mcp_framework import BaseAgent, trace

class MyAgent(BaseAgent):
    @trace("my_agent_execution")
    async def execute(self, request):
        with self.tracer.span("processing"):
            result = await self.process(request)
        
        self.metrics.increment("requests_processed")
        return result
```

---

## 💡 Best Practices

### 1. Single Responsibility
Each agent should do one thing well.

### 2. Use Dataclasses
Define clear request/response types.

### 3. Handle Errors Gracefully
```python
class RobustAgent(BaseAgent):
    async def execute(self, request):
        try:
            return await self.primary_method(request)
        except PrimaryError:
            return await self.fallback_method(request)
```

### 4. Clean Up Resources
```python
class ResourceAgent(BaseAgent):
    async def initialize(self):
        self.connection = await create_connection()
    
    async def cleanup(self):
        await self.connection.close()
```

---

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 📬 Contact

**Ravi Teja K** - AI/ML Engineer
- GitHub: [@TEJA4704](https://github.com/TEJA4704)
