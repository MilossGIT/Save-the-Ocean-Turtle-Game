# Asset Credits

## Primary art

| Asset | Location | Notes |
|-------|----------|-------|
| Player turtle swim frames | `assets/turtle/turtle_swim_*.png` | Cartoon sea turtle |
| Plastic obstacles | `assets/obstacles/plastic_*.png` | Photorealistic debris |
| Shark | `assets/obstacles/shark_*.png` | Game sprite |
| Reef background | `assets/backgrounds/ocean_base.png` | Reef photo |
| Baby turtle, friends, treasure, seaweed | `assets/turtle/`, `assets/friends/`, `assets/collectibles/` | Generated source art |
| Ocean zones | `assets/backgrounds/zone_*.png` | Zone backgrounds |

## Setup

Generate source PNGs (if missing), then install at game-ready sizes:

```bash
python3 scripts/build_special_sources.py
python3 scripts/generate_source_assets.py
python3 scripts/install_user_assets.py
```

Raw source files live in `assets/source/`. Processed game files live in `assets/`.

Bubble and ripple FX are built by `scripts/build_hd_assets.py` when missing.

Replace any file in `assets/source/` with your own art, then re-run the install script.
