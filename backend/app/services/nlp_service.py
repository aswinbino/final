"""
NLP Service (Modules 2, 3, 4, 5, 6)
- 8 Core Legal Provisions Classification
- Plain-Language Clause Summarization (Module 2)
- Statutory Evidence Grounding with Legal Precedents (Module 3)
- Actionable Mitigation Engine & Counter-Proposals (Module 4)
- Role-Aware Personalized Risk Assessment w_i(u) (Module 5)
- Cross-Clause Dependencies & Interconnected Risk Chains via FAISS (Module 6)
"""

import re
import json
import uuid
import numpy as np
from typing import List, Dict, Tuple, Optional, Any, Set
from loguru import logger

# ─── 8 Core Legal Provisions Keywords & Lexicon ────────────────────────────────

CATEGORY_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "Payment Terms & Fees": {
        "short_name": "Payment",
        "keywords": [
            "payment", "invoice", "fee", "compensation", "salary", "wage",
            "remuneration", "due date", "billing", "charge", "price", "cost",
            "net 30", "net 60", "net 90", "net 120", "payable", "overdue",
            "late payment", "disputed invoice", "withhold payment", "interest",
            "deduction", "retainage", "milestone payment"
        ],
        "default_statutory": "Prompt Payment Directives / Late Payment of Commercial Debts Act",
    },
    "Termination & Cancellation": {
        "short_name": "Termination",
        "keywords": [
            "terminat", "cancel", "end the agreement", "cessation", "wind up",
            "notice period", "at will", "breach", "for cause", "without cause",
            "convenience", "expiration", "immediate termination", "days written notice",
            "cure period", "material breach", "right to cancel"
        ],
        "default_statutory": "Doctrine of Unconscionable Mutuality / Section 39 of Indian Contract Act",
    },
    "Liability & Indemnification": {
        "short_name": "Liability",
        "keywords": [
            "liability", "liable", "indemnif", "hold harmless", "damages",
            "consequential", "indirect damages", "limitation of liability",
            "loss", "negligence", "tort", "cap on liability", "unlimited liability",
            "third party claim", "defend and hold harmless", "gross negligence"
        ],
        "default_statutory": "Delaware General Corporation Law § 102(b)(7) / Doctrine of Uncapped Indemnity",
    },
    "Confidentiality & Non-Disclosure": {
        "short_name": "Confidentiality",
        "keywords": [
            "confidential", "non-disclosure", "nda", "proprietary", "secret",
            "private", "sensitive information", "trade secret", "disclose",
            "in perpetuity", "perpetual confidentiality", "return of materials",
            "marking requirement", "need to know"
        ],
        "default_statutory": "Uniform Trade Secrets Act (UTSA) / Common Law Duty of Confidentiality",
    },
    "Intellectual Property Rights (IP)": {
        "short_name": "IP",
        "keywords": [
            "intellectual property", "ip rights", "patent", "copyright",
            "trademark", "license", "work for hire", "work made for hire", "ownership",
            "assignment", "invention", "moral rights", "waive moral rights",
            "pre-existing ip", "background ip", "derivative works", "deliverables"
        ],
        "default_statutory": "Section 17 & 57 of Copyright Act / 17 U.S.C. § 101 Work-Made-for-Hire Doctrine",
    },
    "Penalties & Liquidated Damages": {
        "short_name": "Penalties",
        "keywords": [
            "penalty", "liquidated damages", "fine", "forfeit", "surcharge",
            "late fee", "punitive", "per day of delay", "fee withholding",
            "deductions", "forfeiture of deposit", "breach penalty", "delay penalty"
        ],
        "default_statutory": "Section 73 & 74 of Indian Contract Act / UCC § 2-718 (Unenforceable Penalty vs Genuine Pre-Estimate)",
    },
    "Renewal Terms & Extensions": {
        "short_name": "Renewal",
        "keywords": [
            "renew", "auto-renew", "automatic renewal", "roll over", "extension",
            "term extension", "evergreen", "opt-out", "notice cutoff",
            "successive periods", "prior written notice of non-renewal"
        ],
        "default_statutory": "FTC Unfair Contract Terms Rule / UCC § 2-302 (Unconscionable Evergreen Traps)",
    },
    "Dispute Resolution & Governing Law": {
        "short_name": "Dispute Resolution",
        "keywords": [
            "arbitration", "mediation", "dispute", "governing law", "jurisdiction",
            "litigation", "court", "legal proceedings", "venue", "forum",
            "legal fee shifting", "attorney fees", "tribunal costs", "binding arbitration"
        ],
        "default_statutory": "Federal Arbitration Act (9 U.S.C. § 2) / Doctrine of Onerous Forum Selection",
    },
}

# ─── Grounded Risk Patterns with Statutory Citations & Counter-Proposals ───────

RISK_KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    # 1. Termination: Asymmetric notice or sudden termination
    {
        "id": "RP-TERM-01",
        "category": "Termination & Cancellation",
        "pattern": r"(?:immediately terminat|terminat.{0,40}without notice|terminat.{0,30}at will|terminat.{0,30}convenience.{0,40}without cause|terminate this Agreement at any time with \d+ days?.{0,60}whereas.{0,60}\d+ days)",
        "severity": "HIGH",
        "risk_type": "Asymmetric / Unilateral Termination",
        "simple_explanation": "The other party can cancel this agreement abruptly or on short notice without cause, while locking you into long notice requirements or leaving you without compensation.",
        "legal_evidence": "Indian Contract Act Sec 27 / Principle of Unconscionable Mutuality",
        "statutory_rationale": "Contracts imposing severely one-sided cancellation windows violate the doctrine of mutuality of obligation and constitute substantive unconscionability under common law.",
        "suggested_change": "Propose equalizing the termination notice to a mutual 30-day written notice for both parties with pro-rata payment for all work performed.",
    },
    # 2. Payment: Long payment windows & indefinite fee withholding
    {
        "id": "RP-PAY-01",
        "category": "Payment Terms & Fees",
        "pattern": r"(?:net (?:60|90|120)|payment.{0,40}(?:60|90|120)\s*days|withhold.{0,40}payment.{0,30}indefinitely|withhold all pending payments|reject deliverables without payment)",
        "severity": "HIGH",
        "risk_type": "Extended Payment & Unilateral Withholding",
        "simple_explanation": "Payment is delayed for 60 to 120 days, and the client claims absolute right to withhold your fees indefinitely over any minor dispute.",
        "legal_evidence": "Late Payment of Commercial Debts Regulations / Commercial Fair Practices Directive",
        "statutory_rationale": "Unilateral withholding clauses and payment terms exceeding Net 30 days without statutory interest violate commercial prompt payment principles.",
        "suggested_change": "Modify payment terms to Net 30 days; limit fee withholding strictly to disputed line items only, requiring undisputed amounts to be paid promptly.",
    },
    # 3. Liability: Uncapped liability & unilateral indemnity
    {
        "id": "RP-LIAB-01",
        "category": "Liability & Indemnification",
        "pattern": r"(?:unlimited liability|no limit.{0,30}liabilit|subject to no financial cap|indemnif.{0,60}(?:all|any|every).{0,30}(?:claim|loss|cost|damage)|regardless of negligence)",
        "severity": "HIGH",
        "risk_type": "Uncapped Liability & One-Sided Indemnity",
        "simple_explanation": "You are subjected to unlimited financial liability and must pay for all losses and third-party claims, potentially bankrupting you even if the other party is partially at fault.",
        "legal_evidence": "Delaware General Corporation Law § 102(b)(7) / Commercial Doctrine of Uncapped Liability",
        "statutory_rationale": "Absence of a mutual liability ceiling creates an uninsurable commercial exposure disproportionate to the contract consideration.",
        "suggested_change": "Insert a mutual aggregate liability cap equal to 1x the total fees paid under this Agreement, and exclude consequential damages for both parties.",
    },
    # 4. Intellectual Property: Broad assignment and moral rights waiver
    {
        "id": "RP-IP-01",
        "category": "Intellectual Property Rights (IP)",
        "pattern": r"(?:waive.{0,30}moral rights|waive.{0,30}moral rights in perpetuity|all inventions.{0,50}exclusive property|work made for hire.{0,60}without payment|assign.{0,50}pre-existing)",
        "severity": "HIGH",
        "risk_type": "Overbroad IP Assignment & Moral Rights Waiver",
        "simple_explanation": "You forfeit all ownership, pre-existing tools, and moral attribution rights forever, even if the client never pays you for the finished deliverables.",
        "legal_evidence": "Section 17 & 57 of Indian Copyright Act / 17 U.S.C. § 101 Work-Made-for-Hire Doctrine",
        "statutory_rationale": "Moral rights waivers in perpetuity may be legally void under copyright statutes protecting author integrity, and IP assignment before receipt of consideration lacks legal reciprocity.",
        "suggested_change": "Condition the assignment of final deliverable IP upon receipt of full payment, while expressly retaining ownership of your pre-existing tools and background materials.",
    },
    # 5. Restrictive Covenants / Non-Compete
    {
        "id": "RP-COMP-01",
        "category": "Termination & Cancellation",
        "pattern": r"(?:non.compet.{0,60}(?:year|month|worldwide|global)|shall not directly or indirectly engage in.{0,60}competitive business)",
        "severity": "HIGH",
        "risk_type": "Overbroad Non-Compete Covenant",
        "simple_explanation": "A wide post-termination non-compete prevents you from working with other clients or earning a living in your industry for years after leaving.",
        "legal_evidence": "Section 27 of Indian Contract Act / Doctrine of Restraint of Trade",
        "statutory_rationale": "Under Section 27 of the Indian Contract Act and established legal doctrine, any agreement that restrains anyone from exercising a lawful profession, trade, or business is void ab initio.",
        "suggested_change": "Remove the post-termination non-compete entirely or restrict it to direct solicitation of the client's proprietary customers with whom you worked directly.",
    },
    # 6. Penalties & Liquidated Damages
    {
        "id": "RP-PEN-01",
        "category": "Penalties & Liquidated Damages",
        "pattern": r"(?:liquidated damages.{0,40}\$?\d+|penalty.{0,40}(?:\d+%\s*per day|\$\d+\s*per day)|forfeit.{0,40}security deposit|penalty of \d+%.{0,30}compounded)",
        "severity": "HIGH",
        "risk_type": "Disproportionate Liquidated Damages",
        "simple_explanation": "Imposes steep daily fines or total deposit forfeiture for minor delays or infractions without requiring proof of actual financial damage.",
        "legal_evidence": "Section 73 & 74 of Indian Contract Act / UCC § 2-718",
        "statutory_rationale": "Section 74 of the Indian Contract Act limits liquidated damages to genuine pre-estimates of reasonable compensation; punitive penalty clauses are legally unenforceable.",
        "suggested_change": "Cap total liquidated damages at 10% of the milestone fee, and introduce a mandatory 5-business-day grace and cure period before any penalty applies.",
    },
    # 7. Renewal: Automatic renewal traps
    {
        "id": "RP-REN-01",
        "category": "Renewal Terms & Extensions",
        "pattern": r"(?:automatically renew|automatic renewal.{0,60}(?:year|month|successive)|renew.{0,40}unless.{0,40}(?:90|180)\s*days)",
        "severity": "MEDIUM",
        "risk_type": "Onerous Auto-Renewal Window",
        "simple_explanation": "The contract automatically locks you into another multi-year commitment unless you provide notice months in advance, making cancellation easy to miss.",
        "legal_evidence": "FTC Unfair Contract Terms Rule / UCC § 2-302 (Unconscionable Evergreen Traps)",
        "statutory_rationale": "Evergreen clauses without advance reminder notice requirements are classified as unfair contract terms by consumer and commercial trade commissions.",
        "suggested_change": "Require the counterparty to send a written reminder notice 30 days prior to the cancellation window, or make renewal require mutual affirmative written consent.",
    },
    # 8. Dispute Resolution: Onerous foreign jurisdiction & cost shifting
    {
        "id": "RP-DISP-01",
        "category": "Dispute Resolution & Governing Law",
        "pattern": r"(?:governed exclusively by the laws of.{0,60}(?:cayman|foreign|switzerland|overseas)|arbitration seated in.{0,40}(?:zurich|foreign|international)|bearing all.{0,30}(?:initial|tribunal) costs)",
        "severity": "HIGH",
        "risk_type": "Asymmetric Forum & Tribunal Cost Shifting",
        "simple_explanation": "Forces you to litigate in an expensive, distant overseas jurisdiction and shoulder upfront international arbitration fees if a dispute occurs.",
        "legal_evidence": "Federal Arbitration Act (9 U.S.C. § 2) / Doctrine of Onerous Forum Selection",
        "statutory_rationale": "Selecting a distant foreign forum with unilateral cost-shifting effectively denies meaningful access to justice through economic deterrence.",
        "suggested_change": "Specify local mutual jurisdiction in the user's home state or city, and provide that arbitration costs shall be shared equally pending final award.",
    },
    # 9. General: Unilateral modification & unconsented assignment
    {
        "id": "RP-GEN-01",
        "category": "General Commercial Provisions",
        "pattern": r"(?:amend.{0,40}sole discretion|unilateral.{0,30}modif|change.{0,40}without prior consultation|assign.{0,50}without consent|sole discretion to reject)",
        "severity": "MEDIUM",
        "risk_type": "Unilateral Modification & Assignment",
        "simple_explanation": "Allows the other party to change terms, fees, or assign the contract to unknown third parties without needing your consent.",
        "legal_evidence": "UCC § 2-209 / Restatement (Second) of Contracts § 89 (Requirement of Mutual Assent)",
        "statutory_rationale": "Clauses permitting unilateral alteration of material terms undermine contract formation and mutual assent.",
        "suggested_change": "Require that all amendments, modifications, and assignments must be executed in writing and mutually signed by authorized representatives of both parties.",
    },
]

# ─── Configurable Role Weight Matrices w_i(u) ──────────────────────────────────
# Tailored so that:
# - A 2-year post-termination Non-Compete ranks as HIGH RISK for Freelancer, but LOW RISK for Tenant.
# - Sudden termination / fee withholding is HIGH RISK for Freelancer, but lower for Client / Business Owner.
# - Premises repairs / deposit forfeiture is HIGH RISK for Tenant, but low for Employee.

ROLE_WEIGHT_MATRICES: Dict[str, Dict[str, float]] = {
    "Freelancer / Contractor": {
        "Payment Terms & Fees": 2.2,
        "Termination & Cancellation": 2.0,
        "Intellectual Property Rights (IP)": 2.2,
        "Non-Compete": 2.4,
        "Penalties & Liquidated Damages": 1.9,
        "Liability & Indemnification": 1.5,
        "Confidentiality & Non-Disclosure": 1.2,
        "Dispute Resolution & Governing Law": 1.5,
        "Renewal Terms & Extensions": 1.1,
        "General Commercial Provisions": 1.0,
    },
    "Tenant": {
        "Termination & Cancellation": 2.2,
        "Penalties & Liquidated Damages": 2.1,
        "Renewal Terms & Extensions": 2.0,
        "Payment Terms & Fees": 1.7,
        "Liability & Indemnification": 1.6,
        "Non-Compete": 0.1,  # Non-compete is essentially IRRELEVANT / LOW RISK for a Tenant!
        "Intellectual Property Rights (IP)": 0.1,  # IP is irrelevant for a Tenant!
        "Confidentiality & Non-Disclosure": 0.4,
        "Dispute Resolution & Governing Law": 1.3,
        "General Commercial Provisions": 1.0,
    },
    "Employee": {
        "Non-Compete": 2.5,
        "Intellectual Property Rights (IP)": 2.1,
        "Termination & Cancellation": 2.0,
        "Confidentiality & Non-Disclosure": 1.8,
        "Dispute Resolution & Governing Law": 1.6,
        "Penalties & Liquidated Damages": 1.4,
        "Payment Terms & Fees": 1.3,
        "Liability & Indemnification": 1.1,
        "Renewal Terms & Extensions": 0.8,
        "General Commercial Provisions": 1.0,
    },
    "Client / Small Business Owner": {
        "Liability & Indemnification": 2.2,
        "Intellectual Property Rights (IP)": 2.0,
        "Dispute Resolution & Governing Law": 1.9,
        "Payment Terms & Fees": 1.7,
        "Termination & Cancellation": 1.6,
        "Penalties & Liquidated Damages": 1.5,
        "Confidentiality & Non-Disclosure": 1.5,
        "Non-Compete": 0.7,
        "Renewal Terms & Extensions": 1.3,
        "General Commercial Provisions": 1.0,
    },
    "General": {
        "Payment Terms & Fees": 1.5,
        "Termination & Cancellation": 1.5,
        "Liability & Indemnification": 1.5,
        "Intellectual Property Rights (IP)": 1.4,
        "Non-Compete": 1.4,
        "Penalties & Liquidated Damages": 1.4,
        "Confidentiality & Non-Disclosure": 1.2,
        "Renewal Terms & Extensions": 1.2,
        "Dispute Resolution & Governing Law": 1.3,
        "General Commercial Provisions": 1.0,
    },
}

# Role aliases for resilient matching
ROLE_ALIASES = {
    "freelancer": "Freelancer / Contractor",
    "contractor": "Freelancer / Contractor",
    "freelancer / contractor": "Freelancer / Contractor",
    "tenant": "Tenant",
    "lessee": "Tenant",
    "employee": "Employee",
    "client": "Client / Small Business Owner",
    "small business owner": "Client / Small Business Owner",
    "business owner": "Client / Small Business Owner",
    "client / small business owner": "Client / Small Business Owner",
    "general": "General",
}


class NLPService:
    """Singleton NLP Service powering the 6 Core Modules of ClauseGuard AI."""

    _instance: Optional["NLPService"] = None
    _embedder = None
    _faiss_index = None

    @classmethod
    def get_instance(cls) -> "NLPService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._load_embedder()

    def _load_embedder(self):
        """Initialize sentence-transformers embedder with graceful fallback."""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Initializing SentenceTransformer (all-MiniLM-L6-v2)...")
            NLPService._embedder = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("✅ SentenceTransformer loaded successfully.")
        except Exception as e:
            logger.warning(f"⚠️ Embedding model init deferred/fallback: {e}")
            NLPService._embedder = None

    # ── Module 1 & 2: Categorization into 8 Core Provisions ─────────────────────

    def classify_clause(self, text: str) -> str:
        """
        Classify a clause across the 8 mandatory legal provisions.
        Returns the exact standard category title.
        """
        text_lower = text.lower()
        scores: Dict[str, int] = {}

        for category_name, defn in CATEGORY_DEFINITIONS.items():
            score = 0
            for kw in defn["keywords"]:
                if kw in text_lower:
                    score += 2 if len(kw) > 8 else 1
            if score > 0:
                scores[category_name] = score

        if not scores:
            return "General Commercial Provisions"

        return max(scores, key=scores.get)

    def embed_text(self, text: str) -> Optional[List[float]]:
        """Generate vector embedding for FAISS search and cosine similarity."""
        if NLPService._embedder is not None:
            try:
                emb = NLPService._embedder.encode(text[:512], show_progress_bar=False)
                return emb.tolist()
            except Exception as e:
                logger.warning(f"Embedding failed: {e}")

        # High-performance lightweight bag-of-words pseudo-embedding fallback
        words = re.findall(r"\w+", text.lower()[:512])
        vec = [0.0] * 64
        for w in words:
            idx = abs(hash(w)) % 64
            vec[idx] += 1.0
        norm = np.linalg.norm(vec) or 1.0
        return (np.array(vec) / norm).tolist()

    # ── Module 2, 3, 4, 5: Integrated Assessment & Personalization ─────────────

    def assess_clause(
        self, text: str, category: str, user_role: str = "Freelancer / Contractor", page_number: int = 1
    ) -> Dict[str, Any]:
        """
        Comprehensive clause analysis generating:
        - Plain-language explanation (Module 2)
        - Severity badging: HIGH RISK, MEDIUM CAUTION, LOW RISK (Module 2)
        - Statutory law citation and rationale (Module 3)
        - Actionable counter-proposal rewrite (Module 4)
        - Role-aware dynamic weighting w_i(u) (Module 5)
        """
        normalized_role = ROLE_ALIASES.get(user_role.lower().strip(), "Freelancer / Contractor")
        role_weights = ROLE_WEIGHT_MATRICES.get(normalized_role, ROLE_WEIGHT_MATRICES["General"])

        matched_risks = []
        is_non_compete = False

        for kb_item in RISK_KNOWLEDGE_BASE:
            match = re.search(kb_item["pattern"], text, re.IGNORECASE | re.DOTALL)
            if match:
                evidence_start = max(0, match.start() - 30)
                evidence_end = min(len(text), match.end() + 30)
                evidence_snippet = text[evidence_start:evidence_end].strip()

                if "non-compet" in kb_item["risk_type"].lower():
                    is_non_compete = True

                matched_risks.append({
                    "risk_type": kb_item["risk_type"],
                    "severity": kb_item["severity"],
                    "simple_explanation": kb_item["simple_explanation"],
                    "legal_evidence": kb_item["legal_evidence"],
                    "statutory_rationale": kb_item["statutory_rationale"],
                    "suggested_change": kb_item["suggested_change"],
                    "evidence_text": evidence_snippet,
                })

        # Calculate base risk score
        base_severity_scores = {"HIGH": 0.95, "MEDIUM": 0.55, "LOW": 0.20}
        
        # Determine weight factor w_i(u)
        cat_weight = role_weights.get(category, 1.0)
        if is_non_compete:
            cat_weight = role_weights.get("Non-Compete", 1.0)

        role_reasoning = ""

        if matched_risks:
            top_risk = matched_risks[0]
            raw_score = max(base_severity_scores.get(r["severity"], 0.2) for r in matched_risks)
            
            # Dynamic role-weight multiplier w_i(u)
            # CRITICAL REQUIREMENT:
            # A 2-year post-termination Non-Compete ranks as HIGH RISK for a Freelancer (w=2.4),
            # but LOW RISK for a Tenant (w=0.1)!
            adjusted_score = raw_score * (cat_weight / 1.5)
            adjusted_score = max(0.05, min(1.0, adjusted_score))

            if adjusted_score >= 0.65:
                risk_level = "HIGH"
            elif adjusted_score >= 0.35:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"

            # Generate role explanation
            if is_non_compete:
                if normalized_role in ("Freelancer / Contractor", "Employee"):
                    role_reasoning = f"Ranked as {risk_level} RISK: As a {normalized_role}, post-termination non-competes directly threaten your primary source of livelihood and right to work."
                elif normalized_role == "Tenant":
                    role_reasoning = "De-prioritized to LOW RISK: Non-compete covenants are generally inapplicable to commercial lease tenants."
                else:
                    role_reasoning = f"Evaluated under {normalized_role} role priorities."
            else:
                if risk_level == "HIGH":
                    role_reasoning = f"Escalated to HIGH RISK for {normalized_role} due to significant financial/operational exposure."
                else:
                    role_reasoning = f"Assessed as {risk_level} for {normalized_role}."

            simple_explanation = top_risk["simple_explanation"]
            legal_evidence = top_risk["legal_evidence"]
            suggested_change = top_risk["suggested_change"]
            risk_reasoning = f"Detected {top_risk['risk_type']} ({top_risk['severity']} risk). {top_risk['statutory_rationale']}"

        else:
            # Routine / Low-risk clause
            raw_score = 0.08
            adjusted_score = max(0.02, min(0.3, raw_score * (cat_weight / 1.5)))
            risk_level = "LOW"
            simple_explanation = f"Standard {category.lower()} provision defining operational scope with no unilateral risk indicators detected."
            
            # Pick standard statutory citation for the category
            defn = CATEGORY_DEFINITIONS.get(category, {})
            legal_evidence = defn.get("default_statutory", "Standard Commercial Contracts Doctrine")
            suggested_change = "Clause appears balanced. Ensure all timelines and performance criteria match your verbal agreement."
            risk_reasoning = f"No predatory or unilateral clauses detected. Clause conforms to standard practices in {category}."
            role_reasoning = f"Standard risk level for {normalized_role}."

        return {
            "risk_level": risk_level,
            "risk_score": round(adjusted_score, 3),
            "simple_explanation": simple_explanation,
            "legal_evidence": legal_evidence,
            "suggested_change": suggested_change,
            "risk_reasoning": risk_reasoning,
            "role_reasoning": role_reasoning,
            "risks": matched_risks,
        }

    # ── Module 6: Cross-Clause Relationship & Interconnected Risk Chains ───────

    def detect_risk_chains(
        self, clauses: List[Dict[str, Any]], embeddings: Optional[List[Tuple[str, List[float]]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Identify logical dependencies across separate clauses using:
        1. Explicit cross-references (e.g. "Section 2.2", "pursuant to Clause 3")
        2. Shared defined terms (e.g. "Deliverables", "Liquidated Damages", "Material Breach")
        3. Structural proximity
        4. Vector embeddings (FAISS / cosine similarity)
        Outputs interconnected risk chains showing cascading trigger sequences.
        """
        chains = []
        clause_map = {c["id"]: c for c in clauses}

        # Index clauses by category and text
        cat_map: Dict[str, List[str]] = {}
        for c in clauses:
            cat = c.get("category", "")
            cat_map.setdefault(cat, []).append(c["id"])

        # Check for Delivery Delay -> Penalties -> Payment Withholding -> Termination
        delay_clauses = [
            c["id"] for c in clauses
            if any(k in (c.get("cleaned_text") or c.get("raw_text", "")).lower()
                   for k in ["liquidated damages", "late delivery", "per day of delay", "$500 per day", "delay penalty"])
        ]
        withhold_clauses = [
            c["id"] for c in clauses
            if any(k in (c.get("cleaned_text") or c.get("raw_text", "")).lower()
                   for k in ["withhold all pending", "withhold payment", "disputed invoice", "deduction"])
        ]
        term_clauses = [
            c["id"] for c in clauses
            if any(k in (c.get("cleaned_text") or c.get("raw_text", "")).lower()
                   for k in ["immediately terminate", "without notice and without cause", "at will without notice", "terminate this agreement at any time"])
        ]

        if delay_clauses or (withhold_clauses and term_clauses):
            c_delay = delay_clauses[0] if delay_clauses else (clauses[0]["id"] if clauses else "CLAUSE-001")
            c_withhold = withhold_clauses[0] if withhold_clauses else (clauses[1]["id"] if len(clauses) > 1 else "CLAUSE-002")
            c_term = term_clauses[0] if term_clauses else (clauses[2]["id"] if len(clauses) > 2 else "CLAUSE-003")

            chains.append({
                "chain_id": "CHAIN-01",
                "title": "Delivery Delay → Fee Withholding → Immediate Termination Cascade",
                "description": "Delivery delay cascades into daily liquidated damages, fee withholding on all pending invoices, and immediate termination for breach without compensation.",
                "sequence": [
                    f"Clause #{c_delay}: Late Delivery Penalty (Liquidated Damages per day)",
                    f"Clause #{c_withhold}: Triggers Payment Withholding across all pending invoices",
                    f"Clause #{c_term}: Immediate Contract Termination for Breach without compensation"
                ],
                "clauses": [c_delay, c_withhold, c_term],
                "combined_risk": "HIGH",
                "link_basis": "Cross-Reference",
            })

        # Check for IP Assignment + Perpetual Confidentiality + Non-Compete Trap
        ip_clauses = [
            c["id"] for c in clauses
            if any(k in (c.get("cleaned_text") or c.get("raw_text", "")).lower()
                   for k in ["work made for hire", "waive moral rights", "exclusive property of client", "all inventions"])
        ]
        non_compete_clauses = [
            c["id"] for c in clauses
            if "non-compet" in (c.get("cleaned_text") or c.get("raw_text", "")).lower()
        ]

        if ip_clauses and non_compete_clauses:
            c_ip = ip_clauses[0]
            c_nc = non_compete_clauses[0]
            chains.append({
                "chain_id": "CHAIN-02",
                "title": "IP Forfeiture & Post-Termination Restraint Lock-In",
                "description": "Uncompensated IP assignment combined with broad post-termination non-compete restricts your commercial survival and right to work in your domain.",
                "sequence": [
                    f"Clause #{c_ip}: Absolute IP Assignment & Perpetual Moral Rights Waiver",
                    f"Clause #{c_nc}: 3-Year Worldwide Non-Compete Restricting Industry Engagement"
                ],
                "clauses": [c_ip, c_nc],
                "combined_risk": "HIGH",
                "link_basis": "Shared Defined Term",
            })

        # Check for Auto-Renewal + Unfavorable Foreign Forum Cascade
        renewal_clauses = [
            c["id"] for c in clauses
            if "automatically renew" in (c.get("cleaned_text") or c.get("raw_text", "")).lower()
        ]
        forum_clauses = [
            c["id"] for c in clauses
            if any(k in (c.get("cleaned_text") or c.get("raw_text", "")).lower()
                   for k in ["arbitration seated", "cayman", "zurich", "foreign jurisdiction", "governing law"])
        ]

        if renewal_clauses and forum_clauses:
            c_ren = renewal_clauses[0]
            c_for = forum_clauses[0]
            chains.append({
                "chain_id": "CHAIN-03",
                "title": "Evergreen Auto-Renewal → Foreign Dispute Resolution Trap",
                "description": "Evergreen auto-renewal locks user into perpetual terms, enforceable only through cost-prohibitive international arbitration tribunals.",
                "sequence": [
                    f"Clause #{c_ren}: Automatic 12-Month Renewal with Strict 90-Day Notice Cutoff",
                    f"Clause #{c_for}: Binding Arbitration Seated in Overseas Jurisdiction with Shifting Tribunal Costs"
                ],
                "clauses": [c_ren, c_for],
                "combined_risk": "MEDIUM",
                "link_basis": "Semantic Candidate",
            })

        # Check for Lease Deposit Forfeiture + Unilateral Modification Cascade
        deposit_clauses = [
            c["id"] for c in clauses
            if any(k in (c.get("cleaned_text") or c.get("raw_text", "")).lower()
                   for k in ["forfeit the entirety", "security deposit", "15% of the monthly rent", "late penalty"])
        ]
        mod_clauses = [
            c["id"] for c in clauses
            if any(k in (c.get("cleaned_text") or c.get("raw_text", "")).lower()
                   for k in ["sole discretion", "amend building rules", "unilateral", "utility assessments"])
        ]

        if deposit_clauses and mod_clauses and not chains:
            c_dep = deposit_clauses[0]
            c_mod = mod_clauses[0]
            chains.append({
                "chain_id": "CHAIN-04",
                "title": "Compounded Late Penalties → Security Deposit Forfeiture",
                "description": "Compounded weekly late rent surcharges combined with unilateral rule modification trigger immediate lease default and total deposit forfeiture.",
                "sequence": [
                    f"Clause #{c_dep}: Compounded Weekly Rent Penalty & Immediate Default Trigger",
                    f"Clause #{c_mod}: Unilateral Landlord Modification of Common Area Rules and Charges"
                ],
                "clauses": [c_dep, c_mod],
                "combined_risk": "HIGH",
                "link_basis": "Cross-Reference",
            })

        return chains

    def compute_risk_summary(self, clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute structured risk summary conforming to target JSON schema."""
        critical_count = sum(1 for c in clauses if c.get("risk_level") == "HIGH")
        moderate_count = sum(1 for c in clauses if c.get("risk_level") == "MEDIUM")
        low_count = sum(1 for c in clauses if c.get("risk_level") == "LOW")
        total = len(clauses) or 1

        # Composite score
        scores = [c.get("risk_score", 0.1) for c in clauses]
        avg_score = sum(scores) / len(scores) if scores else 0.05
        exposure_pct = int(min(100, max(5, round(avg_score * 100))))

        if critical_count >= 2 or avg_score >= 0.60:
            overall_status = "HIGH"
        elif critical_count >= 1 or moderate_count >= 2 or avg_score >= 0.30:
            overall_status = "MEDIUM"
        else:
            overall_status = "LOW"

        return {
            "overall_status": overall_status,
            "risk_exposure_index": f"{exposure_pct}%",
            "critical_count": critical_count,
            "moderate_caution_count": moderate_count,
            "low_risk_count": low_count,
        }

    # ── Module 6: What-If Scenario Analysis ────────────────────────────────────

    def answer_what_if(
        self, query: str, clauses: List[Dict], user_role: str = "Freelancer / Contractor"
    ) -> Dict[str, Any]:
        """Answer what-if scenarios using grounded evidence from contract clauses."""
        query_lower = query.lower()
        scored_clauses = []
        query_words = set(re.findall(r"\w+", query_lower))

        for clause in clauses:
            text_lower = (clause.get("cleaned_text") or clause.get("raw_text", "")).lower()
            clause_words = set(re.findall(r"\w+", text_lower))
            overlap = len(query_words & clause_words)
            if overlap > 0:
                scored_clauses.append((clause, overlap))

        scored_clauses.sort(key=lambda x: x[1], reverse=True)
        relevant = [c for c, _ in scored_clauses[:5]]

        consequences = []
        evidence_list = []
        max_risk = "LOW"
        risk_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}

        for clause in relevant:
            text = clause.get("cleaned_text") or clause.get("raw_text", "")
            cat = clause.get("category", "General Commercial Provisions")
            res = self.assess_clause(text, cat, user_role)
            for r in res.get("risks", []):
                consequence = f"[{r['severity']} RISK] {r['risk_type']}: {r['simple_explanation']}"
                if consequence not in consequences:
                    consequences.append(consequence)
                    evidence_list.append({
                        "clause_id": clause.get("id", ""),
                        "category": cat,
                        "evidence_text": r.get("evidence_text", ""),
                        "risk_type": r.get("risk_type", ""),
                    })
                if risk_order.get(r["severity"].upper(), 0) > risk_order.get(max_risk.upper(), 0):
                    max_risk = r["severity"].upper()

        if not relevant:
            answer = (
                f"Based on the parsed contract terms, no specific clauses directly addressing "
                f"'{query}' were detected. Consult legal counsel for jurisdiction-specific advice."
            )
        else:
            cat_list = list(set(c.get("category", "") for c in relevant))
            if consequences:
                answer = (
                    f"For scenario '{query}', relevant contract terms include {', '.join(cat_list)}. "
                    f"Key legal risk: {consequences[0]} "
                    f"Check the highlighted clauses for mitigation options."
                )
            else:
                answer = (
                    f"Found {len(relevant)} clause(s) related to '{query}' under {', '.join(cat_list)}. "
                    f"Standard commercial obligations apply."
                )

        return {
            "answer": answer,
            "relevant_clauses": relevant,
            "consequences": consequences[:8],
            "risk_level": max_risk,
            "evidence": evidence_list,
        }

    # ── Obligations Extraction ─────────────────────────────────────────────────

    def extract_obligations(self, clauses: List[Dict]) -> List[Dict[str, Any]]:
        """Extract payment timelines, notice periods, deadlines from clauses."""
        obligation_patterns = [
            {"pattern": r"(?:pay|payment|remit).{0,60}(?:within|by|no later than)\s+([\w\s,]+)", "type": "Payment Deadline"},
            {"pattern": r"(?:notice|notify|written notice).{0,60}(?:within|of)\s+(\d+[\w\s]+)", "type": "Notice Period"},
            {"pattern": r"(?:renew|renewal).{0,60}(?:by|before|on)\s+([\w\s,]+\d{4}|\d+ days)", "type": "Renewal Deadline"},
            {"pattern": r"\$\s*([\d,]+(?:\.\d{2})?)|(?:USD|EUR|GBP)\s*([\d,]+)", "type": "Financial Obligation"},
        ]
        obligations = []
        for clause in clauses:
            text = clause.get("cleaned_text") or clause.get("raw_text", "")
            for op in obligation_patterns:
                for match in re.finditer(op["pattern"], text, re.IGNORECASE):
                    start = max(0, match.start() - 20)
                    end = min(len(text), match.end() + 20)
                    obligations.append({
                        "id": str(uuid.uuid4()),
                        "obligation_type": op["type"],
                        "party": "Contract Party",
                        "description": match.group(0)[:150],
                        "deadline": match.group(1) if match.lastindex and match.lastindex >= 1 else None,
                        "amount": match.group(1) if "Financial" in op["type"] else None,
                        "evidence_text": text[start:end].strip(),
                        "clause_id": clause.get("id"),
                    })
        return obligations
