"""
Module 2: Plain-Language Clause Extraction, Classification & Statutory Evidence Grounding
POST /api/v1/extract-clauses/{contract_id}
GET  /api/v1/extract-clauses/{contract_id}
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.models.contract import Contract, Clause, ClauseRisk, ClauseCategory, RiskLevel, UserRole
from app.services.document_parser import DocumentParser
from app.services.nlp_service import NLPService, ROLE_ALIASES
from app.schemas.contract import ClauseExtractionResponse, ClauseSchema, ClauseRiskSchema
from loguru import logger

router = APIRouter()


@router.post("/{contract_id}", response_model=ClauseExtractionResponse, summary="Extract and classify clauses (Module 2)")
async def extract_clauses(
    contract_id: str,
    user_role: Optional[str] = Query("Freelancer / Contractor", description="User role for risk prioritization"),
    db: AsyncSession = Depends(get_db),
):
    """
    Extract and classify all clauses from a processed contract.
    - Segments into clauses preserving exact page numbers and headers.
    - Classifies every clause across the 8 mandatory legal categories.
    - Plain-language legalese translation (Module 2).
    - Statutory evidence grounding with legal doctrines (Module 3).
    - Mitigation counter-proposal generation (Module 4).
    - Role-aware dynamic weighting w_i(u) (Module 5).
    """
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()

    if not contract:
        raise HTTPException(status_code=404, detail=f"Contract '{contract_id}' not found.")

    if not contract.raw_text:
        raise HTTPException(
            status_code=422,
            detail="Contract text could not be extracted. Please ensure the document is not an image-only scan.",
        )

    # Clean existing clauses if re-extracting
    existing = await db.execute(select(Clause).where(Clause.contract_id == contract_id))
    for c in existing.scalars().all():
        await db.delete(c)
    await db.commit()

    # Re-segment
    pages = [{"page_number": p, "text": ""} for p in range(1, (contract.page_count or 1) + 1)]
    raw_clauses = DocumentParser.segment_into_clauses(contract.raw_text, pages)
    nlp = NLPService.get_instance()
    
    normalized_role = ROLE_ALIASES.get(user_role.lower().strip(), "Freelancer / Contractor")

    saved_clauses = []
    for c_data in raw_clauses:
        text = c_data["cleaned_text"] or c_data["raw_text"]
        page_num = c_data.get("page_number", 1)

        # 8 Core Provisions Classification
        category_full = nlp.classify_clause(text)

        # Integrated Assessment (Modules 2, 3, 4, 5)
        assessment = nlp.assess_clause(
            text=text,
            category=category_full,
            user_role=normalized_role,
            page_number=page_num,
        )

        embedding = nlp.embed_text(text[:512])

        clause = Clause(
            clause_code=c_data.get("id") or f"CLAUSE-{(len(saved_clauses) + 1):03d}",
            contract_id=contract_id,
            index=c_data["index"],
            raw_text=c_data["raw_text"],
            cleaned_text=c_data["cleaned_text"],
            category=category_full,
            risk_level=assessment["risk_level"],
            risk_score=assessment["risk_score"],
            risk_reasoning=assessment["risk_reasoning"],
            page_number=page_num,
            start_char=c_data.get("start_char"),
            end_char=c_data.get("end_char"),
            simple_explanation=assessment["simple_explanation"],
            legal_evidence=assessment["legal_evidence"],
            suggested_change=assessment["suggested_change"],
            role_reasoning=assessment["role_reasoning"],
            embedding=embedding,
            related_clause_ids=[],
        )
        db.add(clause)
        await db.flush()

        # Save individual risks for verbatim evidence grounding
        for r in assessment["risks"]:
            clause_risk = ClauseRisk(
                clause_id=clause.id,
                risk_type=r["risk_type"],
                description=r["simple_explanation"],
                evidence_text=r["evidence_text"],
                severity=r["severity"],
            )
            db.add(clause_risk)

        saved_clauses.append(clause)

    # Update contract extracted_clause_count
    contract.extracted_clause_count = len(saved_clauses)
    contract.status = "done"
    await db.commit()

    for c in saved_clauses:
        await db.refresh(c, ["risks"])

    clause_schemas = [
        ClauseSchema(
            id=c.clause_code or c.id,
            index=c.index,
            raw_text=c.raw_text,
            cleaned_text=c.cleaned_text,
            category=c.category,
            risk_level=c.risk_level,
            risk_score=c.risk_score,
            risk_reasoning=c.risk_reasoning,
            page_number=c.page_number,
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
        for c in saved_clauses
    ]

    return ClauseExtractionResponse(
        contract_id=contract_id,
        total_clauses=len(clause_schemas),
        clauses=clause_schemas,
    )


@router.get("/{contract_id}", response_model=ClauseExtractionResponse, summary="Get extracted clauses (Module 2)")
async def get_clauses(contract_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve previously extracted clauses for a contract."""
    result = await db.execute(
        select(Clause).where(Clause.contract_id == contract_id).order_by(Clause.index)
    )
    clauses = result.scalars().all()

    if not clauses:
        raise HTTPException(status_code=404, detail="No clauses found. Run POST /extract-clauses/{id} first.")

    for c in clauses:
        await db.refresh(c, ["risks"])

    clause_schemas = [
        ClauseSchema(
            id=c.clause_code or c.id,
            index=c.index,
            raw_text=c.raw_text,
            cleaned_text=c.cleaned_text,
            category=c.category,
            risk_level=c.risk_level,
            risk_score=c.risk_score,
            risk_reasoning=c.risk_reasoning,
            page_number=c.page_number,
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
        for c in clauses
    ]

    return ClauseExtractionResponse(
        contract_id=contract_id,
        total_clauses=len(clause_schemas),
        clauses=clause_schemas,
    )
