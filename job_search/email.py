from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Iterable, Mapping

from .models import ResponseType, parse_date
from .normalization import normalize_company, normalize_role, normalize_text


@dataclass(frozen=True, slots=True)
class EmailCandidate:
    message_id: str
    sender: str
    subject: str
    body: str
    received_at: str


@dataclass(frozen=True, slots=True)
class EmailClassification:
    response_type: ResponseType
    confidence: float
    rationale: str


@dataclass(frozen=True, slots=True)
class EmailMatch:
    application_id: str | None
    confidence: float
    ambiguous: bool
    candidate_ids: tuple[str, ...]
    rationale: str


def classify_email(email: EmailCandidate) -> EmailClassification:
    body = normalize_text(email.body)
    combined = normalize_text(f"{email.subject}\n{email.body}")

    rules: tuple[tuple[ResponseType, tuple[str, ...], float], ...] = (
        (ResponseType.OFFER, ("offer of employment", "pleased to offer you", "formal offer"), 0.98),
        (
            ResponseType.REJECTION,
            ("will not be moving forward", "not moving forward", "unfortunately", "other candidates"),
            0.95,
        ),
        (
            ResponseType.INTERVIEW,
            ("schedule an interview", "interview availability", "meet with the team", "calendar link"),
            0.95,
        ),
        (
            ResponseType.ASSESSMENT,
            ("coding assessment", "technical assessment", "take-home", "take home", "online assessment"),
            0.94,
        ),
        (
            ResponseType.REQUEST_FOR_INFORMATION,
            ("provide the following", "additional information", "confirm your", "please answer"),
            0.88,
        ),
        (
            ResponseType.ACKNOWLEDGEMENT,
            ("application has been received", "thank you for applying", "we received your application"),
            0.93,
        ),
        (
            ResponseType.RECRUITER_CONTACT,
            ("would like to discuss", "interested in your background", "speak about the role", "next steps"),
            0.84,
        ),
    )

    for response_type, phrases, confidence in rules:
        matches = [phrase for phrase in phrases if phrase in combined]
        if matches and len(body) >= 20:
            return EmailClassification(response_type, confidence, f"body supports: {matches[0]}")

    return EmailClassification(ResponseType.OTHER, 0.35, "job-related intent is not clear enough")


def _sender_domain(sender: str) -> str:
    match = re.search(r"@([a-z0-9.-]+)", sender.casefold())
    return match.group(1) if match else ""


def match_email_to_application(
    email: EmailCandidate,
    applications: Iterable[Mapping[str, object]],
) -> EmailMatch:
    combined = normalize_text(f"{email.subject}\n{email.body}")
    sender_domain = _sender_domain(email.sender)
    received = parse_date(email.received_at)
    scored: list[tuple[int, str, list[str]]] = []

    for application in applications:
        app_id = str(application.get("application_id", ""))
        score = 0
        signals: list[str] = []
        company = str(application.get("company", ""))
        role = str(application.get("role", ""))
        employer_domain = str(application.get("employer_domain", ""))
        ats_domain = str(application.get("ats_domain", ""))

        if app_id and normalize_text(app_id) in combined:
            score += 10
            signals.append("explicit application id")
        if company and normalize_company(company) in normalize_company(combined):
            score += 4
            signals.append("company")
        role_tokens = set(normalize_role(role).split())
        if role_tokens and len(role_tokens & set(normalize_role(combined).split())) >= min(2, len(role_tokens)):
            score += 3
            signals.append("role")
        if sender_domain and employer_domain and sender_domain.endswith(employer_domain.casefold()):
            score += 3
            signals.append("employer sender")
        if sender_domain and ats_domain and sender_domain.endswith(ats_domain.casefold()):
            score += 2
            signals.append("ATS sender")

        applied = parse_date(str(application.get("date_applied", "")))
        if received and applied:
            distance = (received - applied).days
            if 0 <= distance <= 90:
                score += 1
                signals.append("timeframe")

        scored.append((score, app_id, signals))

    scored.sort(reverse=True)
    if not scored or scored[0][0] < 7:
        return EmailMatch(None, 0.0, False, (), "no application has sufficient matching signals")

    top_score = scored[0][0]
    contenders = [item for item in scored if top_score - item[0] < 2 and item[0] >= 7]
    if len(contenders) > 1:
        return EmailMatch(
            None,
            min(0.89, top_score / 12),
            True,
            tuple(item[1] for item in contenders),
            "multiple applications have materially similar signals",
        )

    top = scored[0]
    return EmailMatch(top[1], min(0.99, top[0] / 12), False, (top[1],), ", ".join(top[2]))
