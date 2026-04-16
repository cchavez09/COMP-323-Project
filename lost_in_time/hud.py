import pygame


class HUD:
    def __init__(self, screen_w: int, hud_h: int) -> None:
        self.screen_w = screen_w
        self.hud_h = hud_h
        self.elapsed = 0.0
        self.collected = False
        self._font = pygame.font.SysFont(None, 36)

        # pause button (top-right corner of HUD)
        self._btn_font = pygame.font.SysFont("Times New Roman", 28, True)
        btn_w, btn_h = 120, 50
        self.pause_btn_rect = pygame.Rect(
            screen_w - btn_w - 20,
            (hud_h - btn_h) // 2,
            btn_w,
            btn_h,
        )
        self.pause_clicked = False

    def reset(self) -> None:
        self.elapsed = 0.0
        self.collected = False

    def notify_collected(self) -> None:
        self.collected = True

    def update(self, dt: float) -> None:
        self.elapsed += dt

    # pause button click is handled separately from player input events since UI element
    def handle_event(self, event: pygame.event.Event) -> None:
        self.pause_clicked = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.pause_btn_rect.collidepoint(event.pos):
                self.pause_clicked = True

    def draw(self, screen: pygame.Surface, paused: bool = False) -> None:
        minutes = int(self.elapsed) // 60 # calculate minutes by integer division
        seconds = int(self.elapsed) % 60 # calculate seconds by modulus to get remainder after minutes
        timer_surf = self._font.render(f"Time: {minutes:02d}:{seconds:02d}", True, pygame.Color("#FFFFFF")) # format time as MM:SS with leading zeros
        screen.blit(timer_surf, (20, self.hud_h // 2 - timer_surf.get_height() // 2)) # draw timer on left side of HUD, vertically centered

        # circle appears only once picked up
        label_surf = self._font.render("Collectible:", True, pygame.Color("#FFFFFF"))
        lx = self.screen_w // 2 - 80
        ly = self.hud_h // 2 - label_surf.get_height() // 2
        screen.blit(label_surf, (lx, ly))

        # only draw the collectible indicator if it's been collected
        if self.collected:
            cx = lx + label_surf.get_width() + 20
            cy = self.hud_h // 2
            pygame.draw.circle(screen, pygame.Color("#69005D"), (cx, cy), 10)

        # pause button
        btn_color = pygame.Color("#555555") if paused else pygame.Color("#3D3D3D")
        if self.pause_btn_rect.collidepoint(pygame.mouse.get_pos()):
            btn_color = pygame.Color("#777777")
        pygame.draw.rect(screen, btn_color, self.pause_btn_rect, border_radius=8)
        pygame.draw.rect(screen, pygame.Color("#FFD700"), self.pause_btn_rect, width=2, border_radius=8)
        label = "RESUME" if paused else "PAUSE"
        btn_label = self._btn_font.render(label, True, pygame.Color("#FFFFFF"))
        screen.blit(btn_label, (
            self.pause_btn_rect.centerx - btn_label.get_width() // 2,
            self.pause_btn_rect.centery - btn_label.get_height() // 2,
        ))