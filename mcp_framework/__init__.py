"""
MCP Agent Framework

Enterprise-grade agent orchestration implementing Model Context Protocol (MCP).
"""

from .core.protocol import MCPRequest, MCPResponse, MCPContext
from .core.router import MCPRouter
from .core.base_agent import BaseAgent, AgentRequest, AgentResponse

__version__ = "1.0.0"
__all__ = [
    "MCPRequest",
    "MCPResponse",
    "MCPContext",
    "MCPRouter",
    "BaseAgent",
    "AgentRequest",
    "AgentResponse",
]
