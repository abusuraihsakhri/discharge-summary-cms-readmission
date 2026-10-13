"""
FastAPI REST API Server for Discharge Summary Cms Readmission.
"""
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor
from lace_readmission.lace_score import calculate_lace

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Discharge Summary Cms Readmission API",
    description="Research LACE index and experimental threshold checks; not CMS HWR or clinical decision support",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


class LACERequest(BaseModel):
    length_of_stay_days: int = Field(ge=0, strict=True)
    acute_admission: bool = Field(strict=True)
    charlson_score: int = Field(ge=0, strict=True)
    ed_visits_6_months: int = Field(ge=0, strict=True)


@app.post("/api/lace")
def api_lace(req: LACERequest):
    """Original LACE index points only; not the CMS HWR measure."""
    return calculate_lace(
        req.length_of_stay_days, req.acute_admission,
        req.charlson_score, req.ed_visits_6_months
    ).to_dict()


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "discharge-summary-cms-readmission", "domain": "Clinical & Biomedical AI", "standard": "Unvalidated demonstration rules", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
    except SecurityException:
        raise HTTPException(status_code=422, detail="Identifier pattern detected; use de-identified inputs")
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        raise HTTPException(status_code=422, detail="Identifier pattern detected; use de-identified inputs")


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
