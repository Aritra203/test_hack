from __future__ import annotations

import re
from datetime import datetime, timezone
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from backend.models.schemas import AnalysisResultPayload, FIRGenerationRequest


class FIRService:
    def build_filename(self, complainant_name: str) -> str:
        safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", complainant_name).strip("_").lower() or "citizen"
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"fir_{safe}_{timestamp}.pdf"

    def generate_pdf(
        self,
        payload: FIRGenerationRequest,
        analysis: AnalysisResultPayload,
        evidence_urls: list[str],
    ) -> bytes:
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Title"],
            fontSize=18,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=12,
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["BodyText"],
            fontSize=10,
            leading=15,
            spaceAfter=8,
        )

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=32, rightMargin=32, topMargin=28, bottomMargin=28)
        story = []

        story.append(Paragraph("Smart FIR Report - Cyber Crime", title_style))
        story.append(Paragraph(f"<b>Complainant:</b> {payload.complainant_name}", body_style))
        story.append(Paragraph(f"<b>Contact:</b> {payload.complainant_contact}", body_style))
        story.append(Paragraph(f"<b>Location:</b> {payload.location}", body_style))
        story.append(Paragraph(f"<b>Incident Time:</b> {payload.incident_datetime.isoformat()}", body_style))
        story.append(Paragraph(f"<b>Subject is Minor:</b> {'Yes' if payload.subject_is_minor else 'No'}", body_style))
        story.append(Spacer(1, 8))

        story.append(Paragraph("<b>Incident Description</b>", styles["Heading3"]))
        story.append(Paragraph(payload.incident_description, body_style))
        if payload.accused_details:
            story.append(Paragraph(f"<b>Accused Details:</b> {payload.accused_details}", body_style))
        if payload.additional_notes:
            story.append(Paragraph(f"<b>Additional Notes:</b> {payload.additional_notes}", body_style))
        story.append(Spacer(1, 8))

        story.append(Paragraph("<b>AI Analysis Summary</b>", styles["Heading3"]))
        story.append(Paragraph(f"<b>Risk Level:</b> {analysis.risk_level}", body_style))
        story.append(Paragraph(f"<b>Toxicity Score:</b> {analysis.toxicity_score}", body_style))
        story.append(Paragraph(f"<b>Detected Language:</b> {analysis.detected_language}", body_style))
        story.append(Paragraph(f"<b>Escalation Detected:</b> {'Yes' if analysis.escalation_detected else 'No'}", body_style))
        story.append(Paragraph(f"<b>Context Summary:</b> {analysis.context_summary}", body_style))
        if analysis.grooming_signals:
            story.append(Paragraph(f"<b>Grooming Signals:</b> {', '.join(analysis.grooming_signals)}", body_style))
        story.append(Spacer(1, 8))

        label_table = [["Label", "Score"]] + [[lbl.label, f"{lbl.score:.4f}"] for lbl in analysis.labels]
        t1 = Table(label_table, colWidths=[220, 120])
        t1.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.HexColor("#f1f5f9")]),
                ]
            )
        )
        story.append(t1)
        story.append(Spacer(1, 8))

        law_table = [["Section", "Law", "Rationale"]] + [
            [sec.section, sec.law, sec.rationale] for sec in analysis.legal_sections
        ]
        t2 = Table(law_table, colWidths=[90, 120, 230])
        t2.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
                ]
            )
        )
        story.append(Paragraph("<b>Applicable Legal Sections</b>", styles["Heading3"]))
        story.append(t2)
        story.append(Spacer(1, 8))

        story.append(Paragraph("<b>Evidence Links (Cloudinary)</b>", styles["Heading3"]))
        for idx, url in enumerate(evidence_urls, start=1):
            story.append(Paragraph(f"{idx}. {url}", body_style))

        story.append(Spacer(1, 8))
        story.append(
            Paragraph(
                "This AI-generated FIR draft is intended for legal support and must be reviewed by law enforcement.",
                ParagraphStyle("Disclaimer", parent=styles["Italic"], fontSize=9, textColor=colors.HexColor("#475569")),
            )
        )

        doc.build(story)
        return buffer.getvalue()


fir_service = FIRService()

