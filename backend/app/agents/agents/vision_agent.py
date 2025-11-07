"""Vision Agent for processing meal photos and creating meal entries.

This agent uses LangGraph to orchestrate a workflow that:
1. Analyzes meal photos using GPT-4 Vision
2. Searches for nutrition information
3. Calculates total nutrition values
4. Creates Meal and MealItem database entries

The agent handles partial failures gracefully, saving recognized items
even if complete nutrition data cannot be retrieved.
"""

import json
import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph
from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.agents.tools.search_tools import search_nutrition_info
from app.agents.tools.vision_tools import analyze_food_photo
from app.models.meal import Meal, MealItem

logger = logging.getLogger(__name__)


class VisionAgentState(TypedDict):
    """State for Vision Agent workflow.

    This state is passed through the LangGraph workflow nodes,
    accumulating results at each step.

    Attributes:
        user_id: ID of the user who uploaded the photo
        day_id: ID of the day this meal belongs to
        photo_path: Absolute path to the meal photo file
        category: Meal category (breakfast, lunch, dinner, snack)
        recognized_items: List of food items identified by Vision API
        nutrition_data: List of nutrition info for each item
        needs_web_search: List of items that need web search
        totals: Calculated total nutrition values
        meal_id: ID of created meal (set on success)
        success: Whether the workflow completed successfully
        error: Error message if workflow failed
        partial_results: Partial results if workflow partially failed
        confidence: Overall confidence level (high/medium/low)
    """
    user_id: int
    day_id: int
    photo_path: str
    category: str
    # Intermediate results
    recognized_items: List[Dict[str, Any]]
    nutrition_data: List[Dict[str, Any]]
    needs_web_search: List[str]
    totals: Optional[Dict[str, float]]
    # Final output
    meal_id: Optional[int]
    success: bool
    error: Optional[str]
    partial_results: Optional[Dict[str, Any]]
    confidence: str


class VisionAgent(BaseAgent):
    """Agent for processing meal photos and creating meal entries.

    This agent extends BaseAgent and uses LangGraph to orchestrate
    a multi-step workflow for analyzing meal photos:

    1. analyze_photo: Use GPT-4 Vision to identify food items
    2. search_nutrition: Lookup nutrition info for each item
    3. calculate_totals: Sum up total nutrition values
    4. create_meal: Save to database
    5. handle_error: Handle partial failures gracefully

    Example:
        ```python
        agent = VisionAgent(db_session, user_id=1)
        result = await agent.execute({
            "day_id": 42,
            "photo_path": "/uploads/meal_photos/lunch.jpg",
            "category": "lunch"
        })

        if result["success"]:
            print(f"Created meal ID: {result['meal_id']}")
        else:
            print(f"Error: {result['error']}")
            if result.get("partial_results"):
                print(f"Saved partial results: {result['partial_results']}")
        ```
    """

    def __init__(self, db_session: Session, user_id: int):
        """Initialize Vision Agent.

        Args:
            db_session: SQLAlchemy database session
            user_id: ID of the user this agent operates for
        """
        super().__init__(db_session, user_id, "vision")
        self.graph = self._build_graph()
        logger.info(f"Vision Agent initialized for user {user_id}")

    def _build_graph(self) -> Any:
        """Build the LangGraph workflow.

        Creates a state machine that orchestrates the meal photo
        processing workflow with conditional edges for error handling.

        Returns:
            Compiled LangGraph workflow
        """
        workflow = StateGraph(VisionAgentState)

        # Add nodes for each step
        workflow.add_node("analyze_photo", self._analyze_photo)
        workflow.add_node("search_nutrition", self._search_nutrition)
        workflow.add_node("calculate_totals", self._calculate_totals)
        workflow.add_node("create_meal", self._create_meal)
        workflow.add_node("handle_error", self._handle_error)

        # Define workflow edges
        workflow.set_entry_point("analyze_photo")

        # Conditional routing after photo analysis
        workflow.add_conditional_edges(
            "analyze_photo",
            self._should_search_nutrition,
            {
                "search": "search_nutrition",
                "calculate": "calculate_totals",
                "error": "handle_error"
            }
        )

        # After nutrition search, always calculate totals
        workflow.add_edge("search_nutrition", "calculate_totals")

        # Conditional routing after calculating totals
        workflow.add_conditional_edges(
            "calculate_totals",
            self._should_create_meal,
            {
                "create": "create_meal",
                "error": "handle_error"
            }
        )

        # End points
        workflow.add_edge("create_meal", END)
        workflow.add_edge("handle_error", END)

        return workflow.compile()

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute vision agent workflow.

        Processes a meal photo through the complete workflow:
        analyze → search → calculate → create.

        Args:
            input_data: Dictionary with required keys:
                - day_id (int): ID of the day
                - photo_path (str): Absolute path to photo
                - category (str, optional): Meal category, defaults to "snack"

        Returns:
            Dictionary with workflow results:
                - success (bool): Whether workflow succeeded
                - meal_id (int, optional): ID of created meal
                - error (str, optional): Error message if failed
                - partial_results (dict, optional): Partial results if partially failed
                - confidence (str): Overall confidence (high/medium/low)
                - recognized_items (list): Items identified
                - nutrition_data (list): Nutrition info found

        Raises:
            ValueError: If required input fields are missing
        """
        # Validate input
        if "day_id" not in input_data:
            raise ValueError("Missing required field: day_id")
        if "photo_path" not in input_data:
            raise ValueError("Missing required field: photo_path")

        logger.info(
            f"Executing Vision Agent workflow for user {self.user_id}, "
            f"day {input_data['day_id']}, photo {input_data['photo_path']}"
        )

        # Initialize state
        initial_state: VisionAgentState = {
            "user_id": self.user_id,
            "day_id": input_data["day_id"],
            "photo_path": input_data["photo_path"],
            "category": input_data.get("category", "snack"),
            "recognized_items": [],
            "nutrition_data": [],
            "needs_web_search": [],
            "totals": None,
            "meal_id": None,
            "success": False,
            "error": None,
            "partial_results": None,
            "confidence": "low"
        }

        # Execute workflow
        try:
            result = await self.graph.ainvoke(initial_state)

            # Log result
            if result["success"]:
                logger.info(
                    f"Vision Agent workflow completed successfully. "
                    f"Created meal ID: {result['meal_id']}"
                )
            else:
                logger.warning(
                    f"Vision Agent workflow failed: {result['error']}. "
                    f"Partial results: {result.get('partial_results')}"
                )

            return result

        except Exception as e:
            logger.error(f"Vision Agent workflow error: {e}", exc_info=True)
            return {
                "success": False,
                "meal_id": None,
                "error": f"Workflow execution failed: {str(e)}",
                "partial_results": None,
                "confidence": "low",
                "recognized_items": [],
                "nutrition_data": []
            }

    async def _analyze_photo(self, state: VisionAgentState) -> VisionAgentState:
        """Step 1: Analyze photo using GPT-4 Vision.

        Uses the vision_tools.analyze_food_photo function to identify
        food items in the meal photo.

        Args:
            state: Current workflow state

        Returns:
            Updated state with recognized_items and confidence
        """
        logger.info(f"Analyzing photo: {state['photo_path']}")

        try:
            result = await analyze_food_photo(state["photo_path"])

            if result["success"]:
                state["recognized_items"] = result["items"]
                state["confidence"] = result.get("confidence", "low")
                logger.info(
                    f"Photo analysis successful. Found {len(result['items'])} items "
                    f"with {state['confidence']} confidence"
                )
            else:
                state["error"] = result.get("error", "Photo analysis failed")
                logger.error(f"Photo analysis failed: {state['error']}")

        except Exception as e:
            logger.error(f"Error in _analyze_photo: {e}", exc_info=True)
            state["error"] = f"Photo analysis error: {str(e)}"

        return state

    async def _search_nutrition(self, state: VisionAgentState) -> VisionAgentState:
        """Step 2: Search nutrition info for recognized items.

        For each recognized food item, searches for nutrition information
        using web search or local database.

        Args:
            state: Current workflow state with recognized_items

        Returns:
            Updated state with nutrition_data and needs_web_search
        """
        logger.info(f"Searching nutrition for {len(state['recognized_items'])} items")

        nutrition_data = []
        needs_web_search = []

        for item in state["recognized_items"]:
            try:
                food_name = item.get("name", "Unknown food")
                quantity = item.get("quantity")
                unit = item.get("unit")

                logger.debug(f"Searching nutrition for: {food_name} ({quantity} {unit})")

                nutrition = await search_nutrition_info(
                    food_name=food_name,
                    quantity=quantity,
                    unit=unit
                )

                if nutrition["success"]:
                    # Merge item info with nutrition data
                    nutrition_data.append({
                        "item": item,
                        "nutrition": nutrition["nutrition"],
                        "source": nutrition.get("source", "unknown"),
                        "confidence": nutrition.get("confidence", "low")
                    })
                    logger.debug(f"Found nutrition for {food_name}: {nutrition['nutrition']}")
                else:
                    # Track items that need web search
                    needs_web_search.append(food_name)
                    logger.warning(f"No nutrition found for {food_name}")

                    # Add placeholder with zero nutrition
                    nutrition_data.append({
                        "item": item,
                        "nutrition": {
                            "calories": 0.0,
                            "protein": 0.0,
                            "carbs": 0.0,
                            "fat": 0.0,
                            "fiber": 0.0,
                            "sugar": 0.0,
                            "sodium": 0.0
                        },
                        "source": "none",
                        "confidence": "low"
                    })

            except Exception as e:
                logger.error(f"Error searching nutrition for {item.get('name')}: {e}")
                needs_web_search.append(item.get("name", "Unknown"))

        state["nutrition_data"] = nutrition_data
        state["needs_web_search"] = needs_web_search

        logger.info(
            f"Nutrition search complete. Found data for "
            f"{len(nutrition_data) - len(needs_web_search)}/{len(nutrition_data)} items"
        )

        return state

    async def _calculate_totals(self, state: VisionAgentState) -> VisionAgentState:
        """Step 3: Calculate total nutrition values.

        Sums up nutrition values from all items to get meal totals.

        Args:
            state: Current workflow state with nutrition_data

        Returns:
            Updated state with totals
        """
        logger.info("Calculating nutrition totals")

        totals = {
            "calories": 0.0,
            "protein": 0.0,
            "carbs": 0.0,
            "fat": 0.0,
            "fiber": 0.0,
            "sugar": 0.0,
            "sodium": 0.0
        }

        try:
            for nutrition_entry in state["nutrition_data"]:
                nutrition = nutrition_entry.get("nutrition", {})
                for key in totals:
                    value = nutrition.get(key, 0.0)
                    # Handle both float and string values
                    if isinstance(value, str):
                        try:
                            value = float(value)
                        except (ValueError, TypeError):
                            value = 0.0
                    totals[key] += float(value)

            # Round to 2 decimal places
            totals = {k: round(v, 2) for k, v in totals.items()}

            state["totals"] = totals
            logger.info(f"Calculated totals: {totals}")

        except Exception as e:
            logger.error(f"Error calculating totals: {e}", exc_info=True)
            state["error"] = f"Failed to calculate totals: {str(e)}"

        return state

    async def _create_meal(self, state: VisionAgentState) -> VisionAgentState:
        """Step 4: Create Meal and MealItems in database.

        Creates a Meal entry with the calculated totals and individual
        MealItem entries for each recognized food item.

        Note: The current Meal model doesn't have photo_path,
        photo_processing_status, or ai_recognized_items fields.
        Using available fields (photo_url, notes, ai_summary).

        Args:
            state: Current workflow state with totals and nutrition_data

        Returns:
            Updated state with meal_id and success=True
        """
        logger.info(f"Creating meal in database for day {state['day_id']}")

        try:
            totals = state["totals"]
            if not totals:
                raise ValueError("No totals calculated")

            # Prepare AI recognized items data
            ai_recognized_items = state["recognized_items"]

            # Prepare AI summary text
            item_names = [item.get("name", "unknown") for item in state["recognized_items"]]
            ai_summary = f"Recognized {len(item_names)} items: {', '.join(item_names)}"

            # Create Meal
            meal = Meal(
                day_id=state["day_id"],
                category=state["category"],
                calories=Decimal(str(totals["calories"])),
                protein=Decimal(str(totals["protein"])),
                carbs=Decimal(str(totals["carbs"])),
                fat=Decimal(str(totals["fat"])),
                fiber=Decimal(str(totals.get("fiber", 0.0))),
                sugar=Decimal(str(totals.get("sugar", 0.0))),
                sodium=Decimal(str(totals.get("sodium", 0.0))),
                photo_path=state["photo_path"],
                photo_processing_status="completed",
                ai_recognized_items=ai_recognized_items,
                ai_summary=ai_summary,
                notes="Auto-generated from photo analysis"
            )

            self.db.add(meal)
            self.db.flush()  # Get the meal ID

            logger.info(f"Created meal ID: {meal.id}")

            # Create MealItems
            for nutrition_entry in state["nutrition_data"]:
                item = nutrition_entry["item"]
                nutrition = nutrition_entry["nutrition"]

                try:
                    # Parse quantity
                    quantity_str = str(item.get("quantity", "100"))
                    try:
                        quantity = float(quantity_str)
                    except (ValueError, TypeError):
                        quantity = 100.0

                    meal_item = MealItem(
                        meal_id=meal.id,
                        name=item.get("name", "Unknown food"),
                        amount=Decimal(str(quantity)),
                        unit=item.get("unit", "grams"),
                        calories=Decimal(str(nutrition.get("calories", 0.0))),
                        protein=Decimal(str(nutrition.get("protein", 0.0))),
                        carbs=Decimal(str(nutrition.get("carbs", 0.0))),
                        fat=Decimal(str(nutrition.get("fat", 0.0)))
                    )

                    self.db.add(meal_item)
                    logger.debug(f"Created meal item: {meal_item.name}")

                except Exception as e:
                    logger.error(f"Error creating meal item for {item.get('name')}: {e}")
                    # Continue with other items

            # Commit transaction
            self.db.commit()

            state["meal_id"] = meal.id
            state["success"] = True

            logger.info(
                f"Successfully created meal {meal.id} with "
                f"{len(state['nutrition_data'])} items"
            )

        except Exception as e:
            logger.error(f"Error creating meal in database: {e}", exc_info=True)
            self.db.rollback()
            state["error"] = f"Database error: {str(e)}"
            state["success"] = False

        return state

    async def _handle_error(self, state: VisionAgentState) -> VisionAgentState:
        """Handle errors with partial results.

        When the workflow fails, this node attempts to save partial
        results so the user can review and complete manually.

        For example, if Vision API recognized items but nutrition
        search failed, we save the recognized items for manual entry.

        Args:
            state: Current workflow state with error

        Returns:
            Updated state with partial_results and success=False
        """
        logger.warning(f"Handling error: {state.get('error')}")

        # Collect partial results
        partial_results = {
            "recognized_items": state.get("recognized_items", []),
            "nutrition_data": state.get("nutrition_data", []),
            "needs_web_search": state.get("needs_web_search", []),
            "confidence": state.get("confidence", "low")
        }

        state["partial_results"] = partial_results
        state["success"] = False

        # If we have some recognized items, try to save them to database
        # as a meal with "needs_review" status
        if state.get("recognized_items"):
            try:
                logger.info("Attempting to save partial results to database")

                # Create a meal with partial data
                ai_recognized_items_list = state["recognized_items"]

                # Add metadata to items
                for item in ai_recognized_items_list:
                    item["needs_review"] = True

                meal = Meal(
                    day_id=state["day_id"],
                    category=state["category"],
                    photo_path=state["photo_path"],
                    photo_processing_status="failed",
                    photo_processing_error=state.get("error"),
                    ai_recognized_items=ai_recognized_items_list,
                    ai_summary=f"Partial recognition: {len(ai_recognized_items_list)} items need review",
                    notes="Partial results - needs manual review"
                )

                self.db.add(meal)
                self.db.commit()

                state["meal_id"] = meal.id
                logger.info(f"Saved partial results as meal ID: {meal.id}")

            except Exception as e:
                logger.error(f"Failed to save partial results: {e}", exc_info=True)
                self.db.rollback()

        return state

    def _should_search_nutrition(self, state: VisionAgentState) -> str:
        """Decide next step after photo analysis.

        Routing logic:
        - If error occurred → go to error handler
        - If items recognized → go to nutrition search
        - Otherwise → go to error handler

        Args:
            state: Current workflow state

        Returns:
            Next node name: "search", "calculate", or "error"
        """
        if state.get("error"):
            logger.debug("Routing to error handler due to error")
            return "error"

        if state.get("recognized_items"):
            logger.debug(f"Routing to nutrition search for {len(state['recognized_items'])} items")
            return "search"

        logger.debug("Routing to error handler - no items recognized")
        state["error"] = "No food items recognized in photo"
        return "error"

    def _should_create_meal(self, state: VisionAgentState) -> str:
        """Decide whether to create meal or handle error.

        Routing logic:
        - If error occurred → go to error handler
        - If totals calculated → go to create meal
        - Otherwise → go to error handler

        Args:
            state: Current workflow state

        Returns:
            Next node name: "create" or "error"
        """
        if state.get("error"):
            logger.debug("Routing to error handler due to error")
            return "error"

        if state.get("totals"):
            logger.debug("Routing to meal creation")
            return "create"

        logger.debug("Routing to error handler - no totals calculated")
        state["error"] = "Failed to calculate nutrition totals"
        return "error"
