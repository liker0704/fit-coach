"""Multi-agent coordination service."""

import logging
from typing import Any, AsyncIterator, Dict, List, Optional

from sqlalchemy.orm import Session

from app.agents.agents import (
    ChatbotAgent,
    DailySummaryAgent,
    NutritionCoachAgent,
    WorkoutCoachAgent,
)
from app.models.user import User
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class AgentCoordinator:
    """Coordinator for orchestrating multiple AI agents."""

    @staticmethod
    async def coordinate_agents(
        db: Session,
        user: User,
        task: str,
        agents: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Coordinate multiple agents to complete a complex task.

        Args:
            db: Database session
            user: User instance
            task: High-level task description
            agents: List of agent types to use (e.g., ["nutrition", "workout", "daily_summary"])
            context: Optional context data

        Returns:
            Dictionary with coordinated results from all agents

        Example:
            # Coordinate nutrition and workout for comprehensive plan
            result = await AgentCoordinator.coordinate_agents(
                db=db,
                user=user,
                task="Create a comprehensive health improvement plan",
                agents=["nutrition", "workout"],
                context={"date": "2024-01-15"}
            )
        """
        try:
            logger.info(f"Coordinating agents {agents} for user {user.id}")

            results = {}
            context = context or {}

            # Execute each agent and collect results
            for agent_type in agents:
                try:
                    if agent_type == "nutrition":
                        agent = NutritionCoachAgent(db, user.id)
                        result = await agent.execute({
                            "question": f"Based on task: {task}",
                            "date": context.get("date"),
                            "conversation_history": []
                        })
                        results["nutrition"] = result

                    elif agent_type == "workout":
                        agent = WorkoutCoachAgent(db, user.id)
                        result = await agent.execute({
                            "question": f"Based on task: {task}",
                            "date": context.get("date"),
                            "conversation_history": []
                        })
                        results["workout"] = result

                    elif agent_type == "daily_summary":
                        agent = DailySummaryAgent(db, user.id)
                        result = await agent.execute({
                            "date": context.get("date")
                        })
                        results["daily_summary"] = result

                    elif agent_type == "chatbot":
                        agent = ChatbotAgent(db, user.id)
                        result = await agent.execute({
                            "message": f"Help with: {task}",
                            "conversation_history": []
                        })
                        results["chatbot"] = result

                except Exception as e:
                    logger.error(f"Error executing {agent_type} agent: {e}", exc_info=True)
                    results[agent_type] = {
                        "success": False,
                        "error": str(e)
                    }

            # Synthesize results from all agents
            synthesis = await AgentCoordinator._synthesize_results(
                task=task,
                agent_results=results
            )

            return {
                "success": True,
                "task": task,
                "agent_results": results,
                "synthesis": synthesis
            }

        except Exception as e:
            logger.error(f"Error in agent coordination: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    async def _synthesize_results(
        task: str,
        agent_results: Dict[str, Any]
    ) -> str:
        """Synthesize results from multiple agents into coherent response.

        Args:
            task: Original task description
            agent_results: Results from each agent

        Returns:
            Synthesized response combining all agent outputs
        """
        try:
            # Build synthesis prompt
            synthesis_prompt = f"Task: {task}\n\n"
            synthesis_prompt += "Agent Responses:\n\n"

            for agent_type, result in agent_results.items():
                if result.get("success"):
                    response = result.get("response", "No response")
                    synthesis_prompt += f"{agent_type.title()} Agent:\n{response}\n\n"

            synthesis_prompt += (
                "Please synthesize the above agent responses into a coherent, "
                "comprehensive plan that addresses the original task. "
                "Ensure the recommendations from different agents complement each other."
            )

            # Use LLM to synthesize
            llm = LLMService.get_llm()
            from langchain.schema import HumanMessage, SystemMessage

            messages = [
                SystemMessage(content="You are a health and fitness coordinator. Synthesize multiple agent responses into a comprehensive plan."),
                HumanMessage(content=synthesis_prompt)
            ]

            response = llm.invoke(messages)
            return response.content

        except Exception as e:
            logger.error(f"Error synthesizing results: {e}", exc_info=True)
            return "Error synthesizing agent responses"

    @staticmethod
    async def stream_coordinated_response(
        db: Session,
        user: User,
        task: str,
        agents: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[str]:
        """Stream coordinated response from multiple agents.

        Args:
            db: Database session
            user: User instance
            task: Task description
            agents: List of agent types
            context: Optional context

        Yields:
            Chunks of synthesized response
        """
        try:
            # First, collect results from all agents (non-streaming)
            results = {}
            context = context or {}

            for agent_type in agents:
                try:
                    if agent_type == "nutrition":
                        agent = NutritionCoachAgent(db, user.id)
                        result = await agent.execute({
                            "question": f"Based on task: {task}",
                            "date": context.get("date"),
                            "conversation_history": []
                        })
                        results["nutrition"] = result

                    elif agent_type == "workout":
                        agent = WorkoutCoachAgent(db, user.id)
                        result = await agent.execute({
                            "question": f"Based on task: {task}",
                            "date": context.get("date"),
                            "conversation_history": []
                        })
                        results["workout"] = result

                except Exception as e:
                    logger.error(f"Error executing {agent_type} agent: {e}")
                    results[agent_type] = {"success": False, "error": str(e)}

            # Build synthesis prompt
            synthesis_prompt = f"Task: {task}\n\n"
            synthesis_prompt += "Agent Responses:\n\n"

            for agent_type, result in results.items():
                if result.get("success"):
                    response = result.get("response", "No response")
                    synthesis_prompt += f"{agent_type.title()} Agent:\n{response}\n\n"

            synthesis_prompt += (
                "Please synthesize the above agent responses into a coherent, "
                "comprehensive plan that addresses the original task."
            )

            # Stream synthesis
            llm = LLMService.get_llm()
            from langchain.schema import HumanMessage, SystemMessage

            messages = [
                SystemMessage(content="You are a health and fitness coordinator."),
                HumanMessage(content=synthesis_prompt)
            ]

            async for chunk in llm.astream(messages):
                if hasattr(chunk, 'content') and chunk.content:
                    yield chunk.content

        except Exception as e:
            logger.error(f"Error in streamed coordination: {e}", exc_info=True)
            yield f"[ERROR: {str(e)}]"
