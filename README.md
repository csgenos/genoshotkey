# GenosHotkey v1.0.0.0

**Advanced open-source auto clicker and macro tool for Linux.**

![Logo](genos_icon.png)

## Features
- Modern dark UI with red accents
- Global customizable hotkey (default F6)
- Precise delay control (ms → days) with live CPS display
- Advanced macro recorder (mouse + keyboard)
- Smart chord support (`ctrl+shift+t`)
- Key hold/release
- Fixed position clicking
- Powerful Scripting Engine (AHK-like)
  - Functions with parameters
  - While / For loops
  - If/Else conditions
  - Variables with math
  - Pixel search
  - Mouse drag
  - Random delays
  - Text typing

## Quick Start

```bash
git clone https://github.com/csgenos/GenosHotkey.git
cd GenosHotkey
pip install -r requirements.txt
python genos_hotkey.py
Building AppImage
Bashchmod +x build_appimage.sh
./build_appimage.sh
```

Support Development
If GenosHotkey has helped you, consider supporting the project! ❤️
<img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-FFDD00?style=for-the-badge&#x26;logo=buy-me-a-coffee&#x26;logoColor=black" alt="Buy Me a Coffee">
Crypto Donations:

Bitcoin (BTC): bc1qk02j3230x0ev6m7sar04wn3pynvnz23v4jqwsq
USDT (TRC20): 0xFc4e188281E5aE8cA1Dc6A9e822B9BC5d9c07E24

Requirements
Bashpip install -r requirements.txt
Optional for pixel search:

pyautogui

Wayland Users
Install ydotool for best performance:
```sudo apt install ydotool or equivalent for your distro
```
