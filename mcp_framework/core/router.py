"""
MCP Router - Intelligent Model Selection and Request Routing

Routes requests to the optimal model based on task type, requirements, and load.
"""

from typing import Optional, Dict
import logging

from .protocol import (
    MCPRequest,
    ModelType,
    TaskType,
)

logger = logging.getLogger(__name__)


class MCPRouter:
    """
    Intelligent router for MCP requests.
    
    Selects the best model for each task based on:
    - Task type (creative, reasoning, classification, etc.)
    - Request requirements (creativity, reasoning depth)
    - Model capabilities and performance
    - Current load and availability
    
    Example:
        router = MCPRouter()
        model = router.select_model(request)
    """

    # Model capability matrix - customize for your models
    MODEL_CAPABILITIES = {
        ModelType.GPT4: {
            "tasks": [TaskType.CREATIVE, TaskType.REASONING, TaskType.SUMMARIZATION, TaskType.GENERAL],
            "creativity": 0.9,
            "reasoning": 0.95,
            "speed": 0.5,
            "context_window": 128000,
        },
        ModelType.GPT35_TURBO: {
            "tasks": [TaskType.CLASSIFICATION, TaskType.EXTRACTION, TaskType.GENERAL],
            "creativity": 0.7,
            "reasoning": 0.7,
            "speed": 0.9,
            "context_window": 16384,
        },
        ModelType.CLAUDE_3_OPUS: {
            "tasks": [TaskType.REASONING, TaskType.CREATIVE, TaskType.SUMMARIZATION],
            "creativity": 0.95,
            "reasoning": 0.95,
            "speed": 0.4,
            "context_window": 200000,
        },
        ModelType.CLAUDE_3_SONNET: {
            "tasks": [TaskType.CLASSIFICATION, TaskType.EXTRACTION, TaskType.REASONING],
            "creativity": 0.8,
            "reasoning": 0.85,
            "speed": 0.8,
            "context_window": 200000,
        },
        ModelType.GEMINI_PRO: {
            "tasks": [TaskType.CREATIVE, TaskType.REASONING, TaskType.GENERAL],
            "creativity": 0.85,
            "reasoning": 0.85,
            "speed": 0.7,
            "context_window": 1000000,
        },
        ModelType.EMBEDDING: {
            "tasks": [TaskType.EMBEDDING],
            "creativity": 0.0,
            "reasoning": 0.0,
            "speed": 1.0,
            "context_window": 8191,
        },
    }

    def __init__(self):
        """Initialize MCP Router."""
        self.model_health = {model: True for model in ModelType}
        logger.info(f"MCP Router initialized with {len(self.model_health)} models")

    def select_model(self, request: MCPRequest) -> ModelType:
        """
        Select the optimal model for a request.
        
        Args:
            request: MCP request to route
            
        Returns:
            Selected ModelType
        """
        # If model explicitly specified, use it (if healthy)
        if request.model:
            if self.is_model_healthy(request.model):
                logger.debug(f"Using specified model: {request.model.value}")
                return request.model
            else:
                logger.warning(f"Specified model unhealthy: {request.model.value}")

        # Embedding task - always use embedding model
        if request.task_type == TaskType.EMBEDDING:
            return ModelType.EMBEDDING

        # Select based on requirements and task type
        selected_model = self._intelligent_selection(request)

        logger.info(
            f"Router selected: {selected_model.value} for task={request.task_type.value}"
        )

        return selected_model

    def _intelligent_selection(self, request: MCPRequest) -> ModelType:
        """
        Intelligent model selection based on request characteristics.
        
        Selection logic:
        1. High creativity requirement → GPT-4 or Claude Opus
        2. Complex reasoning → GPT-4 or Claude Opus
        3. Fast classification/extraction → GPT-3.5 or Claude Sonnet
        4. General → GPT-3.5 (fast and capable)
        """
        # High creativity requirement
        if request.require_creativity:
            return ModelType.GPT4

        # Complex reasoning requirement
        if request.require_reasoning:
            return ModelType.CLAUDE_3_OPUS

        # Task-based selection
        task_type = request.task_type

        if task_type == TaskType.CREATIVE:
            return ModelType.GPT4

        elif task_type == TaskType.REASONING:
            return ModelType.CLAUDE_3_OPUS

        elif task_type == TaskType.CLASSIFICATION:
            return ModelType.GPT35_TURBO

        elif task_type == TaskType.EXTRACTION:
            # Use faster model for simple extraction
            if len(request.content) > 2000:  # Long content = complex
                return ModelType.CLAUDE_3_SONNET
            return ModelType.GPT35_TURBO

        elif task_type == TaskType.SUMMARIZATION:
            return ModelType.GEMINI_PRO

        else:  # GENERAL or unknown
            return ModelType.GPT35_TURBO

    def get_fallback_model(self, primary_model: ModelType) -> Optional[ModelType]:
        """
        Get fallback model if primary fails.
        
        Args:
            primary_model: The model that failed
            
        Returns:
            Fallback ModelType or None
        """
        fallback_map = {
            ModelType.GPT4: ModelType.CLAUDE_3_OPUS,
            ModelType.GPT35_TURBO: ModelType.CLAUDE_3_SONNET,
            ModelType.CLAUDE_3_OPUS: ModelType.GPT4,
            ModelType.CLAUDE_3_SONNET: ModelType.GPT35_TURBO,
            ModelType.GEMINI_PRO: ModelType.GPT4,
            ModelType.EMBEDDING: None,  # No fallback for embeddings
        }

        fallback = fallback_map.get(primary_model)

        if fallback and self.is_model_healthy(fallback):
            logger.info(f"Fallback: {primary_model.value} -> {fallback.value}")
            return fallback
        elif fallback:
            logger.error(f"Fallback {fallback.value} also unhealthy")

        return None

    def is_model_healthy(self, model: ModelType) -> bool:
        """Check if a model is healthy and available."""
        return self.model_health.get(model, False)

    def mark_model_unhealthy(self, model: ModelType) -> None:
        """Mark a model as unhealthy."""
        self.model_health[model] = False
        logger.warning(f"Model marked unhealthy: {model.value}")

    def mark_model_healthy(self, model: ModelType) -> None:
        """Mark a model as healthy."""
        self.model_health[model] = True
        logger.info(f"Model marked healthy: {model.value}")

    def get_model_stats(self) -> Dict:
        """Get router statistics."""
        healthy_count = sum(1 for h in self.model_health.values() if h)
        return {
            "total_models": len(self.model_health),
            "healthy_models": healthy_count,
            "unhealthy_models": len(self.model_health) - healthy_count,
            "model_status": {
                model.value: "healthy" if healthy else "unhealthy"
                for model, healthy in self.model_health.items()
            },
        }

    def validate_routing_decision(
        self, request: MCPRequest, selected_model: ModelType
    ) -> tuple:
        """
        Validate that the routing decision is appropriate.
        
        Args:
            request: The original request
            selected_model: The model selected by router
            
        Returns:
            (is_valid, reason)
        """
        # Check model health
        if not self.is_model_healthy(selected_model):
            return False, f"Selected model {selected_model.value} is unhealthy"

        # Check task compatibility
        capabilities = self.MODEL_CAPABILITIES.get(selected_model)
        if not capabilities:
            return False, f"Unknown model {selected_model.value}"

        if request.task_type not in capabilities["tasks"]:
            logger.warning(f"Model {selected_model.value} may not be optimal for {request.task_type.value}")

        # Check context window
        if request.max_tokens and request.max_tokens > capabilities["context_window"]:
            return (
                False,
                f"Request max_tokens ({request.max_tokens}) exceeds context window ({capabilities['context_window']})",
            )

        return True, None


# Singleton instance
_router_instance: Optional[MCPRouter] = None


def get_router() -> MCPRouter:
    """Get the global MCP router instance."""
    global _router_instance
    if _router_instance is None:
        _router_instance = MCPRouter()
    return _router_instance
