from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from job_search.answers import AnswerStatus, resolve_question
from job_search.candidate import load_private_candidate_facts


PRIVATE_FACTS_PATH = Path(".job-search/private-candidate-facts.json")


class PrivateCandidateFactsTests(unittest.TestCase):
    def test_public_candidate_policy_contains_no_private_identity_or_salary_values(self) -> None:
        public_facts = json.loads(
            Path("job_search/policy/candidate_facts.json").read_text(encoding="utf-8")
        )
        self.assertNotIn("previous_salary", public_facts)
        self.assertNotIn("full_legal_name", public_facts.get("identity", {}))
        self.assertNotIn("mailing_address", public_facts.get("identity", {}))

    def test_private_candidate_store_is_ignored_and_does_not_leak_into_tracked_files(self) -> None:
        if not PRIVATE_FACTS_PATH.is_file():
            self.skipTest("private candidate-facts store is intentionally absent")

        ignored = subprocess.run(
            ["git", "check-ignore", "--quiet", str(PRIVATE_FACTS_PATH)],
            check=False,
        )
        self.assertEqual(0, ignored.returncode)
        self.assertEqual(0, PRIVATE_FACTS_PATH.stat().st_mode & 0o077)

        private_facts = json.loads(PRIVATE_FACTS_PATH.read_text(encoding="utf-8"))
        sensitive_values = (
            private_facts["legal_identity"]["full_legal_name"],
            private_facts["legal_identity"]["mailing_address"]["street"],
            private_facts["legal_identity"]["mailing_address"]["barangay"],
            private_facts["legal_identity"]["mailing_address"]["formatted"],
        )
        tracked = subprocess.run(
            ["git", "ls-files", "-z"],
            check=True,
            capture_output=True,
        ).stdout.split(b"\0")
        leaks: list[str] = []
        for raw_path in tracked:
            if not raw_path:
                continue
            path = Path(raw_path.decode())
            try:
                content = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, FileNotFoundError):
                continue
            for value in sensitive_values:
                if value and value in content:
                    leaks.append(f"{path}: private value present")
        self.assertEqual([], leaks)

    def test_local_private_legal_identity_and_address_round_trip_when_available(self) -> None:
        private_facts = load_private_candidate_facts()
        if not private_facts:
            self.skipTest("private candidate-facts store is intentionally absent")
        legal_name = resolve_question(
            "legal_name", "Please provide your full legal birth name."
        )
        mailing_address = resolve_question(
            "mailing_address", "Please provide your full mailing address."
        )
        self.assertEqual(
            private_facts["legal_identity"]["full_legal_name"], legal_name.answer
        )
        self.assertEqual(
            private_facts["legal_identity"]["mailing_address"]["formatted"],
            mailing_address.answer,
        )
        self.assertEqual(AnswerStatus.EXACT, legal_name.status)
        self.assertEqual(AnswerStatus.EXACT, mailing_address.status)


if __name__ == "__main__":
    unittest.main()
