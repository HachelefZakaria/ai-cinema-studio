"""CLI entry point for the AI Cinema & Video Factory."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import shutil
from pathlib import Path

from ai_cinema_factory import AICinemaPipeline, PipelineContext, PROVIDER_PRESETS


def shutil_which(executable: str) -> str | None:
    """Resolve an executable path or command name without invoking a shell."""
    candidate = Path(executable).expanduser()
    if candidate.is_file():
        return str(candidate.resolve())
    return shutil.which(executable)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a scene-planned AI video production package."
    )
    parser.add_argument("--prompt", required=True, help="Creative video concept")
    parser.add_argument(
        "--provider",
        default="deepseek",
        choices=sorted(PROVIDER_PRESETS),
        help="LLM provider preset (API credentials are read from environment variables)",
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Model identifier accepted by the selected provider",
    )
    parser.add_argument("--project-title", default=None)
    parser.add_argument("--project-id", default=None)
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--frame-rate", type=int, default=24)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument(
        "--generate-images",
        action="store_true",
        help="Generate one real still image per storyboard scene (uses a separate image API)",
    )
    parser.add_argument(
        "--image-provider",
        default="openai",
        choices=["gemini", "openai", "stability", "stability-ultra", "replicate"],
        help="Image generation provider; independent from the text LLM provider",
    )
    parser.add_argument(
        "--image-model",
        default=None,
        help="Image model ID; for Replicate use owner/name or owner/name:version",
    )
    parser.add_argument(
        "--image-size",
        default="1536x864",
        help="Image output dimensions (default 1536x864, 16:9)",
    )
    parser.add_argument(
        "--image-quality",
        default="high",
        choices=["auto", "low", "medium", "high", "xhigh", "max"],
    )
    parser.add_argument(
        "--generate-videos",
        action="store_true",
        help="Generate a motion clip for every scene (uses a separate video API).",
    )
    parser.add_argument(
        "--video-provider",
        default="runway",
        choices=["runway", "replicate"],
        help="Video generation provider; independent of the text and image providers.",
    )
    parser.add_argument(
        "--video-model",
        default=None,
        help="Video model ID. Defaults to Runway gen4.5; Replicate requires owner/name or owner/name:version.",
    )
    parser.add_argument(
        "--video-clip-duration",
        type=int,
        default=None,
        help="Optional fixed clip duration in seconds; otherwise derived from the scene duration.",
    )
    parser.add_argument(
        "--video-resolution",
        default="720p",
        choices=["480p", "720p", "1080p", "1k", "2k"],
    )
    parser.add_argument(
        "--video-fps",
        type=int,
        default=24,
        help="Video generator frame rate, separate from the NLE timeline frame rate (Runway Gen-4.5: 24 or 25).",
    )
    parser.add_argument("--generate-audio", action="store_true", help="Generate dialogue, voiceover, SFX, and music assets.")
    parser.add_argument("--audio-provider", default="elevenlabs", choices=["elevenlabs", "openai"], help="Audio synthesis provider.")
    parser.add_argument("--audio-model", default=None, help="Optional TTS model ID override.")
    parser.add_argument("--audio-voice-id", default=None, help="ElevenLabs voice ID; alternatively set ELEVENLABS_VOICE_ID.")
    parser.add_argument("--audio-voice", default="coral", help="OpenAI built-in TTS voice name.")
    parser.add_argument("--disable-sfx", action="store_true", help="Skip sound-effect generation.")
    parser.add_argument("--disable-music", action="store_true", help="Skip music generation.")
    parser.add_argument("--render", action="store_true", help="Render generated scene videos and audio to final MP4 using FFmpeg.")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="FFmpeg executable path.")
    parser.add_argument("--ffprobe", default="ffprobe", help="FFprobe executable path.")
    parser.add_argument("--quality-check", action="store_true", help="Run final media quality checks after rendering.")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return parser.parse_args()


async def async_main(args: argparse.Namespace) -> int:
    output_dir = args.output_dir.expanduser().resolve()
    logs_dir = output_dir / "logs"
    exports_dir = output_dir / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    settings = {
        "llm": {
            "provider": args.provider,
            "model": args.model,
            "temperature": 0.4,
            "max_tokens": 4096,
            "timeout_seconds": 120,
        },
        "director": {
            "max_attempts": 3,
            "raw_response_path": str(logs_dir / "director_last_response.txt"),
        },
        "scriptwriter": {
            "max_attempts": 3,
            "raw_response_path": str(logs_dir / "scriptwriter_last_response.txt"),
        },
        "visual_agent": {
            "max_attempts": 3,
            "raw_response_path": str(logs_dir / "visual_last_response.txt"),
            "aspect_ratio": "16:9",
            "default_art_style": "cinematic photorealism, coherent production design",
        },
        "audio_agent": {
            "max_attempts": 3,
            "raw_response_path": str(logs_dir / "audio_last_response.txt"),
        },
        "assembler_agent": {
            "max_attempts": 3,
            "raw_response_path": str(logs_dir / "assembler_last_response.txt"),
            "manifest_path": str(exports_dir / "master_project_manifest.json"),
            "edl_path": str(exports_dir / "master_timeline.edl"),
            "frame_rate": args.frame_rate,
            "width": args.width,
            "height": args.height,
            "project_title": args.project_title,
        },
    }
    if args.generate_images:
        image_settings = {
            "enabled": True,
            "provider": args.image_provider,
            "output_dir": str(output_dir / "media" / "images"),
            "manifest_path": str(output_dir / "media" / "image_manifest.json"),
            "reference_library_path": str(output_dir / "references" / "visual_reference_library.sqlite3"),
            "aspect_ratio": "16:9",
            "size": args.image_size,
            "quality": args.image_quality,
            "output_format": "png",
            "max_concurrency": 2,
            "max_attempts": 3,
        }
        if args.image_model:
            image_settings["model"] = args.image_model
        elif args.image_provider == "replicate":
            raise ValueError("--image-model is required when --image-provider replicate")
        settings["image_generation"] = image_settings

    if args.generate_videos:
        video_settings = {
            "enabled": True,
            "provider": args.video_provider,
            "output_dir": str(output_dir / "media" / "video"),
            "manifest_path": str(output_dir / "media" / "video_manifest.json"),
            "aspect_ratio": "16:9",
            "resolution": args.video_resolution,
            "fps": args.video_fps,
            "max_concurrency": 1,
            "max_attempts": 2,
        }
        if args.video_model:
            video_settings["model"] = args.video_model
        elif args.video_provider == "replicate":
            raise ValueError("--video-model is required when --video-provider replicate")
        if args.video_clip_duration is not None:
            video_settings["clip_duration_seconds"] = args.video_clip_duration
        settings["video_generation"] = video_settings

    if args.generate_audio:
        if args.audio_provider == "elevenlabs":
            voice_id = args.audio_voice_id or os.getenv("ELEVENLABS_VOICE_ID")
            if not voice_id:
                raise ValueError(
                    "ElevenLabs TTS requires --audio-voice-id or ELEVENLABS_VOICE_ID."
                )
            if not os.getenv("ELEVENLABS_API_KEY"):
                raise ValueError("Set ELEVENLABS_API_KEY before enabling audio generation.")
        elif args.audio_provider == "openai" and not os.getenv("OPENAI_API_KEY"):
            raise ValueError("Set OPENAI_API_KEY before enabling OpenAI audio generation.")
        audio_settings = {
            "enabled": True,
            "provider": args.audio_provider,
            "output_dir": str(output_dir / "media" / "audio"),
            "manifest_path": str(output_dir / "media" / "audio_manifest.json"),
            "default_voice_id": args.audio_voice_id or os.getenv("ELEVENLABS_VOICE_ID"),
            "default_voice": args.audio_voice,
            "generate_tts": True,
            "generate_sound_effects": args.audio_provider == "elevenlabs" and not args.disable_sfx,
            "generate_music": args.audio_provider == "elevenlabs" and not args.disable_music,
            "max_concurrency": 2,
            "max_attempts": 3,
            "tts_gain_db": 0.0,
            "voiceover_gain_db": -1.0,
            "music_gain_db": -18.0,
        }
        if args.audio_model:
            audio_settings["tts_model"] = args.audio_model
        settings["audio_generation"] = audio_settings

    if args.render:
        missing_media_flags = [
            flag for flag, enabled in (
                ("--generate-videos", args.generate_videos),
                ("--generate-audio", args.generate_audio),
            ) if not enabled
        ]
        if missing_media_flags:
            raise ValueError(
                "--render requires " + " and ".join(missing_media_flags)
                + "; use --generate-videos --generate-audio to render a complete film."
            )
        if not shutil_which(args.ffmpeg) or not shutil_which(args.ffprobe):
            raise ValueError("FFmpeg and FFprobe must be installed and available on PATH (or supplied with --ffmpeg/--ffprobe).")
        settings["renderer"] = {
            "enabled": True,
            "ffmpeg": args.ffmpeg,
            "ffprobe": args.ffprobe,
            "output_path": str(exports_dir / "final_video.mp4"),
            "preset": "medium",
            "crf": 20,
            "audio_bitrate": "192k",
            "allow_silent_output": False,
        }
    if args.quality_check:
        if not args.render:
            raise ValueError("--quality-check requires --render")
        settings["quality_control"] = {
            "enabled": True,
            "ffprobe": args.ffprobe,
            "report_path": str(exports_dir / "quality_report.json"),
            "check_asset_hashes": True,
            "require_audio": True,
            "fail_pipeline_on_failure": True,
        }

    context = PipelineContext(workspace_dir=output_dir)

    async with AICinemaPipeline(settings=settings, context=context) as pipeline:
        result = await pipeline.run(
            args.prompt,
            project_title=args.project_title,
            project_id=args.project_id,
        )

    print("\nAI Cinema pipeline completed successfully")
    print(f"Run ID: {context.run_id}")
    print(f"Scenes: {len(result.timeline.scenes)}")
    print(f"Duration: {result.export_output.project_manifest.total_duration_seconds:.2f}s")
    print(f"Manifest: {result.export_output.manifest_path}")
    print(f"EDL: {result.export_output.edl_path}")
    if result.image_output is not None:
        print(f"Generated scene images: {len(result.image_output.scenes)}")
        print(f"Image manifest: {result.image_output.manifest_path}")
    if result.video_output is not None:
        print(f"Generated scene video clips: {len(result.video_output.scenes)}")
        print(f"Video manifest: {result.video_output.manifest_path}")
    if result.audio_generation_output is not None:
        total_audio = sum(len(scene.assets) for scene in result.audio_generation_output.scenes)
        print(f"Generated audio assets: {total_audio}")
        print(f"Audio manifest: {result.audio_generation_output.manifest_path}")
    if result.render_output is not None:
        print(f"Final MP4: {result.render_output.output_path}")
    if result.qc_report is not None:
        print(f"Quality control: {'PASSED' if result.qc_report.passed else 'FAILED'}")
        print(f"QC report: {result.qc_report.report_path}")
    return 0


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    try:
        return asyncio.run(async_main(args))
    except KeyboardInterrupt:
        logging.getLogger(__name__).warning("Pipeline interrupted by user")
        return 130
    except Exception:
        logging.getLogger(__name__).exception("AI Cinema pipeline failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
