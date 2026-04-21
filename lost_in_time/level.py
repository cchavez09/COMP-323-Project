import pygame

from lost_in_time.collectible import Collectible
from lost_in_time.hazard import Hazard, MovingHazard
from lost_in_time.lever import Lever, MovableWall
from lost_in_time.exit_door import ExitDoor
from lost_in_time.pressure_button import PressureButton
from lost_in_time import sprites


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
        self.pressure_buttons = []
        self.exit_door = None

        # Default spawn positions (bottom corners); _build methods may override these
        self.spawn_p1 = (self.playfield.left + 20, self.playfield.bottom - 20)
        self.spawn_p2 = (self.playfield.right - 20, self.playfield.bottom - 20)

        # cache themed background once per level
        self._background = sprites.get_background(self.level_number, self.screen_w, self.screen_h)

        if self.level_number == 1:
            self._build_level1()
        elif self.level_number == 2:
            self._build_level2()
        elif self.level_number == 3:
            self._build_level3()

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

        # --- Hazard under the right cage platform (x=1100–1350, ground level) ---
        # 6 upward spikes spanning x=1115–1295, sitting on the ground at y=1000
        hz = Hazard(
            (1115, pf.bottom - 30),
            color=pygame.Color("#bf616a"),
            count=8,
            spike_w=30,
            spike_h=30,
            direction="up",
        )
        self.hazards.add(hz)

        # --- Collectible on top of Step 1 (center of platform) ---
        self.collectibles = [
            Collectible(175, 910)   # radius=10, so center sits 10 px above y=920 surface
        ]

        # --- Lever (player 1 activates it to open the mid-wall and free player 2) ---
        # Sits on the left end of the top platform; interact with E (P1) or / (P2)
        self.levers = [
            Lever(250, 480, linked_walls=[mid_wall])
        ]

        # --- Exit door (top platform, right end — both players must touch simultaneously) ---
        self.exit_door = ExitDoor(700, 480)

    def _build_level2(self) -> None:
        pf = self.playfield

        self.spawn_p1 = (185, 610)
        self.spawn_p2 = (1700, 410)

        wall_l    = MovableWall(620,  pf.top, 40, pf.bottom - pf.top)
        wall_r    = MovableWall(1290, pf.top, 40, pf.bottom - pf.top)
        exit_gate = MovableWall(840, 600, 20, 280)
        self.movable_walls = [wall_l, wall_r, exit_gate]

        self.walls = [
            pygame.Rect(50,  620, 240, 20),
            pygame.Rect(300, 530, 220, 20),
            pygame.Rect(80,  440, 220, 20),
            pygame.Rect(50,  350, 200, 20),
            pygame.Rect(380, 350, 240, 20),

            pygame.Rect(1570, 420, 260, 20),
            pygame.Rect(1330, 560, 270, 20),
            pygame.Rect(1570, 700, 260, 20),
            pygame.Rect(1330, 840, 350, 20),

            pygame.Rect(660,  750, 570, 20),
            pygame.Rect(660,  880, 630, 20),
        ]

        self.hazards.add(Hazard(
            (pf.left, pf.bottom - 30),
            color=pygame.Color("#bf616a"),
            count=61, spike_w=30, spike_h=30, direction="up",
        ))
        self.hazards.add(Hazard(
            (1345, 530),
            color=pygame.Color("#bf616a"),
            count=3, spike_w=25, spike_h=30, direction="up",
        ))
        self.hazards.add(Hazard(
            (880, 850),
            color=pygame.Color("#bf616a"),
            count=4, spike_w=30, spike_h=30, direction="up",
        ))

        self.collectibles = [
            Collectible(150, 340),
        ]

        self.levers = [
            Lever(480, 350, linked_walls=[wall_r]),
            Lever(1450, 840, linked_walls=[wall_l]),
        ]

        self.pressure_buttons = [
            PressureButton(1150, 880, linked_walls=[exit_gate], hold=False),
        ]

        self.exit_door = ExitDoor(750, 880)

    def _build_level3(self) -> None:
        pf = self.playfield

        self.spawn_p1 = (200,  1020)
        self.spawn_p2 = (1720, 1020)

        gate_l = MovableWall(220, pf.top, 20, 350 - pf.top)
        gate_r = MovableWall(1680, pf.top, 20, 350 - pf.top)
        center_gate_l = MovableWall(910, 0, 25, 430)
        center_gate_r = MovableWall(985, 0, 25, 430)
        self.movable_walls = [gate_l, gate_r, center_gate_l, center_gate_r]

        self.walls = [
            pygame.Rect(50,  900, 370, 20),
            pygame.Rect(50,  760, 300, 20),
            pygame.Rect(50,  620, 230, 20),
            pygame.Rect(50,  480, 150, 20),

            pygame.Rect(1500, 900, 370, 20),
            pygame.Rect(1570, 760, 300, 20),
            pygame.Rect(1640, 620, 230, 20),
            pygame.Rect(1720, 480, 150, 20),

            pygame.Rect(920, 900, 100, 20),

            pygame.Rect(240, 350, 1440, 20),
        ]

        self.hazards.add(Hazard(
            (860, pf.bottom - 30),
            color=pygame.Color("#bf616a"),
            count=6, spike_w=30, spike_h=30, direction="up",
        ))

        _c = pygame.Color("#bf616a")

        self.hazards.add(MovingHazard(
            (80, 870), color=_c, count=2, spike_w=25, spike_h=30, direction="up",
            min_x=80, max_x=420, speed=120,
        ))
        self.hazards.add(MovingHazard(
            (1790, 870), color=_c, count=2, spike_w=25, spike_h=30, direction="up",
            min_x=1500, max_x=1840, speed=-120,
        ))

        self.hazards.add(MovingHazard(
            (300, 730), color=_c, count=2, spike_w=25, spike_h=30, direction="up",
            min_x=80, max_x=350, speed=-150,
        ))
        self.hazards.add(MovingHazard(
            (1570, 730), color=_c, count=2, spike_w=25, spike_h=30, direction="up",
            min_x=1570, max_x=1840, speed=150,
        ))

        self.hazards.add(MovingHazard(
            (80, 590), color=_c, count=2, spike_w=25, spike_h=30, direction="up",
            min_x=80, max_x=280, speed=180,
        ))
        self.hazards.add(MovingHazard(
            (1790, 590), color=_c, count=2, spike_w=25, spike_h=30, direction="up",
            min_x=1640, max_x=1840, speed=-180,
        ))

        self.collectibles = [
            Collectible(970, 890),
        ]

        self.levers = [
            Lever(100,  480, linked_walls=[gate_r]),
            Lever(1800, 480, linked_walls=[gate_l]),
            Lever(940,  900, linked_walls=[center_gate_l, center_gate_r]),
        ]

        self.exit_door = ExitDoor(960, 350)

    def draw(self, screen: pygame.Surface) -> None:
        # themed background
        screen.blit(self._background, (0, 0))

        # HUD backing
        hud_rect = pygame.Rect(0, 0, self.screen_w, self.hud_h)
        pygame.draw.rect(screen, pygame.Color("#2a3040"), hud_rect)

        # playfield frame
        pygame.draw.rect(screen, pygame.Color("#ffffff"), self.playfield, 2)

        for wall in self.walls:
            sprites.draw_themed_platform(screen, wall, self.level_number)

        for mw in self.movable_walls:
            if mw.active:
                sprites.draw_themed_wall(screen, mw.rect, self.level_number)

        for lever in self.levers:
            lever.draw(screen)

        for btn in self.pressure_buttons:
            btn.draw(screen)

        if self.exit_door:
            self.exit_door.draw(screen)

        for collectible in self.collectibles:
            collectible.draw(screen)

        # try themed hazard art; fall back to default spikes otherwise
        for hazard in self.hazards:
            if sprites.draw_themed_hazard(screen, hazard, self.level_number):
                continue
            for i in range(hazard.count):
                if hazard.direction == "up":
                    bx = hazard.rect.x + i * hazard.spike_w
                    by = hazard.rect.y
                    pts = [(bx, by + hazard.spike_h),
                           (bx + hazard.spike_w // 2, by),
                           (bx + hazard.spike_w, by + hazard.spike_h)]
                elif hazard.direction == "down":
                    bx = hazard.rect.x + i * hazard.spike_w
                    by = hazard.rect.y
                    pts = [(bx, by),
                           (bx + hazard.spike_w // 2, by + hazard.spike_h),
                           (bx + hazard.spike_w, by)]
                pygame.draw.polygon(screen, hazard.color, pts)
                pygame.draw.polygon(screen, pygame.Color("#000000"), pts, 2)