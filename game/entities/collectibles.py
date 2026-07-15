"""Collectible bubbles — shiny PNG sprite with gentle float animation."""

from __future__ import annotations

import math
import random

import pygame

from game import config as cfg
from game.world.assets import get_assets
from game.world.drawing import blit_center


class Collectible:
    """Sparkly clean-water bubble."""

    def __init__(self, x: float, y: float, scroll_speed: float):
        self.x = x
        self.y = y
        self.scroll_speed = scroll_speed
        self.time = random.uniform(0, 100)
        self.active = True
        self._base = get_assets().bubble_img
        if self._base:
            self.width, self.height = self._base.get_size()
        else:
            self.width, self.height = 72, 72

    @property
    def rect(self) -> pygame.Rect:
        bob = math.sin(self.time * 2) * 6
        w = int(self.width * cfg.HITBOX_SHRINK)
        h = int(self.height * cfg.HITBOX_SHRINK)
        return pygame.Rect(int(self.x - w // 2), int(self.y + bob - h // 2), w, h)

    def update(self) -> None:
        self.x -= self.scroll_speed
        self.time += 0.06
        if self.x < -80:
            self.active = False

    def draw(self, surface: pygame.Surface) -> None:
        if not self._base:
            return
        bob = math.sin(self.time * 2) * 6
        pulse = 1.0 + math.sin(self.time * 3.5) * 0.06
        w = max(1, int(self.width * pulse))
        h = max(1, int(self.height * pulse))
        sprite = pygame.transform.smoothscale(self._base, (w, h))
        # Soft shimmer — brief brightness pulse
        shimmer = 0.85 + math.sin(self.time * 5) * 0.15
        tinted = sprite.copy()
        tinted.fill(
            (int(200 * shimmer), int(240 * shimmer), 255, 255),
            special_flags=pygame.BLEND_RGBA_MULT,
        )
        blit_center(surface, tinted, self.x, self.y + bob)
