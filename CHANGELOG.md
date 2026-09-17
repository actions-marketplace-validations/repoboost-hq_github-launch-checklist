# Changelog

All notable changes to this project are recorded here.

## [1.0.1] - 2026-09-18

### Added

- GitHub Action (`uses: repoboost-hq/github-launch-checklist@v1`) with a configurable `fail-under` threshold
- Docker image published to GHCR: `ghcr.io/repoboost-hq/github-launch-checklist`
- New `--fail-under N` CLI option (the `--strict` flag remains as an alias for 8)
- Self-check workflow that runs the action on this repository

## [1.0.0] - 2026-09-18

### Added

- Ten-point launch readiness audit: name, description, topics, README, license,
  demo, installation, contributing guide, issue templates, social preview
- CLI with `--json` and `--strict` modes
- Explanations and fixes for every check in `docs/checks.md`
- Test suite (26 tests) and CI across Python 3.9-3.12
