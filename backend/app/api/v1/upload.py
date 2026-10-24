"""
Module 1: Contract Upload & Document Ingestion Status API
POST /api/v1/upload
GET  /api/v1/upload/{contract_id}/status
"""

import os
import uuid
import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.models.contract import Contract
from app.services.document_parser import DocumentParser
from app.schemas.contract import UploadResponse
from loguru import logger

router = APIRouter()

ALLOWED_TYPES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/msword": ".doc",
    "text/plain": ".txt",
}


async def process_contract_background(contract_id: str, file_path: str, filename: str, db_url: str):
    """Background task: parse document and store text and metadata."""
    from app.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(Contract).where(Contract.id == contract_id))
            contract = result.scalar_one_or_none()
            if not contract:
                return

            contract.status = "processing"
            await db.commit()

            parsed = DocumentParser.parse(file_path, filename)
            contract.raw_text = parsed["raw_text"]
            contract.page_count = parsed["page_count"]
            contract.extracted_clause_count = parsed.get("extracted_clause_count", 0)
            contract.status = "done"
            await db.commit()

            logger.info(f"Contract {contract_id} processed: {parsed['page_count']} pages, {parsed.get('extracted_clause_count')} clauses.")
        except Exception as e:
            logger.error(f"Processing failed for contract {contract_id}: {e}")
            result = await db.execute(select(Contract).where(Contract.id == contract_id))
            contract = result.scalar_one_or_none()
            if contract:
                contract.status = "error"
                contract.error_message = str(e)
                await db.commit()


@router.post("", response_model=UploadResponse, summary="Upload a contract document (Module 1)")
async def upload_contract(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF or DOCX contract file"),
    db: AsyncSession = Depends(get_db),
):
    """
    Module 1: Upload a contract file (PDF or DOCX).
    - Validates file type and size.
    - Stores the file and queues background text extraction.
    - Returns document confirmation metadata.
    """
    if file.content_type not in ALLOWED_TYPES and not file.filename.lower().endswith((".pdf", ".docx", ".doc", ".txt")):
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: '{file.content_type}'. Please upload a PDF or DOCX contract document.",
        )

    content = await file.read()
    file_size = len(content)
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024

    if file_size > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({file_size / 1_048_576:.1f} MB). Maximum allowed is {settings.MAX_FILE_SIZE_MB} MB.",
        )

    if file_size == 0:
        raise HTTPException(status_code=400, detail="Uploaded contract file is empty.")

    suffix = Path(file.filename).suffix.lower() or ".pdf"
    contract_id = f"doc_{uuid.uuid4().hex[:8]}"
    safe_filename = f"{contract_id}{suffix}"
    upload_path = Path(settings.UPLOAD_DIR) / safe_filename
    upload_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(upload_path, "wb") as f:
            f.write(content)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Failed to write file to storage: {str(e)}")

    # Create Contract record
    contract = Contract(
        id=contract_id,
        filename=safe_filename,
        original_name=file.filename,
        file_path=str(upload_path),
        file_type=suffix.lstrip("."),
        file_size=file_size,
        status="uploaded",
        page_count=1,
        extracted_clause_count=0,
    )
    db.add(contract)
    await db.commit()

    # Queue background parsing
    background_tasks.add_task(
        process_contract_background,
        contract_id, str(upload_path), file.filename, settings.DATABASE_URL
    )

    logger.info(f"Contract uploaded: {file.filename} → {contract_id}")

    return UploadResponse(
        contract_id=contract_id,
        filename=file.filename,
        file_type=suffix.lstrip("."),
        page_count=1,
        total_clauses=0,
        status="uploaded",
        message="Contract uploaded successfully. Document ingestion started.",
    )


@router.get("/{contract_id}/status", summary="Check contract ingestion status (Module 1)")
async def get_contract_status(contract_id: str, db: AsyncSession = Depends(get_db)):
    """Check the ingestion status and confirmation metadata of an uploaded contract."""
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()

    if not contract:
        raise HTTPException(status_code=404, detail=f"Contract '{contract_id}' not found.")

    return {
        "contract_id": contract_id,
        "filename": contract.original_name,
        "total_pages": contract.page_count or 1,
        "clause_count": contract.extracted_clause_count or 0,
        "extracted_clause_count": contract.extracted_clause_count or 0,
        "status": contract.status,
        "processing_status": "NLP Pipeline Complete" if contract.status == "done" else contract.status,
        "file_type": contract.file_type,
        "error": contract.error_message,
    }
