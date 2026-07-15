"""Daily mission generation and progress tracking."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date

from game import config as cfg


@dataclass
class DailyMission:
    """One random goal per game session, seeded by today's date."""

    kind: str
    target: int
    description: str
    reward_text: str = "+1 life & bonus score!"

    @classmethod
    def generate(cls) -> DailyMission:
        rng = random.Random(date.today().isoformat())
        templates = [
            ("bubbles", 30, "Collect 30 bubbles"),
            ("baby_rescue", 2, "Rescue 2 baby turtles"),
            ("shark_avoid", 45 * cfg.FPS, "Avoid sharks for 45 seconds"),
            ("treasures", 5, "Open 5 treasure chests"),
            ("friendlies", 8, "Befriend 8 sea creatures"),
        ]
        kind, target, desc = rng.choice(templates)
        return cls(kind=kind, target=target, description=desc)

    def progress_text(self, current: int) -> str:
        if self.kind == "shark_avoid":
            secs = current // cfg.FPS
            need = self.target // cfg.FPS
            return f"Mission: {self.description} ({secs}/{need}s)"
        if self.kind == "friendlies" and current >= self.target:
            return f"Mission: Friend squad united! ({self.target}/{self.target})"
        return f"Mission: {self.description} ({current}/{self.target})"

    def is_complete(self, stats) -> bool:
        if self.kind == "bubbles":
            return stats.bubbles_collected >= self.target
        if self.kind == "baby_rescue":
            return stats.baby_turtles_rescued >= self.target
        if self.kind == "shark_avoid":
            return stats.sharks_avoided_best >= self.target
        if self.kind == "treasures":
            return stats.treasures_opened >= self.target
        if self.kind == "friendlies":
            return stats.friendlies_waved >= self.target
        return False

    def current_value(self, stats) -> int:
        mapping = {
            "bubbles": stats.bubbles_collected,
            "baby_rescue": stats.baby_turtles_rescued,
            "shark_avoid": stats.sharks_avoided_best,
            "treasures": stats.treasures_opened,
            "friendlies": stats.friendlies_waved,
        }
        val = mapping.get(self.kind, 0)
        if self.kind == "friendlies":
            return min(val, self.target)
        return val
