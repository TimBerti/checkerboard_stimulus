import time
import colour
import threading
import json
import tkinter as tk
import numpy as np
from checkerboard import CheckerBoard
from pylsl import StreamInfo, StreamOutlet


class CheckerBoardGUI:

    DEFAULT_SETTINGS = {
        "tile_size": 120, "color1": "127,127,127", "color2": "127,127,127",
        "frequency": 7.5, "screen_width": 2560, "screen_height": 1440
    }

    PRESETS = {
        "grey": {"color1": "127,127,127", "color2": "127,127,127"},
        "black-and-white": {"color1": "255,255,255", "color2": "0,0,0"},
        "protanomaly-red": {"color1": "254, 0, 1", "color2": "128, 18, 0"},
        # "protanomaly-green": {"color1": "127, 234, 0", "color2": "0, 252, 12"},
        # "protanomaly-blue": {"color1": "0, 20, 243", "color2": "127, 0, 255"},
        "deuteranomaly-red": {"color1": "255, 0, 4", "color2": "128, 54, 0"},
        # "deuteranomaly-green": {"color1": "32, 161, 0", "color2": "0, 174, 0"},
        # "deuteranomaly-blue": {"color1": "0, 54, 128", "color2": "127, 0, 132"},
        # "tritanomaly-red": {"color1": "210, 0, 51", "color2": "255, 22, 0"},
        # "tritanomaly-green": {"color1": "15, 251, 0", "color2": "0, 247, 12"},
        # "tritanomaly-blue": {"color1": "0, 0, 193", "color2": "16, 0, 195"},
    }

    SERIES = {
        "reference-series": [
            {"preset": "grey", "duration": 4.0},
            {"preset": "black-and-white", "duration": 4.0},
            {"preset": "grey", "duration": 4.0},
            {"preset": "black-and-white", "duration": 4.0},
            {"preset": "grey", "duration": 4.0},
        ],
        "protanomaly-series": [
            {"preset": "grey", "duration": 4.0},
            {"preset": "protanomaly-red", "duration": 4.0},
            {"preset": "grey", "duration": 4.0},
            {"preset": "protanomaly-red", "duration": 4.0},
            {"preset": "grey", "duration": 4.0},
        ],
        "deuteranomaly-series": [
            {"preset": "grey", "duration": 4.0},
            {"preset": "deuteranomaly-red", "duration": 4.0},
            {"preset": "grey", "duration": 4.0},
            {"preset": "deuteranomaly-red", "duration": 4.0},
            {"preset": "grey", "duration": 4.0},
        ],
        "mixed-deuteranomaly-series": [
            {"preset": "grey", "duration": 4.0},
            {"preset": "black-and-white", "duration": 4.0},
            {"preset": "grey", "duration": 4.0},
            {"preset": "deuteranomaly-red", "duration": 4.0},
            {"preset": "grey", "duration": 4.0},
        ],
        "mixed-protanomaly-series": [
            {"preset": "grey", "duration": 4.0},
            {"preset": "black-and-white", "duration": 4.0},
            {"preset": "grey", "duration": 4.0},
            {"preset": "protanomaly-red", "duration": 4.0},
            {"preset": "grey", "duration": 4.0},
        ],
        "mixed-series": [
            {"preset": "grey", "duration": 4.0},
            {"preset": "black-and-white", "duration": 4.0},
            {"preset": "protanomaly-red", "duration": 4.0},
            {"preset": "deuteranomaly-red", "duration": 4.0},
            {"preset": "grey", "duration": 4.0},
        ],
    }

    color_vision_deficency = {"deficiency": "Deuteranomaly", "severity": 0}

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
        self.deficiency.set("Deuteranomaly")
        self.dropdown = tk.OptionMenu(
            self.root, self.deficiency, "Deuteranomaly", "Protanomaly", "Tritanomaly")
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
                  command=self.start).grid(row=10, column=0)
        tk.Button(self.root, text="Update",
                  command=self.update).grid(row=10, column=1)
        tk.Button(self.root, text="Pause",
                  command=self.pause).grid(row=11, column=0)

        max_columns = 3

        # Calculate the total number of rows needed for the presets
        preset_rows = len(self.PRESETS) // max_columns
        if len(self.PRESETS) % max_columns > 0:
            preset_rows += 1

        i = 0
        for preset in self.PRESETS.keys():
            tk.Button(self.root, text=preset, command=lambda preset=preset: self.apply_settings(
                self.PRESETS[preset])).grid(row=12 + i // max_columns, column=max_columns - 1 - (i % max_columns))
            i += 1

        i = 0  # Reset the counter for series buttons
        for series in self.SERIES.items():
            tk.Button(self.root, text=series[0], command=lambda series=series: self.run_sequence(
                *series)).grid(row=12 + preset_rows + i // max_columns, column=max_columns - 1 - (i % max_columns))
            i += 1

        stream_info = StreamInfo('marker', 'Markers', 1, 0, 'string', 'myuid34234')
        self.sender = StreamOutlet(stream_info)
        self.apply_settings(self.DEFAULT_SETTINGS)


    def start(self):
        self.board = CheckerBoard(*self._get_params())
        self.board.start()

    def update(self):
        if self.board:
            self._update_color_vision_deficiency()
            self.board.update_params(*self._get_params())

    def _update_color_vision_deficiency(self):
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
            color1 = np.round(colour.algebra.vector_dot(
                color_vision_deficency_model, color1).clip(0, 255)).astype(int)
            color2 = np.round(colour.algebra.vector_dot(
                color_vision_deficency_model, color2).clip(0, 255)).astype(int)

        return color1, color2

    def pause(self):
        if self.board:
            self.board.running = False

    def quit(self):
        if self.board:
            self.board.running = False
        self.root.quit()

    def apply_settings(self, settings):
        if "tile_size" in settings:
            self.tile_size.delete(0, tk.END)
            self.tile_size.insert(0, str(settings["tile_size"]))
        if "color1" in settings:
            self.color1.delete(0, tk.END)
            self.color1.insert(0, settings["color1"])
        if "color2" in settings:
            self.color2.delete(0, tk.END)
            self.color2.insert(0, settings["color2"])
        if "frequency" in settings:
            self.frequency.delete(0, tk.END)
            self.frequency.insert(0, str(settings["frequency"]))
        if "screen_width" in settings:
            self.screen_width.delete(0, tk.END)
            self.screen_width.insert(0, str(settings["screen_width"]))
        if "screen_height" in settings:
            self.screen_height.delete(0, tk.END)
            self.screen_height.insert(0, str(settings["screen_height"]))
        self.update()

    def run_sequence(self, series, sequence):
        threading.Thread(target=self._sequence, args=[series, sequence]).start()

    def _sequence(self, series, sequence):
        meta_data = {
            "series": series,
            "screen_width": self.screen_width.get(),
            "screen_height": self.screen_height.get(),
            "frequency": self.frequency.get(),
            "tile_size": self.tile_size.get(),
            "deficiency": self.color_vision_deficency["deficiency"], 
            "severity": self.color_vision_deficency["severity"]
        }
        self.sender.push_sample([json.dumps(meta_data)])
        for step in sequence:
            self.sender.push_sample([step["preset"]])
            self.apply_settings(self.PRESETS[step["preset"]])
            time.sleep(step["duration"])
        self.apply_settings(self.PRESETS["grey"])
        self.sender.push_sample(["stop"])

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    gui = CheckerBoardGUI()
    gui.run()
