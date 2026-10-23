"""
SQLAlchemy ORM Models for ClauseGuard AI.
"""

from sqlalchemy import (
    Column, String, Text, Float, Integer, DateTime,
    JSON, ForeignKey, Enum as SAEnum, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.core.database import Base


def gen_uuid():
    return str(uuid.uuid4())


# ─── Enums ───────────────────────────────────────────────────────────────────

class RiskLevel(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class ClauseCategory(str, enum.Enum):
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

class UserRole(str, enum.Enum):
    FREELANCER = "Freelancer"
    TENANT = "Tenant"
    EMPLOYEE = "Employee"
    BUSINESS_OWNER = "Business Owner"
    VENDOR = "Vendor"
    GENERAL = "General"


# ─── Models ──────────────────────────────────────────────────────────────────

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(String, primary_key=True, default=gen_uuid)
    filename = Column(String, nullable=False)
    original_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf / docx
    file_size = Column(Integer)
    upload_date = Column(DateTime, default=datetime.utcnow)
    raw_text = Column(Text)
    page_count = Column(Integer)
    status = Column(String, default="uploaded")  # uploaded, processing, done, error
    error_message = Column(Text, nullable=True)

    # Relationships
    clauses = relationship("Clause", back_populates="contract", cascade="all, delete-orphan")
    risk_report = relationship("RiskReport", back_populates="contract", uselist=False, cascade="all, delete-orphan")
    obligations = relationship("Obligation", back_populates="contract", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Contract id={self.id} name={self.original_name}>"


class Clause(Base):
    __tablename__ = "clauses"

    id = Column(String, primary_key=True, default=gen_uuid)
    contract_id = Column(String, ForeignKey("contracts.id"), nullable=False)
    index = Column(Integer)  # Clause order in document
    raw_text = Column(Text, nullable=False)
    cleaned_text = Column(Text)
    category = Column(SAEnum(ClauseCategory), default=ClauseCategory.GENERAL)
    risk_level = Column(SAEnum(RiskLevel), default=RiskLevel.LOW)
    risk_score = Column(Float, default=0.0)  # 0.0 – 1.0
    risk_reasoning = Column(Text)
    page_number = Column(Integer, nullable=True)
    start_char = Column(Integer, nullable=True)
    end_char = Column(Integer, nullable=True)
    embedding = Column(JSON, nullable=True)  # stored as list[float]
    related_clause_ids = Column(JSON, default=list)  # risk chain links
    created_at = Column(DateTime, default=datetime.utcnow)

    contract = relationship("Contract", back_populates="clauses")
    risks = relationship("ClauseRisk", back_populates="clause", cascade="all, delete-orphan")


class ClauseRisk(Base):
    __tablename__ = "clause_risks"

    id = Column(String, primary_key=True, default=gen_uuid)
    clause_id = Column(String, ForeignKey("clauses.id"), nullable=False)
    risk_type = Column(String)
    description = Column(Text)
    evidence_text = Column(Text)  # Verbatim text snippet from clause
    severity = Column(SAEnum(RiskLevel))
    role_weights = Column(JSON, default=dict)  # {role: weight} personalization map
    created_at = Column(DateTime, default=datetime.utcnow)

    clause = relationship("Clause", back_populates="risks")


class RiskReport(Base):
    __tablename__ = "risk_reports"

    id = Column(String, primary_key=True, default=gen_uuid)
    contract_id = Column(String, ForeignKey("contracts.id"), nullable=False, unique=True)
    overall_risk_score = Column(Float)
    overall_risk_level = Column(SAEnum(RiskLevel))
    summary = Column(Text)
    recommendations = Column(JSON, default=list)
    role_used = Column(SAEnum(UserRole), default=UserRole.GENERAL)
    clause_chains = Column(JSON, default=list)  # risk dependency chains
    generated_at = Column(DateTime, default=datetime.utcnow)

    contract = relationship("Contract", back_populates="risk_report")


class Obligation(Base):
    __tablename__ = "obligations"

    id = Column(String, primary_key=True, default=gen_uuid)
    contract_id = Column(String, ForeignKey("contracts.id"), nullable=False)
    obligation_type = Column(String)  # Payment, Notice, Renewal, Deadline
    party = Column(String)
    description = Column(Text)
    deadline = Column(String, nullable=True)  # Natural language or ISO date
    amount = Column(String, nullable=True)
    evidence_text = Column(Text)
    clause_id = Column(String, ForeignKey("clauses.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    contract = relationship("Contract", back_populates="obligations")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String)
    role = Column(SAEnum(UserRole), default=UserRole.GENERAL)
    preferences = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
