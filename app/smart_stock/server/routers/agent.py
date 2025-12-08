"""SmartStock AI Agent router - runs the agent directly in FastAPI.

This router provides the AI assistant functionality using:
1. Databricks Foundation Model APIs for LLM
2. Direct database queries for real-time inventory data from Lakebase
3. Genie API for complex analytical queries
"""

import logging
import os
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from server.services.agent import get_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agent", tags=["agent"])


class ChatMessage(BaseModel):
    """Chat message model."""

    role: str
    content: str


class AgentChatRequest(BaseModel):
    """Agent chat request model."""

    messages: list[ChatMessage]


class AgentChatResponse(BaseModel):
    """Agent chat response model."""

    message_id: str
    content: str
    status: str
    error: Optional[str] = None
    tool_calls: Optional[list[dict]] = None


@router.post("/send-message", response_model=AgentChatResponse)
async def send_message(request: AgentChatRequest):
    """Send a message to the SmartStock AI agent.

    This endpoint processes messages using an agent that:
    1. Uses Databricks Foundation Model APIs for LLM
    2. Has tools for querying inventory data directly from Lakebase
    3. Can use Genie for complex analytical queries
    """
    try:
        # Get the agent
        agent = get_agent()

        # Convert messages to the format expected by the agent
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        # Process the chat
        logger.info(f"Processing {len(messages)} messages with SmartStock agent")
        result = await agent.chat(messages)

        # Generate a message ID
        message_id = f"agent-{uuid4().hex[:12]}"

        return AgentChatResponse(
            message_id=message_id,
            content=result.get("content", "No response generated."),
            status="completed" if "error" not in result else "error",
            error=result.get("error"),
            tool_calls=result.get("tool_calls", []),
        )

    except Exception as e:
        logger.error(f"Error in agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@router.get("/health")
async def health_check():
    """Check if the agent is configured and ready."""
    try:
        agent = get_agent()

        # Check configuration
        host = os.getenv("DATABRICKS_HOST")
        token = os.getenv("DATABRICKS_TOKEN")
        llm_endpoint = os.getenv("LLM_ENDPOINT", "databricks-meta-llama-3-3-70b-instruct")
        genie_space = os.getenv("GENIE_SPACE_ID")

        return {
            "status": "healthy",
            "agent_type": "smartstock",
            "configured": {
                "databricks_host": bool(host),
                "databricks_token": bool(token),
                "llm_endpoint": llm_endpoint,
                "genie_space": bool(genie_space),
                "database": agent.inventory_tools is not None,
            },
            "tools_available": [t["function"]["name"] for t in agent.tools] if agent.tools else [],
        }
    except Exception as e:
        return {"status": "error", "agent_type": "smartstock", "error": str(e)}


@router.get("/tools")
async def list_tools():
    """List all available tools for the agent."""
    try:
        agent = get_agent()

        tools = []
        for tool in agent.tools:
            func = tool.get("function", {})
            tools.append(
                {
                    "name": func.get("name"),
                    "description": func.get("description"),
                    "parameters": func.get("parameters", {}).get("properties", {}),
                }
            )

        return {"tools": tools, "count": len(tools)}
    except Exception as e:
        return {"error": str(e), "tools": []}
