from __future__ import annotations

from dataclasses import dataclass

from .models import Job
from .normalization import normalize_text


@dataclass(frozen=True, slots=True)
class EvidenceSelection:
    narrative: str
    projects: tuple[str, ...]
    summaries: tuple[str, ...]


PUBLIC_EVIDENCE = {
    "ordr-now": (
        "Ordr.now",
        "end-to-end ownership of a multi-tenant hospitality platform across web, mobile, backend, data, cloud delivery, offline-first synchronization, and production verification",
    ),
    "ai-native-platform": (
        "AI-native multi-tenant delivery platform",
        "hands-on architecture and implementation of repository-grounded agent execution, multi-tenant workflows, automated verification, preview evidence, and controlled integration for a confidential client",
    ),
    "datagpt": (
        "DataGPT AI",
        "AI product engineering for analytics workflows, asynchronous system states, advanced visual results, and a node-based agent orchestration interface",
    ),
    "privv": (
        "PRIVV",
        "incremental modernization of a mature React production system while preserving behavior and continued delivery",
    ),
    "experience-digital": (
        "Experience Digital",
        "product-to-platform range across application modernization, cloud infrastructure, CI/CD, observability, AWS, and Azure",
    ),
    "chorefree": (
        "Chorefree Living",
        "frontend technical ownership for booking and scheduling workflows using React, TypeScript, and GraphQL",
    ),
}


def _selection(narrative: str, keys: tuple[str, ...]) -> EvidenceSelection:
    return EvidenceSelection(
        narrative=narrative,
        projects=tuple(PUBLIC_EVIDENCE[key][0] for key in keys),
        summaries=tuple(PUBLIC_EVIDENCE[key][1] for key in keys),
    )


def select_evidence(job: Job, narrative_hint: str | None = None) -> EvidenceSelection:
    text = normalize_text(" ".join([job.role, job.description, narrative_hint or ""]))

    # Platform roles can mention agentic automation without being agent-product
    # roles. Preserve the role's center of gravity instead of allowing one AI
    # keyword to displace the stronger infrastructure evidence.
    if any(
        term in text
        for term in (
            "devops engineer",
            "platform engineer",
            "infrastructure",
            "terraform",
            "observability",
            "developer experience",
        )
    ):
        return _selection("Platform engineering", ("ordr-now", "experience-digital"))

    if any(term in text for term in ("coding agent", "agentic", "autonomous agent", "developer productivity")):
        return _selection("AI-native / agentic engineering", ("ai-native-platform", "ordr-now"))

    if any(term in text for term in ("ai product", "analytics", "llm application", "workflow ux")):
        return _selection("AI product engineering", ("datagpt", "ordr-now"))

    if any(term in text for term in ("modernization", "legacy", "migration", "react architecture")):
        return _selection("Incremental modernization", ("privv", "experience-digital"))

    if any(term in text for term in ("frontend lead", "graphql", "scheduling", "booking")):
        return _selection("Senior frontend product engineering", ("privv", "chorefree"))

    return _selection("Senior software engineering", ("ordr-now", "experience-digital"))
