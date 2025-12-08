"""Databricks Jobs API endpoints for demo reset functionality."""

import os
import logging
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

# Demo reset job ID
DEMO_RESET_JOB_ID = 60972489698708


class JobRunResponse(BaseModel):
    """Response model for job run."""
    run_id: int
    job_id: int
    state: str
    life_cycle_state: str
    result_state: Optional[str] = None
    state_message: Optional[str] = None
    run_page_url: Optional[str] = None


class TriggerJobResponse(BaseModel):
    """Response model for triggering a job."""
    run_id: int
    job_id: int
    message: str
    run_page_url: Optional[str] = None


def get_databricks_client():
    """Get Databricks API client configuration."""
    host = os.getenv("DATABRICKS_HOST", "").rstrip("/")
    token = os.getenv("DATABRICKS_TOKEN")
    
    if not host or not token:
        raise HTTPException(
            status_code=500,
            detail="Databricks credentials not configured (DATABRICKS_HOST, DATABRICKS_TOKEN)"
        )
    
    return host, token


@router.get("/demo-reset/status", response_model=Optional[JobRunResponse])
async def get_demo_reset_status():
    """Get the status of the most recent demo reset job run."""
    try:
        host, token = get_databricks_client()
        headers = {"Authorization": f"Bearer {token}"}
        
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            # List recent runs for this job
            response = await client.get(
                f"{host}/api/2.1/jobs/runs/list",
                headers=headers,
                params={
                    "job_id": DEMO_RESET_JOB_ID,
                    "limit": 1,
                    "active_only": False
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to list job runs: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=response.text)
            
            data = response.json()
            runs = data.get("runs", [])
            
            if not runs:
                return None
            
            run = runs[0]
            state = run.get("state", {})
            
            return JobRunResponse(
                run_id=run.get("run_id"),
                job_id=run.get("job_id"),
                state=state.get("life_cycle_state", "UNKNOWN"),
                life_cycle_state=state.get("life_cycle_state", "UNKNOWN"),
                result_state=state.get("result_state"),
                state_message=state.get("state_message"),
                run_page_url=run.get("run_page_url")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/demo-reset/active-run", response_model=Optional[JobRunResponse])
async def get_active_demo_reset_run():
    """Check if there's an active (running/pending) demo reset job."""
    try:
        host, token = get_databricks_client()
        headers = {"Authorization": f"Bearer {token}"}
        
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            # List active runs for this job
            response = await client.get(
                f"{host}/api/2.1/jobs/runs/list",
                headers=headers,
                params={
                    "job_id": DEMO_RESET_JOB_ID,
                    "active_only": True,
                    "limit": 1
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to list active runs: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=response.text)
            
            data = response.json()
            runs = data.get("runs", [])
            
            if not runs:
                return None
            
            run = runs[0]
            state = run.get("state", {})
            
            return JobRunResponse(
                run_id=run.get("run_id"),
                job_id=run.get("job_id"),
                state=state.get("life_cycle_state", "UNKNOWN"),
                life_cycle_state=state.get("life_cycle_state", "UNKNOWN"),
                result_state=state.get("result_state"),
                state_message=state.get("state_message"),
                run_page_url=run.get("run_page_url")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking active runs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/demo-reset/trigger", response_model=TriggerJobResponse)
async def trigger_demo_reset():
    """Trigger a new demo reset job run."""
    try:
        host, token = get_databricks_client()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            # First check if there's already an active run
            active_response = await client.get(
                f"{host}/api/2.1/jobs/runs/list",
                headers=headers,
                params={
                    "job_id": DEMO_RESET_JOB_ID,
                    "active_only": True,
                    "limit": 1
                }
            )
            
            if active_response.status_code == 200:
                active_data = active_response.json()
                active_runs = active_data.get("runs", [])
                
                if active_runs:
                    run = active_runs[0]
                    state = run.get("state", {})
                    return TriggerJobResponse(
                        run_id=run.get("run_id"),
                        job_id=run.get("job_id"),
                        message="A demo reset is already in progress",
                        run_page_url=run.get("run_page_url")
                    )
            
            # Trigger a new run
            response = await client.post(
                f"{host}/api/2.1/jobs/run-now",
                headers=headers,
                json={"job_id": DEMO_RESET_JOB_ID}
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to trigger job: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=response.text)
            
            data = response.json()
            run_id = data.get("run_id")
            
            # Get the run details to get the URL
            run_response = await client.get(
                f"{host}/api/2.1/jobs/runs/get",
                headers=headers,
                params={"run_id": run_id}
            )
            
            run_page_url = None
            if run_response.status_code == 200:
                run_data = run_response.json()
                run_page_url = run_data.get("run_page_url")
            
            return TriggerJobResponse(
                run_id=run_id,
                job_id=DEMO_RESET_JOB_ID,
                message="Demo reset job triggered successfully",
                run_page_url=run_page_url
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering job: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/demo-reset/run/{run_id}", response_model=JobRunResponse)
async def get_run_status(run_id: int):
    """Get the status of a specific job run."""
    try:
        host, token = get_databricks_client()
        headers = {"Authorization": f"Bearer {token}"}
        
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            response = await client.get(
                f"{host}/api/2.1/jobs/runs/get",
                headers=headers,
                params={"run_id": run_id}
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get run status: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=response.text)
            
            run = response.json()
            state = run.get("state", {})
            
            return JobRunResponse(
                run_id=run.get("run_id"),
                job_id=run.get("job_id"),
                state=state.get("life_cycle_state", "UNKNOWN"),
                life_cycle_state=state.get("life_cycle_state", "UNKNOWN"),
                result_state=state.get("result_state"),
                state_message=state.get("state_message"),
                run_page_url=run.get("run_page_url")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting run status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

