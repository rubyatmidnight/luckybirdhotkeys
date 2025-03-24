import keyboard
import pyautogui
import secrets
import time
from art import tprint
from typing import List, Dict
from tkinter import Tk, Label, Button, Entry, StringVar, OptionMenu

class CoordinateCalibrator:
    def __init__(self):
        self.root = Tk()
        self.root.title("Game Calibration")
        self.coordinates = {"base_x": 0, "base_y": 0}
        self.recording = False
        self.setup_ui()
        
        # Make window appear on top
        self.root.lift()
        self.root.attributes('-topmost', True)

    def setup_ui(self):
        # Instructions
        Label(self.root, text="1. Click 'Start Recording'").pack(pady=5)
        Label(self.root, text="2. You'll have 3 seconds to position your mouse").pack(pady=5)
        Label(self.root, text="3. Keep your mouse still at the desired position, you do not need to click.").pack(pady=5)
        Label(self.root, text="4. Position will be captured after a moment.").pack(pady=5)
        Label(self.root, text="The defaults are designed for a 1080p monitor with chat disabled and the page scrolled to the top.").pack(pady=5)
        # Status label
        self.status_label = Label(self.root, text="Ready to record position")
        self.status_label.pack(pady=5)
        
        # Position display
        self.position_label = Label(self.root, text="")
        self.position_label.pack(pady=5)
        
        # Buttons
        Button(self.root, text="Start Recording", command=self.start_recording).pack(pady=5)
        Button(self.root, text="Try Again", command=self.reset_position).pack(pady=5)
        Button(self.root, text="Done", command=self.root.destroy).pack(pady=5)

    def start_recording(self):
        self.status_label.config(text="Get ready to position mouse...")
        self.root.iconify()  # Minimize window
        
        def countdown():
            for i in range(3, 0, -1):
                self.status_label.config(text=f"Recording in {i}...")
                self.root.update()
                time.sleep(1)
            
            # Record position
            x, y = pyautogui.position()
            self.coordinates["base_x"] = x
            self.coordinates["base_y"] = y
            
            # Show results
            self.root.deiconify()  # Restore window
            self.status_label.config(text="Position recorded!")
            self.position_label.config(text=f"Recorded position: ({x}, {y})")
            
            # Verify position
            print(f"Base position set to: ({x}, {y})")
            print("Move your mouse to verify it's in the correct spot")
        
        # Run countdown in a separate thread to prevent UI freeze
        import threading
        threading.Thread(target=countdown, daemon=True).start()

    def reset_position(self):
        self.coordinates = {"base_x": 0, "base_y": 0}
        self.status_label.config(text="Ready to record position")
        self.position_label.config(text="")
        print("Position reset. You can try recording again.")

def get_calibrated_coordinates():
    print("NOTICE: Base coordinates are now determined by difficulty setting.")
    print("The calibration is only used as fallback for unknown difficulty settings.")
    calibrator = CoordinateCalibrator()
    calibrator.root.mainloop()
    return calibrator.coordinates

# Configuration and setup
def get_user_preferences():
    print("Press 'L' to press start button, 1-4 for columns, or use automation modes.")
    max_clicks = int(input("Enter target number of rows (1-9). The cursor will not move beyond the max set row (will never over-step target): "))
    difficulty = input("Easy, Medium, Hard, Extreme, or Nightmare? ('expert' and 'master' are also acceptable inputs): ").lower()
    auto_mode = input("Choose mode (manual/random/sequence): ").lower()
    sequence = []
    if auto_mode == "sequence":
        sequence = [int(x) - 1 for x in input("Enter sequence (e.g., 111223412): ") 
                   if x.isdigit() and 0 < int(x) <= 4]
    delay_mode = input("Delay setting for lag compensation 'verylow', 'low', 'medium' or 'high'? Higher settings click slower: ").lower()
    if delay_mode == "verylow":
        delay = float(0.02)
    elif delay_mode == "low":
        delay = float(0.05)
    elif delay_mode == "medium":
        delay = float(0.07)
    else:
        delay = float(0.1)

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

class GameController:
    def __init__(self, base_coords, max_clicks, difficulty, auto_mode, sequence, delay):
        self.difficulty = difficulty.lower()
        
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
        else:
            # Fallback to calibrated coordinates if unknown difficulty
            self.base_x = base_coords["base_x"]
            self.base_y = base_coords["base_y"]
            
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
        self.setup_keyboard_hooks()

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
        # Coordinates for wager controls
        min_bet_x, min_bet_y = 552, 239
        half_bet_x, half_bet_y = 589, 242
        double_bet_x, double_bet_y = 621, 240
        max_bet_x, max_bet_y = 659, 235
        
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
            
    def toggle_pause(self, event) -> None:
        # Pause toggle always works (can't be blocked by pause)
        if event.name == 'P':  # Capital P indicates Shift+P
            self.paused = not self.paused
            status = "PAUSED" if self.paused else "RESUMED"
            print(f"Script {status}: {'All hotkeys disabled' if self.paused else 'All hotkeys enabled'}")

    def key_pressed(self, event) -> None:
        # Only respond to hotkeys if not paused and not in automation mode
        if not self.automation_active and not self.paused:
            if event.name in ['1', '2', '3', '4']:
                self.click_tile(int(event.name) - 1)
            elif event.name.lower() in ['pause', 'l']:
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
    base_coords = get_calibrated_coordinates()
    max_clicks, difficulty, auto_mode, sequence, delay = get_user_preferences()
    
    controller = GameController(base_coords, max_clicks, difficulty, auto_mode, sequence, delay)
    print("~~~   ~~~~   ~~~")
    print("")
    tprint("RubyTower :3", font="magical")
    print("~~~   ~~~~   ~~~")
    print(f"Script running at {difficulty} difficulty with {auto_mode} mode.")
    print("Wager controls: 'm' for min bet, 'h' for half bet, 'd' for double bet, 'x' for max bet.")
    print("Press 'k' to toggle automation, Shift+P to pause/resume all hotkeys, Escape key at any time to stop.")
    
    import threading
    automation_thread = threading.Thread(target=controller.automated_clicking, daemon=True)
    automation_thread.start()
    keyboard.wait('esc')

if __name__ == "__main__":
    main()