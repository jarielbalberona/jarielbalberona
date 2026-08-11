from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from job_search.ledger import Ledger
from job_search.models import CompanyOrigin, Job
from job_search.normalization import canonicalize_url


def fixture_job(source: str, url: str, source_id: str) -> Job:
    return Job(
        source=source,
        source_posting_id=source_id,
        role="Senior Product Engineer",
        company="International Systems Inc",
        description="Own the same production platform across TypeScript, Node.js, React and PostgreSQL.",
        original_url=url,
        company_origin=CompanyOrigin.INTERNATIONAL,
        remote_from_ph=True,
        engineering_domain_eligible=True,
    )


class DeduplicationTests(unittest.TestCase):
    def test_tracking_parameters_are_removed_but_job_identity_is_preserved(self) -> None:
        result = canonicalize_url(
            "https://ph.indeed.com/viewjob?jk=abc123&utm_source=email&from=serp"
        )
        self.assertEqual("https://ph.indeed.com/viewjob?jk=abc123", result)

    def test_same_underlying_job_from_two_sources_is_one_job(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "ledger.sqlite"
            with Ledger(db) as ledger:
                ledger.initialize()
                first_id, first_duplicate = ledger.upsert_job(
                    fixture_job("indeed_ph", "https://ph.indeed.com/viewjob?jk=abc", "abc")
                )
                second_id, second_duplicate = ledger.upsert_job(
                    fixture_job("linkedin", "https://linkedin.com/jobs/view/999", "999")
                )
                self.assertFalse(first_duplicate)
                self.assertTrue(second_duplicate)
                self.assertEqual(first_id, second_id)
                self.assertEqual(1, ledger.table_count("jobs"))
                self.assertEqual(2, ledger.table_count("job_sources"))


if __name__ == "__main__":
    unittest.main()
