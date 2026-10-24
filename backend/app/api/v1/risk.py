"""
Modules 3, 4, 5, 6: Risk Analysis, Personalized Context w_i(u), and Risk Chain Analysis
POST /api/v1/risk-analysis
GET  /api/v1/risk-analysis/{contract_id}
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.models.contract import Contract, Clause, RiskReport, ClauseRisk
from app.services.nlp_service import NLPService, ROLE_WEIGHT_MATRICES, ROLE_ALIASES
from app.schemas.contract import (
    RiskAnalysisRequest, RiskAnalysisResponse, ClauseSchema, RiskChain, ClauseRiskSchema
)
from loguru import logger

router = APIRouter()


@router.post("", response_model=RiskAnalysisResponse, summary="Run role-aware risk assessment & chain detection")
async def run_risk_analysis(
    request: RiskAnalysisRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Run role-aware personalized risk assessment across Modules 3-6:
    - Module 3: Grounded statutory evidence and legal principles.
    - Module 4: Actionable counter-proposals for High/Medium clauses.
    - Module 5: Dynamic weighting w_i(u) across roles (Freelancer vs Tenant vs Employee vs Business Owner).
    - Module 6: Cascading risk dependency chains.
    """
    contract_res = await db.execute(select(Contract).where(Contract.id == request.contract_id))
    contract = contract_res.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail=f"Contract '{request.contract_id}' not found.")

    clause_res = await db.execute(
        select(Clause).where(Clause.contract_id == request.contract_id).order_by(Clause.index)
    )
    clauses = clause_res.scalars().all()

    if not clauses:
        raise HTTPException(
            status_code=409,
            detail="No clauses found. Run POST /extract-clauses/{id} first.",
        )

    for c in clauses:
        await db.refresh(c, ["risks"])

    nlp = NLPService.get_instance()
    role_raw = request.user_role.value if hasattr(request.user_role, "value") else str(request.user_role)
    normalized_role = ROLE_ALIASES.get(role_raw.lower().strip(), "Freelancer / Contractor")

    # Re-evaluate all clauses under active user role
    high_risk, medium_risk, low_risk = [], [], []
    clause_dicts_for_chains = []

    for c in clauses:
        text = c.cleaned_text or c.raw_text
        assessment = nlp.assess_clause(
            text=text,
            category=c.category,
            user_role=normalized_role,
            page_number=c.page_number or 1,
        )

        # Update clause properties in DB
        c.risk_level = assessment["risk_level"]
        c.risk_score = assessment["risk_score"]
        c.risk_reasoning = assessment["risk_reasoning"]
        c.simple_explanation = assessment["simple_explanation"]
        c.legal_evidence = assessment["legal_evidence"]
        c.suggested_change = assessment["suggested_change"]
        c.role_reasoning = assessment["role_reasoning"]

        schema_item = ClauseSchema(
            id=c.clause_code or c.id,
            index=c.index,
            raw_text=c.raw_text,
            cleaned_text=c.cleaned_text,
            category=c.category,
            risk_level=assessment["risk_level"],
            risk_score=assessment["risk_score"],
            risk_reasoning=assessment["risk_reasoning"],
            page_number=c.page_number or 1,
            simple_explanation=assessment["simple_explanation"],
            legal_evidence=assessment["legal_evidence"],
            suggested_change=assessment["suggested_change"],
            role_reasoning=assessment["role_reasoning"],
            related_clause_ids=c.related_clause_ids or [],
            risks=[
                ClauseRiskSchema(
                    risk_type=r.risk_type or "",
                    description=r.description or "",
                    evidence_text=r.evidence_text or "",
                    severity=r.severity or "LOW",
                )
                for r in c.risks
            ],
        )

        if assessment["risk_level"] == "HIGH":
            high_risk.append(schema_item)
        elif assessment["risk_level"] == "MEDIUM":
            medium_risk.append(schema_item)
        else:
            low_risk.append(schema_item)

        clause_dicts_for_chains.append({
            "id": c.clause_code or c.id,
            "category": c.category,
            "raw_text": text,
            "cleaned_text": text,
            "risk_level": assessment["risk_level"],
        })

    # Module 6: Risk chain detection
    raw_chains = nlp.detect_risk_chains(clause_dicts_for_chains)
    risk_chains = [
        RiskChain(
            chain_id=ch["chain_id"],
            title=ch["title"],
            clauses=ch["clauses"],
            combined_risk=ch["combined_risk"],
            description=ch["description"],
            sequence=ch.get("sequence", []),
            link_basis=ch.get("link_basis", "Cross-Reference"),
        )
        for ch in raw_chains
    ]

    # Compute composite overall risk score
    all_scores = [c.risk_score for c in clauses]
    overall_score = sum(all_scores) / len(all_scores) if all_scores else 0.05
    
    if len(high_risk) >= 2 or overall_score >= 0.60:
        overall_level = "HIGH"
    elif len(high_risk) >= 1 or len(medium_risk) >= 2 or overall_score >= 0.30:
        overall_level = "MEDIUM"
    else:
        overall_level = "LOW"

    # Executive Summary & Recommendations
    summary = (
        f"As a {normalized_role}, this contract carries an overall {overall_level} risk profile. "
        f"Identified {len(high_risk)} critical risk clause(s), {len(medium_risk)} moderate caution(s), "
        f"and {len(low_risk)} low-risk standard clause(s) across {len(clauses)} analyzed provisions. "
        f"{f'{len(risk_chains)} cascading risk chain(s) detected with cross-clause trigger dependencies.' if risk_chains else 'No severe cascading traps identified.'}"
    )

    recommendations = []
    if high_risk:
        recommendations.append("Immediate counter-proposal required: Send rewritten clauses for all flagged HIGH RISK provisions.")
    if any(c.category == "Termination & Cancellation" for c in high_risk):
        recommendations.append("Equalize termination notice: Insist on mutual 30 days written notice with pay for work completed.")
    if any(c.category == "Intellectual Property Rights (IP)" for c in high_risk):
        recommendations.append("Retain background IP: Ensure deliverable ownership transfers only upon receipt of full payment.")
    if any(c.category == "Payment Terms & Fees" for c in high_risk):
        recommendations.append("Protect cash flow: Restrict fee withholding to disputed items and reduce net terms to Net 30.")
    if any(c.category == "Liability & Indemnification" for c in high_risk):
        recommendations.append("Insert liability ceiling: Limit total exposure to 1x contract fees and exclude consequential damages.")
    if risk_chains:
        recommendations.append("Sever interconnected trigger chains: Ensure delayed delivery does not automatically trigger total payment forfeiture.")
    if not recommendations:
        recommendations.append("Contract appears commercially balanced for the active role. Confirm deliverables and payment milestones.")

    # Save to RiskReport
    report_res = await db.execute(select(RiskReport).where(RiskReport.contract_id == request.contract_id))
    report = report_res.scalar_one_or_none()

    if report:
        report.overall_risk_score = round(overall_score, 3)
        report.overall_risk_level = overall_level
        report.summary = summary
        report.recommendations = recommendations
        report.role_used = normalized_role
        report.clause_chains = [ch.dict() for ch in risk_chains]
    else:
        report = RiskReport(
            contract_id=request.contract_id,
            overall_risk_score=round(overall_score, 3),
            overall_risk_level=overall_level,
            summary=summary,
            recommendations=recommendations,
            role_used=normalized_role,
            clause_chains=[ch.dict() for ch in risk_chains],
        )
        db.add(report)

    await db.commit()

    return RiskAnalysisResponse(
        contract_id=request.contract_id,
        overall_risk_score=round(overall_score, 3),
        overall_risk_level=overall_level,
        summary=summary,
        role_used=normalized_role,
        high_risk_clauses=high_risk,
        medium_risk_clauses=medium_risk,
        low_risk_clauses=low_risk,
        risk_chains=risk_chains,
        recommendations=recommendations[:8],
    )


@router.get("/{contract_id}", response_model=RiskAnalysisResponse, summary="Get saved risk analysis")
async def get_risk_analysis(contract_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve saved risk analysis report for a contract."""
    report_res = await db.execute(select(RiskReport).where(RiskReport.contract_id == contract_id))
    report = report_res.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="No risk analysis found. Run POST /risk-analysis first.")

    clause_res = await db.execute(select(Clause).where(Clause.contract_id == contract_id).order_by(Clause.index))
    clauses = clause_res.scalars().all()
    for c in clauses:
        await db.refresh(c, ["risks"])

    def to_schema(c):
        return ClauseSchema(
            id=c.clause_code or c.id,
            index=c.index,
            raw_text=c.raw_text,
            cleaned_text=c.cleaned_text,
            category=c.category,
            risk_level=c.risk_level,
            risk_score=c.risk_score,
            risk_reasoning=c.risk_reasoning,
            page_number=c.page_number or 1,
            simple_explanation=c.simple_explanation,
            legal_evidence=c.legal_evidence,
            suggested_change=c.suggested_change,
            role_reasoning=c.role_reasoning,
            related_clause_ids=c.related_clause_ids or [],
            risks=[
                ClauseRiskSchema(
                    risk_type=r.risk_type or "",
                    description=r.description or "",
                    evidence_text=r.evidence_text or "",
                    severity=r.severity or "LOW",
                )
                for r in c.risks
            ],
        )

    high_risk = [to_schema(c) for c in clauses if c.risk_level == "HIGH"]
    medium_risk = [to_schema(c) for c in clauses if c.risk_level == "MEDIUM"]
    low_risk = [to_schema(c) for c in clauses if c.risk_level == "LOW"]

    chains = [RiskChain(**ch) for ch in (report.clause_chains or [])]

    return RiskAnalysisResponse(
        contract_id=contract_id,
        overall_risk_score=report.overall_risk_score,
        overall_risk_level=report.overall_risk_level,
        summary=report.summary or "",
        role_used=report.role_used or "Freelancer / Contractor",
        high_risk_clauses=high_risk,
        medium_risk_clauses=medium_risk,
        low_risk_clauses=low_risk,
        risk_chains=chains,
        recommendations=report.recommendations or [],
    )
