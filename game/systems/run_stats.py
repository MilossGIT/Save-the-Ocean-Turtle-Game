"""Per-run statistics tracked during a single game session."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RunStats:
    """Counters for the current run — used on the end screen."""

    bubbles_collected: int = 0
    baby_turtles_rescued: int = 0
    sharks_hit: int = 0
    sharks_avoided_timer: int = 0
    sharks_avoided_best: int = 0
    treasures_opened: int = 0
    friendlies_waved: int = 0
    zone_index: int = 0
    mission_completed: bool = False

    def tick_shark_avoid(self) -> None:
        self.sharks_avoided_timer += 1
        if self.sharks_avoided_timer > self.sharks_avoided_best:
            self.sharks_avoided_best = self.sharks_avoided_timer

    def reset_shark_avoid(self) -> None:
        self.sharks_avoided_timer = 0

    def on_shark_hit(self) -> None:
        self.sharks_hit += 1
        self.reset_shark_avoid()
