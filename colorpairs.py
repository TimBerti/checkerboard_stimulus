import colour
import csv
import numpy as np
from itertools import product
from tqdm import tqdm


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

def save_matching_pairs(matching_pairs, file_name):
    with open(f'{file_name}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['color1', 'color2', 'transformed_color1',
                        'transformed_color2', 'distance', 'transformed_distance'])
        writer.writerows(matching_pairs)


def scan_grid_for_matching_pairs(grid, color_vision_deficency, file_name, threshold):
    M = colour.blindness.matrix_cvd_Machado2009(color_vision_deficency, 1)

    matching_pairs = []

    print(f'{file_name}')
    for color_pair in tqdm(grid, total=128**4):
        color1, color2 = color_pair
        transformed_color1 = np.rint(M @ color1).astype(int).clip(0, 255)
        transformed_color2 = np.rint(M @ color2).astype(int).clip(0, 255)

        distance = np.linalg.norm(color1 - color2)
        transformed_distance = np.linalg.norm(
            transformed_color1 - transformed_color2)
        if distance > threshold and transformed_distance <= threshold:
            matching_pairs.append(
                [tuple(color1), tuple(color2), tuple(transformed_color1), tuple(transformed_color2), distance, transformed_distance])

    save_matching_pairs(matching_pairs, file_name)

def scan_colorspace(color_vision_deficency, threshold=0):
    grid = product(reds_no_blue, reds_no_green, threshold)
    scan_grid_for_matching_pairs(
        grid, color_vision_deficency, f'{color_vision_deficency}_red')

    grid = product(greens_no_blue, greens_no_red, threshold)
    scan_grid_for_matching_pairs(
        grid, color_vision_deficency, f'{color_vision_deficency}_green')

    grid = product(blues_no_green, blues_no_red, threshold)
    scan_grid_for_matching_pairs(
        grid, color_vision_deficency, f'{color_vision_deficency}_blue')


def main():
    scan_colorspace('Protanopia')
    scan_colorspace('Deuteranopia')
    scan_colorspace('Tritanopia', threshold=2)


if __name__ == '__main__':
    main()
