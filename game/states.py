"""Game state machine and main play loop."""

from __future__ import annotations

import math
import random
from enum import Enum, auto

import pygame

from game import config as cfg
from game.entities.turtle import Turtle
from game.systems.audio import AudioSystem
from game.systems.collision import CollisionSystem
from game.systems.feedback import FeedbackSystem
from game.systems.milestones import MilestoneSystem
from game.systems.missions import DailyMission
from game.systems.run_stats import RunStats
from game.systems.save_data import SaveData
from game.systems.spawner import Spawner
from game.systems.zones import ZONES, ZoneManager
from game.ui.hud import HUD
from game.ui.screens import Screens
from game.world.assets import get_assets
from game.world.background import Background
from game.world.particles import ParticleSystem
from game.world.sprite_fx import SpriteBackFX


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    COSMETICS = auto()


class GameSession:
    """Orchestrates all game systems."""

    def __init__(self, screen: pygame.Surface):
        get_assets()
        self.screen = screen
        self.save = SaveData.load()
        self.save.unlock_cosmetics_from_stats()

        self.state = GameState.MENU
        self.back_fx = SpriteBackFX()
        self.background = Background()
        self.particles = ParticleSystem()
        self.turtle = Turtle(self.back_fx)
        self.spawner = Spawner(self.back_fx)
        self.collision = CollisionSystem()
        self.hud = HUD()
        self.screens = Screens()
        self.audio = AudioSystem()
        self.audio.init()
        self.feedback = FeedbackSystem()
        self.milestones = MilestoneSystem()
        self.mission = DailyMission.generate()
        self.stats = RunStats()

        self.score = 0.0
        self.lives = cfg.STARTING_LIVES
        self.max_lives = cfg.STARTING_LIVES
        self.shake_timer = 0
        self.bubble_frenzy_timer = 0
        self.celebration_timer = 0
        self._apply_cosmetic()

    def _difficulty_profile(self) -> dict:
        return self.save.get_difficulty_profile()

    def _apply_cosmetic(self) -> None:
        self.turtle.cosmetic_id = self.save.selected_cosmetic

    def reset(self) -> None:
        profile = self._difficulty_profile()
        self.turtle = Turtle(self.back_fx)
        self.turtle.cosmetic_id = self.save.selected_cosmetic
        self.spawner = Spawner(self.back_fx, profile)
        self.collision = CollisionSystem()
        self.particles = ParticleSystem()
        self.feedback = FeedbackSystem()
        self.milestones = MilestoneSystem()
        self.mission = DailyMission.generate()
        self.stats = RunStats()
        self.score = 0.0
        self.max_lives = profile["starting_lives"]
        self.lives = self.max_lives
        self.shake_timer = 0
        self.bubble_frenzy_timer = 0
        self.celebration_timer = 0
        self.background.zones = ZoneManager()
        self.background.reef_index = 0
        self.background.reef_from = 0
        self.background.reef_transition = 0
        self.background.cycle_timer = 0
        self.background.reef_dwell_timer = 0

    # --- Event callbacks from collision / gameplay ---

    def on_baby_rescued(self, x: float, y: float) -> None:
        self.score += cfg.BABY_TURTLE_SCORE
        self.stats.baby_turtles_rescued += 1
        self.feedback.add_float("Baby Turtle Rescued!", x, y, cfg.SEAWEED_GREEN, 26)
        self.feedback.add_score(cfg.BABY_TURTLE_SCORE, x, y)
        self.particles.spawn_sparkle(x, y)
        self.audio.play_happy()
        self._check_mission_complete()

    def on_bubble_collected(self, bonus: int, x: float, y: float) -> None:
        self.stats.bubbles_collected += 1
        self.feedback.add_score(bonus, x, y)
        self.particles.spawn_bubble_pop(x, y)
        self.particles.spawn_sparkle(x, y)
        self._check_mission_complete()

    def on_friendly_wave(self, x: float, y: float, kind: str = "") -> None:
        self.score += cfg.FRIENDLY_PROXIMITY_SCORE
        self.stats.friendlies_waved += 1
        count = self.stats.friendlies_waved
        self.particles.spawn_friend_wave(x, y)

        if self.mission.kind == "friendlies" and not self.stats.mission_completed:
            self.feedback.add_float(
                f"Friend {count}/{self.mission.target}!",
                x,
                y - 35,
                cfg.SEAWEED_GREEN,
                26,
            )
            if count == self.mission.target:
                self._celebrate_friend_squad(x, y)
        else:
            self.feedback.add_float("Hi friend!", x, y, cfg.FISH_BLUE, 20)

        self.feedback.add_score(cfg.FRIENDLY_PROXIMITY_SCORE, x, y)
        self.audio.play_wave()
        self._check_mission_complete()

    def _celebrate_friend_squad(self, x: float, y: float) -> None:
        """Special moment when the 8th sea friend joins the squad."""
        self.turtle.apply_friend_boost()
        self.score += cfg.FRIEND_MISSION_BONUS_SCORE
        self.celebration_timer = cfg.FRIEND_CELEBRATION_FRAMES
        self.particles.spawn_friend_party(self.turtle.x, self.turtle.y)
        self.feedback.show_popup("Friend Squad United!")
        self.feedback.show_reward(
            f"Zoom boost for {cfg.FRIEND_MISSION_BOOST_FRAMES // cfg.FPS}s! "
            f"+{cfg.FRIEND_MISSION_BONUS_SCORE} pts"
        )
        self.audio.play_milestone()

    def on_treasure_opened(self, x: float, y: float) -> None:
        self.stats.treasures_opened += 1
        reward = random.choice(["score", "life", "frenzy", "power"])
        if reward == "score":
            self.score += cfg.TREASURE_SCORE_REWARD
            self.feedback.show_reward(f"Treasure! +{cfg.TREASURE_SCORE_REWARD} score")
            self.feedback.add_score(cfg.TREASURE_SCORE_REWARD, x, y)
        elif reward == "life":
            self.lives = min(self.max_lives + 1, self.lives + 1)
            self.feedback.show_reward("Treasure! Extra life!")
        elif reward == "frenzy":
            self.bubble_frenzy_timer = cfg.BUBBLE_FRENZY_DURATION_FRAMES
            self.feedback.show_reward("Treasure! Bubble Frenzy!")
        else:
            self.turtle.apply_power_up()
            self.feedback.show_reward("Treasure! Seaweed Power!")
        self.particles.spawn_confetti()
        self.audio.play_treasure()
        self._check_mission_complete()

    def on_powerup_collected(self) -> None:
        self.feedback.show_popup("Seaweed Power!")
        self.audio.play_powerup()

    def on_plastic_deflected(self, x: float, y: float) -> None:
        self.feedback.add_float("Blocked!", x, y, cfg.SEAWEED_GREEN, 20)
        self.particles.spawn_sparkle(x, y)

    def on_shark_collision(self) -> None:
        pass  # audio/particles handled in update after message change

    def on_plastic_collision(self) -> None:
        pass

    def _check_mission_complete(self) -> None:
        if self.stats.mission_completed:
            return
        if self.mission.is_complete(self.stats):
            self.stats.mission_completed = True
            self.score += cfg.MISSION_SCORE_REWARD
            self.lives = min(self.max_lives + 1, self.lives + 1)
            self.save.missions_completed += 1
            self.feedback.show_popup("Mission Complete! +1 life")
            self.particles.spawn_confetti()
            self.audio.play_milestone()

    def _finalize_run(self) -> None:
        final = int(self.score)
        if final > self.save.best_score:
            self.save.best_score = final
        self.save.lifetime_bubbles += self.stats.bubbles_collected
        self.save.lifetime_baby_rescues += self.stats.baby_turtles_rescued
        self.save.lifetime_treasures += self.stats.treasures_opened
        self.save.unlock_cosmetics_from_stats()
        self.save.save()
        self.screens.pick_end_content()

    # --- Input ---

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                self.audio.toggle()
            if event.key == pygame.K_ESCAPE:
                if self.state == GameState.PLAYING:
                    self.state = GameState.PAUSED
                elif self.state == GameState.PAUSED:
                    self.state = GameState.PLAYING
                elif self.state == GameState.COSMETICS:
                    self.state = GameState.MENU
                elif self.state in (GameState.MENU, GameState.GAME_OVER):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            if event.key == pygame.K_SPACE:
                if self.state == GameState.MENU:
                    self.reset()
                    self.state = GameState.PLAYING
                elif self.state == GameState.GAME_OVER:
                    self.reset()
                    self.state = GameState.PLAYING
                elif self.state == GameState.PAUSED:
                    self.reset()
                    self.state = GameState.PLAYING
            if event.key == pygame.K_q and self.state == GameState.PAUSED:
                self.state = GameState.MENU
            if event.key == pygame.K_c and self.state == GameState.MENU:
                self.state = GameState.COSMETICS
            if event.key == pygame.K_e and self.state == GameState.MENU:
                self.save.toggle_difficulty()
                self.save.save()
            if self.state == GameState.COSMETICS:
                if event.key == pygame.K_LEFT:
                    self.save.cycle_cosmetic(-1)
                    self._apply_cosmetic()
                    self.save.save()
                elif event.key == pygame.K_RIGHT:
                    self.save.cycle_cosmetic(1)
                    self._apply_cosmetic()
                    self.save.save()

    def update(self) -> None:
        self.screens.update()
        self.back_fx.update()
        self.feedback.update()

        if self.state == GameState.MENU:
            self.background.update(cfg.BASE_SCROLL_SPEED * 0.5, 0, menu_mode=True)
            self.particles.set_zone_color(cfg.BUBBLE_COLOR)
            self.particles.update()
            bob = math.sin(self.screens._anim * 0.03) * 8
            drift = math.cos(self.screens._anim * 0.022) * 6
            self.turtle.x = cfg.MENU_TURTLE_X + drift
            self.turtle.y = cfg.MENU_TURTLE_Y + bob
            self.turtle.moving = True
            self.turtle._anim_counter += 1
            if self.turtle._anim_counter >= cfg.MENU_TURTLE_ANIM_STRIDE:
                self.turtle._anim_counter = 0
                self.turtle.anim_frame = (self.turtle.anim_frame + 1) % self.turtle.FRAMES

        if self.state == GameState.COSMETICS:
            self.background.update(cfg.BASE_SCROLL_SPEED * 0.4, 0, menu_mode=True)
            bob = math.sin(self.screens._anim * 0.05) * 6
            self.turtle.x = cfg.MENU_TURTLE_X
            self.turtle.y = cfg.MENU_TURTLE_Y + bob
            self.turtle.moving = True
            self.turtle._anim_counter += 1
            if self.turtle._anim_counter >= cfg.MENU_TURTLE_ANIM_STRIDE:
                self.turtle._anim_counter = 0
                self.turtle.anim_frame = (self.turtle.anim_frame + 1) % self.turtle.FRAMES

        if self.state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            self.turtle.handle_input(keys)

            if self.turtle.moving:
                self.particles.spawn_trail(
                    self.turtle.x - 20, self.turtle.y,
                    self.turtle.is_boosted or self.turtle.is_powered,
                    rainbow=self.turtle.is_powered or self.turtle.is_friend_boosted,
                )

            if self.turtle.pop_direction_changed():
                self.particles.spawn_splash(self.turtle.x, self.turtle.y)
                self.audio.play_splash()

            self.turtle.update()
            scroll = self.spawner.scroll_speed
            self.background.update(scroll, self.score)
            self.stats.zone_index = self.background.zones.current_index
            self.particles.set_zone_color(self.background.zones.particle_color())
            self.spawner.update()
            self.particles.update()

            if self.bubble_frenzy_timer > 0:
                self.bubble_frenzy_timer -= 1
            if self.celebration_timer > 0:
                self.celebration_timer -= 1

            self.stats.tick_shark_avoid()

            prev_msg = self.collision.message
            self.collision.check(self.turtle, self.spawner, self)
            if self.collision.message != prev_msg:
                msg = self.collision.message.lower()
                if "shark" in msg:
                    self.audio.play_hurt()
                    self.particles.spawn_hit(self.turtle.x, self.turtle.y, "shark")
                    self.shake_timer = 22
                elif "plastic" in msg:
                    self.audio.play_plastic()
                    self.particles.spawn_hit(self.turtle.x, self.turtle.y, "plastic")
                elif "bubble" in msg:
                    self.audio.play_collect()

            if self.milestones.update(self.score):
                self.particles.spawn_confetti()
                self.audio.play_milestone()

            self.collision.update()
            self.score += cfg.SCORE_PER_FRAME
            if self.shake_timer > 0:
                self.shake_timer -= 1

            if self.lives <= 0:
                self._finalize_run()
                self.state = GameState.GAME_OVER

    def draw(self) -> None:
        self.screen.fill(cfg.WATER_DEEP)
        self.background.draw(self.screen)

        shake_x = shake_y = 0
        if self.shake_timer > 0:
            shake_x = random.randint(-5, 5)
            shake_y = random.randint(-4, 4)

        if self.state in (GameState.PLAYING, GameState.PAUSED, GameState.GAME_OVER):
            layer = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
            self.particles.draw(layer)
            self.spawner.draw(layer)
            self.turtle.draw(layer)
            self.feedback.draw(layer)
            self.screen.blit(layer, (shake_x, shake_y))
        elif self.state == GameState.MENU:
            self.particles.draw(self.screen)

        if self.state == GameState.PLAYING:
            msg_alpha = min(1.0, self.collision.message_timer / 30)
            milestone = self.milestones.active_message if self.milestones.showing else ""
            self.hud.draw(
                self.screen,
                int(self.score),
                self.lives,
                self.max_lives,
                self.collision.message,
                msg_alpha,
                self.turtle.is_slowed,
                self.mission.progress_text(self.mission.current_value(self.stats)),
                self.turtle.power_timer / cfg.FPS,
                milestone,
                self.background.zones.zone.name,
                self.bubble_frenzy_timer / cfg.FPS,
                self.turtle.friend_boost_timer / cfg.FPS,
            )
        elif self.state == GameState.PAUSED:
            self.hud.draw(self.screen, int(self.score), self.lives, self.max_lives, "", 0, False)
            self.screens.draw_pause(self.screen)
        elif self.state == GameState.MENU:
            self.screens.draw_start(self.screen, self.save)
            self.turtle.draw(self.screen, menu_showcase=True)
        elif self.state == GameState.COSMETICS:
            self.screens.draw_cosmetics(self.screen, self.save)
            self.turtle.draw(self.screen, menu_showcase=True)
        elif self.state == GameState.GAME_OVER:
            self.screens.draw_game_over(
                self.screen, int(self.score), self.stats, self.save, self.stats.mission_completed
            )

        if self.celebration_timer > 0 and self.state == GameState.PLAYING:
            t = self.celebration_timer / cfg.FRIEND_CELEBRATION_FRAMES
            alpha = int(90 * t)
            glow = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
            glow.fill((255, 230, 120, alpha))
            self.screen.blit(glow, (0, 0))
