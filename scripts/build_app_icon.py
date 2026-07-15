#!/usr/bin/env python3
"""Build a bold, readable macOS app icon from the turtle sprite."""

from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SRC = ASSETS / "turtle" / "turtle_swim_0.png"
OUT_PNG = ASSETS / "app_icon.png"
OUT_ICNS = ASSETS / "app_icon.icns"


def _radial_ocean(size: int) -> Image.Image:
    """Bright centre + deep edges — reads well on light and dark desktops."""
    img = Image.new("RGBA", (size, size))
    px = img.load()
    cx = cy = size / 2
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - cx, y - cy) / (size * 0.72)
            d = min(1.0, d)
            # centre: bright aqua, edge: rich ocean blue
            r = int(20 + (130 - 20) * (1 - d))
            g = int(175 + (230 - 175) * (1 - d))
            b = int(255 + (170 - 255) * (1 - d))
            px[x, y] = (r, g, b, 255)
    return img


def _draw_bubbles(draw: ImageDraw.ImageDraw, size: int) -> None:
    specs = [
        (size * 0.18, size * 0.22, size * 0.07),
        (size * 0.82, size * 0.28, size * 0.05),
        (size * 0.12, size * 0.72, size * 0.045),
        (size * 0.88, size * 0.68, size * 0.055),
        (size * 0.72, size * 0.84, size * 0.04),
    ]
    for bx, by, br in specs:
        r = int(br)
        draw.ellipse((bx - r, by - r, bx + r, by + r), fill=(255, 255, 255, 70))
        hr = max(2, r // 3)
        draw.ellipse((bx - r // 2, by - r // 2, bx - r // 2 + hr, by - r // 2 + hr), fill=(255, 255, 255, 150))


def _soft_glow(size: int) -> Image.Image:
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    pad = int(size * 0.08)
    d.ellipse((pad, pad, size - pad, size - pad), fill=(255, 255, 255, 55))
    return glow.filter(ImageFilter.GaussianBlur(radius=size * 0.04))


def _outline_sprite(sprite: Image.Image, width: int = 6) -> Image.Image:
    """Smooth white rim — stays crisp when macOS scales to 32×32."""
    pad = width + 4
    w, h = sprite.size
    padded = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    padded.paste(sprite, (pad, pad), sprite)
    alpha = padded.split()[3]
    dilated = alpha
    for _ in range(width):
        dilated = dilated.filter(ImageFilter.MaxFilter(3))
    rim = Image.new("RGBA", padded.size, (255, 255, 255, 255))
    rim.putalpha(dilated)
    out = Image.alpha_composite(Image.new("RGBA", padded.size, (0, 0, 0, 0)), rim)
    out.paste(padded, (0, 0), padded)
    return out


def build_icon_png(size: int = 1024) -> Image.Image:
    if not SRC.exists():
        raise SystemExit(f"Missing turtle sprite: {SRC}")

    canvas = _radial_ocean(size)
    canvas = Image.alpha_composite(canvas, _soft_glow(size))

    bubble_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    _draw_bubbles(ImageDraw.Draw(bubble_layer), size)
    canvas = Image.alpha_composite(canvas, bubble_layer)

    turtle = Image.open(SRC).convert("RGBA")
    # Flip to face right (more friendly for dock icon)
    turtle = turtle.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    turtle = ImageEnhance.Color(turtle).enhance(1.12)
    turtle = ImageEnhance.Contrast(turtle).enhance(1.08)
    turtle = ImageEnhance.Brightness(turtle).enhance(1.05)

    outline_w = max(3, size // 180)
    turtle = _outline_sprite(turtle, outline_w)

    # Fill ~96% of icon width — big and readable on the Dock
    target_w = int(size * 0.96)
    scale = target_w / turtle.width
    target_h = int(turtle.height * scale)
    turtle = turtle.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # Slight upward bias — turtle reads better in squircle crop
    x = (size - target_w) // 2
    y = int(size * 0.46) - target_h // 2
    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse(
        (x + target_w * 0.15, y + target_h * 0.88, x + target_w * 0.85, y + target_h * 1.02),
        fill=(0, 40, 80, 90),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=size * 0.015))
    canvas = Image.alpha_composite(canvas, shadow)
    canvas.paste(turtle, (x, y), turtle)

    # Subtle top shine (macOS-style gloss)
    gloss = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gloss)
    gd.ellipse((int(size * 0.05), int(size * 0.02), int(size * 0.95), int(size * 0.55)), fill=(255, 255, 255, 35))
    canvas = Image.alpha_composite(canvas, gloss)
    return canvas


def build_icns(png: Path, icns: Path) -> None:
    iconset = ASSETS / "app_icon.iconset"
    iconset.mkdir(exist_ok=True)
    for f in iconset.glob("*.png"):
        f.unlink()
    for dim in 16, 32, 64, 128, 256, 512:
        out = iconset / f"icon_{dim}x{dim}.png"
        subprocess.run(
            ["sips", "-z", str(dim), str(dim), str(png), "--out", str(out)],
            check=True,
            capture_output=True,
        )
        out2 = iconset / f"icon_{dim}x{dim}@2x.png"
        subprocess.run(
            ["sips", "-z", str(dim * 2), str(dim * 2), str(png), "--out", str(out2)],
            check=True,
            capture_output=True,
        )
    subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(icns)], check=True)
    for f in iconset.glob("*.png"):
        f.unlink()
    iconset.rmdir()


def main() -> None:
    print("Building app icon...")
    icon = build_icon_png(1024)
    icon.save(OUT_PNG, "PNG")
    print(f"  {OUT_PNG.relative_to(ROOT)} ({icon.size[0]}x{icon.size[1]})")
    build_icns(OUT_PNG, OUT_ICNS)
    print(f"  {OUT_ICNS.relative_to(ROOT)}")
    print("Done.")


if __name__ == "__main__":
    main()
