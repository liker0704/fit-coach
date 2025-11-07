"""Cost tracking for LLM API usage and agent operations.

This module tracks token usage, API costs, and provides analytics
for monitoring and optimizing LLM usage across all agents.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.models.agent_cost import AgentCost


class CostTracker:
    """Tracks LLM API usage and costs."""

    # Current pricing as of 2025 (per 1K tokens)
    PRICING = {
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "gpt-4-vision-preview": {"input": 0.01, "output": 0.03},
        "gemini-2.0-flash-exp": {"input": 0.0, "output": 0.0},  # Free tier
        "gemini-pro": {"input": 0.00025, "output": 0.0005},
    }

    def __init__(self, db_session: Session):
        """Initialize cost tracker with database session.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    def track_usage(
        self,
        user_id: int,
        agent_type: str,
        model: str,
        tokens_input: int,
        tokens_output: int,
    ) -> AgentCost:
        """Record LLM usage and calculate cost.

        Automatically calculates cost based on PRICING table and stores
        the usage record in the database.

        Args:
            user_id: User ID for cost tracking
            agent_type: Type of agent (nutrition, chatbot, exercise, etc.)
            model: LLM model name (gpt-4-turbo, gemini-pro, etc.)
            tokens_input: Number of input tokens used
            tokens_output: Number of output tokens generated

        Returns:
            AgentCost object with recorded usage and cost

        Example:
            >>> cost = tracker.track_usage(
            ...     user_id=1,
            ...     agent_type="nutrition",
            ...     model="gpt-4-turbo",
            ...     tokens_input=500,
            ...     tokens_output=200
            ... )
            >>> print(f"Cost: ${cost.cost_usd}")
        """
        # Calculate cost
        cost_usd = self.calculate_cost(model, tokens_input, tokens_output)

        # Create cost record
        cost_record = AgentCost(
            user_id=user_id,
            agent_type=agent_type,
            model=model,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            cost_usd=cost_usd,
        )

        # Save to database
        self.db.add(cost_record)
        self.db.commit()
        self.db.refresh(cost_record)

        return cost_record

    def get_user_costs(self, user_id: int, period: str = "month") -> Dict[str, Any]:
        """Get cost statistics for a user.

        Args:
            user_id: User ID to get costs for
            period: Time period ('day', 'week', 'month', 'all')

        Returns:
            Dictionary with cost statistics:
            {
                "total_cost": 2.45,
                "total_tokens": 50000,
                "by_agent": {"nutrition": 1.20, "chatbot": 0.80, ...},
                "by_model": {"gpt-4-turbo": 2.00, "gemini-pro": 0.45},
                "usage_count": 150
            }

        Example:
            >>> stats = tracker.get_user_costs(user_id=1, period="week")
            >>> print(f"Weekly cost: ${stats['total_cost']}")
        """
        # Get date range
        start_date = self._get_period_start_date(period)

        # Build query
        query = self.db.query(AgentCost).filter(AgentCost.user_id == user_id)

        if start_date:
            query = query.filter(AgentCost.created_at >= start_date)

        costs = query.all()

        # Calculate statistics
        total_cost = sum(float(c.cost_usd or 0) for c in costs)
        total_tokens = sum(c.tokens_input + c.tokens_output for c in costs)

        # Group by agent type
        by_agent = {}
        for cost in costs:
            agent_type = cost.agent_type
            by_agent[agent_type] = by_agent.get(agent_type, 0) + float(cost.cost_usd or 0)

        # Group by model
        by_model = {}
        for cost in costs:
            model = cost.model
            by_model[model] = by_model.get(model, 0) + float(cost.cost_usd or 0)

        return {
            "total_cost": round(total_cost, 6),
            "total_tokens": total_tokens,
            "by_agent": {k: round(v, 6) for k, v in by_agent.items()},
            "by_model": {k: round(v, 6) for k, v in by_model.items()},
            "usage_count": len(costs),
        }

    def get_total_costs(self, period: str = "month") -> Dict[str, Any]:
        """Get aggregated costs across all users.

        Args:
            period: Time period ('day', 'week', 'month', 'all')

        Returns:
            Dictionary with aggregated cost statistics:
            {
                "total_cost": 150.25,
                "total_tokens": 2500000,
                "by_agent": {"nutrition": 80.00, "chatbot": 50.25, ...},
                "by_model": {"gpt-4-turbo": 120.00, "gemini-pro": 30.25},
                "user_count": 50,
                "usage_count": 1200
            }

        Example:
            >>> stats = tracker.get_total_costs(period="month")
            >>> print(f"Monthly total: ${stats['total_cost']}")
        """
        # Get date range
        start_date = self._get_period_start_date(period)

        # Build query
        query = self.db.query(AgentCost)

        if start_date:
            query = query.filter(AgentCost.created_at >= start_date)

        costs = query.all()

        # Calculate statistics
        total_cost = sum(float(c.cost_usd or 0) for c in costs)
        total_tokens = sum(c.tokens_input + c.tokens_output for c in costs)
        unique_users = len(set(c.user_id for c in costs))

        # Group by agent type
        by_agent = {}
        for cost in costs:
            agent_type = cost.agent_type
            by_agent[agent_type] = by_agent.get(agent_type, 0) + float(cost.cost_usd or 0)

        # Group by model
        by_model = {}
        for cost in costs:
            model = cost.model
            by_model[model] = by_model.get(model, 0) + float(cost.cost_usd or 0)

        return {
            "total_cost": round(total_cost, 6),
            "total_tokens": total_tokens,
            "by_agent": {k: round(v, 6) for k, v in by_agent.items()},
            "by_model": {k: round(v, 6) for k, v in by_model.items()},
            "user_count": unique_users,
            "usage_count": len(costs),
        }

    @staticmethod
    def calculate_cost(model: str, tokens_input: int, tokens_output: int) -> float:
        """Calculate cost for given token usage.

        Args:
            model: LLM model name
            tokens_input: Number of input tokens
            tokens_output: Number of output tokens

        Returns:
            Cost in USD (rounded to 6 decimal places)

        Raises:
            ValueError: If model is not in PRICING table

        Example:
            >>> cost = CostTracker.calculate_cost("gpt-4-turbo", 1000, 500)
            >>> print(f"Cost: ${cost}")
            Cost: $0.025
        """
        if model not in CostTracker.PRICING:
            raise ValueError(
                f"Unknown model '{model}'. Available models: {list(CostTracker.PRICING.keys())}"
            )

        pricing = CostTracker.PRICING[model]

        # Calculate cost (pricing is per 1K tokens)
        input_cost = (tokens_input / 1000) * pricing["input"]
        output_cost = (tokens_output / 1000) * pricing["output"]
        total_cost = input_cost + output_cost

        return round(total_cost, 6)

    def _get_period_start_date(self, period: str) -> datetime | None:
        """Get the start date for a given period.

        Args:
            period: Time period ('day', 'week', 'month', 'all')

        Returns:
            Datetime object for the start of the period, or None for 'all'

        Raises:
            ValueError: If period is invalid
        """
        now = datetime.now(timezone.utc)

        if period == "day":
            return now - timedelta(days=1)
        elif period == "week":
            return now - timedelta(weeks=1)
        elif period == "month":
            return now - timedelta(days=30)
        elif period == "all":
            return None
        else:
            raise ValueError(
                f"Invalid period '{period}'. Must be one of: day, week, month, all"
            )
