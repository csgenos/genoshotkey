#!/usr/bin/env python3
"""
GenosHotkey v1.0.0.0 - Advanced Auto Clicker + Macro Studio
"""

import tkinter as tk
import customtkinter as ctk
import time
import threading
import random
import json
import subprocess
from pathlib import Path
from tkinter import filedialog

from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Listener as KbListener, Key, KeyCode, Controller as KbController

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class GenosHotkey(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GenosHotkey v1.0.0.0")
        self.geometry("580x960")
        self.resizable(False, False)
        
        self.mouse_ctrl = MouseController()
        self.kb_ctrl = KbController()
        self.running = False
        self.recording = False
        self.macro_steps = []
        self.hotkey = Key.f6
        self.fixed_pos = None
        
        self.icon_path = Path("genos_icon.png")
        if self.icon_path.exists():
            try:
                self.iconphoto(False, tk.PhotoImage(file=str(self.icon_path)))
            except:
                pass
        
        self.create_widgets()
        self.detect_environment()
        self.setup_global_listeners()
        self.setup_hotkeys()

    def detect_environment(self):
        try:
            self.is_wayland = "wayland" in subprocess.getoutput("echo $XDG_SESSION_TYPE").lower()
            if self.is_wayland:
                self.status.configure(text="Wayland detected • ydotool recommended", text_color="#ffcc00")
        except:
            pass

    def create_widgets(self):
        # Header
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=20, pady=12)
        ctk.CTkLabel(header, text="GENOSHOTKEY", font=ctk.CTkFont(size=28, weight="bold"), text_color="#ff3333").pack()
        ctk.CTkLabel(header, text="v1.0.0.0 • Advanced Macro Studio", font=ctk.CTkFont(size=13)).pack()

        # Delay
        ctk.CTkLabel(self, text="Delay Between Actions", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(20,0))
        delay_f = ctk.CTkFrame(self)
        delay_f.pack(pady=10, padx=30, fill="x")
        self.delay_value = ctk.DoubleVar(value=40.0)
        self.delay_unit = ctk.StringVar(value="ms")
        ctk.CTkEntry(delay_f, textvariable=self.delay_value, width=120, justify="center").pack(side="left", padx=20, pady=8)
        units = ["ms", "seconds", "minutes", "hours", "days"]
        ctk.CTkOptionMenu(delay_f, values=units, variable=self.delay_unit).pack(side="left", padx=10)
        self.delay_label = ctk.CTkLabel(self, text="≈ 25 CPS")
        self.delay_label.pack(pady=5)
        self.delay_value.trace("w", lambda *a: self.update_delay_label())
        self.delay_unit.trace("w", lambda *a: self.update_delay_label())

        # Options
        opts = ctk.CTkFrame(self)
        opts.pack(pady=12, padx=30, fill="x")
        self.random_delay = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(opts, text="Human-like Random Variation", variable=self.random_delay).pack(anchor="w", padx=20, pady=6)
        
        ctk.CTkLabel(opts, text="Mouse Button").pack(anchor="w", padx=20, pady=(8,2))
        self.button_var = ctk.StringVar(value="left")
        ctk.CTkSegmentedButton(opts, values=["left", "right", "middle"], variable=self.button_var).pack(pady=4, padx=20, fill="x")
        
        ctk.CTkLabel(opts, text="Click Mode").pack(anchor="w", padx=20, pady=(8,2))
        self.mode_var = ctk.StringVar(value="single")
        ctk.CTkSegmentedButton(opts, values=["single", "double", "hold"], variable=self.mode_var).pack(pady=4, padx=20, fill="x")

        # Hotkey & Position
        hk_frame = ctk.CTkFrame(self)
        hk_frame.pack(pady=10, padx=30, fill="x")
        ctk.CTkLabel(hk_frame, text="Hotkey:").pack(side="left", padx=20)
        self.hotkey_btn = ctk.CTkButton(hk_frame, text="F6", width=100, command=self.set_hotkey)
        self.hotkey_btn.pack(side="left", padx=10)

        pos_frame = ctk.CTkFrame(self)
        pos_frame.pack(pady=8, padx=30, fill="x")
        ctk.CTkButton(pos_frame, text="📍 Set Fixed Position", command=self.pick_position, fg_color="#444444").pack(side="left", padx=20, pady=8)
        self.pos_label = ctk.CTkLabel(pos_frame, text="Dynamic Cursor")
        self.pos_label.pack(side="right", padx=20)

        ctk.CTkLabel(self, text="Repeat Count (0 = Infinite)").pack(pady=(15,0))
        self.repeat_var = ctk.IntVar(value=0)
        ctk.CTkEntry(self, textvariable=self.repeat_var).pack(pady=6, padx=80, fill="x")

        # Macro Studio
        mf = ctk.CTkFrame(self)
        mf.pack(pady=15, padx=30, fill="x")
        ctk.CTkLabel(mf, text="Advanced Macro Studio", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=8)
        
        btnrow = ctk.CTkFrame(mf)
        btnrow.pack(pady=8)
        ctk.CTkButton(btnrow, text="🎙 Record", fg_color="#ff3333", command=self.toggle_record).pack(side="left", padx=5)
        ctk.CTkButton(btnrow, text="▶ Play", command=self.play_macro).pack(side="left", padx=5)
        ctk.CTkButton(btnrow, text="💾 Save", command=self.save_macro).pack(side="left", padx=5)
        ctk.CTkButton(btnrow, text="📂 Load", command=self.load_macro).pack(side="left", padx=5)
        ctk.CTkButton(btnrow, text="Clear", command=self.clear_macro).pack(side="left", padx=5)

        kb_frame = ctk.CTkFrame(mf)
        kb_frame.pack(pady=10, fill="x", padx=20)
        ctk.CTkLabel(kb_frame, text="Add Action:").pack(side="left", padx=10)
        self.key_entry = ctk.CTkEntry(kb_frame, placeholder_text="hold w | ctrl+shift+t | f5")
        self.key_entry.pack(side="left", padx=10, fill="x", expand=True)
        ctk.CTkButton(kb_frame, text="Add", command=self.add_manual_action).pack(side="right", padx=10)

        self.macro_text = ctk.CTkTextbox(mf, height=260)
        self.macro_text.pack(pady=10, padx=20, fill="x")

        self.toggle_btn = ctk.CTkButton(self, text="START", fg_color="#ff3333", hover_color="#cc2222",
                                        font=ctk.CTkFont(size=20, weight="bold"), height=70, command=self.toggle_clicking)
        self.toggle_btn.pack(pady=25, padx=50, fill="x")

        self.status = ctk.CTkLabel(self, text="Ready • v1.0.0.0", text_color="#aaaaaa")
        self.status.pack(pady=10)

    # === All other methods (get_delay_seconds, update_delay_label, set_hotkey, etc.) remain the same as the last complete version I gave you.

    # (To save space, use the full methods from the previous complete code I sent. They are already optimized.)

if __name__ == "__main__":
    app = GenosHotkey()
    app.mainloop()
