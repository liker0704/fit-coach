"""Computer vision tools for meal photo analysis using GPT-4 Vision.

This module provides tools for analyzing meal photos and identifying food items
using GPT-4 Vision API.
"""

import base64
import json
import logging
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from openai import AsyncOpenAI, OpenAIError
from PIL import Image

from app.config import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# Load vision prompt
VISION_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "vision_agent.txt"
try:
    with open(VISION_PROMPT_PATH, "r", encoding="utf-8") as f:
        VISION_PROMPT = f.read().strip()
except Exception as e:
    logger.error(f"Failed to load vision prompt: {e}")
    VISION_PROMPT = """You are a food recognition expert. Analyze this meal photo and identify all food items.
Return ONLY a JSON array with food items including name, quantity, unit, preparation, and confidence."""


def prepare_image(photo_path: str, max_size: Tuple[int, int] = (2048, 2048)) -> str:
    """Prepare image for Vision API.

    Resizes the image if it's too large and converts it to base64.

    Args:
        photo_path: Absolute path to the meal photo
        max_size: Maximum dimensions (width, height) for the image

    Returns:
        Base64-encoded image string

    Raises:
        FileNotFoundError: If the image file doesn't exist
        ValueError: If the image is corrupted or invalid
    """
    try:
        # Check if file exists
        if not Path(photo_path).exists():
            raise FileNotFoundError(f"Image file not found: {photo_path}")

        # Open and process image
        with Image.open(photo_path) as img:
            # Convert RGBA to RGB if needed
            if img.mode == "RGBA":
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # Resize if too large
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                logger.info(f"Resized image from original size to {img.size}")

            # Convert to base64
            buffered = BytesIO()
            img.save(buffered, format="JPEG", quality=85)
            img_bytes = buffered.getvalue()
            img_base64 = base64.b64encode(img_bytes).decode("utf-8")

            return img_base64

    except FileNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error preparing image {photo_path}: {e}")
        raise ValueError(f"Failed to process image: {str(e)}")


async def analyze_food_photo(photo_path: str) -> Dict[str, Any]:
    """Analyze a meal photo using GPT-4 Vision.

    Identifies food items, estimates portions, and returns structured data
    about the meal contents.

    Args:
        photo_path: Absolute path to the meal photo

    Returns:
        Dictionary with the following structure:
        {
            "success": True/False,
            "items": [
                {
                    "name": "chicken breast",
                    "quantity": "150",
                    "unit": "grams",
                    "preparation": "grilled",
                    "confidence": "high/medium/low"
                },
                ...
            ],
            "confidence": "high/medium/low",  # Overall confidence
            "error": None or error message
        }

    Example:
        >>> result = await analyze_food_photo("/path/to/meal.jpg")
        >>> if result["success"]:
        ...     for item in result["items"]:
        ...         print(f"{item['name']}: {item['quantity']}{item['unit']}")
    """
    result = {
        "success": False,
        "items": [],
        "confidence": "low",
        "error": None
    }

    try:
        # Prepare the image
        logger.info(f"Analyzing food photo: {photo_path}")
        img_base64 = prepare_image(photo_path)

        # Call GPT-4 Vision API
        logger.info(f"Calling Vision API with model: {settings.VISION_MODEL}")
        response = await client.chat.completions.create(
            model=settings.VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": VISION_PROMPT
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=settings.VISION_MAX_TOKENS,
            temperature=0.3,  # Lower temperature for more consistent results
        )

        # Extract response content
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from Vision API")

        logger.info(f"Vision API response: {content[:200]}...")

        # Parse JSON response
        try:
            # Clean up response - sometimes the model adds markdown code blocks
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            items = json.loads(content)

            # Validate the response structure
            if not isinstance(items, list):
                raise ValueError("Response is not a JSON array")

            # Validate each item has required fields
            validated_items = []
            for item in items:
                if not isinstance(item, dict):
                    logger.warning(f"Skipping invalid item: {item}")
                    continue

                # Ensure all required fields exist
                validated_item = {
                    "name": item.get("name", "Unknown food"),
                    "quantity": str(item.get("quantity", "0")),
                    "unit": item.get("unit", "grams"),
                    "preparation": item.get("preparation", "unknown"),
                    "confidence": item.get("confidence", "low")
                }
                validated_items.append(validated_item)

            if not validated_items:
                raise ValueError("No valid food items identified")

            # Calculate overall confidence
            confidence_levels = {"high": 3, "medium": 2, "low": 1}
            avg_confidence = sum(confidence_levels.get(item["confidence"], 1)
                               for item in validated_items) / len(validated_items)

            if avg_confidence >= 2.5:
                overall_confidence = "high"
            elif avg_confidence >= 1.5:
                overall_confidence = "medium"
            else:
                overall_confidence = "low"

            result["success"] = True
            result["items"] = validated_items
            result["confidence"] = overall_confidence

            logger.info(f"Successfully analyzed photo: found {len(validated_items)} items "
                       f"with {overall_confidence} confidence")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {content}")
            result["error"] = f"Failed to parse Vision API response: {str(e)}"

            # Try to provide partial results
            result["items"] = [{
                "name": "Unidentified food",
                "quantity": "0",
                "unit": "grams",
                "preparation": "unknown",
                "confidence": "low"
            }]

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        result["error"] = str(e)

    except ValueError as e:
        logger.error(f"Image processing error: {e}")
        result["error"] = str(e)

    except OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        result["error"] = f"Vision API error: {str(e)}"

    except Exception as e:
        logger.error(f"Unexpected error analyzing photo: {e}", exc_info=True)
        result["error"] = f"Unexpected error: {str(e)}"

    return result


async def analyze_meal_image(photo_path: str) -> Dict[str, Any]:
    """Legacy alias for analyze_food_photo.

    Args:
        photo_path: Absolute path to the meal photo

    Returns:
        Same as analyze_food_photo
    """
    return await analyze_food_photo(photo_path)
