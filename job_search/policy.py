from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .models import CompanyOrigin, EligibilityResult, Job, Verdict
from .normalization import fingerprint, normalize_text


POLICY_PATH = Path(__file__).parent / "policy" / "employer_exclusions.json"


@dataclass(frozen=True, slots=True)
class ExclusionIdentity:
    identity_id: str
    company_hashes: frozenset[str]
    domain_hashes: frozenset[str]


class EmployerExclusionMatcher:
    def __init__(self, identities: Iterable[ExclusionIdentity]):
        self.identities = tuple(identities)
        self.company_hashes = frozenset(h for item in self.identities for h in item.company_hashes)
        self.domain_hashes = frozenset(h for item in self.identities for h in item.domain_hashes)

    @classmethod
    def load(cls, path: Path = POLICY_PATH) -> "EmployerExclusionMatcher":
        data = json.loads(path.read_text(encoding="utf-8"))
        identities = [
            ExclusionIdentity(
                identity_id=item["id"],
                company_hashes=frozenset(item["company_hashes"]),
                domain_hashes=frozenset(item["domain_hashes"]),
            )
            for item in data["identities"]
        ]
        return cls(identities)

    def matches(self, companies: Iterable[str | None], domains: Iterable[str | None]) -> bool:
        company_match = any(
            value and fingerprint("company", value) in self.company_hashes for value in companies
        )
        domain_match = any(value and fingerprint("domain", value) in self.domain_hashes for value in domains)
        return bool(company_match or domain_match)

    def contains_in_text(self, text: str) -> bool:
        tokens = re.findall(r"[a-z0-9]+", normalize_text(text))
        for length in range(1, min(6, len(tokens) + 1)):
            for start in range(0, len(tokens) - length + 1):
                phrase = " ".join(tokens[start : start + length])
                if fingerprint("company", phrase) in self.company_hashes:
                    return True
        domains = re.findall(r"(?:https?://)?(?:www\.)?([a-z0-9.-]+\.[a-z]{2,})", text.casefold())
        return any(fingerprint("domain", value) in self.domain_hashes for value in domains)


DEPRIORITIZED_ROLE_PATTERNS = (
    r"\bjunior\b",
    r"\bmid[- ]?level\b",
    r"\bdata scientist\b",
    r"\bresearch scientist\b",
    r"\bmachine learning researcher\b",
    r"\bcuda\b",
    r"\bkernel engineer",
    r"\bwordpress\b",
    r"\bvirtual assistant\b",
)


def evaluate_eligibility(job: Job, matcher: EmployerExclusionMatcher | None = None) -> EligibilityResult:
    matcher = matcher or EmployerExclusionMatcher.load()
    if matcher.matches(
        companies=(job.company, job.actual_employer, job.destination_company),
        domains=(job.company_domain, job.destination_domain),
    ):
        return EligibilityResult(
            can_score=False,
            verdict=Verdict.SKIP,
            reason_codes=("CURRENT_EMPLOYER_EXCLUDED",),
            explanation="The actual or destination employer is confidentially excluded.",
        )

    if job.company_origin == CompanyOrigin.PHILIPPINES:
        return EligibilityResult(
            can_score=False,
            verdict=Verdict.SKIP,
            reason_codes=("PH_LOCAL_COMPANY",),
            explanation="The actual employer is confirmed Philippine-headquartered.",
        )

    if job.company_origin == CompanyOrigin.AMBIGUOUS:
        return EligibilityResult(
            can_score=False,
            verdict=Verdict.REVIEW,
            reason_codes=("COMPANY_ORIGIN_UNVERIFIED",),
            explanation="The actual employer origin is unresolved and must be verified.",
        )

    if job.remote_from_ph is False:
        return EligibilityResult(
            can_score=False,
            verdict=Verdict.SKIP,
            reason_codes=("REMOTE_PH_INELIGIBLE",),
            explanation="The role cannot be performed from the Philippines.",
        )

    if job.remote_from_ph is None:
        return EligibilityResult(
            can_score=False,
            verdict=Verdict.REVIEW,
            reason_codes=("REMOTE_PH_UNVERIFIED",),
            explanation="Remote-from-Philippines compatibility is unresolved.",
        )

    role_text = normalize_text(job.role)
    if any(re.search(pattern, role_text) for pattern in DEPRIORITIZED_ROLE_PATTERNS):
        return EligibilityResult(
            can_score=False,
            verdict=Verdict.SKIP,
            reason_codes=("ROLE_DEPRIORITIZED",),
            explanation="The role is outside the target senior hands-on engineering scope.",
        )

    if job.engineering_domain_eligible is False:
        return EligibilityResult(
            can_score=False,
            verdict=Verdict.SKIP,
            reason_codes=("ENGINEERING_DOMAIN_MISMATCH",),
            explanation="The actual responsibilities are outside product or platform engineering.",
        )

    if not job.active:
        return EligibilityResult(
            can_score=False,
            verdict=Verdict.SKIP,
            reason_codes=("INACTIVE_JOB",),
            explanation="The listing is no longer active.",
        )

    return EligibilityResult(can_score=True)
