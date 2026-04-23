import pygame


INTERACT_KEY_P1 = pygame.K_e
INTERACT_KEY_P2 = pygame.K_SLASH


class MovableWall:
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.active = True

    def draw(self, screen: pygame.Surface) -> None:
        if self.active:
            pygame.draw.rect(screen, pygame.Color("#E8832A"), self.rect)


class Lever:
    WIDTH = 16
    HEIGHT = 40
    INTERACT_RANGE = 60

    # cached sprites, loaded once
    _sprite_off = None
    _sprite_on = None

    @classmethod
    def _load_sprites(cls) -> None:
        if cls._sprite_off is not None:
            return
        cls._sprite_off = pygame.image.load("assets/sprites/lever_off.png").convert_alpha()
        cls._sprite_on  = pygame.image.load("assets/sprites/lever_on.png").convert_alpha()

    def __init__(self, x: int, y: int, linked_walls: list) -> None:
        self.rect = pygame.Rect(0, 0, self.WIDTH, self.HEIGHT)
        self.rect.midbottom = (x, y)
        self.activated = False
        self.linked_walls = linked_walls
        self._cooldown = 0.0

    def _apply_to_walls(self) -> None:
        for wall in self.linked_walls:
            wall.active = not self.activated

    def handle_event(self, event: pygame.event.Event, players: list) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (INTERACT_KEY_P1, INTERACT_KEY_P2) and self._cooldown <= 0:
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
        self._load_sprites()
        sprite = self._sprite_on if self.activated else self._sprite_off
        # align sprite's bottom to the rect's midbottom so it sits on the platform
        draw_rect = sprite.get_rect(midbottom=self.rect.midbottom)
        screen.blit(sprite, draw_rect)

        # interaction prompt below the base
        font = pygame.font.SysFont("Arial", 12)
        state_text = "ON" if self.activated else "OFF"
        label = font.render(f"[E/] {state_text}", True, pygame.Color("#FFFFFF"))
        screen.blit(label, (self.rect.centerx - label.get_width() // 2, draw_rect.bottom + 2))