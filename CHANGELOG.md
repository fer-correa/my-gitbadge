# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-08-09

### Added

- Initial version of the `my-gitbadge` project.
- Python script (`generate_badge.py`) to fetch contribution stats (commits, PRs, issues) from the GitHub API.
- Configuration via `config.yml` to specify user and target repositories.
- Generation of a dynamic SVG badge (`badge.svg`) based on fetched stats.
- GitHub Actions workflow (`.github/workflows/update-badge.yml`) for daily, automated badge updates.
- `README.md` with full setup and usage instructions.
- `requirements.txt` for managing Python dependencies.
- `VERSION` file for semantic versioning.
- `CHANGELOG.md` to document changes.
