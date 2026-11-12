# v1.9.0 public-release checklist

Use this checklist before making the repository public or publishing a stable
GitHub Release.

## Prepared in this package

- [x] Apache License 2.0 file added.
- [x] README updated with current scope and unverified-integration limitations.
- [x] Contribution, support, security, citation, and third-party notices added.
- [x] GitHub Actions test workflow added.
- [x] Bug and feature issue templates added.
- [x] Pull request template and Dependabot configuration added.
- [x] `.gitignore` and `.gitattributes` reviewed and extended.
- [x] Source archive rebuilt with a fresh SHA-256 manifest.
- [x] Python compilation check passed.
- [x] Automated tests passed in the preparation environment.
- [x] Secret-pattern and local-path scans completed with no matches.

## Must be completed by the project owner before public publication

- [ ] Confirm that you own or have permission to publish every source file and
      contribution included in the repository.
- [ ] Confirm Apache-2.0 is the intended license. Once people receive a copy
      under an open-source license, you cannot simply revoke the rights already
      granted for that version.
- [ ] Replace the generic author entry in `CITATION.cff` with your preferred
      public author name or organization, if desired.
- [ ] Review the staged Git files and confirm that no local secrets, private
      projects, logs, generated media, or personal files are present.
- [ ] Run the desktop application on Windows and complete visual acceptance.
- [ ] Test at least one real LLM workflow using an account and model you are
      authorized to use.
- [ ] Test paid image/video/audio generation separately, with a small explicit
      budget, before claiming those integrations are verified.
- [ ] Enable GitHub private vulnerability reporting after creating the repo.
- [ ] Update release notes with any new results from Windows and provider tests.

## Do not mark these as complete based only on unit tests

- Live third-party API compatibility or provider quota availability.
- Full media generation from prompt to a playable MP4.
- Windows installer acceptance or signed installer verification.
- Cloud Edition, user accounts, payments, subscriptions, or server-side Credits.
