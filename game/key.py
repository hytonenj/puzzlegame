import pygame
import asyncio

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

    async def shake(self, screen):
        original_position = self.rect.topleft
        shake_distance = 5
        for _ in range(5):
            self.rect.x += shake_distance
            self.draw(screen)
            pygame.display.update()
            await asyncio.sleep(0.01)
            self.rect.x -= shake_distance
            self.draw(screen)
            pygame.display.update()
            await asyncio.sleep(0.01)
        self.rect.topleft = original_position
        self.draw(screen)
        pygame.display.update()