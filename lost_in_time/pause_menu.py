import pygame




class PauseMenu:


    OVERLAY_COLOR = (0, 0, 0, 160)  
    PANEL_COLOR = pygame.Color("#2B2B2B")
    PANEL_BORDER = pygame.Color("#FFD700")
    TITLE_COLOR = pygame.Color("#FFD700")
    BTN_COLOR = pygame.Color("#3D3D3D")
    BTN_HOVER_COLOR = pygame.Color("#555555")
    BTN_TEXT_COLOR = pygame.Color("#FFFFFF")
    BTN_WIDTH = 340
    BTN_HEIGHT = 70
    BTN_GAP = 20


    def __init__(self, screen_w: int, screen_h: int) -> None:
        self.screen_w = screen_w
        self.screen_h = screen_h

        # Small bitmap fonts scaled up nearest-neighbor for arcade pixel look
        self.title_font = pygame.font.Font(None, 24)
        self.btn_font = pygame.font.Font(None, 20)


        # button labels in display order
        self._labels = ["Resume", "Level Select", "Restart", "Quit"]


        # vertical layout
        total_h = len(self._labels) * self.BTN_HEIGHT + (len(self._labels) - 1) * self.BTN_GAP
        panel_padding = 60
        panel_w = self.BTN_WIDTH + panel_padding * 2
        panel_h = 120 + total_h + panel_padding


        self.panel_rect = pygame.Rect(
            (screen_w - panel_w) // 2,
            (screen_h - panel_h) // 2,
            panel_w,
            panel_h,
        )


        # button rects
        btn_x = self.panel_rect.centerx - self.BTN_WIDTH // 2
        btn_start_y = self.panel_rect.top + 130  # below title
        self._btn_rects: list[pygame.Rect] = []
        for i in range(len(self._labels)):
            r = pygame.Rect(btn_x, btn_start_y + i * (self.BTN_HEIGHT + self.BTN_GAP),
                            self.BTN_WIDTH, self.BTN_HEIGHT)
            self._btn_rects.append(r)


        # overlay surface
        self._overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        self._overlay.fill(self.OVERLAY_COLOR)


        # action chosen this frame
        self.action: str | None = None


    # render pixel-art arcade text by scaling up a small render nearest-neighbor
    def _arcade_text(self, text: str, font: pygame.font.Font, color: pygame.Color, scale: int = 2) -> pygame.Surface:
        small = font.render(text, False, color)
        w, h = small.get_size()
        return pygame.transform.scale(small, (w * scale, h * scale))


    def handle_event(self, event: pygame.event.Event) -> None:
        self.action = None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for label, rect in zip(self._labels, self._btn_rects):
                if rect.collidepoint(event.pos):
                    self.action = label.lower().replace(" ", "_")  # e.g. "level_select"


    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self._overlay, (0, 0))


        # panel background
        pygame.draw.rect(screen, self.PANEL_COLOR, self.panel_rect, border_radius=16)
        pygame.draw.rect(screen, self.PANEL_BORDER, self.panel_rect, width=3, border_radius=16)


        # title in pixel-art arcade style
        title_surf = self._arcade_text("PAUSED", self.title_font, self.TITLE_COLOR, scale=4)
        screen.blit(title_surf, (self.panel_rect.centerx - title_surf.get_width() // 2,
                                 self.panel_rect.top + 28))


        # buttons
        mouse_pos = pygame.mouse.get_pos()
        for label, rect in zip(self._labels, self._btn_rects):
            hovered = rect.collidepoint(mouse_pos)
            color = self.BTN_HOVER_COLOR if hovered else self.BTN_COLOR
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, self.PANEL_BORDER, rect, width=2, border_radius=10)
            text_surf = self._arcade_text(label.upper(), self.btn_font, self.BTN_TEXT_COLOR, scale=2)
            screen.blit(text_surf, (rect.centerx - text_surf.get_width() // 2,
                                    rect.centery - text_surf.get_height() // 2))