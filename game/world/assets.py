"""Load PNG assets from assets/ — installed by scripts/install_user_assets.py."""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

import pygame

from game import config as cfg
from game.paths import app_root, assets_dir, is_frozen

log = logging.getLogger(__name__)

ROOT = app_root()
ASSETS_DIR = assets_dir()
INSTALL_SCRIPT = ROOT / "scripts" / "install_user_assets.py"

REQUIRED = [
    "turtle/turtle_swim_0.png",
    "turtle/turtle_idle.png",
    "turtle/baby_turtle.png",
    "obstacles/plastic_bag.png",
    "obstacles/shark_0.png",
    "backgrounds/ocean_base.png",
    "collectibles/bubble.png",
    "collectibles/treasure_chest.png",
    "collectibles/seaweed_powerup.png",
    "friends/dolphin.png",
]

REEF_BACKGROUNDS = [
    "backgrounds/ocean_base.png",
    "backgrounds/ocean_coral_2.png",
    "backgrounds/ocean_coral_3.png",
]

ZONE_BACKGROUNDS = [
    "backgrounds/ocean_base.png",
    "backgrounds/zone_kelp.png",
    "backgrounds/zone_deep.png",
    "backgrounds/zone_lagoon.png",
    "backgrounds/zone_night.png",
]


def ensure_assets() -> None:
    missing = [rel for rel in REQUIRED if not (ASSETS_DIR / rel).exists()]
    if not missing:
        return
    if is_frozen():
        log.error("Missing bundled assets: %s", missing)
        return
    if not INSTALL_SCRIPT.exists():
        log.error("Missing assets and install script not found: %s", missing)
        return
    log.info("Missing assets %s — running install_user_assets.py", missing)
    subprocess.check_call([sys.executable, str(INSTALL_SCRIPT)], cwd=str(ROOT))


class AssetManager:
    """Loads PNGs from assets/."""

    def __init__(self) -> None:
        self._cache: dict[str, pygame.Surface] = {}
        self.turtle_moving: list[pygame.Surface] = []
        self.turtle_idle: list[pygame.Surface] = []
        self.baby_turtle: pygame.Surface | None = None
        self.plastic: dict[str, pygame.Surface | None] = {}
        self.shark_frames: list[pygame.Surface] = []
        self.friends: dict[str, pygame.Surface | None] = {}
        self.treasure_chest: pygame.Surface | None = None
        self.seaweed_powerup: pygame.Surface | None = None
        self.ocean_base: pygame.Surface | None = None
        self.reef_backgrounds: list[pygame.Surface | None] = []
        self.zone_backgrounds: list[pygame.Surface | None] = []
        self.bubble_img: pygame.Surface | None = None
        self.ripple_frames: list[pygame.Surface] = []
        self.has_images = False
        self._load_all()

    def _load_all(self) -> None:
        self.turtle_moving = self._load_turtle_swim()
        self.turtle_idle = self._load_turtle_idle()
        self.baby_turtle = self._load("turtle/baby_turtle.png")
        self.plastic = {
            "bag": self._load("obstacles/plastic_bag.png"),
            "ring": self._load("obstacles/plastic_ring.png"),
            "bottle": self._load("obstacles/plastic_bottle.png"),
        }
        self.shark_frames = self._load_shark_frames()
        self.friends = {
            "dolphin": self._load("friends/dolphin.png"),
            "clownfish": self._load("friends/clownfish.png"),
            "turtle": self._load("friends/turtle.png"),
            "ray": self._load("friends/ray.png"),
        }
        self.treasure_chest = self._load("collectibles/treasure_chest.png")
        self.seaweed_powerup = self._load("collectibles/seaweed_powerup.png")
        self.ocean_base = self._load_bg("backgrounds/ocean_base.png")
        self.reef_backgrounds = [self._load_bg(rel) for rel in REEF_BACKGROUNDS]
        if not any(self.reef_backgrounds):
            self.reef_backgrounds = [self.ocean_base]
        self.zone_backgrounds = [self._load_bg(rel) for rel in ZONE_BACKGROUNDS]
        self.bubble_img = self._load("collectibles/bubble.png")
        self.ripple_frames = self._load_ripples()
        self.has_images = bool(self.turtle_moving and self.ocean_base)

    def reef_background(self, index: int) -> pygame.Surface | None:
        if self.reef_backgrounds:
            idx = index % len(self.reef_backgrounds)
            bg = self.reef_backgrounds[idx]
            if bg is not None:
                return bg
        return self.ocean_base

    def zone_background(self, index: int) -> pygame.Surface | None:
        if 0 <= index < len(self.zone_backgrounds):
            bg = self.zone_backgrounds[index]
            if bg is not None:
                return bg
        return self.ocean_base

    def _path(self, rel: str) -> Path:
        return ASSETS_DIR / rel

    def _load(self, rel: str, *, alpha: bool = True) -> pygame.Surface | None:
        path = self._path(rel)
        if not path.exists():
            log.warning("Missing: %s", rel)
            return None
        cache_key = f"{rel}:{'a' if alpha else 'o'}"
        if cache_key not in self._cache:
            surf = pygame.image.load(str(path))
            if pygame.display.get_surface() is not None:
                try:
                    surf = surf.convert_alpha() if alpha else surf.convert()
                except pygame.error:
                    surf = surf.convert()
            self._cache[cache_key] = surf
        return self._cache[cache_key]

    def _load_bg(self, rel: str) -> pygame.Surface | None:
        """Opaque backgrounds — avoids alpha glitches on the main draw surface."""
        return self._load(rel, alpha=False)

    def _load_turtle_swim(self) -> list[pygame.Surface]:
        frames: list[pygame.Surface] = []
        for i in range(cfg.TURTLE_ANIM_FRAMES):
            surf = self._load(f"turtle/turtle_swim_{i}.png")
            if surf:
                frames.append(surf)
        return frames

    def _load_turtle_idle(self) -> list[pygame.Surface]:
        idle = self._load("turtle/turtle_idle.png")
        if idle:
            return [idle] * cfg.TURTLE_ANIM_FRAMES
        if self.turtle_moving:
            return [self.turtle_moving[0]] * cfg.TURTLE_ANIM_FRAMES
        return []

    def _load_shark_frames(self) -> list[pygame.Surface]:
        return [s for i in range(4) if (s := self._load(f"obstacles/shark_{i}.png"))]

    def _load_ripples(self) -> list[pygame.Surface]:
        sheet = self._load("effects/ripples_sheet.png")
        if not sheet:
            return []
        fw = sheet.get_width() // 4
        fh = sheet.get_height()
        return [sheet.subsurface(pygame.Rect(i * fw, 0, fw, fh)).copy() for i in range(4)]


_manager: AssetManager | None = None


def get_assets() -> AssetManager:
    global _manager
    if _manager is None:
        _manager = AssetManager()
    return _manager


def reload_assets() -> AssetManager:
    global _manager
    _manager = AssetManager()
    return _manager
