"""OTPR (On-Time Production Rate) API endpoint."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from ..db_selector import db

router = APIRouter(prefix="/otpr", tags=["otpr"])


class OTPRMetrics(BaseModel):
    """On-Time Production Rate metrics from the database view."""
    otpr_last_30d: Optional[float] = None
    otpr_prev_30d: Optional[float] = None
    change_ppt: Optional[float] = None
    trend: Optional[str] = None
    error: Optional[str] = None


@router.get("/", response_model=OTPRMetrics)
async def get_otpr_metrics():
    """
    Get On-Time Production Rate metrics from the otpr view.

    Returns the current and previous 30-day OTPR percentages,
    the percentage point change, and trend indicator.

    This endpoint reads real-time metrics from the database view,
    so it will reflect any updates immediately.
    """
    try:
        # Query the OTPR view directly
        schema = os.getenv("DB_SCHEMA", "public")
        query = f"SELECT * FROM {schema}.otpr"
        result = db.execute_query(query)

        if result and len(result) > 0:
            row = result[0]
            return OTPRMetrics(
                otpr_last_30d=float(row.get('otpr_last_30d', 0)) if row.get('otpr_last_30d') is not None else None,
                otpr_prev_30d=float(row.get('otpr_prev_30d', 0)) if row.get('otpr_prev_30d') is not None else None,
                change_ppt=float(row.get('change_ppt', 0)) if row.get('change_ppt') is not None else None,
                trend=row.get('trend', '→')
            )
        else:
            # Return error if view is empty
            raise HTTPException(status_code=404, detail="No data available in OTPR view")

    except Exception as e:
        # Return error for any database issues
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")