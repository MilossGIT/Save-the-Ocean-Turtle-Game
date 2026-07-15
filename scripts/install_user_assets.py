#!/usr/bin/env python3
"""Install PNG art from assets/source/ into assets/ at game-ready sizes."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SOURCE = ROOT / "assets" / "source"

SCREEN_W, SCREEN_H = 960, 540
SCROLL_W = 1440
TURTLE_TARGET_W = 150
OBSTACLE_MAX = 105
SHARK_TARGET_W = 155
BABY_TURTLE_W = 85
FRIENDLY_MAX = 105
SPECIAL_COLLECTIBLE_MAX = 110
BG_TOLERANCE = 34
SPECIAL_BG_TOLERANCE = 38
PLASTIC_BG_TOLERANCE = 28

ZONE_BACKGROUNDS = [
    "backgrounds/ocean_base.png",
    "backgrounds/zone_kelp.png",
    "backgrounds/zone_deep.png",
    "backgrounds/zone_lagoon.png",
    "backgrounds/zone_night.png",
]


def save(img: Image.Image, rel: str) -> None:
    path = ASSETS / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG")
    print(f"  {rel} ({img.size[0]}x{img.size[1]})")


def resolve_source(*candidates: str) -> Path:
    for name in candidates:
        p = SOURCE / name
        if p.exists():
            return p
    return SOURCE / candidates[0]


def _is_studio_bg_pixel(r: int, g: int, b: int, tolerance: int) -> bool:
    """Gray/white studio backdrop — avoids pure-white character details (e.g. clownfish stripes)."""
    spread = max(r, g, b) - min(r, g, b)
    brightness = (r + g + b) // 3
    return spread <= tolerance + 6 and 205 <= brightness <= 248


def _is_fringe_pixel(r: int, g: int, b: int, tolerance: int) -> bool:
    """Gray halo pixels at edges — never eats pure-white sprite details."""
    spread = max(r, g, b) - min(r, g, b)
    brightness = (r + g + b) // 3
    return spread <= tolerance + 4 and 200 <= brightness <= 242


def _bg_distance(r: int, g: int, b: int, bg: tuple[int, int, int]) -> int:
    return max(abs(r - bg[0]), abs(g - bg[1]), abs(b - bg[2]))


def remove_background(img: Image.Image, tolerance: int = BG_TOLERANCE) -> Image.Image:
    """Corner flood-fill only — safe for white objects like plastic bags."""
    img = img.convert("RGBA")
    w, h = img.size
    px = img.load()
    corners = [px[0, 0][:3], px[w - 1, 0][:3], px[0, h - 1][:3], px[w - 1, h - 1][:3]]
    bg = tuple(sum(c[i] for c in corners) // 4 for i in range(3))
    from collections import deque

    seen = bytearray(w * h)
    q: deque[tuple[int, int]] = deque()
    for x in range(w):
        for y in (0, h - 1):
            q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            q.append((x, y))
    while q:
        x, y = q.popleft()
        idx = y * w + x
        if seen[idx]:
            continue
        seen[idx] = 1
        r, g, b, a = px[x, y]
        if a == 0 or _bg_distance(r, g, b, bg) > tolerance:
            continue
        px[x, y] = (r, g, b, 0)
        if x > 0:
            q.append((x - 1, y))
        if x + 1 < w:
            q.append((x + 1, y))
        if y > 0:
            q.append((x, y - 1))
        if y + 1 < h:
            q.append((x, y + 1))
    _defringe(img, tolerance // 2, fringe_only=True)
    return img


def remove_neutral_background(img: Image.Image, tolerance: int = SPECIAL_BG_TOLERANCE) -> Image.Image:
    """Remove studio backdrops from AI sprites — preserves pure-white character details."""
    img = remove_background(img, tolerance)
    img = img.convert("RGBA")
    w, h = img.size
    px = img.load()
    from collections import deque

    seen = bytearray(w * h)
    q: deque[tuple[int, int]] = deque()
    for x in range(w):
        for y in (0, h - 1):
            q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            q.append((x, y))
    while q:
        x, y = q.popleft()
        idx = y * w + x
        if seen[idx]:
            continue
        seen[idx] = 1
        r, g, b, a = px[x, y]
        if a == 0:
            continue
        if not _is_studio_bg_pixel(r, g, b, tolerance):
            continue
        px[x, y] = (r, g, b, 0)
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < w and 0 <= ny < h:
                q.append((nx, ny))
    _defringe(img, tolerance, fringe_only=True)
    return img


def _defringe(img: Image.Image, tolerance: int, *, fringe_only: bool = False) -> None:
    w, h = img.size
    px = img.load()
    to_fix: list[tuple[int, int]] = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            touches_clear = any(
                0 <= nx < w and 0 <= ny < h and px[nx, ny][3] == 0
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
            )
            if not touches_clear:
                continue
            if fringe_only:
                if _is_fringe_pixel(r, g, b, tolerance):
                    to_fix.append((x, y))
            elif _is_studio_bg_pixel(r, g, b, tolerance):
                to_fix.append((x, y))
    for x, y in to_fix:
        r, g, b, a = px[x, y]
        px[x, y] = (r, g, b, 0)


def trim_alpha(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img


def scale_to_width(img: Image.Image, width: int) -> Image.Image:
    w, h = img.size
    if w == 0:
        return img
    return img.resize((width, max(1, int(h * width / w))), Image.Resampling.LANCZOS)


def scale_to_max(img: Image.Image, max_dim: int) -> Image.Image:
    w, h = img.size
    scale = max_dim / max(w, h)
    if scale >= 1:
        return img
    return img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.LANCZOS)


def flip_h(img: Image.Image) -> Image.Image:
    return img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)


def fit_background_wide(
    img: Image.Image,
    screen_w: int,
    scroll_w: int,
    height: int,
    crop_bias: float = 0.0,
) -> Image.Image:
    """Crop a wide scrollable strip from a photo for horizontal panning."""
    src_w, src_h = img.size
    scale = max(scroll_w / src_w, height / src_h)
    new_w, new_h = int(src_w * scale), int(src_h * scale)
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    max_left = max(0, new_w - scroll_w)
    left = int((max_left / 2) * (1.0 + crop_bias))
    left = max(0, min(left, max_left))
    top = max(0, (new_h - height) // 2)
    return img.crop((left, top, left + scroll_w, top + height))


def fit_background(img: Image.Image, width: int, height: int) -> Image.Image:
    src_w, src_h = img.size
    scale = max(width / src_w, height / src_h)
    new_w, new_h = int(src_w * scale), int(src_h * scale)
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - width) // 2
    top = (new_h - height) // 2
    return img.crop((left, top, left + width, top + height))


def fit_parallax(img: Image.Image, height: int) -> Image.Image:
    src_w, src_h = img.size
    return img.resize((max(1, int(src_w * height / src_h)), height), Image.Resampling.LANCZOS)


def _load_sprite(path: Path, width: int | None = None, max_dim: int | None = None, flip: bool = False) -> Image.Image:
    img = trim_alpha(remove_background(Image.open(path)))
    if flip:
        img = flip_h(img)
    if width:
        img = scale_to_width(img, width)
    elif max_dim:
        img = scale_to_max(img, max_dim)
    return img


def _load_plastic_sprite(path: Path) -> Image.Image:
    """Conservative bg removal — keeps white plastic visible."""
    img = trim_alpha(remove_background(Image.open(path), PLASTIC_BG_TOLERANCE))
    return scale_to_max(img, OBSTACLE_MAX)


def remove_gray_background(img: Image.Image, tolerance: int = 42) -> Image.Image:
    """Corner flood only — never defringes; safe for white stripes on clownfish."""
    img = img.convert("RGBA")
    w, h = img.size
    px = img.load()
    corners = [px[0, 0][:3], px[w - 1, 0][:3], px[0, h - 1][:3], px[w - 1, h - 1][:3]]
    bg = tuple(sum(c[i] for c in corners) // 4 for i in range(3))
    from collections import deque

    seen = bytearray(w * h)
    q: deque[tuple[int, int]] = deque()
    for x in range(w):
        for y in (0, h - 1):
            q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            q.append((x, y))
    while q:
        x, y = q.popleft()
        idx = y * w + x
        if seen[idx]:
            continue
        seen[idx] = 1
        r, g, b, a = px[x, y]
        if a == 0 or _bg_distance(r, g, b, bg) > tolerance:
            continue
        px[x, y] = (r, g, b, 0)
        if x > 0:
            q.append((x - 1, y))
        if x + 1 < w:
            q.append((x + 1, y))
        if y > 0:
            q.append((x, y - 1))
        if y + 1 < h:
            q.append((x, y + 1))
    return img


def _load_clownfish_sprite(path: Path) -> Image.Image:
    """Load HQ clownfish — gray bg removal only, keeps white stripes."""
    hq = SOURCE / "_generated" / "clownfish.png"
    src = hq if hq.exists() else path
    img = trim_alpha(remove_gray_background(Image.open(src), tolerance=44))
    return scale_to_max(flip_h(img), FRIENDLY_MAX)


def _load_special_sprite(path: Path, width: int | None = None, max_dim: int | None = None, flip: bool = False) -> Image.Image:
    """Load AI-generated sprites with aggressive white/gray background removal."""
    img = trim_alpha(remove_neutral_background(Image.open(path)))
    if flip:
        img = flip_h(img)
    if width:
        img = scale_to_width(img, width)
    elif max_dim:
        img = scale_to_max(img, max_dim)
    return img


def ensure_source_assets() -> None:
    gen = ROOT / "scripts" / "generate_source_assets.py"
    specials = ROOT / "scripts" / "build_special_sources.py"
    need = SOURCE / "turtle" / "baby_turtle.png"
    if specials.exists():
        print("Running build_special_sources.py...")
        subprocess.check_call([sys.executable, str(specials)], cwd=str(ROOT))
    elif not need.exists() and gen.exists():
        print("Running generate_source_assets.py...")
        subprocess.check_call([sys.executable, str(gen)], cwd=str(ROOT))


def install_turtle_frames() -> None:
    swim: list[Image.Image] = []
    names = ["turtle/turtle_swim_0.png", "turtle/turtle_swim_1.png", "turtle/turtle_swim_2.png"]
    legacy = [
        "image-104abda9-a99b-4bd0-8d2a-99e7cad05d29.png",
        "image-b9fde11d-ff70-437b-b6e4-85287894a34d.png",
        "image-e4c1aa19-3426-4e85-814d-4551a27d8d0e.png",
    ]
    for i, (rel, leg) in enumerate(zip(names, legacy)):
        src = resolve_source(rel, leg)
        if not src.exists():
            src = ASSETS / f"turtle/turtle_swim_{i}.png"
        img = _load_sprite(src, width=TURTLE_TARGET_W, flip=True)
        swim.append(img)
        save(img, f"turtle/turtle_swim_{i}.png")
    save(swim[0], "turtle/turtle_idle.png")
    for i in range(3, 8):
        save(swim[i % 3], f"turtle/turtle_swim_{i}.png")


def install_obstacles() -> None:
    mapping = {
        "obstacles/plastic_bag.png": ("obstacles/plastic_bag.png", "image-db144e04-aed5-4a5d-a707-f512df5f8fca.png"),
        "obstacles/plastic_ring.png": ("obstacles/plastic_ring.png", "image-c7590db5-9e04-445b-a50f-2ab7de1875b7.png"),
        "obstacles/plastic_bottle.png": ("obstacles/plastic_bottle.png", "image-b2e22389-456c-4ce4-9d30-85e715c92d65.png"),
    }
    for dest, candidates in mapping.items():
        src = resolve_source(*candidates)
        save(_load_plastic_sprite(src), dest)


def install_shark() -> None:
    src = resolve_source("obstacles/shark.png", "shark_game_sprite.png")
    if not src.exists():
        src = ASSETS / "obstacles/shark_0.png"
    img = _load_sprite(src, width=SHARK_TARGET_W)
    for i in range(4):
        save(img, f"obstacles/shark_{i}.png")


def install_backgrounds() -> None:
    base_src = resolve_source("backgrounds/ocean_base.png", "image-574634f6-a166-47f1-bd06-dfa70b6a147e.png")
    base_img = Image.open(base_src).convert("RGB")
    save(fit_background_wide(base_img, SCREEN_W, SCROLL_W, SCREEN_H, crop_bias=0.0), "backgrounds/ocean_base.png")
    coral2_src = resolve_source("backgrounds/ocean_coral_2.png")
    if coral2_src.exists():
        save(
            fit_background_wide(Image.open(coral2_src).convert("RGB"), SCREEN_W, SCROLL_W, SCREEN_H, crop_bias=-0.2),
            "backgrounds/ocean_coral_2.png",
        )
    else:
        save(fit_background_wide(base_img, SCREEN_W, SCROLL_W, SCREEN_H, crop_bias=-0.35), "backgrounds/ocean_coral_2.png")
    coral3_src = resolve_source("backgrounds/ocean_coral_3.png")
    if coral3_src.exists():
        save(
            fit_background_wide(Image.open(coral3_src).convert("RGB"), SCREEN_W, SCROLL_W, SCREEN_H, crop_bias=0.25),
            "backgrounds/ocean_coral_3.png",
        )
    else:
        save(fit_background_wide(base_img, SCREEN_W, SCROLL_W, SCREEN_H, crop_bias=0.35), "backgrounds/ocean_coral_3.png")
    para_src = resolve_source("backgrounds/ocean_parallax.png", "image-33cfff6a-2b39-4ff1-b151-fb2a68e25da9.png")
    if para_src.exists():
        save(fit_parallax(Image.open(para_src).convert("RGB"), SCREEN_H), "backgrounds/ocean_parallax.png")


def install_zone_backgrounds() -> None:
    zone_files = [
        ("backgrounds/zone_kelp.png", "backgrounds/zone_kelp.png", -0.18),
        ("backgrounds/zone_deep.png", "backgrounds/zone_deep.png", 0.22),
        ("backgrounds/zone_lagoon.png", "backgrounds/zone_lagoon.png", -0.28),
        ("backgrounds/zone_night.png", "backgrounds/zone_night.png", 0.12),
    ]
    base_src = resolve_source("backgrounds/ocean_base.png", "image-574634f6-a166-47f1-bd06-dfa70b6a147e.png")
    base_img = Image.open(base_src).convert("RGB") if base_src.exists() else None
    for dest, src_rel, crop_bias in zone_files:
        src = SOURCE / src_rel
        if not src.exists() and base_img is not None:
            save(
                fit_background_wide(base_img, SCREEN_W, SCROLL_W, SCREEN_H, crop_bias=crop_bias),
                dest,
            )
            continue
        if not src.exists():
            continue
        save(
            fit_background_wide(Image.open(src).convert("RGB"), SCREEN_W, SCROLL_W, SCREEN_H, crop_bias=crop_bias),
            dest,
        )


def install_specials() -> None:
    baby = resolve_source("turtle/baby_turtle.png")
    if baby.exists():
        save(_load_special_sprite(baby, width=BABY_TURTLE_W, flip=True), "turtle/baby_turtle.png")
    friends = {
        "dolphin": ("friends/dolphin.png",),
        "clownfish": ("friends/clownfish.png",),
        "turtle": ("friends/friendly_turtle.png",),
        "ray": ("friends/ray.png",),
    }
    for kind, candidates in friends.items():
        src = resolve_source(*candidates)
        if not src.exists():
            continue
        if kind == "clownfish":
            save(_load_clownfish_sprite(src), f"friends/{kind}.png")
        else:
            save(_load_special_sprite(src, max_dim=FRIENDLY_MAX, flip=True), f"friends/{kind}.png")
    for rel, dest in [
        ("collectibles/treasure_chest.png", "collectibles/treasure_chest.png"),
        ("collectibles/seaweed_powerup.png", "collectibles/seaweed_powerup.png"),
    ]:
        src = resolve_source(rel)
        if src.exists():
            save(_load_special_sprite(src, max_dim=SPECIAL_COLLECTIBLE_MAX), dest)


def ensure_bubble_and_ripples() -> None:
    bubble = ASSETS / "collectibles/bubble.png"
    ripples = ASSETS / "effects/ripples_sheet.png"
    if bubble.exists() and ripples.exists():
        return
    build = ROOT / "scripts" / "build_hd_assets.py"
    if build.exists():
        subprocess.check_call([sys.executable, str(build)], cwd=str(ROOT))


def main() -> None:
    print("Installing assets from source...")
    ensure_source_assets()
    if not SOURCE.exists():
        raise SystemExit(f"No source folder at {SOURCE}")
    install_backgrounds()
    install_zone_backgrounds()
    install_obstacles()
    install_turtle_frames()
    install_shark()
    install_specials()
    ensure_bubble_and_ripples()
    print("Done — assets installed.")


if __name__ == "__main__":
    main()
