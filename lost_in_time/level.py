import pygame

from lost_in_time.collectible import Collectible
from lost_in_time.hazard import Hazard
from lost_in_time.lever import Lever, MovableWall
from lost_in_time.exit_door import ExitDoor

# Level information stored here for game.py use
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
        self.walls = []              # static solid walls
        self.movable_walls = []      # MovableWall instances (lever/button controlled)
        self.hazards = pygame.sprite.Group()
        self.collectibles = []
        self.levers = []
        self.exit_door = None

        if self.level_number == 1:
            self._build_level1()

    def _build_level1(self) -> None:
        pf = self.playfield
        # Playfield: left=50, top=150, right=1870, bottom=1030
        # Max jump height ≈ 153 px  (JUMP_SPEED=820, GRAVITY=2200)
        # Platforms are spaced ~130 px apart vertically so each step is reachable

        # --- Movable wall: the central divider that cages player 2 ---
        # Spans x=940–980, y=480–1030. Starts at the top platform level so
        # neither player can cross until the lever is pulled.
        mid_wall = MovableWall(940, 480, 40, pf.bottom - 480)
        self.movable_walls = [mid_wall]

        self.walls = [
            # Box ceiling — seals the top of player 2's cage
            # Connects to the top of mid_wall; together they create an enclosed right-side box
            pygame.Rect(980, 480, pf.right - 980, 20),

            # ── Left-side climbing platforms (~110 px vertical gaps, easily jumpable) ──
            # Staggered left/right so the player walks a zigzag path upward
            pygame.Rect(pf.left,  920, 250, 20),   # Step 1  (gap from ground: 110 px)
            pygame.Rect(350,      810, 250, 20),   # Step 2  (gap: 110 px, staggered right)
            pygame.Rect(pf.left,  700, 250, 20),   # Step 3  (gap: 110 px)
            pygame.Rect(350,      590, 250, 20),   # Step 4  (gap: 110 px, staggered right)

            # Top platform split into two pieces with a 120 px gap (x=380–500) above Step 4.
            # Players jump through the gap to land on top; lever is on the left piece,
            # exit door is on the right piece.
            pygame.Rect(pf.left, 480, 330, 20),   # Step 5-left  (x=50–380)  lever here
            pygame.Rect(500,     480, 420, 20),   # Step 5-right (x=500–920) exit door here

            # ── Right-side platform inside the cage (gives player 2 something to do while waiting) ──
            pygame.Rect(1100, 920, 250, 20),
        ]

        # --- Lever (player 1 activates it to open the mid-wall and free player 2) ---
        # Sits on the left end of the top platform; interact with E (P1) or / (P2)
        self.levers = [
            Lever(250, 480, linked_walls=[mid_wall])
        ]

        # --- Exit door (top platform, right end — both players must touch simultaneously) ---
        self.exit_door = ExitDoor(700, 480)

    def draw(self, screen: pygame.Surface) -> None:
        hud_rect = pygame.Rect(0, 0, self.screen_w, self.hud_h)
        pygame.draw.rect(screen, pygame.Color("#8FBFFD"), hud_rect)
        pygame.draw.rect(screen, pygame.Color("#868686"), self.playfield)

        for wall in self.walls:
            pygame.draw.rect(screen, pygame.Color("#A9E9E6"), wall)

        for mw in self.movable_walls:
            mw.draw(screen)

        for lever in self.levers:
            lever.draw(screen)

        if self.exit_door:
            self.exit_door.draw(screen)

        for collectible in self.collectibles:
            collectible.draw(screen)

        for hazard in self.hazards:
            for i in range(hazard.count):
                if hazard.direction == "up":
                    bx = hazard.rect.x + i * hazard.spike_w
                    by = hazard.rect.y
                    pts = [(bx, by + hazard.spike_h), (bx + hazard.spike_w // 2, by), (bx + hazard.spike_w, by + hazard.spike_h)]
                elif hazard.direction == "down":
                    bx = hazard.rect.x + i * hazard.spike_w
                    by = hazard.rect.y
                    pts = [(bx, by), (bx + hazard.spike_w // 2, by + hazard.spike_h), (bx + hazard.spike_w, by)]
                pygame.draw.polygon(screen, hazard.color, pts)
                pygame.draw.polygon(screen, pygame.Color("#000000"), pts, 2)