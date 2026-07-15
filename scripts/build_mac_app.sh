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
python3 scripts/build_app_icon.py
ICON_ICNS="$ROOT/assets/app_icon.icns"

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
