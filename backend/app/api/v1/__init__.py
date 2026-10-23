"""
API v1 Router — aggregates all module endpoints.
"""

from fastapi import APIRouter
from app.api.v1 import (
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

router.include_router(upload.router, prefix="/upload", tags=["Module 1 · Upload"])
router.include_router(clauses.router, prefix="/extract-clauses", tags=["Module 2 · Clauses"])
router.include_router(risk.router, prefix="/risk-analysis", tags=["Module 3-5 · Risk"])
router.include_router(whatif.router, prefix="/what-if", tags=["Module 6 · What-If"])
router.include_router(obligations.router, prefix="/obligations", tags=["Module 8 · Obligations"])
router.include_router(compare.router, prefix="/compare", tags=["Module 9 · Compare"])
router.include_router(report.router, prefix="/report", tags=["Module 10 · Report"])
router.include_router(profile.router, prefix="/profile", tags=["User Profile"])
