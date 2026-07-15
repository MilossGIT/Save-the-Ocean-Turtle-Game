"""Resolve project paths for development and bundled desktop builds."""

from __future__ import annotations

import sys
from pathlib import Path

APP_NAME = "Save the Ocean"
SAVE_FILENAME = "savegame.json"


def is_frozen() -> bool:
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def app_root() -> Path:
    """Root folder — project directory in dev, PyInstaller bundle when packaged."""
    if is_frozen():
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[1]


def assets_dir() -> Path:
    return app_root() / "assets"


def save_path() -> Path:
    """Save file — next to project in dev, Application Support when bundled."""
    if is_frozen():
        folder = Path.home() / "Library" / "Application Support" / APP_NAME
        folder.mkdir(parents=True, exist_ok=True)
        return folder / SAVE_FILENAME
    return app_root() / SAVE_FILENAME
