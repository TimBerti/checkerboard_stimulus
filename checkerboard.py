import pygame
import time
import threading
import numpy as np


class CheckerBoard:

    def __init__(self, tile_size, color1=(0, 0, 0), color2=(255, 255, 255), frequency=1, screen_width=800, screen_height=600):
        pygame.display.init()
        self.running = True
        self.dot_radius = 10 
        self.dot_color = (0, 0, 0)
        self.dot_position = (screen_width // 2, screen_height // 2)
        self._init_board_params(tile_size, color1, color2,
                                frequency, screen_width, screen_height)

    def _init_board_params(self, tile_size, color1, color2, frequency, screen_width, screen_height):
        self.tile_size = tile_size
        self.color1 = color1
        self.color2 = color2
        self.frequency = frequency
        self.screen_width = screen_width
        self.screen_height = screen_height
        self._calculate_board_size_and_position()

    def _calculate_board_size_and_position(self):
        self.width = self.height = min(self.screen_width, self.screen_height)
        self.start_x = (self.screen_width - self.width) // 2
        self.start_y = (self.screen_height - self.height) // 2

    def update_params(self, tile_size, color1, color2, frequency, screen_width, screen_height):
        self._init_board_params(tile_size, color1, color2,
                                frequency, screen_width, screen_height)
        self.surface.fill((0, 0, 0))
                
        self.dot_radius = 10 
        self.dot_color = self._largest_contrast(color1, color2)
        self.dot_position = (self.screen_width // 2, self.screen_height // 2)
        pygame.display.flip()

    def start(self):
        self._setup_display()
        threading.Thread(target=self._game_loop).start()

    def _setup_display(self):
        self.surface = pygame.display.set_mode(
            (self.screen_width, self.screen_height), pygame.NOFRAME)

    def _game_loop(self):
        while self.running:
            self._handle_events()
            self._draw_checkerboard()
            pygame.draw.circle(self.surface, self.dot_color, self.dot_position, self.dot_radius)
            pygame.display.flip()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()

    def _draw_checkerboard(self):
        color_sequence = self._get_color_sequence()

        for y in range(self.start_y, self.start_y + self.height, self.tile_size):
            for x in range(self.start_x, self.start_x + self.width, self.tile_size):
                rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                pygame.draw.rect(self.surface, color_sequence[(
                    x-self.start_x) // self.tile_size % 2 == (y-self.start_y) // self.tile_size % 2], rect)

    def _get_color_sequence(self):
        return (self.color1, self.color2) if int(time.time() * self.frequency) % 2 == 0 else (self.color2, self.color1)

    def _largest_contrast(self, color1, color2):
        color1 = np.array(color1)
        color2 = np.array(color2)
        return tuple(np.cross(color1, color2).clip(0, 255).astype(int))
        