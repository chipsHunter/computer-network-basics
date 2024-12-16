import tkinter as tk
import os

from design import MyMainWindow

os.environ["XDG_SESSION_TYPE"] = "xcb"

if __name__ == "__main__":
    root = tk.Tk()
    app = MyMainWindow(root)
    root.protocol("WM_DELETE_WINDOW", app.close)  # Handle window close
    binary_string = int.from_bytes(b"hello wo", byteorder="big")
    divider = int("111100111", 2)
    result = binary_string
    while result > divider & result.bit_length() - divider.bit_length():
        shifted_divider = divider << result.bit_length() - divider.bit_length()
        result = result ^ shifted_divider
    root.mainloop()