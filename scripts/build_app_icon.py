#!/usr/bin/env python3
"""Minimal macOS app icon — large turtle, transparent outside (fits Dock squircle)."""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SRC = ASSETS / "turtle" / "turtle_swim_0.png"
OUT_PNG = ASSETS / "app_icon.png"
OUT_ICNS = ASSETS / "app_icon.icns"

# How much of the canvas width the turtle fills (inside Apple's safe zone).
TURTLE_WIDTH_RATIO = 0.84


def _key_out_black(sprite: Image.Image, threshold: int = 42) -> Image.Image:
    """Game sprites use a black matte — remove it so only the turtle remains."""
    out = sprite.convert("RGBA")
    px = out.load()
    w, h = out.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if r <= threshold and g <= threshold and b <= threshold:
                px[x, y] = (0, 0, 0, 0)
    return out


def _trim_to_alpha(sprite: Image.Image) -> Image.Image:
    bbox = sprite.split()[3].getbbox()
    if not bbox:
        return sprite
    return sprite.crop(bbox)


def _drop_shadow(size: int, turtle_w: int, turtle_h: int, x: int, y: int) -> Image.Image:
    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cx = x + turtle_w // 2
    cy = y + int(turtle_h * 0.92)
    rx = int(turtle_w * 0.34)
    ry = max(6, int(turtle_h * 0.05))
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(0, 0, 0, 70))
    return layer.filter(ImageFilter.GaussianBlur(radius=max(4, size // 180)))


def build_icon_png(size: int = 1024) -> Image.Image:
    if not SRC.exists():
        raise SystemExit(f"Missing turtle sprite: {SRC}")

    turtle = Image.open(SRC).convert("RGBA")
    turtle = turtle.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    turtle = _key_out_black(turtle)
    turtle = _trim_to_alpha(turtle)
    turtle = ImageEnhance.Color(turtle).enhance(1.08)
    turtle = ImageEnhance.Contrast(turtle).enhance(1.05)
    turtle = ImageEnhance.Sharpness(turtle).enhance(1.15)

    target_w = int(size * TURTLE_WIDTH_RATIO)
    scale = target_w / turtle.width
    target_h = int(turtle.height * scale)
    turtle = turtle.resize((target_w, target_h), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - target_w) // 2
    y = (size - target_h) // 2

    shadow = _drop_shadow(size, target_w, target_h, x, y)
    canvas = Image.alpha_composite(canvas, shadow)
    canvas.paste(turtle, (x, y), turtle)
    return canvas


def build_icns(png: Path, icns: Path) -> None:
    iconset = ASSETS / "app_icon.iconset"
    iconset.mkdir(exist_ok=True)
    for f in iconset.glob("*.png"):
        f.unlink()

    master = Image.open(png).convert("RGBA")
    sizes = {
        "icon_16x16.png": 16,
        "icon_16x16@2x.png": 32,
        "icon_32x32.png": 32,
        "icon_32x32@2x.png": 64,
        "icon_128x128.png": 128,
        "icon_128x128@2x.png": 256,
        "icon_256x256.png": 256,
        "icon_256x256@2x.png": 512,
        "icon_512x512.png": 512,
        "icon_512x512@2x.png": 1024,
    }
    for name, dim in sizes.items():
        resized = master.resize((dim, dim), Image.Resampling.LANCZOS)
        resized.save(iconset / name, "PNG")

    try:
        subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(icns)], check=True)
    finally:
        for f in iconset.glob("*.png"):
            f.unlink(missing_ok=True)
        iconset.rmdir()


def main() -> None:
    print("Building app icon (turtle only)...")
    icon = build_icon_png(1024)
    icon.save(OUT_PNG, "PNG")
    print(f"  {OUT_PNG.relative_to(ROOT)} ({icon.size[0]}x{icon.size[1]})")
    build_icns(OUT_PNG, OUT_ICNS)
    print(f"  {OUT_ICNS.relative_to(ROOT)}")
    print("Done.")


if __name__ == "__main__":
    main()
