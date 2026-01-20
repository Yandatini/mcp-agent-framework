"""
Base Agent - Abstract Base Class for MCP Agents

Provides the foundation for creating agents that participate in the MCP ecosystem.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional, Protocol
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)


class LLMClient(Protocol):
    """Protocol for LLM clients."""
    async def generate(self, prompt: str, **kwargs) -> str:
        ...


@dataclass
class AgentRequest:
    """
    Base class for agent requests.
    
    Extend this for your specific agent input types.
    """
    request_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class AgentResponse:
    """
    Base class for agent responses.
    
    Extend this for your specific agent output types.
    """
    request_id: str = ""
    success: bool = True
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Abstract base class for MCP agents.
    
    All agents in the MCP system should inherit from this class.
    
    Example:
        class MyAgent(BaseAgent):
            async def execute(self, request: MyRequest) -> MyResponse:
                # Your agent logic
                return MyResponse(success=True)
    """

    def __init__(
        self,
        name: str = "unnamed_agent",
        llm_client: Optional[LLMClient] = None,
        **kwargs
    ):
        """
        Initialize the agent.
        
        Args:
            name: Human-readable agent name
            llm_client: LLM client for generation
            **kwargs: Additional configuration
        """
        self.name = name
        self.llm_client = llm_client
        self.config = kwargs
        self._initialized = False
        
        logger.info(f"Agent created: {self.name}")

    async def initialize(self) -> None:
        """
        Initialize agent resources.
        
        Override this to set up connections, load models, etc.
        """
        self._initialized = True
        logger.debug(f"Agent initialized: {self.name}")

    async def cleanup(self) -> None:
        """
        Clean up agent resources.
        
        Override this to close connections, free resources, etc.
        """
        self._initialized = False
        logger.debug(f"Agent cleaned up: {self.name}")

    @abstractmethod
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute the agent's main logic.
        
        Args:
            request: Agent-specific request
            
        Returns:
            Agent-specific response
        """
        pass

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
        return False

    def validate_request(self, request: AgentRequest) -> tuple:
        """
        Validate an incoming request.
        
        Override for custom validation logic.
        
        Returns:
            (is_valid, error_message)
        """
        if not request.request_id:
            return False, "Request ID is required"
        return True, None

    async def _call_llm(self, prompt: str, **kwargs) -> str:
        """
        Call the configured LLM.
        
        Args:
            prompt: The prompt to send
            **kwargs: Additional arguments for the LLM
            
        Returns:
            LLM response
        """
        if not self.llm_client:
            raise ValueError("No LLM client configured")
        
        response = await self.llm_client.generate(prompt, **kwargs)
        return response if isinstance(response, str) else str(response)

    def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        return {
            "name": self.name,
            "initialized": self._initialized,
            "has_llm": self.llm_client is not None,
        }
