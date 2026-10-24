"""
SQLAlchemy ORM Models for ClauseGuard AI.
Configured for 8 Core Legal Provisions, Personalized Roles, and Grounded Mitigation.
"""

from sqlalchemy import (
    Column, String, Text, Float, Integer, DateTime,
    JSON, ForeignKey, Boolean
)
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


def gen_uuid():
    return str(uuid.uuid4())


# ─── Enums & Constants ─────────────────────────────────────────────────────────

class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

    @classmethod
    def normalize(cls, val: str) -> "RiskLevel":
        if not val:
            return cls.LOW
        v = str(val).upper().strip()
        if "HIGH" in v:
            return cls.HIGH
        elif "MED" in v or "CAUTION" in v:
            return cls.MEDIUM
        return cls.LOW


class ClauseCategory(str, enum.Enum):
    # 8 Core Legal Provisions
    PAYMENT = "Payment Terms & Fees"
    TERMINATION = "Termination & Cancellation"
    LIABILITY = "Liability & Indemnification"
    CONFIDENTIALITY = "Confidentiality & Non-Disclosure"
    IP = "Intellectual Property Rights (IP)"
    PENALTIES = "Penalties & Liquidated Damages"
    RENEWAL = "Renewal Terms & Extensions"
    DISPUTE_RESOLUTION = "Dispute Resolution & Governing Law"
    GENERAL = "General Commercial Provisions"

    @classmethod
    def normalize(cls, val: str) -> "ClauseCategory":
        if not val:
            return cls.GENERAL
        v = str(val).lower().strip()
        if "pay" in v or "fee" in v or "invoice" in v:
            return cls.PAYMENT
        elif "terminat" in v or "cancel" in v:
            return cls.TERMINATION
        elif "liab" in v or "indemn" in v or "harm" in v:
            return cls.LIABILITY
        elif "confid" in v or "nda" in v or "secret" in v:
            return cls.CONFIDENTIALITY
        elif "ip" in v or "intellect" in v or "patent" in v or "copyright" in v or "work for hire" in v or "assign" in v:
            return cls.IP
        elif "penalt" in v or "liquidat" in v or "damage" in v or "fine" in v:
            return cls.PENALTIES
        elif "renew" in v or "exten" in v or "evergreen" in v:
            return cls.RENEWAL
        elif "dispute" in v or "arbitrat" in v or "jurisdict" in v or "governing law" in v:
            return cls.DISPUTE_RESOLUTION
        return cls.GENERAL


class UserRole(str, enum.Enum):
    FREELANCER = "Freelancer / Contractor"
    TENANT = "Tenant"
    EMPLOYEE = "Employee"
    BUSINESS_OWNER = "Client / Small Business Owner"
    GENERAL = "General"

    @classmethod
    def normalize(cls, val: str) -> "UserRole":
        if not val:
            return cls.FREELANCER
        v = str(val).lower().strip()
        if "tenant" in v or "lease" in v:
            return cls.TENANT
        elif "employ" in v:
            return cls.EMPLOYEE
        elif "client" in v or "business" in v or "owner" in v:
            return cls.BUSINESS_OWNER
        elif "freelance" in v or "contractor" in v or "vendor" in v:
            return cls.FREELANCER
        return cls.GENERAL


# ─── Models ──────────────────────────────────────────────────────────────────

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(String, primary_key=True, default=gen_uuid)
    filename = Column(String, nullable=False)
    original_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf / docx / txt
    file_size = Column(Integer, nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    raw_text = Column(Text, nullable=True)
    page_count = Column(Integer, default=1)
    extracted_clause_count = Column(Integer, default=0)
    status = Column(String, default="uploaded")  # uploaded, processing, done, error
    error_message = Column(Text, nullable=True)

    # Relationships
    clauses = relationship("Clause", back_populates="contract", cascade="all, delete-orphan", order_by="Clause.index")
    risk_report = relationship("RiskReport", back_populates="contract", uselist=False, cascade="all, delete-orphan")
    obligations = relationship("Obligation", back_populates="contract", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Contract id={self.id} name={self.original_name}>"


class Clause(Base):
    __tablename__ = "clauses"

    id = Column(String, primary_key=True, default=gen_uuid)
    clause_code = Column(String, nullable=True)  # e.g. "CLAUSE-005"
    contract_id = Column(String, ForeignKey("contracts.id"), nullable=False)
    index = Column(Integer, default=0)  # Clause order in document
    raw_text = Column(Text, nullable=False)
    cleaned_text = Column(Text, nullable=True)
    category = Column(String, default=ClauseCategory.GENERAL.value)
    risk_level = Column(String, default=RiskLevel.LOW.value)
    risk_score = Column(Float, default=0.0)  # 0.0 – 1.0
    risk_reasoning = Column(Text, nullable=True)
    page_number = Column(Integer, default=1)
    start_char = Column(Integer, nullable=True)
    end_char = Column(Integer, nullable=True)
    
    # Feature 1 & 2 additions: plain language, statutory citations, counter-proposals
    simple_explanation = Column(Text, nullable=True)
    legal_evidence = Column(Text, nullable=True)
    suggested_change = Column(Text, nullable=True)
    role_reasoning = Column(Text, nullable=True)
    link_basis = Column(String, nullable=True)  # Cross-Reference, Shared Defined Term, Semantic Candidate

    embedding = Column(JSON, nullable=True)  # stored as list[float]
    related_clause_ids = Column(JSON, default=list)  # risk chain links
    created_at = Column(DateTime, default=datetime.utcnow)

    contract = relationship("Contract", back_populates="clauses")
    risks = relationship("ClauseRisk", back_populates="clause", cascade="all, delete-orphan")


class ClauseRisk(Base):
    __tablename__ = "clause_risks"

    id = Column(String, primary_key=True, default=gen_uuid)
    clause_id = Column(String, ForeignKey("clauses.id"), nullable=False)
    risk_type = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    evidence_text = Column(Text, nullable=True)  # Verbatim text snippet from clause
    severity = Column(String, default=RiskLevel.LOW.value)
    role_weights = Column(JSON, default=dict)  # {role: weight} personalization map
    created_at = Column(DateTime, default=datetime.utcnow)

    clause = relationship("Clause", back_populates="risks")


class RiskReport(Base):
    __tablename__ = "risk_reports"

    id = Column(String, primary_key=True, default=gen_uuid)
    contract_id = Column(String, ForeignKey("contracts.id"), nullable=False, unique=True)
    overall_risk_score = Column(Float, default=0.0)
    overall_risk_level = Column(String, default=RiskLevel.LOW.value)
    summary = Column(Text, nullable=True)
    recommendations = Column(JSON, default=list)
    role_used = Column(String, default=UserRole.FREELANCER.value)
    clause_chains = Column(JSON, default=list)  # risk dependency chains
    generated_at = Column(DateTime, default=datetime.utcnow)

    contract = relationship("Contract", back_populates="risk_report")


class Obligation(Base):
    __tablename__ = "obligations"

    id = Column(String, primary_key=True, default=gen_uuid)
    contract_id = Column(String, ForeignKey("contracts.id"), nullable=False)
    obligation_type = Column(String, nullable=True)  # Payment, Notice, Renewal, Deadline
    party = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    deadline = Column(String, nullable=True)  # Natural language or ISO date
    amount = Column(String, nullable=True)
    evidence_text = Column(Text, nullable=True)
    clause_id = Column(String, ForeignKey("clauses.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    contract = relationship("Contract", back_populates="obligations")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=True)
    role = Column(String, default=UserRole.FREELANCER.value)
    preferences = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
