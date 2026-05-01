
---

### 4. `build_appimage.sh`

```bash
#!/bin/bash
set -e
echo "Building GenosHotkey AppImage..."

pip install pyinstaller -r requirements.txt

pyinstaller --onefile --windowed \
    --name GenosHotkey \
    --add-data "genos_icon.png:." \
    --collect-all customtkinter \
    --hidden-import=pynput \
    genos_hotkey.py

echo "✅ Build complete! ./dist/GenosHotkey"
chmod +x dist/GenosHotkey
