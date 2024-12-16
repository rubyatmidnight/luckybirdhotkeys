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
        
        self.root.lift()
        self.root.attributes('-topmost', True)

    def setup_ui(self):

        Label(self.root, text="1. Click 'Start Recording'").pack(pady=5)
        Label(self.root, text="2. You'll have 3 seconds to position your mouse").pack(pady=5)
        Label(self.root, text="3. Keep your mouse still at the desired position, you do not need to click.").pack(pady=5)
        Label(self.root, text="4. Position will be captured after a moment.").pack(pady=5)
        Label(self.root, text="The defaults are designed for a 1080p monitor with chat disabled and the page scrolled to the top.").pack(pady=5)

        self.status_label = Label(self.root, text="Ready to record position")
        self.status_label.pack(pady=5)

        self.position_label = Label(self.root, text="")
        self.position_label.pack(pady=5)

        Button(self.root, text="Start Recording", command=self.start_recording).pack(pady=5)
        Button(self.root, text="Try Again", command=self.reset_position).pack(pady=5)
        Button(self.root, text="Done", command=self.root.destroy).pack(pady=5)

    def start_recording(self):
        self.status_label.config(text="Get ready to position mouse...")
        self.root.iconify() 
        
        def countdown():
            for i in range(3, 0, -1):
                self.status_label.config(text=f"Recording in {i}...")
                self.root.update()
                time.sleep(1)
            

            x, y = pyautogui.position()
            self.coordinates["base_x"] = x
            self.coordinates["base_y"] = y
            

            self.root.deiconify()  
            self.status_label.config(text="Position recorded! Hit 'done' then return to the cmd window.")
            self.position_label.config(text=f"Recorded position: ({x}, {y})")
            

            print(f"Base position set to: ({x}, {y})")
            print("Move your mouse to verify it's in the correct spot")
        
        import threading
        threading.Thread(target=countdown, daemon=True).start()

    def reset_position(self):
        self.coordinates = {"base_x": 0, "base_y": 0}
        self.status_label.config(text="Ready to record position")
        self.position_label.config(text="")
        print("Position reset. You can try recording again.")

def get_calibrated_coordinates():
    calibrator = CoordinateCalibrator()
    calibrator.root.mainloop()
    return calibrator.coordinates

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
        'medium':  [{"x": -96, "y": -50}, {"x": 22, "y": -50}, {"x": 144, "y": -50}],
        'extreme': [{"x": -96, "y": -50}, {"x": 22, "y": -50}, {"x": 144, "y": -50}], 
        'expert': [{"x": -96, "y": -50}, {"x": 22, "y": -50}, {"x": 144, "y": -50}],

        'hard': [{"x": -96, "y": -50}, {"x": 96, "y": -50}],

        'easy': [{"x": -130, "y": -50}, {"x": -35, "y": -50}, {"x": 60, "y": -50}, {"x": 155, "y": -50}],
        'nightmare': [{"x": -130, "y": -50}, {"x": -35, "y": -50}, {"x": 60, "y": -50}, {"x": 155, "y": -50}],
        'master': [{"x": -130, "y": -50}, {"x": -35, "y": -50}, {"x": 60, "y": -50}, {"x": 155, "y": -50}]
    }
    return offsets.get(difficulty, offsets['easy'])

class GameController:
    def __init__(self, base_coords, max_clicks, difficulty, auto_mode, sequence, delay):
        self.base_x = base_coords["base_x"]
        self.base_y = base_coords["base_y"]
        self.max_clicks = max_clicks
        self.column_coords = get_column_offsets(difficulty)
        self.column_number = len(self.column_coords)
        self.auto_mode = auto_mode
        self.sequence = sequence
        self.delay = delay
        self.click_distance = 43
        self.global_click_counter = 0
        self.automation_active = False
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
        pyautogui.click(self.base_x, self.base_y)
        print("Restarted.")
    
    # def clickwagerHotkeys(self, event) -> None:
    #    decreaseWx = self.base_x + 127
    #    decreaseWy = self.base_y + 61
    #    increaseWx = self.base_x + 170
    #    increaseWy = self.base_y + 61
    #    if not self.automation_active:
    #        if event.name == '+' or '=':
    #            pyautogui.click(increaseWx, increaseWy)
    #        elif event.name == '-' or '_':
    #            pyautogui.click(decreaseWx, decreaseWy)


    def toggle_automation(self, event) -> None:
        if event.name == 'k':
            self.automation_active = not self.automation_active
            print(f"Automation {'enabled' if self.automation_active else 'disabled'}")

    def key_pressed(self, event) -> None:
        if not self.automation_active:
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
    #    keyboard.on_press_key('=' or '+', self.clickwagerHotkeys)
    #    keyboard.on_press_key('_' or '-', self.clickwagerHotkeys)

def main():
    base_coords = get_calibrated_coordinates()
    max_clicks, difficulty, auto_mode, sequence, delay = get_user_preferences()
    
    controller = GameController(base_coords, max_clicks, difficulty, auto_mode, sequence, delay)
    print("~~~   ~~~~   ~~~")
    print("")
    tprint("RubyTower :3", font="magical")
    print("~~~   ~~~~   ~~~")
    print(f"Script running at {difficulty} difficulty with {auto_mode} mode.")
    # print("- and = to increase or decrease wager.")
    print("Press 'k' to toggle automation, Escape key at any time to stop.")
    
    import threading
    automation_thread = threading.Thread(target=controller.automated_clicking, daemon=True)
    automation_thread.start()
    keyboard.wait('esc')

if __name__ == "__main__":
    main()
