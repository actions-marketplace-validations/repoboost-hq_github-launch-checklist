# Contributing

Thanks for improving the GitHub Launch Checklist.

## Setup

```bash
git clone https://github.com/repoboost-hq/github-launch-checklist.git
cd github-launch-checklist
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

## Adding or changing a check

1. Every check is a small pure function in `checklist.py` returning `(status, detail)`.
2. Add unit tests in `tests/test_checklist.py` - no network calls in tests; pass fake repository data.
3. If the check reads new API data, extend `fetch_repo`, `fetch_readme` or `fetch_community` - and keep failure modes graceful (missing data means the check fails cleanly, never crashes).
4. Keep output stable: the report format is part of the interface.

## Rules

- One change per pull request, tests green (`python -m pytest tests/`).
- No new dependencies without a strong reason - the tool runs on `requests` alone.
- Checks must work on any public repository, with or without a token.

## Questions

Open an issue or message us on Telegram: https://t.me/AlpinTamhas928
