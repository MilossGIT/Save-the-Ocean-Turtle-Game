"""Floating text and score popups for game juice."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from game import config as cfg
from game.ui import fonts


@dataclass
class FloatingText:
    """Rises and fades — used for score pops and rescue messages."""

    text: str
    x: float
    y: float
    color: tuple[int, int, int]
    life: int = cfg.FLOAT_TEXT_DURATION
    max_life: int = cfg.FLOAT_TEXT_DURATION
    vy: float = -1.2
    size: int = 22

    def update(self) -> bool:
        self.y += self.vy
        self.life -= 1
        return self.life > 0

    def draw(self, surface: pygame.Surface) -> None:
        alpha = int(255 * (self.life / self.max_life))
        fonts.blit_at(
            surface,
            self.text,
            self.x,
            self.y,
            self.size,
            self.color,
            bold=True,
            alpha=alpha,
        )


class FeedbackSystem:
    """Manages floating numbers, popups, and reward banners."""

    def __init__(self) -> None:
        self.floats: list[FloatingText] = []
        self.popup_text = ""
        self.popup_timer = 0
        self.reward_text = ""

    def add_float(self, text: str, x: float, y: float,
                  color: tuple[int, int, int] = cfg.UI_YELLOW, size: int = 22) -> None:
        self.floats.append(FloatingText(text, x, y, color, size=size))

    def add_score(self, amount: int, x: float, y: float) -> None:
        sign = "+" if amount >= 0 else ""
        self.add_float(f"{sign}{amount}", x, y - 20, cfg.UI_YELLOW, 26)

    def show_popup(self, text: str, duration: int = cfg.MESSAGE_DURATION_FRAMES) -> None:
        self.popup_text = text
        self.popup_timer = duration

    def show_reward(self, text: str) -> None:
        self.reward_text = text
        self.popup_timer = cfg.MESSAGE_DURATION_FRAMES

    def update(self) -> None:
        if self.popup_timer > 0:
            self.popup_timer -= 1
        else:
            self.popup_text = ""
            self.reward_text = ""
        self.floats = [f for f in self.floats if f.update()]

    def draw(self, surface: pygame.Surface) -> None:
        for f in self.floats:
            f.draw(surface)
        if self.popup_timer > 0 and self.popup_text:
            alpha = min(255, self.popup_timer * 4)
            fonts.blit_centered(
                surface,
                self.popup_text,
                cfg.SCREEN_HEIGHT // 2 - 60,
                30,
                cfg.WHITE,
                alpha=alpha,
            )
        if self.popup_timer > 0 and self.reward_text:
            alpha = min(255, self.popup_timer * 4)
            fonts.blit_centered(
                surface,
                self.reward_text,
                cfg.SCREEN_HEIGHT // 2 - 20,
                24,
                cfg.UI_YELLOW,
                bold=False,
                alpha=alpha,
            )
