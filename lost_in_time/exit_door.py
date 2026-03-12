import pygame


class ExitDoor:
    WIDTH = 50
    HEIGHT = 80

    COLOR_INACTIVE = pygame.Color("#5A3E2B")   # dark brown - waiting for players
    COLOR_PARTIAL  = pygame.Color("#C8A84B")   # gold - one player touching
    COLOR_COMPLETE = pygame.Color("#00FF88")   # green - both players touching

    def __init__(self, x: int, y: int) -> None:
        # x, y = midbottom of the door
        self.rect = pygame.Rect(0, 0, self.WIDTH, self.HEIGHT)
        self.rect.midbottom = (x, y)

        self.p1_touching = False
        self.p2_touching = False
        # Set to True when both players are on the door simultaneously
        self.completed = False

    def update(self, players: list) -> None:
        # Reset touch state each frame
        self.p1_touching = False
        self.p2_touching = False

        for i, player in enumerate(players):
            if self.rect.colliderect(player.rect):
                if i == 0:
                    self.p1_touching = True
                else:
                    self.p2_touching = True

        if self.p1_touching and self.p2_touching:
            self.completed = True

    def draw(self, screen: pygame.Surface) -> None:
        # Choose color based on how many players are touching
        touching_count = self.p1_touching + self.p2_touching
        if touching_count == 2:
            color = self.COLOR_COMPLETE
        elif touching_count == 1:
            color = self.COLOR_PARTIAL
        else:
            color = self.COLOR_INACTIVE

        pygame.draw.rect(screen, color, self.rect)

        # Door frame
        pygame.draw.rect(screen, pygame.Color("#000000"), self.rect, 3)

        # Door knob
        knob_x = self.rect.right - 10
        knob_y = self.rect.centery
        pygame.draw.circle(screen, pygame.Color("#FFD700"), (knob_x, knob_y), 5)

        # Label showing how many players still need to touch
        font = pygame.font.SysFont("Arial", 14, True)
        if not self.completed:
            needed = 2 - touching_count
            label = font.render(f"Need {needed} more", True, pygame.Color("#FFFFFF"))
        else:
            label = font.render("EXIT!", True, pygame.Color("#000000"))
        screen.blit(label, (self.rect.centerx - label.get_width() // 2, self.rect.top - 20))