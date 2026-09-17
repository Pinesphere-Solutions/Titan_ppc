
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.dashboard.schemas import DashboardSummary
from app.modules.dashboard.service import get_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary(db: Annotated[AsyncSession, Depends(get_db)]) -> DashboardSummary:
    summary = await get_dashboard_summary(db)
    return DashboardSummary(**summary)