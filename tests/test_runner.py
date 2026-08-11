from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from job_search.ledger import Ledger
from job_search.runner import run_dry_run


class RunnerTests(unittest.TestCase):
    def test_existing_job_can_be_reassessed_without_duplicate_application(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "input.json"
            db_path = root / "ledger.sqlite"
            state_dir = root / "state"
            payload = {
                "run_id": "run_1",
                "source": "fixture",
                "mode": "DRY_RUN",
                "jobs": [
                    {
                        "role": "Senior Product Engineer",
                        "company": "International Product Company",
                        "description": "Own a TypeScript product platform and its production delivery.",
                        "original_url": "https://jobs.example.com/1",
                        "source_posting_id": "1",
                        "company_origin": "INTERNATIONAL",
                        "remote_from_ph": True,
                        "engineering_domain_eligible": True,
                        "rubric": {
                            "actual_responsibilities": 23,
                            "architecture_match": 14,
                            "career_direction_fit": 20,
                            "technical_stack": 9,
                            "ai_product_platform_relevance": 9,
                            "seniority_scope": 9,
                            "remote_compatibility": 10,
                        },
                        "analysis": {
                            "eligibility_confidence": 95,
                            "application_readiness": 90,
                        },
                    }
                ],
            }
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            first = run_dry_run(input_path, db_path=db_path, state_dir=state_dir)
            self.assertEqual(1, first["counts"]["strong_apply_count"])

            payload["run_id"] = "run_2"
            payload["reassess_existing"] = True
            payload["jobs"][0]["analysis"]["eligibility_confidence"] = 80
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            second = run_dry_run(input_path, db_path=db_path, state_dir=state_dir)

            self.assertEqual(1, second["counts"]["duplicate_count"])
            self.assertEqual(1, second["counts"]["reassessed_count"])
            with Ledger(db_path) as ledger:
                self.assertEqual(1, ledger.table_count("jobs"))
                self.assertEqual(2, ledger.table_count("assessments"))


if __name__ == "__main__":
    unittest.main()
