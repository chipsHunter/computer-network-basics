import tkinter as tk
import os

from design import MyMainWindow

os.environ["XDG_SESSION_TYPE"] = "xcb"

if __name__ == "__main__":
    root = tk.Tk()
    app = MyMainWindow(root)
    root.protocol("WM_DELETE_WINDOW", app.close)  # Handle window close
    root.mainloop()