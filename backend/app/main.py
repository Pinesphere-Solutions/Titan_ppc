"""App factory — registers routers and middleware. See architecture doc
Section 5.2."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware.error_handlers import register_error_handlers
from app.modules.auth.router import router as auth_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.dc_verification.router import router as dc_verification_router
from app.modules.deviations.router import router as deviations_router
from app.modules.masters.router import router as masters_router
from app.modules.physical_verification.router import router as physical_verification_router
from app.modules.ppc_collection.router import router as ppc_collection_router
from app.modules.qa_inspection.router import router as qa_inspection_router
from app.modules.qc_acknowledgement.router import router as qc_acknowledgement_router
from app.modules.receiving.router import router as receiving_router
from app.modules.reports.router import router as reports_router
from app.modules.sap_outward.router import router as sap_outward_router
from app.modules.sap_processing.router import router as sap_processing_router
from app.modules.settings.router import router as settings_router
from app.modules.storage.router import router as storage_router
from app.modules.zqmtl1.router import router as zqmtl1_router
from app.workers.scheduler import start_scheduler, stop_scheduler

ALL_ROUTERS = [
    auth_router,
    dashboard_router,
    sap_outward_router,
    receiving_router,
    dc_verification_router,
    physical_verification_router,
    deviations_router,
    qc_acknowledgement_router,
    sap_processing_router,
    ppc_collection_router,
    qa_inspection_router,
    zqmtl1_router,
    storage_router,
    reports_router,
    masters_router,
    settings_router,
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


def create_app() -> FastAPI:
    app = FastAPI(title="PPC CBE Tracking Application API", lifespan=lifespan)

    # CORS — restricted to known frontend origin(s) in production.
    # See architecture doc Section 7.3.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)

    for router in ALL_ROUTERS:
        app.include_router(router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    async def ready() -> dict[str, str]:
        # TODO: check DB connectivity before reporting ready.
        return {"status": "ready"}

    return app


app = create_app()
