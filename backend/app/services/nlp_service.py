"""
NLP Service (Modules 2, 3, 7)
- Clause classification using keyword + embedding-based matching
- Risk assessment with severity scoring
- Evidence-grounded explanations
- FAISS-based semantic search
"""

import re
import json
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from loguru import logger
from functools import lru_cache


# ─── Risk Lexicon ─────────────────────────────────────────────────────────────
# Maps clause categories to trigger keywords
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Payment": [
        "payment", "invoice", "fee", "compensation", "salary", "wage",
        "remuneration", "due date", "billing", "charge", "price", "cost",
        "net 30", "net 60", "payable", "overdue", "late payment",
    ],
    "Termination": [
        "terminat", "cancel", "end the agreement", "cessation", "wind up",
        "notice period", "at will", "breach", "for cause", "without cause",
        "expiration", "dissolution",
    ],
    "Liability": [
        "liability", "liable", "indemnif", "hold harmless", "damages",
        "consequential", "indirect damages", "limitation of liability",
        "loss", "negligence", "tort", "cap on liability",
    ],
    "Confidentiality": [
        "confidential", "non-disclosure", "nda", "proprietary", "secret",
        "private", "sensitive information", "trade secret", "disclose",
    ],
    "IP": [
        "intellectual property", "ip rights", "patent", "copyright",
        "trademark", "license", "work for hire", "ownership", "assignment",
        "invention", "moral rights",
    ],
    "Penalties": [
        "penalty", "penalt", "liquidated damages", "fine", "forfeit",
        "surcharge", "breach penalty", "late fee", "punitive",
    ],
    "Renewal": [
        "renew", "auto-renew", "automatic renewal", "roll over", "extension",
        "term extension", "evergreen", "opt-out",
    ],
    "Dispute Resolution": [
        "arbitration", "mediation", "dispute", "governing law", "jurisdiction",
        "litigation", "court", "legal proceedings", "venue", "forum",
    ],
    "Obligations": [
        "shall", "must", "obligat", "required to", "responsible for",
        "duty", "covenant", "undertake", "commitment", "warrant",
        "represent", "guarantee",
    ],
}

# Risk patterns with severity weights
RISK_PATTERNS: List[Dict[str, Any]] = [
    # HIGH risk patterns
    {
        "pattern": r"sole discretion|absolute discretion",
        "severity": "High",
        "risk_type": "Unfair Discretion",
        "description": "Counterparty retains unilateral/absolute discretion with no checks.",
    },
    {
        "pattern": r"unlimited liability|no limit.{0,30}liabilit",
        "severity": "High",
        "risk_type": "Unlimited Liability",
        "description": "No cap on liability exposure — potentially catastrophic financial risk.",
    },
    {
        "pattern": r"waive.{0,30}right|irrevocabl.{0,30}waiver",
        "severity": "High",
        "risk_type": "Rights Waiver",
        "description": "Party permanently waives legal rights with no recourse.",
    },
    {
        "pattern": r"immediately terminat|terminat.{0,30}without notice|terminat.{0,30}at will",
        "severity": "High",
        "risk_type": "Sudden Termination",
        "description": "Contract can be terminated without any notice period.",
    },
    {
        "pattern": r"non.compet.{0,80}(year|month|worldwide|global)",
        "severity": "High",
        "risk_type": "Broad Non-Compete",
        "description": "Wide-scope non-compete clause restricting future employment/business.",
    },
    {
        "pattern": r"assign.{0,60}without.{0,20}consent|transfer.{0,60}without.{0,20}approval",
        "severity": "High",
        "risk_type": "Unconsented Assignment",
        "description": "Contract rights can be assigned to third parties without your approval.",
    },
    # MEDIUM risk patterns
    {
        "pattern": r"auto.?renew|automatic.{0,20}renewal|automatically renew",
        "severity": "Medium",
        "risk_type": "Auto-Renewal",
        "description": "Contract renews automatically — may lock in unfavorable terms.",
    },
    {
        "pattern": r"penalty.{0,60}(\d+%|\$[\d,]+)|liquidated damages",
        "severity": "Medium",
        "risk_type": "Financial Penalty",
        "description": "Specific financial penalties defined for breach or late performance.",
    },
    {
        "pattern": r"unilateral.{0,40}modif|amend.{0,40}sole discretion|change.{0,40}without notice",
        "severity": "Medium",
        "risk_type": "Unilateral Modification",
        "description": "Other party can modify terms without mutual consent.",
    },
    {
        "pattern": r"exclusiv.{0,30}(jurisdiction|forum|venue).{0,80}(foreign|international|overseas)",
        "severity": "Medium",
        "risk_type": "Unfavorable Jurisdiction",
        "description": "Disputes must be resolved in an unfavorable or distant jurisdiction.",
    },
    {
        "pattern": r"indemnif.{0,100}(all|any|every).{0,30}(claim|loss|cost|damage)",
        "severity": "Medium",
        "risk_type": "Broad Indemnification",
        "description": "Broad indemnification obligation covering all claims and costs.",
    },
    {
        "pattern": r"net (?:60|90|120)|payment.{0,30}(?:60|90|120)\s+days",
        "severity": "Medium",
        "risk_type": "Long Payment Terms",
        "description": "Extended payment terms that may affect cash flow negatively.",
    },
    # LOW risk patterns
    {
        "pattern": r"confidential.{0,50}perpetual|confidential.{0,50}indefinite",
        "severity": "Low",
        "risk_type": "Perpetual Confidentiality",
        "description": "Confidentiality obligations last indefinitely.",
    },
    {
        "pattern": r"reasonable.{0,30}notice|prior.{0,20}written notice",
        "severity": "Low",
        "risk_type": "Notice Requirement",
        "description": "Advance notice required before certain actions.",
    },
]

# Role-based risk priority weights (higher = more important for this role)
ROLE_RISK_WEIGHTS: Dict[str, Dict[str, float]] = {
    "Freelancer": {
        "Payment": 2.0, "IP": 2.0, "Termination": 1.8,
        "Non-Compete": 1.9, "Liability": 1.2, "Confidentiality": 1.1,
        "Dispute Resolution": 1.3, "Penalties": 1.5,
    },
    "Tenant": {
        "Termination": 2.0, "Obligations": 1.8, "Penalties": 1.9,
        "Renewal": 1.8, "Liability": 1.2, "Payment": 1.5,
    },
    "Employee": {
        "IP": 2.0, "Non-Compete": 2.0, "Termination": 1.8,
        "Confidentiality": 1.5, "Obligations": 1.3, "Payment": 1.2,
    },
    "Business Owner": {
        "Liability": 2.0, "Payment": 1.8, "IP": 1.7,
        "Dispute Resolution": 1.6, "Termination": 1.5, "Penalties": 1.5,
    },
    "Vendor": {
        "Payment": 2.0, "Liability": 1.9, "Termination": 1.7,
        "Penalties": 1.8, "Dispute Resolution": 1.4, "IP": 1.2,
    },
    "General": {
        "Liability": 1.5, "Payment": 1.5, "Termination": 1.5,
        "IP": 1.3, "Penalties": 1.4, "Confidentiality": 1.2,
    },
}


class NLPService:
    """Singleton NLP service for clause analysis."""

    _instance: Optional["NLPService"] = None
    _embedder = None
    _faiss_index = None
    _indexed_clause_ids: List[str] = []

    @classmethod
    def get_instance(cls) -> "NLPService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._load_embedder()

    def _load_embedder(self):
        """Load sentence transformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading embedding model (all-MiniLM-L6-v2)...")
            NLPService._embedder = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("✅ Embedding model loaded")
        except Exception as e:
            logger.warning(f"⚠️  Could not load embedding model: {e}. Using keyword-only mode.")
            NLPService._embedder = None

    # ── Module 2: Clause Classification ──────────────────────────────────────

    def classify_clause(self, text: str) -> str:
        """Classify clause into a legal category using keyword matching."""
        text_lower = text.lower()
        scores: Dict[str, int] = {}

        for category, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[category] = score

        if not scores:
            return "General"

        return max(scores, key=scores.get)

    def embed_text(self, text: str) -> Optional[List[float]]:
        """Generate sentence embedding for a text chunk."""
        if NLPService._embedder is None:
            return None
        try:
            embedding = NLPService._embedder.encode(text, show_progress_bar=False)
            return embedding.tolist()
        except Exception as e:
            logger.warning(f"Embedding failed: {e}")
            return None

    # ── Module 3: Risk Assessment ─────────────────────────────────────────────

    def assess_clause_risk(
        self, text: str, category: str, user_role: str = "General"
    ) -> Dict[str, Any]:
        """
        Assess risk of a clause and return severity, score, and evidence.
        All risk flags are grounded in verbatim evidence from the text.
        """
        risks_found = []
        matched_severity_scores = {"High": 1.0, "Medium": 0.55, "Low": 0.25}

        for pattern_info in RISK_PATTERNS:
            match = re.search(pattern_info["pattern"], text, re.IGNORECASE | re.DOTALL)
            if match:
                # Evidence = verbatim matched text (Module 7 grounding)
                evidence_start = max(0, match.start() - 50)
                evidence_end = min(len(text), match.end() + 50)
                evidence_text = text[evidence_start:evidence_end].strip()

                risks_found.append({
                    "risk_type": pattern_info["risk_type"],
                    "description": pattern_info["description"],
                    "evidence_text": evidence_text,
                    "severity": pattern_info["severity"],
                })

        # Base score from category weight for role
        role_weights = ROLE_RISK_WEIGHTS.get(user_role, ROLE_RISK_WEIGHTS["General"])
        category_weight = role_weights.get(category, 1.0)

        # Calculate composite risk score
        if risks_found:
            severity_values = [matched_severity_scores[r["severity"]] for r in risks_found]
            base_score = max(severity_values)
            # Boost by number of risk signals (up to 1.0 cap)
            composite_score = min(1.0, base_score * (1 + 0.1 * (len(risks_found) - 1)))
            # Apply role weight
            composite_score = min(1.0, composite_score * (category_weight / 1.5))
        else:
            composite_score = 0.05 * (category_weight / 1.5)

        # Determine severity level
        if composite_score >= 0.65:
            overall_severity = "High"
        elif composite_score >= 0.35:
            overall_severity = "Medium"
        else:
            overall_severity = "Low"

        # Build reasoning
        if risks_found:
            top_risks = [r["risk_type"] for r in risks_found[:3]]
            reasoning = f"Detected {len(risks_found)} risk indicator(s): {', '.join(top_risks)}."
        else:
            reasoning = f"No critical risk patterns detected. Clause appears routine for category '{category}'."

        return {
            "risk_level": overall_severity,
            "risk_score": round(composite_score, 3),
            "risk_reasoning": reasoning,
            "risks": risks_found,
        }

    # ── Module 5: Risk Chain Analysis ─────────────────────────────────────────

    def find_related_clauses(
        self, target_embedding: List[float], all_embeddings: List[Tuple[str, List[float]]], top_k: int = 3
    ) -> List[str]:
        """Find semantically related clauses using cosine similarity."""
        if not target_embedding or not all_embeddings:
            return []

        target = np.array(target_embedding)
        related = []
        for clause_id, emb in all_embeddings:
            if emb is None:
                continue
            other = np.array(emb)
            # Cosine similarity
            sim = np.dot(target, other) / (np.linalg.norm(target) * np.linalg.norm(other) + 1e-8)
            related.append((clause_id, float(sim)))

        related.sort(key=lambda x: x[1], reverse=True)
        # Return top-k excluding identical (sim ≈ 1.0)
        return [cid for cid, sim in related if sim < 0.999][:top_k]

    def detect_risk_chains(self, clauses: List[Dict]) -> List[Dict[str, Any]]:
        """
        Detect dependency chains across clauses.
        Example: Payment → Penalty → Termination chain.
        """
        CHAIN_RULES = [
            {
                "title": "Payment → Penalty → Termination Chain",
                "categories": ["Payment", "Penalties", "Termination"],
                "description": (
                    "Missing a payment triggers financial penalties, which if unpaid "
                    "can lead to contract termination. This is a high-risk chain."
                ),
                "combined_risk": "High",
            },
            {
                "title": "IP Assignment → Confidentiality → Non-Compete Chain",
                "categories": ["IP", "Confidentiality"],
                "description": (
                    "IP assignment coupled with broad confidentiality clauses "
                    "may severely restrict your future activities."
                ),
                "combined_risk": "High",
            },
            {
                "title": "Dispute Resolution → Jurisdiction → Liability Chain",
                "categories": ["Dispute Resolution", "Liability"],
                "description": (
                    "Unfavorable dispute jurisdiction combined with unlimited liability "
                    "creates significant legal and financial exposure."
                ),
                "combined_risk": "Medium",
            },
            {
                "title": "Renewal → Payment Terms Chain",
                "categories": ["Renewal", "Payment"],
                "description": (
                    "Auto-renewal clauses combined with payment obligations lock you "
                    "into potentially unfavorable financial commitments."
                ),
                "combined_risk": "Medium",
            },
        ]

        # Build a category-to-clause map
        cat_clause_map: Dict[str, List[str]] = {}
        for clause in clauses:
            cat = clause.get("category", "General")
            if cat not in cat_clause_map:
                cat_clause_map[cat] = []
            cat_clause_map[cat].append(clause["id"])

        chains = []
        for rule in CHAIN_RULES:
            matched_clause_ids = []
            for cat in rule["categories"]:
                matched_clause_ids.extend(cat_clause_map.get(cat, []))

            if len(matched_clause_ids) >= 2:
                import uuid
                chains.append({
                    "chain_id": str(uuid.uuid4()),
                    "title": rule["title"],
                    "clauses": matched_clause_ids,
                    "combined_risk": rule["combined_risk"],
                    "description": rule["description"],
                })

        return chains

    # ── Module 6: What-If Analysis ─────────────────────────────────────────────

    def answer_what_if(
        self, query: str, clauses: List[Dict], user_role: str = "General"
    ) -> Dict[str, Any]:
        """
        Answer a what-if scenario query by finding relevant clauses
        and synthesizing a plain-language answer.
        """
        query_lower = query.lower()

        # Find relevant clauses via keyword overlap
        scored_clauses = []
        query_words = set(re.findall(r"\w+", query_lower))

        for clause in clauses:
            text_lower = clause.get("cleaned_text", "").lower()
            clause_words = set(re.findall(r"\w+", text_lower))
            overlap = len(query_words & clause_words)
            if overlap > 1:
                scored_clauses.append((clause, overlap))

        scored_clauses.sort(key=lambda x: x[1], reverse=True)
        relevant = [c for c, _ in scored_clauses[:5]]

        # Build consequences from matching risk patterns
        consequences = []
        evidence_list = []
        max_risk = "Low"
        risk_order = {"Low": 0, "Medium": 1, "High": 2}

        for clause in relevant:
            risk_result = self.assess_clause_risk(
                clause.get("cleaned_text", ""), clause.get("category", "General"), user_role
            )
            for risk in risk_result["risks"]:
                consequence = f"[{risk['severity']} Risk] {risk['risk_type']}: {risk['description']}"
                if consequence not in consequences:
                    consequences.append(consequence)
                    evidence_list.append({
                        "clause_id": clause.get("id", ""),
                        "category": clause.get("category", ""),
                        "evidence_text": risk["evidence_text"],
                        "risk_type": risk["risk_type"],
                    })
                if risk_order.get(risk["severity"], 0) > risk_order.get(max_risk, 0):
                    max_risk = risk["severity"]

        # Build plain-language answer
        if not relevant:
            answer = (
                f"Based on the uploaded contract, no specific clauses directly addressing "
                f"'{query}' were found. Please consult a legal professional for this scenario."
            )
        else:
            cat_list = list(set(c.get("category", "General") for c in relevant))
            if consequences:
                answer = (
                    f"For the scenario: '{query}' — the following contract sections are relevant: "
                    f"{', '.join(cat_list)}. "
                    f"Key risks identified include: {consequences[0] if consequences else 'None detected'}. "
                    f"Review the {len(relevant)} highlighted clause(s) carefully."
                )
            else:
                answer = (
                    f"The contract contains {len(relevant)} clause(s) related to '{query}' "
                    f"in the {', '.join(cat_list)} section(s). No critical risk patterns were detected "
                    f"for this scenario, but standard due diligence applies."
                )

        return {
            "answer": answer,
            "relevant_clauses": relevant,
            "consequences": consequences[:10],
            "risk_level": max_risk,
            "evidence": evidence_list,
        }

    # ── Module 8: Obligation Extraction ───────────────────────────────────────

    def extract_obligations(self, clauses: List[Dict]) -> List[Dict[str, Any]]:
        """
        Extract deadlines, payment timelines, notice periods from clauses.
        """
        obligation_patterns = [
            {
                "pattern": r"(?:pay|payment|remit).{0,60}(?:within|by|no later than)\s+([\w\s,]+)",
                "type": "Payment",
            },
            {
                "pattern": r"(?:notice|notify|written notice).{0,60}(?:within|of)\s+(\d+[\w\s]+)",
                "type": "Notice Period",
            },
            {
                "pattern": r"(?:renew|renewal).{0,60}(?:by|before|on)\s+([\w\s,]+\d{4}|\d+ days)",
                "type": "Renewal Deadline",
            },
            {
                "pattern": r"(?:deliver|submit|provide|complete).{0,80}(?:by|on|within)\s+([\w\s,]+)",
                "type": "Delivery Deadline",
            },
            {
                "pattern": r"\$\s*([\d,]+(?:\.\d{2})?)|(?:USD|EUR|GBP)\s*([\d,]+)",
                "type": "Financial Amount",
            },
        ]

        obligations = []
        import uuid

        for clause in clauses:
            text = clause.get("cleaned_text", "")
            for op in obligation_patterns:
                for match in re.finditer(op["pattern"], text, re.IGNORECASE | re.DOTALL):
                    evidence_start = max(0, match.start() - 30)
                    evidence_end = min(len(text), match.end() + 30)
                    evidence = text[evidence_start:evidence_end].strip()

                    # Determine party (heuristic: look for "Contractor", "Client", etc.)
                    party = "Unknown"
                    party_patterns = [
                        (r"\b(contractor|freelancer|service provider|vendor)\b", "Service Provider"),
                        (r"\b(client|customer|buyer|employer)\b", "Client"),
                        (r"\b(tenant|lessee)\b", "Tenant"),
                        (r"\b(landlord|lessor)\b", "Landlord"),
                        (r"\b(employee)\b", "Employee"),
                        (r"\b(employer|company)\b", "Employer"),
                    ]
                    for pp, role_name in party_patterns:
                        if re.search(pp, text[:200], re.IGNORECASE):
                            party = role_name
                            break

                    obligations.append({
                        "id": str(uuid.uuid4()),
                        "obligation_type": op["type"],
                        "party": party,
                        "description": match.group(0)[:200],
                        "deadline": match.group(1) if match.lastindex and match.lastindex >= 1 else None,
                        "amount": match.group(1) if op["type"] == "Financial Amount" else None,
                        "evidence_text": evidence,
                        "clause_id": clause.get("id"),
                    })

        return obligations
