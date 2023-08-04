import time
import tkinter as tk
from tkinter import messagebox
from checkerboard import CheckerBoard


class CheckerBoardGUI:

    PRESETS = {
        "Preset 1": {"tile_size": 60, "color1": "255,255,255",
                     "color2": "0,0,0", "frequency": 1.0, "screen_width": 1920, "screen_height": 1080},
        "Preset 2": {"tile_size": 60, "color1": "0,0,255",
                     "color2": "0,255,0", "frequency": 1.0, "screen_width": 1920, "screen_height": 1080},
        "Preset 3": {"tile_size": 60, "color1": "255,255,0",
                     "color2": "0,255,255", "frequency": 1.5, "screen_width": 1920, "screen_height": 1080},
        # Add more presets here...
    }

    SERIES = {
        "Series 1": [
            {"preset": "Preset 1", "duration": 2.0},
            {"preset": "Preset 2", "duration": 5.0},
            {"preset": "Preset 3", "duration": 5.0}
        ],
        # Add more series here...
    }

    def __init__(self):

        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.board = None

        tk.Label(self.root, text="Tile Size:").grid(row=1, column=0)
        tk.Label(self.root, text="Color 1 (R,G,B):").grid(row=2, column=0)
        tk.Label(self.root, text="Color 2 (R,G,B):").grid(row=3, column=0)
        tk.Label(self.root, text="Frequency:").grid(row=4, column=0)
        tk.Label(self.root, text="Screen Width:").grid(row=5, column=0)
        tk.Label(self.root, text="Screen Height:").grid(row=6, column=0)

        self.tile_size = tk.Entry(self.root)
        self.color1 = tk.Entry(self.root)
        self.color2 = tk.Entry(self.root)
        self.frequency = tk.Entry(self.root)
        self.screen_width = tk.Entry(self.root)
        self.screen_height = tk.Entry(self.root)

        self.tile_size.grid(row=1, column=1)
        self.color1.grid(row=2, column=1)
        self.color2.grid(row=3, column=1)
        self.frequency.grid(row=4, column=1)
        self.screen_width.grid(row=5, column=1)
        self.screen_height.grid(row=6, column=1)

        tk.Button(self.root, text="Start",
                  command=self.start).grid(row=7, column=0)
        tk.Button(self.root, text="Update",
                  command=self.update).grid(row=7, column=1)
        tk.Button(self.root, text="Pause",
                  command=self.pause).grid(row=8, column=0)

        for i, (preset, settings) in enumerate(self.PRESETS.items()):
            tk.Button(self.root, text=preset, command=lambda settings=settings: self.apply_settings(
                settings)).grid(row=int(9+(i/3) % 3), column=i % 3)

        for i, (series, sequence) in enumerate(self.SERIES.items()):
            tk.Button(self.root, text=series, command=lambda sequence=sequence: self.run_sequence(
                sequence)).grid(row=int(10+(i/3) % 3), column=i % 3)

    def start(self):
        try:
            self.board = CheckerBoard(*self._get_params())
            self.board.start()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update(self):
        try:
            if self.board:
                self.board.update_params(*self._get_params())
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _get_params(self):
        tile_size = int(self.tile_size.get())
        color1 = tuple(map(int, self.color1.get().split(',')))
        color2 = tuple(map(int, self.color2.get().split(',')))
        frequency = float(self.frequency.get())
        screen_width = int(self.screen_width.get())
        screen_height = int(self.screen_height.get())
        return tile_size, color1, color2, frequency, screen_width, screen_height

    def pause(self):
        if self.board:
            self.board.running = False

    def quit(self):
        if self.board:
            self.board.running = False
        self.root.quit()

    def apply_settings(self, settings):
        self.tile_size.delete(0, tk.END)
        self.tile_size.insert(0, str(settings["tile_size"]))
        self.color1.delete(0, tk.END)
        self.color1.insert(0, settings["color1"])
        self.color2.delete(0, tk.END)
        self.color2.insert(0, settings["color2"])
        self.frequency.delete(0, tk.END)
        self.frequency.insert(0, str(settings["frequency"]))
        self.screen_width.delete(0, tk.END)
        self.screen_width.insert(0, str(settings["screen_width"]))
        self.screen_height.delete(0, tk.END)
        self.screen_height.insert(0, str(settings["screen_height"]))
        self.update()

    def run_sequence(self, sequence):
        for step in sequence:
            self.apply_settings(self.PRESETS[step["preset"]])
            time.sleep(step["duration"])
        self.pause()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    gui = CheckerBoardGUI()
    gui.run()
