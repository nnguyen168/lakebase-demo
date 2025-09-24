"""User router for Databricks user information."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class UserInfo(BaseModel):
  """Databricks user information."""

  userName: str
  displayName: str | None = None
  role: str | None = None
  active: bool
  emails: list[str] = []


class UserWorkspaceInfo(BaseModel):
  """User and workspace information."""

  user: UserInfo
  workspace: dict


@router.get('/me', response_model=UserInfo)
async def get_current_user():
  """Get current user information from Databricks."""
  # Mock user data for Elena Rodriguez
  return UserInfo(
    userName="elena.rodriguez@company.com",
    displayName="Elena Rodriguez",
    role="Senior Inventory Planner",
    active=True,
    emails=["elena.rodriguez@company.com"],
  )


@router.get('/me/workspace', response_model=UserWorkspaceInfo)
async def get_user_workspace_info():
  """Get user information along with workspace details."""
  # Mock user and workspace data for Elena Rodriguez
  return UserWorkspaceInfo(
    user=UserInfo(
      userName="elena.rodriguez@company.com",
      displayName="Elena Rodriguez",
      role="Senior Inventory Planner",
      active=True,
      emails=["elena.rodriguez@company.com"],
    ),
    workspace={
      "workspaceId": "1234567890",
      "workspaceName": "SmartStock Production",
      "deploymentName": "smartstock-prod",
      "region": "us-west-2"
    }
  )
