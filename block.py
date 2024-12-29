import pygame
from color import Color

class Block:
    def __init__(self, x, y, width, height, image_path="assets/block.png"):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (width, height))

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)