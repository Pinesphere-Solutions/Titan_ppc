"""APScheduler setup — the one genuinely time-based job (periodic SAP
dispatch-data sync) that plain BackgroundTasks can't cover, since it must
run without a triggering request. See architecture doc Section 5.2."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.workers.jobs import kpi_refresh_job, sap_sync_job

scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    scheduler.add_job(sap_sync_job, "interval", minutes=15, id="sap_sync_job", replace_existing=True)
    scheduler.add_job(kpi_refresh_job, "interval", seconds=60, id="kpi_refresh_job", replace_existing=True)
    scheduler.start()


def stop_scheduler() -> None:
    scheduler.shutdown(wait=False)
