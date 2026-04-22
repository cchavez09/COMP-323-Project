import pygame


class HUD:
    _gem_sprites = None

    @classmethod
    def _load_gem_sprites(cls) -> dict:
        if cls._gem_sprites is not None:
            return cls._gem_sprites
        cls._gem_sprites = {
            "green": pygame.image.load("assets/sprites/gem_green.png").convert_alpha(),
            "red":   pygame.image.load("assets/sprites/gem_red.png").convert_alpha(),
            "blue":  pygame.image.load("assets/sprites/gem_blue.png").convert_alpha(),
        }
        return cls._gem_sprites

    def __init__(self, screen_w: int, hud_h: int) -> None:
        self.screen_w = screen_w
        self.hud_h = hud_h
        self.elapsed = 0.0
        self.collected = False
        self.gem_kind = "green"  
        self._font = pygame.font.SysFont(None, 36)

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

    # which gem kind the HUD should display for the current level
    def set_gem_kind(self, kind: str) -> None:
        self.gem_kind = kind

    def notify_collected(self) -> None:
        self.collected = True

    def update(self, dt: float) -> None:
        self.elapsed += dt

    def handle_event(self, event: pygame.event.Event) -> None:
        self.pause_clicked = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.pause_btn_rect.collidepoint(event.pos):
                self.pause_clicked = True

    def draw(self, screen: pygame.Surface, paused: bool = False) -> None:
        minutes = int(self.elapsed) // 60
        seconds = int(self.elapsed) % 60
        timer_surf = self._font.render(f"Time: {minutes:02d}:{seconds:02d}", True, pygame.Color("#FFFFFF"))
        screen.blit(timer_surf, (20, self.hud_h // 2 - timer_surf.get_height() // 2))

        label_surf = self._font.render("Collectible:", True, pygame.Color("#FFFFFF"))
        lx = self.screen_w // 2 - 80
        ly = self.hud_h // 2 - label_surf.get_height() // 2
        screen.blit(label_surf, (lx, ly))

        # draw the gem next to the label: ghosted if uncollected, full if collected
        sprites = self._load_gem_sprites()
        gem = sprites.get(self.gem_kind, sprites["green"])
        # scale gem to fit the HUD compactly
        target_h = int(self.hud_h * 0.3)
        scale = target_h / gem.get_height()
        target_w = int(gem.get_width() * scale)
        gem_scaled = pygame.transform.smoothscale(gem, (target_w, target_h))
        gx = lx + label_surf.get_width() + 10
        gy = self.hud_h // 2 - target_h // 2

        if self.collected:
            screen.blit(gem_scaled, (gx, gy))
        else:
            # ghosted silhouette so the player knows what to look for
            ghost = gem_scaled.copy()
            ghost.set_alpha(70)
            screen.blit(ghost, (gx, gy))

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