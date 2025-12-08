"""Agent chat router using Databricks Model Serving endpoint.

DEPRECATED: This is the old implementation that calls an external Model Serving endpoint.
The new implementation in agent.py runs the agent locally within FastAPI.
"""

import logging
import os
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agent-model-serving", tags=["agent-model-serving"])


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


def get_auth_config():
    """Get authentication configuration for Databricks Model Serving."""
    host = os.getenv("DATABRICKS_HOST", "").rstrip("/")
    token = os.getenv("DATABRICKS_TOKEN")
    endpoint_url = os.getenv("MODEL_SERVING_ENDPOINT")

    logger.info(
        f"Auth config - Host: {host[:30] if host else 'None'}..., "
        f"Token: {'Present' if token else 'Missing'}, "
        f"Endpoint: {'Present' if endpoint_url else 'Missing'}"
    )

    return host, token, endpoint_url


@router.post("/send-message", response_model=AgentChatResponse)
async def send_message(request: AgentChatRequest):
    """Send a message to the agent via Model Serving endpoint."""
    host, token, endpoint_url = get_auth_config()

    if not host or not token:
        logger.error(f"Missing auth - Host: {bool(host)}, Token: {bool(token)}")
        raise HTTPException(status_code=500, detail="Authentication not configured properly.")

    if not endpoint_url:
        logger.error("Missing Model Serving endpoint URL")
        raise HTTPException(
            status_code=500,
            detail="Model Serving endpoint not configured. Set MODEL_SERVING_ENDPOINT environment variable.",
        )

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    agent_messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

    payload = {"input": agent_messages}

    logger.info(f"Sending request to model serving endpoint: {endpoint_url}")

    async with httpx.AsyncClient(timeout=120.0, verify=False) as client:
        try:
            response = await client.post(endpoint_url, headers=headers, json=payload)

            if response.status_code != 200:
                logger.error(f"Model serving request failed: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Model serving request failed: {response.text}",
                )

            data = response.json()
            output_list = data.get("output", [])

            if not output_list:
                raise HTTPException(status_code=500, detail="No output received from model serving endpoint")

            first_message = output_list[0]
            message_id = first_message.get("id", "unknown")

            content_list = first_message.get("content", [])
            response_text = ""

            for content_item in content_list:
                if content_item.get("type") == "output_text":
                    response_text = content_item.get("text", "")
                    break

            if not response_text:
                response_text = "I received your message but couldn't generate a response."

            return AgentChatResponse(
                message_id=message_id, content=response_text, status="completed", error=None
            )

        except httpx.TimeoutException:
            logger.error("Request to model serving endpoint timed out")
            raise HTTPException(
                status_code=504, detail="Request timed out. The agent is taking too long to respond."
            )
        except httpx.RequestError as e:
            logger.error(f"Network error calling model serving endpoint: {str(e)}")
            raise HTTPException(status_code=503, detail=f"Failed to connect to model serving endpoint: {str(e)}")
        except Exception as e:
            logger.error(f"Error in agent API call: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to communicate with agent: {str(e)}")


@router.get("/health")
async def health_check():
    """Check if Agent Model Serving endpoint is configured and accessible."""
    try:
        host, token, endpoint_url = get_auth_config()
        configured = bool(endpoint_url) and bool(token) and bool(host)

        return {
            "status": "healthy",
            "configured": configured,
            "endpoint": endpoint_url[:50] + "..." if endpoint_url and len(endpoint_url) > 50 else endpoint_url,
            "host": host[:30] + "..." if host else None,
        }
    except Exception as e:
        return {"status": "error", "configured": False, "error": str(e)}

