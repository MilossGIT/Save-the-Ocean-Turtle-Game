# Save the Ocean — Turtle Game

A fun, kid-friendly endless ocean game for ages **7 and up**. Help a sea turtle swim through the ocean, dodge plastic trash and sharks, and collect clean bubbles!

### New in this version

- **Baby turtle rescue**, **friendly sea animals**, **treasure chests**, and **seaweed power-ups**
- **5 ocean zones** that change every 500 points
- **Daily missions**, **milestones**, **floating score feedback**, and **cosmetic unlocks**
- **Easy / Normal** difficulty (press **E** on the menu)
- **Cosmetics screen** — press **C** on the menu

## How to Play

- **Up / Down arrows** — swim up and down to dodge obstacles
- **Left / Right arrows** — move around the ocean
- **Space** — start or play again
- **Esc** — pause / resume (during game)
- **Space** — start or restart (menu, pause, or game over)
- **Q** — return to menu (while paused)
- **M** — toggle sound on/off
- **F** or **F11** — toggle fullscreen
- **Drag window corner** — resize the window (game scales up smoothly)
- **E** — switch Easy / Normal mode (menu)
- **C** — open cosmetic outfits (menu)

### Obstacles

| Hazard | What happens |
|--------|--------------|
| Plastic (bags, rings, bottles) | Slows the turtle down for a few seconds |
| Shark | Takes away one life (you start with 3) |
| Clean bubble | +10 points and a small speed boost! |

Swim as far as you can and keep our ocean clean!

## Desktop app (double-click to play)

You can turn the game into a **Mac app** — no terminal, no Python, no server. Just double-click the icon on your Desktop.

**One-time build** (needs Python installed once):

```bash
bash scripts/build_mac_app.sh
```

When it finishes, you'll have:

```
dist/Save the Ocean.app
```

**Put it on your Desktop:** the build script tries to install automatically. If you see `Operation not permitted`, macOS is blocking an overwrite of the old app — quit the game, **drag the old Desktop app to Trash in Finder**, then run the build again.

Manual install (use Finder or `ditto`, not `cp -R`):

```bash
osascript -e 'quit app "Save the Ocean"' 2>/dev/null || true
# In Finder: move ~/Desktop/Save the Ocean.app to Trash, then:
ditto "dist/Save the Ocean.app" ~/Desktop/"Save the Ocean.app"
```

Double-click **Save the Ocean** to play. Your save file is stored in  
`~/Library/Application Support/Save the Ocean/` (not inside the app).

> **First launch:** macOS may say the app is from an unidentified developer.  
> Right-click the app → **Open** → **Open** once, and it will work normally after that.

## Installation (run from source)

You need **Python 3.10 or newer** installed on your computer.

1. Open a terminal in this folder (`turtle game`).

2. Install the game dependency:

```bash
pip install -r requirements.txt
```

3. Generate and install PNG art:

```bash
python3 scripts/generate_source_assets.py
python3 scripts/install_user_assets.py
```

4. Run the game:

```bash
python main.py
```

## Assets

All sprites and backgrounds are **PNG files** processed from `assets/source/`:

```
assets/
  source/          # Raw PNGs (generate or replace)
  turtle/            # Player + baby turtle
  obstacles/         # Plastic + shark
  friends/           # Dolphin, clownfish, ray, friendly turtle
  collectibles/      # Bubble, treasure chest, seaweed power-up
  backgrounds/       # Reef + 4 ocean zones
  effects/           # Ripple sheet
```

Three **coral reef panoramas** (`ocean_base`, `ocean_coral_2`, `ocean_coral_3`) scroll horizontally and crossfade as you swim — on the menu every ~7 seconds, and in the Coral Reef zone every ~180 m.

```bash
python3 scripts/build_special_sources.py   # baby turtle, friends, treasure, seaweed (HQ)
python3 scripts/generate_source_assets.py  # zone backgrounds only
python3 scripts/install_user_assets.py      # scales, removes backgrounds, installs
```

High-quality character art lives in `assets/source/_generated/` and is used automatically by `build_special_sources.py`.

Replace any file in `assets/source/` with your own art, then re-run the install script.

## Tips for Parents & Teachers

- The game uses bright colors, simple controls, and positive messages about ocean conservation.
- Collisions are slightly forgiving to help younger players.
- Sound effects are off by default — press **M** to turn them on.
- No internet connection required after setup.

## Project Structure

```
turtle game/
├── main.py              # Start here
├── requirements.txt
├── README.md
├── scripts/
│   ├── build_special_sources.py
│   ├── generate_source_assets.py
│   ├── install_user_assets.py
│   ├── build_hd_assets.py       # bubble + ripple FX
│   └── build_mac_app.sh         # macOS desktop app builder
├── assets/
│   ├── source/          # raw PNG inputs
│   └── ...              # game-ready PNGs
└── game/
    ├── config.py        # Game settings
    ├── states.py        # Main game loop
    ├── entities/        # Turtle, obstacles, collectibles
    ├── world/           # Background, particles, assets, sprite FX
    ├── systems/         # Spawning, collisions, audio
    └── ui/              # HUD and menus
```

Enjoy saving the ocean!
