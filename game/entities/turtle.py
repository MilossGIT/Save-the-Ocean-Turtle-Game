"""Animated turtle player — uses user-provided PNG swim frames."""

from __future__ import annotations

import math

import pygame

from game import config as cfg
from game.world.assets import get_assets
from game.world.drawing import blit_center
from game.world.sprite_fx import SpriteBackFX


class Turtle:
    """Player-controlled turtle."""

    FRAMES = cfg.TURTLE_ANIM_FRAMES

    def __init__(self, back_fx: SpriteBackFX | None = None) -> None:
        self.x = float(cfg.TURTLE_X)
        self.y = float(cfg.SCREEN_HEIGHT // 2)
        self.vx = 0.0
        self.vy = 0.0
        self.anim_frame = 0
        self._anim_counter = 0
        self.moving = False
        self.slow_timer = 0
        self.boost_timer = 0
        self.friend_boost_timer = 0
        self.invincible_timer = 0
        self.hit_timer = 0
        self.hit_kind: str | None = None
        self.knockback_x = 0.0
        self.knockback_y = 0.0
        self.power_timer = 0
        self.squash_timer = 0
        self.cosmetic_id = cfg.COSMETIC_NONE
        self.tilt = 0.0
        self._last_dir = None
        self._back_fx = back_fx
        self._assets = get_assets()

    @property
    def max_speed(self) -> float:
        speed = cfg.TURTLE_BASE_SPEED
        if self.slow_timer > 0 and not self.is_powered:
            speed *= cfg.SLOW_MULTIPLIER
        if self.boost_timer > 0:
            speed *= cfg.BUBBLE_SPEED_BOOST
        if self.friend_boost_timer > 0:
            speed *= cfg.FRIEND_MISSION_SPEED_BOOST
        if self.is_powered:
            speed *= cfg.POWERUP_SPEED_BOOST
        return speed

    @property
    def h_speed(self) -> float:
        speed = cfg.TURTLE_H_SPEED
        if self.slow_timer > 0 and not self.is_powered:
            speed *= cfg.SLOW_MULTIPLIER
        if self.boost_timer > 0:
            speed *= cfg.BUBBLE_SPEED_BOOST
        if self.friend_boost_timer > 0:
            speed *= cfg.FRIEND_MISSION_SPEED_BOOST
        if self.is_powered:
            speed *= cfg.POWERUP_SPEED_BOOST
        return speed

    @property
    def is_powered(self) -> bool:
        return self.power_timer > 0

    @property
    def rect(self) -> pygame.Rect:
        shrink = cfg.HITBOX_SHRINK
        w = int(cfg.TURTLE_WIDTH * shrink)
        h = int(cfg.TURTLE_HEIGHT * shrink)
        return pygame.Rect(int(self.x - w // 2), int(self.y - h // 2), w, h)

    @property
    def is_invincible(self) -> bool:
        return self.invincible_timer > 0

    @property
    def is_slowed(self) -> bool:
        return self.slow_timer > 0

    @property
    def is_boosted(self) -> bool:
        return self.boost_timer > 0 or self.friend_boost_timer > 0

    @property
    def is_friend_boosted(self) -> bool:
        return self.friend_boost_timer > 0

    def _apply_knockback(self, from_x: float, from_y: float, strength: float) -> None:
        dx = self.x - from_x
        dy = self.y - from_y
        dist = math.hypot(dx, dy) or 1.0
        self.knockback_x += (dx / dist) * strength
        self.knockback_y += (dy / dist) * strength

    def on_plastic_hit(self, from_x: float, from_y: float) -> None:
        if self.is_powered:
            return
        self.slow_timer = cfg.SLOW_DURATION_FRAMES
        self.hit_timer = cfg.PLASTIC_HIT_FRAMES
        self.hit_kind = "plastic"
        self._apply_knockback(from_x, from_y, 3.5)
        self.tilt = 10 if from_y < self.y else -10

    def on_shark_hit(self, from_x: float, from_y: float) -> None:
        self.invincible_timer = cfg.INVINCIBLE_FRAMES
        self.hit_timer = cfg.SHARK_HIT_FRAMES
        self.hit_kind = "shark"
        self._apply_knockback(from_x, from_y, 9.0)
        self.tilt = 18 if from_y < self.y else -18

    def apply_boost(self) -> None:
        self.boost_timer = cfg.BUBBLE_BOOST_FRAMES

    def apply_friend_boost(self) -> None:
        self.friend_boost_timer = cfg.FRIEND_MISSION_BOOST_FRAMES
        self.squash_timer = cfg.SQUASH_STRETCH_FRAMES

    def apply_power_up(self) -> None:
        self.power_timer = cfg.POWERUP_DURATION_FRAMES
        self.slow_timer = 0

    def trigger_collect_squash(self) -> None:
        self.squash_timer = cfg.SQUASH_STRETCH_FRAMES

    def handle_input(self, keys) -> None:
        if self.hit_kind == "shark" and self.hit_timer > cfg.SHARK_HIT_FRAMES - 12:
            return

        self.vx = 0.0
        self.vy = 0.0
        self.moving = False
        speed = self.max_speed
        h_speed = self.h_speed

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vy = -speed
            self.moving = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vy = speed
            self.moving = True
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -h_speed
            self.moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = h_speed
            self.moving = True

        target_tilt = max(-12, min(12, -self.vy * 1.8))
        if self.hit_timer == 0:
            self.tilt += (target_tilt - self.tilt) * 0.2

        new_dir = (self.vx, self.vy)
        if new_dir != (0, 0) and new_dir != self._last_dir and self._last_dir is not None:
            self._direction_changed = True
        else:
            self._direction_changed = False
        if new_dir != (0, 0):
            self._last_dir = new_dir

    def update(self) -> None:
        self.x += self.vx + self.knockback_x
        self.y += self.vy + self.knockback_y
        self.knockback_x *= 0.82
        self.knockback_y *= 0.82
        self.x = max(cfg.TURTLE_MIN_X, min(cfg.TURTLE_MAX_X, self.x))
        self.y = max(cfg.TURTLE_MIN_Y, min(cfg.TURTLE_MAX_Y, self.y))

        if self.slow_timer > 0:
            self.slow_timer -= 1
        if self.boost_timer > 0:
            self.boost_timer -= 1
        if self.friend_boost_timer > 0:
            self.friend_boost_timer -= 1
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.power_timer > 0:
            self.power_timer -= 1
        if self.squash_timer > 0:
            self.squash_timer -= 1
        if self.hit_timer > 0:
            self.hit_timer -= 1
        else:
            self.hit_kind = None

        if self.hit_timer == 0 and not self.moving:
            self.tilt *= 0.85
        elif self.hit_kind == "plastic" and self.hit_timer > 0:
            self.tilt += math.sin(self.hit_timer * 0.55) * 0.9
        elif self.hit_kind == "shark" and self.hit_timer > 0:
            self.tilt += math.sin(self.hit_timer * 1.1) * 1.6

        anim_stride = cfg.TURTLE_ANIM_STRIDE * (2 if self.is_slowed else 1)
        if not self.moving:
            anim_stride = cfg.TURTLE_ANIM_STRIDE * 3
        self._anim_counter += 1
        if self._anim_counter >= anim_stride:
            self._anim_counter = 0
            self.anim_frame = (self.anim_frame + 1) % self.FRAMES

    def _anim_index(self) -> int:
        return (self.anim_frame // 2) % self.FRAMES

    def pop_direction_changed(self) -> bool:
        changed = getattr(self, "_direction_changed", False)
        self._direction_changed = False
        return changed

    def _current_sprite(self) -> pygame.Surface:
        pool = self._assets.turtle_moving if self.moving else self._assets.turtle_idle
        if not pool:
            pool = self._assets.turtle_moving
        base = pool[self._anim_index() % len(pool)]
        angle = self.tilt
        if self.hit_kind == "plastic" and self.hit_timer > 0:
            angle += math.sin(self.hit_timer * 0.7) * 7
        elif self.hit_kind == "shark" and self.hit_timer > 0:
            angle += math.sin(self.hit_timer * 1.4) * 14
        if abs(angle) > 0.5:
            return pygame.transform.rotate(base, angle)
        return base

    def _draw_stars(self, surface: pygame.Surface, cx: int, cy: int) -> None:
        for i in range(4):
            angle = self.hit_timer * 0.35 + i * (math.pi / 2)
            radius = 34 + math.sin(self.hit_timer * 0.5 + i) * 6
            sx = cx + int(math.cos(angle) * radius)
            sy = cy + int(math.sin(angle) * radius)
            star = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(star, (255, 240, 120, 200), (5, 5), 4)
            surface.blit(star, (sx - 5, sy - 5))

    def _draw_plastic_sparks(self, surface: pygame.Surface, cx: int, cy: int) -> None:
        for i in range(3):
            t = self.hit_timer * 0.25 + i * 2.1
            sx = cx + int(math.cos(t) * 28)
            sy = cy + int(math.sin(t) * 18)
            spark = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(spark, (180, 210, 235, 170), (4, 4), 3)
            surface.blit(spark, (sx - 4, sy - 4))

    def draw(self, surface: pygame.Surface, *, menu_showcase: bool = False) -> None:
        if self._back_fx and not menu_showcase:
            self._back_fx.draw_entity_back(
                surface, self.x, self.y, "turtle", self.anim_frame, self.is_boosted
            )

        sprite = self._current_sprite()

        # Squash & stretch on collect
        if self.squash_timer > 0:
            t = self.squash_timer / cfg.SQUASH_STRETCH_FRAMES
            sx = 1.0 + (1.0 - t) * 0.15
            sy = 1.0 - (1.0 - t) * 0.1
            w, h = sprite.get_size()
            sprite = pygame.transform.smoothscale(sprite, (max(1, int(w * sx)), max(1, int(h * sy))))

        draw_x, draw_y = self.x, self.y

        if self.is_powered:
            glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pulse = 0.5 + math.sin(self.anim_frame * 0.4) * 0.3
            pygame.draw.circle(glow, (100, 255, 180, int(80 * pulse)), (60, 60), 50)
            blit_center(surface, glow, draw_x, draw_y)
        elif self.is_friend_boosted:
            glow = pygame.Surface((130, 130), pygame.SRCALPHA)
            pulse = 0.55 + math.sin(self.anim_frame * 0.55) * 0.35
            pygame.draw.circle(glow, (255, 180, 220, int(75 * pulse)), (65, 65), 54)
            blit_center(surface, glow, draw_x, draw_y)

        if self.hit_kind == "shark" and self.hit_timer > 0:
            shake = math.sin(self.hit_timer * 1.8) * min(8, self.hit_timer * 0.25)
            draw_x += shake
            draw_y += shake * 0.4
            tinted = sprite.copy()
            tinted.fill((255, 160, 160, 255), special_flags=pygame.BLEND_RGBA_MULT)
            sprite = tinted
            sprite.set_alpha(170 + (self.hit_timer % 10) * 8)
            self._draw_stars(surface, int(draw_x), int(draw_y - 18))

        elif self.hit_kind == "plastic" and self.hit_timer > 0:
            drag = math.sin(self.hit_timer * 0.45) * 4
            draw_x -= drag
            tinted = sprite.copy()
            tinted.fill((200, 220, 235, 255), special_flags=pygame.BLEND_RGBA_MULT)
            sprite = tinted
            self._draw_plastic_sparks(surface, int(draw_x), int(draw_y))

        elif self.is_slowed:
            tinted = sprite.copy()
            tinted.fill((210, 220, 230, 255), special_flags=pygame.BLEND_RGBA_MULT)
            sprite = tinted

        elif self.is_powered:
            tinted = sprite.copy()
            tinted.fill((200, 255, 220, 255), special_flags=pygame.BLEND_RGBA_MULT)
            sprite = tinted

        elif self.is_invincible:
            sprite = sprite.copy()
            sprite.set_alpha(175 + (self.invincible_timer % 14) * 5)

        blit_center(surface, sprite, draw_x, draw_y)
        self._draw_cosmetic(surface, int(draw_x), int(draw_y - 20))

    def _draw_cosmetic(self, surface: pygame.Surface, cx: int, cy: int) -> None:
        c = self.cosmetic_id
        if c == "pirate_hat":
            pygame.draw.polygon(surface, (40, 30, 20), [(cx - 18, cy - 8), (cx + 18, cy - 8), (cx + 14, cy - 28), (cx - 14, cy - 28)])
            pygame.draw.circle(surface, (255, 255, 255), (cx + 12, cy - 22), 4)
        elif c == "princess_crown":
            pts = [(cx - 16, cy - 6), (cx - 8, cy - 22), (cx, cy - 10), (cx + 8, cy - 22), (cx + 16, cy - 6)]
            pygame.draw.polygon(surface, cfg.UI_YELLOW, pts)
        elif c == "sunglasses":
            pygame.draw.rect(surface, (30, 30, 40), (cx - 20, cy - 6, 40, 10), border_radius=3)
            pygame.draw.rect(surface, (60, 60, 80), (cx - 18, cy - 4, 14, 6))
            pygame.draw.rect(surface, (60, 60, 80), (cx + 4, cy - 4, 14, 6))
        elif c == "red_shell":
            pygame.draw.ellipse(surface, (200, 50, 50), (cx - 24, cy - 10, 48, 30), 3)
        elif c == "blue_shell":
            pygame.draw.ellipse(surface, (60, 120, 220), (cx - 24, cy - 10, 48, 30), 3)
        elif c == "rainbow_shell":
            colors = [cfg.HEART_RED, cfg.CORAL_ORANGE, cfg.UI_YELLOW, cfg.SEAWEED_GREEN, cfg.FISH_BLUE, cfg.CORAL_PURPLE]
            for i, col in enumerate(colors):
                pygame.draw.arc(surface, col, (cx - 26, cy - 14, 52, 34), 3.14 + i * 0.15, 3.14 + (i + 1) * 0.15, 3)

