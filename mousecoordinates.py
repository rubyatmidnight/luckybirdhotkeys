import pyautogui
import tkinter as tk
from tkinter import Label
import keyboard

def update_position():
    x, y = pyautogui.position()
    position_label.config(text=f"Mouse position: X: {x}, Y: {y}")
    root.after(100, update_position)  # Update every 100ms

def logClick():
    if keyboard.press('left alt'):
        print(pyautogui.position)

# Create the main window
root = tk.Tk()
root.title("Mouse Position Tracker")
root.geometry("300x50")

# Create and pack the label
position_label = Label(root, text="Mouse position: X: 0, Y: 0")
position_label.pack(pady=10)

# Start updating the position
update_position()

# Start the GUI event loop
root.mainloop()