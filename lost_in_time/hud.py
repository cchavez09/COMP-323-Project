import pygame


class HUD:
    def __init__(self, screen_w: int, hud_h: int) -> None:
        self.screen_w = screen_w
        self.hud_h = hud_h
        self.elapsed = 0.0
        self.collected = False
        self._font = pygame.font.SysFont(None, 36)

    def reset(self) -> None:
        self.elapsed = 0.0
        self.collected = False

    def notify_collected(self) -> None:
        self.collected = True

    def update(self, dt: float) -> None:
        self.elapsed += dt

    def draw(self, screen: pygame.Surface) -> None:
        minutes = int(self.elapsed) // 60
        seconds = int(self.elapsed) % 60
        timer_surf = self._font.render(f"Time: {minutes:02d}:{seconds:02d}", True, pygame.Color("#FFFFFF"))
        screen.blit(timer_surf, (20, self.hud_h // 2 - timer_surf.get_height() // 2))

        # circle appears only once picked up
        label_surf = self._font.render("Collectible:", True, pygame.Color("#FFFFFF"))
        lx = self.screen_w // 2 - 80
        ly = self.hud_h // 2 - label_surf.get_height() // 2
        screen.blit(label_surf, (lx, ly))

        if self.collected:
            cx = lx + label_surf.get_width() + 20
            cy = self.hud_h // 2
            pygame.draw.circle(screen, pygame.Color("#69005D"), (cx, cy), 10)