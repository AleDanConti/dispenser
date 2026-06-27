# ui/base_screen.py
import tkinter as tk
from ui.theme import COLORS

class BaseScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller

    def on_show(self, **kwargs):
        pass
