"""Positive world entities — PNG sprites with procedural fallback."""

from __future__ import annotations

import math
import random

import pygame

from game import config as cfg
from game.world.assets import get_assets
from game.world.drawing import blit_center, draw_shaded_circle


def _proximity_rect(x: float, y: float, w: int, h: int) -> pygame.Rect:
    return pygame.Rect(int(x - w // 2), int(y - h // 2), w, h)


def _size_from_sprite(sprite: pygame.Surface | None, default: tuple[int, int]) -> tuple[int, int]:
    if sprite:
        return sprite.get_size()
    return default


class BabyTurtle:
    """Rare rescue target — swims away happily when touched."""

    def __init__(self, x: float, y: float, scroll_speed: float) -> None:
        self.x = x
        self.y = y
        self.scroll_speed = scroll_speed
        self.active = True
        self.rescued = False
        self.escape_timer = 0
        self.time = random.uniform(0, 50)
        self._assets = get_assets()
        self._sprite = self._assets.baby_turtle
        self.width, self.height = _size_from_sprite(self._sprite, (48, 36))

    @property
    def rect(self) -> pygame.Rect:
        return _proximity_rect(self.x, self.y, int(self.width * 0.8), int(self.height * 0.8))

    def rescue(self) -> None:
        self.rescued = True
        self.escape_timer = 45

    def update(self) -> None:
        self.time += 0.08
        if self.rescued:
            self.x += 2.5
            self.y += math.sin(self.time * 3) * 0.8
            self.escape_timer -= 1
            if self.escape_timer <= 0 or self.x > cfg.SCREEN_WIDTH + 80:
                self.active = False
            return
        self.x -= self.scroll_speed * 0.85
        self.y += math.sin(self.time * 2) * 0.6
        if self.x < -80:
            self.active = False

    def draw(self, surface: pygame.Surface) -> None:
        bob = math.sin(self.time * 2.5) * 3
        draw_y = self.y + bob
        scale = 0.55 if self.rescued else 1.0
        if self._sprite:
            sprite = self._sprite
            if scale != 1.0:
                w = max(1, int(sprite.get_width() * scale))
                h = max(1, int(sprite.get_height() * scale))
                sprite = pygame.transform.smoothscale(sprite, (w, h))
            blit_center(surface, sprite, self.x, draw_y)
            return
        cx, cy = int(self.x), int(draw_y)
        w, h = int(44 * scale), int(32 * scale)
        shell = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
        pygame.draw.ellipse(surface, cfg.TURTLE_SHELL, shell)
        draw_shaded_circle(surface, (cx + w // 3, cy - 4), max(4, int(6 * scale)), cfg.TURTLE_SKIN)


class FriendlyAnimal:
    """Harmless sea friend — proximity wave grants a small bonus."""

    KINDS = ("dolphin", "clownfish", "turtle", "ray")

    def __init__(self, x: float, y: float, scroll_speed: float, kind: str | None = None) -> None:
        self.x = x
        self.y = y
        self.scroll_speed = scroll_speed
        self.kind = kind or random.choice(self.KINDS)
        self.active = True
        self.time = random.uniform(0, 50)
        self.waved = False
        self.wave_timer = 0
        self.leaving = False
        self._assets = get_assets()
        self._sprite = self._assets.friends.get(self.kind)
        self.width, self.height = _size_from_sprite(self._sprite, (70, 40))

    @property
    def rect(self) -> pygame.Rect:
        return _proximity_rect(self.x, self.y, self.width, self.height)

    def proximity_rect(self) -> pygame.Rect:
        r = cfg.FRIENDLY_PROXIMITY_RADIUS
        return pygame.Rect(int(self.x - r), int(self.y - r), r * 2, r * 2)

    def trigger_wave(self) -> None:
        self.waved = True
        self.wave_timer = 45
        self.leaving = True

    def update(self) -> None:
        self.time += 0.06
        if self.leaving:
            self.wave_timer -= 1
            self.x += 2.2
            self.y += math.sin(self.time * 4) * 0.6
            if self.wave_timer <= 0 or self.x > cfg.SCREEN_WIDTH + 100:
                self.active = False
            return
        self.x -= self.scroll_speed * 0.7
        self.y += math.sin(self.time * 2) * 0.5
        if self.x < -100:
            self.active = False

    def draw(self, surface: pygame.Surface) -> None:
        bob = math.sin(self.time * 2) * 4
        wave_off = math.sin(self.time * 5) * 6 if self.leaving else 0
        draw_y = self.y + bob + wave_off
        if self._sprite:
            angle = math.sin(self.time * 5) * 5 if self.leaving else 0
            sprite = self._sprite
            if self.leaving:
                sprite = sprite.copy()
                alpha = max(80, int(255 * (self.wave_timer / 45)))
                sprite.set_alpha(alpha)
            if abs(angle) > 0.5:
                sprite = pygame.transform.rotate(sprite, angle)
            blit_center(surface, sprite, self.x, draw_y)
            return
        cx, cy = int(self.x), int(draw_y)
        pygame.draw.ellipse(surface, cfg.FISH_BLUE, (cx - 30, cy - 12, 60, 24))


class TreasureChest:
    """Rare chest with a random reward."""

    def __init__(self, x: float, y: float, scroll_speed: float) -> None:
        self.x = x
        self.y = y
        self.scroll_speed = scroll_speed
        self.active = True
        self.opened = False
        self.open_anim = 0
        self.time = 0.0
        self._assets = get_assets()
        self._sprite = self._assets.treasure_chest
        self.width, self.height = _size_from_sprite(self._sprite, (52, 44))

    @property
    def rect(self) -> pygame.Rect:
        return _proximity_rect(self.x, self.y, self.width, self.height)

    def open(self) -> None:
        self.opened = True
        self.open_anim = 30

    def update(self) -> None:
        self.time += 0.05
        if self.opened:
            self.open_anim -= 1
            if self.open_anim <= 0:
                self.active = False
            return
        self.x -= self.scroll_speed * 0.75
        self.y += math.sin(self.time * 2) * 0.4
        if self.x < -70:
            self.active = False

    def draw(self, surface: pygame.Surface) -> None:
        bob = math.sin(self.time * 2) * 2
        if self._sprite:
            sprite = self._sprite
            if self.opened and self.open_anim > 0:
                angle = min(40, (30 - self.open_anim) * 2)
                sprite = pygame.transform.rotate(sprite, angle)
            alpha = max(80, int(255 * (self.open_anim / 30))) if self.opened else 255
            if alpha < 255:
                sprite = sprite.copy()
                sprite.set_alpha(alpha)
            blit_center(surface, sprite, self.x, self.y + bob)
            return
        cx, cy = int(self.x), int(self.y + bob)
        pygame.draw.rect(surface, cfg.SAND_DARK, (cx - 22, cy - 8, 44, 26), border_radius=4)


class SeaweedPowerUp:
    """Glowing seaweed — grants temporary super power."""

    def __init__(self, x: float, y: float, scroll_speed: float) -> None:
        self.x = x
        self.y = y
        self.scroll_speed = scroll_speed
        self.active = True
        self.time = random.uniform(0, 50)
        self._assets = get_assets()
        self._sprite = self._assets.seaweed_powerup
        self.width, self.height = _size_from_sprite(self._sprite, (40, 50))

    @property
    def rect(self) -> pygame.Rect:
        return _proximity_rect(self.x, self.y, self.width, self.height)

    def update(self) -> None:
        self.time += 0.07
        self.x -= self.scroll_speed * 0.8
        self.y += math.sin(self.time * 2.5) * 0.5
        if self.x < -60:
            self.active = False

    def draw(self, surface: pygame.Surface) -> None:
        bob = math.sin(self.time * 2.5) * 3
        if self._sprite:
            pulse = 0.85 + math.sin(self.time * 4) * 0.15
            w = max(1, int(self._sprite.get_width() * pulse))
            h = max(1, int(self._sprite.get_height() * pulse))
            sprite = pygame.transform.smoothscale(self._sprite, (w, h))
            blit_center(surface, sprite, self.x, self.y + bob)
            return
        cx, cy = int(self.x), int(self.y + bob)
        pygame.draw.polygon(surface, cfg.SEAWEED_GREEN, [(cx, cy + 16), (cx - 8, cy - 12), (cx + 8, cy - 12)])
