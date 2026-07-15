"""Shared drawing helpers for sprites and particles."""

import pygame


def lerp_color(a: tuple, b: tuple, t: float) -> tuple:
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shade(color: tuple, amount: int) -> tuple:
    return tuple(max(0, min(255, c + amount)) for c in color)


def draw_shaded_circle(
    surface: pygame.Surface,
    center: tuple,
    radius: int,
    color: tuple,
    light_offset=(-2, -2),
) -> None:
    cx, cy = center
    pygame.draw.circle(surface, shade(color, -35), (cx, cy), radius)
    pygame.draw.circle(surface, color, (cx, cy), max(1, radius - 2))
    hl_x = cx + light_offset[0]
    hl_y = cy + light_offset[1]
    pygame.draw.circle(surface, (*shade(color, 55), 180), (hl_x, hl_y), max(2, radius // 3))


def blit_center(surface: pygame.Surface, sprite: pygame.Surface, x: float, y: float) -> None:
    rect = sprite.get_rect(center=(int(x), int(y)))
    surface.blit(sprite, rect)
