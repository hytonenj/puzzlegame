import pygame
from color import Color

class Key:
    def __init__(self, x, y, width, height, image_path="assets/key.png"):
        self.movements = []
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (width, height))

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def record_movement(self, direction):
        self.movements.append(direction)

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        self.record_movement((dx, dy))

    def undo_movement(self):
        if self.movements:
            dx, dy = self.movements.pop()
            self.rect.x -= dx
            self.rect.y -= dy
    
    def delete_key(self):
        self.rect.x = -100
        self.rect.y = -100