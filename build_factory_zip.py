#!/usr/bin/env python3
"""Validate and build a clean, reproducible ai_cinema_factory.zip archive.

Run from any working directory:
    python build_factory_zip.py

Or choose paths explicitly:
    python build_factory_zip.py --source-dir ./ --output ./dist/ai_cinema_factory.zip

The archive contains the ``ai_cinema_factory/`` and ``ai_cinema_studio/``
packages, tests, project documentation, license notices, example environment
file, CLI, and this build script. Runtime artifacts, credentials, bytecode, and
caches are never packaged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Iterable

ARCHIVE_NAME = "ai_cinema_studio_v1_9_0_source.zip"
REQUIRED_PATHS = (
    "ai_cinema_factory/__init__.py",
    "ai_cinema_factory/providers.py",  # Backward-compatible import path.
    "ai_cinema_factory/llm/__init__.py",
    "ai_cinema_factory/llm/providers.py",
    "ai_cinema_factory/llm/routing.py",
    "ai_cinema_factory/images/__init__.py",
    "ai_cinema_factory/images/providers.py",
    "ai_cinema_factory/images/reference_library.py",
    "ai_cinema_factory/videos/__init__.py",
    "ai_cinema_factory/videos/providers.py",
    "ai_cinema_factory/audio/__init__.py",
    "ai_cinema_factory/audio/providers.py",
    "ai_cinema_factory/rendering/__init__.py",
    "ai_cinema_factory/rendering/renderer.py",
    "ai_cinema_factory/rendering/quality_control.py",
    "ai_cinema_factory/agents/__init__.py",
    "ai_cinema_factory/agents/base_agent.py",
    "ai_cinema_factory/agents/director.py",
    "ai_cinema_factory/agents/scriptwriter.py",
    "ai_cinema_factory/agents/visual_agent.py",
    "ai_cinema_factory/agents/image_generation_agent.py",
    "ai_cinema_factory/agents/video_generation_agent.py",
    "ai_cinema_factory/agents/audio_generation_agent.py",
    "ai_cinema_factory/agents/audio_agent.py",
    "ai_cinema_factory/agents/assembler_agent.py",
    "ai_cinema_factory/core/__init__.py",
    "ai_cinema_factory/core/pipeline_context.py",
    "ai_cinema_factory/core/cost_guard.py",
    "ai_cinema_factory/core/language_policy.py",
    "ai_cinema_factory/pipeline.py",
    "ai_cinema_studio/__init__.py",
    "ai_cinema_studio/settings_store.py",
    "ai_cinema_studio/i18n.py",
    "ai_cinema_studio/project_specs.py",
    "ai_cinema_studio/workers.py",
    "ai_cinema_studio/window.py",
    "run_studio.py",
    "main.py",
    "README.md",
    "requirements.txt",
    "pyproject.toml",
    ".env.example",
)
ROOT_FILES = (
    "main.py",
    "run_studio.py",
    "README.md",
    "requirements.txt",
    "pyproject.toml",
    ".env.example",
    ".gitignore",
    "SECURITY.md",
    "CHANGELOG.md",
    "LANGUAGE_SUPPORT.md",
    "LICENSE",
    "NOTICE",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SUPPORT.md",
    "CITATION.cff",
    "RELEASE_NOTES_v1.9.0.md",
    "THIRD_PARTY_NOTICES.md",
    "GITHUB_PUBLISH.md",
    "RELEASE_CHECKLIST.md",
    "build_factory_zip.py",
)
EXCLUDED_DIRS = {
    "__pycache__",
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "output",
    "workspace",
    "projects",
    "test_outputs",
    "references",
    "logs",
    "media",
    "exports",
    "dist",
    "build",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".log", ".tmp", ".pem", ".p12", ".key"}
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)


class BuildError(RuntimeError):
    """Raised when the source project is incomplete or cannot be archived."""


def _is_excluded(path: Path) -> bool:
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return True
    if path.name == ".env" or path.name.startswith(".env.") and path.name != ".env.example":
        return True
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return True
    if path.name.endswith("_last_response.txt"):
        return True
    if path.suffix.lower() == ".zip":
        return True
    return False


def _collect_files(source_root: Path) -> list[Path]:
    package_roots = [source_root / "ai_cinema_factory", source_root / "ai_cinema_studio"]
    if not package_roots[0].is_dir():
        raise BuildError(f"Missing package directory: {package_roots[0]}")

    candidates: set[Path] = set()
    for package_root in package_roots:
        if not package_root.is_dir():
            continue
        for path in package_root.rglob("*.py"):
            if path.is_file() and not _is_excluded(path.relative_to(source_root)):
                candidates.add(path)

    for relative_name in ROOT_FILES:
        path = source_root / relative_name
        if path.is_file() and not _is_excluded(Path(relative_name)):
            candidates.add(path)

    # UTF-8 translation catalogs are runtime package data, not Python source.
    locale_root = source_root / "ai_cinema_studio" / "locales"
    if locale_root.is_dir():
        for path in locale_root.glob("*.json"):
            if path.is_file() and not _is_excluded(path.relative_to(source_root)):
                candidates.add(path)

    tests_root = source_root / "tests"
    if tests_root.is_dir():
        for path in tests_root.rglob("*.py"):
            if path.is_file() and not _is_excluded(path.relative_to(source_root)):
                candidates.add(path)

    missing = [name for name in REQUIRED_PATHS if not (source_root / name).is_file()]
    if missing:
        raise BuildError(
            "Required project files are missing:\n  - " + "\n  - ".join(missing)
        )

    return sorted(candidates, key=lambda item: item.relative_to(source_root).as_posix())


def _validate_python(files: Iterable[Path], source_root: Path) -> int:
    checked = 0
    errors: list[str] = []
    for path in files:
        if path.suffix != ".py":
            continue
        relative = path.relative_to(source_root).as_posix()
        try:
            source = path.read_text(encoding="utf-8")
            compile(source, relative, "exec")
            checked += 1
        except (OSError, UnicodeError, SyntaxError) as exc:
            errors.append(f"{relative}: {exc}")
    if errors:
        raise BuildError("Python syntax validation failed:\n  - " + "\n  - ".join(errors))
    return checked


def _zip_info(archive_name: str, executable: bool = False) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(archive_name, date_time=ZIP_EPOCH)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    mode = stat.S_IFREG | (0o755 if executable else 0o644)
    info.external_attr = mode << 16
    return info


def build_archive(source_root: Path, output_path: Path) -> tuple[Path, int, int]:
    source_root = source_root.resolve()
    output_path = output_path.expanduser().resolve()
    files = _collect_files(source_root)
    checked_python = _validate_python(files, source_root)

    # Content hashes make the archive self-describing and help verify transfers.
    manifest_entries = []
    payloads: list[tuple[str, bytes, bool]] = []
    for path in files:
        relative = path.relative_to(source_root).as_posix()
        data = path.read_bytes()
        executable = bool(path.stat().st_mode & stat.S_IXUSR)
        payloads.append((relative, data, executable))
        manifest_entries.append(
            {
                "path": relative,
                "size_bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )

    build_manifest = {
        "archive": output_path.name,
        "package_version": "1.9.0",
        "python_files_syntax_checked": checked_python,
        "files": manifest_entries,
    }
    manifest_bytes = (json.dumps(build_manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=f".{output_path.stem}.",
            suffix=".tmp",
            dir=output_path.parent,
            delete=False,
        ) as handle:
            temp_path = Path(handle.name)

        with zipfile.ZipFile(temp_path, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for relative, data, executable in payloads:
                archive.writestr(_zip_info(relative, executable), data)
            archive.writestr(_zip_info("BUILD_MANIFEST.json"), manifest_bytes)

        # Verify central directory and all member CRCs before publishing.
        with zipfile.ZipFile(temp_path, mode="r") as archive:
            bad_member = archive.testzip()
            if bad_member is not None:
                raise BuildError(f"ZIP integrity check failed at {bad_member}")

        os.replace(temp_path, output_path)
        temp_path = None
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass

    return output_path, len(files), checked_python


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    default_root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=default_root,
        help="Project root containing ai_cinema_factory/ (default: this script's directory)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=default_root / ARCHIVE_NAME,
        help=f"Output ZIP path (default: {ARCHIVE_NAME} beside this script)",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Validate required files and Python syntax without writing a ZIP",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source_root = args.source_dir.expanduser().resolve()
    try:
        files = _collect_files(source_root)
        checked = _validate_python(files, source_root)
        if args.check_only:
            print(f"Validation passed: {len(files)} files, {checked} Python files syntax-checked.")
            return 0

        archive_path, file_count, python_count = build_archive(source_root, args.output)
        size_kb = archive_path.stat().st_size / 1024
        print(f"Created: {archive_path}")
        print(f"Files: {file_count} (+ BUILD_MANIFEST.json)")
        print(f"Python files syntax-checked: {python_count}")
        print(f"Archive size: {size_kb:.1f} KB")
        return 0
    except (BuildError, OSError, zipfile.BadZipFile) as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
