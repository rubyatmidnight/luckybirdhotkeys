import sys
import os
import json

# Hide console window when packaged as .exe (Windows only)
if getattr(sys, 'frozen', False):
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 1)  # 0=hide, 1=show

try:
    import keyboard
    import pyautogui
    import secrets
    import time
    from art import tprint
    from typing import List, Dict
    import threading
    import tkinter as tk
    from tkinter import StringVar
except ImportError as e:
    print("A required module is missing:", e)
    print("Please run 'pip install -r requirements.txt' before running this program.")
    input("Press Enter to exit...")
    sys.exit(1)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

CONFIG_FILENAME = "lbtower2_config.json"

def get_config_path():
    # Store config in user home directory for portability
    home = os.path.expanduser("~")
    return os.path.join(home, CONFIG_FILENAME)

def load_config():
    config_path = get_config_path()
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            # Validate config keys
            if not isinstance(config, dict):
                return {}
            return config
        except Exception:
            return {}
    return {}

def save_config(config):
    config_path = get_config_path()
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save config: {e}")

def get_user_preferences():
    config = load_config()
    print("Press 'L' to press start button, 1-4 for respective columns, or use automation modes.")

    # Helper to get value from config or prompt
    def get_int(prompt, key, default, minval, maxval):
        val = config.get(key, default)
        while True:
            try:
                inp = input(f"{prompt} [{val}]: ").strip()
                if inp == "":
                    v = int(val)
                else:
                    v = int(inp)
                if minval <= v <= maxval:
                    config[key] = v
                    return v
                else:
                    print(f"Please enter a number between {minval} and {maxval}.")
            except ValueError:
                print(f"Invalid input. Please enter a number between {minval} and {maxval}.")

    def get_str(prompt, key, default, allowed=None):
        val = config.get(key, default)
        while True:
            inp = input(f"{prompt} [{val}]: ").strip()
            v = inp.lower() if inp else str(val).lower()
            if allowed is None or v in allowed:
                config[key] = v
                return v
            else:
                print(f"Please enter one of: {', '.join(allowed)}.")

    max_clicks = get_int(
        "Enter target number of rows (1-9). The cursor will not move beyond the max set row, in any mode (will never over-step target):",
        "max_clicks", 5, 1, 9
    )

    difficulty = get_str(
        "Easy, Medium, Hard, Extreme, or Nightmare? ('expert' and 'master' are also acceptable inputs):",
        "difficulty", "easy",
        allowed=["easy", "medium", "hard", "extreme", "nightmare", "expert", "master"]
    )

    auto_mode = get_str(
        "Choose mode (manual/random/sequence):",
        "auto_mode", "manual",
        allowed=["manual", "random", "sequence"]
    )

    sequence = []
    if auto_mode == "sequence":
        prev_seq = "".join(str(int(x)+1) for x in config.get("sequence", [])) if config.get("sequence") else ""
        seq_input = input(f"Enter sequence (e.g., 111223412) [{prev_seq}]: ").strip()
        if not seq_input and prev_seq:
            seq_input = prev_seq
        sequence = [int(x) - 1 for x in seq_input if x.isdigit() and 0 < int(x) <= 4]
        config["sequence"] = sequence
    else:
        config["sequence"] = []

    delay_mode = get_str(
        "Delay setting for lag compensation 'low', 'high'? The high setting clicks slowly for laggier environments:",
        "delay_mode", "low",
        allowed=["low", "high"]
    )
    if delay_mode == "low":
        delay = float(0.06)
    else:
        delay = float(0.1)
    config["delay_mode"] = delay_mode

    # Save config for next run
    save_config(config)
    return max_clicks, difficulty, auto_mode, sequence, delay

def get_column_offsets(difficulty: str) -> List[Dict[str, int]]:
    offsets = {
        'medium':  [{"x": 0, "y": 0}, {"x": 125, "y": 0}, {"x": 250, "y": 0}],
        'expert': [{"x": 0, "y": 0}, {"x": 125, "y": 0}, {"x": 250, "y": 0}],
        'hard': [{"x": 0, "y": 0}, {"x": 184, "y": 0}],
        'easy': [{"x": 0, "y": 0}, {"x": 93, "y": 0}, {"x": 186, "y": 0}, {"x": 279, "y": 0}],
        'extreme': [{"x": 0, "y": 0}, {"x": 93, "y": 0}, {"x": 186, "y": 0}, {"x": 279, "y": 0}],
        'nightmare': [{"x": 0, "y": 0}, {"x": 93, "y": 0}, {"x": 186, "y": 0}, {"x": 279, "y": 0}],
        'master': [{"x": 0, "y": 0}, {"x": 93, "y": 0}, {"x": 186, "y": 0}, {"x": 279, "y": 0}]
    }
    return offsets.get(difficulty, offsets['easy'])

class StatusWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("RubyTower Hotkeys Status")
        self.root.geometry("320x140")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        try:
            self.root.iconbitmap(False, resource_path("favicon.ico"))
        except Exception:
            pass

        self.status_var = StringVar()
        self.automation_var = StringVar()
        self.difficulty_var = StringVar()
        self.mode_var = StringVar()

        tk.Label(self.root, text="RubyTower Hotkeys", font=("Segoe UI", 14, "bold")).pack(pady=(8, 0))
        tk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 11)).pack()
        tk.Label(self.root, textvariable=self.automation_var, font=("Segoe UI", 11)).pack()
        tk.Label(self.root, textvariable=self.difficulty_var, font=("Segoe UI", 10)).pack()
        tk.Label(self.root, textvariable=self.mode_var, font=("Segoe UI", 10)).pack()
        tk.Label(self.root, text="Pause: [p]   Automation: [k]   Quit: [esc]", font=("Segoe UI", 8)).pack(pady=(8, 0))

        self.status_var.set("Status: Ready")
        self.automation_var.set("Automation: Disabled")
        self.difficulty_var.set("")
        self.mode_var.set("")

        # Run the tkinter mainloop in a thread
        self.thread = threading.Thread(target=self.root.mainloop, daemon=True)
        self.thread.start()

    def set_status(self, paused: bool):
        if paused:
            self.status_var.set("Status: PAUSED (all hotkeys disabled)")
        else:
            self.status_var.set("Status: Running (hotkeys enabled)")

    def set_automation(self, enabled: bool):
        self.automation_var.set(f"Automation: {'Enabled' if enabled else 'Disabled'}")

    def set_difficulty(self, difficulty: str):
        self.difficulty_var.set(f"Difficulty: {difficulty.capitalize()}")

    def set_mode(self, mode: str):
        self.mode_var.set(f"Mode: {mode.capitalize()}")

class GameController:
    def __init__(self, max_clicks, difficulty, auto_mode, sequence, delay, status_window=None):
        self.difficulty = difficulty.lower()
        self.max_clicks = max_clicks
        self.column_coords = get_column_offsets(self.difficulty)
        self.column_number = len(self.column_coords)
        self.auto_mode = auto_mode
        self.sequence = sequence
        self.delay = delay
        self.click_distance = 44  # Updated vertical offset
        self.global_click_counter = 0
        self.automation_active = False
        self.paused = False
        self.status_window = status_window
        # Set base coordinates based on difficulty
        if self.difficulty in ['easy', 'extreme', 'master', 'nightmare']:
            self.base_x = 997
            self.base_y = 688
        elif self.difficulty in ['medium', 'expert']:
            self.base_x = 1013
            self.base_y = 688
        elif self.difficulty in ['hard']:
            self.base_x = 1045
            self.base_y = 688
        self.setup_keyboard_hooks()
        if self.status_window:
            self.status_window.set_status(self.paused)
            self.status_window.set_automation(self.automation_active)
            self.status_window.set_difficulty(self.difficulty)
            self.status_window.set_mode(self.auto_mode)

    def click_tile(self, column: int) -> None:
        if column < self.column_number:
            x = self.base_x + self.column_coords[column]["x"]
            y = self.base_y + self.column_coords[column]["y"] - (self.click_distance * self.global_click_counter)
            pyautogui.click(x, y)
            print(f"{column + 1}.")
            self.global_click_counter += 1
            if self.global_click_counter >= self.max_clicks:
                self.global_click_counter = 0
                if self.automation_active:
                    self.click_start()

    def click_start(self) -> None:
        self.global_click_counter = 0
        pyautogui.click(535, 409)  # Hardcoded play button at 1080p
        print("Restarted.")

    def wager_hotkeys(self, event) -> None:
        # Coordinates for wager controls for 1080p no chat
        min_bet_x, min_bet_y = 552, 280
        half_bet_x, half_bet_y = 589, 280
        double_bet_x, double_bet_y = 621, 280
        max_bet_x, max_bet_y = 659, 280

        # Only respond if not paused and not in automation mode
        if not self.automation_active and not self.paused:
            if event.name == 'm':
                pyautogui.click(min_bet_x, min_bet_y)
                print("Min bet")
            elif event.name == 'h':
                pyautogui.click(half_bet_x, half_bet_y)
                print("Half bet")
            elif event.name == 'd':
                pyautogui.click(double_bet_x, double_bet_y)
                print("Double bet")
            elif event.name == 'x':
                pyautogui.click(max_bet_x, max_bet_y)
                print("Max bet")

    def toggle_automation(self, event) -> None:
        # Automation toggle works even when paused
        if event.name == 'k':
            self.automation_active = not self.automation_active
            print(f"Automation {'enabled' if self.automation_active else 'disabled'}")
            if self.status_window:
                self.status_window.set_automation(self.automation_active)

    def toggle_pause(self, event) -> None:
        # Pause toggle always works (can't be blocked by pause)
        # Now mapped to 'p' (lowercase, easier to hit)
        if event.name == 'p':
            self.paused = not self.paused
            status = "PAUSED" if self.paused else "RESUMED"
            print(f"Script {status}: {'All hotkeys disabled' if self.paused else 'All hotkeys enabled'}")
            if self.status_window:
                self.status_window.set_status(self.paused)

    def key_pressed(self, event) -> None:
        # Only respond to hotkeys if not paused and not in automation mode
        if not self.automation_active and not self.paused:
            if event.name in ['1', '2', '3', '4']:
                self.click_tile(int(event.name) - 1)
            elif event.name.lower() == 'l' or event.name == 'pause':
                self.click_start()

    def automated_clicking(self) -> None:
        while True:
            if self.automation_active:
                if self.auto_mode == "random":
                    column = secrets.randbelow(self.column_number)
                    self.click_tile(column)
                elif self.auto_mode == "sequence":
                    for column in self.sequence:
                        if not self.automation_active:
                            break
                        self.click_tile(column)
                        time.sleep(self.delay)
                    if self.automation_active:
                        self.click_start()
                        time.sleep(self.delay)
                time.sleep(self.delay)
            time.sleep(0.1)

    def setup_keyboard_hooks(self):
        keyboard.on_press(self.key_pressed)
        keyboard.on_press(self.toggle_automation)
        keyboard.on_press(self.toggle_pause)
        keyboard.on_press(self.wager_hotkeys)

def main():
    # Print a friendly message for Windows users
    print("Welcome to RubyTower Hotkeys!")
    print("If you see a Windows Defender SmartScreen warning, click 'More info' and then 'Run anyway'.")
    print("If you have issues, make sure to run as Administrator for hotkeys to work.")
    print("")

    max_clicks, difficulty, auto_mode, sequence, delay = get_user_preferences()

    # Start the status window
    status_window = StatusWindow()

    controller = GameController(max_clicks, difficulty, auto_mode, sequence, delay, status_window=status_window)
    print("~~~   ~~~~   ~~~")
    print("")
    try:
        tprint("RubyTower :3", font="magical")
    except Exception:
        print("RubyTower :3")
    print("~~~   ~~~~   ~~~")
    print(f"Script running at {difficulty} difficulty with {auto_mode} mode.")
    print("Wager controls: 'm' for min bet, 'h' for half bet, 'd' for double bet, 'x' for max bet.")
    print("Press 'k' to toggle automation, 'p' to pause/resume all hotkeys, Escape key at any time to stop.")

    if status_window:
        status_window.set_difficulty(difficulty)
        status_window.set_mode(auto_mode)

    automation_thread = threading.Thread(target=controller.automated_clicking, daemon=True)
    automation_thread.start()
    try:
        keyboard.wait('esc')
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()