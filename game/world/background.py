"""Ocean background with horizontal scroll and reef variant crossfades."""

from __future__ import annotations

import math

import pygame

from game import config as cfg
from game.systems.zones import ZoneManager
from game.ui import fonts
from game.world.assets import get_assets


def _ease(t: float) -> float:
    """Smooth step — slow start and end for gentle crossfades."""
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


class Background:
    """Scrollable zone backgrounds with smooth reef cycling and crossfades."""

    def __init__(self) -> None:
        self.scroll = 0.0
        self._assets = get_assets()
        self.zones = ZoneManager()
        self.reef_index = 0
        self.reef_from = 0
        self.reef_transition = 0
        self.cycle_timer = 0
        self.reef_dwell_timer = 0
        self.menu_mode = False

    def update(self, scroll_speed: float, score: float = 0.0, *, menu_mode: bool = False) -> None:
        self.menu_mode = menu_mode
        self.scroll += scroll_speed
        if not menu_mode:
            self.zones.update(score)
            self._update_reef_cycle(score)
        else:
            self.cycle_timer += 1
            if self.cycle_timer >= cfg.MENU_BG_CYCLE_FRAMES and self.reef_transition == 0:
                self._start_reef_transition((self.reef_index + 1) % self._reef_count())
                self.cycle_timer = 0
        if self.reef_transition > 0:
            self.reef_transition -= 1
        else:
            self.reef_dwell_timer += 1

    def _reef_count(self) -> int:
        reefs = self._assets.reef_backgrounds
        return max(1, len([r for r in reefs if r is not None]))

    def _start_reef_transition(self, target: int) -> None:
        if target == self.reef_index:
            return
        self.reef_from = self.reef_index
        self.reef_index = target
        self.reef_transition = cfg.REEF_CROSSFADE_FRAMES
        self.reef_dwell_timer = 0

    def _update_reef_cycle(self, score: float) -> None:
        if not cfg.REEF_VARIANT_CYCLING:
            return
        if self.zones.current_index != 0:
            return
        if self.reef_dwell_timer < cfg.REEF_MIN_DWELL_FRAMES:
            return
        target = int(score // cfg.REEF_VARIANT_SCORE_INTERVAL) % self._reef_count()
        if target != self.reef_index and self.reef_transition == 0:
            self._start_reef_transition(target)

    def _reef_blend(self) -> float:
        if self.reef_transition <= 0:
            return 1.0
        raw = 1.0 - self.reef_transition / cfg.REEF_CROSSFADE_FRAMES
        return _ease(raw)

    def _zone_bg(self) -> pygame.Surface | None:
        if self.zones.current_index == 0 and not self.menu_mode:
            return self._assets.reef_background(self.reef_index)
        if self.menu_mode:
            return self._assets.reef_background(self.reef_index)
        return self._assets.zone_background(self.zones.current_index)

    def _previous_zone_bg(self) -> pygame.Surface | None:
        if self.reef_transition > 0 and (self.menu_mode or self.zones.current_index == 0):
            return self._assets.reef_background(self.reef_from)
        if self.zones.transition_timer > 0:
            return self._assets.zone_background(self.zones.transition_from)
        return None

    def _zone_blend(self) -> float:
        if self.reef_transition > 0 and (self.menu_mode or self.zones.current_index == 0):
            return self._reef_blend()
        if self.zones.transition_timer > 0:
            return self.zones.blend
        return 1.0

    def _scroll_offset(self, img: pygame.Surface) -> int:
        w = img.get_width()
        sw = cfg.SCREEN_WIDTH
        if w <= sw:
            return int(math.sin(self.scroll * 0.025) * 10)
        return int(self.scroll * cfg.BG_SCROLL_FACTOR) % (w - sw)

    def _blit_scrolling(
        self,
        surface: pygame.Surface,
        img: pygame.Surface,
        alpha: int = 255,
        *,
        offset: int | None = None,
    ) -> None:
        if alpha <= 0:
            return
        if offset is None:
            offset = self._scroll_offset(img)
        if alpha >= 255:
            surface.blit(img, (-offset, 0))
            return
        faded = img.copy()
        faded.set_alpha(alpha)
        surface.blit(faded, (-offset, 0))

    def draw(self, surface: pygame.Surface) -> None:
        current = self._zone_bg()
        previous = self._previous_zone_bg()
        blend = self._zone_blend()

        # Keep both layers aligned during crossfade so the swap feels smooth.
        scroll_offset = self._scroll_offset(current) if current else 0

        if previous and blend < 1.0:
            self._blit_scrolling(surface, previous, 255, offset=scroll_offset)
            if current and current is not previous:
                self._blit_scrolling(surface, current, int(255 * blend), offset=scroll_offset)
        elif current:
            self._blit_scrolling(surface, current, offset=scroll_offset)
        else:
            surface.fill(cfg.WATER_DEEP)

        if not self.menu_mode and self.zones.transition_timer > cfg.ZONE_TRANSITION_FRAMES - 90:
            alpha = min(
                200,
                int(200 * (1.0 - (self.zones.transition_timer - (cfg.ZONE_TRANSITION_FRAMES - 90)) / 90)),
            )
            fonts.blit_centered(
                surface,
                self.zones.zone.name,
                80,
                28,
                cfg.WHITE,
                bold=True,
                alpha=alpha,
            )
