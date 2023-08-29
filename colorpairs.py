import colour
import csv
import numpy as np
from itertools import product
from tqdm import tqdm


class ColorspaceScanner:

    reds_no_green = np.array(
        list(product(range(128, 256), [0], range(0, 128))))
    reds_no_blue = np.array(
        list(product(range(128, 256), range(0, 128), [0])))
    greens_no_blue = np.array(
        list(product(range(0, 128), range(128, 256), [0])))
    greens_no_red = np.array(
        list(product([0], range(128, 256), range(0, 128))))
    blues_no_red = np.array(
        list(product([0], range(0, 128), range(128, 256))))
    blues_no_green = np.array(
        list(product(range(0, 128), [0], range(128, 256))))
    
    
    def __init__(self, color_vision_deficency, threshold=0):
        self.color_vision_deficency = color_vision_deficency
        self.threshold = threshold

        self.matching_pairs = {'red': [], 'green': [], 'blue': []}
        self.grid = {
            'red': product(self.reds_no_green, self.reds_no_blue),
            'green': product(self.greens_no_blue, self.greens_no_red),
            'blue': product(self.blues_no_red, self.blues_no_green)
        }

        self.transformation_matrix = colour.blindness.matrix_cvd_Machado2009(self.color_vision_deficency, 1)


    def save_matching_pairs(self, color):
        filename = f'{self.color_vision_deficency}_{color}.csv'
        with open(f'color_pairs/{filename}', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['color1', 'color2', 'transformed_color1',
                            'transformed_color2', 'distance', 'transformed_distance'])
            writer.writerows(self.matching_pairs[color])


    def scan_grid_for_matching_pairs(self, color):

        print(f'{self.color_vision_deficency}_{color}')
        for color_pair in tqdm(self.grid[color], total=128**4):
            color1, color2 = color_pair
            transformed_color1 = np.rint(self.transformation_matrix @ color1).astype(int).clip(0, 255)
            transformed_color2 = np.rint(self.transformation_matrix @ color2).astype(int).clip(0, 255)

            distance = np.linalg.norm(color1 - color2)
            transformed_distance = np.linalg.norm(
                transformed_color1 - transformed_color2)
            if distance > self.threshold and transformed_distance <= self.threshold:
                self.matching_pairs[color].append(
                    [tuple(color1), tuple(color2), tuple(transformed_color1), tuple(transformed_color2), distance, transformed_distance])

        self.save_matching_pairs(color)

    def scan_colorspace(self):
        self.scan_grid_for_matching_pairs('red')
        self.scan_grid_for_matching_pairs('green')
        self.scan_grid_for_matching_pairs('blue')


def main():

    scanner = ColorspaceScanner('Protanomaly')
    scanner.scan_colorspace()

    scanner = ColorspaceScanner('Deuteranomaly')
    scanner.scan_colorspace()

    scanner = ColorspaceScanner('Tritanomaly')
    scanner.scan_colorspace()


if __name__ == '__main__':
    main()
