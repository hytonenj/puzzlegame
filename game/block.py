import pygame

class Block:
    def __init__(self, x, y, width, height, can_move=False, image_path="assets/block.png", image_path_moveable="assets/block_moveable.png"):
        self.movements = []
        self.rect = pygame.Rect(x, y, width, height)
        self.can_move = can_move
        self.image_path = image_path
        self.image_path_moveable = image_path_moveable
        self.load_image()

    def load_image(self):
        if self.can_move:
            self.image = pygame.image.load(self.image_path_moveable)
        else:
            self.image = pygame.image.load(self.image_path)
        self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def change_movability(self):
        if self.can_move:
            self.can_move = False
            self.load_image()
        else:
            self.can_move = True
            self.load_image()

    def record_movement(self, direction):
        self.movements.append(direction)

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        self.record_movement((dx, dy))

    def shake(self, screen):
        original_position = self.rect.topleft
        shake_distance = 5
        for _ in range(5):
            self.rect.x += shake_distance
            self.draw(screen)
            pygame.display.update()
            pygame.time.wait(10)
            self.rect.x -= shake_distance
            self.draw(screen)
            pygame.display.update()
            pygame.time.wait(10)
        self.rect.topleft = original_position
        self.draw(screen)
        pygame.display.update()