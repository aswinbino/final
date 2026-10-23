"""
Module 8: Obligation & Deadline Extraction
POST /api/v1/obligations/{contract_id}
GET  /api/v1/obligations/{contract_id}
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.contract import Clause, Obligation
from app.services.nlp_service import NLPService
from app.schemas.contract import ObligationResponse, ObligationSchema

router = APIRouter()


@router.post("/{contract_id}", response_model=ObligationResponse, summary="Extract obligations and deadlines")
async def extract_obligations(contract_id: str, db: AsyncSession = Depends(get_db)):
    """
    Extract all obligations, deadlines, and financial commitments from a contract.
    Returns a structured table of: payment timelines, notice periods, renewal deadlines, delivery obligations.
    """
    clause_result = await db.execute(
        select(Clause).where(Clause.contract_id == contract_id).order_by(Clause.index)
    )
    clauses = clause_result.scalars().all()

    if not clauses:
        raise HTTPException(status_code=409, detail="No clauses found. Run extract-clauses first.")

    clause_dicts = [
        {"id": c.id, "cleaned_text": c.cleaned_text or c.raw_text, "category": str(c.category)}
        for c in clauses
    ]

    nlp = NLPService.get_instance()
    raw_obligations = nlp.extract_obligations(clause_dicts)

    # Delete existing and save new
    existing = await db.execute(select(Obligation).where(Obligation.contract_id == contract_id))
    for ob in existing.scalars().all():
        await db.delete(ob)
    await db.commit()

    saved = []
    for ob_data in raw_obligations:
        ob = Obligation(
            id=ob_data["id"],
            contract_id=contract_id,
            obligation_type=ob_data["obligation_type"],
            party=ob_data["party"],
            description=ob_data["description"],
            deadline=ob_data.get("deadline"),
            amount=ob_data.get("amount"),
            evidence_text=ob_data["evidence_text"],
            clause_id=ob_data.get("clause_id"),
        )
        db.add(ob)
        saved.append(ob)

    await db.commit()

    return ObligationResponse(
        contract_id=contract_id,
        obligations=[
            ObligationSchema(
                id=ob.id,
                obligation_type=ob.obligation_type,
                party=ob.party,
                description=ob.description,
                deadline=ob.deadline,
                amount=ob.amount,
                evidence_text=ob.evidence_text,
            )
            for ob in saved
        ],
        total=len(saved),
    )


@router.get("/{contract_id}", response_model=ObligationResponse, summary="Get extracted obligations")
async def get_obligations(contract_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Obligation).where(Obligation.contract_id == contract_id))
    obligations = result.scalars().all()

    return ObligationResponse(
        contract_id=contract_id,
        obligations=[
            ObligationSchema(
                id=ob.id,
                obligation_type=ob.obligation_type,
                party=ob.party,
                description=ob.description,
                deadline=ob.deadline,
                amount=ob.amount,
                evidence_text=ob.evidence_text,
            )
            for ob in obligations
        ],
        total=len(obligations),
    )
