# AI Cinema Studio v1.9.0

AI Cinema Studio is the desktop application for the AI Cinema & Video Factory engine.

A modular, model-agnostic Python system that turns a creative brief into a
validated production plan, generated images, generated video clips, generated
audio assets, a rendered MP4, and a machine-readable quality report.

> **Open-source release:** AI Cinema Studio is distributed under the Apache
> License 2.0. See [LICENSE](LICENSE), [CONTRIBUTING.md](CONTRIBUTING.md),
> [SECURITY.md](SECURITY.md), and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
>
> **Release status:** v1.9.0 includes automated tests using mock providers.
> Paid-provider live generation and a full Windows visual acceptance test have
> not been completed as part of this source-package preparation. Review the
> provider's current model access, quota, and pricing before enabling paid use.
> Cloud user accounts, hosted workers, payment processing, and a server-side
> Credits system are not included in this version.
>
> The repository is the complete source project. The v1.9.0 ZIP source
> distribution is not a signed installer; follow the Windows setup steps below.
> See [RELEASE_NOTES_v1.9.0.md](RELEASE_NOTES_v1.9.0.md) for the release summary
> and [CITATION.cff](CITATION.cff) for citation metadata. See
> [GITHUB_PUBLISH.md](GITHUB_PUBLISH.md) for publishing instructions and
> [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) for the final acceptance gates.

## Production stages

The pipeline is composed from independent agents and modality-specific provider
interfaces:

1. **Director Agent** — creates and validates the scene timeline.
2. **Scriptwriter Agent** — writes scene dialogue, voiceover, SFX cues, and music mood.
3. **Visual / Storyboard Agent** — creates detailed image and video prompts.
4. **Audio Planning Agent** — defines voice profiles, sound effects, and music mix directions.
5. **Image Generation Agent (optional)** — generates one still image per scene and can use a
   persistent SQLite visual-reference library for recurring characters and locations.
6. **Video Generation Agent (optional)** — generates a motion clip per scene.
7. **Audio Generation Agent (optional)** — generates actual dialogue/voiceover, sound effects,
   and music assets.
8. **Assembler / Export Agent** — merges validated outputs into a master project manifest,
   a frame-based multi-track timeline mapping, and an EDL.
9. **Video Renderer Agent (optional)** — uses FFmpeg to conform scene clips, mix generated
   audio tracks, and export a final MP4.
10. **Quality Control Agent (optional)** — uses FFprobe to inspect the final render, verify
    stream properties, duration, hashes, and source assets, then writes a QC report.

The implementation order is optimized to share a single validated project structure:
planning agents -> optional image/video/audio generation -> assembler -> renderer -> QC.

## Architecture

The project uses separate provider protocols for each modality:

- `LLMProvider` — OpenAI, DeepSeek, Gemini, Kimi/Moonshot, Groq, Mistral, Cohere,
  OpenRouter, Ollama/local, and Anthropic.
- `ImageProvider` — Google Gemini Image (Nano Banana 2 / Pro model IDs), OpenAI Images, Stability AI, and Replicate.
- `VideoProvider` — Runway and Replicate.
- `AudioProvider` — ElevenLabs (TTS, sound effects, and music) and OpenAI (TTS).

Providers are injected into agents for tests/custom integrations, or created from
settings. The LLM, image, video, and audio credentials are independent. A change in
one provider does not require rewriting the agent or changing the other modalities.

The desktop **Agent Model Hub** can save an independent LLM provider/model profile
for Director, Scriptwriter, Visual, Audio Planning, and Assembler. Any agent without
an override inherits the global LLM Center profile. Agent-specific API keys are kept
in the operating-system credential vault; runtime settings contain keys only in memory.

Google Nano Banana image generation uses the native Gemini Interactions API,
not the OpenAI-compatible LLM endpoint. The default image model is
`gemini-3.1-flash-image`; change the model ID in the New Production settings when
you have access to another Gemini image model. A Gemini key saved in LLM Center is
reused for image generation when Gemini is selected and no separate media key exists.
The New Production page includes a **Generate one test image** action. It sends one
image request only, asks for confirmation first, and saves the result under
`test_outputs/` without launching the full pipeline. Gemini image generation may
incur charges; check the current Google AI Studio pricing before confirming a request.

## Desktop workspace (v1.9.0)

The desktop app includes a project-builder workspace designed around a familiar editing-suite layout:

- A large creative-brief editor for the story, genre, and visual direction.
- A right-side Project Inspector with format, media, and output tabs.
- Project targets for runtime, scene count, aspect ratio, resolution, and frame rate.
- A production-sequence strip showing the real agent stages from story through delivery.
- A single-frame image test that is separate from the full multi-scene production run.

The interface uses a black / electric-blue / red visual identity. Project specifications are passed to the Director, manifest assembler, and media configuration; the Director retries invalid scene-count or runtime outputs within its configured attempt limit. Model output is still probabilistic, so the generated manifest should be reviewed before paid media generation.


### Project budget and cost guard

The desktop Project Builder includes a BYOK cost preflight and local reservation guard.
Users enter their own current normalized estimates for a project-wide LLM allowance,
image cost per generated image, video cost per generated second, and aggregate audio
cost per generated minute. The app calculates a project estimate, adds a configurable
contingency buffer, asks for confirmation before starting paid generation, and reserves
configured amounts before media-provider requests. If the next reservation would exceed
the project limit, that request is stopped before it is sent. A non-secret
`exports/cost_ledger.json` records local reservations.

Rates are intentionally user-entered rather than hard-coded because prices vary by
provider, model, account, resolution, region, and billing unit. The LLM amount is a
manual project allowance, not token-level metering. Media rates are normalized estimates
that may differ from provider billing. This feature is a local spend-control aid, not a
guaranteed invoice cap: provider billing dashboards and invoices remain authoritative,
and requests made outside this application are not covered. Disabling the guard removes
local preflight/reservation checks.

### Bring your own API key (BYOK)

Users connect their own provider accounts in LLM Center, Agent Model Hub, or Media Integrations. Credentials are stored through the operating-system credential vault when available. If the vault is unavailable, newly entered credentials remain in memory for the current app session only; the app does not write them to project manifests or plain-text settings files. Do not commit `.env`, credentials, generated workspaces, media, logs, or local reference databases. The `.gitignore` excludes these local artifacts.

A provider's successful connectivity test does not guarantee quota, billing eligibility, model access, or rate-limit capacity for generation. The app treats a hard zero-quota image response as non-retryable and cancels queued image-scene requests after the first failure to avoid unnecessary calls.

Run the desktop UI with:

```powershell
python run_studio.py
```

## Requirements

- Python 3.10 or newer. Python 3.15 uses the initial support provided by PySide6 6.12; see the current Qt for Python release notes before upgrading.
- Pydantic v2
- HTTPX
- FFmpeg and FFprobe executables for rendering and quality control
- Provider API credentials only for the generation stages you enable

Install Python dependencies:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Install FFmpeg separately using a trusted package manager or the official FFmpeg
builds for your operating system. Ensure both `ffmpeg` and `ffprobe` are available
on `PATH`, or pass explicit paths with `--ffmpeg` and `--ffprobe`.

## Configure credentials

Copy `.env.example` to `.env` for your own local reference, or export the required
variables in your shell. The application reads environment variables directly; it
does not automatically load `.env`, so install/use a dotenv loader in your own
launcher if desired.

Typical full-pipeline credentials:

| Stage | Environment variable | Provider |
|---|---|---|
| Text planning | `DEEPSEEK_API_KEY` | DeepSeek (or another LLM key) |
| Image generation | `GEMINI_API_KEY` | Gemini Nano Banana (or `OPENAI_API_KEY`, Stability, Replicate) |
| Video generation | `RUNWAYML_API_SECRET` | Runway (or Replicate) |
| TTS/SFX/music | `ELEVENLABS_API_KEY` | ElevenLabs |
| TTS only | `OPENAI_API_KEY` | OpenAI Speech |

For ElevenLabs, set `ELEVENLABS_VOICE_ID` or pass `--audio-voice-id`. The OpenAI
audio adapter currently supports speech synthesis; it does not generate sound
effects or music. The CLI disables those two asset types automatically when
`--audio-provider openai` is selected.

## Run a planning-only project

This calls the selected LLM provider and creates the timeline, script, storyboard,
audio plan, master JSON manifest, timeline mapping, and EDL. It does not generate
media or produce a final MP4.

```powershell
$env:DEEPSEEK_API_KEY = "your-llm-key"
python main.py --provider deepseek --model deepseek-chat --prompt "A cinematic mystery about a forgotten observatory receiving a signal from beneath the ocean."
```

For a local Ollama model:

```bash
ollama serve
python main.py --provider ollama --model llama3.1 --prompt "A short cinematic story about a lighthouse keeper during a storm."
```

## Run the full media pipeline

The full CLI sequence generates images, video clips, audio assets, renders the
final MP4, and runs quality control. `--render` intentionally requires both
`--generate-videos` and `--generate-audio` so a final export does not silently omit
one of the major media types.

Windows PowerShell example:

```powershell
$env:DEEPSEEK_API_KEY = "your-llm-key"
$env:OPENAI_API_KEY = "your-image-key"
$env:RUNWAYML_API_SECRET = "your-runway-key"
$env:ELEVENLABS_API_KEY = "your-elevenlabs-key"
$env:ELEVENLABS_VOICE_ID = "your-voice-id"

python main.py `
  --provider deepseek `
  --model deepseek-chat `
  --prompt "A cinematic science-fiction story about a lone explorer discovering an abandoned city on Mars." `
  --generate-images `
  --generate-videos `
  --generate-audio `
  --render `
  --quality-check
```

The same pipeline can use Replicate for image/video generation by selecting
`--image-provider replicate` or `--video-provider replicate` and supplying the
required `--image-model` / `--video-model` identifiers for the exact model you
intend to run. Replicate input parameters are model-specific; consult that model's
input schema before supplying extra settings.

OpenAI Speech-only example:

```powershell
$env:OPENAI_API_KEY = "your-openai-key"
python main.py --provider deepseek --model deepseek-chat --prompt "A short documentary about an ancient library." --generate-audio --audio-provider openai
```

This produces TTS audio only. Add a provider with SFX/music capabilities if the
render requires those tracks.

## CLI options

Run:

```bash
python main.py --help
```

Useful flags:

- `--generate-images` — enable Agent 06 image creation.
- `--generate-videos` — enable Agent 07 video clip creation.
- `--generate-audio` — enable Agent 08 TTS/SFX/music generation.
- `--render` — enable Agent 09 FFmpeg rendering; requires video and audio generation.
- `--quality-check` — enable Agent 10 FFprobe-based quality checks; requires rendering.
- `--frame-rate`, `--width`, `--height` — output timeline dimensions.
- `--ffmpeg`, `--ffprobe` — executable paths if not on `PATH`.

## Output layout

By default, output is written under `output/`:

```text
output/
├── exports/
│   ├── master_project_manifest.json
│   ├── master_timeline.edl
│   ├── final_video.mp4                 # when --render is enabled
│   └── quality_report.json             # when --quality-check is enabled
├── media/
│   ├── images/run_<run_id>/scene_001.png
│   ├── image_manifest.json
│   ├── video/run_<run_id>/scene_001.mp4
│   ├── video_manifest.json
│   ├── audio/run_<run_id>/scene_001/*.mp3
│   └── audio_manifest.json
├── references/
│   └── visual_reference_library.sqlite3
└── logs/
    ├── director_last_response.txt
    ├── scriptwriter_last_response.txt
    ├── visual_last_response.txt
    ├── audio_last_response.txt
    └── assembler_last_response.txt
```

The master manifest records generated media paths, MIME types, byte sizes,
checksums, timing, voice/speaker metadata, and generation provider/model details.
The timeline mapping contains video V1 and audio A1-A4 events. The EDL is a
CMX-3600-style video edit decision list; the full multi-track audio references are
preserved in the JSON manifest and timeline mapping.

## Multilingual production and UTF-8

The desktop UI includes English, French, and Arabic localization, with right-to-left
layout support for Arabic. The project builder separately lets users choose an
output language (or auto-detect from the creative brief) and a language for image/video
prompts. The project language is passed to Director, Scriptwriter, Visual, Audio Planning,
and Assembler through a shared language policy.

Creative output supports a broad set of selectable language names plus a custom language
entry. Actual comprehension, writing quality, dialect handling, and TTS voice availability
depend on the selected provider/model; UTF-8 preserves characters but does not grant a
model new language capabilities. English remains the recommended prompt language for
image/video models unless the selected model is known to perform well in another language.

All application-owned text files, diagnostics, JSON manifests, and translation catalogs
use UTF-8. JSON output uses `ensure_ascii=False` so Unicode text remains readable. API keys
remain in the OS credential vault when available and are never written to project files.

## Python API

```python
import asyncio
from ai_cinema_factory import AICinemaPipeline, PipelineContext

settings = {
    "llm": {
        "provider": "deepseek",
        "model": "deepseek-chat",
        "temperature": 0.4,
        "max_tokens": 4096,
    },
    "image_generation": {
        "enabled": True,
        "provider": "openai",
        "output_dir": "media/images",
    },
    "video_generation": {
        "enabled": True,
        "provider": "runway",
        "output_dir": "media/video",
    },
    "audio_generation": {
        "enabled": True,
        "provider": "elevenlabs",
        "output_dir": "media/audio",
        "default_voice_id": "your-voice-id",
        "generate_tts": True,
        "generate_sound_effects": True,
        "generate_music": True,
    },
    "renderer": {
        "enabled": True,
        "output_path": "exports/final_video.mp4",
        "allow_silent_output": False,
    },
    "quality_control": {
        "enabled": True,
        "report_path": "exports/quality_report.json",
        "require_audio": True,
        "fail_pipeline_on_failure": True,
    },
}

async def main() -> None:
    context = PipelineContext(workspace_dir="output")
    async with AICinemaPipeline(settings=settings, context=context) as pipeline:
        result = await pipeline.run(
            "A cinematic mystery about a signal under an ancient city.",
            project_title="The Signal Below",
        )
        print(result.export_output.manifest_path)
        if result.render_output is not None:
            print(result.render_output.output_path)
        if result.qc_report is not None:
            print("QC passed:", result.qc_report.passed)

asyncio.run(main())
```

Each stage passes validated Pydantic artifacts to the next stage. Provider objects
can be injected into `AICinemaPipeline(..., providers={...})` for tests or custom
integrations. See `ai_cinema_factory/pipeline.py` for supported injection keys.

## Build the ZIP archive

From the project root:

```bash
python build_factory_zip.py
```

The builder validates required source files and Python syntax, excludes secrets,
bytecode, caches, runtime logs, generated media, and existing ZIP files, then
writes a deterministic ZIP and `BUILD_MANIFEST.json` containing per-file SHA-256
hashes. Use `python build_factory_zip.py --check-only` to validate without writing.

## Tests

```bash
python -m pip install pytest
python -m pytest -q
```

Tests use mock providers for external APIs. Renderer/QC tests also create a short
local media fixture with FFmpeg when it is installed. They do not make paid API
calls; verify your API credentials and model access separately before production.
For development dependencies, use `python -m pip install -e ".[dev]"`.
Contributions are described in [CONTRIBUTING.md](CONTRIBUTING.md).

## Important operational notes

- Real image/video/audio generation incurs costs at the selected provider's rates.
  Generation flags are opt-in; planning-only runs do not call media-generation APIs.
- Image, video, and audio services have different model constraints and output
  formats. Check the selected model's API schema and account access.
- Long-running media APIs are asynchronous. Providers poll tasks with timeouts,
  bounded retries, and temporary-result handling; download generated media promptly
  because hosted output URLs may expire.
- FFmpeg/FFprobe must be installed externally; they are not Python dependencies.
- Generated assets are stored locally. The project does not yet include cloud
  object storage, a web dashboard, user authentication, or a distributed job queue.
- The quality-control agent checks file integrity and technical media properties;
  it does not replace human creative review.

---

## AI Cinema Studio Desktop App (new)

This repository also includes a native desktop interface built with PySide6. It
uses the existing `AICinemaPipeline` directly; it does not create a parallel or
mock pipeline.

### Launch on Windows

```powershell
# From the project root, with your virtual environment activated:
python -m pip install -r requirements.txt
python run_studio.py
```

The desktop workspace includes:

- **Overview** — project and export counts plus recent workspaces.
- **New Production** — creative brief, output workspace, and optional media stages. Image, video, and audio agents each have their own provider/model settings for the run.
- **LLM Center** — global provider/model/base URL settings and a real connection test.
- **Agent Model Hub** — independent LLM profiles for Director, Scriptwriter, Visual, Audio Planning, and Assembler, with global-profile inheritance and per-agent connection tests.
- **Agent Control** — live stage status and progress from the pipeline itself.
- **Export Library** — opens manifests, EDL files, QC reports, and rendered videos.
- **Media Integrations** — independent image, video, and audio credentials, including a Gemini credential that can be reused by Nano Banana.

The LLM Center supports the provider presets already implemented by the engine,
including Ollama/local models and custom OpenAI-compatible endpoints. For Ollama,
start the local Ollama service and select a model name that is already installed.

API keys are not written into the project workspace or application settings file.
The desktop app uses the operating-system credential vault through `keyring`
when a secure backend is available. When no secure backend is available, newly
entered values are retained in memory for the current application session only.

A planning-only project needs only a configured LLM provider. Image, video, audio,
rendering, and quality-control stages remain optional and require their respective
providers and credentials. Rendering also requires FFmpeg and FFprobe on `PATH`.

For text planning, the Agent Model Hub lets each of the five text agents use a
separate LLM provider and model. Unconfigured agents inherit the global LLM Center
profile. For media generation, New Production stores separate Image, Video, and
Audio provider/model selections for each run. Gemini image generation uses the
native Gemini Interactions API; the default is Nano Banana 2
(`gemini-3.1-flash-image`). The image size selector accepts `1K`, `2K`, and `4K`
for models that support those resolutions. Verify your Google account/model access
and review current pricing before enabling paid generation.

### Desktop development notes

- Launch entry point: `run_studio.py`
- UI package: `ai_cinema_studio/`
- Pipeline progress callback: `AICinemaPipeline.run(..., progress_callback=...)`
- The progress callback is optional and does not change existing CLI/API calls.
- The existing CLI remains available through `python main.py --help`.


## LLM connection diagnostics

If the LLM Center test fails, the application writes the full Python traceback to `logs/llm_test_traceback.log`. The API key value is redacted before the log is written. Share that log for troubleshooting; do not share API keys.
