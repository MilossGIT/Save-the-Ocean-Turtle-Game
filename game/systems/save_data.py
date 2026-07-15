"""Persistent save data — cosmetics, difficulty, lifetime stats."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field

from game import config as cfg
from game.paths import save_path

SAVE_PATH = save_path()


@dataclass
class SaveData:
    """Local progress stored between sessions."""

    version: int = cfg.SAVE_VERSION
    difficulty: str = "normal"
    selected_cosmetic: str = cfg.COSMETIC_NONE
    unlocked_cosmetics: list[str] = field(default_factory=list)
    best_score: int = 0
    lifetime_bubbles: int = 0
    lifetime_baby_rescues: int = 0
    lifetime_treasures: int = 0
    missions_completed: int = 0

    @classmethod
    def load(cls) -> SaveData:
        if not SAVE_PATH.exists():
            return cls()
        try:
            raw = json.loads(SAVE_PATH.read_text(encoding="utf-8"))
            data = cls()
            for key, value in raw.items():
                if hasattr(data, key):
                    setattr(data, key, value)
            if data.version < cfg.SAVE_VERSION:
                data.version = cfg.SAVE_VERSION
            return data
        except (json.JSONDecodeError, OSError, TypeError):
            return cls()

    def save(self) -> None:
        self.version = cfg.SAVE_VERSION
        SAVE_PATH.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    def unlock_cosmetics_from_stats(self) -> None:
        """Grant cosmetics when lifetime stats meet requirements."""
        stats = {
            "best_score": self.best_score,
            "baby_rescues": self.lifetime_baby_rescues,
            "bubbles_collected": self.lifetime_bubbles,
            "treasures_opened": self.lifetime_treasures,
            "missions_completed": self.missions_completed,
        }
        for cosmetic_id, (_name, stat_key, threshold) in cfg.COSMETICS.items():
            if stats.get(stat_key, 0) >= threshold and cosmetic_id not in self.unlocked_cosmetics:
                self.unlocked_cosmetics.append(cosmetic_id)

    def is_unlocked(self, cosmetic_id: str) -> bool:
        return cosmetic_id in self.unlocked_cosmetics

    def cycle_cosmetic(self, direction: int = 1) -> None:
        """Cycle through unlocked cosmetics (+1 forward, -1 backward)."""
        options = [cfg.COSMETIC_NONE] + sorted(self.unlocked_cosmetics)
        if not options:
            return
        try:
            idx = options.index(self.selected_cosmetic)
        except ValueError:
            idx = 0
        self.selected_cosmetic = options[(idx + direction) % len(options)]

    def get_difficulty_profile(self) -> dict:
        if self.difficulty == "easy":
            return {
                "starting_lives": cfg.EASY_STARTING_LIVES,
                "plastic_weight": cfg.EASY_PLASTIC_WEIGHT,
                "shark_weight": cfg.EASY_SHARK_WEIGHT,
                "bubble_weight": cfg.EASY_BUBBLE_WEIGHT,
                "spawn_interval_bonus": cfg.EASY_SPAWN_INTERVAL_BONUS,
                "shark_speed_mult": cfg.EASY_SHARK_SPEED_MULT,
            }
        return {
            "starting_lives": cfg.STARTING_LIVES,
            "plastic_weight": cfg.PLASTIC_WEIGHT,
            "shark_weight": cfg.SHARK_WEIGHT,
            "bubble_weight": cfg.BUBBLE_WEIGHT,
            "spawn_interval_bonus": 0,
            "shark_speed_mult": 1.0,
        }

    def toggle_difficulty(self) -> str:
        self.difficulty = "easy" if self.difficulty == "normal" else "normal"
        return self.difficulty
