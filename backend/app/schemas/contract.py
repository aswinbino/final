"""
Pydantic schemas for request/response validation in ClauseGuard AI.
Includes models for Target API Schema (POST /api/v1/contracts/analyze) and all 6 Core Modules.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime


# ─── Enums ───────────────────────────────────────────────────────────────────

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ClauseCategory(str, Enum):
    PAYMENT = "Payment Terms & Fees"
    TERMINATION = "Termination & Cancellation"
    LIABILITY = "Liability & Indemnification"
    CONFIDENTIALITY = "Confidentiality & Non-Disclosure"
    IP = "Intellectual Property Rights (IP)"
    PENALTIES = "Penalties & Liquidated Damages"
    RENEWAL = "Renewal Terms & Extensions"
    DISPUTE_RESOLUTION = "Dispute Resolution & Governing Law"
    GENERAL = "General Commercial Provisions"


class UserRole(str, Enum):
    FREELANCER = "Freelancer / Contractor"
    TENANT = "Tenant"
    EMPLOYEE = "Employee"
    BUSINESS_OWNER = "Client / Small Business Owner"
    GENERAL = "General"


# ─── Target API Schema: POST /api/v1/contracts/analyze ─────────────────────────

class DocumentMetadataSchema(BaseModel):
    id: str
    filename: str
    total_pages: int
    total_clauses: int
    status: str = "NLP Pipeline Complete"


class RiskSummarySchema(BaseModel):
    overall_status: str  # e.g. "LOW", "MEDIUM", "HIGH"
    risk_exposure_index: str  # e.g. "6%", "42%"
    critical_count: int
    moderate_caution_count: int
    low_risk_count: int


class UserContextSchema(BaseModel):
    active_role: str
    risk_summary: RiskSummarySchema


class AnalyzedClauseSchema(BaseModel):
    id: str  # e.g. "CLAUSE-005"
    category: str
    verbatim_text: str
    page_number: int
    simple_explanation: str
    risk_level: str  # "HIGH", "MEDIUM", "LOW"
    legal_evidence: str
    suggested_change: str
    related_clause_ids: List[str] = []
    # Additional enriched fields for advanced UI inspection
    role_reasoning: Optional[str] = None
    link_basis: Optional[str] = None
    risk_score: Optional[float] = None


class InterconnectedRiskChainSchema(BaseModel):
    chain_id: str
    description: str
    sequence: List[str]
    link_basis: Optional[str] = None  # "Cross-Reference", "Shared Defined Term", "Semantic Candidate"


class ContractAnalyzeResponse(BaseModel):
    document: DocumentMetadataSchema
    user_context: UserContextSchema
    clauses: List[AnalyzedClauseSchema]
    interconnected_risk_chains: List[InterconnectedRiskChainSchema]


class ContractAnalyzeRequest(BaseModel):
    contract_id: Optional[str] = None
    text: Optional[str] = None
    filename: Optional[str] = "Contract_Document.pdf"
    role: Optional[str] = "Freelancer / Contractor"


# ─── Upload Schema ────────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    contract_id: str
    filename: str
    file_type: str
    page_count: Optional[int] = 1
    total_clauses: Optional[int] = 0
    status: str
    message: str


# ─── Module 2 & 7: Clause Schemas ─────────────────────────────────────────────

class ClauseRiskSchema(BaseModel):
    risk_type: str
    description: str
    evidence_text: str
    severity: str

    class Config:
        from_attributes = True


class ClauseSchema(BaseModel):
    id: str
    index: int
    raw_text: str
    cleaned_text: Optional[str] = None
    category: str
    risk_level: str
    risk_score: float
    risk_reasoning: Optional[str] = None
    page_number: Optional[int] = 1
    simple_explanation: Optional[str] = None
    legal_evidence: Optional[str] = None
    suggested_change: Optional[str] = None
    role_reasoning: Optional[str] = None
    link_basis: Optional[str] = None
    related_clause_ids: List[str] = []
    risks: List[ClauseRiskSchema] = []

    class Config:
        from_attributes = True


class ClauseExtractionResponse(BaseModel):
    contract_id: str
    total_clauses: int
    clauses: List[ClauseSchema]


# ─── Modules 3, 4, 5: Risk Analysis Schemas ────────────────────────────────────

class RiskChain(BaseModel):
    chain_id: str
    title: str
    clauses: List[str]  # Clause IDs
    combined_risk: str
    description: str
    sequence: Optional[List[str]] = None
    link_basis: Optional[str] = None


class RiskAnalysisRequest(BaseModel):
    contract_id: str
    user_role: Union[UserRole, str] = UserRole.FREELANCER


class RiskAnalysisResponse(BaseModel):
    contract_id: str
    overall_risk_score: float
    overall_risk_level: str
    summary: str
    role_used: str
    high_risk_clauses: List[ClauseSchema]
    medium_risk_clauses: List[ClauseSchema]
    low_risk_clauses: List[ClauseSchema]
    risk_chains: List[RiskChain]
    recommendations: List[str]


# ─── Module 6: What-If ─────────────────────────────────────────────────────────

class WhatIfRequest(BaseModel):
    contract_id: str
    query: str = Field(..., min_length=3, max_length=500)
    user_role: Union[UserRole, str] = UserRole.FREELANCER


class WhatIfResponse(BaseModel):
    query: str
    answer: str
    relevant_clauses: List[ClauseSchema]
    consequences: List[str]
    risk_level: str
    evidence: List[Dict[str, Any]]


# ─── Module 8: Obligations ─────────────────────────────────────────────────────

class ObligationSchema(BaseModel):
    id: str
    obligation_type: str
    party: str
    description: str
    deadline: Optional[str] = None
    amount: Optional[str] = None
    evidence_text: str

    class Config:
        from_attributes = True


class ObligationResponse(BaseModel):
    contract_id: str
    obligations: List[ObligationSchema]
    total: int


# ─── Module 9: Comparison ──────────────────────────────────────────────────────

class CompareRequest(BaseModel):
    contract_id_a: str
    contract_id_b: str


class ClauseDiff(BaseModel):
    change_type: str  # added | removed | modified | unchanged
    category: str
    text_a: Optional[str] = None
    text_b: Optional[str] = None
    risk_delta: str  # increased | decreased | unchanged | new | removed
    risk_level_a: Optional[str] = None
    risk_level_b: Optional[str] = None


class CompareResponse(BaseModel):
    contract_a_name: str
    contract_b_name: str
    total_changes: int
    added: int
    removed: int
    modified: int
    diffs: List[ClauseDiff]
    risk_summary: str


# ─── Module 10: Report ─────────────────────────────────────────────────────────

class ReportRequest(BaseModel):
    contract_id: str
    user_role: Union[UserRole, str] = UserRole.FREELANCER
    format: str = "json"  # json | pdf


class ReportResponse(BaseModel):
    contract_id: str
    report_id: str
    generated_at: str
    download_url: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


# ─── User Profile ────────────────────────────────────────────────────────────

class UserProfileCreate(BaseModel):
    name: str
    role: str = UserRole.FREELANCER.value
    preferences: Dict[str, Any] = {}


class UserProfileResponse(BaseModel):
    id: str
    name: str
    role: str
    preferences: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
