import pygame


class PressureButton:
    """
    A floor button that activates when any player stands on it.

    Two modes (set via `hold` parameter):
      hold=True  – walls stay open only while a player is on the button (default)
      hold=False – first player contact toggles the walls; stepping off changes nothing
    """

    WIDTH = 50
    HEIGHT = 12

    COLOR_IDLE     = pygame.Color("#CC4400")  # orange-red = not pressed
    COLOR_PRESSED  = pygame.Color("#00CC44")  # green = pressed

    def __init__(self, x: int, y: int, linked_walls: list, hold: bool = True) -> None:
        # x, y = midbottom of the button (sits flat on the ground)
        self.rect = pygame.Rect(0, 0, self.WIDTH, self.HEIGHT)
        self.rect.midbottom = (x, y)
        self.linked_walls = linked_walls
        self.hold = hold
        self.pressed = False
        self._was_pressed = False  # used for toggle-mode edge detection

    def _apply_to_walls(self, open_walls: bool) -> None:
        for wall in self.linked_walls:
            wall.active = not open_walls  # open_walls=True → walls hidden

    def update(self, players: list) -> None:
        currently_pressed = any(player.rect.colliderect(self.rect) for player in players)

        if self.hold:
            # Walls open while button is held down
            self.pressed = currently_pressed
            self._apply_to_walls(self.pressed)
        else:
            # Toggle mode: trigger on the leading edge (first frame of contact)
            if currently_pressed and not self._was_pressed:
                self.pressed = not self.pressed
                self._apply_to_walls(self.pressed)
            self._was_pressed = currently_pressed

    def draw(self, screen: pygame.Surface) -> None:
        color = self.COLOR_PRESSED if self.pressed else self.COLOR_IDLE
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, pygame.Color("#000000"), self.rect, 2)

        # Small indicator light on the button surface
        light_color = pygame.Color("#FFFFFF") if self.pressed else pygame.Color("#550000")
        pygame.draw.circle(screen, light_color, self.rect.center, 4)