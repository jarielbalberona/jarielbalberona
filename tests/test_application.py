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
    def test_agentic_role_selects_agentic_evidence(self) -> None:
        selection = select_evidence(
            job("Senior Agentic AI Engineer", "Build coding agents with tool use and verification loops.")
        )
        self.assertEqual("AI-native / agentic engineering", selection.narrative)
        self.assertEqual(
            ("AI-native multi-tenant delivery platform", "Ordr.now"), selection.projects
        )

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

    def test_unknown_consequential_facts_remain_unresolved(self) -> None:
        resolved, unresolved = resolve_application_answers(
            {
                "work_authorization": "Are you authorized to work in the United States?",
                "notice_period": "What is your notice period?",
                "portfolio": "Portfolio URL",
            },
            {"portfolio": "https://jarielbalberona.dev"},
        )
        self.assertEqual({"portfolio": "https://jarielbalberona.dev"}, resolved)
        self.assertEqual(2, len(unresolved))


if __name__ == "__main__":
    unittest.main()
