"""Game constants and configuration."""

# Screen
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60
TITLE = "Save the Ocean — Turtle Game"

# Colors — bright kid-friendly ocean palette
SKY_TOP = (120, 210, 255)
SKY_BOTTOM = (70, 170, 240)
WATER_SHALLOW = (40, 190, 210)
WATER_DEEP = (10, 120, 180)
WATER_DARK = (5, 70, 130)
CORAL_PINK = (255, 120, 140)
CORAL_ORANGE = (255, 170, 110)
CORAL_PURPLE = (200, 120, 220)
SEAWEED_GREEN = (30, 160, 90)
SEAWEED_DARK = (20, 110, 65)
SAND = (245, 220, 170)
SAND_DARK = (210, 180, 130)
WHITE = (255, 255, 255)
BLACK = (25, 35, 45)
TURTLE_SHELL = (45, 155, 75)
TURTLE_SHELL_DARK = (25, 110, 55)
TURTLE_SHELL_LIGHT = (95, 200, 120)
TURTLE_SKIN = (110, 210, 150)
TURTLE_SKIN_DARK = (70, 170, 115)
TURTLE_BELLY = (180, 245, 200)
TURTLE_OUTLINE = (20, 80, 50)
PLASTIC_WHITE = (235, 245, 255)
PLASTIC_BLUE = (80, 150, 255)
PLASTIC_SHADOW = (140, 170, 200)
SHARK_TOP = (95, 120, 145)
SHARK_BELLY = (210, 225, 235)
SHARK_DARK = (55, 70, 90)
SHARK_OUTLINE = (35, 45, 60)
HEART_RED = (255, 90, 110)
BUBBLE_COLOR = (170, 240, 255)
UI_YELLOW = (255, 230, 90)
UI_SHADOW = (0, 40, 60)
DEBUFF_TINT = (80, 60, 40)
FISH_BLUE = (80, 170, 230)
FISH_YELLOW = (255, 210, 80)

# Player — sized to user-provided turtle art (install_user_assets.py)
TURTLE_BASE_SPEED = 3.0
TURTLE_H_SPEED = 2.0
TURTLE_WIDTH = 150
TURTLE_HEIGHT = 100
TURTLE_X = SCREEN_WIDTH // 3
TURTLE_MIN_Y = 25
TURTLE_MAX_Y = SCREEN_HEIGHT - 25
TURTLE_MIN_X = 40
TURTLE_MAX_X = SCREEN_WIDTH - 60

# Debuff
SLOW_MULTIPLIER = 0.4
SLOW_DURATION_FRAMES = 150
INVINCIBLE_FRAMES = 90
PLASTIC_HIT_FRAMES = 45
SHARK_HIT_FRAMES = 50

# Power-up (glowing seaweed)
POWERUP_DURATION_FRAMES = 8 * FPS
POWERUP_SPEED_BOOST = 1.25
BUBBLE_FRENZY_DURATION_FRAMES = 10 * FPS
BUBBLE_FRENZY_MULTIPLIER = 2.0

# Lives & score
STARTING_LIVES = 3
EASY_STARTING_LIVES = 5
SCORE_PER_FRAME = 0.05
PLASTIC_SCORE_PENALTY = 5
BUBBLE_SCORE_BONUS = 10
BUBBLE_SPEED_BOOST = 1.15
BUBBLE_BOOST_FRAMES = 60
BABY_TURTLE_SCORE = 50
FRIENDLY_PROXIMITY_SCORE = 5
FRIENDLY_PROXIMITY_RADIUS = 90
FRIEND_MISSION_SPEED_BOOST = 1.35
FRIEND_MISSION_BOOST_FRAMES = 12 * FPS
FRIEND_MISSION_BONUS_SCORE = 40
FRIEND_CELEBRATION_FRAMES = 150
TREASURE_SCORE_REWARD = 100

# Scroll & difficulty
BASE_SCROLL_SPEED = 1.8
MAX_SCROLL_SPEED = 3.5
DIFFICULTY_RAMP_SECONDS = 45
SHARK_GRACE_SECONDS = 8

# Spawner — normal difficulty weights
SPAWN_MIN_GAP = 280
SPAWN_BASE_INTERVAL = 140
SPAWN_MIN_INTERVAL = 85
PLASTIC_WEIGHT = 0.70
SHARK_WEIGHT = 0.25
BUBBLE_WEIGHT = 0.05

# Easy mode modifiers (applied via difficulty profile)
EASY_PLASTIC_WEIGHT = 0.50
EASY_SHARK_WEIGHT = 0.12
EASY_BUBBLE_WEIGHT = 0.15
EASY_SPAWN_INTERVAL_BONUS = 35
EASY_SHARK_SPEED_MULT = 0.75

# Rare spawn timers (frames between spawn attempts)
BABY_TURTLE_SPAWN_INTERVAL = 720
BABY_TURTLE_SPAWN_CHANCE = 0.35
FRIENDLY_SPAWN_INTERVAL = 300
FRIENDLY_SPAWN_CHANCE = 0.55
TREASURE_SPAWN_INTERVAL = 900
TREASURE_SPAWN_CHANCE = 0.30
SEAWEED_SPAWN_INTERVAL = 600
SEAWEED_SPAWN_CHANCE = 0.40

# Ocean zones — transition every N score points (m)
ZONE_SCORE_INTERVAL = 250
ZONE_TRANSITION_FRAMES = 300

# Reef background scrolling and variant cycling
BG_SCROLL_FACTOR = 0.55
REEF_VARIANT_SCORE_INTERVAL = 250
REEF_VARIANT_CYCLING = False  # keep one coral reef look while playing; menu still cycles
REEF_MIN_DWELL_FRAMES = 5000
REEF_CROSSFADE_FRAMES = 360   # ~6 sec smooth crossfade
MENU_BG_CYCLE_FRAMES = 3600   # ~60 sec between reef views on menu

# Turtle swim animation — higher = slower flipper cycle
TURTLE_ANIM_STRIDE = 7
MENU_TURTLE_ANIM_STRIDE = 10

# Menu layout — keep turtle below the title panel
MENU_SWIM_LANE_Y = 310
MENU_PANEL_BOTTOM = 300
MENU_TURTLE_X = 300
MENU_TURTLE_Y = 430

# Milestones
MILESTONE_SCORES = (100, 500, 1000, 2000, 5000)
MILESTONE_MESSAGES = {
    100: "Great Job!",
    500: "Ocean Hero!",
    1000: "Amazing Explorer!",
    2000: "Reef Champion!",
    5000: "Legend of the Sea!",
}

# Daily mission reward
MISSION_SCORE_REWARD = 75

# Feedback
FLOAT_TEXT_DURATION = 90
SQUASH_STRETCH_FRAMES = 12

# Hitboxes (smaller than sprite for forgiving collisions)
HITBOX_SHRINK = 0.72

# UI
FONT_SIZE_LARGE = 48
FONT_SIZE_MEDIUM = 32
FONT_SIZE_SMALL = 24
MESSAGE_DURATION_FRAMES = 120

# Assets — user-provided PNGs (install_user_assets.py)
TURTLE_ANIM_FRAMES = 8
BABY_TURTLE_WIDTH = 85
FRIENDLY_MAX = 105
SPECIAL_COLLECTIBLE_MAX = 110

# Save data
SAVE_VERSION = 1
SAVE_FILENAME = "savegame.json"

# Cosmetics (id -> display name, unlock type, unlock value)
COSMETIC_NONE = "none"
COSMETICS = {
    "pirate_hat": ("Pirate Hat", "best_score", 500),
    "princess_crown": ("Princess Crown", "baby_rescues", 5),
    "sunglasses": ("Sunglasses", "bubbles_collected", 100),
    "red_shell": ("Red Shell", "treasures_opened", 3),
    "blue_shell": ("Blue Shell", "best_score", 1500),
    "rainbow_shell": ("Rainbow Shell", "missions_completed", 5),
}

# Ocean facts (shown after each run)
OCEAN_FACTS = [
    "Sea turtles can live more than 50 years!",
    "Plastic can stay in the ocean for hundreds of years.",
    "The ocean produces over half of Earth's oxygen!",
    "Baby sea turtles use moonlight to find the ocean.",
    "Dolphins sleep with one eye open!",
    "Coral reefs are home to 25% of all sea life!",
    "A group of fish is called a school!",
    "Sea turtles remember the beach where they were born!",
]

# Encouraging end-screen messages
ENCOURAGING_MESSAGES = [
    "You're helping keep the ocean clean!",
    "Every bubble counts!",
    "See you in the ocean again!",
    "You made the reef a happier place!",
    "The turtles are cheering for you!",
]
