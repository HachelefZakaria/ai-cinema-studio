# Publishing this source project to GitHub

This guide prepares the local source tree for a public repository. It does not
publish anything automatically.

## 1. Create an empty GitHub repository

On GitHub, create a repository named `ai-cinema-studio`.

- Choose **Public** only after you have reviewed the source and confirmed you
  have the right to publish every included file.
- Do not initialize it with a README, `.gitignore`, or license; these are
  already included in this source tree.
- Keep the GitHub repository URL handy.

## 2. Review the source tree before staging

Open PowerShell in the extracted project folder and run:

```powershell
git status --short
Get-ChildItem -Force
```

Confirm that no `.env` file, provider key, private project, generated media,
local database, log, or personal file is present. `.env.example` is safe; it
contains empty placeholders.

## 3. Initialize and push the repository

Configure your own Git identity if Git has not been configured on this computer:

```powershell
git config --global user.name "YOUR NAME"
git config --global user.email "YOUR VERIFIED GITHUB EMAIL"
```

Then initialize, review the staged file list, and create the first commit:

```powershell
git init
git branch -M main
git add .
git diff --cached --check
git status --short
git diff --cached --name-only
git commit -m "Publish AI Cinema Studio v1.9.0"
```

Inspect the staged file list before committing. Do not continue if you see an
`.env` file, generated workspace, `exports/`, `logs/`, private media, keys, or
personal files.

Add your actual repository URL and push:

```powershell
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/ai-cinema-studio.git
git push -u origin main
```

Replace `YOUR_GITHUB_USERNAME` with your GitHub username. Do not paste access
tokens or passwords into source files or commit messages. Authenticate through
the Git credential manager or GitHub's approved sign-in flow.

## 4. Configure repository settings

After the first push:

- Confirm the repository license is detected as Apache-2.0.
- Enable Issues and Discussions only if you plan to monitor them.
- Enable private vulnerability reporting under the Security settings.
- Keep branch protection in mind before accepting outside contributions.
- Add a short repository description and topics such as `python`,
  `multi-agent`, `generative-ai`, `ai-video`, `pyside6`, and `desktop-app`.
- Review Actions permissions and keep the CI workflow enabled.

## 5. Publish a GitHub Release only after acceptance testing

The v1.9.0 source release notes are in `RELEASE_NOTES_v1.9.0.md`. Before
creating a stable Release, complete the Windows installation/GUI acceptance test
and any provider integration tests you intend to advertise. The current source
package has not completed those checks.

When ready, create an annotated tag and push it:

```powershell
git tag -a v1.9.0 -m "AI Cinema Studio v1.9.0"
git push origin v1.9.0
```

Then use GitHub's Releases page to create a release from tag `v1.9.0` and paste
the contents of `RELEASE_NOTES_v1.9.0.md`. Do not describe untested paid
integrations as verified.
