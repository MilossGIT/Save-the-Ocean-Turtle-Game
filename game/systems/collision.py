"""Collision detection and game event handling."""

from __future__ import annotations

from game import config as cfg


class CollisionSystem:
    """Handles hits between turtle and world entities."""

    def __init__(self) -> None:
        self.message = ""
        self.message_timer = 0

    def set_message(self, text: str) -> None:
        self.message = text
        self.message_timer = cfg.MESSAGE_DURATION_FRAMES

    def update(self) -> None:
        if self.message_timer > 0:
            self.message_timer -= 1

    def check(self, turtle, spawner, session) -> None:
        """Process all collisions for one frame."""
        t_rect = turtle.rect
        gs = session

        # Positive pickups first — always allowed
        for power in spawner.powerups:
            if power.active and t_rect.colliderect(power.rect):
                power.active = False
                turtle.apply_power_up()
                gs.on_powerup_collected()

        for baby in spawner.baby_turtles:
            if baby.active and not baby.rescued and t_rect.colliderect(baby.rect):
                baby.rescue()
                gs.on_baby_rescued(baby.x, baby.y)

        for chest in spawner.treasures:
            if chest.active and not chest.opened and t_rect.colliderect(chest.rect):
                chest.open()
                gs.on_treasure_opened(chest.x, chest.y)

        for friend in spawner.friendlies:
            if friend.active and not friend.waved and t_rect.colliderect(friend.proximity_rect()):
                friend.trigger_wave()
                gs.on_friendly_wave(friend.x, friend.y, friend.kind)

        bubble_bonus = cfg.BUBBLE_SCORE_BONUS
        if gs.bubble_frenzy_timer > 0:
            bubble_bonus = int(bubble_bonus * cfg.BUBBLE_FRENZY_MULTIPLIER)

        for col in spawner.collectibles:
            if col.active and t_rect.colliderect(col.rect):
                col.active = False
                gs.score += bubble_bonus
                turtle.apply_boost()
                turtle.trigger_collect_squash()
                gs.on_bubble_collected(bubble_bonus, col.x, col.y)
                self.set_message("Clean bubble! +{} points!".format(bubble_bonus))

        # Hazards — skip shark damage when invincible or powered
        for obs in spawner.obstacles:
            if not obs.active:
                continue
            if not t_rect.colliderect(obs.rect):
                continue

            if obs.is_shark:
                if turtle.is_invincible or turtle.is_powered:
                    continue
                obs.active = False
                gs.lives -= 1
                turtle.on_shark_hit(obs.x, obs.y)
                gs.stats.on_shark_hit()
                gs.on_shark_collision()
                self.set_message("Watch out for sharks!")
            elif obs.is_plastic:
                if turtle.is_powered:
                    obs.active = False
                    gs.on_plastic_deflected(obs.x, obs.y)
                    continue
                obs.active = False
                turtle.on_plastic_hit(obs.x, obs.y)
                gs.score = max(0, gs.score - cfg.PLASTIC_SCORE_PENALTY)
                gs.on_plastic_collision()
                self.set_message("Ouch! Plastic slows you down — keep our ocean clean!")
