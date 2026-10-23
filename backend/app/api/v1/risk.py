"""
Modules 3, 4, 5: Risk Analysis, Personalized Context, Risk Chain Detection
POST /api/v1/risk-analysis
GET  /api/v1/risk-analysis/{contract_id}
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.contract import Contract, Clause, RiskReport, ClauseRisk, RiskLevel as DBRiskLevel, UserRole as DBUserRole
from app.services.nlp_service import NLPService, ROLE_RISK_WEIGHTS
from app.schemas.contract import (
    RiskAnalysisRequest, RiskAnalysisResponse, RiskLevel, UserRole, ClauseSchema, RiskChain
)
from loguru import logger
import uuid

router = APIRouter()

RISK_ORDER = {"Low": 0, "Medium": 1, "High": 2}


@router.post("", response_model=RiskAnalysisResponse, summary="Run full risk analysis")
async def run_risk_analysis(
    request: RiskAnalysisRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Run full risk analysis on a contract.
    
    - Module 3: Assesses clause severity (Low/Medium/High).
    - Module 4: Re-weights risks based on user role.
    - Module 5: Detects risk dependency chains across clauses.
    - Generates recommendations and executive summary.
    """
    # Load contract
    contract_result = await db.execute(select(Contract).where(Contract.id == request.contract_id))
    contract = contract_result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail=f"Contract '{request.contract_id}' not found.")

    # Load clauses
    clause_result = await db.execute(
        select(Clause).where(Clause.contract_id == request.contract_id).order_by(Clause.index)
    )
    clauses = clause_result.scalars().all()

    if not clauses:
        raise HTTPException(
            status_code=409,
            detail="No clauses found. Run POST /extract-clauses/{contract_id} first.",
        )

    # Refresh risks
    for clause in clauses:
        await db.refresh(clause, ["risks"])

    nlp = NLPService.get_instance()
    role = request.user_role.value

    # Module 4: Re-weight by user role
    role_weights = ROLE_RISK_WEIGHTS.get(role, ROLE_RISK_WEIGHTS["General"])
    
    # Re-score clauses with role-adjusted weights
    high_risk, medium_risk, low_risk = [], [], []
    
    for clause in clauses:
        cat = clause.category.value if hasattr(clause.category, "value") else str(clause.category)
        weight = role_weights.get(cat, 1.0)
        adjusted_score = min(1.0, clause.risk_score * (weight / 1.5))

        # Determine final level after role adjustment
        if adjusted_score >= 0.65:
            final_level = "High"
        elif adjusted_score >= 0.35:
            final_level = "Medium"
        else:
            final_level = "Low"

        clause_schema = ClauseSchema(
            id=clause.id,
            index=clause.index,
            raw_text=clause.raw_text,
            cleaned_text=clause.cleaned_text,
            category=clause.category,
            risk_level=final_level,
            risk_score=round(adjusted_score, 3),
            risk_reasoning=clause.risk_reasoning,
            page_number=clause.page_number,
            related_clause_ids=clause.related_clause_ids or [],
            risks=[{
                "risk_type": r.risk_type,
                "description": r.description,
                "evidence_text": r.evidence_text,
                "severity": r.severity,
            } for r in clause.risks],
        )

        if final_level == "High":
            high_risk.append(clause_schema)
        elif final_level == "Medium":
            medium_risk.append(clause_schema)
        else:
            low_risk.append(clause_schema)

    # Module 5: Risk chain detection
    clause_dicts = [
        {"id": c.id, "category": c.category.value if hasattr(c.category, "value") else str(c.category)}
        for c in clauses
    ]
    raw_chains = nlp.detect_risk_chains(clause_dicts)
    
    risk_chains = [
        RiskChain(
            chain_id=ch["chain_id"],
            title=ch["title"],
            clauses=ch["clauses"],
            combined_risk=ch["combined_risk"],
            description=ch["description"],
        )
        for ch in raw_chains
    ]

    # Calculate overall score (weighted average)
    if clauses:
        all_scores = [c.risk_score for c in clauses]
        overall_score = sum(all_scores) / len(all_scores)
        # Boost for role
        max_cat_weight = max(role_weights.values(), default=1.0)
        overall_score = min(1.0, overall_score * (max_cat_weight / 1.5))
    else:
        overall_score = 0.0

    if overall_score >= 0.65:
        overall_level = "High"
    elif overall_score >= 0.35:
        overall_level = "Medium"
    else:
        overall_level = "Low"

    # Generate summary
    summary = _build_summary(
        overall_level, len(clauses), len(high_risk), len(medium_risk), len(low_risk), role, raw_chains
    )

    # Generate recommendations
    recommendations = _build_recommendations(high_risk, medium_risk, role, raw_chains)

    # Persist risk report
    existing_report = await db.execute(select(RiskReport).where(RiskReport.contract_id == request.contract_id))
    report = existing_report.scalar_one_or_none()

    try:
        overall_db_level = DBRiskLevel(overall_level)
    except ValueError:
        overall_db_level = DBRiskLevel.LOW

    try:
        role_db = DBUserRole(role)
    except ValueError:
        role_db = DBUserRole.GENERAL

    if report:
        report.overall_risk_score = round(overall_score, 3)
        report.overall_risk_level = overall_db_level
        report.summary = summary
        report.recommendations = recommendations
        report.role_used = role_db
        report.clause_chains = [ch.dict() for ch in risk_chains]
    else:
        report = RiskReport(
            contract_id=request.contract_id,
            overall_risk_score=round(overall_score, 3),
            overall_risk_level=overall_db_level,
            summary=summary,
            recommendations=recommendations,
            role_used=role_db,
            clause_chains=[ch.dict() for ch in risk_chains],
        )
        db.add(report)

    await db.commit()

    logger.info(
        f"Risk analysis complete for {request.contract_id}: "
        f"{overall_level} ({overall_score:.2f}) | {len(high_risk)}H {len(medium_risk)}M {len(low_risk)}L"
    )

    return RiskAnalysisResponse(
        contract_id=request.contract_id,
        overall_risk_score=round(overall_score, 3),
        overall_risk_level=overall_level,
        summary=summary,
        role_used=request.user_role,
        high_risk_clauses=high_risk,
        medium_risk_clauses=medium_risk,
        low_risk_clauses=low_risk,
        risk_chains=risk_chains,
        recommendations=recommendations,
    )


@router.get("/{contract_id}", response_model=RiskAnalysisResponse, summary="Get saved risk analysis")
async def get_risk_analysis(contract_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve previously computed risk analysis for a contract."""
    report_result = await db.execute(select(RiskReport).where(RiskReport.contract_id == contract_id))
    report = report_result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="No risk analysis found. Run POST /risk-analysis first.",
        )

    clause_result = await db.execute(
        select(Clause).where(Clause.contract_id == contract_id)
    )
    clauses = clause_result.scalars().all()
    for c in clauses:
        await db.refresh(c, ["risks"])

    high_risk = [c for c in clauses if c.risk_level.value == "High"]
    medium_risk = [c for c in clauses if c.risk_level.value == "Medium"]
    low_risk = [c for c in clauses if c.risk_level.value == "Low"]

    def to_schema(clause):
        return ClauseSchema(
            id=clause.id, index=clause.index, raw_text=clause.raw_text,
            cleaned_text=clause.cleaned_text, category=clause.category,
            risk_level=clause.risk_level, risk_score=clause.risk_score,
            risk_reasoning=clause.risk_reasoning, page_number=clause.page_number,
            related_clause_ids=clause.related_clause_ids or [],
            risks=[{"risk_type": r.risk_type, "description": r.description,
                    "evidence_text": r.evidence_text, "severity": r.severity} for r in clause.risks],
        )

    return RiskAnalysisResponse(
        contract_id=contract_id,
        overall_risk_score=report.overall_risk_score,
        overall_risk_level=report.overall_risk_level,
        summary=report.summary,
        role_used=report.role_used or UserRole.GENERAL,
        high_risk_clauses=[to_schema(c) for c in high_risk],
        medium_risk_clauses=[to_schema(c) for c in medium_risk],
        low_risk_clauses=[to_schema(c) for c in low_risk],
        risk_chains=[RiskChain(**ch) for ch in (report.clause_chains or [])],
        recommendations=report.recommendations or [],
    )


def _build_summary(level, total, high, medium, low, role, chains):
    chain_note = f" {len(chains)} risk dependency chain(s) detected." if chains else ""
    return (
        f"As a {role}, this contract presents {level.upper()} overall risk. "
        f"Analyzed {total} clauses: {high} high-risk, {medium} medium-risk, {low} low-risk.{chain_note} "
        f"{'Immediate legal review recommended.' if level == 'High' else 'Review flagged clauses before signing.' if level == 'Medium' else 'Contract appears relatively standard for this role.'}"
    )


def _build_recommendations(high_clauses, medium_clauses, role, chains):
    recs = []
    cats_high = set(c.category.value if hasattr(c.category, "value") else str(c.category) for c in high_clauses)

    if "Termination" in cats_high:
        recs.append("Negotiate a minimum 30-day written notice requirement before termination.")
    if "Liability" in cats_high:
        recs.append("Request a liability cap clause limiting total exposure to contract value.")
    if "IP" in cats_high:
        recs.append("Clarify IP ownership clauses — ensure work product rights are explicitly defined.")
    if "Payment" in cats_high:
        recs.append("Negotiate payment terms to Net 30 or better; include late payment interest protections.")
    if "Penalties" in cats_high:
        recs.append("Review and negotiate penalty clauses — request caps and cure periods for breaches.")
    if chains:
        recs.append("Address risk chains: linked clause dependencies may amplify individual risks significantly.")
    if role == "Freelancer":
        recs.append("As a freelancer, ensure IP rights revert if payment is not received.")
    if role == "Employee":
        recs.append("Review non-compete scope — overly broad clauses may be unenforceable in many jurisdictions.")
    if not recs:
        recs.append("Contract appears relatively standard. Verify all obligations and deadlines are clearly defined.")

    return recs[:8]
