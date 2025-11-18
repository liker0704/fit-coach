"""Unit tests for Agent Infrastructure.

Tests for:
- memory_manager.py - Agent memory storage and retrieval
- cost_tracker.py - LLM cost tracking and analytics
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from app.agents.memory_manager import AgentMemoryManager
from app.agents.cost_tracker import CostTracker


# ===== Memory Manager Tests =====

def test_store_preference(db_session, test_user):
    """Test storing a user preference."""
    manager = AgentMemoryManager(db_session)

    memory = manager.store_preference(
        user_id=test_user.id,
        agent_type="nutrition",
        key="diet",
        value="vegetarian",
        metadata={"reason": "health"}
    )

    assert memory is not None
    assert memory.user_id == test_user.id
    assert memory.agent_type == "nutrition"
    assert memory.memory_type == "preference"
    assert memory.key == "diet"
    assert memory.value == "vegetarian"
    assert memory.meta_data["reason"] == "health"


def test_store_preference_update_existing(db_session, test_user):
    """Test updating an existing preference."""
    manager = AgentMemoryManager(db_session)

    # Store initial preference
    memory1 = manager.store_preference(
        user_id=test_user.id,
        agent_type="nutrition",
        key="diet",
        value="vegetarian"
    )

    # Update same preference
    memory2 = manager.store_preference(
        user_id=test_user.id,
        agent_type="nutrition",
        key="diet",
        value="vegan",
        metadata={"updated": True}
    )

    # Should be same memory, updated
    assert memory1.id == memory2.id
    assert memory2.value == "vegan"
    assert memory2.meta_data["updated"] is True


def test_store_fact(db_session, test_user):
    """Test storing an important fact."""
    manager = AgentMemoryManager(db_session)

    memory = manager.store_fact(
        user_id=test_user.id,
        agent_type="nutrition",
        fact="Allergic to peanuts",
        metadata={"severity": "high"}
    )

    assert memory is not None
    assert memory.memory_type == "fact"
    assert memory.value == "Allergic to peanuts"
    assert memory.meta_data["severity"] == "high"


def test_store_action(db_session, test_user):
    """Test storing an action and result."""
    manager = AgentMemoryManager(db_session)

    memory = manager.store_action(
        user_id=test_user.id,
        agent_type="nutrition",
        action="Recommended oatmeal breakfast",
        result="User loved it"
    )

    assert memory is not None
    assert memory.memory_type == "action"
    assert memory.value == "Recommended oatmeal breakfast"
    assert memory.meta_data["result"] == "User loved it"


def test_get_context_with_memories(db_session, test_user):
    """Test getting formatted context with memories."""
    manager = AgentMemoryManager(db_session)

    # Store different types of memories
    manager.store_preference(test_user.id, "nutrition", "diet", "vegan")
    manager.store_fact(test_user.id, "nutrition", "Allergic to nuts")
    manager.store_action(test_user.id, "nutrition", "Suggested smoothie", "Enjoyed")

    context = manager.get_context(test_user.id, "nutrition")

    assert "User Preferences:" in context
    assert "diet: vegan" in context
    assert "Important Facts:" in context
    assert "Allergic to nuts" in context
    assert "Action History:" in context
    assert "Suggested smoothie" in context


def test_get_context_empty(db_session, test_user):
    """Test getting context with no memories."""
    manager = AgentMemoryManager(db_session)

    context = manager.get_context(test_user.id, "nutrition")

    assert "No previous context available" in context


def test_get_context_limit(db_session, test_user):
    """Test context retrieval with limit."""
    manager = AgentMemoryManager(db_session)

    # Store many preferences
    for i in range(30):
        manager.store_preference(
            test_user.id,
            "nutrition",
            f"pref_{i}",
            f"value_{i}"
        )

    context = manager.get_context(test_user.id, "nutrition", limit=5)

    # Should only include 5 most recent
    lines = context.split("\n")
    pref_lines = [l for l in lines if "pref_" in l]
    assert len(pref_lines) <= 5


def test_search_memories(db_session, test_user):
    """Test searching memories by keyword."""
    manager = AgentMemoryManager(db_session)

    manager.store_fact(test_user.id, "nutrition", "Allergic to peanuts")
    manager.store_fact(test_user.id, "nutrition", "Prefers morning workouts")
    manager.store_preference(test_user.id, "nutrition", "diet", "vegetarian")

    # Search for "allergy" related memories
    results = manager.search_memories(test_user.id, "allerg")

    assert len(results) >= 1
    assert any("peanut" in m.value.lower() for m in results)


def test_get_memories_all(db_session, test_user):
    """Test getting all memories for a user."""
    manager = AgentMemoryManager(db_session)

    manager.store_preference(test_user.id, "nutrition", "diet", "vegan")
    manager.store_preference(test_user.id, "workout", "type", "strength")
    manager.store_fact(test_user.id, "nutrition", "Lactose intolerant")

    memories = manager.get_memories(test_user.id)

    assert len(memories) == 3


def test_get_memories_filtered_by_agent(db_session, test_user):
    """Test getting memories filtered by agent type."""
    manager = AgentMemoryManager(db_session)

    manager.store_preference(test_user.id, "nutrition", "diet", "vegan")
    manager.store_preference(test_user.id, "workout", "type", "strength")

    nutrition_memories = manager.get_memories(test_user.id, agent_type="nutrition")

    assert len(nutrition_memories) == 1
    assert nutrition_memories[0].agent_type == "nutrition"


def test_get_memories_filtered_by_type(db_session, test_user):
    """Test getting memories filtered by memory type."""
    manager = AgentMemoryManager(db_session)

    manager.store_preference(test_user.id, "nutrition", "diet", "vegan")
    manager.store_fact(test_user.id, "nutrition", "Allergic to eggs")

    facts = manager.get_memories(test_user.id, memory_type="fact")

    assert len(facts) == 1
    assert facts[0].memory_type == "fact"


def test_update_memory(db_session, test_user):
    """Test updating an existing memory."""
    manager = AgentMemoryManager(db_session)

    memory = manager.store_fact(test_user.id, "nutrition", "Allergic to peanuts")

    updated = manager.update_memory(
        memory.id,
        "Allergic to tree nuts",
        metadata={"severity": "moderate"}
    )

    assert updated.id == memory.id
    assert updated.value == "Allergic to tree nuts"
    assert updated.meta_data["severity"] == "moderate"


def test_update_memory_not_found(db_session, test_user):
    """Test updating non-existent memory raises error."""
    manager = AgentMemoryManager(db_session)

    with pytest.raises(ValueError):
        manager.update_memory(99999, "New value")


def test_delete_memory(db_session, test_user):
    """Test deleting a memory."""
    manager = AgentMemoryManager(db_session)

    memory = manager.store_fact(test_user.id, "nutrition", "Test fact")
    memory_id = memory.id

    # Delete
    success = manager.delete_memory(memory_id)
    assert success is True

    # Verify deleted
    memories = manager.get_memories(test_user.id)
    assert not any(m.id == memory_id for m in memories)


def test_delete_memory_not_found(db_session, test_user):
    """Test deleting non-existent memory returns False."""
    manager = AgentMemoryManager(db_session)

    success = manager.delete_memory(99999)
    assert success is False


# ===== Cost Tracker Tests =====

def test_track_usage(db_session, test_user):
    """Test tracking LLM usage."""
    tracker = CostTracker(db_session)

    cost = tracker.track_usage(
        user_id=test_user.id,
        agent_type="nutrition",
        model="gpt-4-turbo",
        tokens_input=500,
        tokens_output=200
    )

    assert cost is not None
    assert cost.user_id == test_user.id
    assert cost.agent_type == "nutrition"
    assert cost.model == "gpt-4-turbo"
    assert cost.tokens_input == 500
    assert cost.tokens_output == 200
    assert cost.cost_usd > 0


def test_calculate_cost_gpt4():
    """Test cost calculation for GPT-4."""
    cost = CostTracker.calculate_cost("gpt-4-turbo", 1000, 500)

    # 1000 input tokens at $0.01/1k + 500 output tokens at $0.03/1k
    expected = (1000/1000 * 0.01) + (500/1000 * 0.03)
    assert cost == pytest.approx(expected, abs=0.000001)


def test_calculate_cost_gpt35():
    """Test cost calculation for GPT-3.5."""
    cost = CostTracker.calculate_cost("gpt-3.5-turbo", 2000, 1000)

    # 2000 input at $0.0005/1k + 1000 output at $0.0015/1k
    expected = (2000/1000 * 0.0005) + (1000/1000 * 0.0015)
    assert cost == pytest.approx(expected, abs=0.000001)


def test_calculate_cost_gemini_free():
    """Test cost calculation for free Gemini model."""
    cost = CostTracker.calculate_cost("gemini-2.0-flash-exp", 5000, 2000)

    # Free tier
    assert cost == 0.0


def test_calculate_cost_unknown_model():
    """Test cost calculation with unknown model raises error."""
    with pytest.raises(ValueError):
        CostTracker.calculate_cost("unknown-model", 1000, 500)


def test_get_user_costs_day(db_session, test_user):
    """Test getting user costs for a day."""
    tracker = CostTracker(db_session)

    # Track some usage
    tracker.track_usage(test_user.id, "nutrition", "gpt-4-turbo", 500, 200)
    tracker.track_usage(test_user.id, "chatbot", "gpt-3.5-turbo", 300, 150)

    stats = tracker.get_user_costs(test_user.id, period="day")

    assert stats["total_cost"] > 0
    assert stats["total_tokens"] == 1150
    assert "nutrition" in stats["by_agent"]
    assert "chatbot" in stats["by_agent"]
    assert stats["usage_count"] == 2


def test_get_user_costs_week(db_session, test_user):
    """Test getting user costs for a week."""
    tracker = CostTracker(db_session)

    tracker.track_usage(test_user.id, "nutrition", "gpt-4-turbo", 1000, 500)

    stats = tracker.get_user_costs(test_user.id, period="week")

    assert stats["total_cost"] > 0
    assert stats["usage_count"] == 1


def test_get_user_costs_all(db_session, test_user):
    """Test getting all-time user costs."""
    tracker = CostTracker(db_session)

    tracker.track_usage(test_user.id, "nutrition", "gpt-4-turbo", 500, 200)
    tracker.track_usage(test_user.id, "workout", "gpt-3.5-turbo", 300, 100)

    stats = tracker.get_user_costs(test_user.id, period="all")

    assert stats["usage_count"] == 2
    assert len(stats["by_agent"]) == 2


def test_get_user_costs_by_model(db_session, test_user):
    """Test cost breakdown by model."""
    tracker = CostTracker(db_session)

    tracker.track_usage(test_user.id, "nutrition", "gpt-4-turbo", 500, 200)
    tracker.track_usage(test_user.id, "nutrition", "gpt-3.5-turbo", 300, 100)

    stats = tracker.get_user_costs(test_user.id, period="all")

    assert "gpt-4-turbo" in stats["by_model"]
    assert "gpt-3.5-turbo" in stats["by_model"]
    assert stats["by_model"]["gpt-4-turbo"] > stats["by_model"]["gpt-3.5-turbo"]


def test_get_total_costs(db_session, test_user, test_user2):
    """Test getting aggregated costs across all users."""
    tracker = CostTracker(db_session)

    # Track usage for multiple users
    tracker.track_usage(test_user.id, "nutrition", "gpt-4-turbo", 500, 200)
    tracker.track_usage(test_user2.id, "chatbot", "gpt-3.5-turbo", 300, 100)

    stats = tracker.get_total_costs(period="all")

    assert stats["total_cost"] > 0
    assert stats["usage_count"] == 2
    assert stats["user_count"] == 2
    assert len(stats["by_agent"]) == 2


def test_get_total_costs_empty(db_session):
    """Test getting total costs with no usage."""
    tracker = CostTracker(db_session)

    stats = tracker.get_total_costs(period="all")

    assert stats["total_cost"] == 0
    assert stats["usage_count"] == 0
    assert stats["user_count"] == 0


def test_period_start_date():
    """Test period start date calculation."""
    tracker = CostTracker(MagicMock())

    now = datetime.now(timezone.utc)

    # Test day
    day_start = tracker._get_period_start_date("day")
    assert day_start < now
    assert (now - day_start).days < 2

    # Test week
    week_start = tracker._get_period_start_date("week")
    assert (now - week_start).days >= 6

    # Test month
    month_start = tracker._get_period_start_date("month")
    assert (now - month_start).days >= 29

    # Test all
    all_start = tracker._get_period_start_date("all")
    assert all_start is None


def test_period_start_date_invalid():
    """Test invalid period raises error."""
    tracker = CostTracker(MagicMock())

    with pytest.raises(ValueError):
        tracker._get_period_start_date("invalid")


# ===== Fixtures =====

@pytest.fixture
def db_session():
    """Create test database session."""
    from app.core.database import SessionLocal, Base, engine

    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """Create test user."""
    from app.models.user import User

    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed",
        name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture
def test_user2(db_session):
    """Create second test user."""
    from app.models.user import User

    user = User(
        email="test2@example.com",
        username="testuser2",
        hashed_password="hashed",
        name="Test User 2"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


if __name__ == "__main__":
    """Run tests manually."""
    print("Running Agent Infrastructure Tests...")
    print("=" * 60)

    print("Use 'pytest tests/test_agent_infrastructure.py -v' to run these tests")
    print("=" * 60)
