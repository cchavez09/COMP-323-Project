import pygame


# Interact keys - P1 uses E, P2 uses / (separate from movement controls)
INTERACT_KEY_P1 = pygame.K_e
INTERACT_KEY_P2 = pygame.K_SLASH


class MovableWall:
    """A wall that can be shown or hidden by a Lever or PressureButton."""

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.active = True  # True = wall is solid/visible, False = wall is removed/hidden

    def draw(self, screen: pygame.Surface) -> None:
        if self.active:
            pygame.draw.rect(screen, pygame.Color("#E8832A"), self.rect)


class Lever:
    WIDTH = 16
    HEIGHT = 40
    INTERACT_RANGE = 60  # pixels from lever center a player must be within

    COLOR_OFF = pygame.Color("#8B0000")   # dark red handle = off
    COLOR_ON  = pygame.Color("#00CC44")   # green handle = on
    BASE_COLOR = pygame.Color("#555555")

    def __init__(self, x: int, y: int, linked_walls: list) -> None:
        # x, y = midbottom of the lever base
        self.rect = pygame.Rect(0, 0, self.WIDTH, self.HEIGHT)
        self.rect.midbottom = (x, y)
        self.activated = False
        # List of MovableWall objects this lever controls
        self.linked_walls = linked_walls
        self._cooldown = 0.0  # prevents instant re-toggling

    def _apply_to_walls(self) -> None:
        for wall in self.linked_walls:
            wall.active = not self.activated  # activated lever = walls hidden

    def handle_event(self, event: pygame.event.Event, players: list) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (INTERACT_KEY_P1, INTERACT_KEY_P2) and self._cooldown <= 0:
                # Check if any player is close enough to interact
                for player in players:
                    dist = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(player.rect.center))
                    if dist <= self.INTERACT_RANGE:
                        self.activated = not self.activated
                        self._apply_to_walls()
                        self._cooldown = 0.3
                        break

    def update(self, dt: float) -> None:
        if self._cooldown > 0:
            self._cooldown -= dt

    def draw(self, screen: pygame.Surface) -> None:
        # Draw base box
        pygame.draw.rect(screen, self.BASE_COLOR, self.rect)
        pygame.draw.rect(screen, pygame.Color("#000000"), self.rect, 2)

        # Draw handle - tilts left (off) or right (on)
        cx = self.rect.centerx
        base_y = self.rect.top + 8
        if self.activated:
            tip = (cx + 12, base_y - 16)
        else:
            tip = (cx - 12, base_y - 16)
        handle_color = self.COLOR_ON if self.activated else self.COLOR_OFF
        pygame.draw.line(screen, handle_color, (cx, base_y), tip, 5)
        pygame.draw.circle(screen, handle_color, tip, 5)

        # Label
        font = pygame.font.SysFont("Arial", 12)
        state_text = "ON" if self.activated else "OFF"
        label = font.render(f"[E/] {state_text}", True, pygame.Color("#FFFFFF"))
        screen.blit(label, (self.rect.centerx - label.get_width() // 2, self.rect.bottom + 4))