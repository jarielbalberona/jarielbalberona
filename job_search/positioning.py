from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
import re


class PositioningReasonCode(StrEnum):
    UNNECESSARY_UNDERSELL = "UNNECESSARY_UNDERSELL"
    UNSUPPORTED_OVERCLAIM = "UNSUPPORTED_OVERCLAIM"


@dataclass(frozen=True, slots=True)
class PositioningIssue:
    reason_code: PositioningReasonCode
    explanation: str

    def to_dict(self) -> dict[str, str]:
        value = asdict(self)
        value["reason_code"] = self.reason_code.value
        return value


@dataclass(frozen=True, slots=True)
class PositioningReview:
    issues: tuple[PositioningIssue, ...]
    review_name: str = "SENIOR_POSITIONING_REVIEW"

    @property
    def passes(self) -> bool:
        return not self.issues

    @property
    def reason_codes(self) -> tuple[str, ...]:
        return tuple(issue.reason_code.value for issue in self.issues)

    def to_dict(self) -> dict[str, object]:
        return {
            "review": self.review_name,
            "status": "PASS" if self.passes else "REVISE",
            "reason_codes": list(self.reason_codes),
            "issues": [issue.to_dict() for issue in self.issues],
        }


CMS_STRONG_POSITIONING = (
    "I have substantial hands-on CMS engineering experience, including architecting and "
    "building custom content-management systems, content models, administration and publishing "
    "workflows, WordPress, Shopify, APIs, and database-backed content platforms."
)


_UNDERSSELL_PATTERNS = (
    r"\bi(?:'m| am) eager to learn\b",
    r"\bi(?:'m| am) willing to learn\b",
    r"\bi(?:'m| am) hoping to gain experience\b",
    r"\bi have little experience\b",
    r"\bi have limited or no experience\b",
    r"\bi have limited or no (?:direct )?cms experience\b",
    r"\bi would love the opportunity to learn\b",
    r"\bi(?:'m| am) still developing my experience\b",
)

_UNSUPPORTED_OVERCLAIM_PATTERNS = (
    r"\b(?:expert|specialist) (?:with|in) (?:adobe )?aem\b",
    r"\bdeep (?:hands-on )?(?:adobe )?aem experience\b",
    r"\b(?:expert|specialist) (?:with|in) sitecore\b",
    r"\bdeep (?:hands-on )?sitecore experience\b",
    r"\blarge-scale cms solutions\b",
    r"\blarger,? enterprise cms environments?\b",
    r"\bmulti-site or multi-language builds?\b",
    r"\bhigh-traffic (?:cms )?optimizations?\b",
    r"\bcomplex enterprise headless migrations?\b",
)


def strengthen_supported_positioning(text: str) -> str:
    """Rewrite only known evidence-backed weak CMS framing.

    Generic weak statements about unrelated technologies are intentionally not rewritten because
    doing so without capability evidence could create an overclaim.
    """

    replacements = (
        r"I have limited or no direct CMS experience, but I am eager to learn and grow in this area\.?",
        r"I have limited or no CMS experience\.?",
        r"I'm eager to learn CMS\.?",
        r"I am eager to learn CMS\.?",
    )
    strengthened = text
    for pattern in replacements:
        strengthened = re.sub(
            pattern,
            CMS_STRONG_POSITIONING,
            strengthened,
            flags=re.IGNORECASE,
        )
    return strengthened


def review_senior_positioning(text: str) -> PositioningReview:
    issues: list[PositioningIssue] = []
    for pattern in _UNDERSSELL_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            issues.append(
                PositioningIssue(
                    PositioningReasonCode.UNNECESSARY_UNDERSELL,
                    "The wording weakens supported senior experience or uses junior-style learning language.",
                )
            )
            break
    for pattern in _UNSUPPORTED_OVERCLAIM_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            issues.append(
                PositioningIssue(
                    PositioningReasonCode.UNSUPPORTED_OVERCLAIM,
                    "The wording claims unsupported CMS vendor specialization or enterprise-scale delivery.",
                )
            )
            break
    return PositioningReview(tuple(issues))


def assert_senior_positioning(text: str) -> PositioningReview:
    review = review_senior_positioning(text)
    if not review.passes:
        codes = ", ".join(review.reason_codes)
        raise ValueError(f"SENIOR_POSITIONING_REVIEW failed: {codes}")
    return review
