#!/usr/bin/env python3
"""
GitHub Launch Checklist
=======================
Audit a GitHub repository before launch. Checks the ten things that decide
whether a repository looks ready for its first visitors - name, description,
topics, README, license, demo link, installation instructions, contributing
guide, issue templates and social preview.

Usage:
    python checklist.py owner/repo
    python checklist.py owner/repo --json
    python checklist.py owner/repo --token $GITHUB_TOKEN
    python checklist.py owner/repo --strict      # exit 1 if readiness < 8/10

Works on any public repository. A GitHub token is optional and only raises
the API rate limit.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

import requests

API = "https://api.github.com"
PASS = "pass"
WARN = "warn"
FAIL = "fail"
MANUAL = "manual"

OK_MARK = "\u2713"     # check
WARN_MARK = "\u26a0"   # warning
FAIL_MARK = "\u2717"   # cross

GENERIC_NAMES = {"test", "demo", "project", "repo", "repository", "app", "code", "stuff", "tmp"}


def fetch_repo(owner: str, name: str, token: str | None = None) -> dict:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "github-launch-checklist"}
    if token:
        headers["Authorization"] = "Bearer " + token
    r = requests.get("%s/repos/%s/%s" % (API, owner, name), headers=headers, timeout=30)
    if r.status_code == 404:
        raise SystemExit("Repository not found: %s/%s (check spelling, or it is private)" % (owner, name))
    if r.status_code == 403:
        raise SystemExit("GitHub API rate limit reached. Pass --token to raise it.")
    r.raise_for_status()
    return r.json()


def fetch_readme(owner: str, name: str, token: str | None = None) -> str:
    headers = {"Accept": "application/vnd.github.raw", "User-Agent": "github-launch-checklist"}
    if token:
        headers["Authorization"] = "Bearer " + token
    r = requests.get("%s/repos/%s/%s/readme" % (API, owner, name), headers=headers, timeout=30)
    if r.status_code != 200:
        return ""
    return r.text


def fetch_community(owner: str, name: str, token: str | None = None) -> dict:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "github-launch-checklist"}
    if token:
        headers["Authorization"] = "Bearer " + token
    r = requests.get("%s/repos/%s/%s/community/profile" % (API, owner, name),
                     headers=headers, timeout=30)
    if r.status_code != 200:
        return {}
    return r.json()


def check_name(name: str) -> tuple:
    if len(name) < 3 or name.lower() in GENERIC_NAMES:
        return FAIL, "name is generic - use the phrase people search for"
    if len(name) < 6:
        return WARN, "short name - descriptive names rank and read better"
    if not re.search(r"[a-z]", name):
        return WARN, "no lowercase letters - hard to type"
    return PASS, "descriptive and searchable"


def check_description(desc: str | None) -> tuple:
    if not desc:
        return FAIL, "missing - the About line is your storefront"
    if len(desc) < 20:
        return WARN, "very short - front-load the keywords"
    if len(desc) > 300:
        return WARN, "over 300 chars - trim to one clear line"
    return PASS, "present and well sized"


def check_topics(topics: list) -> tuple:
    n = len(topics or [])
    if n >= 5:
        return PASS, "%d topics" % n
    if n >= 3:
        return WARN, "%d/5 recommended" % n
    return FAIL, "%d topics - add at least 5" % n


def check_readme(words: int) -> tuple:
    if words >= 300:
        return PASS, "%d words" % words
    if words >= 100:
        return WARN, "%d words - expand with usage and examples" % words
    return FAIL, "missing or under 100 words"


def check_license(license_obj: dict | None) -> tuple:
    if not license_obj:
        return FAIL, "missing - add a license file"
    return PASS, license_obj.get("spdx_id") or "present"


def check_demo(homepage: str | None) -> tuple:
    if not homepage:
        return FAIL, "Missing - set a homepage, demo or docs link"
    return PASS, "homepage set"


def check_installation(readme_text: str) -> tuple:
    lowered = readme_text.lower()
    markers = ["## install", "### install", "pip install", "npm install", "npm i ",
               "cargo install", "go install", "git clone", "docker run", "quick start",
               "## usage", "## getting started"]
    for m in markers:
        if m in lowered:
            return PASS, "installation or quick start found"
    return FAIL, "no install or quick start section in the README"


def check_contributing(community: dict) -> tuple:
    files = (community or {}).get("files") or {}
    if files.get("contributing"):
        return PASS, "guide present"
    if files.get("code_of_conduct"):
        return WARN, "no CONTRIBUTING.md - community file exists, add the guide"
    return FAIL, "missing - add CONTRIBUTING.md"


def check_issue_templates(community: dict) -> tuple:
    files = (community or {}).get("files") or {}
    if files.get("issue_template"):
        return PASS, "templates present"
    return FAIL, "missing - add .github/ISSUE_TEMPLATE"


def run_checks(repo: dict, readme_text: str, community: dict) -> list:
    issues = (community or {}).get("files") or {}
    return [
        ("Repository name", *check_name(repo.get("name", ""))),
        ("Description", *check_description(repo.get("description"))),
        ("Topics", *check_topics(repo.get("topics") or [])),
        ("README", *check_readme(len(readme_text.split()))),
        ("License", *check_license(repo.get("license"))),
        ("Demo", *check_demo(repo.get("homepage"))),
        ("Installation", *check_installation(readme_text)),
        ("Contributing guide", *check_contributing(community)),
        ("Issue templates", *check_issue_templates(community)),
        ("Social preview", MANUAL, "check manually in repo Settings"),
    ]


def score(results: list) -> float:
    points = 0.0
    for _, status, _ in results:
        if status == PASS:
            points += 1.0
        elif status == WARN:
            points += 0.5
    return round(points, 1)


def render(repo: dict, results: list) -> str:
    full = repo.get("full_name", "?")
    lines = ["", "GitHub Launch Readiness", "\u2500" * 24, ""]
    for label, status, detail in results:
        mark = {PASS: OK_MARK, WARN: WARN_MARK, FAIL: FAIL_MARK, MANUAL: WARN_MARK}[status]
        lines.append("%-20s %s %s" % (label, mark, detail if detail else ""))
    total = score(results)
    lines += ["", "Launch readiness: %s/10" % ("%g" % total), "", "Repository: %s" % full, ""]
    return "\n".join(lines)


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Audit a GitHub repository before launch")
    ap.add_argument("repo", help="Repository in owner/repo format")
    ap.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"),
                    help="GitHub token (optional, raises rate limit)")
    ap.add_argument("--json", action="store_true", help="Output results as JSON")
    ap.add_argument("--strict", action="store_true", help="Exit 1 if readiness is below 8/10")
    args = ap.parse_args()

    if "/" not in args.repo:
        print("Invalid format: %s. Use owner/repo." % args.repo)
        return 2
    owner, name = args.repo.split("/", 1)

    repo = fetch_repo(owner, name, args.token)
    readme = fetch_readme(owner, name, args.token)
    community = fetch_community(owner, name, args.token)
    results = run_checks(repo, readme, community)

    if args.json:
        print(json.dumps({
            "repository": repo.get("full_name"),
            "readiness": score(results),
            "checks": [{"check": c, "status": s, "detail": d} for c, s, d in results],
        }, indent=2))
    else:
        print(render(repo, results))

    if args.strict and score(results) < 8:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
