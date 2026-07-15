"""Plastic and shark obstacles — user-provided PNG sprites."""

from __future__ import annotations

import math
import random

import pygame

from game import config as cfg
from game.world.assets import get_assets
from game.world.drawing import blit_center
from game.world.sprite_fx import SpriteBackFX

PLASTIC_TYPES = ("bag", "ring", "bottle")


class Obstacle:
    """Base scrolling hazard."""

    def __init__(
        self,
        x: float,
        y: float,
        kind: str,
        scroll_speed: float,
        back_fx: SpriteBackFX | None = None,
    ) -> None:
        self.x = x
        self.y = y
        self.kind = kind
        self.scroll_speed = scroll_speed
        self.time = random.uniform(0, 100)
        self.frame = 0
        self.active = True
        self._back_fx = back_fx
        self._assets = get_assets()
        self.width, self.height = 64, 64
        self.hitbox_shrink = 0.68 if kind == "shark" else 0.72
        sprite = self._sprite()
        if sprite:
            self.width, self.height = sprite.get_size()

    @property
    def rect(self) -> pygame.Rect:
        w = int(self.width * self.hitbox_shrink)
        h = int(self.height * self.hitbox_shrink)
        bob = self._bob_offset()
        return pygame.Rect(int(self.x - w // 2), int(self.y + bob - h // 2), w, h)

    def _bob_offset(self) -> float:
        if self.kind == "shark":
            return math.sin(self.time * 2) * 3
        return math.sin(self.time * 3) * 10

    @property
    def is_shark(self) -> bool:
        return self.kind == "shark"

    @property
    def is_plastic(self) -> bool:
        return self.kind in PLASTIC_TYPES

    def update(self) -> None:
        self.x -= self.scroll_speed
        self.time += 0.06
        self.frame += 1
        if self.x < -160:
            self.active = False

    def _sprite(self) -> pygame.Surface | None:
        if self.kind == "shark":
            frames = self._assets.shark_frames
            if frames:
                return frames[self.frame % len(frames)]
            return None
        return self._assets.plastic.get(self.kind)

    def draw(self, surface: pygame.Surface) -> None:
        sprite = self._sprite()
        if sprite is None:
            return

        bob = self._bob_offset()
        draw_y = self.y + bob

        if self._back_fx:
            self._back_fx.draw_entity_back(surface, self.x, draw_y, self.kind, self.frame)

        if self.is_plastic:
            angle = math.sin(self.time * 2) * 4
            sprite = pygame.transform.rotate(sprite, angle)

        blit_center(surface, sprite, self.x, draw_y)


def make_plastic(
    x: float, y: float, scroll_speed: float, back_fx: SpriteBackFX | None = None
) -> Obstacle:
    return Obstacle(x, y, random.choice(PLASTIC_TYPES), scroll_speed, back_fx)


def make_shark(
    x: float, y: float, scroll_speed: float, back_fx: SpriteBackFX | None = None
) -> Obstacle:
    return Obstacle(x, y, "shark", scroll_speed, back_fx)
