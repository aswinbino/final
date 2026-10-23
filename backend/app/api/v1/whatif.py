"""
Module 6: What-If Impact Analysis
POST /api/v1/what-if
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.contract import Clause
from app.services.nlp_service import NLPService
from app.schemas.contract import WhatIfRequest, WhatIfResponse, ClauseSchema

router = APIRouter()


@router.post("", response_model=WhatIfResponse, summary="What-if scenario analysis")
async def what_if_analysis(
    request: WhatIfRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Answer what-if scenario questions about the contract.
    
    Examples:
    - "What happens if I terminate early?"
    - "What if I miss a payment deadline?"
    - "What are the consequences of breaching confidentiality?"
    
    Returns:
    - Plain-language answer
    - Relevant clauses (with evidence)
    - List of potential consequences
    - Overall risk level for the scenario
    """
    # Load clauses
    result = await db.execute(
        select(Clause).where(Clause.contract_id == request.contract_id).order_by(Clause.index)
    )
    clauses = result.scalars().all()

    if not clauses:
        raise HTTPException(
            status_code=409,
            detail="No clauses found for this contract. Run POST /extract-clauses/{contract_id} first.",
        )

    for clause in clauses:
        await db.refresh(clause, ["risks"])

    # Convert to dicts for NLP service
    clause_dicts = [
        {
            "id": clause.id,
            "cleaned_text": clause.cleaned_text or clause.raw_text,
            "category": clause.category.value if hasattr(clause.category, "value") else str(clause.category),
            "risk_level": clause.risk_level.value if hasattr(clause.risk_level, "value") else str(clause.risk_level),
            "risks": [
                {
                    "risk_type": r.risk_type,
                    "description": r.description,
                    "evidence_text": r.evidence_text,
                    "severity": r.severity.value if hasattr(r.severity, "value") else str(r.severity),
                }
                for r in clause.risks
            ],
        }
        for clause in clauses
    ]

    nlp = NLPService.get_instance()
    result_data = nlp.answer_what_if(request.query, clause_dicts, request.user_role.value)

    # Build relevant clause schemas
    relevant_ids = {c.get("id") for c in result_data["relevant_clauses"]}
    relevant_schemas = []
    for clause in clauses:
        if clause.id in relevant_ids:
            relevant_schemas.append(ClauseSchema(
                id=clause.id,
                index=clause.index,
                raw_text=clause.raw_text,
                cleaned_text=clause.cleaned_text,
                category=clause.category,
                risk_level=clause.risk_level,
                risk_score=clause.risk_score,
                risk_reasoning=clause.risk_reasoning,
                page_number=clause.page_number,
                related_clause_ids=clause.related_clause_ids or [],
                risks=[{
                    "risk_type": r.risk_type,
                    "description": r.description,
                    "evidence_text": r.evidence_text,
                    "severity": r.severity,
                } for r in clause.risks],
            ))

    return WhatIfResponse(
        query=request.query,
        answer=result_data["answer"],
        relevant_clauses=relevant_schemas,
        consequences=result_data["consequences"],
        risk_level=result_data["risk_level"],
        evidence=result_data["evidence"],
    )
