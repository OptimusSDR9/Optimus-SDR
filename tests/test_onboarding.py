import unittest

from app.utils.onboarding import build_onboarding_steps


class OnboardingModuleTests(unittest.TestCase):
    def test_progress_increases_as_user_completes_steps(self):
        initial = build_onboarding_steps(total_leads=0, total_notes=0, settings_configured=False)

        self.assertEqual(initial["percent"], 0)
        self.assertFalse(initial["steps"][0]["completed"])

        completed = build_onboarding_steps(total_leads=1, total_notes=1, settings_configured=True)

        self.assertEqual(completed["completed"], 4)
        self.assertGreater(completed["percent"], initial["percent"])
        self.assertTrue(completed["steps"][0]["completed"])
        self.assertTrue(completed["steps"][3]["completed"])


if __name__ == "__main__":
    unittest.main()
