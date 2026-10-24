"""
Contracts Analyze API (Core Specifications Endpoint)
POST /api/v1/contracts/analyze
GET  /api/v1/contracts/{contract_id}/analyze
Outputs structured JSON strictly conforming to ClauseGuard AI Refinement Brief.
"""

import os
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

from fastapi import APIRouter, UploadFile, File, Form, Body, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.core.config import settings
from app.core.database import get_db
from app.models.contract import (
    Contract, Clause, ClauseRisk, RiskReport,
    ClauseCategory, RiskLevel, UserRole
)
from app.schemas.contract import (
    ContractAnalyzeResponse, DocumentMetadataSchema,
    UserContextSchema, RiskSummarySchema,
    AnalyzedClauseSchema, InterconnectedRiskChainSchema,
    ContractAnalyzeRequest
)
from app.services.document_parser import DocumentParser
from app.services.nlp_service import NLPService, ROLE_ALIASES, CATEGORY_DEFINITIONS

router = APIRouter()


@router.post(
    "/analyze",
    response_model=ContractAnalyzeResponse,
    summary="Direct Contract Analysis Pipeline (Target Schema)",
)
async def analyze_contract(
    request: Request,
    file: Optional[UploadFile] = File(None, description="Optional PDF/DOCX file to analyze"),
    contract_id: Optional[str] = Form(None),
    role: Optional[str] = Form(None),
    text: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Unified end-to-end contract risk assessment endpoint.
    Accepts:
    1. Direct file upload (multipart/form-data)
    2. JSON payload with `contract_id` or raw `text` and `role`
    
    Returns structured JSON strictly conforming to the specification:
    - document (id, filename, total_pages, total_clauses, status)
    - user_context (active_role, risk_summary)
    - clauses (id, category, verbatim_text, page_number, simple_explanation, risk_level, legal_evidence, suggested_change, related_clause_ids)
    - interconnected_risk_chains (chain_id, description, sequence)
    """
    nlp = NLPService.get_instance()
    
    # Handle JSON body if content-type is application/json
    active_role = role or "Freelancer / Contractor"
    target_contract_id = contract_id
    contract_text = text
    filename = "Contract_Document.pdf"
    total_pages = 1
    doc_id = target_contract_id or f"doc_{uuid.uuid4().hex[:8]}"

    if request.headers.get("content-type", "").startswith("application/json"):
        try:
            body = await request.json()
            target_contract_id = body.get("contract_id", target_contract_id)
            contract_text = body.get("text", contract_text)
            active_role = body.get("role", active_role)
            filename = body.get("filename", filename)
        except Exception:
            pass

    # Normalize active role
    normalized_role = ROLE_ALIASES.get(active_role.lower().strip(), "Freelancer / Contractor")

    # CASE A: If file is uploaded directly
    if file is not None and file.filename:
        filename = file.filename
        content = await file.read()
        suffix = Path(filename).suffix.lower() or ".pdf"
        doc_id = f"doc_{uuid.uuid4().hex[:8]}"
        safe_path = Path(settings.UPLOAD_DIR) / f"{doc_id}{suffix}"
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        with open(safe_path, "wb") as f:
            f.write(content)

        parsed = DocumentParser.parse(str(safe_path), filename)
        contract_text = parsed["raw_text"]
        total_pages = parsed["page_count"]
        raw_segmented = parsed["clauses"]

        # Save contract to DB
        contract_record = Contract(
            id=doc_id,
            filename=f"{doc_id}{suffix}",
            original_name=filename,
            file_path=str(safe_path),
            file_type=suffix.lstrip("."),
            file_size=len(content),
            raw_text=contract_text,
            page_count=total_pages,
            extracted_clause_count=len(raw_segmented),
            status="NLP Pipeline Complete",
        )
        db.add(contract_record)
        await db.commit()

    # CASE B: If existing contract_id is supplied
    elif target_contract_id:
        result = await db.execute(select(Contract).where(Contract.id == target_contract_id))
        contract_record = result.scalar_one_or_none()
        if not contract_record:
            raise HTTPException(status_code=404, detail=f"Contract '{target_contract_id}' not found.")
        
        doc_id = contract_record.id
        filename = contract_record.original_name or contract_record.filename
        total_pages = contract_record.page_count or 1
        contract_text = contract_record.raw_text or ""
        
        # Segment from text
        raw_segmented = DocumentParser.segment_into_clauses(
            contract_text, [{"page_number": p, "text": ""} for p in range(1, total_pages + 1)]
        )

    # CASE C: Raw text provided directly
    elif contract_text:
        raw_segmented = DocumentParser.segment_into_clauses(
            contract_text, [{"page_number": 1, "text": contract_text}]
        )
        total_pages = max(1, len(contract_text) // 2500)
        contract_record = Contract(
            id=doc_id,
            filename=filename,
            original_name=filename,
            file_path="memory://direct_payload",
            file_type="txt",
            file_size=len(contract_text),
            raw_text=contract_text,
            page_count=total_pages,
            extracted_clause_count=len(raw_segmented),
            status="NLP Pipeline Complete",
        )
        db.add(contract_record)
        await db.commit()
    else:
        raise HTTPException(
            status_code=400,
            detail="Please provide a contract file, contract_id, or raw contract text to analyze.",
        )

    # Run NLP Pipeline across all 6 Core Modules
    analyzed_clauses: List[AnalyzedClauseSchema] = []
    clause_dicts_for_chains: List[Dict[str, Any]] = []

    for idx, c_raw in enumerate(raw_segmented):
        clause_id = c_raw.get("id") or f"CLAUSE-{(idx + 1):03d}"
        c_text = c_raw.get("cleaned_text") or c_raw.get("raw_text", "")
        page_num = c_raw.get("page_number", 1)

        # Module 1 & 2: Categorize into 8 Core Provisions
        category_full = nlp.classify_clause(c_text)
        
        # Short form for category display in target schema (e.g. "Termination", "Payment")
        defn = CATEGORY_DEFINITIONS.get(category_full, {})
        category_short = defn.get("short_name", category_full)

        # Module 2-5: Assessment, Plain Language, Statutory Grounding, Mitigation, Role Weighting
        assessment = nlp.assess_clause(
            text=c_text,
            category=category_full,
            user_role=normalized_role,
            page_number=page_num,
        )

        analyzed_clause = AnalyzedClauseSchema(
            id=clause_id,
            category=category_short,
            verbatim_text=c_text,
            page_number=page_num,
            simple_explanation=assessment["simple_explanation"],
            risk_level=assessment["risk_level"],
            legal_evidence=assessment["legal_evidence"],
            suggested_change=assessment["suggested_change"],
            related_clause_ids=[],
            role_reasoning=assessment["role_reasoning"],
            risk_score=assessment["risk_score"],
        )
        analyzed_clauses.append(analyzed_clause)
        
        clause_dicts_for_chains.append({
            "id": clause_id,
            "category": category_full,
            "raw_text": c_text,
            "cleaned_text": c_text,
            "risk_level": assessment["risk_level"],
        })

    # Module 6: Cross-Clause Relationship & Risk Chain Analysis
    raw_chains = nlp.detect_risk_chains(clause_dicts_for_chains)
    
    interconnected_risk_chains: List[InterconnectedRiskChainSchema] = []
    # Link related clauses based on detected chains
    chain_clause_ids: Set[str] = set()
    for ch in raw_chains:
        chain_schema = InterconnectedRiskChainSchema(
            chain_id=ch["chain_id"],
            description=ch["description"],
            sequence=ch["sequence"],
            link_basis=ch.get("link_basis", "Cross-Reference"),
        )
        interconnected_risk_chains.append(chain_schema)
        chain_clauses = ch.get("clauses", [])
        for cid in chain_clauses:
            chain_clause_ids.add(cid)

    # Populate related_clause_ids for clauses in chains
    for c in analyzed_clauses:
        if c.id in chain_clause_ids:
            for ch in raw_chains:
                if c.id in ch.get("clauses", []):
                    c.related_clause_ids = [other for other in ch.get("clauses", []) if other != c.id]
                    c.link_basis = ch.get("link_basis", "Cross-Reference")

    # Compute User Context Risk Summary
    risk_summary_data = nlp.compute_risk_summary(
        [{"risk_level": c.risk_level, "risk_score": c.risk_score} for c in analyzed_clauses]
    )

    # Display clean active role name for schema output
    display_role = "Freelancer" if "Freelancer" in normalized_role else normalized_role

    response = ContractAnalyzeResponse(
        document=DocumentMetadataSchema(
            id=doc_id,
            filename=filename,
            total_pages=total_pages,
            total_clauses=len(analyzed_clauses),
            status="NLP Pipeline Complete",
        ),
        user_context=UserContextSchema(
            active_role=display_role,
            risk_summary=RiskSummarySchema(
                overall_status=risk_summary_data["overall_status"],
                risk_exposure_index=risk_summary_data["risk_exposure_index"],
                critical_count=risk_summary_data["critical_count"],
                moderate_caution_count=risk_summary_data["moderate_caution_count"],
                low_risk_count=risk_summary_data["low_risk_count"],
            ),
        ),
        clauses=analyzed_clauses,
        interconnected_risk_chains=interconnected_risk_chains,
    )

    return response


@router.get(
    "/{contract_id}/analyze",
    response_model=ContractAnalyzeResponse,
    summary="Get Analyzed Contract by ID (Target Schema)",
)
async def get_analyzed_contract(
    contract_id: str,
    role: Optional[str] = "Freelancer / Contractor",
    db: AsyncSession = Depends(get_db),
):
    """Retrieve or re-compute the target analysis schema for an existing contract ID."""
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail=f"Contract '{contract_id}' not found.")

    nlp = NLPService.get_instance()
    normalized_role = ROLE_ALIASES.get(role.lower().strip(), "Freelancer / Contractor")

    raw_segmented = DocumentParser.segment_into_clauses(
        contract.raw_text or "",
        [{"page_number": p, "text": ""} for p in range(1, (contract.page_count or 1) + 1)],
    )

    analyzed_clauses: List[AnalyzedClauseSchema] = []
    clause_dicts_for_chains = []

    for idx, c_raw in enumerate(raw_segmented):
        clause_id = c_raw.get("id") or f"CLAUSE-{(idx + 1):03d}"
        c_text = c_raw.get("cleaned_text") or c_raw.get("raw_text", "")
        page_num = c_raw.get("page_number", 1)

        category_full = nlp.classify_clause(c_text)
        defn = CATEGORY_DEFINITIONS.get(category_full, {})
        category_short = defn.get("short_name", category_full)

        assessment = nlp.assess_clause(
            text=c_text,
            category=category_full,
            user_role=normalized_role,
            page_number=page_num,
        )

        analyzed_clause = AnalyzedClauseSchema(
            id=clause_id,
            category=category_short,
            verbatim_text=c_text,
            page_number=page_num,
            simple_explanation=assessment["simple_explanation"],
            risk_level=assessment["risk_level"],
            legal_evidence=assessment["legal_evidence"],
            suggested_change=assessment["suggested_change"],
            related_clause_ids=[],
            role_reasoning=assessment["role_reasoning"],
            risk_score=assessment["risk_score"],
        )
        analyzed_clauses.append(analyzed_clause)
        clause_dicts_for_chains.append({
            "id": clause_id,
            "category": category_full,
            "raw_text": c_text,
            "cleaned_text": c_text,
            "risk_level": assessment["risk_level"],
        })

    raw_chains = nlp.detect_risk_chains(clause_dicts_for_chains)
    interconnected_risk_chains = [
        InterconnectedRiskChainSchema(
            chain_id=ch["chain_id"],
            description=ch["description"],
            sequence=ch["sequence"],
            link_basis=ch.get("link_basis", "Cross-Reference"),
        )
        for ch in raw_chains
    ]

    chain_clause_ids = set()
    for ch in raw_chains:
        for cid in ch.get("clauses", []):
            chain_clause_ids.add(cid)

    for c in analyzed_clauses:
        if c.id in chain_clause_ids:
            for ch in raw_chains:
                if c.id in ch.get("clauses", []):
                    c.related_clause_ids = [other for other in ch.get("clauses", []) if other != c.id]
                    c.link_basis = ch.get("link_basis", "Cross-Reference")

    risk_summary_data = nlp.compute_risk_summary(
        [{"risk_level": c.risk_level, "risk_score": c.risk_score} for c in analyzed_clauses]
    )
    display_role = "Freelancer" if "Freelancer" in normalized_role else normalized_role

    return ContractAnalyzeResponse(
        document=DocumentMetadataSchema(
            id=contract.id,
            filename=contract.original_name or contract.filename,
            total_pages=contract.page_count or 1,
            total_clauses=len(analyzed_clauses),
            status="NLP Pipeline Complete",
        ),
        user_context=UserContextSchema(
            active_role=display_role,
            risk_summary=RiskSummarySchema(
                overall_status=risk_summary_data["overall_status"],
                risk_exposure_index=risk_summary_data["risk_exposure_index"],
                critical_count=risk_summary_data["critical_count"],
                moderate_caution_count=risk_summary_data["moderate_caution_count"],
                low_risk_count=risk_summary_data["low_risk_count"],
            ),
        ),
        clauses=analyzed_clauses,
        interconnected_risk_chains=interconnected_risk_chains,
    )
