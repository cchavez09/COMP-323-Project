import pygame


class ExitDoor:
    WIDTH = 50
    HEIGHT = 80

    # 4 frames, ~0.4s per full cycle
    FRAME_COUNT = 4
    FRAME_MS = 100   # 100ms per frame = 400ms total cycle

    # cached spritesheet, loaded once
    _frames = None

    @classmethod
    def _load_frames(cls) -> list:
        if cls._frames is not None:
            return cls._frames
        sheet = pygame.image.load("assets/sprites/portal.png").convert_alpha()
        frame_w = sheet.get_width() // cls.FRAME_COUNT
        frame_h = sheet.get_height()
        # scale each frame so the portal is roughly 1.4x the collision box
        target_h = int(cls.HEIGHT * 1.4)
        target_w = int(frame_w * (target_h / frame_h))
        cls._frames = []
        for i in range(cls.FRAME_COUNT):
            frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), (i * frame_w, 0, frame_w, frame_h))
            frame = pygame.transform.scale(frame, (target_w, target_h))
            cls._frames.append(frame)
        return cls._frames

    def __init__(self, x: int, y: int) -> None:
        self.rect = pygame.Rect(0, 0, self.WIDTH, self.HEIGHT)
        self.rect.midbottom = (x, y)

        self.p1_touching = False
        self.p2_touching = False
        self.completed = False

    def update(self, players: list) -> None:
        self.p1_touching = False
        self.p2_touching = False

        for i, player in enumerate(players):
            if self.rect.colliderect(player.rect):
                if i == 0:
                    self.p1_touching = True
                else:
                    self.p2_touching = True

        if self.p1_touching and self.p2_touching:
            self.completed = True

    def draw(self, screen: pygame.Surface) -> None:
        frames = self._load_frames()
        # pick frame based on elapsed time
        frame_idx = (pygame.time.get_ticks() // self.FRAME_MS) % self.FRAME_COUNT
        sprite = frames[frame_idx]

        # tint the portal based on touch state: inactive = dim, partial = normal, complete = bright
        touching_count = self.p1_touching + self.p2_touching
        if touching_count == 2:
            tinted = sprite.copy()
            # bright green glow overlay when complete
            glow = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
            glow.fill((100, 255, 160, 80))
            tinted.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            sprite = tinted
        elif touching_count == 0:
            # darken when no players near
            tinted = sprite.copy()
            dark = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
            dark.fill((0, 0, 0, 90))
            tinted.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            sprite = tinted

        # center sprite on collision rect's midbottom so it stands on the same ground
        draw_rect = sprite.get_rect(midbottom=self.rect.midbottom)
        screen.blit(sprite, draw_rect)

        font = pygame.font.SysFont("Arial", 14, True)
        if not self.completed:
            needed = 2 - touching_count
            label = font.render(f"Need {needed} more", True, pygame.Color("#FFFFFF"))
        else:
            label = font.render("EXIT!", True, pygame.Color("#FFFF00"))
        screen.blit(label, (self.rect.centerx - label.get_width() // 2, draw_rect.top - 20))