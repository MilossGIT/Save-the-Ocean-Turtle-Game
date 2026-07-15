#!/bin/bash
# Build "Save the Ocean.app" — double-click to play, no terminal needed.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
APP_NAME="Save the Ocean"

echo "==> Checking assets..."
if [ ! -f "assets/turtle/turtle_swim_0.png" ]; then
  echo "Assets missing — running install script..."
  python3 scripts/install_user_assets.py
fi

echo "==> Installing build tools (one-time)..."
python3 -m pip install -q -r requirements-build.txt

echo "==> Creating app icon..."
ICON_PNG="$ROOT/assets/app_icon.png"
ICON_ICNS="$ROOT/assets/app_icon.icns"
if [ ! -f "$ICON_ICNS" ]; then
  python3 - <<'PY'
from pathlib import Path
from PIL import Image

root = Path(".")
src = root / "assets/turtle/turtle_swim_0.png"
out = root / "assets/app_icon.png"
img = Image.open(src).convert("RGBA")
size = 512
canvas = Image.new("RGBA", (size, size), (10, 120, 180, 255))
scale = min(size * 0.82 / img.width, size * 0.82 / img.height)
nw, nh = int(img.width * scale), int(img.height * scale)
img = img.resize((nw, nh), Image.Resampling.LANCZOS)
canvas.paste(img, ((size - nw) // 2, (size - nh) // 2), img)
canvas.save(out)
print(f"  wrote {out}")
PY
  ICONSET="$ROOT/assets/app_icon.iconset"
  rm -rf "$ICONSET"
  mkdir -p "$ICONSET"
  for dim in 16 32 64 128 256 512; do
    sips -z "$dim" "$dim" "$ICON_PNG" --out "$ICONSET/icon_${dim}x${dim}.png" >/dev/null
    d2=$((dim * 2))
    sips -z "$d2" "$d2" "$ICON_PNG" --out "$ICONSET/icon_${dim}x${dim}@2x.png" >/dev/null
  done
  iconutil -c icns "$ICONSET" -o "$ICON_ICNS"
  rm -rf "$ICONSET"
fi

echo "==> Building $APP_NAME.app (this may take a minute)..."
python3 -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "$APP_NAME" \
  --icon "$ICON_ICNS" \
  --add-data "assets:assets" \
  --hidden-import pygame.freetype \
  --osx-bundle-identifier "com.savetheocean.turtlegame" \
  main.py

echo ""
echo "Done! Your app is ready:"
echo "  $ROOT/dist/$APP_NAME.app"
echo ""
echo "To put it on your Desktop:"
echo "  cp -R \"$ROOT/dist/$APP_NAME.app\" ~/Desktop/"
echo ""
echo "Double-click the app to play — no terminal or server needed."
