"""
Report Generation Service (Module 10)
Produces structured JSON reports and PDF exports.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger


class ReportGenerator:
    """Generates structured JSON and PDF risk reports."""

    @staticmethod
    def build_json_report(
        contract: Dict,
        clauses: list,
        risk_data: Dict,
        obligations: list,
        user_role: str = "General",
    ) -> Dict[str, Any]:
        """Consolidate all module outputs into a clean structured JSON report."""

        high_clauses = [c for c in clauses if str(c.get("risk_level", "")).upper() == "HIGH"]
        medium_clauses = [c for c in clauses if str(c.get("risk_level", "")).upper() == "MEDIUM"]
        low_clauses = [c for c in clauses if str(c.get("risk_level", "")).upper() == "LOW"]

        return {
            "report_metadata": {
                "contract_id": contract.get("id"),
                "contract_name": contract.get("original_name"),
                "generated_at": datetime.utcnow().isoformat(),
                "user_role": user_role,
                "app_version": "1.0.0",
            },
            "executive_summary": {
                "overall_risk_level": risk_data.get("overall_risk_level", "Low"),
                "overall_risk_score": risk_data.get("overall_risk_score", 0.0),
                "total_clauses_analyzed": len(clauses),
                "high_risk_count": len(high_clauses),
                "medium_risk_count": len(medium_clauses),
                "low_risk_count": len(low_clauses),
                "summary": risk_data.get("summary", ""),
            },
            "risk_breakdown": {
                "high": [ReportGenerator._clause_to_dict(c) for c in high_clauses],
                "medium": [ReportGenerator._clause_to_dict(c) for c in medium_clauses],
                "low": [ReportGenerator._clause_to_dict(c) for c in low_clauses],
            },
            "risk_chains": risk_data.get("risk_chains", []),
            "obligations": [ReportGenerator._obligation_to_dict(o) for o in obligations],
            "recommendations": risk_data.get("recommendations", []),
            "evidence_grounding": ReportGenerator._build_evidence_map(clauses),
        }

    @staticmethod
    def generate_pdf_report(report_data: Dict, output_path: str) -> bool:
        """Generate a PDF report using fpdf2 (installed) or reportlab."""
        # Try fpdf2 first
        try:
            from fpdf import FPDF
            
            class PDF(FPDF):
                def header(self):
                    self.set_font("Helvetica", "B", 16)
                    self.set_text_color(15, 23, 42)
                    self.cell(0, 10, "ClauseGuard AI - Contract Risk Assessment Report", ln=True, align="L")
                    self.set_font("Helvetica", "", 9)
                    self.set_text_color(100, 116, 139)
                    self.cell(0, 5, "Explainable Legal Risk Assessment & Decision Support", ln=True, align="L")
                    self.ln(5)
                    self.set_draw_color(226, 232, 240)
                    self.line(10, self.get_y(), 200, self.get_y())
                    self.ln(5)

                def footer(self):
                    self.set_y(-15)
                    self.set_font("Helvetica", "I", 8)
                    self.set_text_color(148, 163, 184)
                    self.cell(0, 10, f"Page {self.page_no()}", align="C")

            pdf = PDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()

            meta = report_data.get("report_metadata", {})
            summary = report_data.get("executive_summary", {})

            # Metadata section
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(30, 41, 59)
            pdf.cell(40, 7, "Contract File:", 0)
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 7, str(meta.get("contract_name", "Unknown")), ln=True)

            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(40, 7, "Active Role:", 0)
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 7, str(meta.get("user_role", "General")), ln=True)

            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(40, 7, "Overall Risk:", 0)
            pdf.set_font("Helvetica", "B", 11)
            risk_lvl = summary.get("overall_risk_level", "Low")
            if risk_lvl == "High":
                pdf.set_text_color(239, 68, 68)
            elif risk_lvl == "Medium":
                pdf.set_text_color(245, 158, 11)
            else:
                pdf.set_text_color(16, 185, 129)
            pdf.cell(0, 7, f"{risk_lvl} ({summary.get('overall_risk_score', 0):.0%} Exposure)", ln=True)

            pdf.ln(4)

            # Executive Summary
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(0, 9, "Executive Summary", ln=True)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(51, 65, 85)
            pdf.multi_cell(0, 5, summary.get("summary", "Analysis completed."))
            pdf.ln(5)

            # Stats
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(45, 8, f"Total Clauses: {summary.get('total_clauses_analyzed', 0)}", 1, 0, "C")
            pdf.cell(45, 8, f"High Risk: {summary.get('high_risk_count', 0)}", 1, 0, "C")
            pdf.cell(45, 8, f"Medium Risk: {summary.get('medium_risk_count', 0)}", 1, 0, "C")
            pdf.cell(45, 8, f"Low Risk: {summary.get('low_risk_count', 0)}", 1, 1, "C")
            pdf.ln(8)

            # High Risk Clauses
            high_clauses = report_data.get("risk_breakdown", {}).get("high", [])
            if high_clauses:
                pdf.set_font("Helvetica", "B", 12)
                pdf.set_text_color(239, 68, 68)
                pdf.cell(0, 8, "High-Risk Unfavorable Clauses", ln=True)
                for idx, c in enumerate(high_clauses[:6]):
                    pdf.set_font("Helvetica", "B", 9)
                    pdf.set_text_color(15, 23, 42)
                    pdf.cell(0, 6, f"Clause #{idx + 1} [{c.get('category', 'General')}]", ln=True)
                    pdf.set_font("Helvetica", "", 8)
                    pdf.set_text_color(71, 85, 105)
                    text_snippet = c.get("cleaned_text", "")[:280] + ("..." if len(c.get("cleaned_text", "")) > 280 else "")
                    pdf.multi_cell(0, 4, text_snippet)
                    pdf.set_font("Helvetica", "I", 8)
                    pdf.set_text_color(220, 38, 38)
                    pdf.multi_cell(0, 4, f"Reason: {c.get('risk_reasoning', '')}")
                    pdf.ln(3)

            # Recommendations
            recs = report_data.get("recommendations", [])
            if recs:
                pdf.ln(4)
                pdf.set_font("Helvetica", "B", 12)
                pdf.set_text_color(15, 23, 42)
                pdf.cell(0, 8, "Key Negotiation Counter-Terms", ln=True)
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(51, 65, 85)
                for r in recs[:6]:
                    pdf.multi_cell(0, 5, f"- {r}")

            pdf.output(output_path)
            logger.info(f"PDF report generated via fpdf2: {output_path}")
            return True

        except Exception as fpdf_err:
            logger.warning(f"fpdf2 failed ({fpdf_err}), trying reportlab fallback...")
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.lib import colors
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                HRFlowable, PageBreak
            )

            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2 * cm,
                leftMargin=2 * cm,
                topMargin=2.5 * cm,
                bottomMargin=2 * cm,
            )

            styles = getSampleStyleSheet()
            story = []

            # ── Header ────────────────────────────────────────────────────────
            title_style = ParagraphStyle(
                "title",
                parent=styles["Title"],
                fontSize=22,
                textColor=colors.HexColor("#0F172A"),
                spaceAfter=6,
            )
            subtitle_style = ParagraphStyle(
                "subtitle",
                parent=styles["Normal"],
                fontSize=11,
                textColor=colors.HexColor("#64748B"),
                spaceAfter=20,
            )
            heading_style = ParagraphStyle(
                "heading",
                parent=styles["Heading2"],
                fontSize=14,
                textColor=colors.HexColor("#1E293B"),
                spaceBefore=16,
                spaceAfter=8,
            )
            body_style = ParagraphStyle(
                "body",
                parent=styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor("#374151"),
                spaceAfter=6,
                leading=14,
            )

            meta = report_data.get("report_metadata", {})
            summary = report_data.get("executive_summary", {})

            story.append(Paragraph("ClauseGuard AI", title_style))
            story.append(Paragraph("Contract Risk Assessment Report", subtitle_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0")))
            story.append(Spacer(1, 12))

            # ── Metadata table ────────────────────────────────────────────────
            meta_data = [
                ["Contract:", meta.get("contract_name", "Unknown")],
                ["Generated:", meta.get("generated_at", "")[:19].replace("T", " ")],
                ["User Role:", meta.get("user_role", "General")],
                ["Overall Risk:", summary.get("overall_risk_level", "N/A")],
                ["Risk Score:", f"{summary.get('overall_risk_score', 0):.1%}"],
            ]
            meta_table = Table(meta_data, colWidths=[4 * cm, 12 * cm])
            meta_table.setStyle(TableStyle([
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#64748B")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(meta_table)
            story.append(Spacer(1, 16))

            # ── Summary ───────────────────────────────────────────────────────
            story.append(Paragraph("Executive Summary", heading_style))
            story.append(Paragraph(summary.get("summary", "No summary available."), body_style))

            # Stats row
            stats = [
                ["Total Clauses", "High Risk", "Medium Risk", "Low Risk"],
                [
                    str(summary.get("total_clauses_analyzed", 0)),
                    str(summary.get("high_risk_count", 0)),
                    str(summary.get("medium_risk_count", 0)),
                    str(summary.get("low_risk_count", 0)),
                ],
            ]
            stats_table = Table(stats, colWidths=[4 * cm] * 4)
            stats_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (1, 1), (1, 1), colors.HexColor("#FEE2E2")),
                ("BACKGROUND", (2, 1), (2, 1), colors.HexColor("#FEF3C7")),
                ("BACKGROUND", (3, 1), (3, 1), colors.HexColor("#D1FAE5")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("ROUNDEDCORNERS", [4]),
            ]))
            story.append(Spacer(1, 8))
            story.append(stats_table)

            # ── High Risk Clauses ─────────────────────────────────────────────
            high_clauses = report_data.get("risk_breakdown", {}).get("high", [])
            if high_clauses:
                story.append(PageBreak())
                story.append(Paragraph("🔴 High Risk Clauses", heading_style))
                for i, clause in enumerate(high_clauses[:10]):
                    story.append(Paragraph(
                        f"<b>Clause {i + 1} [{clause.get('category', 'General')}]</b>",
                        body_style
                    ))
                    story.append(Paragraph(
                        clause.get("cleaned_text", "")[:400] + "...",
                        body_style
                    ))
                    story.append(Paragraph(
                        f"<i>Risk Reason: {clause.get('risk_reasoning', '')}</i>",
                        ParagraphStyle("italic", parent=body_style, textColor=colors.HexColor("#EF4444"))
                    ))
                    story.append(Spacer(1, 8))

            # ── Obligations ───────────────────────────────────────────────────
            obligations = report_data.get("obligations", [])
            if obligations:
                story.append(Paragraph("📋 Obligations & Deadlines", heading_style))
                ob_data = [["Type", "Party", "Description", "Deadline/Amount"]]
                for ob in obligations[:20]:
                    ob_data.append([
                        ob.get("obligation_type", ""),
                        ob.get("party", ""),
                        ob.get("description", "")[:80],
                        ob.get("deadline") or ob.get("amount") or "—",
                    ])
                ob_table = Table(ob_data, colWidths=[3 * cm, 3 * cm, 8 * cm, 3 * cm])
                ob_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]))
                story.append(ob_table)

            # ── Recommendations ───────────────────────────────────────────────
            recommendations = report_data.get("recommendations", [])
            if recommendations:
                story.append(Paragraph("💡 Recommendations", heading_style))
                for rec in recommendations:
                    story.append(Paragraph(f"• {rec}", body_style))

            doc.build(story)
            logger.info(f"PDF report generated: {output_path}")
            return True

        except ImportError:
            logger.error("ReportLab not installed. Install with: pip install reportlab")
            return False
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return False

    @staticmethod
    def _clause_to_dict(clause) -> Dict:
        if hasattr(clause, "__dict__"):
            return {
                "id": str(clause.id),
                "category": clause.category.value if hasattr(clause.category, "value") else str(clause.category),
                "risk_level": clause.risk_level.value if hasattr(clause.risk_level, "value") else str(clause.risk_level),
                "risk_score": clause.risk_score,
                "risk_reasoning": clause.risk_reasoning,
                "cleaned_text": clause.cleaned_text,
                "page_number": clause.page_number,
            }
        return clause  # Already a dict

    @staticmethod
    def _obligation_to_dict(ob) -> Dict:
        if hasattr(ob, "__dict__"):
            return {
                "id": str(ob.id),
                "obligation_type": ob.obligation_type,
                "party": ob.party,
                "description": ob.description,
                "deadline": ob.deadline,
                "amount": ob.amount,
                "evidence_text": ob.evidence_text,
            }
        return ob

    @staticmethod
    def _build_evidence_map(clauses: list) -> Dict[str, Any]:
        """Map every risk finding back to its source clause for full evidence grounding."""
        evidence_map = {}
        for clause in clauses:
            clause_id = str(clause.id) if hasattr(clause, "id") else clause.get("id", "")
            if not clause_id:
                continue
            risks = clause.risks if hasattr(clause, "risks") else clause.get("risks", [])
            evidence_map[clause_id] = {
                "page_number": clause.page_number if hasattr(clause, "page_number") else clause.get("page_number"),
                "category": clause.category.value if hasattr(clause, "category") and hasattr(clause.category, "value") else clause.get("category"),
                "risk_evidences": [
                    {
                        "risk_type": r.risk_type if hasattr(r, "risk_type") else r.get("risk_type"),
                        "evidence_text": r.evidence_text if hasattr(r, "evidence_text") else r.get("evidence_text"),
                        "severity": r.severity.value if hasattr(r, "severity") and hasattr(r.severity, "value") else r.get("severity"),
                    }
                    for r in risks
                ],
            }
        return evidence_map
