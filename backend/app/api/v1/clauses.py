"""
Modules 2 & 7: Clause Extraction, Classification, and Evidence Grounding
POST /api/v1/extract-clauses/{contract_id}
GET  /api/v1/extract-clauses/{contract_id}
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.contract import Contract, Clause, ClauseRisk, ClauseCategory, RiskLevel
from app.services.document_parser import DocumentParser
from app.services.nlp_service import NLPService
from app.schemas.contract import ClauseExtractionResponse, ClauseSchema, UserRole
from loguru import logger

router = APIRouter()


@router.post("/{contract_id}", response_model=ClauseExtractionResponse, summary="Extract and classify clauses")
async def extract_clauses(
    contract_id: str,
    user_role: UserRole = Query(UserRole.GENERAL, description="User role for risk prioritization"),
    db: AsyncSession = Depends(get_db),
):
    """
    Extract and classify all clauses from a processed contract.
    
    - Segments text into individual legal clauses.
    - Classifies each clause (Payment, Termination, Liability, etc.).
    - Runs initial risk assessment with verbatim evidence grounding.
    - Generates semantic embeddings for vector search.
    """
    # Load contract
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()

    if not contract:
        raise HTTPException(status_code=404, detail=f"Contract '{contract_id}' not found.")

    if contract.status != "done":
        raise HTTPException(
            status_code=409,
            detail=f"Contract is not ready (status: {contract.status}). Wait for processing to complete.",
        )

    if not contract.raw_text:
        raise HTTPException(status_code=422, detail="Contract text could not be extracted. The file may be corrupt or image-based.")

    # Delete existing clauses (re-extraction)
    existing = await db.execute(select(Clause).where(Clause.contract_id == contract_id))
    for clause in existing.scalars().all():
        await db.delete(clause)
    await db.commit()

    # Segment into clauses
    pages = [{"page_number": 1, "text": contract.raw_text}]
    if contract.page_count and contract.page_count > 1:
        # Best-effort page split for multi-page docs
        pages = _split_pages_heuristic(contract.raw_text, contract.page_count)

    raw_clauses = DocumentParser.segment_into_clauses(contract.raw_text, pages)
    nlp = NLPService.get_instance()

    saved_clauses = []
    for clause_data in raw_clauses:
        text = clause_data["cleaned_text"] or clause_data["raw_text"]

        # Module 2: Classify
        category_str = nlp.classify_clause(text)
        try:
            category = ClauseCategory(category_str)
        except ValueError:
            category = ClauseCategory.GENERAL

        # Module 3: Risk assessment
        risk_result = nlp.assess_clause_risk(text, category_str, user_role.value)
        try:
            risk_level = RiskLevel(risk_result["risk_level"])
        except ValueError:
            risk_level = RiskLevel.LOW

        # Module 7: Generate embedding (evidence grounding via vector)
        embedding = nlp.embed_text(text[:512])

        # Create Clause record
        clause = Clause(
            contract_id=contract_id,
            index=clause_data["index"],
            raw_text=clause_data["raw_text"],
            cleaned_text=clause_data["cleaned_text"],
            category=category,
            risk_level=risk_level,
            risk_score=risk_result["risk_score"],
            risk_reasoning=risk_result["risk_reasoning"],
            page_number=clause_data.get("page_number"),
            start_char=clause_data.get("start_char"),
            end_char=clause_data.get("end_char"),
            embedding=embedding,
        )
        db.add(clause)
        await db.flush()  # Get the clause ID

        # Create ClauseRisk records (verbatim evidence)
        for risk in risk_result["risks"]:
            try:
                risk_severity = RiskLevel(risk["severity"])
            except ValueError:
                risk_severity = RiskLevel.LOW

            clause_risk = ClauseRisk(
                clause_id=clause.id,
                risk_type=risk["risk_type"],
                description=risk["description"],
                evidence_text=risk["evidence_text"],  # Verbatim from contract
                severity=risk_severity,
            )
            db.add(clause_risk)

        saved_clauses.append(clause)

    await db.commit()

    # Refresh to load relationships
    for clause in saved_clauses:
        await db.refresh(clause, ["risks"])

    logger.info(f"Extracted {len(saved_clauses)} clauses from contract {contract_id}")

    # Build response
    clause_schemas = []
    for clause in saved_clauses:
        clause_schemas.append(ClauseSchema(
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

    return ClauseExtractionResponse(
        contract_id=contract_id,
        total_clauses=len(clause_schemas),
        clauses=clause_schemas,
    )


@router.get("/{contract_id}", response_model=ClauseExtractionResponse, summary="Get extracted clauses")
async def get_clauses(contract_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve previously extracted clauses for a contract."""
    result = await db.execute(
        select(Clause).where(Clause.contract_id == contract_id).order_by(Clause.index)
    )
    clauses = result.scalars().all()

    if not clauses:
        raise HTTPException(status_code=404, detail="No clauses found. Run POST first to extract clauses.")

    for clause in clauses:
        await db.refresh(clause, ["risks"])

    clause_schemas = [
        ClauseSchema(
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
        )
        for clause in clauses
    ]

    return ClauseExtractionResponse(
        contract_id=contract_id,
        total_clauses=len(clause_schemas),
        clauses=clause_schemas,
    )


def _split_pages_heuristic(raw_text: str, page_count: int) -> list:
    """Split raw text into approximate pages."""
    if not page_count or page_count <= 1:
        return [{"page_number": 1, "text": raw_text}]

    chars_per_page = max(1, len(raw_text) // page_count)
    pages = []
    for i in range(page_count):
        start = i * chars_per_page
        end = start + chars_per_page if i < page_count - 1 else len(raw_text)
        pages.append({"page_number": i + 1, "text": raw_text[start:end]})
    return pages
