"""
Module 10: Decision Support & Report Generation
POST /api/v1/report
GET  /api/v1/report/{contract_id}/download
"""

import os
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings
from app.models.contract import Contract, Clause, RiskReport, Obligation
from app.services.report_generator import ReportGenerator
from app.schemas.contract import ReportRequest, ReportResponse

router = APIRouter()


@router.post("", response_model=ReportResponse, summary="Generate full decision support report")
async def generate_report(request: ReportRequest, db: AsyncSession = Depends(get_db)):
    """
    Generate a comprehensive decision support report (JSON or PDF).
    
    Consolidates:
    - Executive summary and risk scores
    - All clause risk findings with evidence
    - Obligation/deadline table
    - Risk chains and recommendations
    """
    # Load data
    contract_res = await db.execute(select(Contract).where(Contract.id == request.contract_id))
    contract = contract_res.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail=f"Contract '{request.contract_id}' not found.")

    clause_res = await db.execute(
        select(Clause).where(Clause.contract_id == request.contract_id)
    )
    clauses = clause_res.scalars().all()

    risk_report_res = await db.execute(
        select(RiskReport).where(RiskReport.contract_id == request.contract_id)
    )
    risk_report = risk_report_res.scalar_one_or_none()

    obligation_res = await db.execute(
        select(Obligation).where(Obligation.contract_id == request.contract_id)
    )
    obligations = obligation_res.scalars().all()

    if not clauses:
        raise HTTPException(status_code=409, detail="No analysis found. Run extract-clauses and risk-analysis first.")

    # Refresh relationships
    for c in clauses:
        await db.refresh(c, ["risks"])

    risk_data = {}
    if risk_report:
        risk_data = {
            "overall_risk_level": risk_report.overall_risk_level.value if hasattr(risk_report.overall_risk_level, "value") else str(risk_report.overall_risk_level),
            "overall_risk_score": risk_report.overall_risk_score,
            "summary": risk_report.summary,
            "recommendations": risk_report.recommendations or [],
            "risk_chains": risk_report.clause_chains or [],
        }

    contract_dict = {
        "id": contract.id,
        "original_name": contract.original_name,
    }

    report_data = ReportGenerator.build_json_report(
        contract=contract_dict,
        clauses=list(clauses),
        risk_data=risk_data,
        obligations=list(obligations),
        user_role=request.user_role.value,
    )

    report_id = str(uuid.uuid4())
    generated_at = datetime.utcnow().isoformat()
    download_url = None

    if request.format == "pdf":
        pdf_dir = os.path.join(settings.UPLOAD_DIR, "reports")
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, f"{report_id}.pdf")

        success = ReportGenerator.generate_pdf_report(report_data, pdf_path)
        if success:
            download_url = f"/api/v1/report/{request.contract_id}/download?report_id={report_id}"
        else:
            download_url = None

    return ReportResponse(
        contract_id=request.contract_id,
        report_id=report_id,
        generated_at=generated_at,
        download_url=download_url,
        data=report_data if request.format == "json" else None,
    )


@router.get("/{contract_id}/download", summary="Download a PDF report")
async def download_report(contract_id: str, report_id: str):
    """Download a previously generated PDF report."""
    pdf_path = os.path.join(settings.UPLOAD_DIR, "reports", f"{report_id}.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Report not found or expired.")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"clauseguard_report_{contract_id[:8]}.pdf",
    )
