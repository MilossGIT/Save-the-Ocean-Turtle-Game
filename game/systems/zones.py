"""Ocean zone definitions and smooth transitions."""

from __future__ import annotations

from dataclasses import dataclass

from game import config as cfg


@dataclass(frozen=True)
class OceanZone:
    """Visual theme for a section of the ocean."""

    name: str
    tint: tuple[int, int, int]
    particle_color: tuple[int, int, int]
    decoration_color: tuple[int, int, int]
    ambient_alpha: int


ZONES: tuple[OceanZone, ...] = (
    OceanZone("Coral Reef", (255, 240, 230), cfg.BUBBLE_COLOR, cfg.CORAL_PINK, 18),
    OceanZone("Kelp Forest", (200, 255, 210), (140, 230, 170), cfg.SEAWEED_GREEN, 22),
    OceanZone("Deep Ocean", (180, 210, 255), (120, 180, 240), (60, 100, 180), 28),
    OceanZone("Tropical Lagoon", (255, 255, 210), (255, 240, 160), cfg.FISH_YELLOW, 16),
    OceanZone("Night Ocean", (200, 180, 255), (160, 140, 255), cfg.CORAL_PURPLE, 32),
)


class ZoneManager:
    """Picks zone from score and crossfades between themes."""

    def __init__(self) -> None:
        self.current_index = 0
        self.transition_timer = 0
        self.transition_from = 0
        self.transition_to = 0

    @property
    def zone(self) -> OceanZone:
        return ZONES[self.current_index]

    def update(self, score: float) -> None:
        target = min(len(ZONES) - 1, int(score // cfg.ZONE_SCORE_INTERVAL))
        if target != self.current_index and self.transition_timer == 0:
            self.transition_from = self.current_index
            self.transition_to = target
            self.transition_timer = cfg.ZONE_TRANSITION_FRAMES
            self.current_index = target
        if self.transition_timer > 0:
            self.transition_timer -= 1

    @property
    def blend(self) -> float:
        if self.transition_timer <= 0:
            return 1.0
        raw = 1.0 - self.transition_timer / cfg.ZONE_TRANSITION_FRAMES
        t = max(0.0, min(1.0, raw))
        return t * t * (3.0 - 2.0 * t)

    def blended_tint(self) -> tuple[int, int, int]:
        if self.transition_timer <= 0:
            return self.zone.tint
        a = ZONES[self.transition_from].tint
        b = ZONES[self.transition_to].tint
        t = self.blend
        return (
            int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t),
        )

    def particle_color(self) -> tuple[int, int, int]:
        return self.zone.particle_color
