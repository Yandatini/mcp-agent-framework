"""
MCP Protocol - Core Request/Response Schemas

Defines the Model Context Protocol message formats, types, and validation.
This implements the MCP standard for agent-to-agent and agent-to-model communication.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)


class MCPMessageType(Enum):
    """MCP message types for different communication patterns."""

    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    CONTEXT_SHARE = "context_share"
    HEALTH_CHECK = "health_check"


class MCPPriority(Enum):
    """Request priority levels for queue management."""

    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class ModelType(Enum):
    """
    Available model types.
    
    Override these with your own model identifiers.
    """

    GPT4 = "gpt-4"
    GPT35_TURBO = "gpt-3.5-turbo"
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    GEMINI_PRO = "gemini-pro"
    EMBEDDING = "text-embedding-3-small"


class TaskType(Enum):
    """Task types for intelligent routing."""

    CREATIVE = "creative"  # Content creation, query generation
    REASONING = "reasoning"  # Complex analysis, logic
    CLASSIFICATION = "classification"  # Categorization
    EXTRACTION = "extraction"  # Entity/data extraction
    SUMMARIZATION = "summarization"  # Text summarization
    EMBEDDING = "embedding"  # Vector generation
    GENERAL = "general"  # Default


@dataclass
class MCPContext:
    """
    Context shared between models and agents.

    This is the core of MCP - enabling models to share information
    and maintain coherent multi-step reasoning across agent boundaries.
    
    Example:
        context = MCPContext()
        context.add_message("user", "What is the capital of France?")
        context.set_memory("country", "France")
    """

    conversation_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: Optional[str] = None
    history: List[Dict[str, Any]] = field(default_factory=list)
    shared_memory: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: str, content: str, model: Optional[str] = None) -> None:
        """Add a message to conversation history."""
        self.history.append(
            {
                "role": role,
                "content": content,
                "model": model,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def get_history(self, last_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conversation history (optionally last N messages)."""
        if last_n:
            return self.history[-last_n:]
        return self.history

    def set_memory(self, key: str, value: Any) -> None:
        """Store data in shared memory (accessible by all agents)."""
        self.shared_memory[key] = value
        logger.debug(f"Set shared memory: {key}")

    def get_memory(self, key: str, default: Any = None) -> Any:
        """Retrieve data from shared memory."""
        return self.shared_memory.get(key, default)

    def clear_memory(self) -> None:
        """Clear shared memory."""
        self.shared_memory.clear()
        logger.debug(f"Cleared shared memory: {self.conversation_id}")


@dataclass
class MCPRequest:
    """
    MCP Request schema.

    Represents a request to be processed by the MCP system.
    
    Example:
        request = MCPRequest(
            content="Summarize this document",
            task_type=TaskType.SUMMARIZATION,
            priority=MCPPriority.HIGH
        )
    """

    # Core fields
    request_id: str = field(default_factory=lambda: str(uuid4()))
    content: str = ""
    task_type: TaskType = TaskType.GENERAL
    model: Optional[ModelType] = None  # If None, router will select automatically

    # Priority and routing
    priority: MCPPriority = MCPPriority.NORMAL
    require_reasoning: bool = False
    require_creativity: bool = False
    max_tokens: Optional[int] = None
    temperature: float = 0.7

    # Context
    context: Optional[MCPContext] = None
    use_context: bool = True

    # Caching
    cache_enabled: bool = True
    cache_ttl: int = 3600  # seconds

    # Metadata
    agent_name: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate and initialize request."""
        if not self.content and self.task_type != TaskType.EMBEDDING:
            logger.warning(f"Empty request content: {self.request_id}")

        if self.context is None and self.use_context:
            self.context = MCPContext()

        logger.info(f"MCP request created: {self.request_id}, task={self.task_type.value}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary."""
        return {
            "request_id": self.request_id,
            "content": self.content,
            "task_type": self.task_type.value,
            "model": self.model.value if self.model else None,
            "priority": self.priority.value,
            "require_reasoning": self.require_reasoning,
            "require_creativity": self.require_creativity,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl,
            "agent_name": self.agent_name,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class MCPResponse:
    """
    MCP Response schema.

    Represents the response from the MCP system.
    """

    # Core fields
    request_id: str
    content: str
    model_used: ModelType
    success: bool = True

    # Performance metrics
    latency_ms: float = 0.0
    tokens_used: int = 0
    cached: bool = False

    # Context
    context: Optional[MCPContext] = None

    # Error handling
    error: Optional[str] = None
    fallback_used: bool = False
    fallback_model: Optional[ModelType] = None

    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate response."""
        if not self.success and not self.error:
            logger.warning(f"Failed response without error: {self.request_id}")

        logger.info(
            f"MCP response: {self.request_id}, model={self.model_used.value}, "
            f"success={self.success}, latency={self.latency_ms}ms"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "request_id": self.request_id,
            "content": self.content,
            "model_used": self.model_used.value,
            "success": self.success,
            "latency_ms": self.latency_ms,
            "tokens_used": self.tokens_used,
            "cached": self.cached,
            "error": self.error,
            "fallback_used": self.fallback_used,
            "fallback_model": self.fallback_model.value if self.fallback_model else None,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class MCPMessage:
    """
    Generic MCP message wrapper.

    Used for internal communication between MCP components.
    """

    message_id: str = field(default_factory=lambda: str(uuid4()))
    message_type: MCPMessageType = MCPMessageType.REQUEST
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None
    destination: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "destination": self.destination,
        }


class MCPProtocolValidator:
    """Validates MCP protocol messages."""

    @staticmethod
    def validate_request(request: MCPRequest) -> tuple:
        """
        Validate MCP request.

        Returns:
            (is_valid, error_message)
        """
        if not request.content and request.task_type != TaskType.EMBEDDING:
            return False, "Request content cannot be empty"

        if request.max_tokens and request.max_tokens <= 0:
            return False, "max_tokens must be positive"

        if not 0 <= request.temperature <= 2.0:
            return False, "temperature must be between 0 and 2.0"

        if request.cache_ttl < 0:
            return False, "cache_ttl cannot be negative"

        return True, None

    @staticmethod
    def validate_response(response: MCPResponse) -> tuple:
        """
        Validate MCP response.

        Returns:
            (is_valid, error_message)
        """
        if not response.success and not response.error:
            return False, "Failed response must include error message"

        if response.latency_ms < 0:
            return False, "latency_ms cannot be negative"

        if response.tokens_used < 0:
            return False, "tokens_used cannot be negative"

        return True, None


# Convenience functions
def create_request(
    content: str,
    task_type: TaskType = TaskType.GENERAL,
    model: Optional[ModelType] = None,
    **kwargs,
) -> MCPRequest:
    """Create a validated MCP request."""
    request = MCPRequest(content=content, task_type=task_type, model=model, **kwargs)

    is_valid, error = MCPProtocolValidator.validate_request(request)
    if not is_valid:
        logger.error(f"Invalid MCP request: {error}")
        raise ValueError(f"Invalid MCP request: {error}")

    return request


def create_response(
    request_id: str,
    content: str,
    model_used: ModelType,
    **kwargs,
) -> MCPResponse:
    """Create a validated MCP response."""
    response = MCPResponse(
        request_id=request_id, content=content, model_used=model_used, **kwargs
    )

    is_valid, error = MCPProtocolValidator.validate_response(response)
    if not is_valid:
        logger.error(f"Invalid MCP response: {error}")
        raise ValueError(f"Invalid MCP response: {error}")

    return response
