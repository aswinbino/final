"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


# ─── Enums ───────────────────────────────────────────────────────────────────

class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class ClauseCategory(str, Enum):
    PAYMENT = "Payment"
    TERMINATION = "Termination"
    LIABILITY = "Liability"
    CONFIDENTIALITY = "Confidentiality"
    IP = "IP"
    PENALTIES = "Penalties"
    RENEWAL = "Renewal"
    DISPUTE = "Dispute Resolution"
    OBLIGATIONS = "Obligations"
    GENERAL = "General"


class UserRole(str, Enum):
    FREELANCER = "Freelancer"
    TENANT = "Tenant"
    EMPLOYEE = "Employee"
    BUSINESS_OWNER = "Business Owner"
    VENDOR = "Vendor"
    GENERAL = "General"


# ─── Upload ──────────────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    contract_id: str
    filename: str
    file_type: str
    page_count: Optional[int]
    status: str
    message: str


# ─── Clause ──────────────────────────────────────────────────────────────────

class ClauseRiskSchema(BaseModel):
    risk_type: str
    description: str
    evidence_text: str
    severity: RiskLevel

    class Config:
        from_attributes = True


class ClauseSchema(BaseModel):
    id: str
    index: int
    raw_text: str
    cleaned_text: Optional[str]
    category: ClauseCategory
    risk_level: RiskLevel
    risk_score: float
    risk_reasoning: Optional[str]
    page_number: Optional[int]
    related_clause_ids: List[str] = []
    risks: List[ClauseRiskSchema] = []

    class Config:
        from_attributes = True


class ClauseExtractionResponse(BaseModel):
    contract_id: str
    total_clauses: int
    clauses: List[ClauseSchema]


# ─── Risk Analysis ───────────────────────────────────────────────────────────

class RiskChain(BaseModel):
    chain_id: str
    title: str
    clauses: List[str]  # Clause IDs
    combined_risk: RiskLevel
    description: str


class RiskAnalysisRequest(BaseModel):
    contract_id: str
    user_role: UserRole = UserRole.GENERAL


class RiskAnalysisResponse(BaseModel):
    contract_id: str
    overall_risk_score: float
    overall_risk_level: RiskLevel
    summary: str
    role_used: UserRole
    high_risk_clauses: List[ClauseSchema]
    medium_risk_clauses: List[ClauseSchema]
    low_risk_clauses: List[ClauseSchema]
    risk_chains: List[RiskChain]
    recommendations: List[str]


# ─── What-If ─────────────────────────────────────────────────────────────────

class WhatIfRequest(BaseModel):
    contract_id: str
    query: str = Field(..., min_length=5, max_length=500)
    user_role: UserRole = UserRole.GENERAL


class WhatIfResponse(BaseModel):
    query: str
    answer: str
    relevant_clauses: List[ClauseSchema]
    consequences: List[str]
    risk_level: RiskLevel
    evidence: List[Dict[str, Any]]


# ─── Obligations ─────────────────────────────────────────────────────────────

class ObligationSchema(BaseModel):
    id: str
    obligation_type: str
    party: str
    description: str
    deadline: Optional[str]
    amount: Optional[str]
    evidence_text: str

    class Config:
        from_attributes = True


class ObligationResponse(BaseModel):
    contract_id: str
    obligations: List[ObligationSchema]
    total: int


# ─── Comparison ──────────────────────────────────────────────────────────────

class CompareRequest(BaseModel):
    contract_id_a: str
    contract_id_b: str


class ClauseDiff(BaseModel):
    change_type: str  # added | removed | modified | unchanged
    category: ClauseCategory
    text_a: Optional[str]
    text_b: Optional[str]
    risk_delta: str  # increased | decreased | unchanged | new | removed
    risk_level_a: Optional[RiskLevel]
    risk_level_b: Optional[RiskLevel]


class CompareResponse(BaseModel):
    contract_a_name: str
    contract_b_name: str
    total_changes: int
    added: int
    removed: int
    modified: int
    diffs: List[ClauseDiff]
    risk_summary: str


# ─── Report ──────────────────────────────────────────────────────────────────

class ReportRequest(BaseModel):
    contract_id: str
    user_role: UserRole = UserRole.GENERAL
    format: str = "json"  # json | pdf


class ReportResponse(BaseModel):
    contract_id: str
    report_id: str
    generated_at: str
    download_url: Optional[str]
    data: Optional[Dict[str, Any]]


# ─── User Profile ────────────────────────────────────────────────────────────

class UserProfileCreate(BaseModel):
    name: str
    role: UserRole
    preferences: Dict[str, Any] = {}


class UserProfileResponse(BaseModel):
    id: str
    name: str
    role: UserRole
    preferences: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
