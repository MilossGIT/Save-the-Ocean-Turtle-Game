"""Crisp UI font rendering with pygame.freetype."""

from __future__ import annotations

import pygame
import pygame.freetype as ft

from game import config as cfg

_FONT_NAMES = (
    "Arial Rounded MT Bold",
    "Chalkboard SE",
    "Verdana",
    "Helvetica Neue",
    "Arial",
    "sans-serif",
)

_cache: dict[tuple[int, bool], ft.Font] = {}
_initialized = False


def _ensure_init() -> None:
    global _initialized
    if not _initialized:
        if not ft.get_init():
            ft.init()
        _initialized = True


def get_font(size: int, bold: bool = True) -> ft.Font:
    _ensure_init()
    key = (size, bold)
    if key not in _cache:
        font = ft.SysFont(_FONT_NAMES, size)
        font.strong = bold
        font.antialiased = True
        font.pad = True
        _cache[key] = font
    return _cache[key]


def render(
    text: str,
    size: int,
    color: tuple[int, int, int] = cfg.WHITE,
    *,
    bold: bool = True,
    shadow: bool = True,
    shadow_color: tuple[int, int, int] = cfg.UI_SHADOW,
    shadow_offset: tuple[int, int] = (2, 2),
) -> pygame.Surface:
    font = get_font(size, bold)
    if shadow:
        shadow_surf, _ = font.render(text, shadow_color)
        main_surf, _ = font.render(text, color)
        w = max(shadow_surf.get_width(), main_surf.get_width()) + abs(shadow_offset[0])
        h = max(shadow_surf.get_height(), main_surf.get_height()) + abs(shadow_offset[1])
        out = pygame.Surface((w, h), pygame.SRCALPHA)
        out.blit(shadow_surf, (max(0, shadow_offset[0]), max(0, shadow_offset[1])))
        out.blit(main_surf, (0, 0))
        return out
    surf, _ = font.render(text, color)
    return surf.convert_alpha()


def blit_centered(
    surface: pygame.Surface,
    text: str,
    y: int | float,
    size: int,
    color: tuple[int, int, int] = cfg.WHITE,
    *,
    bold: bool = True,
    shadow: bool = True,
    alpha: int = 255,
) -> None:
    font = get_font(size, bold)
    y = int(y)
    cx = cfg.SCREEN_WIDTH // 2
    if shadow:
        sh, sh_rect = font.render(text, cfg.UI_SHADOW)
        sh_rect.center = (cx + 2, y + 2)
        if alpha < 255:
            sh.set_alpha(alpha)
        surface.blit(sh, sh_rect)
    surf, rect = font.render(text, color)
    rect.center = (cx, y)
    if alpha < 255:
        surf.set_alpha(alpha)
    surface.blit(surf, rect)


def blit_at(
    surface: pygame.Surface,
    text: str,
    x: int | float,
    y: int | float,
    size: int,
    color: tuple[int, int, int] = cfg.WHITE,
    *,
    bold: bool = False,
    shadow: bool = True,
    alpha: int = 255,
) -> None:
    font = get_font(size, bold)
    x, y = int(x), int(y)
    if shadow:
        sh, _ = font.render(text, cfg.UI_SHADOW)
        if alpha < 255:
            sh.set_alpha(alpha)
        surface.blit(sh, (x + 2, y + 2))
    surf, _ = font.render(text, color)
    if alpha < 255:
        surf.set_alpha(alpha)
    surface.blit(surf, (x, y))


def blit_centered_rect(
    surface: pygame.Surface,
    text: str,
    center: tuple[int, int],
    size: int,
    color: tuple[int, int, int] = cfg.WHITE,
    *,
    bold: bool = True,
    shadow: bool = True,
    alpha: int = 255,
) -> None:
    font = get_font(size, bold)
    cx, cy = center
    if shadow:
        sh, sh_rect = font.render(text, cfg.UI_SHADOW)
        sh_rect.center = (cx + 2, cy + 2)
        if alpha < 255:
            sh.set_alpha(alpha)
        surface.blit(sh, sh_rect)
    surf, rect = font.render(text, color)
    rect.center = (cx, cy)
    if alpha < 255:
        surf.set_alpha(alpha)
    surface.blit(surf, rect)
