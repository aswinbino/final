"""
Module 1: Contract Upload & Document Processing API
POST /api/v1/upload
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
    """Background task: parse document and store text."""
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
            contract.status = "done"
            await db.commit()

            logger.info(f"Contract {contract_id} processed: {parsed['page_count']} pages")
        except Exception as e:
            logger.error(f"Processing failed for contract {contract_id}: {e}")
            result = await db.execute(select(Contract).where(Contract.id == contract_id))
            contract = result.scalar_one_or_none()
            if contract:
                contract.status = "error"
                contract.error_message = str(e)
                await db.commit()


@router.post("", response_model=UploadResponse, summary="Upload a contract document")
async def upload_contract(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF or DOCX contract file"),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a contract file (PDF or DOCX).
    - Validates file type and size.
    - Stores the file and queues background text extraction.
    - Returns a contract_id for subsequent API calls.
    """
    # Validate content type
    if file.content_type not in ALLOWED_TYPES and not file.filename.lower().endswith((".pdf", ".docx", ".doc", ".txt")):
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: '{file.content_type}'. Please upload a PDF, DOCX, or TXT file.",
        )

    # Read and validate size
    content = await file.read()
    file_size = len(content)
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024

    if file_size > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({file_size / 1_048_576:.1f} MB). Maximum is {settings.MAX_FILE_SIZE_MB} MB.",
        )

    if file_size == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Determine extension
    suffix = Path(file.filename).suffix.lower() or ".pdf"
    contract_id = str(uuid.uuid4())
    safe_filename = f"{contract_id}{suffix}"
    upload_path = Path(settings.UPLOAD_DIR) / safe_filename
    upload_path.parent.mkdir(parents=True, exist_ok=True)

    # Save file
    try:
        with open(upload_path, "wb") as f:
            f.write(content)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Create DB record
    contract = Contract(
        id=contract_id,
        filename=safe_filename,
        original_name=file.filename,
        file_path=str(upload_path),
        file_type=suffix.lstrip("."),
        file_size=file_size,
        status="uploaded",
    )
    db.add(contract)
    await db.commit()

    # Queue background processing
    background_tasks.add_task(
        process_contract_background,
        contract_id, str(upload_path), file.filename, settings.DATABASE_URL
    )

    logger.info(f"Contract uploaded: {file.filename} → {contract_id}")

    return UploadResponse(
        contract_id=contract_id,
        filename=file.filename,
        file_type=suffix.lstrip("."),
        page_count=None,
        status="uploaded",
        message="Contract uploaded successfully. Processing started in background.",
    )


@router.get("/{contract_id}/status", summary="Check contract processing status")
async def get_contract_status(contract_id: str, db: AsyncSession = Depends(get_db)):
    """Check the processing status of an uploaded contract."""
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()

    if not contract:
        raise HTTPException(status_code=404, detail=f"Contract '{contract_id}' not found.")

    return {
        "contract_id": contract_id,
        "status": contract.status,
        "filename": contract.original_name,
        "page_count": contract.page_count,
        "error": contract.error_message,
    }
