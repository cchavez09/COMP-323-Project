import pygame

# Player information stored here for game.py use
class Player:
    # Data from week2 example
    SIZE = 20
    ACCEL = 2400.0
    MAX_SPEED = 520.0
    FRICTION = 15

    GRAVITY = 2200.0
    JUMP_SPEED = 820.0

    def __init__(self, x: int, y: int) -> None:
        self.rect = pygame.Rect(0, 0, self.SIZE, self.SIZE)
        self.pos = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        
        self.health = 1

        self.jump_requested = False
        self.on_ground = True
        

    def handle_event(self, event: pygame.event.Event) -> None:
        # Cannot hold down key to jump repeatedly
        if event.type == pygame.KEYDOWN:
            if event.key in {pygame.K_w, pygame.K_UP} and self.on_ground:
                if self.on_ground:
                    self.jump_requested = True

    def _read_horizontal(self) -> float:
        keys = pygame.key.get_pressed()
        x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            x += 1
        return float(x)

    def update(self, dt: float) -> None:
        x = self._read_horizontal()

        # Horizontal accel; no vertical input (gravity handles Y).
        self.velocity.x += x * self.ACCEL * dt
        if x == 0:
            self.velocity.x -= self.velocity.x * min(1.0, self.FRICTION * dt)
        self.velocity.x = max(-self.MAX_SPEED, min(self.MAX_SPEED, self.velocity.x))

        # Jump is a discrete action.
        if self.jump_requested and self.on_ground:
            self.velocity.y = -self.JUMP_SPEED
            self.on_ground = False
        self.jump_requested = False

        # Gravity.
        self.velocity.y += self.GRAVITY * dt

        self.pos += self.velocity * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))
    
    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, pygame.Color("#FF0000"), self.rect)