import math
import random
import pygame


# particle burst matches the gem
_PARTICLE_PALETTES = {
    "green": [
        pygame.Color("#2EDD2E"),
        pygame.Color("#9EFF9E"),
        pygame.Color("#FFD700"),
        pygame.Color("#FFFFFF"),
    ],
    "red": [
        pygame.Color("#FF3030"),
        pygame.Color("#FF9090"),
        pygame.Color("#FFD700"),
        pygame.Color("#FFFFFF"),
    ],
    "blue": [
        pygame.Color("#2E90FF"),
        pygame.Color("#90D0FF"),
        pygame.Color("#FFD700"),
        pygame.Color("#FFFFFF"),
    ],
}


class Particle:
    def __init__(self, x: int, y: int, palette: list) -> None:
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(80, 260)
        self.velocity = pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
        self.pos = pygame.Vector2(x, y)
        self.lifetime = random.uniform(0.35, 0.7)
        self.age = 0.0
        self.radius = random.randint(3, 6)
        self.color = random.choice(palette)

    def update(self, dt: float) -> bool:
        self.age += dt
        if self.age >= self.lifetime:
            return False
        self.velocity *= max(0.0, 1.0 - dt * 3)
        self.velocity.y -= 60 * dt
        self.pos += self.velocity * dt
        return True

    def draw(self, screen: pygame.Surface) -> None:
        alpha = max(0, int(255 * (1.0 - self.age / self.lifetime)))
        surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        color_with_alpha = (*self.color[:3], alpha)
        pygame.draw.circle(surf, color_with_alpha, (self.radius, self.radius), self.radius)
        screen.blit(surf, (int(self.pos.x) - self.radius, int(self.pos.y) - self.radius))


class Collectible:
    RADIUS = 10
    BOB_AMPLITUDE = 5
    BOB_SPEED = 2.5
    NUM_PARTICLES = 22

    # cached gem sprites, loaded once
    _sprites = None

    @classmethod
    def _load_sprites(cls) -> dict:
        if cls._sprites is not None:
            return cls._sprites
        cls._sprites = {
            "green": pygame.image.load("assets/sprites/gem_green.png").convert_alpha(),
            "red":   pygame.image.load("assets/sprites/gem_red.png").convert_alpha(),
            "blue":  pygame.image.load("assets/sprites/gem_blue.png").convert_alpha(),
        }
        return cls._sprites

    def __init__(self, x: int, y: int, kind: str = "green") -> None:
        self.origin = pygame.Vector2(x, y)
        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(0, 0, self.RADIUS * 2, self.RADIUS * 2)
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.active = True
        self.kind = kind
        self._bob_t = 0.0
        self._particles: list = []

    def update(self, dt: float) -> None:
        if self.active:
            self._bob_t += dt
            offset = math.sin(self._bob_t * self.BOB_SPEED) * self.BOB_AMPLITUDE
            self.pos.y = self.origin.y + offset
            self.rect.center = (int(self.pos.x), int(self.pos.y))
        else:
            self._particles = [p for p in self._particles if p.update(dt)]

    def collect(self) -> None:
        self.active = False
        palette = _PARTICLE_PALETTES.get(self.kind, _PARTICLE_PALETTES["green"])
        for _ in range(self.NUM_PARTICLES):
            self._particles.append(Particle(int(self.pos.x), int(self.pos.y), palette))

    @property
    def has_live_particles(self) -> bool:
        return len(self._particles) > 0

    def draw(self, screen: pygame.Surface) -> None:
        if self.active:
            sprites = self._load_sprites()
            gem = sprites.get(self.kind, sprites["green"])
            draw_rect = gem.get_rect(center=(int(self.pos.x), int(self.pos.y)))
            screen.blit(gem, draw_rect)
        for p in self._particles:
            p.draw(screen)