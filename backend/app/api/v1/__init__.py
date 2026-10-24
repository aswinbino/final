"""
API v1 Router — aggregates all module endpoints.
Includes target contracts analyze endpoint and the 6 Core Modules.
"""

from fastapi import APIRouter
from app.api.v1 import (
    contracts,
    upload,
    clauses,
    risk,
    whatif,
    obligations,
    compare,
    report,
    profile,
)

router = APIRouter()

# Target API specification: POST /api/v1/contracts/analyze
router.include_router(contracts.router, prefix="/contracts", tags=["Target Schema · Contracts Analyze"])

# 6 Core Modules endpoints
router.include_router(upload.router, prefix="/upload", tags=["Module 1 · Upload & Ingestion"])
router.include_router(clauses.router, prefix="/extract-clauses", tags=["Module 2 · Plain-Language Extraction"])
router.include_router(risk.router, prefix="/risk-analysis", tags=["Module 3-5 · Personalized Risk & Mitigation"])
router.include_router(whatif.router, prefix="/what-if", tags=["Module 6 · Scenario Simulator"])
router.include_router(obligations.router, prefix="/obligations", tags=["Obligations & Deadlines"])
router.include_router(compare.router, prefix="/compare", tags=["Contract Comparison"])
router.include_router(report.router, prefix="/report", tags=["Decision Support Reports"])
router.include_router(profile.router, prefix="/profile", tags=["User Profile"])
