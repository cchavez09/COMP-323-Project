import random

import pygame


from lost_in_time.button import Button
from lost_in_time.sprites import get_sprite


class Menu:
    # cached padlock sprite, loaded once
    _padlock_sprite = None

    # Mute state persists across menu rebuilds so toggling it once keeps it
    # consistent when moving between title/game_mode/level_select screens
    music_muted = False

    @classmethod
    def _load_padlock(cls) -> pygame.Surface:
        if cls._padlock_sprite is None:
            cls._padlock_sprite = pygame.image.load("assets/sprites/padlock.png").convert_alpha()
        return cls._padlock_sprite


    def __init__(self, screen_width: int, screen_height: int, menu: str, collected_gems: set = None, ip: str = "") -> None:
        # Initialized screen tracking, buttons and fonts for title name and header
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.menu = menu
        self.next_screen = None
        self.buttons = []
        self.ip = ip
        # Small bitmap fonts rendered then scaled up nearest-neighbor = chunky arcade look
        self.title_font = pygame.font.Font(None, 40)
        self.header_font = pygame.font.Font(None, 28)
        self.subtitle_font = pygame.font.Font(None, 20)
        self.background_color = "#A7A7A7"

        # Gems collected across levels 1-3, used to gate level 4
        self.collected_gems = collected_gems if collected_gems is not None else set()
        self.level4_unlocked = len(self.collected_gems) >= 3

        # Era info used to theme each level button on the level select screen
        self._level_era_info = {
            "1": {"era": "Modern",     "color": "#3c5a7a", "top": "#6fa8d6", "accent": "#9cdfff"},
            "2": {"era": "Wild West",  "color": "#7a5020", "top": "#b8864b", "accent": "#e0b070"},
            "3": {"era": "Colosseum",  "color": "#b8a886", "top": "#e8ddc4", "accent": "#f8f0d8"},
            "4": {"era": "Space",      "color": "#141830", "top": "#00bbee", "accent": "#0077cc"},
        }

        # Pre-render the themed background once so stars don't redraw every frame
        self._background = self._build_themed_background()

        # Mute button sits in the top-right corner on all menu screens
        mute_size = 60
        self.mute_btn_rect = pygame.Rect(
            self.screen_width - mute_size - 30,
            30,
            mute_size,
            mute_size,
        )


        # Creation of buttons for each menu screen
        if self.menu == "title":
            self.buttons.append(Button("Play", (self.screen_width // 2, 620), 300, 110, "#8DF78DFF"))
        elif self.menu == "game_mode":
            # Same width for both buttons so they sit symmetrically around center
            mode_btn_w, mode_btn_h = 400, 110
            mode_gap = 80
            left_x  = self.screen_width // 2 - (mode_btn_w + mode_gap) // 2
            right_x = self.screen_width // 2 + (mode_btn_w + mode_gap) // 2
            self.buttons.append(Button("Local",       (left_x,  600), mode_btn_w, mode_btn_h, self.background_color))
            self.buttons.append(Button("Multiplayer", (right_x, 600), mode_btn_w, mode_btn_h, self.background_color))
            # Store centers so hint text below can line up with each button
            self._mode_btn_centers = (left_x, right_x)
            self.buttons.append(Button("Back", (self.screen_width // 2, 900), 300, 100, self.background_color))
        elif self.menu == "level_select":
            # Level tiles spaced evenly, centered across the screen
            btn_w, btn_h = 220, 220
            spacing = 70
            total_w = 4 * btn_w + 3 * spacing
            start_x = self.screen_width // 2 - total_w // 2 + btn_w // 2
            y = 620
            for i, label in enumerate(["1", "2", "3", "4"]):
                x = start_x + i * (btn_w + spacing)
                era = self._level_era_info[label]
                color = era["color"]
                # Level 4 dimmed until all gems collected
                if label == "4" and not self.level4_unlocked:
                    color = "#2a2a2a"
                btn = Button(label, (x, y), btn_w, btn_h, color)
                btn.locked = (label == "4" and not self.level4_unlocked)
                self.buttons.append(btn)
            self.buttons.append(Button("Back", (self.screen_width // 2, 960), 300, 100, self.background_color))
        elif self.menu == "multiplayer":
            self.buttons.append(Button("Host", (self.screen_width // 2 - 150, 600), 220, 100, self.background_color))
            self.buttons.append(Button("Join", (self.screen_width // 2 + 150, 600), 220, 100, self.background_color))
            self.buttons.append(Button("Back", (self.screen_width // 2, 900), 450, 100, self.background_color))
        elif self.menu == "host":
            self.buttons.append(Button("Back", (self.screen_width // 2, 900), 450, 100, self.background_color))
        elif self.menu == "join":
            self.buttons.append(Button("Back", (self.screen_width // 2, 900), 450, 100, self.background_color))



    # build themed cosmic background with stars, nebula and era silhouettes
    def _build_themed_background(self) -> pygame.Surface:
        w, h = self.screen_width, self.screen_height
        surf = pygame.Surface((w, h))

        # Cosmic gradient from midnight blue down to warm violet
        for y in range(h):
            t = y / h
            r = int(10 + t * 55)
            g = int(8  + t * 20)
            b = int(40 + t * 65)
            pygame.draw.line(surf, (r, g, b), (0, y), (w, y))

        # Seeded rng keeps stars and silhouettes consistent between frames
        rng = random.Random(17)

        # Starfield with mixed tints
        for _ in range(450):
            sx = rng.randint(0, w - 1)
            sy = rng.randint(0, h - 1)
            br = rng.randint(130, 255)
            tint = rng.choice([
                (br, br, br),
                (br, br - 20, br - 40),
                (br - 40, br - 20, br),
                (br - 10, br, br - 10),
            ])
            if rng.random() < 0.08:
                pygame.draw.circle(surf, tint, (sx, sy), 2)
            else:
                surf.set_at((sx, sy), tint)

        # Nebula clouds behind the title
        neb = pygame.Surface((w, 500), pygame.SRCALPHA)
        for cx, cy, r, col in [
            (w // 2 - 300, 200, 180, (120, 30, 160, 22)),
            (w // 2 + 280, 240, 220, (40,  60, 180, 24)),
            (w // 2,       140, 260, (60,  20, 120, 18)),
            (w // 2 - 100, 320, 140, (180, 80, 140, 16)),
        ]:
            pygame.draw.circle(neb, col, (cx, cy), r)
        surf.blit(neb, (0, 0))

        # Era silhouettes along the horizon: pyramid, colosseum, saloon, skyscrapers, rocket
        horizon_y = h
        silhouette = (14, 10, 28)

        # Pyramid (far left)
        pygame.draw.polygon(surf, silhouette, [
            (120, horizon_y), (240, horizon_y - 140), (360, horizon_y)
        ])

        # Colosseum arches
        col_x = 500
        pygame.draw.rect(surf, silhouette, (col_x, horizon_y - 120, 220, 120))
        for ax in range(col_x + 15, col_x + 210, 35):
            pygame.draw.rect(surf, (28, 22, 45), (ax, horizon_y - 90, 20, 60))
            pygame.draw.circle(surf, (28, 22, 45), (ax + 10, horizon_y - 90), 10)

        # Saloon / wild west building
        sal_x = 820
        pygame.draw.rect(surf, silhouette, (sal_x, horizon_y - 100, 180, 100))
        pygame.draw.polygon(surf, silhouette, [
            (sal_x - 10, horizon_y - 100),
            (sal_x + 90, horizon_y - 140),
            (sal_x + 190, horizon_y - 100),
        ])

        # Modern skyscraper cluster with lit windows
        sky_x = 1080
        for bx, bw, bh in [(0, 60, 160), (70, 90, 220), (170, 70, 180), (250, 100, 260), (360, 80, 200)]:
            pygame.draw.rect(surf, silhouette, (sky_x + bx, horizon_y - bh, bw, bh))
            for wy in range(horizon_y - bh + 20, horizon_y - 10, 20):
                for wx in range(sky_x + bx + 8, sky_x + bx + bw - 8, 18):
                    if rng.random() < 0.35:
                        pygame.draw.rect(surf, (255, 220, 110), (wx, wy, 4, 8))

        # Rocket / space station (far right)
        rk_x = 1700
        pygame.draw.rect(surf, silhouette, (rk_x, horizon_y - 200, 40, 200))
        pygame.draw.polygon(surf, silhouette, [
            (rk_x, horizon_y - 200),
            (rk_x + 20, horizon_y - 250),
            (rk_x + 40, horizon_y - 200),
        ])
        pygame.draw.polygon(surf, silhouette, [
            (rk_x - 20, horizon_y - 40),
            (rk_x, horizon_y - 100),
            (rk_x, horizon_y - 40),
        ])
        pygame.draw.polygon(surf, silhouette, [
            (rk_x + 40, horizon_y - 40),
            (rk_x + 40, horizon_y - 100),
            (rk_x + 60, horizon_y - 40),
        ])

        return surf


    # draw parchment panel for menu headers
    def _draw_parchment(self, screen: pygame.Surface, rect: pygame.Rect, tint: tuple = (232, 210, 160)) -> None:
        pygame.draw.rect(screen, tint, rect, border_radius=8)
        pygame.draw.rect(screen, (120, 90, 50), rect, 4, border_radius=8)
        # top highlight band
        inner = rect.inflate(-8, -8)
        pygame.draw.line(screen, (180, 150, 100), (inner.left, inner.top), (inner.right, inner.top), 2)


    # draw the mute button with a pixel-art speaker icon, X overlay when muted
    def _draw_mute_button(self, screen: pygame.Surface) -> None:
        rect = self.mute_btn_rect
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        body_color = pygame.Color("#4a2890") if hovered else pygame.Color("#2a1060")
        pygame.draw.rect(screen, body_color, rect, border_radius=8)
        pygame.draw.rect(screen, pygame.Color("#ffd95a"), rect, width=2, border_radius=8)

        # Speaker icon: small trapezoid body with 2 sound waves
        cx, cy = rect.center
        icon_color = pygame.Color("#ffffff")
        # speaker square (the magnet part)
        pygame.draw.rect(screen, icon_color, (cx - 14, cy - 6, 8, 12))
        # speaker cone (trapezoid)
        pygame.draw.polygon(screen, icon_color, [
            (cx - 6, cy - 6),
            (cx + 4, cy - 14),
            (cx + 4, cy + 14),
            (cx - 6, cy + 6),
        ])
        if Menu.music_muted:
            # Red X drawn over the icon when muted
            x_color = pygame.Color("#ff4444")
            pygame.draw.line(screen, x_color, (cx + 2, cy - 12), (cx + 16, cy + 12), 4)
            pygame.draw.line(screen, x_color, (cx + 16, cy - 12), (cx + 2, cy + 12), 4)
        else:
            # Sound waves arcing out from the cone when unmuted
            pygame.draw.arc(screen, icon_color, (cx + 4, cy - 10, 10, 20), -0.8, 0.8, 2)
            pygame.draw.arc(screen, icon_color, (cx + 8, cy - 14, 14, 28), -0.8, 0.8, 2)


    # render text in pixel-art arcade style by scaling up a small render nearest-neighbor
    def _arcade_text(self, text: str, font: pygame.font.Font, color: pygame.Color, scale: int = 4) -> pygame.Surface:
        small = font.render(text, False, color)
        w, h = small.get_size()
        return pygame.transform.scale(small, (w * scale, h * scale))


    # event in relation to button click
    def handle_event(self, event: pygame.event.Event) -> None:
        # Mute button toggles music pause; check before other buttons
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.mute_btn_rect.collidepoint(event.pos):
                Menu.music_muted = not Menu.music_muted
                if Menu.music_muted:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
                return

        for button in self.buttons:
            button.handle_event(event)
            # Locked buttons swallow the click so next_screen stays None
            if button.clicked and getattr(button, "locked", False):
                button.clicked = False
                continue
            # Assign next_screen to allow tranistion between screen menus in relation to
            # button clicks
            if button.clicked:
                if button.text == "Play":
                    self.next_screen = "game_mode"
                if button.text == "Local":
                    self.next_screen = "level_select"
                if button.text == "Back":
                    self.next_screen = "back"
                if button.text == "1":
                    self.next_screen = "game"
                if button.text == "2":
                    self.next_screen = "game2"
                if button.text == "3":
                    self.next_screen = "game3"
                if button.text == "4":
                    self.next_screen = "game4"
                if button.text == "Multiplayer":
                    self.next_screen = "multiplayer"
                if button.text == "Host":
                    self.next_screen = "host"
                if button.text == "Join":
                    self.next_screen = "join"

    # draw a level select tile with era name and lock state
    def _draw_level_tile(self, screen: pygame.Surface, button: Button) -> None:
        era = self._level_era_info.get(button.text)
        rect = button.rect
        locked = getattr(button, "locked", False)

        # Hover lifts the tile up slightly for feedback
        hovered = rect.collidepoint(pygame.mouse.get_pos()) and not locked
        draw_rect = rect.copy()
        if hovered:
            draw_rect.y -= 6

        # Dark tile body
        base_color = pygame.Color("#1a1426") if not locked else pygame.Color("#0f0a18")
        pygame.draw.rect(screen, base_color, draw_rect, border_radius=14)

        # Era-colored accent band across the top
        band_rect = pygame.Rect(draw_rect.x, draw_rect.y, draw_rect.width, 50)
        accent_color = pygame.Color(era["color"]) if not locked else pygame.Color("#333333")
        pygame.draw.rect(screen, accent_color, band_rect, border_radius=14)
        # square off the bottom of the band so only the top corners round
        pygame.draw.rect(screen, accent_color, (band_rect.x, band_rect.bottom - 14, band_rect.width, 14))

        # Outer border
        border_color = pygame.Color(era["accent"]) if not locked else pygame.Color("#555555")
        pygame.draw.rect(screen, border_color, draw_rect, 3, border_radius=14)

        # Level number centered in the tile, nudged up to leave room for era label
        num_color = pygame.Color("#ffffff") if not locked else pygame.Color("#777777")
        num_surf = self._arcade_text(button.text, self.title_font, num_color, scale=3)
        screen.blit(num_surf, num_surf.get_rect(center=(draw_rect.centerx, draw_rect.centery - 10)))

        # Era label below the number
        era_text = era["era"].upper() if not locked else "LOCKED"
        era_color = pygame.Color(era["accent"]) if not locked else pygame.Color("#aa0000")
        era_surf = self._arcade_text(era_text, self.subtitle_font, era_color, scale=2)
        screen.blit(era_surf, era_surf.get_rect(center=(draw_rect.centerx, draw_rect.bottom - 30)))

        # Padlock drawn on top of locked tiles
        if locked:
            padlock = self._load_padlock()
            # Scale the padlock so it fills most of the tile height while keeping aspect ratio
            target_h = int(draw_rect.height * 0.7)
            scale = target_h / padlock.get_height()
            target_w = int(padlock.get_width() * scale)
            scaled = pygame.transform.scale(padlock, (target_w, target_h))
            screen.blit(scaled, scaled.get_rect(center=(draw_rect.centerx, draw_rect.centery - 10)))


    # draw a parchment-style button for non-level-tile buttons
    def _draw_themed_button(self, screen: pygame.Surface, button: Button) -> None:
        rect = button.rect
        hovered = rect.collidepoint(pygame.mouse.get_pos())

        # Hover lifts the button slightly
        draw_rect = rect.copy()
        if hovered:
            draw_rect.y -= 4

        # Retint grey buttons to warm parchment; keep custom colors as-is
        body = pygame.Color(button.rect_color)
        if button.rect_color == self.background_color:
            body = pygame.Color("#d9bf88") if not hovered else pygame.Color("#ead19a")
        pygame.draw.rect(screen, body, draw_rect, border_radius=10)
        pygame.draw.rect(screen, pygame.Color("#5a3a1a"), draw_rect, 4, border_radius=10)
        # top highlight band
        pygame.draw.line(
            screen, pygame.Color("#ffe8b0"),
            (draw_rect.left + 8, draw_rect.top + 5),
            (draw_rect.right - 8, draw_rect.top + 5), 2,
        )

        # Button label in pixel-art arcade style, all caps
        label = self._arcade_text(button.text.upper(), self.header_font, pygame.Color("#1a0e04"), scale=2)
        screen.blit(label, label.get_rect(center=draw_rect.center))


    # draw background
    def draw(self, screen: pygame.Surface) -> None:
        # Re-apply mute state each frame so it sticks even if music was restarted externally
        if Menu.music_muted and pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()

        # Themed cosmic background
        screen.blit(self._background, (0, 0))

        # Title in pixel-art arcade style with shadow + glow, centered on screen center
        title_y = 180
        center_x = self.screen_width // 2
        shadow = self._arcade_text("LOST IN TIME", self.title_font, pygame.Color("#2a1060"), scale=4)
        glow   = self._arcade_text("LOST IN TIME", self.title_font, pygame.Color("#ffd95a"), scale=4)
        title  = self._arcade_text("LOST IN TIME", self.title_font, pygame.Color("#ffffff"), scale=4)
        screen.blit(shadow, shadow.get_rect(center=(center_x + 8, title_y + 8)))
        # glow layer drawn slightly larger by offsetting in 4 directions
        glow_rect = glow.get_rect(center=(center_x, title_y))
        for ox, oy in [(-3, 0), (3, 0), (0, -3), (0, 3)]:
            screen.blit(glow, glow_rect.move(ox, oy))
        screen.blit(title, title.get_rect(center=(center_x, title_y)))

        # menu visuals
        if self.menu == "title":
            # cowboy and roman soldier Play button on both sides
            play_cy = 620
            portrait_offset = 260

            # Cowboy on the left
            cowboy = get_sprite("cowboy", "idle", 0, facing_left=False)
            cowboy_big = pygame.transform.scale(
                cowboy, (cowboy.get_width() * 2, cowboy.get_height() * 2)
            )
            screen.blit(cowboy_big, cowboy_big.get_rect(center=(center_x - portrait_offset, play_cy)))

            # Roman soldier on the right, flipped to face the Play button
            roman = get_sprite("roman", "idle", 0, facing_left=True)
            roman_big = pygame.transform.scale(
                roman, (roman.get_width() * 2, roman.get_height() * 2)
            )
            screen.blit(roman_big, roman_big.get_rect(center=(center_x + portrait_offset, play_cy)))

        elif self.menu == "game_mode":
            # Header parchment panel, centered
            panel_rect = pygame.Rect(0, 0, 900, 120)
            panel_rect.center = (center_x, 400)
            self._draw_parchment(screen, panel_rect)
            header = self._arcade_text("CHOOSE GAME MODE", self.header_font, pygame.Color("#3a1f08"), scale=3)
            screen.blit(header, header.get_rect(center=panel_rect.center))

            # Hint text lined up with each button's center x
            left_x, right_x = self._mode_btn_centers
            local_hint = self._arcade_text("SAME SCREEN, TWO PLAYERS", self.subtitle_font, pygame.Color("#d0c8e8"), scale=2)
            mp_hint    = self._arcade_text("PLAY OVER THE NETWORK", self.subtitle_font, pygame.Color("#d0c8e8"), scale=2)
            screen.blit(local_hint, local_hint.get_rect(center=(left_x,  700)))
            screen.blit(mp_hint,    mp_hint.get_rect(center=(right_x, 700)))

        elif self.menu == "level_select":
            # Header parchment panel, centered
            panel_rect = pygame.Rect(0, 0, 700, 120)
            panel_rect.center = (center_x, 400)
            self._draw_parchment(screen, panel_rect)
            header = self._arcade_text("CHOOSE ERA", self.header_font, pygame.Color("#3a1f08"), scale=3)
            screen.blit(header, header.get_rect(center=panel_rect.center))

        elif self.menu == "host":
            panel_rect = pygame.Rect(0, 0, 900, 200)
            panel_rect.center = (center_x, 400)
            self._draw_parchment(screen, panel_rect)
            header = self._arcade_text("HOSTING", self.header_font, pygame.Color("#3a1f08"), scale=3)
            screen.blit(header, header.get_rect(center=(center_x, 370)))
            ip_surf = self._arcade_text(f"YOUR IP: {self.ip}", self.subtitle_font, pygame.Color("#3a1f08"), scale=2)
            screen.blit(ip_surf, ip_surf.get_rect(center=(center_x, 430)))
            wait_surf = self._arcade_text("WAITING FOR PLAYER TO JOIN...", self.subtitle_font, pygame.Color("#d0c8e8"), scale=2)
            screen.blit(wait_surf, wait_surf.get_rect(center=(center_x, 560)))

        elif self.menu == "join":
            panel_rect = pygame.Rect(0, 0, 900, 200)
            panel_rect.center = (center_x, 400)
            self._draw_parchment(screen, panel_rect)
            header = self._arcade_text("JOIN GAME", self.header_font, pygame.Color("#3a1f08"), scale=3)
            screen.blit(header, header.get_rect(center=(center_x, 370)))
            ip_surf = self._arcade_text(f"ENTER HOST IP: {self.ip}_", self.subtitle_font, pygame.Color("#3a1f08"), scale=2)
            screen.blit(ip_surf, ip_surf.get_rect(center=(center_x, 430)))
            hint_surf = self._arcade_text("PRESS ENTER TO CONNECT", self.subtitle_font, pygame.Color("#d0c8e8"), scale=2)
            screen.blit(hint_surf, hint_surf.get_rect(center=(center_x, 560)))
        

        # Draw buttons: level tiles on level select, parchment buttons everywhere else
        for button in self.buttons:
            if self.menu == "level_select" and button.text in ("1", "2", "3", "4"):
                self._draw_level_tile(screen, button)
            else:
                self._draw_themed_button(screen, button)

        # Gem progress message under the level tiles
        if self.menu == "level_select":
            collected = len(self.collected_gems)
            if self.level4_unlocked:
                msg = "ALL GEMS COLLECTED! THE SPACE ERA IS OPEN."
                color = pygame.Color("#80ff90")
            else:
                msg = f"COLLECT ALL 3 GEMS IN ERAS 1-3 TO UNLOCK THE SPACE ERA  ({collected}/3)"
                color = pygame.Color("#ff9090")
            progress_surf = self._arcade_text(msg, self.subtitle_font, color, scale=2)
            screen.blit(progress_surf, progress_surf.get_rect(center=(center_x, 870)))

        # Mute button drawn last so it sits on top of everything else
        self._draw_mute_button(screen)