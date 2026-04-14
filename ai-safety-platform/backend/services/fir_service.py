from __future__ import annotations

import re
from datetime import datetime, timezone
from importlib import import_module
from io import BytesIO


def _load_reportlab():
    try:
        colors_module = import_module("reportlab.lib.colors")
        pagesizes_module = import_module("reportlab.lib.pagesizes")
        styles_module = import_module("reportlab.lib.styles")
        platypus_module = import_module("reportlab.platypus")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "reportlab is not installed. Install backend requirements before generating FIR PDFs."
        ) from exc

    return colors_module, pagesizes_module, styles_module, platypus_module


class FIRService:
    LEGAL_REFERENCES = [
        ("IT Act 2000 - Section 66C", "Identity theft and misuse of digital credentials."),
        ("IT Act 2000 - Section 67", "Publishing or transmitting obscene content in electronic form."),
        ("IT Act 2000 - Section 67B", "Child sexual abuse material and related exploitation."),
        ("IPC Section 354D", "Cyber stalking and repeated online harassment."),
        ("IPC Section 499/500", "Defamation through digital communication."),
        ("IPC Section 509", "Insulting the modesty of a person through words/gestures/messages."),
    ]

    def build_filename(self, username: str) -> str:
        cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", username).strip("_").lower() or "citizen"
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"fir_{cleaned}_{timestamp}.pdf"

    def generate_pdf(
        self,
        username: str,
        incident_description: str,
        evidence_notes: str | None,
        evidence_url: str | None,
    ) -> bytes:
        colors_module, pagesizes_module, styles_module, platypus_module = _load_reportlab()
        a4_page = getattr(pagesizes_module, "A4")
        paragraph_style_cls = getattr(styles_module, "ParagraphStyle")
        get_sample_style_sheet = getattr(styles_module, "getSampleStyleSheet")
        paragraph_cls = getattr(platypus_module, "Paragraph")
        simple_doc_template_cls = getattr(platypus_module, "SimpleDocTemplate")
        spacer_cls = getattr(platypus_module, "Spacer")
        table_cls = getattr(platypus_module, "Table")
        table_style_cls = getattr(platypus_module, "TableStyle")

        buffer = BytesIO()

        doc = simple_doc_template_cls(
            buffer,
            pagesize=a4_page,
            leftMargin=40,
            rightMargin=40,
            topMargin=36,
            bottomMargin=36,
        )

        styles = get_sample_style_sheet()
        title_style = paragraph_style_cls(
            "FIRTitle",
            parent=styles["Title"],
            fontSize=18,
            spaceAfter=10,
            textColor=colors_module.HexColor("#1f2937"),
        )
        body_style = paragraph_style_cls(
            "Body",
            parent=styles["BodyText"],
            leading=16,
            spaceAfter=10,
        )

        submitted_at = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")

        story = [
            paragraph_cls("First Information Report (Cyber Abuse)", title_style),
            paragraph_cls(f"<b>Complainant Name:</b> {username}", body_style),
            paragraph_cls(f"<b>Submission Time:</b> {submitted_at}", body_style),
            spacer_cls(1, 8),
            paragraph_cls("<b>Incident Description</b>", styles["Heading3"]),
            paragraph_cls(incident_description, body_style),
            spacer_cls(1, 6),
            paragraph_cls("<b>Evidence Information</b>", styles["Heading3"]),
            paragraph_cls(f"<b>Evidence Notes:</b> {evidence_notes or 'Not provided'}", body_style),
            paragraph_cls(f"<b>Evidence URL:</b> {evidence_url or 'Not provided'}", body_style),
            spacer_cls(1, 6),
            paragraph_cls("<b>Applicable Legal Sections (Reference)</b>", styles["Heading3"]),
        ]

        table_data = [["Act / Section", "Description"]] + [list(item) for item in self.LEGAL_REFERENCES]
        table = table_cls(table_data, colWidths=[170, 320])
        table.setStyle(
            table_style_cls(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors_module.HexColor("#111827")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors_module.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors_module.HexColor("#d1d5db")),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors_module.whitesmoke, colors_module.HexColor("#f9fafb")],
                    ),
                ]
            )
        )

        story.append(table)
        story.append(spacer_cls(1, 12))
        story.append(
            paragraph_cls(
                "This report has been generated by AI Safety & Smart FIR Platform and should be verified by law enforcement authorities.",
                paragraph_style_cls(
                    "Disclaimer",
                    parent=styles["Italic"],
                    textColor=colors_module.HexColor("#4b5563"),
                    fontSize=9,
                ),
            )
        )

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes


fir_service = FIRService()
