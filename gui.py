import time
import colour
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
    }

    SERIES = {
        "Series 1": [
            {"preset": "Preset 1", "duration": 2.0},
            {"preset": "Preset 2", "duration": 5.0},
            {"preset": "Preset 3", "duration": 5.0}
        ],
    }

    color_vision_deficency = {"deficiency": "Protanomaly", "severity": 0}

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
        tk.Label(self.root, text="Color Vision Deficiency:").grid(
            row=7, column=0)
        tk.Label(self.root, text="Severity:").grid(row=8, column=0)

        self.tile_size = tk.Entry(self.root)
        self.color1 = tk.Entry(self.root)
        self.color2 = tk.Entry(self.root)
        self.frequency = tk.Entry(self.root)
        self.screen_width = tk.Entry(self.root)
        self.screen_height = tk.Entry(self.root)
        self.deficiency = tk.StringVar(self.root)
        self.deficiency.set("Protanomaly")
        self.dropdown = tk.OptionMenu(
            self.root, self.deficiency, "Protanomaly", "Deuteranomaly", "Tritanomaly")
        self.severity = tk.Scale(
            self.root, from_=0, to=1, resolution=0.1, orient=tk.HORIZONTAL,)

        self.tile_size.grid(row=1, column=1)
        self.color1.grid(row=2, column=1)
        self.color2.grid(row=3, column=1)
        self.frequency.grid(row=4, column=1)
        self.screen_width.grid(row=5, column=1)
        self.screen_height.grid(row=6, column=1)
        self.dropdown.grid(row=7, column=1)
        self.severity.grid(row=8, column=1)

        tk.Button(self.root, text="Start",
                  command=self.start).grid(row=9, column=0)
        tk.Button(self.root, text="Update",
                  command=self.update).grid(row=9, column=1)
        tk.Button(self.root, text="Pause",
                  command=self.pause).grid(row=10, column=0)

        for i, (preset, settings) in enumerate(self.PRESETS.items()):
            tk.Button(self.root, text=preset, command=lambda settings=settings: self.apply_settings(
                settings)).grid(row=int(11+(i/3) % 3), column=i % 3)

        for i, (series, sequence) in enumerate(self.SERIES.items()):
            tk.Button(self.root, text=series, command=lambda sequence=sequence: self.run_sequence(
                sequence)).grid(row=int(12+(i/3) % 3), column=i % 3)

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
                self.update_color_vision_deficiency()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_color_vision_deficiency(self):
        self.color_vision_deficency["deficiency"] = self.deficiency.get()
        self.color_vision_deficency["severity"] = self.severity.get()

    def _get_params(self):
        tile_size = int(self.tile_size.get())
        color1, color2 = self._get_color()
        frequency = float(self.frequency.get())
        screen_width = int(self.screen_width.get())
        screen_height = int(self.screen_height.get())
        return tile_size, color1, color2, frequency, screen_width, screen_height

    def _get_color(self):
        color1 = tuple(map(int, self.color1.get().split(',')))
        color2 = tuple(map(int, self.color2.get().split(',')))

        if self.color_vision_deficency["severity"] > 0:
            color_vision_deficency_model = colour.blindness.matrix_cvd_Machado2009(
                self.color_vision_deficency["deficiency"], self.color_vision_deficency["severity"])
            color1 = colour.algebra.vector_dot(
                color_vision_deficency_model, color1)
            color2 = colour.algebra.vector_dot(
                color_vision_deficency_model, color2)
            color1 = [0 if colour1 < 0 else 255 if colour1 >
                      255 else colour1 for colour1 in color1]
            color2 = [0 if colour2 < 0 else 255 if colour2 >
                      255 else colour2 for colour2 in color2]

        return color1, color2

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
