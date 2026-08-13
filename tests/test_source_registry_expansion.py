from __future__ import annotations

import unittest

from job_search.source_registry import (
    list_discovery_sources,
    load_source_registry,
    validate_source_registry,
)


class SourceRegistryExpansionTests(unittest.TestCase):
    def test_expanded_recurring_sources_and_priorities(self) -> None:
        registry = load_source_registry()
        expected = {
            "wellfound": ("JOB_BOARD", "P0"),
            "arc_dev": ("DEVELOPER_JOB_BOARD", "P0"),
            "dynamite_jobs": ("REMOTE_JOB_BOARD", "P0"),
            "we_work_remotely": ("REMOTE_JOB_BOARD", "P0"),
            "remote_yeah": ("REMOTE_JOB_BOARD", "P0"),
            "remoteok": ("REMOTE_JOB_BOARD", "P1"),
            "remotive": ("REMOTE_JOB_BOARD", "P1"),
            "working_nomads": ("REMOTE_JOB_BOARD", "P1"),
            "hiretalent_ph": ("PH_REMOTE_JOB_BOARD", "P1"),
            "filipino_contractors": ("PH_CONTRACTOR_JOB_BOARD", "P1"),
            "foundit_ph": ("GENERAL_JOB_BOARD", "P2"),
            "remote_talent_ph": ("PH_REMOTE_JOB_BOARD", "P2"),
            "remotify_ph": ("PH_EOR_REMOTE_SOURCE", "P2"),
            "turing": ("TALENT_NETWORK", "P2"),
            "toptal": ("TALENT_NETWORK", "P2"),
            "contra": ("PROFESSIONAL_FREELANCE_MARKETPLACE", "P2"),
            "dover": ("ATS", "P1"),
            "yc_work_at_a_startup": ("JOB_BOARD", "P1"),
            "justremote": ("REMOTE_JOB_BOARD", "P3"),
            "upwork": ("FREELANCE_MARKETPLACE", "P3"),
        }
        for source_id, (source_type, priority) in expected.items():
            with self.subTest(source=source_id):
                source = registry["sources"][source_id]
                self.assertTrue(source["enabled"])
                self.assertTrue(source["discovery"])
                self.assertEqual(source_type, source["type"])
                self.assertEqual(priority, source["priority"])
                self.assertIn("notes", source)

    def test_rotation_is_priority_sorted_and_priority_does_not_enter_scoring(self) -> None:
        rotation = list_discovery_sources()
        order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
        priorities = [order[source["priority"]] for source in rotation]
        self.assertEqual(sorted(priorities), priorities)
        for source in rotation:
            self.assertNotIn("fit_score", source)
            self.assertNotIn("score_weight", source)

    def test_registry_is_not_allowlist_and_paid_access_is_not_authorized(self) -> None:
        registry = load_source_registry()
        self.assertTrue(registry["registry_policy"]["preferred_not_allowlist"])
        self.assertTrue(registry["registry_policy"]["auto_add_reusable_sources"])
        self.assertFalse(registry["candidate_paid_access"]["default_authorized"])
        self.assertTrue(registry["candidate_paid_access"]["free_profile_creation_allowed"])

    def test_onlinejobs_is_disabled_and_opportunistic_sources_are_not_rotated(self) -> None:
        registry = load_source_registry()
        onlinejobs = registry["sources"]["onlinejobs_ph"]
        self.assertFalse(onlinejobs["enabled"])
        self.assertFalse(onlinejobs["discovery"])
        rotation_ids = {source["id"] for source in list_discovery_sources()}
        for source in registry["opportunistic_discovery"]["not_in_default_rotation"]:
            self.assertNotIn(source, rotation_ids)

    def test_job_trawlers_is_registered_for_manual_intake_without_automated_crawling(self) -> None:
        registry = load_source_registry()
        source = registry["sources"]["job_trawlers"]
        self.assertTrue(source["enabled"])
        self.assertFalse(source["discovery"])
        self.assertTrue(source["manual_intake_supported"])
        self.assertTrue(source["requires_account"])
        self.assertFalse(source["paid_access_required"])
        self.assertEqual("RESTRICTED", source["applicant_automation_policy"])
        self.assertEqual("https://jobtrawlers.com/terms", source["policy_evidence"])
        self.assertNotIn(
            "job_trawlers",
            {entry["id"] for entry in list_discovery_sources()},
        )

    def test_registry_has_no_invalid_types_priorities_or_duplicate_aliases(self) -> None:
        self.assertEqual([], validate_source_registry())


if __name__ == "__main__":
    unittest.main()
