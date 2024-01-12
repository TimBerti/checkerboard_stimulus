import time
import colour
import threading
import json
import customtkinter as ctk
import numpy as np
from checkerboard import CheckerBoard
from pylsl import StreamInfo, StreamOutlet

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class CheckerBoardGUI:

    DEFAULT_SETTINGS = {
        "tile_size": 144, "color1": "127,127,127", "color2": "127,127,127",
        "frequency": 16.5, "screen_width": 2560, "screen_height": 1440
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
        "tritanomaly-red": {"color1": "210, 0, 51", "color2": "255, 22, 0"},
        # "tritanomaly-green": {"color1": "15, 251, 0", "color2": "0, 247, 12"},
        # "tritanomaly-blue": {"color1": "0, 0, 193", "color2": "16, 0, 195"},
        # "protanomaly-contrast_0.0": {"color1": "0, 37,0", "color2": "255, 0 ,0"},
        # "protanomaly-contrast_0.45": {"color1": "23, 31, 0", "color2": "126, 22, 0"},
        # "protanomaly-contrast_0.65": {"color1": "29, 30, 0", "color2": "89, 26, 0"},
        # "protanomaly-contrast_0.8": {"color1": "34, 29, 0", "color2": "66, 28, 0"},
        # "protanomaly-contrast_0.9": {"color1": "36, 29, 0", "color2": "51, 28, 0"},
        # "deuteranomaly-contrast_0.0": {"color1": "0, 106,0", "color2": "255, 0 ,7"},
        # "deuteranomaly-contrast_0.45": {"color1": "61, 84, 2", "color2": "144, 43, 5"},
        # "deuteranomaly-contrast_0.65": {"color1": "75, 79, 3", "color2": "119, 55, 4"},
        # "deuteranomaly-contrast_0.8": {"color1": "83, 75, 3", "color2": "106, 63, 4"},
        # "deuteranomaly-contrast_0.9": {"color1": "87, 73, 4", "color2": "98, 67, 4"},
        "deuteranomaly-1-1": {"color1": "255, 148, 7", "color2": "0, 255, 0"},
        "deuteranomaly-2-1": {"color1": "255, 0, 7", "color2": "0, 106, 0"},
        "deuteranomaly-3-1": {"color1": "255, 148, 255", "color2": "0, 255, 247"},
        "deuteranomaly-4-1": {"color1": "255, 0, 255", "color2": "0, 106, 247"},
        "deuteranomaly-1-0.25": {"color1": "159, 188, 4", "color2": "95, 214, 2"},
        "deuteranomaly-2-0.25": {"color1": "159, 40, 4", "color2": "95, 66, 2"},
        "deuteranomaly-3-0.25": {"color1": "159, 188, 252", "color2": "95, 214, 250"},
        "deuteranomaly-4-0.25": {"color1": "159, 40, 252", "color2": "95, 66, 250"},
    }

    SERIES = {
        "reference-series": [
            {"preset": "grey", "duration": 4.0},
            {"preset": "black-and-white", "duration": 4.0},
            {"preset": "grey", "duration": 4.0},
            {"preset": "black-and-white", "duration": 4.0},
            {"preset": "grey", "duration": 4.0},
        ],
        "mixed-deuteranomaly-series": [
            {"preset": "grey", "duration": 4.0},
            {"preset": "black-and-white", "duration": 4.0},
            {"preset": "grey", "duration": 4.0},
            {"preset": "deuteranomaly-red", "duration": 4.0},
            {"preset": "grey", "duration": 4.0},
        ],
        # "mixed-protanomaly-series": [
        #     {"preset": "grey", "duration": 4.0},
        #     {"preset": "black-and-white", "duration": 4.0},
        #     {"preset": "grey", "duration": 4.0},
        #     {"preset": "protanomaly-red", "duration": 4.0},
        #     {"preset": "grey", "duration": 4.0},
        # ],
        # "mixed-series": [
        #     {"preset": "grey", "duration": 4.0},
        #     {"preset": "black-and-white", "duration": 4.0},
        #     {"preset": "protanomaly-red", "duration": 4.0},
        #     {"preset": "deuteranomaly-red", "duration": 4.0},
        #     {"preset": "grey", "duration": 4.0},
        # ],
        # "protanomaly-contrast-series": [
        #     {"preset": "grey", "duration": 2.0},
        #     {"preset": "protanomaly-contrast_0.0", "duration": 4.0},
        #     {"preset": "protanomaly-contrast_0.8", "duration": 4.0},
        #     {"preset": "protanomaly-contrast_0.45", "duration": 4.0},
        #     {"preset": "protanomaly-contrast_0.9", "duration": 4.0},
        #     {"preset": "protanomaly-contrast_0.65", "duration": 4.0},
        #     {"preset": "grey", "duration": 2.0},
        # ],
        # "deuteranomaly-contrast-series": [
        #     {"preset": "grey", "duration": 2.0},
        #     {"preset": "deuteranomaly-contrast_0.0", "duration": 4.0},
        #     {"preset": "deuteranomaly-contrast_0.8", "duration": 4.0},
        #     {"preset": "deuteranomaly-contrast_0.45", "duration": 4.0},
        #     {"preset": "deuteranomaly-contrast_0.9", "duration": 4.0},
        #     {"preset": "deuteranomaly-contrast_0.65", "duration": 4.0},
        #     {"preset": "grey", "duration": 2.0},
        # ],
        # "mixed-contrast-series": [
        #     {"preset": "grey", "duration": 2.0},
        #     {"preset": "black-and-white", "duration": 3.0},
        #     {"preset": "grey", "duration": 2.0},
        #     {"preset": "deuteranomaly-contrast_0.0", "duration": 3.0},
        #     {"preset": "grey", "duration": 2.0},
        #     {"preset": "protanomaly-contrast_0.8", "duration": 3.0},
        #     {"preset": "grey", "duration": 2.0},
        #     {"preset": "black-and-white", "duration": 3.0},
        #     {"preset": "grey", "duration": 2.0},
        #     {"preset": "protanomaly-contrast_0.0", "duration": 3.0},
        #     {"preset": "grey", "duration": 2.0},
        #     {"preset": "deuteranomaly-contrast_0.8", "duration": 3.0},
        #     {"preset": "grey", "duration": 2.0},
        # ],
        # "mixed-contrast-series": [
        #     {"preset": "grey", "duration": 2.0},
        #     {"preset": "black-and-white", "duration": 3.0},
        #     {"preset": "grey", "duration": 2.0},
        #     {"preset": "deuteranomaly-contrast_0.0", "duration": 3.0},
        #     {"preset": "grey", "duration": 2.0},
        #     {"preset": "black-and-white", "duration": 3.0},
        #     {"preset": "grey", "duration": 2.0},
        #     {"preset": "deuteranomaly-contrast_0.8", "duration": 3.0},
        #     {"preset": "grey", "duration": 2.0},
        # ],
        "multicolor-deuteranomaly-series": [
            {"preset": "grey", "duration": 2.0},
            {"preset": "deuteranomaly-1-1", "duration": 4.0},
            {"preset": "grey", "duration": 3.0},
            {"preset": "deuteranomaly-3-0.25", "duration": 4.0},
            {"preset": "grey", "duration": 3.0},
            {"preset": "deuteranomaly-1-0.25", "duration": 4.0},
            {"preset": "grey", "duration": 3.0},
            {"preset": "deuteranomaly-3-1", "duration": 4.0},
            {"preset": "grey", "duration": 2.0},
        ],
    }

    color_vision_deficency = {"deficiency": "Deuteranomaly", "severity": 0}

    def __init__(self):

        self.root = ctk.CTk()
        self.root.title("Checkerboard GUI")
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.board = None

        ctk.CTkLabel(self.root, text="Tile Size:").grid(row=1, column=0)
        ctk.CTkLabel(self.root, text="Color 1 (R,G,B):").grid(row=2, column=0)
        ctk.CTkLabel(self.root, text="Color 2 (R,G,B):").grid(row=3, column=0)
        ctk.CTkLabel(self.root, text="Frequency:").grid(row=4, column=0)
        ctk.CTkLabel(self.root, text="Screen Width:").grid(row=5, column=0)
        ctk.CTkLabel(self.root, text="Screen Height:").grid(row=6, column=0)
        ctk.CTkLabel(self.root, text="Color Vision Deficiency:").grid(
            row=7, column=0)
        ctk.CTkLabel(self.root, text="Severity:").grid(row=8, column=0)

        self.tile_size = ctk.CTkEntry(self.root)
        self.color1 = ctk.CTkEntry(self.root)
        self.color2 = ctk.CTkEntry(self.root)
        self.frequency = ctk.CTkEntry(self.root)
        self.screen_width = ctk.CTkEntry(self.root)
        self.screen_height = ctk.CTkEntry(self.root)
        self.deficiency = ctk.CTkOptionMenu(
            self.root, values = ["Deuteranomaly", "Protanomaly", "Tritanomaly"])
        self.severity = ctk.DoubleVar(self.root)
        def round_sensitivity(_):
            self.severity.set(round(float(self.severity.get()), 2))
        self.severity_slider = ctk.CTkSlider(
            self.root, from_=0, to=1, number_of_steps=100, variable=self.severity, command=round_sensitivity)
        self.slider_val = ctk.CTkLabel(self.root, textvariable=self.severity)

        self.tile_size.grid(row=1, column=1)
        self.color1.grid(row=2, column=1)
        self.color2.grid(row=3, column=1)
        self.frequency.grid(row=4, column=1)
        self.screen_width.grid(row=5, column=1)
        self.screen_height.grid(row=6, column=1)
        self.deficiency.grid(row=7, column=1)
        self.severity_slider.grid(row=8, column=1)
        self.slider_val.grid(row=8, column=2)

        ctk.CTkButton(self.root, text="Start",
                  command=self.start).grid(row=10, column=0, pady=10, padx=10)
        ctk.CTkButton(self.root, text="Pause",
                  command=self.pause).grid(row=10, column=1, pady=10, padx=10)
        ctk.CTkButton(self.root, text="Update",
                  command=self.update).grid(row=10, column=2, pady=10, padx=10)

        max_columns = 3

        # Calculate the total number of rows needed for the presets
        preset_rows = len(self.PRESETS) // max_columns
        if len(self.PRESETS) % max_columns > 0:
            preset_rows += 1

        ctk.CTkLabel(self.root, text="Presets:").grid(row=11, column=0)

        i = 0
        for preset in self.PRESETS.keys():
            ctk.CTkButton(self.root, text=preset, command=lambda preset=preset: self.apply_settings(
                self.PRESETS[preset])).grid(row=12 + i // max_columns, column=max_columns - 1 - ((i - 1) % max_columns), pady=10, padx=10)
            i += 1

        ctk.CTkLabel(self.root, text="Series:").grid(row=13 + preset_rows, column=0)

        i = 0  # Reset the counter for series buttons
        for series in self.SERIES.items():
            ctk.CTkButton(self.root, text=series[0], command=lambda series=series: self.run_sequence(
                *series)).grid(row=14 + preset_rows + i // max_columns, column=max_columns - 1 - ((i - 1) % max_columns), pady=10, padx=10)
            i += 1

        stream_info = StreamInfo('marker', 'Markers', 2, 0, 'string', 'myuid34234')
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
            self.tile_size.delete(0, ctk.END)
            self.tile_size.insert(0, str(settings["tile_size"]))
        if "color1" in settings:
            self.color1.delete(0, ctk.END)
            self.color1.insert(0, settings["color1"])
        if "color2" in settings:
            self.color2.delete(0, ctk.END)
            self.color2.insert(0, settings["color2"])
        if "frequency" in settings:
            self.frequency.delete(0, ctk.END)
            self.frequency.insert(0, str(settings["frequency"]))
        if "screen_width" in settings:
            self.screen_width.delete(0, ctk.END)
            self.screen_width.insert(0, str(settings["screen_width"]))
        if "screen_height" in settings:
            self.screen_height.delete(0, ctk.END)
            self.screen_height.insert(0, str(settings["screen_height"]))
        self.update()

    def run_sequence(self, series, sequence):
        threading.Thread(target=self._sequence, args=[series, sequence]).start()

    def _sequence(self, series, sequence):
        self.update()
        meta_data = json.dumps({
            "series": series,
            "screen_width": self.screen_width.get(),
            "screen_height": self.screen_height.get(),
            "frequency": self.frequency.get(),
            "tile_size": self.tile_size.get(),
            "deficiency": self.color_vision_deficency["deficiency"], 
            "severity": self.color_vision_deficency["severity"]
        })
        self.sender.push_sample(["start", meta_data])
        for step in sequence:
            self.sender.push_sample([step["preset"], meta_data])
            self.apply_settings(self.PRESETS[step["preset"]])
            time.sleep(step["duration"])
        self.apply_settings(self.PRESETS["grey"])
        self.sender.push_sample(["stop", meta_data])

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    gui = CheckerBoardGUI()
    gui.run()
