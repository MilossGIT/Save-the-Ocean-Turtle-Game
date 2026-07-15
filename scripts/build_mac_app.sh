#!/bin/bash
# Build "Save the Ocean.app" — double-click to play, no terminal needed.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
APP_NAME="Save the Ocean"
APP_SRC="$ROOT/dist/$APP_NAME.app"
APP_DEST="$HOME/Desktop/$APP_NAME.app"
SKIP_INSTALL=0

for arg in "$@"; do
  case "$arg" in
    --skip-install) SKIP_INSTALL=1 ;;
    -h|--help)
      echo "Usage: bash scripts/build_mac_app.sh [--skip-install]"
      echo "  --skip-install  Build only; leave dist/$APP_NAME.app (no Desktop copy)"
      exit 0
      ;;
  esac
done

install_to_desktop() {
  if [ ! -d "$APP_SRC" ]; then
    echo "Error: built app not found at $APP_SRC"
    exit 1
  fi

  echo "==> Installing to Desktop..."

  # Release any running copy so files are not locked.
  osascript -e "quit app \"$APP_NAME\"" >/dev/null 2>&1 || true
  pkill -x "$APP_NAME" >/dev/null 2>&1 || true
  sleep 1

  if [ -d "$APP_DEST" ]; then
    echo "  Removing old Desktop app..."
    # Finder delete works when plain rm/cp hit macOS Desktop privacy locks.
    if ! osascript -e "tell application \"Finder\" to delete POSIX file \"$APP_DEST\"" >/dev/null 2>&1; then
      rm -rf "$APP_DEST" 2>/dev/null || true
    fi
    sleep 1
  fi

  if [ -d "$APP_DEST" ]; then
    echo ""
    echo "Could not replace the old Desktop app automatically."
    echo "Do this once, then run this script again:"
    echo "  1. Quit Save the Ocean (or Force Quit in Activity Monitor)"
    echo "  2. Drag ~/Desktop/Save the Ocean.app to the Trash in Finder"
    echo "  3. Empty Trash"
    echo ""
    echo "Fresh build is ready here:"
    echo "  $APP_SRC"
    return 1
  fi

  # ditto preserves app bundles + code signing better than cp -R.
  if ! ditto "$APP_SRC" "$APP_DEST"; then
    echo ""
    echo "Copy to Desktop failed. Build succeeded — use Finder:"
    echo "  Drag \"$APP_SRC\" to your Desktop"
    return 1
  fi

  echo "  Installed: $APP_DEST"
}

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

if [ "$SKIP_INSTALL" -eq 0 ]; then
  install_to_desktop || true
fi

echo ""
echo "Done! Your app is ready:"
echo "  $APP_SRC"
if [ -d "$APP_DEST" ]; then
  echo ""
  echo "Double-click Save the Ocean on your Desktop to play."
  echo "  $APP_DEST"
else
  echo ""
  echo "To put it on your Desktop, quit any running copy, trash the old app,"
  echo "then run: bash scripts/build_mac_app.sh"
  echo "Or drag the .app from dist/ to your Desktop in Finder."
fi
echo ""
echo "If macOS blocks the app the first time: right-click → Open → Open."
