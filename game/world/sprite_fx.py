"""Animated ripple/glow effects drawn BEHIND entity sprites."""

from __future__ import annotations

import math

import pygame

from game import config as cfg
from game.world.assets import get_assets
from game.world.drawing import blit_center


class SpriteBackFX:
    """Shadow, ripple sheet, and glow halos under moving sprites."""

    def __init__(self) -> None:
        self._time = 0.0

    def update(self) -> None:
        self._time += 1.0 / cfg.FPS

    def draw_shadow(self, surface: pygame.Surface, x: float, y: float, width: int, height: int) -> None:
        shadow = pygame.Surface((width, height // 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 40, 80, 45), shadow.get_rect())
        surface.blit(shadow, (int(x - width // 2), int(y + height // 5)))

    def draw_ripple(self, surface: pygame.Surface, x: float, y: float, frame: int) -> None:
        frames = get_assets().ripple_frames
        if frames:
            ripple = frames[frame % len(frames)]
            tinted = ripple.copy()
            tinted.set_alpha(140)
            blit_center(surface, tinted, x, y + 16)
            return
        # Fallback animated rings when no sheet
        for i in range(2):
            r = 12 + i * 10 + (frame % 20) * 0.8
            alpha = max(0, 100 - i * 40 - int((frame % 20) * 3))
            ring = pygame.Surface((int(r * 2 + 4), int(r * 2 + 4)), pygame.SRCALPHA)
            pygame.draw.ellipse(ring, (180, 230, 255, alpha), ring.get_rect(), 2)
            blit_center(surface, ring, x, y + 18)

    def draw_glow(self, surface: pygame.Surface, x: float, y: float, radius: int, color: tuple, alpha: int) -> None:
        glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pulse = 1.0 + math.sin(self._time * 4) * 0.1
        r = int(radius * pulse)
        pygame.draw.circle(glow, (*color[:3], alpha), (radius, radius), r)
        blit_center(surface, glow, x, y)

    def draw_entity_back(
        self,
        surface: pygame.Surface,
        x: float,
        y: float,
        kind: str,
        frame: int,
        boosted: bool = False,
    ) -> None:
        sizes = {
            "turtle": (100, 50),
            "bag": (64, 36),
            "ring": (58, 32),
            "bottle": (48, 36),
            "shark": (110, 44),
        }
        w, h = sizes.get(kind, (56, 32))
        self.draw_shadow(surface, x, y, w, h)
        if kind == "turtle":
            self.draw_ripple(surface, x, y, frame)
        if boosted and kind == "turtle":
            self.draw_glow(surface, x, y, 56, (100, 255, 220), 70)
