import colour
import csv
import numpy as np
from itertools import product
from tqdm import tqdm


def color_distance(color1, color2):
    return np.linalg.norm(color1 - color2)


def color_pair_matches(color1, color2, threshold):
    return color_distance(color1, color2) <= threshold


def color_pair_matches_only_with_color_vision_deficiency(color1, color2, M, threshold):
    transformed_color1 = M @ color1
    transformed_color2 = M @ color2
    return color_pair_matches(transformed_color1, transformed_color2, threshold) and not color_pair_matches(color1, color2, threshold)


def save_matching_pairs(matching_pairs, file_name):
    with open(f'{file_name}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['color1', 'color2', 'distance'])
        writer.writerows(matching_pairs)


def scan_grid_for_matching_pairs(grid, color_vision_deficency, file_name, threshold=0):
    M = colour.blindness.matrix_cvd_Machado2009(color_vision_deficency, 1)

    matching_pairs = []

    print(f'{file_name}')
    for color_pair in tqdm(grid, total=128**4):
        if color_pair_matches_only_with_color_vision_deficiency(*color_pair, M, threshold):
            matching_pairs.append(
                [*(tuple(color) for color in color_pair), color_distance(*color_pair)])

    save_matching_pairs(matching_pairs, file_name)


def main():

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

    color_vision_deficency = 'Protanomaly'
    grid = product(greens_no_blue, greens_no_red)
    scan_grid_for_matching_pairs(
        grid, color_vision_deficency, 'Protanomaly_green')

    color_vision_deficency = 'Protanomaly'
    grid = product(blues_no_red, blues_no_green)
    scan_grid_for_matching_pairs(
        grid, color_vision_deficency, 'Protanomaly_blue')

    color_vision_deficency = 'Deuteranomaly'
    grid = product(reds_no_blue, reds_no_green)
    scan_grid_for_matching_pairs(
        grid, color_vision_deficency, 'Deuteranomaly_red')

    color_vision_deficency = 'Deuteranomaly'
    grid = product(blues_no_red, blues_no_green)
    scan_grid_for_matching_pairs(
        grid, color_vision_deficency, 'Deuteranomaly_blue')

    color_vision_deficency = 'Tritanomaly'
    grid = product(reds_no_blue, reds_no_green)
    scan_grid_for_matching_pairs(
        grid, color_vision_deficency, 'Tritanomaly_red')

    color_vision_deficency = 'Tritanomaly'
    grid = product(greens_no_blue, greens_no_red)
    scan_grid_for_matching_pairs(
        grid, color_vision_deficency, 'Tritanomaly_green')


if __name__ == '__main__':
    main()
