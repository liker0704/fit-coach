"""Agent memory management for conversation history and context.

This module handles persistent storage and retrieval of agent memories,
including user preferences, important facts, and action history for
personalized interactions.
"""

from typing import List, Optional

from sqlalchemy import and_, desc, or_
from sqlalchemy.orm import Session

from app.models.agent_memory import AgentMemory


class AgentMemoryManager:
    """Manages agent memory storage and retrieval.

    This class provides methods to store and retrieve different types of memories:
    - Preferences: User settings like dietary restrictions, exercise preferences
    - Facts: Important information like allergies, injuries, medical conditions
    - Actions: History of recommendations and their outcomes

    Example:
        >>> memory_manager = AgentMemoryManager(db_session)
        >>> memory_manager.store_preference(
        ...     user_id=1,
        ...     agent_type="nutrition",
        ...     key="diet",
        ...     value="vegetarian"
        ... )
    """

    def __init__(self, db_session: Session):
        """Initialize the memory manager.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    def store_preference(
        self,
        user_id: int,
        agent_type: str,
        key: str,
        value: str,
        metadata: Optional[dict] = None,
    ) -> AgentMemory:
        """Store a user preference.

        Preferences are key-value pairs representing user settings or choices,
        such as dietary restrictions, favorite exercises, or communication style.
        If a preference with the same key already exists, it will be updated.

        Args:
            user_id: ID of the user
            agent_type: Type of agent (e.g., "nutrition", "fitness", "wellness")
            key: Preference key (e.g., "diet", "favorite_exercise")
            value: Preference value (e.g., "vegetarian", "running")
            metadata: Optional additional context (e.g., {"reason": "health", "since": "2024-01-01"})

        Returns:
            The created or updated AgentMemory object

        Example:
            >>> memory = manager.store_preference(
            ...     user_id=1,
            ...     agent_type="nutrition",
            ...     key="diet",
            ...     value="vegetarian",
            ...     metadata={"reason": "ethical"}
            ... )
        """
        # Check if preference already exists
        existing = (
            self.db.query(AgentMemory)
            .filter(
                and_(
                    AgentMemory.user_id == user_id,
                    AgentMemory.agent_type == agent_type,
                    AgentMemory.memory_type == "preference",
                    AgentMemory.key == key,
                )
            )
            .first()
        )

        if existing:
            # Update existing preference
            existing.value = value
            if metadata:
                existing.meta_data = metadata
            self.db.commit()
            self.db.refresh(existing)
            return existing

        # Create new preference
        memory = AgentMemory(
            user_id=user_id,
            agent_type=agent_type,
            memory_type="preference",
            key=key,
            value=value,
            meta_data=metadata,
        )
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        return memory

    def store_fact(
        self,
        user_id: int,
        agent_type: str,
        fact: str,
        metadata: Optional[dict] = None,
    ) -> AgentMemory:
        """Store an important fact.

        Facts are pieces of information that should be remembered across sessions,
        such as allergies, injuries, medical conditions, or important life events.

        Args:
            user_id: ID of the user
            agent_type: Type of agent (e.g., "nutrition", "fitness", "wellness")
            fact: The fact to store (e.g., "Allergic to peanuts")
            metadata: Optional additional context (e.g., {"severity": "high", "diagnosed": "2023-06"})

        Returns:
            The created AgentMemory object

        Example:
            >>> memory = manager.store_fact(
            ...     user_id=1,
            ...     agent_type="nutrition",
            ...     fact="Allergic to peanuts",
            ...     metadata={"severity": "high"}
            ... )
        """
        memory = AgentMemory(
            user_id=user_id,
            agent_type=agent_type,
            memory_type="fact",
            key=None,
            value=fact,
            meta_data=metadata,
        )
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        return memory

    def store_action(
        self, user_id: int, agent_type: str, action: str, result: str
    ) -> AgentMemory:
        """Store an action and its result.

        Actions represent recommendations made by the agent and the user's
        response or outcome, helping the agent learn from past interactions.

        Args:
            user_id: ID of the user
            agent_type: Type of agent (e.g., "nutrition", "fitness", "wellness")
            action: The action or recommendation made (e.g., "Recommended oatmeal breakfast")
            result: The outcome or user feedback (e.g., "User loved it")

        Returns:
            The created AgentMemory object

        Example:
            >>> memory = manager.store_action(
            ...     user_id=1,
            ...     agent_type="nutrition",
            ...     action="Recommended oatmeal breakfast",
            ...     result="User loved it"
            ... )
        """
        memory = AgentMemory(
            user_id=user_id,
            agent_type=agent_type,
            memory_type="action",
            key=None,
            value=action,
            meta_data={"result": result},
        )
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        return memory

    def get_context(
        self, user_id: int, agent_type: str, limit: int = 20
    ) -> str:
        """Get formatted memory context for prompts.

        This method retrieves and formats memories into a human-readable string
        that can be included in agent prompts to provide personalized context.

        Args:
            user_id: ID of the user
            agent_type: Type of agent to get memories for
            limit: Maximum number of memories to retrieve (default: 20)

        Returns:
            Formatted string containing preferences, facts, and action history

        Example output:
            User Preferences:
            - diet: vegetarian
            - favorite_exercise: running

            Important Facts:
            - Allergic to peanuts (severity: high)
            - Previous knee injury

            Action History:
            - Recommended oatmeal breakfast → User loved it
            - Suggested morning run → User completed it
        """
        memories = (
            self.db.query(AgentMemory)
            .filter(
                and_(
                    AgentMemory.user_id == user_id,
                    AgentMemory.agent_type == agent_type,
                )
            )
            .order_by(desc(AgentMemory.created_at))
            .limit(limit)
            .all()
        )

        if not memories:
            return "No previous context available for this user."

        # Group memories by type
        preferences = []
        facts = []
        actions = []

        for memory in reversed(memories):  # Show oldest first for context
            if memory.memory_type == "preference":
                metadata_str = ""
                if memory.meta_data:
                    metadata_items = [f"{k}: {v}" for k, v in memory.meta_data.items()]
                    metadata_str = f" ({', '.join(metadata_items)})"
                preferences.append(f"- {memory.key}: {memory.value}{metadata_str}")

            elif memory.memory_type == "fact":
                metadata_str = ""
                if memory.meta_data:
                    metadata_items = [f"{k}: {v}" for k, v in memory.meta_data.items()]
                    metadata_str = f" ({', '.join(metadata_items)})"
                facts.append(f"- {memory.value}{metadata_str}")

            elif memory.memory_type == "action":
                result = memory.meta_data.get("result", "Unknown outcome") if memory.meta_data else "Unknown outcome"
                actions.append(f"- {memory.value} → {result}")

        # Build formatted context
        context_parts = []

        if preferences:
            context_parts.append("User Preferences:")
            context_parts.extend(preferences)
            context_parts.append("")

        if facts:
            context_parts.append("Important Facts:")
            context_parts.extend(facts)
            context_parts.append("")

        if actions:
            context_parts.append("Action History:")
            context_parts.extend(actions[:10])  # Limit actions to last 10
            context_parts.append("")

        return "\n".join(context_parts).strip()

    def search_memories(
        self, user_id: int, query: str, limit: int = 5
    ) -> List[AgentMemory]:
        """Simple keyword search in memory values.

        Searches through memory values for matches to the query string.
        This is a basic text search using SQL LIKE.

        Args:
            user_id: ID of the user
            query: Search query string
            limit: Maximum number of results (default: 5)

        Returns:
            List of matching AgentMemory objects

        Example:
            >>> memories = manager.search_memories(
            ...     user_id=1,
            ...     query="allergy"
            ... )
        """
        search_pattern = f"%{query}%"
        memories = (
            self.db.query(AgentMemory)
            .filter(
                and_(
                    AgentMemory.user_id == user_id,
                    or_(
                        AgentMemory.value.ilike(search_pattern),
                        AgentMemory.key.ilike(search_pattern),
                    ),
                )
            )
            .order_by(desc(AgentMemory.created_at))
            .limit(limit)
            .all()
        )
        return memories

    def get_memories(
        self,
        user_id: int,
        agent_type: Optional[str] = None,
        memory_type: Optional[str] = None,
    ) -> List[AgentMemory]:
        """Get memories with optional filters.

        Retrieve memories for a user, optionally filtering by agent type
        and/or memory type.

        Args:
            user_id: ID of the user
            agent_type: Optional agent type filter (e.g., "nutrition", "fitness")
            memory_type: Optional memory type filter (e.g., "preference", "fact", "action")

        Returns:
            List of matching AgentMemory objects, ordered by most recent first

        Example:
            >>> # Get all memories
            >>> all_memories = manager.get_memories(user_id=1)
            >>>
            >>> # Get nutrition preferences only
            >>> nutrition_prefs = manager.get_memories(
            ...     user_id=1,
            ...     agent_type="nutrition",
            ...     memory_type="preference"
            ... )
        """
        query = self.db.query(AgentMemory).filter(AgentMemory.user_id == user_id)

        if agent_type:
            query = query.filter(AgentMemory.agent_type == agent_type)

        if memory_type:
            query = query.filter(AgentMemory.memory_type == memory_type)

        return query.order_by(desc(AgentMemory.created_at)).all()

    def update_memory(
        self, memory_id: int, value: str, metadata: Optional[dict] = None
    ) -> AgentMemory:
        """Update existing memory.

        Updates the value and optionally the metadata of an existing memory.

        Args:
            memory_id: ID of the memory to update
            value: New value for the memory
            metadata: Optional new metadata (will replace existing metadata if provided)

        Returns:
            The updated AgentMemory object

        Raises:
            ValueError: If memory with given ID is not found

        Example:
            >>> memory = manager.update_memory(
            ...     memory_id=123,
            ...     value="vegan",
            ...     metadata={"since": "2024-02-01"}
            ... )
        """
        memory = self.db.query(AgentMemory).filter(AgentMemory.id == memory_id).first()

        if not memory:
            raise ValueError(f"Memory with id {memory_id} not found")

        memory.value = value
        if metadata is not None:
            memory.meta_data = metadata

        self.db.commit()
        self.db.refresh(memory)
        return memory

    def delete_memory(self, memory_id: int) -> bool:
        """Delete a memory.

        Permanently removes a memory from the database.

        Args:
            memory_id: ID of the memory to delete

        Returns:
            True if memory was deleted, False if memory was not found

        Example:
            >>> success = manager.delete_memory(memory_id=123)
            >>> if success:
            ...     print("Memory deleted")
        """
        memory = self.db.query(AgentMemory).filter(AgentMemory.id == memory_id).first()

        if not memory:
            return False

        self.db.delete(memory)
        self.db.commit()
        return True
