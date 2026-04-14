from __future__ import annotations

from backend.models.schemas import LegalSection


def map_to_indian_laws(label_scores: dict[str, float], grooming_signals: list[str], is_minor: bool) -> list[LegalSection]:
    sections: list[LegalSection] = []

    if label_scores.get("cyberbullying", 0) >= 0.4:
        sections.append(
            LegalSection(
                section="IPC 509",
                law="Indian Penal Code",
                rationale="Abusive/insulting online communication impacting dignity and modesty.",
            )
        )

    if label_scores.get("threat", 0) >= 0.45:
        sections.append(
            LegalSection(
                section="IPC 503/506",
                law="Indian Penal Code",
                rationale="Criminal intimidation detected through threatening language.",
            )
        )

    if label_scores.get("hate_speech", 0) >= 0.45:
        sections.append(
            LegalSection(
                section="IPC 153A",
                law="Indian Penal Code",
                rationale="Promotion of enmity or hatred based on protected identity indicators.",
            )
        )

    if label_scores.get("sexual_harassment", 0) >= 0.4:
        sections.append(
            LegalSection(
                section="IPC 354A/354D",
                law="Indian Penal Code",
                rationale="Sexual harassment and stalking markers detected in content.",
            )
        )

    if grooming_signals:
        sections.append(
            LegalSection(
                section="IT Act 67B",
                law="Information Technology Act, 2000",
                rationale="Signals indicate grooming or exploitative intent in digital communication.",
            )
        )
        if is_minor:
            sections.append(
                LegalSection(
                    section="POCSO Act Sections 11/12",
                    law="POCSO Act",
                    rationale="Minor-targeted sexual communication patterns detected.",
                )
            )

    if not sections:
        sections.append(
            LegalSection(
                section="IT Act 66C/66D",
                law="Information Technology Act, 2000",
                rationale="Potential misuse or abusive cyber conduct requiring investigation.",
            )
        )

    return sections

