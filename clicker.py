import keyboard
import pyautogui

print("Press 'L' to press the start button, press 1, 2, 3, or 4 to click each column.")

# Base coordinates and settings
base_x = 777  # X-coordinate of the start button. 982 if chat is not open
base_y = 715  # Y-coordinate of the start button
keyCombination = ['left alt', 'l']
maxClicks = 9  # Maximum number of clicks before resetting
globalclickCounter = 0  # Single counter for all columns

difficulty = input("Easy, Medium, Hard, Extreme, or Nightmare?: ").lower()

# Define the coordinates for each column relative to the base point
def columnoffsetCoords():
    if difficulty in ['medium', 'expert', 'extreme']:
        return [
            {"x": -96, "y": -50},
            {"x": 22, "y": -50}, 
            {"x": 144, "y": -50} 
        ]
    elif difficulty == 'hard':
        return [
            {"x": -96, "y": -50},  # Column 1
            {"x": 96, "y": -50},   # Column 2
        ]
    elif difficulty in ['easy', 'nightmare', 'master']:
        return [
            {"x": -130, "y": -50},  # Column 1
            {"x": -35, "y": -50},   # Column 2
            {"x": 60, "y": -50},  # Column 3
            {"x": 155, "y": -50}   # Column 4
        ]
    else:
        print("Invalid option. Defaulting to Easy.")
        return [
            {"x": -130, "y": -50},  # Column 1
            {"x": -35, "y": -50},   # Column 2
            {"x": 60, "y": -50},  # Column 3
            {"x": 155, "y": -50}   # Column 4
        ]

columnCoords = columnoffsetCoords()
columnNumber = len(columnCoords)

# The vertical distance between clicks in a column
clickDistance = 43

def clickTile(column):
    global globalclickCounter
    if column < columnNumber:
        x = base_x + columnCoords[column]["x"]
        y = base_y + columnCoords[column]["y"] - (clickDistance * globalclickCounter)
        pyautogui.click(x, y)
        print(f"Clicked column {column + 1}.")
        globalclickCounter += 1
        if globalclickCounter >= maxClicks:
            globalclickCounter = 0
    else:
        print(f"N/A")

def clickStart():
    global globalclickCounter
    globalclickCounter = 0
    pyautogui.click(base_x, base_y)
    print("Restarted.")

def keyPressed(event):
    if event.name in ['1', '2', '3', '4']:
        column = int(event.name) - 1
        clickTile(column)
    elif event.name in keyCombination:
        clickStart()

keyboard.on_press(keyPressed)
print(f"Script is running at {difficulty} difficulty. Press Esc to stop.")
keyboard.wait('esc')