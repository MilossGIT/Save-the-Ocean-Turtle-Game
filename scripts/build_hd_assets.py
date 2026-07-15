#!/usr/bin/env python3
"""Build bubble and ripple effect PNGs when missing."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def save(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG")
    print(f"  {path.relative_to(ROOT)}")


def build_bubble() -> None:
    """Shiny translucent bubble — crisp highlight + soft iridescent rim."""
    size = 72
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cx, cy = size // 2, size // 2
    radius = 30

    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r, alpha in ((radius + 8, 35), (radius + 4, 55), (radius + 1, 75)):
        gd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(120, 220, 255, alpha))
    img = Image.alpha_composite(img, glow)

    d = ImageDraw.Draw(img)
    d.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=(140, 225, 255, 175))
    d.ellipse((cx - radius + 4, cy - radius + 2, cx + radius - 2, cy + radius - 2), fill=(185, 245, 255, 140))
    d.ellipse((cx - radius + 8, cy - radius + 10, cx + radius - 10, cy + radius - 4), fill=(210, 250, 255, 90))
    d.arc((cx - radius, cy - radius, cx + radius, cy + radius), 200, 340, fill=(255, 200, 255, 160), width=3)
    d.arc((cx - radius, cy - radius, cx + radius, cy + radius), 20, 120, fill=(180, 255, 240, 140), width=2)
    d.ellipse((cx - 16, cy - 20, cx + 2, cy - 6), fill=(255, 255, 255, 210))
    d.ellipse((cx - 12, cy - 17, cx - 4, cy - 11), fill=(255, 255, 255, 255))
    d.ellipse((cx + 8, cy + 6, cx + 16, cy + 14), fill=(255, 255, 255, 120))
    d.ellipse((cx + 10, cy - 2, cx + 14, cy + 2), fill=(255, 240, 180, 200))
    d.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(255, 255, 255, 200), width=2)
    save(img, ASSETS / "collectibles" / "bubble.png")


def build_ripples() -> None:
    sheet = Image.new("RGBA", (128, 32), (0, 0, 0, 0))
    for i in range(4):
        frame = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        d = ImageDraw.Draw(frame)
        r = 6 + i * 5
        d.ellipse((16 - r, 16 - r, 16 + r, 16 + r), outline=(200, 240, 255, 200 - i * 35), width=2)
        sheet.paste(frame, (i * 32, 0))
    save(sheet, ASSETS / "effects" / "ripples_sheet.png")


def main() -> None:
    print("Building bubble and ripple FX...")
    build_bubble()
    build_ripples()
    print("Done.")


if __name__ == "__main__":
    main()
