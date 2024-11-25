import keyboard
import pyautogui
import random
import secrets
import time
from typing import List, Dict

# Configuration and setup
print("Press 'L' to press the start button, press 1-4 to click columns, or use automation modes.")
base_x = 981
base_y = 720
keyCombination = ['pause', 'l', 'L']
maxClicks = int(input("Enter target number of rows, it will restart after you reach this number so you can't accidentally go further (integer, 1-9): "))
globalclickCounter = 0

# Get user preferences
difficulty = input("Easy, Medium, Hard, Extreme, or Nightmare?: ").lower()
auto_mode = input("Choose mode (manual/random/sequence): ").lower()
if auto_mode == "sequence":
    sequence = input("Enter sequence (e.g., 1234): ")
    sequence = [int(x) - 1 for x in sequence if x.isdigit() and 0 < int(x) <= 4]
delay = float(input("Enter delay between clicks (0.01-1.0 seconds): [0.01-0.03 recommended unless lagging badly. 0.01 may skip even without lag when hitting a high value network call.]: "))
delay = max(0.01, min(1.0, delay))  

def columnoffsetCoords() -> List[Dict[str, int]]:
    if difficulty in ['medium', 'expert', 'extreme']:
        return [
            {"x": -96, "y": -50},
            {"x": 22, "y": -50},
            {"x": 144, "y": -50}
        ]
    elif difficulty == 'hard':
        return [
            {"x": -96, "y": -50},
            {"x": 96, "y": -50},
        ]
    elif difficulty in ['easy', 'nightmare', 'master']:
        return [
            {"x": -130, "y": -50},
            {"x": -35, "y": -50},
            {"x": 60, "y": -50},
            {"x": 155, "y": -50}
        ]
    else:
        print("Invalid option. Defaulting to Medium/Expert.")
        return [
            {"x": -96, "y": -50},
            {"x": 22, "y": -50},
            {"x": 144, "y": -50}
        ]

columnCoords = columnoffsetCoords()
columnNumber = len(columnCoords)
clickDistance = 43
automation_active = False

def clickTile(column: int) -> None:
    global globalclickCounter
    if column < columnNumber:
        x = base_x + columnCoords[column]["x"]
        y = base_y + columnCoords[column]["y"] - (clickDistance * globalclickCounter)
        pyautogui.click(x, y)
        print(f"{column + 1}.")
        globalclickCounter += 1
        if globalclickCounter >= maxClicks:
            globalclickCounter = 0
            if automation_active:
                clickStart()
    else:
        print(f"N/A")

def clickStart() -> None:
    global globalclickCounter
    globalclickCounter = 0
    pyautogui.click(base_x, base_y)
    print("Restarted.")

def toggle_automation(event) -> None:
    global automation_active
    if event.name == 'K'.lower():
        automation_active = not automation_active
        print(f"Automation {'enabled' if automation_active else 'disabled'}")

def automated_clicking() -> None:
    while True:
        if automation_active:
            if auto_mode == "random":
                column = random.randint(0, columnNumber - 1)
                clickTile(column)
            elif auto_mode == "sequence":
                for column in sequence:
                    if not automation_active:
                        break
                    clickTile(column)
                    time.sleep(delay)
                if automation_active:
                    clickStart()
                    time.sleep(delay)
            time.sleep(delay)
        time.sleep(0.1) 

def keyPressed(event) -> None:
    if not automation_active:
        if event.name in ['1', '2', '3', '4']:
            column = int(event.name) - 1
            clickTile(column)
        elif event.name in keyCombination:
            clickStart()

keyboard.on_press(keyPressed)
keyboard.on_press(toggle_automation)

print(f"Script running at {difficulty} difficulty with {auto_mode} mode.")
print("Press 'k' to toggle automation, Esc to stop.")

import threading
automation_thread = threading.Thread(target=automated_clicking, daemon=True)
automation_thread.start()

keyboard.wait('esc')
