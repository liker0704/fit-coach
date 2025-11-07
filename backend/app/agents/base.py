"""Base agent class and interfaces for FitCoach agents.

This module provides the foundation for all AI agents in the application,
including common functionality, state management, and agent lifecycle hooks.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from langchain_core.messages import AIMessage
from sqlalchemy.orm import Session

from app.services.llm_service import LLMService

# Setup logger
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all AI agents.

    This class provides common functionality for all FitCoach agents including:
    - LLM integration via LangChain
    - Database session management
    - Memory management interface
    - Cost tracking interface
    - Token counting utilities
    - Error handling patterns

    All specific agent types (Daily Summary, Vision, Nutrition, etc.) should
    inherit from this class and implement the abstract execute() method.

    Attributes:
        db (Session): Database session for agent operations
        user_id (int): User ID this agent is operating for
        agent_type (str): Type of agent (e.g., 'daily_summary', 'nutrition_coach')
        llm: LangChain LLM instance from LLMService
        memory_manager: Agent memory manager instance (if initialized)
        cost_tracker: Cost tracker instance (if initialized)

    Example:
        ```python
        class DailySummaryAgent(BaseAgent):
            async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
                # Get user context from memory
                context = await self.get_memory_context()

                # Process data with LLM
                result = await self._generate_summary(input_data, context)

                # Track usage
                await self.track_llm_usage("gpt-4", 1000, 500)

                # Store important facts
                await self.store_memory("fact", "User prefers morning workouts")

                return {"summary": result}
        ```
    """

    def __init__(
        self,
        db_session: Session,
        user_id: int,
        agent_type: str,
    ):
        """Initialize the base agent.

        Args:
            db_session: SQLAlchemy database session
            user_id: ID of the user this agent is operating for
            agent_type: Type identifier for this agent (e.g., 'daily_summary')

        Raises:
            ValueError: If LLM service configuration is invalid
        """
        self.db = db_session
        self.user_id = user_id
        self.agent_type = agent_type

        # Initialize LLM service
        try:
            self.llm = LLMService.get_llm()
        except ValueError as e:
            logger.error(f"Failed to initialize LLM for agent {agent_type}: {e}")
            raise

        # Initialize memory manager (lazy loading, will be set when first used)
        self.memory_manager: Optional[Any] = None

        # Initialize cost tracker (lazy loading, will be set when first used)
        self.cost_tracker: Optional[Any] = None

        logger.info(
            f"Initialized {agent_type} agent for user {user_id}"
        )

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main task.

        This method must be implemented by all agent subclasses. It defines
        the core functionality of the agent.

        Args:
            input_data: Agent-specific input parameters. Structure depends
                on the specific agent type. Common keys might include:
                - 'date': Date for the operation
                - 'period': Time period for analysis
                - 'context': Additional context information
                - 'user_preferences': User-specific preferences

        Returns:
            Agent-specific output data. Structure depends on the agent type.
            Should typically include:
            - 'success': Boolean indicating success/failure
            - 'result': Main result data
            - 'metadata': Additional information (tokens used, execution time, etc.)
            - 'error': Error message if success=False

        Raises:
            ValueError: If input_data is invalid or missing required fields
            Exception: For agent-specific execution errors

        Example:
            ```python
            async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
                # Validate input
                if 'date' not in input_data:
                    raise ValueError("Missing required field: date")

                # Execute agent logic
                result = await self._process_data(input_data)

                return {
                    'success': True,
                    'result': result,
                    'metadata': {'tokens_used': 1500}
                }
            ```
        """
        pass

    async def get_memory_context(self, limit: Optional[int] = None) -> str:
        """Get formatted memory context for this agent.

        Retrieves relevant memory (preferences, facts, recent actions) for
        this user and agent type, formatted as context for LLM prompts.

        Args:
            limit: Optional limit on number of memory items to retrieve

        Returns:
            Formatted string containing memory context, ready to be included
            in LLM prompts. Returns empty string if memory manager not available.

        Example output:
            ```
            User Preferences:
            - Prefers morning workouts
            - Allergic to peanuts

            Recent Facts:
            - User increased workout intensity last week
            - User has been consistent with water intake

            Recent Actions:
            - Generated meal plan (2025-11-01)
            - Provided workout advice (2025-11-01)
            ```
        """
        if self.memory_manager is None:
            try:
                # Lazy load memory manager
                from app.agents.memory_manager import AgentMemoryManager
                self.memory_manager = AgentMemoryManager(self.db)
            except Exception as e:
                logger.warning(
                    f"Memory manager not available for {self.agent_type}: {e}"
                )
                return ""

        try:
            context = await self.memory_manager.get_context(
                self.user_id, self.agent_type, limit=limit
            )
            return context
        except Exception as e:
            logger.error(
                f"Failed to retrieve memory context for {self.agent_type}: {e}"
            )
            return ""

    async def track_llm_usage(
        self, model: str, tokens_in: int, tokens_out: int
    ) -> None:
        """Track LLM usage for cost monitoring.

        Records token usage and associated costs for this agent's LLM calls.
        This helps monitor spending and optimize agent performance.

        Args:
            model: Model identifier (e.g., 'gpt-4', 'gpt-3.5-turbo', 'gemini-pro')
            tokens_in: Number of input tokens (prompt)
            tokens_out: Number of output tokens (response)

        Note:
            If cost tracker is not available, usage will be logged but not
            persisted to database.

        Example:
            ```python
            # After LLM call
            response = await self.llm.ainvoke(messages)
            await self.track_llm_usage(
                model="gpt-4",
                tokens_in=len(messages) * 100,  # rough estimate
                tokens_out=len(response.content) // 4
            )
            ```
        """
        if self.cost_tracker is None:
            try:
                # Lazy load cost tracker
                from app.agents.cost_tracker import CostTracker
                self.cost_tracker = CostTracker(self.db)
            except Exception as e:
                logger.warning(
                    f"Cost tracker not available for {self.agent_type}: {e}"
                )
                # Still log the usage even if we can't track it
                logger.info(
                    f"LLM usage: {model} - {tokens_in} in, {tokens_out} out"
                )
                return

        try:
            await self.cost_tracker.track_usage(
                user_id=self.user_id,
                agent_type=self.agent_type,
                model=model,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
            )
        except Exception as e:
            logger.error(f"Failed to track LLM usage for {self.agent_type}: {e}")

    async def store_memory(
        self,
        memory_type: str,
        value: str,
        key: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> bool:
        """Store memory based on type.

        Persists different types of memory (preferences, facts, actions) to
        enable personalized agent behavior over time.

        Args:
            memory_type: Type of memory to store. Must be one of:
                - 'preference': User preferences (requires key)
                - 'fact': Learned facts about user
                - 'action': Actions taken by agent (requires metadata['result'])
            value: The memory content/value to store
            key: Key for preference memories (e.g., 'workout_time_preference')
            metadata: Additional metadata as dictionary

        Returns:
            True if memory was stored successfully, False otherwise

        Raises:
            ValueError: If memory_type is invalid or required fields are missing

        Example:
            ```python
            # Store a preference
            await self.store_memory(
                'preference',
                'morning',
                key='workout_time_preference'
            )

            # Store a fact
            await self.store_memory(
                'fact',
                'User consistently hits step goals on weekdays'
            )

            # Store an action
            await self.store_memory(
                'action',
                'generated_meal_plan',
                metadata={'result': 'Created 7-day meal plan for weight loss'}
            )
            ```
        """
        if memory_type not in ['preference', 'fact', 'action']:
            raise ValueError(
                f"Invalid memory_type '{memory_type}'. "
                f"Must be 'preference', 'fact', or 'action'"
            )

        if memory_type == 'preference' and not key:
            raise ValueError("Preference memories require a 'key' parameter")

        if memory_type == 'action' and (not metadata or 'result' not in metadata):
            raise ValueError(
                "Action memories require metadata with 'result' field"
            )

        if self.memory_manager is None:
            try:
                # Lazy load memory manager
                from app.agents.memory_manager import AgentMemoryManager
                self.memory_manager = AgentMemoryManager(self.db)
            except Exception as e:
                logger.warning(
                    f"Memory manager not available for {self.agent_type}: {e}"
                )
                return False

        try:
            if memory_type == "preference":
                await self.memory_manager.store_preference(
                    user_id=self.user_id,
                    agent_type=self.agent_type,
                    key=key,
                    value=value,
                    metadata=metadata,
                )
            elif memory_type == "fact":
                await self.memory_manager.store_fact(
                    user_id=self.user_id,
                    agent_type=self.agent_type,
                    fact=value,
                    metadata=metadata,
                )
            elif memory_type == "action":
                await self.memory_manager.store_action(
                    user_id=self.user_id,
                    agent_type=self.agent_type,
                    action=value,
                    result=metadata.get("result", ""),
                )

            logger.debug(
                f"Stored {memory_type} memory for {self.agent_type}: {value}"
            )
            return True

        except Exception as e:
            logger.error(
                f"Failed to store {memory_type} memory for {self.agent_type}: {e}"
            )
            return False

    def count_tokens(self, text: str) -> int:
        """Estimate token count for text.

        Provides a rough approximation of how many tokens a text string will
        consume. Useful for managing context windows and estimating costs.

        Note:
            This uses a simple heuristic (4 characters ≈ 1 token) which is
            reasonably accurate for English text but may vary for other
            languages or code. For precise counting, consider using tiktoken
            library directly.

        Args:
            text: Text string to count tokens for

        Returns:
            Estimated token count

        Example:
            ```python
            prompt = "Generate a meal plan for weight loss"
            token_count = self.count_tokens(prompt)
            # token_count ≈ 9
            ```
        """
        if not text:
            return 0

        # Simple estimation: ~4 characters per token for English text
        # This is a rough approximation used by OpenAI
        return max(1, len(text) // 4)

    def count_message_tokens(self, messages: list) -> int:
        """Count tokens in a list of LangChain messages.

        Estimates total token count for a conversation/prompt by summing
        tokens in all messages.

        Args:
            messages: List of LangChain message objects (SystemMessage,
                HumanMessage, AIMessage, etc.)

        Returns:
            Estimated total token count for all messages

        Example:
            ```python
            from langchain.schema import SystemMessage, HumanMessage

            messages = [
                SystemMessage(content="You are a fitness coach"),
                HumanMessage(content="Give me workout advice")
            ]
            total_tokens = self.count_message_tokens(messages)
            ```
        """
        total = 0
        for msg in messages:
            # Count content tokens
            if hasattr(msg, 'content'):
                total += self.count_tokens(str(msg.content))
            # Add overhead for message formatting (roughly 4 tokens per message)
            total += 4

        return total

    async def safe_llm_invoke(
        self, messages: list, **kwargs
    ) -> Optional[AIMessage]:
        """Safely invoke LLM with error handling.

        Wrapper around LLM invocation that provides consistent error handling,
        logging, and automatic usage tracking.

        Args:
            messages: List of LangChain messages to send to LLM
            **kwargs: Additional arguments to pass to LLM (temperature, max_tokens, etc.)

        Returns:
            AIMessage response from LLM, or None if invocation failed

        Example:
            ```python
            from langchain.schema import SystemMessage, HumanMessage

            messages = [
                SystemMessage(content="You are a fitness coach"),
                HumanMessage(content="Create a workout plan")
            ]

            response = await self.safe_llm_invoke(messages, temperature=0.7)
            if response:
                print(response.content)
            ```
        """
        try:
            # Count input tokens
            tokens_in = self.count_message_tokens(messages)

            # Invoke LLM
            response = await self.llm.ainvoke(messages, **kwargs)

            # Count output tokens
            tokens_out = self.count_tokens(response.content)

            # Track usage
            model_name = getattr(self.llm, 'model_name', 'unknown')
            await self.track_llm_usage(model_name, tokens_in, tokens_out)

            logger.debug(
                f"{self.agent_type} LLM call: {tokens_in} in, {tokens_out} out"
            )

            return response

        except Exception as e:
            logger.error(
                f"LLM invocation failed for {self.agent_type}: {e}",
                exc_info=True
            )
            return None

    async def cleanup(self) -> None:
        """Cleanup agent resources.

        Called when agent is being destroyed. Override in subclasses if
        additional cleanup is needed (e.g., closing connections, saving state).

        Base implementation handles basic cleanup of managers.
        """
        logger.info(f"Cleaning up {self.agent_type} agent for user {self.user_id}")

        # Reset manager references (they'll be garbage collected)
        self.memory_manager = None
        self.cost_tracker = None

    def __str__(self) -> str:
        """String representation of agent."""
        return f"{self.agent_type.title()}Agent(user_id={self.user_id})"

    def __repr__(self) -> str:
        """Detailed string representation of agent."""
        return (
            f"{self.__class__.__name__}("
            f"user_id={self.user_id}, "
            f"agent_type='{self.agent_type}', "
            f"llm={getattr(self.llm, 'model_name', 'unknown')}"
            f")"
        )
