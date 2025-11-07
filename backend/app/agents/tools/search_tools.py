"""External search and information retrieval tools for agents.

This module provides tools for agents to search external sources,
retrieve nutritional data, and access fitness information using Tavily API.
"""

import re
import logging
from typing import Any, Dict, Optional

from tavily import TavilyClient

from app.config import settings

logger = logging.getLogger(__name__)

# Simple in-memory cache for nutrition data
_nutrition_cache: Dict[str, Dict[str, Any]] = {}


async def search_nutrition_info(
    food_name: str, quantity: Optional[str] = None, unit: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search for nutrition information using Tavily API.

    Args:
        food_name: Name of the food item (e.g., "grilled chicken breast")
        quantity: Optional quantity (e.g., "150")
        unit: Optional unit (e.g., "grams")

    Returns:
        {
            "success": True/False,
            "food_name": "...",
            "nutrition": {
                "calories": 165,  # per specified quantity or per 100g
                "protein": 31.0,  # grams
                "carbs": 0.0,
                "fat": 3.6,
                "fiber": 0.0,
                "sugar": 0.0,
                "sodium": 74.0  # mg
            },
            "serving_size": "100g" or custom,
            "source": "URL or source name",
            "confidence": "high/medium/low",
            "error": None or error message
        }
    """
    # Check cache first
    cache_key = f"{food_name.lower()}_{quantity}_{unit}"
    cached = get_cached_nutrition(cache_key)
    if cached:
        logger.info(f"Returning cached nutrition data for {food_name}")
        return cached

    # Check if web search is enabled
    if not settings.ENABLE_WEB_SEARCH:
        logger.warning("Web search is disabled, using fallback")
        return await search_backup(food_name)

    # Check if API key is available
    if not settings.TAVILY_API_KEY:
        logger.error("Tavily API key not configured")
        return {
            "success": False,
            "food_name": food_name,
            "nutrition": {},
            "serving_size": "unknown",
            "source": "none",
            "confidence": "low",
            "error": "Tavily API key not configured",
        }

    try:
        # Initialize Tavily client
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)

        # Construct search query
        query = f"{food_name} nutrition facts calories protein carbs fat"
        if quantity and unit:
            query += f" per {quantity} {unit}"

        logger.info(f"Searching nutrition info for: {query}")

        # Perform search
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=5,
            include_domains=[
                "usda.gov",
                "nutritionix.com",
                "myfitnesspal.com",
                "fdc.nal.usda.gov",
                "eatthismuch.com",
                "calorieking.com",
            ],
        )

        if not response or "results" not in response or not response["results"]:
            logger.warning(f"No results found for {food_name}")
            return await search_backup(food_name)

        # Parse results
        best_result = None
        best_confidence = "low"

        for result in response["results"]:
            content = result.get("content", "")
            url = result.get("url", "")

            # Determine source confidence
            confidence = "low"
            if "usda.gov" in url or "fdc.nal.usda.gov" in url:
                confidence = "high"
            elif "nutritionix.com" in url or "myfitnesspal.com" in url:
                confidence = "medium"

            # Parse nutrition data from content
            nutrition_data = parse_nutrition_from_text(content, food_name)

            if nutrition_data and len(nutrition_data) >= 3:  # At least 3 nutrients found
                if best_result is None or confidence == "high":
                    best_result = {
                        "nutrition": nutrition_data,
                        "source": url,
                        "confidence": confidence,
                    }
                    if confidence == "high":
                        break  # Stop at first high-confidence result

        if not best_result:
            logger.warning(f"Could not parse nutrition data from results for {food_name}")
            return await search_backup(food_name)

        # Determine serving size
        serving_size = "100g"  # Default
        if quantity and unit:
            serving_size = f"{quantity}{unit}"

        # Scale nutrition values if custom quantity is provided
        nutrition = best_result["nutrition"]
        if quantity and unit and unit.lower() in ["g", "grams", "gram"]:
            try:
                scale_factor = float(quantity) / 100.0
                nutrition = {k: round(v * scale_factor, 1) for k, v in nutrition.items()}
            except (ValueError, TypeError):
                logger.warning(f"Could not scale nutrition values for quantity: {quantity}")

        result_data = {
            "success": True,
            "food_name": food_name,
            "nutrition": nutrition,
            "serving_size": serving_size,
            "source": best_result["source"],
            "confidence": best_result["confidence"],
            "error": None,
        }

        # Cache the result
        _nutrition_cache[cache_key] = result_data

        return result_data

    except Exception as e:
        logger.error(f"Error searching nutrition info for {food_name}: {e}")
        return {
            "success": False,
            "food_name": food_name,
            "nutrition": {},
            "serving_size": "unknown",
            "source": "none",
            "confidence": "low",
            "error": str(e),
        }


def parse_nutrition_from_text(text: str, food_name: str) -> Dict[str, float]:
    """
    Extract nutrition values from text using regex patterns.

    Look for patterns like:
    - "165 calories"
    - "31g protein"
    - "Protein: 31 grams"
    - "Calories per 100g: 165"

    Args:
        text: Text content to parse
        food_name: Name of the food (for context)

    Returns:
        Dictionary with nutrition values (calories, protein, carbs, fat, etc.)
    """
    nutrition: Dict[str, float] = {}

    # Normalize text
    text = text.lower()

    # Patterns for different nutrients (order matters - more specific first)
    # Using [ \t]+ for whitespace to avoid matching across lines with \s+
    patterns = {
        "calories": [
            r"\b(\d+\.?\d*)[ \t]*calories\b",
            r"\bcalories:?[ \t]+(\d+\.?\d*)",
            r"\benergy:?[ \t]+(\d+\.?\d*)[ \t]*kcal",
            r"\b(\d+\.?\d*)[ \t]*kcal\b",
        ],
        "protein": [
            r"\b(\d+\.?\d*)[ \t]*g(?:rams?)?[ \t]+protein\b",
            r"\bprotein:?[ \t]+(\d+\.?\d*)[ \t]*g(?:rams?)?\b",
        ],
        "carbs": [
            r"\b(\d+\.?\d*)[ \t]*g(?:rams?)?[ \t]+carb",
            r"\bcarb(?:ohydrate)?s?:?[ \t]+(\d+\.?\d*)[ \t]*g(?:rams?)?\b",
        ],
        "fat": [
            r"\b(\d+\.?\d*)[ \t]*g(?:rams?)?[ \t]+(?:total[ \t]+)?fat\b",
            r"\b(?:total[ \t]+)?fat:?[ \t]+(\d+\.?\d*)[ \t]*g(?:rams?)?\b",
        ],
        "fiber": [
            r"\b(\d+\.?\d*)[ \t]*g(?:rams?)?[ \t]+(?:dietary[ \t]+)?fiber\b",
            r"\b(?:dietary[ \t]+)?fiber:?[ \t]+(\d+\.?\d*)[ \t]*g(?:rams?)?\b",
        ],
        "sugar": [
            r"\b(\d+\.?\d*)[ \t]*g(?:rams?)?[ \t]+(?:total[ \t]+)?sugars?\b",
            r"\b(?:total[ \t]+)?sugars?:?[ \t]+(\d+\.?\d*)[ \t]*g(?:rams?)?\b",
        ],
        "sodium": [
            r"\b(\d+\.?\d*)[ \t]*mg[ \t]+sodium\b",
            r"\bsodium:?[ \t]+(\d+\.?\d*)[ \t]*mg\b",
        ],
    }

    # Extract values using patterns
    for nutrient, nutrient_patterns in patterns.items():
        for pattern in nutrient_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    value = float(match.group(1))
                    nutrition[nutrient] = value
                    break  # Found value for this nutrient
                except (ValueError, IndexError):
                    continue

    return nutrition


async def search_backup(food_name: str) -> Dict[str, Any]:
    """
    Fallback to basic nutrition estimates if web search fails.

    Uses a simple database of common foods. In production, this could
    call an LLM for estimation or use a local nutrition database.

    Args:
        food_name: Name of the food item

    Returns:
        Estimated nutrition data with low confidence
    """
    # Common food estimates (per 100g)
    common_foods = {
        "chicken breast": {
            "calories": 165,
            "protein": 31.0,
            "carbs": 0.0,
            "fat": 3.6,
            "fiber": 0.0,
            "sugar": 0.0,
            "sodium": 74.0,
        },
        "rice": {
            "calories": 130,
            "protein": 2.7,
            "carbs": 28.0,
            "fat": 0.3,
            "fiber": 0.4,
            "sugar": 0.1,
            "sodium": 1.0,
        },
        "broccoli": {
            "calories": 34,
            "protein": 2.8,
            "carbs": 7.0,
            "fat": 0.4,
            "fiber": 2.6,
            "sugar": 1.7,
            "sodium": 33.0,
        },
        "salmon": {
            "calories": 208,
            "protein": 20.0,
            "carbs": 0.0,
            "fat": 13.0,
            "fiber": 0.0,
            "sugar": 0.0,
            "sodium": 59.0,
        },
        "egg": {
            "calories": 155,
            "protein": 13.0,
            "carbs": 1.1,
            "fat": 11.0,
            "fiber": 0.0,
            "sugar": 1.1,
            "sodium": 124.0,
        },
        "banana": {
            "calories": 89,
            "protein": 1.1,
            "carbs": 23.0,
            "fat": 0.3,
            "fiber": 2.6,
            "sugar": 12.0,
            "sodium": 1.0,
        },
        "apple": {
            "calories": 52,
            "protein": 0.3,
            "carbs": 14.0,
            "fat": 0.2,
            "fiber": 2.4,
            "sugar": 10.0,
            "sodium": 1.0,
        },
    }

    # Try to find matching food
    food_lower = food_name.lower()
    for key, nutrition in common_foods.items():
        if key in food_lower or food_lower in key:
            logger.info(f"Using backup nutrition data for {food_name} (matched: {key})")
            return {
                "success": True,
                "food_name": food_name,
                "nutrition": nutrition,
                "serving_size": "100g",
                "source": "estimated",
                "confidence": "low",
                "error": "Using estimated values from common food database",
            }

    # No match found, return empty result
    logger.warning(f"No backup data available for {food_name}")
    return {
        "success": False,
        "food_name": food_name,
        "nutrition": {
            "calories": 0,
            "protein": 0.0,
            "carbs": 0.0,
            "fat": 0.0,
            "fiber": 0.0,
            "sugar": 0.0,
            "sodium": 0.0,
        },
        "serving_size": "100g",
        "source": "none",
        "confidence": "low",
        "error": "No nutrition data found",
    }


def get_cached_nutrition(cache_key: str) -> Optional[Dict[str, Any]]:
    """
    Check if we have cached nutrition data for this food.

    Args:
        cache_key: Cache key for the food item

    Returns:
        Cached nutrition data or None if not found
    """
    return _nutrition_cache.get(cache_key)


def clear_nutrition_cache() -> None:
    """Clear the nutrition cache."""
    global _nutrition_cache
    _nutrition_cache = {}
    logger.info("Nutrition cache cleared")
