"""Bubble, splash, and wake particle effects."""

import math
import random

import pygame

from game import config as cfg
from game.world.drawing import lerp_color


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "radius", "kind", "color")

    def __init__(self, x, y, vx, vy, life, radius, kind="bubble", color=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.radius = radius
        self.kind = kind
        self.color = color or cfg.BUBBLE_COLOR


class ParticleSystem:
    """Ambient bubbles, trails, confetti, and hit effects."""

    def __init__(self):
        self.particles: list[Particle] = []
        self._ambient_timer = 0
        self._ambient_color = cfg.BUBBLE_COLOR

    def set_zone_color(self, color: tuple[int, int, int]) -> None:
        self._ambient_color = color

    def spawn_ambient(self):
        x = random.randint(0, cfg.SCREEN_WIDTH)
        y = cfg.SCREEN_HEIGHT + 10
        self.particles.append(Particle(
            x, y,
            random.uniform(-0.4, 0.4),
            random.uniform(-2.0, -0.6),
            random.randint(80, 200),
            random.randint(4, 10),
            color=self._ambient_color,
        ))

    def spawn_trail(self, x: float, y: float, boosted: bool = False, rainbow: bool = False):
        count = 4 if boosted else 2
        for i in range(count):
            if rainbow:
                hue = (pygame.time.get_ticks() // 30 + i * 40) % 360
                color = pygame.Color(0)
                color.hsva = (hue, 70, 100, 100)
                c = (color.r, color.g, color.b)
            elif boosted:
                c = lerp_color(cfg.BUBBLE_COLOR, (140, 255, 210), random.random())
            else:
                c = cfg.BUBBLE_COLOR
            self.particles.append(Particle(
                x + random.randint(-12, 4),
                y + random.randint(-8, 8),
                random.uniform(-1.2, -0.2),
                random.uniform(-0.8, 0.8),
                random.randint(25, 55),
                random.randint(3, 6),
                color=c,
            ))

    def spawn_sparkle(self, x: float, y: float) -> None:
        for _ in range(5):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2.0)
            self.particles.append(Particle(
                x, y, math.cos(angle) * speed, math.sin(angle) * speed,
                random.randint(15, 30), random.randint(2, 4),
                kind="sparkle", color=(255, 255, 200),
            ))

    def spawn_confetti(self) -> None:
        colors = [cfg.CORAL_PINK, cfg.UI_YELLOW, cfg.BUBBLE_COLOR, cfg.SEAWEED_GREEN, cfg.CORAL_PURPLE]
        for _ in range(24):
            self.particles.append(Particle(
                random.randint(0, cfg.SCREEN_WIDTH), -10,
                random.uniform(-1, 1), random.uniform(1, 3),
                random.randint(60, 120), random.randint(3, 6),
                kind="confetti", color=random.choice(colors),
            ))

    def spawn_friend_wave(self, x: float, y: float) -> None:
        """Small burst when greeting one sea friend."""
        for _ in range(8):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.8, 2.2)
            self.particles.append(Particle(
                x, y, math.cos(angle) * speed, math.sin(angle) * speed,
                random.randint(20, 35), random.randint(3, 5),
                kind="heart", color=cfg.CORAL_PINK,
            ))

    def spawn_friend_party(self, x: float, y: float) -> None:
        """Big celebration when the full friend squad is united."""
        colors = [cfg.CORAL_PINK, cfg.FISH_BLUE, cfg.UI_YELLOW, cfg.SEAWEED_GREEN, cfg.CORAL_ORANGE]
        for i in range(8):
            angle = (math.pi * 2 * i) / 8
            for ring in range(4):
                speed = 2.0 + ring * 1.4
                self.particles.append(Particle(
                    x, y,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed - 0.8,
                    random.randint(55, 100),
                    random.randint(5, 10),
                    kind="heart",
                    color=random.choice(colors),
                ))
        for _ in range(36):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.5, 5.0)
            self.particles.append(Particle(
                x, y, math.cos(angle) * speed, math.sin(angle) * speed,
                random.randint(45, 85), random.randint(4, 8),
                kind="sparkle", color=(255, 255, 220),
            ))
        for _ in range(20):
            self.particles.append(Particle(
                random.randint(0, cfg.SCREEN_WIDTH), random.randint(0, cfg.SCREEN_HEIGHT // 2),
                random.uniform(-1.5, 1.5), random.uniform(-2.5, -0.5),
                random.randint(50, 90), random.randint(5, 11),
                kind="bubble", color=cfg.BUBBLE_COLOR,
            ))
        for _ in range(3):
            self.particles.append(Particle(x, y, 0, 0, 70 + _ * 15, 10 + _ * 8, kind="ripple"))
        self.spawn_confetti()

    def spawn_bubble_pop(self, x: float, y: float) -> None:
        for _ in range(10):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.6, 2.5)
            self.particles.append(Particle(
                x, y, math.cos(angle) * speed, math.sin(angle) * speed,
                random.randint(18, 32), random.randint(3, 6),
                kind="bubble", color=cfg.BUBBLE_COLOR,
            ))
        self.particles.append(Particle(x, y, 0, 0, 28, 12, kind="ripple"))

    def spawn_hit(self, x: float, y: float, kind: str = "plastic") -> None:
        if kind == "shark":
            for _ in range(14):
                angle = random.uniform(-math.pi * 0.35, math.pi * 0.35) + math.pi
                speed = random.uniform(2.0, 5.5)
                self.particles.append(Particle(
                    x, y,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    random.randint(16, 32),
                    random.randint(3, 6),
                    kind="splash",
                    color=(255, 130, 110),
                ))
            self.particles.append(Particle(x, y, 0, 0, 35, 18, kind="ripple"))
            return

        for _ in range(10):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 1.8)
            self.particles.append(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                random.randint(20, 40),
                random.randint(2, 5),
                kind="splash",
                color=(170, 200, 225),
            ))

    def spawn_splash(self, x: float, y: float):
        for _ in range(12):
            angle = random.uniform(-math.pi * 0.85, -math.pi * 0.15)
            speed = random.uniform(1.5, 4.0)
            self.particles.append(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                random.randint(18, 40),
                random.randint(2, 5),
                kind="splash",
            ))
        self.particles.append(Particle(x, y, 0, 0, 25, 14, kind="ripple"))

    def update(self):
        self._ambient_timer += 1
        if self._ambient_timer >= 15:
            self._ambient_timer = 0
            self.spawn_ambient()

        alive = []
        for p in self.particles:
            p.x += p.vx
            p.y += p.vy
            p.life -= 1
            if p.kind == "bubble":
                p.vx += math.sin(p.y * 0.04 + p.x * 0.02) * 0.03
                p.vy -= 0.01
            elif p.kind == "splash":
                p.vy += 0.08
            elif p.kind == "ripple":
                p.radius += 0.6
            elif p.kind == "confetti":
                p.vy += 0.04
                p.vx += math.sin(p.y * 0.05) * 0.05
            elif p.kind == "sparkle":
                p.radius *= 0.96
            elif p.kind == "heart":
                p.vy -= 0.02
                p.vx *= 0.98

            if p.life > 0 and -30 < p.x < cfg.SCREEN_WIDTH + 30 and -30 < p.y < cfg.SCREEN_HEIGHT + 30:
                alive.append(p)
        self.particles = alive

    def draw(self, surface: pygame.Surface):
        for p in self.particles:
            alpha = int(200 * (p.life / p.max_life))
            if p.kind == "ripple":
                s = pygame.Surface((p.radius * 4, p.radius * 4), pygame.SRCALPHA)
                pygame.draw.circle(s, (200, 240, 255, alpha // 2),
                                   (p.radius * 2, p.radius * 2), int(p.radius), 2)
                surface.blit(s, (int(p.x - p.radius * 2), int(p.y - p.radius * 2)))
                continue

            if p.kind == "splash":
                color = (*(p.color[:3] if p.color else (210, 240, 255)), alpha)
            elif p.kind == "sparkle":
                color = (255, 255, 220, alpha)
            elif p.kind == "heart":
                color = (*p.color[:3], alpha)
            elif p.kind == "confetti":
                color = (*p.color[:3], alpha)
            else:
                color = (*p.color[:3], alpha)

            size = max(2, p.radius * 2)
            s = pygame.Surface((size, size), pygame.SRCALPHA)
            if p.kind == "heart":
                cx, cy = p.radius, p.radius
                pygame.draw.circle(s, color, (cx, cy - 1), max(2, p.radius - 1))
                pygame.draw.circle(s, color, (cx - p.radius // 2, cy), max(2, p.radius - 1))
                pygame.draw.circle(s, color, (cx + p.radius // 2, cy), max(2, p.radius - 1))
                pygame.draw.polygon(
                    s, color,
                    [(cx, cy + p.radius), (cx - p.radius, cy - 1), (cx + p.radius, cy - 1)],
                )
            else:
                pygame.draw.circle(s, color, (p.radius, p.radius), p.radius)
            if p.kind == "bubble":
                pygame.draw.circle(s, (255, 255, 255, alpha // 2),
                                   (max(1, p.radius // 3), max(1, p.radius // 3)),
                                   max(1, p.radius // 3))
                pygame.draw.circle(s, (*cfg.BUBBLE_COLOR, alpha // 3),
                                   (p.radius, p.radius), p.radius, 1)
            surface.blit(s, (int(p.x - p.radius), int(p.y - p.radius)))
