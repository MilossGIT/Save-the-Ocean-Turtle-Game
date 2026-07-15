"""Obstacle and collectible spawning with difficulty ramp and rare events."""

from __future__ import annotations

import random

from game import config as cfg
from game.entities.collectibles import Collectible
from game.entities.obstacles import make_plastic, make_shark
from game.entities.specials import BabyTurtle, FriendlyAnimal, SeaweedPowerUp, TreasureChest
from game.world.sprite_fx import SpriteBackFX


class Spawner:
    """Spawns hazards, collectibles, and positive world events."""

    def __init__(self, back_fx: SpriteBackFX | None = None, difficulty: dict | None = None) -> None:
        self.obstacles: list = []
        self.collectibles: list = []
        self.baby_turtles: list[BabyTurtle] = []
        self.friendlies: list[FriendlyAnimal] = []
        self.treasures: list[TreasureChest] = []
        self.powerups: list[SeaweedPowerUp] = []
        self.spawn_timer = 0
        self.elapsed_frames = 0
        self._back_fx = back_fx
        self._difficulty = difficulty or {}
        self._baby_timer = 0
        self._friendly_timer = 0
        self._treasure_timer = 0
        self._seaweed_timer = 0

    @property
    def scroll_speed(self) -> float:
        ramp = min(1.0, self.elapsed_frames / (cfg.DIFFICULTY_RAMP_SECONDS * cfg.FPS))
        return cfg.BASE_SCROLL_SPEED + ramp * (cfg.MAX_SCROLL_SPEED - cfg.BASE_SCROLL_SPEED)

    @property
    def spawn_interval(self) -> int:
        ramp = min(1.0, self.elapsed_frames / (cfg.DIFFICULTY_RAMP_SECONDS * cfg.FPS))
        base = int(cfg.SPAWN_BASE_INTERVAL - ramp * (cfg.SPAWN_BASE_INTERVAL - cfg.SPAWN_MIN_INTERVAL))
        return base + self._difficulty.get("spawn_interval_bonus", 0)

    def _pick_y(self) -> float:
        return random.uniform(cfg.TURTLE_MIN_Y + 10, cfg.TURTLE_MAX_Y - 10)

    def _can_spawn(self) -> bool:
        if not self.obstacles:
            return True
        rightmost = max(o.x for o in self.obstacles if o.active)
        return (cfg.SCREEN_WIDTH + 50 - rightmost) >= cfg.SPAWN_MIN_GAP or rightmost < cfg.SCREEN_WIDTH

    def _update_list(self, entities: list, speed: float) -> list:
        for e in entities:
            if hasattr(e, "scroll_speed"):
                e.scroll_speed = speed
            e.update()
        return [e for e in entities if e.active]

    def update(self) -> None:
        self.elapsed_frames += 1
        self.spawn_timer += 1
        speed = self.scroll_speed

        self.obstacles = self._update_list(self.obstacles, speed)
        self.collectibles = self._update_list(self.collectibles, speed)
        self.baby_turtles = self._update_list(self.baby_turtles, speed)
        self.friendlies = self._update_list(self.friendlies, speed)
        self.treasures = self._update_list(self.treasures, speed)
        self.powerups = self._update_list(self.powerups, speed)

        if self.spawn_timer >= self.spawn_interval and self._can_spawn():
            self.spawn_timer = 0
            self._spawn_entity()

        self._try_special_spawns(speed)

    def _try_special_spawns(self, speed: float) -> None:
        self._baby_timer += 1
        if self._baby_timer >= cfg.BABY_TURTLE_SPAWN_INTERVAL:
            self._baby_timer = 0
            if random.random() < cfg.BABY_TURTLE_SPAWN_CHANCE:
                self.baby_turtles.append(BabyTurtle(cfg.SCREEN_WIDTH + 50, self._pick_y(), speed))

        self._friendly_timer += 1
        if self._friendly_timer >= cfg.FRIENDLY_SPAWN_INTERVAL:
            self._friendly_timer = 0
            if random.random() < cfg.FRIENDLY_SPAWN_CHANCE:
                self.friendlies.append(FriendlyAnimal(cfg.SCREEN_WIDTH + 50, self._pick_y(), speed))

        self._treasure_timer += 1
        if self._treasure_timer >= cfg.TREASURE_SPAWN_INTERVAL:
            self._treasure_timer = 0
            if random.random() < cfg.TREASURE_SPAWN_CHANCE:
                self.treasures.append(TreasureChest(cfg.SCREEN_WIDTH + 50, self._pick_y(), speed))

        self._seaweed_timer += 1
        if self._seaweed_timer >= cfg.SEAWEED_SPAWN_INTERVAL:
            self._seaweed_timer = 0
            if random.random() < cfg.SEAWEED_SPAWN_CHANCE:
                self.powerups.append(SeaweedPowerUp(cfg.SCREEN_WIDTH + 50, self._pick_y(), speed))

    def _spawn_entity(self) -> None:
        x = cfg.SCREEN_WIDTH + 60
        y = self._pick_y()
        speed = self.scroll_speed
        grace = self.elapsed_frames < cfg.SHARK_GRACE_SECONDS * cfg.FPS
        bubble_w = self._difficulty.get("bubble_weight", cfg.BUBBLE_WEIGHT)
        shark_w = self._difficulty.get("shark_weight", cfg.SHARK_WEIGHT)
        roll = random.random()

        if roll < bubble_w:
            self.collectibles.append(Collectible(x, y, speed))
        elif roll < bubble_w + shark_w and not grace:
            shark_speed = speed * self._difficulty.get("shark_speed_mult", 1.0)
            self.obstacles.append(make_shark(x, y, shark_speed, self._back_fx))
        else:
            self.obstacles.append(make_plastic(x, y, speed, self._back_fx))

    def draw(self, surface) -> None:
        for col in self.collectibles:
            col.draw(surface)
        for baby in self.baby_turtles:
            baby.draw(surface)
        for friend in self.friendlies:
            friend.draw(surface)
        for chest in self.treasures:
            chest.draw(surface)
        for power in self.powerups:
            power.draw(surface)
        for obs in self.obstacles:
            obs.draw(surface)
