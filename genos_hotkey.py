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
        self.geometry("620x1080")
        self.resizable(False, False)
        
        self.mouse_ctrl = MouseController()
        self.kb_ctrl = KbController()
        self.running = False
        self.recording = False
        self.macro_steps = []
        self.hotkey = Key.f6
        self.fixed_pos = None
        self.variables = {}
        
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
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=20, pady=12)
        ctk.CTkLabel(header, text="GENOSHOTKEY", font=ctk.CTkFont(size=28, weight="bold"), text_color="#ff3333").pack()
        ctk.CTkLabel(header, text="v1.0.0.0 • Advanced Macro Studio", font=ctk.CTkFont(size=13)).pack()

        # Delay Section (same as before)
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

        # Options (same as before)
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

        # Hotkey & Position (same)
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

        # Macro Studio (same)
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

        # Improved Scripting Tab
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(pady=15, padx=20, fill="both", expand=True)
        script_tab = self.tabview.add("Scripting")
        ctk.CTkLabel(script_tab, text="Script Editor (AHK-like)", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        self.script_text = ctk.CTkTextbox(script_tab, height=420, font=ctk.CTkFont(family="Consolas", size=13))
        self.script_text.pack(pady=10, padx=20, fill="both", expand=True)
        self.script_text.insert("0.0", "# Welcome to GenosHotkey Scripting\n\nclick 800 600\nsleep 500\nrandomdelay 50 150\nloop 10:\n    press space\n    sleep 100\ntype Hello from GenosHotkey!\npress enter")

        script_btns = ctk.CTkFrame(script_tab)
        script_btns.pack(pady=10)
        ctk.CTkButton(script_btns, text="Run Script", fg_color="#00cc00", command=self.run_script).pack(side="left", padx=10)
        ctk.CTkButton(script_btns, text="Clear", command=self.clear_script).pack(side="left", padx=10)
        ctk.CTkButton(script_btns, text="Save Script", command=self.save_script).pack(side="left", padx=10)
        ctk.CTkButton(script_btns, text="Load Script", command=self.load_script).pack(side="left", padx=10)
        ctk.CTkButton(script_btns, text="Load Example", command=self.load_example).pack(side="left", padx=10)

        self.toggle_btn = ctk.CTkButton(self, text="START", fg_color="#ff3333", hover_color="#cc2222",
                                        font=ctk.CTkFont(size=20, weight="bold"), height=70, command=self.toggle_clicking)
        self.toggle_btn.pack(pady=25, padx=50, fill="x")

        self.status = ctk.CTkLabel(self, text="Ready • v1.0.0.0", text_color="#aaaaaa")
        self.status.pack(pady=10)

    # ==================== Scripting Engine ====================
    def run_script(self):
        script = self.script_text.get("0.0", "end").strip()
        if not script:
            return
        self.status.configure(text="Running script...", text_color="#00ffaa")
        threading.Thread(target=self.execute_script, args=(script,), daemon=True).start()

    def execute_script(self, script):
        try:
            self.variables = {}
            lines = [line.strip() for line in script.split('\n') if line.strip() and not line.strip().startswith('#')]
            i = 0
            while i < len(lines):
                line = lines[i]
                if line.lower().startswith("loop"):
                    count = int(line.split()[1].rstrip(':'))
                    loop_body = []
                    i += 1
                    while i < len(lines) and not lines[i].strip().lower().startswith("end"):
                        loop_body.append(lines[i])
                        i += 1
                    for _ in range(count):
                        for cmd in loop_body:
                            self.parse_and_execute(cmd)
                else:
                    self.parse_and_execute(line)
                i += 1
        except Exception as e:
            self.after(0, lambda: self.status.configure(text=f"Script Error: {e}", text_color="red"))
        else:
            self.after(0, lambda: self.status.configure(text="Script finished", text_color="#00ffaa"))

    def parse_and_execute(self, line):
        if not line:
            return
        parts = line.split()
        cmd = parts[0].lower()

        try:
            if cmd == "click":
                x, y = int(parts[1]), int(parts[2])
                self.mouse_ctrl.position = (x, y)
                self.mouse_ctrl.click(Button.left)
            elif cmd == "move":
                x, y = int(parts[1]), int(parts[2])
                self.mouse_ctrl.position = (x, y)
            elif cmd == "drag":
                x1, y1, x2, y2 = int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])
                self.mouse_ctrl.position = (x1, y1)
                self.mouse_ctrl.press(Button.left)
                time.sleep(0.1)
                self.mouse_ctrl.position = (x2, y2)
                self.mouse_ctrl.release(Button.left)
            elif cmd == "press":
                self.press_key(parts[1])
            elif cmd == "hold":
                self.hold_key(parts[1])
            elif cmd == "release":
                self.release_key(parts[1])
            elif cmd == "type":
                text = " ".join(parts[1:])
                for char in text:
                    self.kb_ctrl.press(char)
                    self.kb_ctrl.release(char)
                    time.sleep(0.015)
            elif cmd == "sleep":
                ms = int(parts[1])
                time.sleep(ms / 1000.0)
            elif cmd == "randomdelay":
                min_ms = int(parts[1])
                max_ms = int(parts[2])
                ms = random.randint(min_ms, max_ms)
                time.sleep(ms / 1000.0)
            elif cmd == "set":
                var = parts[1]
                value = parts[2]
                if value == "+1":
                    self.variables[var] = self.variables.get(var, 0) + 1
                elif value == "-1":
                    self.variables[var] = self.variables.get(var, 0) - 1
                else:
                    self.variables[var] = int(value)
        except Exception as e:
            print(f"Command failed: {line} -> {e}")

    # ==================== Other Methods (same as previous) ====================
    def setup_global_listeners(self):
        def on_click(x, y, button, pressed):
            if self.recording and pressed:
                self.macro_steps.append({"type": "mouse_click", "x": int(x), "y": int(y)})
                self.refresh_macro_display()

        def on_key_press(key):
            if self.recording:
                try:
                    k = str(key).replace("Key.", "").replace("'", "").lower()
                    self.macro_steps.append({"type": "key_press", "key": k})
                    self.refresh_macro_display()
                except:
                    pass

        self.mouse_listener = mouse.Listener(on_click=on_click)
        self.kb_listener = KbListener(on_press=on_key_press)
        self.mouse_listener.daemon = True
        self.kb_listener.daemon = True
        self.mouse_listener.start()
        self.kb_listener.start()

    def toggle_record(self):
        self.recording = not self.recording
        if self.recording:
            self.macro_steps.clear()
            self.status.configure(text="🔴 RECORDING ACTIVE", text_color="#ff3333")
        else:
            self.status.configure(text="Recording stopped")

    def add_manual_action(self):
        text = self.key_entry.get().strip().lower()
        if not text: return
        if text.startswith("hold "):
            self.macro_steps.append({"type": "key_hold", "key": text[5:].strip()})
        elif text.startswith("release "):
            self.macro_steps.append({"type": "key_release", "key": text[8:].strip()})
        else:
            action = self.parse_key(text)
            if action:
                self.macro_steps.append(action)
        self.refresh_macro_display()
        self.key_entry.delete(0, tk.END)

    def parse_key(self, text):
        if '+' in text:
            return {"type": "key_chord", "keys": [k.strip() for k in text.split('+')]}
        return {"type": "key_press", "key": text}

    def refresh_macro_display(self):
        lines = []
        for s in self.macro_steps:
            if s["type"] == "mouse_click":
                lines.append(f"🖱️ Click at ({s['x']}, {s['y']})")
            elif s["type"] == "key_chord":
                lines.append(f"⌨️ Chord: {' + '.join(s['keys'])}")
            elif s["type"] == "key_hold":
                lines.append(f"⌨️ Hold: {s['key']}")
            elif s["type"] == "key_release":
                lines.append(f"⌨️ Release: {s['key']}")
            else:
                lines.append(f"⌨️ Key: {s.get('key', '')}")
        self.macro_text.delete("0.0", "end")
        self.macro_text.insert("0.0", "\n".join(lines))

    def play_macro(self):
        if not self.macro_steps: return
        threading.Thread(target=self.macro_playback, daemon=True).start()

    def macro_playback(self):
        for step in self.macro_steps:
            try:
                if step["type"] == "mouse_click":
                    self.mouse_ctrl.position = (step["x"], step["y"])
                    self.mouse_ctrl.click(Button.left)
                elif step["type"] == "key_press":
                    self.press_key(step["key"])
                elif step["type"] == "key_chord":
                    self.execute_chord(step["keys"])
                elif step["type"] == "key_hold":
                    self.hold_key(step["key"])
                elif step["type"] == "key_release":
                    self.release_key(step["key"])
            except:
                pass
            time.sleep(0.08)

    def press_key(self, k):
        try:
            key_obj = getattr(Key, k, KeyCode.from_char(k))
            self.kb_ctrl.press(key_obj)
            time.sleep(0.05)
            self.kb_ctrl.release(key_obj)
        except:
            pass

    def hold_key(self, k):
        try:
            key_obj = getattr(Key, k, KeyCode.from_char(k))
            self.kb_ctrl.press(key_obj)
        except:
            pass

    def release_key(self, k):
        try:
            key_obj = getattr(Key, k, KeyCode.from_char(k))
            self.kb_ctrl.release(key_obj)
        except:
            pass

    def execute_chord(self, keys):
        modifiers = [k for k in keys if k in ["ctrl", "shift", "alt", "super"]]
        main = [k for k in keys if k not in modifiers]
        for m in modifiers:
            self.press_key(m)
        for m in main:
            self.press_key(m)
        for m in reversed(modifiers):
            self.release_key(m)

    def save_macro(self):
        path = filedialog.asksaveasfilename(defaultextension=".json")
        if path:
            with open(path, "w") as f:
                json.dump(self.macro_steps, f, indent=2)

    def load_macro(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            with open(path) as f:
                self.macro_steps = json.load(f)
            self.refresh_macro_display()

    def clear_macro(self):
        self.macro_steps.clear()
        self.macro_text.delete("0.0", "end")

    def toggle_clicking(self):
        if self.running:
            self.running = False
            self.toggle_btn.configure(text="START", fg_color="#ff3333")
            self.status.configure(text="Stopped")
        else:
            self.running = True
            self.toggle_btn.configure(text="STOP", fg_color="#cc2222")
            self.status.configure(text="RUNNING...", text_color="#ff3333")
            threading.Thread(target=self.clicker_loop, daemon=True).start()

    def clicker_loop(self):
        clicks = 0
        max_clicks = self.repeat_var.get()
        btn_map = {"left": Button.left, "right": Button.right, "middle": Button.middle}
        btn = btn_map[self.button_var.get()]

        while self.running and (max_clicks == 0 or clicks < max_clicks):
            if self.fixed_pos:
                try:
                    self.mouse_ctrl.position = self.fixed_pos
                except:
                    pass

            if self.mode_var.get() == "hold":
                self.mouse_ctrl.press(btn)
                time.sleep(0.08)
                self.mouse_ctrl.release(btn)
            else:
                self.mouse_ctrl.click(btn)
                if self.mode_var.get() == "double":
                    time.sleep(0.04)
                    self.mouse_ctrl.click(btn)

            clicks += 1
            base = self.get_delay_seconds()
            delay = base * random.uniform(0.9, 1.1) if self.random_delay.get() else base
            time.sleep(max(0.001, delay))

        if self.running:
            self.running = False
            self.after(0, lambda: [self.toggle_btn.configure(text="START", fg_color="#ff3333"),
                                   self.status.configure(text="Finished")])

    def pick_position(self):
        self.withdraw()
        time.sleep(0.6)
        self.fixed_pos = self.mouse_ctrl.position
        self.pos_label.configure(text=f"Fixed: {self.fixed_pos}")
        self.deiconify()

    def get_delay_seconds(self):
        v = self.delay_value.get()
        u = self.delay_unit.get()
        conv = {"ms": 0.001, "seconds": 1, "minutes": 60, "hours": 3600, "days": 86400}
        return v * conv.get(u, 0.001)

    def save_script(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            with open(path, "w") as f:
                f.write(self.script_text.get("0.0", "end"))

    def load_script(self):
        path = filedialog.askopenfilename(filetypes=[("Text", "*.txt")])
        if path:
            with open(path) as f:
                self.script_text.delete("0.0", "end")
                self.script_text.insert("0.0", f.read())

    def clear_script(self):
        self.script_text.delete("0.0", "end")

    def load_example(self):
        example = """# GenosHotkey Script Example
click 800 600
sleep 500
randomdelay 50 150
loop 10:
    press space
    sleep 100
type Hello from GenosHotkey!
press enter"""
        self.script_text.delete("0.0", "end")
        self.script_text.insert("0.0", example)

if __name__ == "__main__":
    app = GenosHotkey()
    app.mainloop()
