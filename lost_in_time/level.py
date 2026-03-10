import pygame

# import collectible
from lost_in_time.collectible import Collectible

# Level infromation stored here for game.py use
class Level:
    def __init__(self, level_number: int, screen_w: int, screen_h: int, padding: int, hud_h: int) -> None:
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.padding = padding
        self.hud_h = hud_h
        self.screen_rect = pygame.Rect(0, 0, self.screen_w, self.screen_h)
        self.playfield = pygame.Rect(
            self.padding,
            self.hud_h + self.padding,
            self.screen_w - 2 * self.padding,
            self.screen_h - self.hud_h - 2 * self.padding,
        )

        self.level_number = level_number
        self.walls = []
        self.spawn = pygame.Vector2(0,0)
        # collectible added to ground in center of playfield for test
        self.collectibles = [
            Collectible(self.playfield.centerx, self.playfield.bottom - 10)
        ]

        if self.level_number == 1:
            self.spawn = pygame.Vector2(self.padding + 20, self.screen_h - self.padding - 20)
            self.walls = [
                pygame.Rect(300, 300, 200, 50),
                pygame.Rect(500, 500, 50, 200),
                pygame.Rect(700, 200, 300, 50),
            ]
    
    def draw(self, screen: pygame.Surface) -> None:
        hud_rect = pygame.Rect(0, 0, self.screen_w, self.hud_h)
        
        pygame.draw.rect(screen, pygame.Color("#8FBFFD"), hud_rect)
        pygame.draw.rect(screen, pygame.Color("#868686"), self.playfield) 

        for wall in self.walls:
            pygame.draw.rect(screen, pygame.Color("#A9E9E6"), wall)

        for collectible in self.collectibles:
            collectible.draw(screen)