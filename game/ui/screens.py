"""Menu, pause, cosmetics, and enhanced end screens."""

from __future__ import annotations

import math
import random

import pygame

from game import config as cfg
from game.systems.run_stats import RunStats
from game.systems.save_data import SaveData
from game.ui import fonts


class Screens:
    """Full-screen overlays for menu states."""

    def __init__(self) -> None:
        self._anim = 0
        self.end_fact = random.choice(cfg.OCEAN_FACTS)
        self.end_message = random.choice(cfg.ENCOURAGING_MESSAGES)

    def update(self) -> None:
        self._anim += 1

    def pick_end_content(self) -> None:
        self.end_fact = random.choice(cfg.OCEAN_FACTS)
        self.end_message = random.choice(cfg.ENCOURAGING_MESSAGES)

    def _draw_top_overlay(self, surface: pygame.Surface, panel_height: int) -> None:
        """Dim only the title area — leave the swim lane showing the reef."""
        overlay = pygame.Surface((cfg.SCREEN_WIDTH, panel_height), pygame.SRCALPHA)
        overlay.fill((0, 35, 70, 120))
        surface.blit(overlay, (0, 0))

    def _draw_title_panel(self, surface: pygame.Surface, y: int, height: int, width: int = 560) -> None:
        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (0, 50, 90, 210), (0, 0, width, height), border_radius=20)
        pygame.draw.rect(panel, (120, 220, 255, 90), (0, 0, width, height), 3, border_radius=20)
        surface.blit(panel, (cfg.SCREEN_WIDTH // 2 - width // 2, y))

    def _draw_swim_lane(self, surface: pygame.Surface) -> None:
        """Decorative bubbles only — reef background stays visible behind the turtle."""
        lane_y = cfg.MENU_SWIM_LANE_Y
        for i in range(6):
            bx = 80 + i * 150 + math.sin(self._anim * 0.03 + i) * 10
            by = lane_y + 50 + math.cos(self._anim * 0.04 + i * 0.8) * 8
            r = 5 + (i % 2) * 2
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*cfg.BUBBLE_COLOR, 100), (r, r), r)
            surface.blit(s, (int(bx), int(by)))

    def draw_start(self, surface: pygame.Surface, save: SaveData) -> None:
        self._draw_swim_lane(surface)
        self._draw_top_overlay(surface, cfg.MENU_PANEL_BOTTOM)
        self._draw_title_panel(surface, y=36, height=250)

        fonts.blit_centered(surface, "Save the Ocean!", 72, 46, cfg.UI_YELLOW)
        fonts.blit_centered(surface, "Explore, rescue friends, and collect treasures!", 118, 24)
        fonts.blit_centered(surface, "Arrow keys to swim  |  SPACE to start", 168, 22)
        diff = save.difficulty.title()
        fonts.blit_centered(
            surface,
            f"Mode: {diff} (E to switch)  |  C for cosmetics",
            200,
            20,
            cfg.BUBBLE_COLOR,
            bold=False,
        )
        fonts.blit_centered(surface, "M to toggle sound", 228, 20, (190, 220, 240), bold=False)
        fonts.blit_centered(surface, "F or F11 — fullscreen  |  drag corner to resize", 256, 18, (170, 200, 220), bold=False)
        if save.best_score:
            fonts.blit_centered(surface, f"Best: {save.best_score} m", 282, 20, cfg.UI_YELLOW, bold=False)

    def draw_cosmetics(self, surface: pygame.Surface, save: SaveData) -> None:
        self._draw_swim_lane(surface)
        self._draw_top_overlay(surface, 400)
        self._draw_title_panel(surface, y=28, height=340, width=580)

        fonts.blit_centered(surface, "Turtle Outfits", 62, 40, cfg.UI_YELLOW)
        current = "Plain Turtle" if save.selected_cosmetic == cfg.COSMETIC_NONE else cfg.COSMETICS.get(save.selected_cosmetic, ("?",))[0]
        fonts.blit_centered(surface, f"Wearing: {current}", 108, 24, cfg.BUBBLE_COLOR, bold=False)
        fonts.blit_centered(surface, "LEFT / RIGHT to change outfit", 148, 20, bold=False)
        fonts.blit_centered(surface, "ESC to return to menu", 176, 20, bold=False)
        y = 214
        for cosmetic_id, (name, stat_key, threshold) in cfg.COSMETICS.items():
            unlocked = save.is_unlocked(cosmetic_id)
            mark = "[x]" if unlocked else "[ ]"
            color = cfg.WHITE if unlocked else (130, 130, 130)
            fonts.blit_centered(
                surface,
                f"{mark} {name}  ({threshold} {stat_key.replace('_', ' ')})",
                y,
                20,
                color,
                bold=False,
            )
            y += 26

    def draw_pause(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 130))
        surface.blit(overlay, (0, 0))
        fonts.blit_centered(surface, "Paused", cfg.SCREEN_HEIGHT // 2 - 52, 44)
        fonts.blit_centered(surface, "ESC — resume", cfg.SCREEN_HEIGHT // 2 - 4, 24, bold=False)
        fonts.blit_centered(surface, "SPACE — restart run", cfg.SCREEN_HEIGHT // 2 + 28, 24, cfg.UI_YELLOW, bold=False)
        fonts.blit_centered(surface, "Q — return to menu", cfg.SCREEN_HEIGHT // 2 + 58, 22, bold=False)

    def draw_game_over(self, surface: pygame.Surface, score: int, stats: RunStats, save: SaveData, mission_done: bool) -> None:
        overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 30, 60, 195))
        surface.blit(overlay, (0, 0))

        fonts.blit_centered(surface, "Great Job!", 64, 44, cfg.UI_YELLOW)
        fonts.blit_centered(surface, self.end_message, 108, 24, cfg.BUBBLE_COLOR, bold=False)

        fonts.blit_centered(surface, f"Final Score: {int(score)} m", 152, 26)
        fonts.blit_centered(surface, f"Best Score: {save.best_score} m", 182, 24, cfg.UI_YELLOW, bold=False)
        fonts.blit_centered(surface, f"Bubbles Collected: {stats.bubbles_collected}", 220, 22, bold=False)
        fonts.blit_centered(surface, f"Baby Turtles Rescued: {stats.baby_turtles_rescued}", 248, 22, bold=False)
        fonts.blit_centered(
            surface,
            f"Sharks Avoided (best streak): {stats.sharks_avoided_best // cfg.FPS}s",
            276,
            22,
            bold=False,
        )
        from game.systems.zones import ZONES

        zone_name = ZONES[min(stats.zone_index, len(ZONES) - 1)].name
        fonts.blit_centered(surface, f"Ocean Zone Reached: {zone_name}", 304, 22, bold=False)
        if mission_done:
            fonts.blit_centered(surface, "Daily mission complete!", 334, 22, cfg.SEAWEED_GREEN, bold=False)

        fact_panel = pygame.Surface((720, 72), pygame.SRCALPHA)
        pygame.draw.rect(fact_panel, (0, 60, 100, 190), (0, 0, 720, 72), border_radius=12)
        surface.blit(fact_panel, (cfg.SCREEN_WIDTH // 2 - 360, 368))
        fonts.blit_centered(surface, "Did you know?", 392, 20, cfg.UI_YELLOW, bold=False)
        fonts.blit_centered(surface, self.end_fact, 420, 20, (220, 240, 255), bold=False)

        fonts.blit_centered(surface, "SPACE to play again  |  ESC to quit", 488, 22, bold=False)
