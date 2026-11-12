# Third-party software notices

AI Cinema Studio is distributed as source code. This repository does not include
vendored copies of its runtime Python dependencies or FFmpeg/FFprobe binaries.
They are installed or obtained separately by the user.

The current runtime dependency declarations are maintained in `requirements.txt`
and `pyproject.toml`. They include:

- Pydantic
- HTTPX
- PySide6 / Qt for the desktop interface
- keyring

The rendering and quality-control features can use FFmpeg and FFprobe, which are
external system tools and are not Python dependencies bundled by this project.

Each third-party package and external tool remains under its own license,
trademark rules, and terms of service. Review the license and distribution terms
for the exact version and build you install. In particular, review the Qt/PySide6
licensing terms before redistributing a packaged desktop binary that includes Qt
libraries, and review the configuration and license of the FFmpeg build you use.

Useful upstream project pages:

- Pydantic: https://github.com/pydantic/pydantic
- HTTPX: https://github.com/encode/httpx
- Qt for Python / PySide6: https://doc.qt.io/qtforpython-6/
- keyring: https://github.com/jaraco/keyring
- FFmpeg: https://ffmpeg.org/legal.html
