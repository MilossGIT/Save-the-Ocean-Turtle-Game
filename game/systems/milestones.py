"""Score milestone celebrations — non-blocking toasts."""

from __future__ import annotations

from game import config as cfg


class MilestoneSystem:
    """Triggers confetti-friendly celebration messages at score thresholds."""

    def __init__(self) -> None:
        self.reached: set[int] = set()
        self.active_message = ""
        self.active_timer = 0

    def update(self, score: float) -> bool:
        """Returns True when a new milestone fires this frame."""
        fired = False
        for threshold in cfg.MILESTONE_SCORES:
            if score >= threshold and threshold not in self.reached:
                self.reached.add(threshold)
                self.active_message = cfg.MILESTONE_MESSAGES.get(threshold, "Awesome!")
                self.active_timer = cfg.MESSAGE_DURATION_FRAMES
                fired = True
        if self.active_timer > 0:
            self.active_timer -= 1
        return fired

    def reset(self) -> None:
        self.reached.clear()
        self.active_message = ""
        self.active_timer = 0

    @property
    def showing(self) -> bool:
        return self.active_timer > 0
