"""Launch the AI Cinema Studio desktop application."""

from __future__ import annotations

import sys


def main() -> int:
    try:
        from ai_cinema_studio.window import launch
    except ImportError as exc:
        message = (
            "AI Cinema Studio desktop dependencies are missing.\n"
            "Install them with: python -m pip install -r requirements.txt\n\n"
            f"Details: {exc}"
        )
        print(message, file=sys.stderr)
        return 2
    return launch()


if __name__ == "__main__":
    raise SystemExit(main())
