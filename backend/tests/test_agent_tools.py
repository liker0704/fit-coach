"""Unit tests for Agent Tools.

Tests for agent tool modules:
- health_tools.py - User health data access
- vision_tools.py - Food photo analysis (GPT-4 Vision / Gemini Vision)
- search_tools.py - Tavily search for nutrition info
"""

import asyncio
import json
import pytest
from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, mock_open, patch
from io import BytesIO

from PIL import Image

# Import tools to test
from app.agents.tools import health_tools, vision_tools, search_tools


# ===== Health Tools Tests =====

def test_get_day_data_with_data(db_session, test_user):
    """Test getting day data when data exists."""
    from app.models.day import Day
    from app.models.meal import Meal
    from app.models.exercise import Exercise

    # Create test day with data
    test_date = date(2025, 1, 15)
    day = Day(user_id=test_user.id, date=test_date)
    db_session.add(day)
    db_session.commit()

    # Add meal
    meal = Meal(
        day_id=day.id,
        category="lunch",
        calories=500.0,
        protein=30.0,
        carbs=50.0,
        fat=15.0
    )
    db_session.add(meal)

    # Add exercise
    exercise = Exercise(
        day_id=day.id,
        name="Running",
        type="cardio",
        duration_minutes=30,
        calories_burned=300.0
    )
    db_session.add(exercise)
    db_session.commit()

    # Get day data
    result = health_tools.get_day_data(db_session, test_user.id, test_date)

    assert result["has_data"] is True
    assert result["date"] == str(test_date)
    assert result["nutrition"]["calories"] == 500.0
    assert result["nutrition"]["protein"] == 30.0
    assert len(result["meals"]) == 1
    assert len(result["exercises"]) == 1


def test_get_day_data_no_data(db_session, test_user):
    """Test getting day data when no data exists."""
    test_date = date(2025, 1, 15)

    result = health_tools.get_day_data(db_session, test_user.id, test_date)

    assert result["has_data"] is False
    assert "No data logged" in result["message"]


def test_get_user_profile(db_session, test_user):
    """Test getting user profile."""
    result = health_tools.get_user_profile(db_session, test_user.id)

    assert "name" in result
    assert "email" in result
    assert result["email"] == test_user.email


def test_get_user_goals_exists(db_session, test_user):
    """Test getting user goals when they exist."""
    from app.models.goal import Goal

    goal = Goal(
        user_id=test_user.id,
        daily_calories=2000.0,
        daily_protein=150.0,
        daily_carbs=200.0,
        daily_fat=60.0,
        weekly_workout_goal=4
    )
    db_session.add(goal)
    db_session.commit()

    result = health_tools.get_user_goals(db_session, test_user.id)

    assert result["has_goals"] is True
    assert result["daily_calories"] == 2000.0
    assert result["daily_protein"] == 150.0


def test_get_user_goals_not_exists(db_session, test_user):
    """Test getting user goals when they don't exist."""
    result = health_tools.get_user_goals(db_session, test_user.id)

    assert result["has_goals"] is False
    assert "No goals set" in result["message"]


def test_calculate_progress_success(db_session, test_user):
    """Test calculating progress with valid data."""
    from app.models.day import Day
    from app.models.meal import Meal
    from app.models.goal import Goal

    # Create goal
    goal = Goal(
        user_id=test_user.id,
        daily_calories=2000.0,
        daily_protein=150.0,
        daily_water_ml=2000.0
    )
    db_session.add(goal)

    # Create day with meal
    test_date = date.today()
    day = Day(user_id=test_user.id, date=test_date, water_ml=1500)
    db_session.add(day)
    db_session.commit()

    meal = Meal(
        day_id=day.id,
        category="lunch",
        calories=1000.0,
        protein=75.0
    )
    db_session.add(meal)
    db_session.commit()

    result = health_tools.calculate_progress(db_session, test_user.id, test_date)

    assert result["has_progress"] is True
    assert result["calories"]["actual"] == 1000.0
    assert result["calories"]["target"] == 2000.0
    assert result["calories"]["percentage"] == 50.0
    assert result["protein"]["percentage"] == 50.0


def test_calculate_progress_no_data(db_session, test_user):
    """Test calculating progress with no data."""
    result = health_tools.calculate_progress(db_session, test_user.id)

    assert result["has_progress"] is False


# ===== Vision Tools Tests =====

@pytest.mark.asyncio
async def test_prepare_image_success():
    """Test successful image preparation."""
    # Create a test image
    img = Image.new('RGB', (100, 100), color='red')
    test_path = "/tmp/test_image.jpg"
    img.save(test_path)

    try:
        result = vision_tools.prepare_image(test_path)

        # Should return base64 string
        assert isinstance(result, str)
        assert len(result) > 0
    finally:
        # Cleanup
        Path(test_path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_prepare_image_resize():
    """Test image resizing for large images."""
    # Create large test image
    img = Image.new('RGB', (3000, 3000), color='blue')
    test_path = "/tmp/test_large_image.jpg"
    img.save(test_path)

    try:
        result = vision_tools.prepare_image(test_path, max_size=(2048, 2048))

        # Should succeed and resize
        assert isinstance(result, str)
        assert len(result) > 0
    finally:
        Path(test_path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_prepare_image_not_found():
    """Test prepare_image with non-existent file."""
    with pytest.raises(FileNotFoundError):
        vision_tools.prepare_image("/nonexistent/image.jpg")


@pytest.mark.asyncio
async def test_analyze_food_photo_gemini_success():
    """Test successful food photo analysis with Gemini."""
    # Create test image
    img = Image.new('RGB', (100, 100), color='green')
    test_path = "/tmp/test_food.jpg"
    img.save(test_path)

    try:
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.text = json.dumps([
            {
                "name": "grilled chicken",
                "quantity": "150",
                "unit": "grams",
                "preparation": "grilled",
                "confidence": "high"
            }
        ])

        with patch('app.agents.tools.vision_tools.settings.GOOGLE_API_KEY', 'test-key'):
            with patch('google.generativeai.GenerativeModel') as mock_model:
                mock_instance = MagicMock()
                mock_instance.generate_content_async = AsyncMock(return_value=mock_response)
                mock_model.return_value = mock_instance

                result = await vision_tools.analyze_food_photo_gemini(test_path)

                assert result["success"] is True
                assert len(result["items"]) == 1
                assert result["items"][0]["name"] == "grilled chicken"
                assert result["confidence"] in ["low", "medium", "high"]
    finally:
        Path(test_path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_analyze_food_photo_gemini_no_api_key():
    """Test Gemini analysis without API key."""
    test_path = "/tmp/test.jpg"
    Image.new('RGB', (100, 100)).save(test_path)

    try:
        with patch('app.agents.tools.vision_tools.settings.GOOGLE_API_KEY', None):
            result = await vision_tools.analyze_food_photo_gemini(test_path)

            assert result["success"] is False
            assert "not configured" in result["error"]
    finally:
        Path(test_path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_analyze_food_photo_openai_success():
    """Test successful food photo analysis with OpenAI."""
    img = Image.new('RGB', (100, 100), color='red')
    test_path = "/tmp/test_food_openai.jpg"
    img.save(test_path)

    try:
        # Mock OpenAI response
        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps([
            {
                "name": "salad",
                "quantity": "200",
                "unit": "grams",
                "preparation": "fresh",
                "confidence": "medium"
            }
        ])

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        with patch('app.agents.tools.vision_tools.openai_client') as mock_client:
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            result = await vision_tools.analyze_food_photo_openai(test_path)

            assert result["success"] is True
            assert len(result["items"]) == 1
            assert result["items"][0]["name"] == "salad"
    finally:
        Path(test_path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_analyze_food_photo_routing():
    """Test that analyze_food_photo routes to correct provider."""
    test_path = "/tmp/test_routing.jpg"
    Image.new('RGB', (100, 100)).save(test_path)

    try:
        # Test Gemini routing
        with patch('app.agents.tools.vision_tools.settings.VISION_PROVIDER', 'gemini'):
            with patch('app.agents.tools.vision_tools.analyze_food_photo_gemini') as mock_gemini:
                mock_gemini.return_value = {"success": True, "items": []}
                await vision_tools.analyze_food_photo(test_path)
                mock_gemini.assert_called_once()

        # Test OpenAI routing
        with patch('app.agents.tools.vision_tools.settings.VISION_PROVIDER', 'openai'):
            with patch('app.agents.tools.vision_tools.analyze_food_photo_openai') as mock_openai:
                mock_openai.return_value = {"success": True, "items": []}
                await vision_tools.analyze_food_photo(test_path)
                mock_openai.assert_called_once()
    finally:
        Path(test_path).unlink(missing_ok=True)


# ===== Search Tools Tests =====

@pytest.mark.asyncio
async def test_search_nutrition_info_success():
    """Test successful nutrition search with Tavily."""
    # Mock Tavily response
    mock_response = {
        "results": [
            {
                "url": "https://fdc.nal.usda.gov/food",
                "content": "Chicken breast: 165 calories, 31g protein, 3.6g fat per 100g"
            }
        ]
    }

    with patch('app.agents.tools.search_tools.settings.ENABLE_WEB_SEARCH', True):
        with patch('app.agents.tools.search_tools.settings.TAVILY_API_KEY', 'test-key'):
            with patch('tavily.TavilyClient') as mock_client:
                mock_instance = MagicMock()
                mock_instance.search.return_value = mock_response
                mock_client.return_value = mock_instance

                result = await search_tools.search_nutrition_info("chicken breast")

                assert result["success"] is True
                assert result["food_name"] == "chicken breast"
                assert "nutrition" in result
                assert result["confidence"] in ["low", "medium", "high"]


@pytest.mark.asyncio
async def test_search_nutrition_info_cached():
    """Test nutrition search returns cached results."""
    # Clear cache first
    search_tools.clear_nutrition_cache()

    # First call - should cache
    with patch('app.agents.tools.search_tools.settings.ENABLE_WEB_SEARCH', False):
        result1 = await search_tools.search_nutrition_info("chicken breast")

    # Add to cache manually
    cache_key = "chicken breast_None_None"
    search_tools._nutrition_cache[cache_key] = {
        "success": True,
        "food_name": "chicken breast",
        "nutrition": {"calories": 165},
        "confidence": "high"
    }

    # Second call - should return cached
    result2 = await search_tools.search_nutrition_info("chicken breast")
    assert result2["success"] is True
    assert result2["confidence"] == "high"


@pytest.mark.asyncio
async def test_search_nutrition_info_no_api_key():
    """Test nutrition search without API key."""
    with patch('app.agents.tools.search_tools.settings.ENABLE_WEB_SEARCH', True):
        with patch('app.agents.tools.search_tools.settings.TAVILY_API_KEY', None):
            result = await search_tools.search_nutrition_info("banana")

            assert result["success"] is False
            assert "not configured" in result["error"]


@pytest.mark.asyncio
async def test_search_nutrition_info_web_disabled():
    """Test nutrition search with web search disabled."""
    with patch('app.agents.tools.search_tools.settings.ENABLE_WEB_SEARCH', False):
        result = await search_tools.search_nutrition_info("apple")

        # Should fall back to backup data
        assert result is not None


@pytest.mark.asyncio
async def test_search_backup_known_food():
    """Test backup search with known food."""
    result = await search_tools.search_backup("chicken breast")

    assert result["success"] is True
    assert result["nutrition"]["calories"] == 165
    assert result["confidence"] == "low"
    assert result["source"] == "estimated"


@pytest.mark.asyncio
async def test_search_backup_unknown_food():
    """Test backup search with unknown food."""
    result = await search_tools.search_backup("exotic_unknown_food")

    assert result["success"] is False
    assert result["nutrition"]["calories"] == 0


def test_parse_nutrition_from_text():
    """Test parsing nutrition values from text."""
    text = """
    Grilled chicken breast nutrition facts:
    - 165 calories per 100g
    - Protein: 31g
    - Fat: 3.6g
    - Carbohydrates: 0g
    - Sodium: 74mg
    """

    result = search_tools.parse_nutrition_from_text(text, "chicken breast")

    assert "calories" in result
    assert result["calories"] == 165
    assert result["protein"] == 31.0
    assert result["fat"] == 3.6


def test_parse_nutrition_empty_text():
    """Test parsing nutrition from empty text."""
    result = search_tools.parse_nutrition_from_text("", "food")
    assert result == {}


def test_get_cached_nutrition():
    """Test getting cached nutrition data."""
    search_tools.clear_nutrition_cache()

    # Add to cache
    cache_key = "test_food_100_g"
    search_tools._nutrition_cache[cache_key] = {"calories": 100}

    result = search_tools.get_cached_nutrition(cache_key)
    assert result is not None
    assert result["calories"] == 100


def test_clear_nutrition_cache():
    """Test clearing nutrition cache."""
    search_tools._nutrition_cache["test"] = {"data": "test"}
    search_tools.clear_nutrition_cache()
    assert len(search_tools._nutrition_cache) == 0


# ===== Fixtures for DB Tests =====

@pytest.fixture
def db_session():
    """Create test database session."""
    from app.core.database import SessionLocal, Base, engine

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    session = SessionLocal()

    yield session

    # Cleanup
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


if __name__ == "__main__":
    """Run tests manually."""
    print("Running Agent Tools Tests...")
    print("=" * 60)

    # Note: Manual running requires proper test setup
    # Use pytest for best results: pytest tests/test_agent_tools.py -v

    print("Use 'pytest tests/test_agent_tools.py -v' to run these tests")
    print("=" * 60)
