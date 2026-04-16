import pygame

from lost_in_time.collectible import Collectible
from lost_in_time.hazard import Hazard, MovingHazard
from lost_in_time.lever import Lever, MovableWall
from lost_in_time.exit_door import ExitDoor
from lost_in_time.pressure_button import PressureButton

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
        # Playfield: left=50, top=150, right=1870, bottom=1030
        # Max jump height ≈ 153 px  (Player SIZE=20)
        #
        # Three-zone layout split by full-height barriers:
        #   Zone L (x=50–620)   – P1 climbs a 4-step zigzag to reach Lever_L
        #   Zone M (x=660–1290) – shared centre; exit door is at the BOTTOM here
        #   Zone R (x=1330–1870)– P2 descends a 3-step zigzag to reach Lever_R
        #
        # Cooperative puzzle:
        #   P1 climbs Zone L → pulls Lever_L → wall_r opens → P2 can leave Zone R
        #   P2 descends Zone R → pulls Lever_R → wall_l opens → P1 can leave Zone L
        #   P2 enters Zone M, steps on the pressure button → exit_gate opens
        #   Both reach the exit door at the bottom of Zone M simultaneously.
        #
        # Zone L upper tier is split into TWO pieces (Upper-L and Upper-R) with a
        # 130-px gap (x=250–380) — players must jump through the gap from Step 3 to
        # land on Upper-R where the lever is.  Upper-L (dead-end) holds the only
        # collectible; reaching it is optional but requires an extra jump back over
        # the gap to pull the lever afterward.

        self.spawn_p1 = (185, 610)   # Zone L start platform surface y=620 → center y=610
        self.spawn_p2 = (1700, 410)  # Zone R start platform surface y=420 → center y=410

        # --- Movable walls (3) ---
        wall_l    = MovableWall(620,  pf.top, 40, pf.bottom - pf.top)  # Zone L/M barrier
        wall_r    = MovableWall(1290, pf.top, 40, pf.bottom - pf.top)  # Zone M/R barrier
        # exit_gate spans y=600–880 (280 px tall) so players can't jump over it from
        # Zone M lower (max jump only reaches y≈727, gate top is at y=600).
        exit_gate = MovableWall(840, 600, 20, 280)
        self.movable_walls = [wall_l, wall_r, exit_gate]

        self.walls = [
            # ── Zone L: four-step zigzag climb (90 px vertical gaps) ──
            pygame.Rect(50,  620, 240, 20),  # P1 start  [x=50–290]
            pygame.Rect(300, 530, 220, 20),  # Step 2    [x=300–520,  90 px up, right]
            pygame.Rect(80,  440, 220, 20),  # Step 3    [x=80–300,   90 px up, left]
            #                                  GAP  x=250–380  ← jump-through gap
            pygame.Rect(50,  350, 200, 20),  # Upper-L   [x=50–250,   90 px up from Step 3]
            pygame.Rect(380, 350, 240, 20),  # Upper-R   [x=380–620, 130 px jump over gap; Lever_L]

            # ── Zone R: three-step zigzag descend (140 px gaps, jumpable going back up) ──
            pygame.Rect(1570, 420, 260, 20), # P2 start  [x=1570–1830]
            pygame.Rect(1330, 560, 270, 20), # Step 1    [x=1330–1600, 140 px down, left]
            pygame.Rect(1570, 700, 260, 20), # Step 2    [x=1570–1830, 140 px down, right]
            pygame.Rect(1330, 840, 350, 20), # Bottom    [x=1330–1680, 140 px down; Lever_R]

            # ── Zone M: two-level centre area ──
            # Mid catches P1 after the long free-fall from Zone L upper (y=350→750)
            pygame.Rect(660,  750, 570, 20), # Zone M mid   [x=660–1230, stepping stone]
            # Lower is where the exit door lives; 130 px below mid (easily jumpable)
            pygame.Rect(660,  880, 630, 20), # Zone M lower [x=660–1290, exit door + button + gate]
        ]

        # --- Hazards ---
        # Full-width ground hazard — spikes across the entire bottom of the level
        # 61 spikes × 30 px = 1830 px, starting at playfield left (x=50)
        self.hazards.add(Hazard(
            (pf.left, pf.bottom - 30),
            color=pygame.Color("#bf616a"),
            count=61, spike_w=30, spike_h=30, direction="up",
        ))
        # Zone R Step 1 surface — spikes on the left end of Step 1 (y=560) punish
        # P2 for landing in the wrong spot when descending from P2 start
        self.hazards.add(Hazard(
            (1345, 530),
            color=pygame.Color("#bf616a"),
            count=3, spike_w=25, spike_h=30, direction="up",
        ))
        # Zone M lower surface — spikes between the exit_gate (x=840) and the
        # pressure button (x=1150), forming a gauntlet P2 must cross after toggling
        self.hazards.add(Hazard(
            (880, 850),
            color=pygame.Color("#bf616a"),
            count=4, spike_w=30, spike_h=30, direction="up",
        ))

        # --- Single collectible: Zone L Upper-L (optional detour) ---
        # Players must climb all four steps, jump to Upper-L to collect it, then
        # jump BACK over the 130-px gap to Upper-R to pull the lever.
        self.collectibles = [
            Collectible(150, 340),  # Upper-L surface y=350 → collectible centre y=340
        ]

        # --- Two levers — each player opens the OTHER player's barrier ---
        self.levers = [
            Lever(480, 350, linked_walls=[wall_r]),   # Zone L Upper-R → P1 opens P2's exit
            Lever(1450, 840, linked_walls=[wall_l]),  # Zone R Bottom  → P2 opens P1's exit
        ]

        # --- Pressure button (toggle): P2 triggers it on entering Zone M from the right ---
        # Placed near the right end of Zone M lower so P2 walks over it naturally.
        # Deactivates exit_gate, allowing both players to reach the exit door.
        self.pressure_buttons = [
            PressureButton(1150, 880, linked_walls=[exit_gate], hold=False),
        ]

        # --- Exit door: bottom of Zone M, left of exit_gate ---
        # P1 (entering from left) can reach it freely.
        # P2 (entering from right) must first step on the button to remove the gate.
        self.exit_door = ExitDoor(750, 880)

    def _build_level3(self) -> None:
        pf = self.playfield
        # Playfield: left=50, top=150, right=1870, bottom=1030
        # Max jump height ≈ 153 px
        #
        # ── The Colosseum ──────────────────────────────────────────────────────────
        # Both players spawn on the ARENA FLOOR.  Tiered platforms rise from each
        # wall getting SHORTER as they go higher (pyramid/tower shape), the opposite
        # of a bowl — so the top tiers are narrow ledges hugging the wall.
        #
        # Cooperative puzzle (3 steps):
        #   1. One player jumps over the central spike pit to the arena column and
        #      pulls Lever_C → opens the center_gate blocking the exit door.
        #      (The collectible is also on the column — bonus for doing the risky jump.)
        #   2. P1 climbs LEFT tiers → pulls Lever_L (on L-T4) → gate_r opens for P2.
        #   3. P2 climbs RIGHT tiers → pulls Lever_R (on R-T4) → gate_l opens for P1.
        #   Both reach the Emperor's Box and touch the exit door simultaneously.

        self.spawn_p1 = (200,  1020)   # left arena floor, clear of spike pit
        self.spawn_p2 = (1720, 1020)   # right arena floor, clear of spike pit

        # --- Movable walls ---
        # Outer gates end flush with Emperor's Box (y=350) so they don't reach
        # into the climbing zone and block players trying to access the tiers.
        gate_l = MovableWall(220, pf.top, 20, 350 - pf.top)   # x=220–240, y=150–350
        gate_r = MovableWall(1680, pf.top, 20, 350 - pf.top)  # x=1680–1700, y=150–350

        # Center gates flank the exit door on both sides, running from the very
        # top of the screen (y=0) down to y=430 so they solidly block lateral
        # movement at Emperor's Box level.  Both are opened by the column lever.
        # Door rect: midtop=(960,350), size 50×80 → x=935–985, y=350–430.
        center_gate_l = MovableWall(910, 0, 25, 430)   # x=910–935, y=0–430 (left of door)
        center_gate_r = MovableWall(985, 0, 25, 430)   # x=985–1010, y=0–430 (right of door)
        self.movable_walls = [gate_l, gate_r, center_gate_l, center_gate_r]

        self.walls = [
            # ── Left tiers: SHORTER going up, all anchored to left wall (x=50) ──
            # Vertical gaps: ground→T1=130 px, T1→T2=T2→T3=T3→T4=140 px (all jumpable)
            pygame.Rect(50,  900, 370, 20),   # L-T1  [x=50–420]
            pygame.Rect(50,  760, 300, 20),   # L-T2  [x=50–350]
            pygame.Rect(50,  620, 230, 20),   # L-T3  [x=50–280]
            pygame.Rect(50,  480, 150, 20),   # L-T4  [x=50–200]  Lever_L at x=100

            # ── Right tiers (mirror, anchored to right wall x=1870) ──
            pygame.Rect(1500, 900, 370, 20),  # R-T1  [x=1500–1870]
            pygame.Rect(1570, 760, 300, 20),  # R-T2  [x=1570–1870]
            pygame.Rect(1640, 620, 230, 20),  # R-T3  [x=1640–1870]
            pygame.Rect(1720, 480, 150, 20),  # R-T4  [x=1720–1870]  Lever_R at x=1800

            # ── Arena column (collectible + lever to open center gate) ──
            pygame.Rect(920, 900, 100, 20),   # Column [x=920–1020]

            # ── Emperor's Box (top-centre, between both outer gates) ──
            pygame.Rect(240, 350, 1440, 20),  # [x=240–1680]  exit door at x=960
        ]

        # --- Hazards ---
        # Central spike pit — must be jumped over to reach the column lever
        self.hazards.add(Hazard(
            (860, pf.bottom - 30),
            color=pygame.Color("#bf616a"),
            count=6, spike_w=30, spike_h=30, direction="up",
        ))

        # Moving hazards on T1, T2, T3 (the three tiers below the top tier T4).
        # Left and right sides start at opposite ends so their timing is offset.
        # Speed increases with height to make higher tiers harder.
        _c = pygame.Color("#bf616a")

        # Moving hazards leave a 30 px safe gap at each wall edge so players can
        # stand near the wall, time the hazard, and jump up to the T4 lever.
        # Left side: min_x=80  (safe zone x=50–79 near left wall)
        # Right side: max_x=1840 (safe zone x=1841–1870 near right wall)

        # T1 (y=900): L starts at safe-zone edge moving right, R starts at right limit moving left
        self.hazards.add(MovingHazard(
            (80, 870), color=_c, count=2, spike_w=25, spike_h=30, direction="up",
            min_x=80, max_x=420, speed=120,
        ))
        self.hazards.add(MovingHazard(
            (1790, 870), color=_c, count=2, spike_w=25, spike_h=30, direction="up",
            min_x=1500, max_x=1840, speed=-120,
        ))

        # T2 (y=760): L starts at right limit moving left, R starts at safe-zone edge moving right
        self.hazards.add(MovingHazard(
            (300, 730), color=_c, count=2, spike_w=25, spike_h=30, direction="up",
            min_x=80, max_x=350, speed=-150,
        ))
        self.hazards.add(MovingHazard(
            (1570, 730), color=_c, count=2, spike_w=25, spike_h=30, direction="up",
            min_x=1570, max_x=1840, speed=150,
        ))

        # T3 (y=620): L starts at safe-zone edge moving right, R starts at right limit moving left
        self.hazards.add(MovingHazard(
            (80, 590), color=_c, count=2, spike_w=25, spike_h=30, direction="up",
            min_x=80, max_x=280, speed=180,
        ))
        self.hazards.add(MovingHazard(
            (1790, 590), color=_c, count=2, spike_w=25, spike_h=30, direction="up",
            min_x=1640, max_x=1840, speed=-180,
        ))

        # --- Single collectible: arena column ---
        # Requires a jump over the spike pit — same risky move needed for Lever_C,
        # so the collectible is a bonus reward for the required column visit.
        self.collectibles = [
            Collectible(970, 890),  # Column surface y=900 → centre y=890
        ]

        # --- Three levers ---
        # L-T4 lever → opens gate_r so P2 can reach Emperor's Box
        # R-T4 lever → opens gate_l so P1 can reach Emperor's Box
        # Column lever → opens center_gate so both can reach the exit door
        self.levers = [
            Lever(100,  480, linked_walls=[gate_r]),       # L-T4
            Lever(1800, 480, linked_walls=[gate_l]),       # R-T4
            Lever(940,  900, linked_walls=[center_gate_l, center_gate_r]),  # Arena column
        ]

        # --- Exit door: Emperor's Box, centre-top ---
        self.exit_door = ExitDoor(960, 350)

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

        for btn in self.pressure_buttons:
            btn.draw(screen)

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