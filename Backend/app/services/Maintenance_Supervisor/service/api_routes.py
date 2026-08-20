"""
api_routes.py

FastAPI API Router Endpoints for the Autonomous Maintenance Supervisor Agent.

Endpoints:
- POST `/api/v1/supervisor/predict`: Single-sample streaming prediction.
- POST `/api/v1/supervisor/predict-batch`: High-throughput batch inference.
- GET  `/api/v1/supervisor/health`: Production health probe.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Final

try:
    from fastapi import APIRouter, HTTPException, status
    HAS_FASTAPI = True
except ImportError:
    APIRouter = object
    HAS_FASTAPI = False

# Bootstrap
_CURRENT_FILE: Final[Path] = Path(__file__).resolve()
_BACKEND_ROOT: Final[Path] = _CURRENT_FILE.parents[4]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.services.Maintenance_Supervisor.service.schemas import (
    TelemetryInputSchema,
    SupervisorDecisionResponseSchema,
    BatchInferenceRequestSchema,
    BatchInferenceResponseSchema,
)
from app.services.Maintenance_Supervisor.service.supervisor_service import MaintenanceSupervisorService

if HAS_FASTAPI:
    router = APIRouter(prefix="/api/v1/supervisor", tags=["Maintenance Supervisor Agent"])

    @router.post("/predict", response_model=SupervisorDecisionResponseSchema)
    def predict_supervisor_decision(telemetry: TelemetryInputSchema):
        try:
            service = MaintenanceSupervisorService.get_instance()
            return service.predict_single(telemetry)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    @router.post("/predict-batch", response_model=BatchInferenceResponseSchema)
    def predict_supervisor_batch(request: BatchInferenceRequestSchema):
        try:
            service = MaintenanceSupervisorService.get_instance()
            decisions = [service.predict_single(rec) for rec in request.records]
            return BatchInferenceResponseSchema(total_processed=len(decisions), decisions=decisions)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    @router.get("/health")
    def health_check():
        return {"status": "healthy", "service": "Maintenance Supervisor Agent", "version": "1.0.0"}
else:
    router = None
