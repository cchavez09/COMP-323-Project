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

    def __init__(self, x: int, y: int, controls: dict) -> None:
        self.rect = pygame.Rect(0, 0, self.SIZE, self.SIZE)
        self.pos = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        
        self.health = 1

        self.jump_requested = False
        self.on_ground = True
        # controls passed from game.py to be used in player class for movement
        self.controls = controls
        

    def handle_event(self, event: pygame.event.Event) -> None:
        # Record the request on keydown; update() will only fire it if on_ground is True.
        # Removing the on_ground guard here prevents missed inputs when on_ground is
        # briefly False due to collision timing on the same frame the key is pressed.
        if event.type == pygame.KEYDOWN:
            if event.key == self.controls["jump"]:
                self.jump_requested = True
    
    # apply the jumping boost collectible
    def apply_jump_boost(self) -> None:
        self.JUMP_SPEED = 1200.0

    def _read_horizontal(self) -> float:
        keys = pygame.key.get_pressed()
        x = 0
        if keys[self.controls["left"]]:
            x -= 1
        if keys[self.controls["right"]]:
            x += 1
        return float(x)

    # override input for server authoritatve movement in multiplayer
    def update(self, dt: float, input_override: dict = None) -> None:
        if input_override is not None:
            x = float(input_override.get("x", 0))
            if input_override.get("jump"):
                self.jump_requested = True
        else:
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
        pygame.draw.rect(screen, self.color, self.rect)