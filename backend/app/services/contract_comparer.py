"""
Contract Comparison Service (Module 9)
Compares two contract versions, highlighting clause-level diffs.
"""

from difflib import SequenceMatcher
from typing import List, Dict, Any, Optional
from loguru import logger


RISK_ORDER = {"Low": 0, "Medium": 1, "High": 2}


class ContractComparer:
    """Compares two sets of contract clauses and detects changes."""

    @staticmethod
    def compare(
        clauses_a: List[Dict], clauses_b: List[Dict]
    ) -> Dict[str, Any]:
        """
        Compare two sets of clauses and return structured diff results.
        Uses category-aware matching + text similarity.
        """
        # Build category-to-clauses maps
        cat_map_a = ContractComparer._build_category_map(clauses_a)
        cat_map_b = ContractComparer._build_category_map(clauses_b)

        all_categories = set(cat_map_a.keys()) | set(cat_map_b.keys())
        diffs = []
        added = removed = modified = unchanged = 0

        for category in all_categories:
            clauses_in_a = cat_map_a.get(category, [])
            clauses_in_b = cat_map_b.get(category, [])

            if not clauses_in_a and clauses_in_b:
                # Clauses added in B
                for clause_b in clauses_in_b:
                    diffs.append({
                        "change_type": "added",
                        "category": category,
                        "text_a": None,
                        "text_b": clause_b.get("cleaned_text", ""),
                        "risk_delta": "new",
                        "risk_level_a": None,
                        "risk_level_b": clause_b.get("risk_level", "Low"),
                    })
                    added += 1

            elif clauses_in_a and not clauses_in_b:
                # Clauses removed in B
                for clause_a in clauses_in_a:
                    diffs.append({
                        "change_type": "removed",
                        "category": category,
                        "text_a": clause_a.get("cleaned_text", ""),
                        "text_b": None,
                        "risk_delta": "removed",
                        "risk_level_a": clause_a.get("risk_level", "Low"),
                        "risk_level_b": None,
                    })
                    removed += 1

            else:
                # Both exist — compare best-match pairs
                for clause_a in clauses_in_a:
                    best_match = ContractComparer._find_best_match(clause_a, clauses_in_b)
                    if best_match is None:
                        diffs.append({
                            "change_type": "removed",
                            "category": category,
                            "text_a": clause_a.get("cleaned_text", ""),
                            "text_b": None,
                            "risk_delta": "removed",
                            "risk_level_a": clause_a.get("risk_level", "Low"),
                            "risk_level_b": None,
                        })
                        removed += 1
                        continue

                    text_a = clause_a.get("cleaned_text", "")
                    text_b = best_match.get("cleaned_text", "")
                    similarity = SequenceMatcher(None, text_a, text_b).ratio()

                    risk_a = clause_a.get("risk_level", "Low")
                    risk_b = best_match.get("risk_level", "Low")
                    risk_delta = ContractComparer._compute_risk_delta(risk_a, risk_b)

                    if similarity > 0.95:
                        change_type = "unchanged"
                        unchanged += 1
                    else:
                        change_type = "modified"
                        modified += 1

                    diffs.append({
                        "change_type": change_type,
                        "category": category,
                        "text_a": text_a,
                        "text_b": text_b,
                        "risk_delta": risk_delta,
                        "risk_level_a": risk_a,
                        "risk_level_b": risk_b,
                    })

        # Build risk summary
        risk_summary = ContractComparer._build_risk_summary(diffs, added, removed, modified)

        return {
            "total_changes": added + removed + modified,
            "added": added,
            "removed": removed,
            "modified": modified,
            "unchanged": unchanged,
            "diffs": diffs,
            "risk_summary": risk_summary,
        }

    @staticmethod
    def _build_category_map(clauses: List[Dict]) -> Dict[str, List[Dict]]:
        result: Dict[str, List[Dict]] = {}
        for clause in clauses:
            cat = clause.get("category", "General")
            if cat not in result:
                result[cat] = []
            result[cat].append(clause)
        return result

    @staticmethod
    def _find_best_match(clause_a: Dict, clauses_b: List[Dict]) -> Optional[Dict]:
        """Find the most similar clause in B for a clause from A."""
        text_a = clause_a.get("cleaned_text", "")
        best_score = 0.3  # Minimum similarity threshold
        best_match = None

        for clause_b in clauses_b:
            text_b = clause_b.get("cleaned_text", "")
            score = SequenceMatcher(None, text_a[:500], text_b[:500]).ratio()
            if score > best_score:
                best_score = score
                best_match = clause_b

        return best_match

    @staticmethod
    def _compute_risk_delta(risk_a: Optional[str], risk_b: Optional[str]) -> str:
        if risk_a is None:
            return "new"
        if risk_b is None:
            return "removed"
        a_val = RISK_ORDER.get(risk_a, 0)
        b_val = RISK_ORDER.get(risk_b, 0)
        if b_val > a_val:
            return "increased"
        elif b_val < a_val:
            return "decreased"
        return "unchanged"

    @staticmethod
    def _build_risk_summary(
        diffs: List[Dict], added: int, removed: int, modified: int
    ) -> str:
        increased_risk = [d for d in diffs if d.get("risk_delta") == "increased"]
        new_high = [d for d in diffs if d.get("risk_level_b") == "High" and d.get("change_type") in ("added", "modified")]

        parts = [f"Contract B has {added} new clause(s), {removed} removed, and {modified} modified."]
        if increased_risk:
            parts.append(f"⚠️  {len(increased_risk)} clause(s) show increased risk in Contract B.")
        if new_high:
            parts.append(f"🔴 {len(new_high)} clause(s) are newly classified as High risk.")
        if not increased_risk and not new_high:
            parts.append("✅ No significant risk escalation detected between the two versions.")

        return " ".join(parts)
