"""
Module 9: Contract Comparison
POST /api/v1/compare
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.contract import Contract, Clause
from app.services.contract_comparer import ContractComparer
from app.schemas.contract import CompareRequest, CompareResponse, ClauseDiff

router = APIRouter()


@router.post("", response_model=CompareResponse, summary="Compare two contract versions")
async def compare_contracts(request: CompareRequest, db: AsyncSession = Depends(get_db)):
    """
    Compare two contracts side-by-side.
    
    - Matches clauses by category and text similarity.
    - Detects added, removed, and modified clauses.
    - Flags areas of increased risk in the newer version.
    """
    # Load both contracts
    for cid in [request.contract_id_a, request.contract_id_b]:
        result = await db.execute(select(Contract).where(Contract.id == cid))
        contract = result.scalar_one_or_none()
        if not contract:
            raise HTTPException(status_code=404, detail=f"Contract '{cid}' not found.")

    # Load clauses for both
    async def load_clauses(contract_id):
        res = await db.execute(
            select(Clause).where(Clause.contract_id == contract_id).order_by(Clause.index)
        )
        return res.scalars().all()

    clauses_a = await load_clauses(request.contract_id_a)
    clauses_b = await load_clauses(request.contract_id_b)

    if not clauses_a or not clauses_b:
        raise HTTPException(
            status_code=409,
            detail="Both contracts must have extracted clauses. Run POST /extract-clauses/{id} for each.",
        )

    # Get contract names
    name_a_res = await db.execute(select(Contract.original_name).where(Contract.id == request.contract_id_a))
    name_b_res = await db.execute(select(Contract.original_name).where(Contract.id == request.contract_id_b))
    name_a = name_a_res.scalar_one_or_none() or "Contract A"
    name_b = name_b_res.scalar_one_or_none() or "Contract B"

    # Convert to dicts
    def to_dict(clause):
        return {
            "id": clause.id,
            "cleaned_text": clause.cleaned_text or clause.raw_text,
            "category": clause.category.value if hasattr(clause.category, "value") else str(clause.category),
            "risk_level": clause.risk_level.value if hasattr(clause.risk_level, "value") else str(clause.risk_level),
        }

    dicts_a = [to_dict(c) for c in clauses_a]
    dicts_b = [to_dict(c) for c in clauses_b]

    comparison = ContractComparer.compare(dicts_a, dicts_b)

    diffs = [
        ClauseDiff(
            change_type=d["change_type"],
            category=d["category"],
            text_a=d.get("text_a"),
            text_b=d.get("text_b"),
            risk_delta=d["risk_delta"],
            risk_level_a=d.get("risk_level_a"),
            risk_level_b=d.get("risk_level_b"),
        )
        for d in comparison["diffs"]
    ]

    return CompareResponse(
        contract_a_name=name_a,
        contract_b_name=name_b,
        total_changes=comparison["total_changes"],
        added=comparison["added"],
        removed=comparison["removed"],
        modified=comparison["modified"],
        diffs=diffs,
        risk_summary=comparison["risk_summary"],
    )
