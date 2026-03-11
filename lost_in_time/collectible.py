import pygame

class Collectible:
    RADIUS = 10

    # initializes collectible pos and rect for collision detection, active to check if collected
    def __init__(self, x: int, y: int) -> None:
        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(0, 0, self.RADIUS * 2, self.RADIUS * 2)
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.active = True

    def draw(self, screen: pygame.Surface) -> None:
        if self.active:
            pygame.draw.circle(screen, pygame.Color("#69005D"), (int(self.pos.x), int(self.pos.y)), self.RADIUS)