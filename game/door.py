import pygame

class Door:
    def __init__(self, x, y, width, height, image_path="assets/door_closed.png"):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.open = False

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def get_location(self):
        return self.rect.x, self.rect.y
    
    def open_door(self):
        self.open = True

    def change_image(self):
        if self.open:
            self.image = pygame.image.load("assets/door_open.png")
            self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
        else:
            self.image = pygame.image.load("assets/door_closed.png")
            self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
