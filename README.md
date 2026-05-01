# GenosHotkey v1.0.0.0

**Advanced open-source auto clicker and macro tool for Linux.**

<img width="512" height="512" alt="G E N O S" src="https://github.com/user-attachments/assets/9909f658-daed-46df-b4d6-730c7faa1676" />

## Features
- Beautiful modern dark UI
- Global customizable hotkey (default F6)
- Precise delay control (ms → days) with live CPS display
- Advanced macro recorder (mouse + keyboard + chords)
- Key hold/release support
- Fixed position clicking
- Works on X11 and Wayland

## Quick Start

```bash
git clone https://github.com/YOURUSERNAME/GenosHotkey.git
cd GenosHotkey
pip install -r requirements.txt
python genos_hotkey.py
Building AppImage (for easy distribution)
Bashchmod +x build_appimage.sh
./build_appimage.sh
```
The AppImage will be created in the dist/ folder.

Requirements

Python 3.8+
ydotool (recommended for Wayland)

Contributing
Feel free to open issues or pull requests!
