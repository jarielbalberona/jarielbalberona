from __future__ import annotations

import unittest

from job_search.application import (
    ConfidentialityError,
    assert_public_safe,
    resolve_application_answers,
)
from job_search.evidence import select_evidence
from job_search.models import CompanyOrigin, Job
from job_search.normalization import fingerprint
from job_search.policy import EmployerExclusionMatcher, ExclusionIdentity
from job_search.positioning import (
    PositioningReasonCode,
    review_senior_positioning,
    strengthen_supported_positioning,
)


def job(role: str, description: str) -> Job:
    return Job(
        source="fixture",
        role=role,
        company="International Product Company",
        description=description,
        original_url="https://jobs.example.com/1",
        company_origin=CompanyOrigin.INTERNATIONAL,
        remote_from_ph=True,
    )


class ApplicationTests(unittest.TestCase):
    def test_senior_positioning_review_flags_weak_and_overclaimed_text(self) -> None:
        weak = review_senior_positioning("I am eager to learn CMS.")
        overclaim = review_senior_positioning("I am an expert in Adobe AEM.")
        strong = review_senior_positioning(
            "I architected and built custom content-management systems and publishing workflows."
        )
        self.assertEqual(
            (PositioningReasonCode.UNNECESSARY_UNDERSELL.value,), weak.reason_codes
        )
        self.assertEqual(
            (PositioningReasonCode.UNSUPPORTED_OVERCLAIM.value,),
            overclaim.reason_codes,
        )
        self.assertTrue(strong.passes)

    def test_known_cms_undersell_is_rewritten_with_supported_ownership(self) -> None:
        strengthened = strengthen_supported_positioning(
            "I have limited or no CMS experience."
        )
        self.assertIn("architecting and building custom", strengthened)
        self.assertTrue(review_senior_positioning(strengthened).passes)

    def test_forced_choice_cms_answer_requires_every_material_claim_to_be_supported(self) -> None:
        supported = review_senior_positioning(
            "I’ve worked with one or more CMS platforms for small to mid-sized businesses, "
            "freelance projects or personal projects."
        )
        enterprise_environment = review_senior_positioning(
            "I’ve contributed to components or features within larger, enterprise CMS "
            "environments - for example, templates, modules, or integrations."
        )
        large_scale = review_senior_positioning(
            "I have extensive, hands-on experience architecting, building, or maintaining "
            "large-scale CMS solutions - such as multi-site or multi-language builds, "
            "complex integrations, headless architectures, or high-traffic optimizations."
        )
        self.assertTrue(supported.passes)
        self.assertEqual(
            (PositioningReasonCode.UNSUPPORTED_OVERCLAIM.value,),
            enterprise_environment.reason_codes,
        )
        self.assertEqual(
            (PositioningReasonCode.UNSUPPORTED_OVERCLAIM.value,),
            large_scale.reason_codes,
        )

    def test_agentic_role_selects_agentic_evidence(self) -> None:
        selection = select_evidence(
            job("Senior Agentic AI Engineer", "Build coding agents with tool use and verification loops.")
        )
        self.assertEqual("AI-native / agentic engineering", selection.narrative)
        self.assertEqual(
            ("AI-native multi-tenant delivery platform", "Ordr.now"), selection.projects
        )

    def test_devops_role_keeps_platform_evidence_when_it_uses_agents(self) -> None:
        selection = select_evidence(
            job(
                "Senior DevOps Engineer",
                "Own AWS, Terraform, observability, and agentic automation for operational toil.",
            )
        )
        self.assertEqual("Platform engineering", selection.narrative)
        self.assertEqual(("Ordr.now", "Experience Digital"), selection.projects)

    def test_modernization_role_selects_modernization_evidence(self) -> None:
        selection = select_evidence(
            job("Senior Software Engineer", "Lead an incremental legacy React modernization and migration.")
        )
        self.assertEqual(("PRIVV", "Experience Digital"), selection.projects)

    def test_confidential_identity_is_rejected_from_public_text(self) -> None:
        private_name = "Hidden Current Client"
        matcher = EmployerExclusionMatcher(
            [
                ExclusionIdentity(
                    "private",
                    frozenset({fingerprint("company", private_name)}),
                    frozenset(),
                )
            ]
        )
        with self.assertRaises(ConfidentialityError):
            assert_public_safe(f"I currently build systems for {private_name}.", matcher)

    def test_canonical_notice_resolves_while_legal_fact_remains_unknown(self) -> None:
        resolved, unresolved = resolve_application_answers(
            {
                "work_authorization": "Are you authorized to work in the United States?",
                "notice_period": "What is your notice period?",
                "portfolio": "Portfolio URL",
            },
            {"portfolio": "https://jarielbalberona.dev"},
        )
        self.assertEqual(
            {
                "notice_period": "None",
                "portfolio": "https://jarielbalberona.dev",
            },
            resolved,
        )
        self.assertEqual(["Are you authorized to work in the United States?"], unresolved)


if __name__ == "__main__":
    unittest.main()
