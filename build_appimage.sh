#!/bin/bash
set -e

APP_NAME="GenosHotkey"
VERSION="1.0.0.0"

echo "🚀 Building $APP_NAME v$VERSION..."

# Install dependencies
pip install pyinstaller -r requirements.txt --quiet

# Clean old builds
rm -rf build dist AppDir *.AppImage 2>/dev/null || true

# Build
pyinstaller --onefile --windowed \
    --name "$APP_NAME" \
    --add-data "genos_icon.png:." \
    --collect-all customtkinter \
    --hidden-import=pynput \
    genos_hotkey.py

echo "✅ Build complete! ./dist/$APP_NAME"
chmod +x "dist/$APP_NAME"

echo "AppImage ready! You can run: ./dist/GenosHotkey"
EOF
