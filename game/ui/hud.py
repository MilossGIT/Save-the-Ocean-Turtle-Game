"""Heads-up display: score, lives, missions, power-up timer."""

from __future__ import annotations

import pygame

from game import config as cfg
from game.ui import fonts


class HUD:
    """In-game overlay."""

    def __init__(self) -> None:
        pass

    def _draw_hearts(self, surface: pygame.Surface, lives: int, max_lives: int) -> None:
        for i in range(max_lives):
            x = 20 + i * 36
            y = 18
            color = cfg.HEART_RED if i < lives else (80, 80, 80)
            self._draw_heart(surface, x, y, color)

    def _draw_heart(self, surface: pygame.Surface, x: int, y: int, color) -> None:
        pygame.draw.circle(surface, color, (x + 6, y + 6), 7)
        pygame.draw.circle(surface, color, (x + 18, y + 6), 7)
        pts = [(x, y + 8), (x + 12, y + 24), (x + 24, y + 8)]
        pygame.draw.polygon(surface, color, pts)

    def draw(
        self,
        surface: pygame.Surface,
        score: int,
        lives: int,
        max_lives: int,
        message: str,
        message_alpha: float,
        slowed: bool,
        mission_text: str = "",
        power_seconds: float = 0,
        milestone_text: str = "",
        zone_name: str = "",
        bubble_frenzy_seconds: float = 0,
        friend_boost_seconds: float = 0,
    ) -> None:
        self._draw_hearts(surface, lives, max_lives)

        score_text = f"Distance: {int(score)} m"
        fonts.blit_at(surface, score_text, cfg.SCREEN_WIDTH - 258, 14, 30, cfg.UI_YELLOW)

        if zone_name:
            fonts.blit_at(surface, zone_name, cfg.SCREEN_WIDTH - 258, 46, 22, cfg.BUBBLE_COLOR, bold=False)

        if mission_text:
            fonts.blit_at(surface, mission_text, 16, 52, 22, (200, 230, 255), bold=False)

        if power_seconds > 0:
            fonts.blit_at(
                surface,
                f"Seaweed Power: {power_seconds:.1f}s",
                cfg.SCREEN_WIDTH // 2 - 110,
                14,
                22,
                (120, 255, 180),
                bold=False,
            )

        if bubble_frenzy_seconds > 0:
            fonts.blit_at(
                surface,
                f"Bubble Frenzy: {bubble_frenzy_seconds:.1f}s",
                cfg.SCREEN_WIDTH // 2 - 110,
                40,
                22,
                cfg.UI_YELLOW,
                bold=False,
            )

        if friend_boost_seconds > 0:
            fonts.blit_at(
                surface,
                f"Friend Squad Boost: {friend_boost_seconds:.1f}s",
                cfg.SCREEN_WIDTH // 2 - 130,
                66 if bubble_frenzy_seconds > 0 else 40,
                22,
                cfg.CORAL_PINK,
                bold=False,
            )

        if slowed:
            fonts.blit_at(
                surface,
                "Slowed by plastic!",
                cfg.SCREEN_WIDTH // 2 - 118,
                68,
                22,
                cfg.CORAL_ORANGE,
                bold=False,
            )

        if milestone_text:
            fonts.blit_centered(surface, milestone_text, 110, 30, cfg.UI_YELLOW)

        if message and message_alpha > 0:
            alpha = int(255 * message_alpha)
            fonts.blit_centered(
                surface,
                message,
                cfg.SCREEN_HEIGHT - 50,
                22,
                cfg.WHITE,
                bold=False,
                alpha=alpha,
            )
