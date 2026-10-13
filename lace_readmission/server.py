"""
FastAPI REST API Server for LACE-Readmission: 30-Day Hospital Readmission Risk & Medication Agent.
"""
from typing import Dict, Any
from .models import FrontierPayload
from .agents import LACEReadmissionCoordinator
from .lace_score import calculate_lace

coordinator = LACEReadmissionCoordinator()


def create_app():
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel, Field

        app = FastAPI(
            title="LACE-Readmission: 30-Day Hospital Readmission Risk & Medication Agent",
            description="Provides /api/lace for published point scoring; legacy /api/audit uses demonstration thresholds and does not reconcile medications.",
            version="2.0.0-FRONTIER",
        )

        class TaskRequest(BaseModel):
            task_id: str = "TASK-2026-001"
            target_identifier: str = "TARGET-BIO-KEY"
            primary_metric: float = 28.5
            secondary_metric: float = 14.2
            status_descriptor: str = "DISCORDANT_ANOMALY"
            is_critical_flag: bool = True
            attributes: Dict[str, Any] = {}

        class ChatRequest(BaseModel):
            query: str

        class LACERequest(BaseModel):
            length_of_stay_days: int = Field(ge=0, strict=True)
            acute_admission: bool = Field(strict=True)
            charlson_score: int = Field(ge=0, strict=True)
            ed_visits_6_months: int = Field(ge=0, strict=True)

        @app.post("/api/lace")
        def api_lace(req: LACERequest):
            return calculate_lace(
                req.length_of_stay_days, req.acute_admission,
                req.charlson_score, req.ed_visits_6_months
            ).to_dict()

        @app.get("/health")
        def health():
            return {"status": "HEALTHY", "system": "discharge-summary-cms-readmission", "domain": "Hospital Medicine", "version": "2.0.0-FRONTIER"}

        @app.post("/api/audit")
        def api_audit(req: TaskRequest):
            payload = FrontierPayload(
                task_id=req.task_id,
                target_identifier=req.target_identifier,
                primary_metric=req.primary_metric,
                secondary_metric=req.secondary_metric,
                status_descriptor=req.status_descriptor,
                is_critical_flag=req.is_critical_flag,
                attributes=req.attributes,
            )
            return coordinator.process(payload)

        @app.post("/api/chat")
        def api_chat(req: ChatRequest):
            return {"response": coordinator.query_supervisory_chat(req.query)}

        return app
    except ImportError:
        return None
