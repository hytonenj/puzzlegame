import pygame
import asyncio

class Door:
    def __init__(self, x, y, width, height, image_path="assets/pixel_door_closed.png"):
        self.movements = []
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.open = False

    def is_open(self):
        return self.open
    
    def is_moveable(self):
        return True

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def get_location(self):
        return self.rect.x, self.rect.y
    
    def open_door(self):
        self.open = True

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
            return -dx, -dy
        else:
            return 0, 0

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

    def change_image(self):
        if self.open:
            self.image = pygame.image.load("assets/pixel_door_open.png")
            self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
        else:
            self.image = pygame.image.load("assets/pixel_door_closed.png")
            self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
