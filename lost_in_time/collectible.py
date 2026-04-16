import math
import random
import pygame


class Particle:
    def __init__(self, x: int, y: int) -> None:
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(80, 260)
        self.velocity = pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
        self.pos = pygame.Vector2(x, y)
        self.lifetime = random.uniform(0.35, 0.7)   # seconds until gone
        self.age = 0.0
        self.radius = random.randint(3, 6)
        # color from a purple/gold palette that matches the collectible
        self.color = random.choice([
            pygame.Color("#69005D"),
            pygame.Color("#A020A0"),
            pygame.Color("#FFD700"),
            pygame.Color("#FF69B4"),
            pygame.Color("#FFFFFF"),
        ])

    def update(self, dt: float) -> bool:
        self.age += dt
        if self.age >= self.lifetime:
            return False
        self.velocity *= max(0.0, 1.0 - dt * 3)
        self.velocity.y -= 60 * dt       # subtle upward drift
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

    def __init__(self, x: int, y: int) -> None:
        self.origin = pygame.Vector2(x, y)   # resting center
        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(0, 0, self.RADIUS * 2, self.RADIUS * 2)
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.active = True
        self._bob_t = 0.0           
        self._particles: list[Particle] = []

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
        for _ in range(self.NUM_PARTICLES):
            self._particles.append(Particle(int(self.pos.x), int(self.pos.y)))

    @property
    def has_live_particles(self) -> bool:
        return len(self._particles) > 0

    def draw(self, screen: pygame.Surface) -> None:
        if self.active:
            pygame.draw.circle(
                screen,
                pygame.Color("#69005D"),
                (int(self.pos.x), int(self.pos.y)),
                self.RADIUS,
            )
        for p in self._particles:
            p.draw(screen)