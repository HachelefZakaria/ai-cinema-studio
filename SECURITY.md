# Security Policy

## API credentials

AI Cinema Studio follows a Bring Your Own Key (BYOK) model. Users connect their own provider accounts.

- Desktop API keys are stored through the operating-system credential vault when a supported keyring backend is available.
- If the secure vault is unavailable, a newly entered key is kept in memory for the current application session only; it is not written to a project file.
- Provider credentials are not included in project manifests, EDL files, or generated source archives.
- Never paste API keys into screenshots, issue reports, chat messages, source files, or Git commits.

## If a key is exposed

1. Revoke or rotate the key in the provider's official console immediately.
2. Create a replacement key and store it in the application's credential vault.
3. Check recent provider usage and billing activity.
4. Remove accidental copies from local files and repository history. Rewriting Git history does not make an exposed key safe again; revocation is still required.

## Reporting a vulnerability

Please do not publish active credentials, private user data, or exploitable vulnerability details in a public issue.

Before making the repository public, maintainers should enable **Private vulnerability reporting** in the repository's GitHub security settings. Once enabled, use the repository's **Security → Advisories → Report a vulnerability** flow. If private reporting is not enabled, contact the maintainers through a verified private channel before sharing sensitive details.

## Repository hygiene

The repository ignores `.env` files, local project workspaces, generated media, logs, reference databases, build outputs, and common private-key file extensions. Review staged changes before every commit. The `.env.example` file contains empty placeholders only and is safe to commit.

## Project cost ledger

The local `exports/cost_ledger.json` contains user-configured budget limits and request reservations only. It must not contain API credentials, prompts, generated media, or raw provider responses. Project workspaces and export folders are ignored by the repository `.gitignore`; do not add a private workspace to Git.

The cost guard is a local estimate/reservation aid. Provider billing dashboards remain authoritative, and it cannot account for requests made outside this app.
