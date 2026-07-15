#!/usr/bin/env python3
"""Build high-quality special sprite sources from user turtle art + generated PNGs."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "source"
GENERATED = SOURCE / "_generated"
CURSOR_ASSETS = Path("/Users/minasesek/.cursor/projects/Users-minasesek-Downloads-turtle-game/assets")
TURTLE_SRC = SOURCE / "turtle" / "turtle_swim_0.png"
TURTLE_ALT = SOURCE / "turtle" / "turtle_swim_1.png"


def _bg_tools():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "_install_assets", ROOT / "scripts" / "install_user_assets.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.remove_neutral_background, mod.trim_alpha


def _prepare(img: Image.Image, canvas: int = 512, margin: float = 0.08) -> Image.Image:
    remove_bg, trim = _bg_tools()
    cleaned = trim(remove_bg(img.convert("RGBA")))
    return _fit_on_canvas(cleaned, canvas=canvas, margin=margin)


def _find_hq(name: str) -> Path | None:
    """Prefer previously generated high-quality PNGs over procedural fallbacks."""
    for folder in (GENERATED, CURSOR_ASSETS, SOURCE):
        p = folder / name
        if p.exists() and p.stat().st_size > 50_000:
            return p
    return None


def save(img: Image.Image, rel: str) -> None:
    path = SOURCE / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG")
    print(f"  source/{rel} ({img.size[0]}x{img.size[1]})")


def _fit_on_canvas(img: Image.Image, canvas: int = 512, margin: float = 0.08) -> Image.Image:
    """Center sprite on transparent canvas — background removed during install."""
    img = img.convert("RGBA")
    w, h = img.size
    inner = int(canvas * (1.0 - margin * 2))
    scale = min(inner / w, inner / h)
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    out.paste(resized, ((canvas - nw) // 2, (canvas - nh) // 2), resized)
    return out


def _derive_baby_turtle() -> None:
    hq = _find_hq("baby_turtle.png")
    if hq:
        save(_prepare(Image.open(hq)), "turtle/baby_turtle.png")
        return
    src = TURTLE_SRC if TURTLE_SRC.exists() else ROOT / "assets" / "turtle" / "turtle_swim_0.png"
    if not src.exists():
        print("  skip baby turtle — no turtle source")
        return
    img = Image.open(src).convert("RGBA")
    # Baby = ~58% scale, slightly brighter/cuter
    w, h = img.size
    nw, nh = int(w * 0.58), int(h * 0.58)
    baby = img.resize((nw, nh), Image.Resampling.LANCZOS)
    baby = ImageEnhance.Color(baby).enhance(1.06)
    baby = ImageEnhance.Brightness(baby).enhance(1.04)
    out = _fit_on_canvas(baby, canvas=512, margin=0.12)
    save(out, "turtle/baby_turtle.png")


def _derive_friendly_turtle() -> None:
    hq = _find_hq("friendly_turtle.png")
    if hq:
        save(_prepare(Image.open(hq)), "friends/friendly_turtle.png")
        return
    for candidate in (TURTLE_ALT, TURTLE_SRC, ROOT / "assets" / "turtle" / "turtle_swim_2.png"):
        if candidate.exists():
            src = candidate
            break
    else:
        print("  skip friendly turtle — no turtle source")
        return
    img = Image.open(src).convert("RGBA")
    img = ImageEnhance.Color(img).enhance(1.02)
    out = _fit_on_canvas(img, canvas=512, margin=0.06)
    save(out, "friends/friendly_turtle.png")


def _import_generated(name: str, dest: str, *, alt_names: tuple[str, ...] = ()) -> None:
    for candidate in (name, *alt_names):
        hq = _find_hq(candidate)
        if hq:
            save(_prepare(Image.open(hq)), dest)
            return
    for folder in (CURSOR_ASSETS, ROOT / "assets"):
        src = folder / name
        if src.exists():
            save(_prepare(Image.open(src)), dest)
            return
    print(f"  skip {dest} — {name} not found")


def _build_clownfish() -> None:
    """Detailed clownfish — best-effort match to 3D cartoon style without AI."""
    size = 1024
    img = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    from PIL import ImageDraw

    cx, cy = 512, 520
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # Body base with highlight
    d.ellipse((cx - 250, cy - 95, cx + 250, cy + 95), fill=(230, 95, 30))
    d.ellipse((cx - 240, cy - 88, cx + 80, cy + 35), fill=(255, 135, 55))
    d.ellipse((cx - 200, cy - 70, cx - 40, cy + 10), fill=(255, 170, 90, 120))

    # White stripes
    for sx, sw in ((cx - 105, 52), (cx + 35, 46)):
        d.rounded_rectangle((sx - sw // 2, cy - 88, sx + sw // 2, cy + 88), radius=8, fill=(255, 255, 255))
        d.rounded_rectangle((sx - sw // 2 + 4, cy - 82, sx + sw // 2 - 4, cy + 82), radius=6, fill=(248, 248, 248))

    # Tail
    d.polygon([(cx + 235, cy), (cx + 330, cy - 65), (cx + 330, cy + 65)], fill=(230, 95, 30))
    d.polygon([(cx + 245, cy), (cx + 310, cy - 45), (cx + 310, cy + 45)], fill=(255, 130, 50))

    # Fins
    d.ellipse((cx - 40, cy + 55, cx + 60, cy + 110), fill=(255, 120, 45))
    d.ellipse((cx - 120, cy - 115, cx - 60, cy - 55), fill=(255, 120, 45))

    # Eye
    d.ellipse((cx - 185, cy - 38, cx - 115, cy + 32), fill=(255, 255, 255))
    d.ellipse((cx - 170, cy - 22, cx - 130, cy + 18), fill=(35, 65, 110))
    d.ellipse((cx - 162, cy - 14, cx - 148, cy), fill=(255, 255, 255))

    # Smile
    d.arc((cx - 210, cy + 5, cx - 130, cy + 45), 20, 160, fill=(180, 60, 20), width=5)

    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.6))
    img = Image.alpha_composite(img, layer)
    save(img, "friends/clownfish.png")


def _prepare_clownfish(path: Path) -> Image.Image:
    remove_gray, trim = _bg_tools()[0], _bg_tools()[1]
    # Import remove_gray_background from install script
    import importlib.util
    spec = importlib.util.spec_from_file_location("_inst", ROOT / "scripts" / "install_user_assets.py")
    inst = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inst)
    cleaned = inst.trim_alpha(inst.remove_gray_background(Image.open(path).convert("RGBA"), 44))
    return _fit_on_canvas(cleaned, canvas=512, margin=0.06)


def main() -> None:
    print("Building high-quality special sprite sources...")
    _derive_baby_turtle()
    _derive_friendly_turtle()
    _import_generated("dolphin_source.png", "friends/dolphin.png", alt_names=("dolphin.png",))
    _import_generated("ray_source.png", "friends/ray.png", alt_names=("ray.png",))
    _import_generated("treasure_source.png", "collectibles/treasure_chest.png", alt_names=("treasure_chest.png",))
    _import_generated("seaweed_source.png", "collectibles/seaweed_powerup.png", alt_names=("seaweed_powerup.png",))
    hq_fish = _find_hq("clownfish.png")
    if hq_fish:
        save(_prepare_clownfish(hq_fish), "friends/clownfish.png")
    else:
        _build_clownfish()
    print("Done.")


if __name__ == "__main__":
    main()
