# AI Cinema Studio v1.9.0

## Highlights

- Model-agnostic multi-agent production pipeline for planning and media tasks.
- Desktop Project Builder with English, French, and Arabic interface support.
- Independent LLM profiles for Director, Scriptwriter, Visual, Audio Planning,
  and Assembler agents, with a global profile fallback.
- BYOK provider configuration for supported text, image, video, and audio
  integrations.
- Project-level cost estimation and local request-reservation guard.
- Optional media generation, FFmpeg rendering, and FFprobe-based quality
  control.
- Automated tests based on mock providers.

## Important limitations

- The local cost guard uses user-entered estimates and reservations. It is not
  an exact token meter or a guaranteed provider invoice cap.
- Provider quotas, model access, prices, and API behavior depend on each
  provider and account. Check current provider documentation before paid use.
- No live paid-provider generation tests are included in this release check.
- A full Windows visual acceptance test has not yet been completed for this
  prepared source package.
- Cloud accounts, hosted job workers, subscription billing, and a server-side
  Credits ledger are not included in v1.9.0.
- Provider fallback is configured manually; automatic failover is not included.

## Verification in the preparation environment

- Python source compilation: passed.
- Automated test suite: 46 passed using mock providers.
- ZIP integrity: checked when the source archive was prepared.
- Live paid API requests: not performed.
- Windows GUI acceptance: pending.

This release archive is a source distribution, not a signed Windows installer.
