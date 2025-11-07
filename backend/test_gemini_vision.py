"""
Test script for Gemini Vision integration.

This script tests the Gemini Vision API integration for meal photo analysis.
It can be used to verify that the API is working correctly before deploying.

Usage:
    python test_gemini_vision.py <path_to_meal_photo>

Example:
    python test_gemini_vision.py uploads/meal_photos/test_meal.jpg
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.agents.tools.vision_tools import analyze_food_photo
from app.config import settings


async def test_vision_api(photo_path: str):
    """Test the vision API with a meal photo."""
    print(f"\n{'='*60}")
    print(f"Testing Vision API")
    print(f"{'='*60}")
    print(f"Provider: {settings.VISION_PROVIDER}")

    if settings.VISION_PROVIDER.lower() == "gemini":
        print(f"Model: {settings.GEMINI_VISION_MODEL}")
        if not settings.GOOGLE_API_KEY:
            print("\nERROR: GOOGLE_API_KEY not set in environment!")
            print("Please set GOOGLE_API_KEY in your .env file")
            return
    else:
        print(f"Model: {settings.VISION_MODEL}")
        if not settings.OPENAI_API_KEY:
            print("\nERROR: OPENAI_API_KEY not set in environment!")
            print("Please set OPENAI_API_KEY in your .env file")
            return

    print(f"Photo: {photo_path}")
    print(f"{'='*60}\n")

    # Check if photo exists
    if not Path(photo_path).exists():
        print(f"ERROR: Photo not found at {photo_path}")
        return

    # Analyze the photo
    print("Analyzing photo...")
    result = await analyze_food_photo(photo_path)

    # Display results
    print(f"\n{'='*60}")
    print(f"Results")
    print(f"{'='*60}")
    print(f"Success: {result['success']}")
    print(f"Confidence: {result['confidence']}")

    if result['error']:
        print(f"Error: {result['error']}")

    if result['items']:
        print(f"\nRecognized Items ({len(result['items'])}):")
        print("-" * 60)
        for i, item in enumerate(result['items'], 1):
            print(f"{i}. {item['name']}")
            print(f"   Quantity: {item['quantity']} {item['unit']}")
            print(f"   Preparation: {item['preparation']}")
            print(f"   Confidence: {item['confidence']}")
            print()

    # Print raw JSON for debugging
    print(f"\n{'='*60}")
    print(f"Raw JSON Response")
    print(f"{'='*60}")
    print(json.dumps(result, indent=2))


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python test_gemini_vision.py <path_to_meal_photo>")
        print("\nExample:")
        print("  python test_gemini_vision.py uploads/meal_photos/test_meal.jpg")
        sys.exit(1)

    photo_path = sys.argv[1]

    # Run the async test
    asyncio.run(test_vision_api(photo_path))


if __name__ == "__main__":
    main()
