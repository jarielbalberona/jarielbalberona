from __future__ import annotations

import unittest

from job_search.email import EmailCandidate, classify_email, match_email_to_application
from job_search.models import ResponseType


def email(body: str, subject: str = "Application update", sender: str = "jobs@employer.com") -> EmailCandidate:
    return EmailCandidate("message-1", sender, subject, body, "2026-08-15T08:00:00+00:00")


class EmailTests(unittest.TestCase):
    def test_classification_fixtures(self) -> None:
        fixtures = {
            "Thank you for applying. We received your application and will review it.": ResponseType.ACKNOWLEDGEMENT,
            "I am interested in your background and would like to discuss the role.": ResponseType.RECRUITER_CONTACT,
            "Please complete the coding assessment using the link below.": ResponseType.ASSESSMENT,
            "We would like to schedule an interview. Please share your interview availability.": ResponseType.INTERVIEW,
            "Unfortunately, we will not be moving forward with your application.": ResponseType.REJECTION,
            "We are pleased to offer you the Senior Software Engineer position. This is a formal offer.": ResponseType.OFFER,
            "There has been an update to the portal. Sign in to see more.": ResponseType.OTHER,
        }
        for body, expected in fixtures.items():
            with self.subTest(expected=expected):
                self.assertEqual(expected, classify_email(email(body)).response_type)

    def test_correct_application_is_selected_when_signals_are_sufficient(self) -> None:
        message = email(
            "We would like to schedule an interview for the Senior Platform Engineer role at Acme Cloud.",
            sender="recruiter@acmecloud.com",
        )
        applications = [
            {
                "application_id": "app_acme",
                "company": "Acme Cloud",
                "role": "Senior Platform Engineer",
                "employer_domain": "acmecloud.com",
                "date_applied": "2026-08-11",
            },
            {
                "application_id": "app_other",
                "company": "Other Systems",
                "role": "Senior Product Engineer",
                "employer_domain": "other.example",
                "date_applied": "2026-08-11",
            },
        ]
        match = match_email_to_application(message, applications)
        self.assertEqual("app_acme", match.application_id)
        self.assertFalse(match.ambiguous)

    def test_ambiguous_match_stays_unresolved(self) -> None:
        message = email("Application update for Senior Software Engineer at Global Systems.")
        applications = [
            {
                "application_id": "app_one",
                "company": "Global Systems",
                "role": "Senior Software Engineer",
                "date_applied": "2026-08-11",
            },
            {
                "application_id": "app_two",
                "company": "Global Systems",
                "role": "Senior Software Engineer",
                "date_applied": "2026-08-12",
            },
        ]
        match = match_email_to_application(message, applications)
        self.assertTrue(match.ambiguous)
        self.assertIsNone(match.application_id)
        self.assertEqual(("app_two", "app_one"), match.candidate_ids)


if __name__ == "__main__":
    unittest.main()
