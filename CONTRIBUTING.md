# Contributing to AI Cinema Studio

Thank you for considering a contribution. Issues, bug reports, documentation
improvements, tests, and focused pull requests are welcome.

## Before opening an issue

- Search existing issues to avoid duplicates.
- Include the application version, operating system, and Python version.
- Describe the smallest reproducible example and the expected behavior.
- Remove API keys, access tokens, personal data, private prompts, generated
  media, and local file paths from logs and screenshots.
- Do not publish security vulnerabilities or exposed credentials in a public
  issue. Follow [SECURITY.md](SECURITY.md) instead.

## Development setup

Python 3.10 or newer is required. The CI matrix includes Python 3.15; its Qt binding support is newer, so report any version-specific issues. From the repository root:

```bash
python -m venv .venv
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
# macOS / Linux
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
```

FFmpeg and FFprobe are optional for planning-only workflows and are required
for local rendering and quality-control workflows. Install them separately and
make sure the executables are available on `PATH`.

## Run checks

```bash
python -m compileall -q ai_cinema_factory ai_cinema_studio tests
python -m pytest -q
python build_factory_zip.py --check-only
```

Tests should use mock providers. Do not add tests that make paid API calls or
require a real provider credential. Tests must not contain real API keys.

## Pull request expectations

- Keep changes focused and explain the user-facing impact.
- Add or update tests for behavior changes.
- Update `README.md`, `CHANGELOG.md`, and relevant language documentation when
  behavior or setup instructions change.
- Preserve BYOK credential-safety behavior and the cost-guard limitations.
- Do not commit `.env`, credentials, local workspaces, generated media, logs,
  SQLite reference databases, build output, or personal files.
- State which checks you ran and which checks you could not run.

By submitting a contribution, you agree that it is provided under the
project's Apache License, Version 2.0, as applicable to your contribution.
