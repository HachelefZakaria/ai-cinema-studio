# Changelog

## v1.9.0 — BYOK Cost Guard

- Added a Project Builder cost and usage guard with a project-wide USD limit.
- Added user-entered LLM allowance and normalized image/video/audio rates; no provider prices are hard-coded.
- Added preflight estimates, configurable contingency, and an explicit confirmation before starting a paid production.
- Added thread-safe per-request media reservations; new requests stop before dispatch if the configured limit would be exceeded.
- Added a non-secret `exports/cost_ledger.json` reservation ledger and a one-image-test budget check.
- Documented that estimates are not invoices or guaranteed exact billing caps; provider dashboards remain authoritative.
- Added tests for estimates, missing rates, persisted ledgers, and budget-stop behavior.

## v1.8.0 — Multilingual Studio

- Synchronized the desktop pages under the shared black / electric-blue / cinematic-red theme.
- Added English, French, and Arabic interface localization, including right-to-left layout for Arabic.
- Added per-project output-language selection with auto-detection and custom-language support.
- Added independent visual-prompt language selection (English recommended by default).
- Passed a shared language policy to Director, Scriptwriter, Visual, Audio Planning, and Assembler.
- Standardized UTF-8 for translation catalogs, logs, and Unicode JSON project metadata.
- Added tests for language policy and Unicode round-tripping.

## v1.7.0

- Added Project Builder workspace and planning timeline.
- Added early-stop image generation batching on non-retryable provider errors.
- Added BYOK credential-safety documentation.
