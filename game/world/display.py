"""Window, fullscreen, and scaling."""

from __future__ import annotations

import pygame

from game import config as cfg


class Display:
    """960×540 logical buffer — SDL scales to window or fullscreen (no letterbox bars)."""

    def __init__(self) -> None:
        self.logical_w = cfg.SCREEN_WIDTH
        self.logical_h = cfg.SCREEN_HEIGHT
        self.fullscreen = False
        self.window_size = (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)
        self.screen = self._create_screen()
        self.virtual = self.screen

    def _create_screen(self) -> pygame.Surface:
        flags = pygame.SCALED | (pygame.FULLSCREEN if self.fullscreen else pygame.RESIZABLE)
        return pygame.display.set_mode((self.logical_w, self.logical_h), flags)

    def toggle_fullscreen(self) -> None:
        self.fullscreen = not self.fullscreen
        self.screen = self._create_screen()
        self.virtual = self.screen

    def handle_resize(self, width: int, height: int) -> None:
        if self.fullscreen:
            return
        # With pygame.SCALED the drawable surface stays 960×540; SDL scales to the window.
        self.window_size = (max(640, width), max(360, height))

    def present(self) -> None:
        """No-op — we draw directly to the display surface (pygame.SCALED handles upscaling)."""
        return
