#!/usr/bin/env python3
"""Generate source PNGs in assets/source/ for the install pipeline."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "source"
W, H = 960, 540


def save(img: Image.Image, rel: str) -> None:
    path = SOURCE / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG")
    print(f"  source/{rel}")


def _gradient(w: int, h: int, top: tuple, mid: tuple, bottom: tuple) -> Image.Image:
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        if t < 0.45:
            u = t / 0.45
            c = tuple(int(top[i] + (mid[i] - top[i]) * u) for i in range(3))
        else:
            u = (t - 0.45) / 0.55
            c = tuple(int(mid[i] + (bottom[i] - mid[i]) * u) for i in range(3))
        d.line([(0, y), (w, y)], fill=c)
    return img


def _rays(img: Image.Image, alpha: int = 30) -> Image.Image:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for i in range(5):
        x = 60 + i * 180
        d.polygon([(x, 0), (x - 50, int(H * 0.5)), (x + 50, int(H * 0.5))], fill=(255, 255, 220, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def build_baby_turtle() -> None:
    img = Image.new("RGBA", (256, 256), (240, 240, 240, 255))
    d = ImageDraw.Draw(img)
    cx, cy = 128, 140
    d.ellipse((cx - 42, cy - 28, cx + 18, cy + 24), fill=(45, 155, 75), outline=(20, 80, 50), width=3)
    for ox, oy in ((0, -6), (-12, 6), (8, 8)):
        d.ellipse((cx + ox - 7, cy + oy - 5, cx + ox + 7, cy + oy + 5), fill=(95, 200, 120))
    d.ellipse((cx + 10, cy - 14, cx + 44, cy + 10), fill=(110, 210, 150), outline=(20, 80, 50), width=2)
    d.ellipse((cx + 24, cy - 6, cx + 36, cy + 4), fill=(255, 255, 255))
    d.ellipse((cx + 28, cy - 4, cx + 32, cy), fill=(25, 35, 45))
    d.arc((cx + 20, cy + 2, cx + 38, cy + 12), 200, 340, fill=(20, 80, 50), width=2)
    d.ellipse((cx - 50, cy - 30, cx - 34, cy - 14), outline=(255, 255, 255, 200), width=2)
    save(img, "turtle/baby_turtle.png")


def build_dolphin() -> None:
    img = Image.new("RGBA", (256, 256), (240, 240, 240, 255))
    d = ImageDraw.Draw(img)
    cx, cy = 128, 132
    d.ellipse((cx - 55, cy - 18, cx + 45, cy + 18), fill=(80, 170, 230), outline=(40, 100, 160), width=2)
    d.polygon([(cx + 40, cy), (cx + 62, cy - 16), (cx + 62, cy + 16)], fill=(80, 170, 230))
    d.ellipse((cx - 20, cy - 8, cx - 8, cy + 4), fill=(255, 255, 255))
    d.ellipse((cx - 16, cy - 4, cx - 12, cy), fill=(25, 35, 45))
    save(img, "friends/dolphin.png")


def build_clownfish() -> None:
    img = Image.new("RGBA", (256, 256), (240, 240, 240, 255))
    d = ImageDraw.Draw(img)
    cx, cy = 128, 132
    d.ellipse((cx - 36, cy - 16, cx + 36, cy + 16), fill=(255, 130, 60), outline=(180, 70, 20), width=2)
    for x in (cx - 14, cx + 8):
        d.rectangle((x - 4, cy - 14, x + 4, cy + 14), fill=(255, 255, 255))
    d.polygon([(cx + 34, cy), (cx + 48, cy - 8), (cx + 48, cy + 8)], fill=(255, 130, 60))
    save(img, "friends/clownfish.png")


def build_friendly_turtle() -> None:
    img = Image.new("RGBA", (256, 256), (240, 240, 240, 255))
    d = ImageDraw.Draw(img)
    cx, cy = 128, 136
    d.ellipse((cx - 38, cy - 22, cx + 22, cy + 20), fill=(95, 200, 120), outline=(20, 80, 50), width=2)
    d.ellipse((cx + 8, cy - 12, cx + 40, cy + 8), fill=(110, 210, 150))
    d.arc((cx + 16, cy + 2, cx + 34, cy + 12), 200, 320, fill=(20, 80, 50), width=2)
    d.ellipse((cx + 22, cy - 4, cx + 30, cy + 2), fill=(255, 255, 255))
    save(img, "friends/friendly_turtle.png")


def build_ray() -> None:
    img = Image.new("RGBA", (256, 256), (240, 240, 240, 255))
    d = ImageDraw.Draw(img)
    cx, cy = 128, 140
    d.ellipse((cx - 58, cy - 22, cx + 58, cy + 10), fill=(160, 180, 200), outline=(100, 120, 150), width=2)
    d.polygon([(cx, cy + 6), (cx - 8, cy + 34), (cx + 8, cy + 34)], fill=(140, 160, 190))
    d.ellipse((cx - 10, cy - 6, cx + 6, cy + 6), fill=(255, 255, 255))
    save(img, "friends/ray.png")


def build_treasure() -> None:
    img = Image.new("RGBA", (256, 256), (240, 240, 240, 255))
    d = ImageDraw.Draw(img)
    cx, cy = 128, 140
    glow = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((cx - 50, cy - 40, cx + 50, cy + 40), fill=(255, 220, 100, 60))
    img = Image.alpha_composite(img, glow)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((cx - 44, cy - 10, cx + 44, cy + 36), radius=6, fill=(120, 85, 45), outline=(80, 55, 25), width=2)
    d.rounded_rectangle((cx - 44, cy - 28, cx + 44, cy - 6), radius=6, fill=(255, 180, 60), outline=(180, 120, 30), width=2)
    d.rectangle((cx - 6, cy - 20, cx + 6, cy + 10), fill=(255, 230, 120))
    save(img, "collectibles/treasure_chest.png")


def build_seaweed() -> None:
    img = Image.new("RGBA", (256, 256), (240, 240, 240, 255))
    glow = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((68, 68, 188, 188), fill=(100, 255, 160, 70))
    img = Image.alpha_composite(img, glow)
    d = ImageDraw.Draw(img)
    cx, cy = 128, 150
    for ox in (-18, 0, 18):
        d.polygon([(cx + ox, cy + 30), (cx + ox - 12, cy - 30), (cx + ox + 12, cy - 30)], fill=(30, 160, 90))
        d.polygon([(cx + ox, cy + 30), (cx + ox - 12, cy - 30), (cx + ox + 12, cy - 30)], outline=(20, 110, 65), width=2)
    for i in range(4):
        sx, sy = cx - 20 + i * 14, cy - 40
        gd2 = ImageDraw.Draw(img)
        gd2.ellipse((sx, sy, sx + 6, sy + 6), fill=(255, 255, 200, 220))
    save(img, "collectibles/seaweed_powerup.png")


def _zone_base(top, mid, bot, floor_fn) -> None:
    img = _gradient(W, H, top, mid, bot)
    img = _rays(img, 25)
    floor_fn(ImageDraw.Draw(img))
    return img


def build_zone_backgrounds() -> None:
    """Photo-derived zone backgrounds — same quality as the user's reef PNG."""
    base_path = SOURCE / "backgrounds/ocean_base.png"
    para_path = SOURCE / "backgrounds/ocean_parallax.png"
    if not base_path.exists():
        return
    from PIL import ImageEnhance

    base = Image.open(base_path).convert("RGB")
    para = Image.open(para_path).convert("RGB") if para_path.exists() else base

    def _save_zone(
        name: str,
        src: Image.Image,
        *,
        color: float = 1.0,
        bright: float = 1.0,
        contrast: float = 1.0,
        tint: tuple[int, int, int, int] | None = None,
    ) -> None:
        img = ImageEnhance.Color(src).enhance(color)
        img = ImageEnhance.Brightness(img).enhance(bright)
        img = ImageEnhance.Contrast(img).enhance(contrast)
        if tint:
            overlay = Image.new("RGBA", img.size, tint)
            img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        save(img, f"backgrounds/{name}")

    # Kelp forest — greener, slightly darker reef photo
    _save_zone(
        "zone_kelp.png", para,
        color=0.82, bright=0.88, contrast=1.05,
        tint=(15, 70, 35, 75),
    )
    # Deep ocean — cooler and darker
    _save_zone(
        "zone_deep.png", base,
        color=0.72, bright=0.72, contrast=1.08,
        tint=(8, 35, 90, 90),
    )
    # Tropical lagoon — brighter warm reef
    _save_zone(
        "zone_lagoon.png", base,
        color=1.14, bright=1.12, contrast=1.02,
        tint=(255, 200, 80, 35),
    )
    # Night ocean — dark blue-violet reef
    _save_zone(
        "zone_night.png", para,
        color=0.55, bright=0.58, contrast=1.1,
        tint=(25, 15, 70, 110),
    )


def build_coral_variants() -> None:
    base_path = SOURCE / "backgrounds/ocean_base.png"
    if not base_path.exists():
        return
    from PIL import ImageEnhance

    base = Image.open(base_path).convert("RGB")
    para_path = SOURCE / "backgrounds/ocean_parallax.png"

    img2 = ImageEnhance.Color(base).enhance(1.12)
    img2 = ImageEnhance.Brightness(img2).enhance(1.06)
    img2 = ImageEnhance.Contrast(img2).enhance(1.05)
    overlay = Image.new("RGBA", img2.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for i in range(10):
        x = 40 + i * 95
        h = 55 + (i % 3) * 18
        d.ellipse((x, H - h - 40, x + 65, H - 35), fill=(255, 105, 125, 120))
        d.ellipse((x + 20, H - h - 70, x + 45, H - h - 45), fill=(255, 150, 160, 90))
    img2 = Image.alpha_composite(img2.convert("RGBA"), overlay).convert("RGB")
    save(img2, "backgrounds/ocean_coral_2.png")

    if para_path.exists():
        img3 = Image.open(para_path).convert("RGB")
        img3 = ImageEnhance.Color(img3).enhance(1.08)
    else:
        img3 = ImageEnhance.Color(base).enhance(0.92)
        img3 = ImageEnhance.Brightness(img3).enhance(0.95)
    overlay3 = Image.new("RGBA", img3.size, (0, 0, 0, 0))
    d3 = ImageDraw.Draw(overlay3)
    for i in range(8):
        x = 60 + i * 115
        d3.ellipse((x, H - 100, x + 55, H - 45), fill=(255, 180, 90, 100))
        d3.rectangle((x + 18, H - 130, x + 28, H - 95), fill=(30, 150, 85, 130))
    img3 = Image.alpha_composite(img3.convert("RGBA"), overlay3).convert("RGB")
    save(img3, "backgrounds/ocean_coral_3.png")


def main() -> None:
    print("Generating source PNGs (zones only)...")
    build_zone_backgrounds()
    build_coral_variants()
    print("Done.")
    print("Run scripts/build_special_sources.py for character sprites.")


if __name__ == "__main__":
    main()
