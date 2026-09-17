"""Tests for github-launch-checklist - all pure checks, no network."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from checklist import (  # noqa: E402
    FAIL, MANUAL, PASS, WARN,
    check_contributing, check_demo, check_description, check_installation,
    check_issue_templates, check_license, check_name, check_readme, check_topics,
    render, run_checks, score,
)

GOOD_REPO = {
    "name": "cloudflare-turnstile-solver",
    "full_name": "example/cloudflare-turnstile-solver",
    "description": "Solve Cloudflare Turnstile challenges with a real browser fingerprint",
    "topics": ["cloudflare", "turnstile", "solver", "captcha", "python"],
    "license": {"spdx_id": "MIT"},
    "homepage": "https://example.com",
}
GOOD_README = """
# Cloudflare Turnstile Solver

Quick start:

    pip install turnstile-solver
    python -m solver

""" + ("word " * 320)

GOOD_COMMUNITY = {"files": {"contributing": {"url": "x"}, "issue_template": {"url": "y"}}}


class TestName(unittest.TestCase):
    def test_generic_fails(self):
        self.assertEqual(check_name("test")[0], FAIL)

    def test_short_warns(self):
        self.assertEqual(check_name("myapp")[0], WARN)

    def test_good_passes(self):
        self.assertEqual(check_name("github-launch-checklist")[0], PASS)


class TestDescription(unittest.TestCase):
    def test_missing_fails(self):
        self.assertEqual(check_description(None)[0], FAIL)

    def test_short_warns(self):
        self.assertEqual(check_description("tiny")[0], WARN)

    def test_good_passes(self):
        self.assertEqual(check_description("A clear line about what this does for developers")[0], PASS)


class TestTopics(unittest.TestCase):
    def test_zero_fails(self):
        self.assertEqual(check_topics([])[0], FAIL)

    def test_three_warns(self):
        self.assertEqual(check_topics(["a", "b", "c"])[0], WARN)

    def test_five_passes(self):
        self.assertEqual(check_topics(["a", "b", "c", "d", "e"])[0], PASS)


class TestReadme(unittest.TestCase):
    def test_empty_fails(self):
        self.assertEqual(check_readme(0)[0], FAIL)

    def test_thin_warns(self):
        self.assertEqual(check_readme(150)[0], WARN)

    def test_full_passes(self):
        self.assertEqual(check_readme(400)[0], PASS)


class TestLicenseDemoInstall(unittest.TestCase):
    def test_license_missing(self):
        self.assertEqual(check_license(None)[0], FAIL)

    def test_license_present(self):
        status, detail = check_license({"spdx_id": "MIT"})
        self.assertEqual(status, PASS)
        self.assertEqual(detail, "MIT")

    def test_demo_missing(self):
        self.assertEqual(check_demo(None)[0], FAIL)

    def test_demo_present(self):
        self.assertEqual(check_demo("https://example.com")[0], PASS)

    def test_install_marker(self):
        self.assertEqual(check_installation("run pip install thing")[0], PASS)

    def test_install_missing(self):
        self.assertEqual(check_installation("nothing here")[0], FAIL)


class TestCommunity(unittest.TestCase):
    def test_contributing_present(self):
        self.assertEqual(check_contributing(GOOD_COMMUNITY)[0], PASS)

    def test_contributing_missing(self):
        self.assertEqual(check_contributing({})[0], FAIL)

    def test_issue_templates_present(self):
        self.assertEqual(check_issue_templates(GOOD_COMMUNITY)[0], PASS)

    def test_issue_templates_missing(self):
        self.assertEqual(check_issue_templates({})[0], FAIL)


class TestScoringAndRender(unittest.TestCase):
    def test_perfect_score(self):
        results = run_checks(GOOD_REPO, GOOD_README, GOOD_COMMUNITY)
        # 9 machine checks pass; social preview is manual
        self.assertEqual(score(results), 9.0)

    def test_empty_repo_scores_low(self):
        results = run_checks({}, "", {})
        self.assertLessEqual(score(results), 1.0)

    def test_manual_check_present(self):
        results = run_checks({}, "", {})
        self.assertEqual(results[-1][1], MANUAL)

    def test_render_contains_summary(self):
        results = run_checks(GOOD_REPO, GOOD_README, GOOD_COMMUNITY)
        text = render(GOOD_REPO, results)
        self.assertIn("GitHub Launch Readiness", text)
        self.assertIn("/10", text)
        self.assertIn("example/cloudflare-turnstile-solver", text)


if __name__ == "__main__":
    unittest.main()
