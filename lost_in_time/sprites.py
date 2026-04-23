import random
import pygame


# Transparent pixel in sprite grids
_T = (0, 0, 0, 0)

# Each palette maps a single ASCII char (used in the grids below) to a color
COWBOY_PALETTE = {
    'o': pygame.Color("#1a0a00"),   # outline
    'h': pygame.Color("#6b4423"),   # hat
    'H': pygame.Color("#4a2f18"),   # hat band
    's': pygame.Color("#e0a878"),   # skin
    'S': pygame.Color("#b07848"),   # skin shadow
    'b': pygame.Color("#c0392b"),   # bandana
    't': pygame.Color("#2c5f8d"),   # shirt
    'v': pygame.Color("#5a3a20"),   # vest
    'p': pygame.Color("#1e3a5f"),   # pants
    'B': pygame.Color("#3a1f10"),   # boots
    'k': pygame.Color("#d4a017"),   # belt buckle
}

ROMAN_PALETTE = {
    'o': pygame.Color("#0a0a0a"),   # outline
    'P': pygame.Color("#b01020"),   # plume
    'p': pygame.Color("#701018"),   # plume shadow
    'h': pygame.Color("#c9a227"),   # helmet
    'H': pygame.Color("#8a6a18"),   # helmet shadow
    's': pygame.Color("#e8b898"),   # skin
    'S': pygame.Color("#a87858"),   # skin shadow
    't': pygame.Color("#c0392b"),   # tunic
    'T': pygame.Color("#801f18"),   # tunic shadow
    'a': pygame.Color("#d4b040"),   # armor
    'A': pygame.Color("#806018"),   # armor shadow
    'b': pygame.Color("#5a3a20"),   # belt
    'B': pygame.Color("#3a1f10"),   # sandals
}


def _draw_pixels(surf: pygame.Surface, grid: list, palette: dict) -> None:
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch == '.' or ch == ' ':
                continue
            color = palette.get(ch)
            if color is None:
                continue
            if x < surf.get_width() and y < surf.get_height():
                surf.set_at((x, y), color)


def _scale(surf: pygame.Surface, factor: int) -> pygame.Surface:
    w, h = surf.get_size()
    return pygame.transform.scale(surf, (w * factor, h * factor))


# Cowboy sprite grids (24x32, faces right)
COWBOY_IDLE = [
    "........................",
    "........................",
    "........ooooooo.........",
    ".......ohhhhhhho........",
    "......ohhhhhhhhho.......",
    "......oHHHHHHHHHo.......",
    "....ooohhhhhhhhhooo.....",
    "...ohhhhhhhhhhhhhhho....",
    "...ooooooooooooooooo....",
    "........osssssso........",
    ".......ossssssso........",
    ".......os.oo.oso........",
    ".......osssssso.........",
    ".......obbbbbbo.........",
    "......obbbbbbbbo........",
    "......obbbbbbbbo........",
    "......ovvttttvvo........",
    ".....ovvvttttvvvo.......",
    "....osvvvttttvvvso......",
    "....osvvvttttvvvso......",
    ".....ovvvttttvvvo.......",
    ".....ovvvttttvvvo.......",
    ".....obbbkkkkbbbo.......",
    "......opppppppo.........",
    "......opppppppo.........",
    "......opppppppo.........",
    "......opp.oopppo........",
    "......opp.opppo.........",
    "......opp.opppo.........",
    ".....oBBBo.oBBBo........",
    "....oBBBBo.oBBBBo.......",
    "....ooooo...ooooo.......",
]

# Walk A: right leg raised
COWBOY_WALK_A = [
    "........................",
    "........................",
    "........ooooooo.........",
    ".......ohhhhhhho........",
    "......ohhhhhhhhho.......",
    "......oHHHHHHHHHo.......",
    "....ooohhhhhhhhhooo.....",
    "...ohhhhhhhhhhhhhhho....",
    "...ooooooooooooooooo....",
    "........osssssso........",
    ".......ossssssso........",
    ".......os.oo.oso........",
    ".......osssssso.........",
    "......obbbbbbbbo........",
    "......obbbbbbbbo........",
    ".....osvvttttvvso.......",
    "....ossvvttttvvvo.......",
    "....osssvttttvvvo.......",
    ".....ovvttttvvvso.......",
    ".....ovvttttvvvso.......",
    "......ovttttvvo.........",
    "......obbbkkkkbbbo......",
    ".......opppppppo........",
    ".......opppppppo........",
    "........opppppo.........",
    ".......op..oppo.........",
    "......op....oppo........",
    ".....oppo....ooo........",
    "....opppo.......opppo...",
    "....oBBBo......oBBBBo...",
    "...oBBBBo......oBBBBBo..",
    "...ooooo........ooooo...",
]

# Walk B: left leg raised (mirror of A)
COWBOY_WALK_B = [
    "........................",
    "........................",
    "........ooooooo.........",
    ".......ohhhhhhho........",
    "......ohhhhhhhhho.......",
    "......oHHHHHHHHHo.......",
    "....ooohhhhhhhhhooo.....",
    "...ohhhhhhhhhhhhhhho....",
    "...ooooooooooooooooo....",
    "........osssssso........",
    ".......ossssssso........",
    ".......os.oo.oso........",
    ".......osssssso.........",
    "......obbbbbbbbo........",
    "......obbbbbbbbo........",
    ".......ovvttttvvso......",
    "......ovvvttttvvsso.....",
    "......ovvvttttvvsso.....",
    ".......ovvttttvvso......",
    ".......ovvttttvvso......",
    "........ovttttvo........",
    "......obbbkkkkbbbo......",
    ".......opppppppo........",
    ".......opppppppo........",
    "........opppppo.........",
    ".........oppo.op........",
    "........oppo..opo.......",
    "........ooo..oppo.......",
    "...opppo.......opppo....",
    "...oBBBBo......oBBBo....",
    "..oBBBBBo......oBBBBo...",
    "..ooooo.........ooooo...",
]

# Jump: arms up, legs tucked
COWBOY_JUMP = [
    "........................",
    "........ooooooo.........",
    ".......ohhhhhhho........",
    "......ohhhhhhhhho.......",
    "......oHHHHHHHHHo.......",
    "....ooohhhhhhhhhooo.....",
    "...ohhhhhhhhhhhhhhho....",
    "...ooooooooooooooooo....",
    "........osssssso........",
    ".......ossssssso........",
    ".......os.oo.oso........",
    ".......osssssso.........",
    "......obbbbbbbbo........",
    "....osbbbbbbbbbbso......",
    "...ossobbbbbbbbobsso....",
    "...osvvttttttvvso.......",
    "....ovvttttttvvo........",
    "....ovvttttttvvo........",
    ".....ovvvttttvvo........",
    ".....obbkkkkbbbo........",
    ".....oppppppppo.........",
    "....opppppppppo.........",
    "....oppo....oppo........",
    "....oBBBo..oBBBo........",
    "....ooooo..ooooo........",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
]

# Roman soldier sprite grids (24x32, faces right)
ROMAN_IDLE = [
    "........................",
    "...........oo...........",
    "..........oPPo..........",
    ".........oPPPPo.........",
    "........oPpPpPPo........",
    "........oPpPpPpPo.......",
    "........oppppppppo......",
    ".......ohhhhhhhhhho.....",
    "......ohhHHHHHHHHhho....",
    "......ohHhhhhhhhhHho....",
    "......oHhsssssssshHo....",
    "......oHhsSoosooSshHo...",
    "......oHhssssssshho.....",
    ".......ohssssssho.......",
    "........ossssso.........",
    ".......oaaaaaaao........",
    "......oaAAAAAAAAAao.....",
    "....osaAttttttttAaso....",
    "....osaAttttttttAaso....",
    ".....oaAtttttttAAao.....",
    ".....oaAAAAAAAAAAAao....",
    "......obbbbbbbbbbo......",
    "......ottottottoTTo.....",
    "......ottottottoTTo.....",
    "......ottottottoTTo.....",
    ".......osso.ossso.......",
    ".......osso.ossso.......",
    ".......osso.ossso.......",
    "......obbbo.obbbo.......",
    "......oBBBo.oBBBo.......",
    ".....oBBBBo.oBBBBo......",
    ".....ooooo...ooooo......",
]

# Walk A: right leg forward
ROMAN_WALK_A = [
    "........................",
    "...........oo...........",
    "..........oPPo..........",
    ".........oPPPPo.........",
    "........oPpPpPPo........",
    "........oPpPpPpPo.......",
    "........oppppppppo......",
    ".......ohhhhhhhhhho.....",
    "......ohhHHHHHHHHhho....",
    "......ohHhhhhhhhhHho....",
    "......oHhsssssssshHo....",
    "......oHhsSoosooSshHo...",
    "......oHhssssssshho.....",
    ".......ohssssssho.......",
    "........ossssso.........",
    ".......oaaaaaaao........",
    "......oaAAAAAAAAAao.....",
    "....osaAttttttttAaso....",
    "....osaAttttttttAaso....",
    ".....oaAtttttttAAao.....",
    ".....oaAAAAAAAAAAAao....",
    "......obbbbbbbbbbo......",
    "......ottottottoTTo.....",
    "......ottottottoTTo.....",
    ".......ottottottoo......",
    "........oooo.ossso......",
    "........ooo..osso.......",
    ".......oss...osso.......",
    "......osso...oBBBo......",
    ".....oBBBo..oBBBBo......",
    ".....oBBBBo.oBBBBo......",
    ".....ooooo...ooooo......",
]

# Walk B: left leg forward
ROMAN_WALK_B = [
    "........................",
    "...........oo...........",
    "..........oPPo..........",
    ".........oPPPPo.........",
    "........oPpPpPPo........",
    "........oPpPpPpPo.......",
    "........oppppppppo......",
    ".......ohhhhhhhhhho.....",
    "......ohhHHHHHHHHhho....",
    "......ohHhhhhhhhhHho....",
    "......oHhsssssssshHo....",
    "......oHhsSoosooSshHo...",
    "......oHhssssssshho.....",
    ".......ohssssssho.......",
    "........ossssso.........",
    ".......oaaaaaaao........",
    "......oaAAAAAAAAAao.....",
    "....osaAttttttttAaso....",
    "....osaAttttttttAaso....",
    ".....oaAtttttttAAao.....",
    ".....oaAAAAAAAAAAAao....",
    "......obbbbbbbbbbo......",
    "......ottottottoTTo.....",
    "......ottottottoTTo.....",
    "......ootottottoTo......",
    ".......ossso.oooo.......",
    ".......osso..ooo........",
    ".......osso...oss.......",
    "......oBBBo....osso.....",
    "......oBBBBo..oBBBo.....",
    "......oBBBBo.oBBBBo.....",
    "......ooooo...ooooo.....",
]

# Jump: arms up, legs tucked
ROMAN_JUMP = [
    "...........oo...........",
    "..........oPPo..........",
    ".........oPPPPo.........",
    "........oPpPpPPo........",
    "........oPpPpPpPo.......",
    "........oppppppppo......",
    ".......ohhhhhhhhhho.....",
    "......ohhHHHHHHHHhho....",
    "......ohHhhhhhhhhHho....",
    "......oHhsssssssshHo....",
    "......oHhsSoosooSshHo...",
    "......oHhssssssshho.....",
    ".......ohssssssho.......",
    "...oss..ossssso..sso....",
    "..ossso.ossssso.ossso...",
    "..ossso.oaaaaao.ossso...",
    "...oso.oaAAAAAao.oso....",
    "....oooaAttttAaooo......",
    ".....oaAttttttAao.......",
    ".....oaAAAAAAAAAao......",
    "......obbbbbbbbbo.......",
    "......ottottottoo.......",
    ".......osso..osso.......",
    "......oBBBo..oBBBo......",
    "......ooooo..ooooo......",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
]


_CHAR_W, _CHAR_H = 24, 32
_CHAR_SCALE = 3

# Cache built frames so we only render each sprite once per run
_FRAME_CACHE = {}


def _build_frame(grid: list, palette: dict) -> pygame.Surface:
    surf = pygame.Surface((_CHAR_W, _CHAR_H), pygame.SRCALPHA)
    surf.fill(_T)
    _draw_pixels(surf, grid, palette)
    return _scale(surf, _CHAR_SCALE)


# Build or return cached animation frames for a character kind
def build_character_frames(kind: str) -> dict:
    if kind in _FRAME_CACHE:
        return _FRAME_CACHE[kind]

    if kind == "cowboy":
        palette = COWBOY_PALETTE
        grids = {
            "idle": [COWBOY_IDLE],
            "walk": [COWBOY_WALK_A, COWBOY_WALK_B],
            "jump": [COWBOY_JUMP],
        }
    elif kind == "roman":
        palette = ROMAN_PALETTE
        grids = {
            "idle": [ROMAN_IDLE],
            "walk": [ROMAN_WALK_A, ROMAN_WALK_B],
            "jump": [ROMAN_JUMP],
        }
    else:
        raise ValueError(f"unknown character kind: {kind}")

    frames = {state: [_build_frame(g, palette) for g in grid_list]
              for state, grid_list in grids.items()}
    _FRAME_CACHE[kind] = frames
    return frames


# Get a sprite frame; facing_left flips it horizontally
def get_sprite(kind: str, state: str, frame_index: int, facing_left: bool) -> pygame.Surface:
    frames = build_character_frames(kind)
    state_frames = frames.get(state, frames["idle"])
    surf = state_frames[frame_index % len(state_frames)]
    if facing_left:
        return pygame.transform.flip(surf, True, False)
    return surf


# Cache backgrounds so each level builds only once
_BG_CACHE = {}


def _bg_space(w: int, h: int) -> pygame.Surface:
    surf = pygame.Surface((w, h))

    # Deep space gradient: near-black at top fading to slightly warmer dark at bottom
    for y in range(h):
        t = y / h
        pygame.draw.line(surf, (int(t * 8), int(t * 5), int(15 + t * 20)), (0, y), (w, y))

    # Stars — fixed seed for determinism
    rng = random.Random(99)
    for _ in range(500):
        sx = rng.randint(0, w - 1)
        sy = rng.randint(0, h - 1)
        br = rng.randint(140, 255)
        tint = rng.choice([
            (br, br, br),
            (br, br - 15, br - 30),
            (br - 30, br - 15, br),
        ])
        if rng.random() < 0.12:
            pygame.draw.circle(surf, tint, (sx, sy), 2)
        else:
            surf.set_at((sx, sy), tint)

    # Nebula cloud (semi-transparent blobs blit onto surface)
    neb = pygame.Surface((360, 240), pygame.SRCALPHA)
    for cx, cy, r, col in [
        (180, 120, 100, (70, 10, 110, 25)),
        (150, 100,  70, (30,  8,  80, 18)),
        (200, 140,  60, (15, 30,  90, 18)),
        (170,  80,  45, (90, 20, 140, 15)),
    ]:
        pygame.draw.circle(neb, col, (cx, cy), r)
    surf.blit(neb, (w - 420, 40))

    # Planet (upper-right quadrant)
    px, py, pr = w - 240, 190, 85
    for ri in range(pr, 0, -1):
        t = 1 - ri / pr
        surf.set_at  # avoid unused-import warning
        pygame.draw.circle(surf, (int(30 + t * 50), int(60 + t * 90), int(120 + t * 80)), (px, py), ri)
    # Ring
    pygame.draw.ellipse(surf, (170, 150, 90), (px - 130, py - 22, 260, 44), 4)
    pygame.draw.ellipse(surf, (120, 100, 65), (px - 108, py - 16, 216, 32), 2)
    # Surface markings
    pygame.draw.circle(surf, (40, 75, 155), (px - 22, py - 18), 14)
    pygame.draw.circle(surf, (25, 55, 120), (px + 30, py + 12), 10)
    pygame.draw.circle(surf, (50, 90, 165), (px - 8, py + 24), 7)

    # Small moon
    mx, my = w - 490, 115
    pygame.draw.circle(surf, (155, 155, 165), (mx, my), 32)
    pygame.draw.circle(surf, (135, 135, 145), (mx, my), 32, 2)
    pygame.draw.circle(surf, (120, 120, 130), (mx - 11, my - 6), 9)
    pygame.draw.circle(surf, (120, 120, 130), (mx + 13, my + 9), 6)

    # Distant space-station silhouette (bottom-left)
    sc = (12, 16, 30)
    sx2, sy2 = 210, h - 190
    pygame.draw.rect(surf, sc, (sx2 - 110, sy2 - 12, 220, 24))   # main hull
    pygame.draw.rect(surf, sc, (sx2 - 85,  sy2 - 55, 22,  75))   # solar panel L
    pygame.draw.rect(surf, sc, (sx2 + 63,  sy2 - 55, 22,  75))   # solar panel R
    pygame.draw.rect(surf, sc, (sx2 - 70,  sy2 - 55, 140, 8))    # panel crossbar L
    pygame.draw.rect(surf, sc, (sx2 - 70,  sy2 + 18, 140, 8))    # panel crossbar R
    pygame.draw.circle(surf, sc, (sx2, sy2), 22)                  # central module

    return surf


def _bg_modern(w: int, h: int) -> pygame.Surface:
    surf = pygame.Surface((w, h))
    # Sky gradient: purple to orange horizon
    for y in range(h):
        t = y / h
        r = int(30 + t * 200)
        g = int(20 + t * 110)
        b = int(70 + t * 40)
        pygame.draw.line(surf, (r, g, b), (0, y), (w, y))

    # Sun near horizon
    pygame.draw.circle(surf, (255, 190, 100), (w // 2, int(h * 0.62)), 90)
    pygame.draw.circle(surf, (255, 230, 150), (w // 2, int(h * 0.62)), 60)

    # Seeded rng so the skyline stays consistent every frame
    rng = random.Random(42)
    far_color = (24, 18, 38)

    # Far skyline silhouettes
    x = 0
    while x < w:
        bw = rng.randint(60, 140)
        bh = rng.randint(200, 380)
        pygame.draw.rect(surf, far_color, (x, h - bh, bw, bh))
        x += bw + rng.randint(0, 8)

    # Near skyline with lit windows
    near_color = (12, 10, 24)
    window_color = (255, 220, 110)
    x = -20
    while x < w:
        bw = rng.randint(110, 200)
        bh = rng.randint(280, 520)
        bx = x
        by = h - bh
        pygame.draw.rect(surf, near_color, (bx, by, bw, bh))
        # window grid
        for wy in range(by + 24, h - 40, 28):
            for wx in range(bx + 12, bx + bw - 8, 22):
                if rng.random() < 0.55:
                    pygame.draw.rect(surf, window_color, (wx, wy, 8, 14))
        x += bw + rng.randint(10, 30)

    return surf


def _bg_wildwest(w: int, h: int) -> pygame.Surface:
    surf = pygame.Surface((w, h))
    # Sky: peach to amber
    for y in range(h):
        t = y / h
        r = int(245 - t * 30)
        g = int(180 - t * 40)
        b = int(120 - t * 60)
        pygame.draw.line(surf, (r, g, b), (0, y), (w, y))

    # Sun
    pygame.draw.circle(surf, (255, 240, 180), (int(w * 0.8), int(h * 0.25)), 70)

    # Distant mesas (flat-topped rocks)
    mesa_far = (180, 120, 90)
    mesa_near = (140, 85, 65)
    for cx, mw, mh in [(250, 420, 180), (760, 360, 150), (1200, 500, 200), (1700, 380, 170)]:
        pygame.draw.rect(surf, mesa_far, (cx - mw // 2, h - 260 - mh, mw, mh))
        # stratification band
        pygame.draw.rect(surf, (150, 95, 70),
                         (cx - mw // 2, h - 260 - mh + mh // 3, mw, 6))

    # Nearer mesas
    for cx, mw, mh in [(120, 480, 140), (640, 440, 120), (1400, 520, 160), (1820, 400, 130)]:
        pygame.draw.rect(surf, mesa_near, (cx - mw // 2, h - 160 - mh, mw, mh))

    # Foreground sand
    pygame.draw.rect(surf, (210, 160, 100), (0, h - 160, w, 160))

    # Scattered background cacti
    cactus_color = (60, 90, 55)
    rng = random.Random(99)
    for _ in range(14):
        cx = rng.randint(40, w - 40)
        cy = h - 160 + rng.randint(0, 30)
        ch = rng.randint(40, 90)
        pygame.draw.rect(surf, cactus_color, (cx, cy - ch, 10, ch))
        # arms
        if rng.random() < 0.7:
            pygame.draw.rect(surf, cactus_color, (cx - 10, cy - ch + 15, 10, 5))
            pygame.draw.rect(surf, cactus_color, (cx - 10, cy - ch + 15, 5, 20))
        if rng.random() < 0.7:
            pygame.draw.rect(surf, cactus_color, (cx + 10, cy - ch + 25, 10, 5))
            pygame.draw.rect(surf, cactus_color, (cx + 15, cy - ch + 5, 5, 25))

    return surf


def _bg_colosseum(w: int, h: int) -> pygame.Surface:
    surf = pygame.Surface((w, h))
    # Sky gradient
    for y in range(h):
        t = y / h
        r = int(130 + t * 40)
        g = int(170 + t * 35)
        b = int(220 - t * 30)
        pygame.draw.line(surf, (r, g, b), (0, y), (w, y))

    # Clouds
    rng = random.Random(7)
    for _ in range(6):
        cx = rng.randint(80, w - 80)
        cy = rng.randint(40, 160)
        for ox, oy, rad in [(-20, 0, 20), (0, -6, 24), (20, 0, 18), (10, 8, 14), (-10, 8, 14)]:
            pygame.draw.circle(surf, (245, 245, 248), (cx + ox, cy + oy), rad)

    # Distant wall with small arches
    stone_far    = (210, 190, 155)
    stone_far_d  = (165, 140, 105)
    arch_shadow  = (80, 65, 45)
    wall_top = int(h * 0.22)
    wall_bot = int(h * 0.42)
    pygame.draw.rect(surf, stone_far, (0, wall_top, w, wall_bot - wall_top))

    # Row of arches along the wall
    arch_w, arch_h = 36, 40
    y_arch = wall_top + 20
    x = 12
    while x < w:
        pygame.draw.rect(surf, arch_shadow, (x, y_arch, arch_w, arch_h - arch_w // 2))
        pygame.draw.circle(surf, arch_shadow, (x + arch_w // 2, y_arch), arch_w // 2)
        pygame.draw.rect(surf, stone_far_d, (x - 3, y_arch - 2, 3, arch_h + 2))
        x += arch_w + 12

    # Cornice line between wall and tiered seating
    pygame.draw.rect(surf, stone_far_d, (0, wall_bot - 6, w, 6))

    # Tiered seating with audience
    tier_colors_light = [(198, 170, 130), (185, 155, 115), (170, 140, 100), (155, 125, 90)]
    tier_colors_dark  = [(150, 120, 85),  (135, 105, 72),  (120, 92, 62),   (100, 75, 50)]
    audience_color    = (55, 40, 30)

    tier_top = wall_bot
    tier_h = 50
    num_tiers = 4
    for i in range(num_tiers):
        top_y = tier_top + i * tier_h
        light = tier_colors_light[i]
        dark  = tier_colors_dark[i]
        pygame.draw.rect(surf, light, (0, top_y, w, tier_h))
        # shadow band at base of tier
        pygame.draw.rect(surf, dark, (0, top_y + tier_h - 8, w, 8))
        pygame.draw.line(surf, dark, (0, top_y), (w, top_y), 2)
        # step seams
        for sx in range(0, w, 90):
            pygame.draw.line(surf, dark, (sx, top_y), (sx, top_y + tier_h), 1)
        # audience figures
        for hx in range(20 + i * 15, w, 45):
            pygame.draw.rect(surf, audience_color, (hx, top_y + 8, 8, 14))
            pygame.draw.circle(surf, audience_color, (hx + 4, top_y + 6), 4)
            # occasional red-draped citizen
            if (hx + i) % 3 == 0:
                pygame.draw.rect(surf, (140, 40, 35), (hx, top_y + 10, 8, 8))

    # Arena sand
    arena_top = tier_top + num_tiers * tier_h
    if arena_top < h:
        pygame.draw.rect(surf, (212, 178, 120), (0, arena_top, w, h - arena_top))
        for y in range(arena_top + 8, h, 18):
            pygame.draw.line(surf, (195, 160, 100), (0, y), (w, y), 1)

    return surf


# Return a cached full-screen background for the given level
def get_background(level_number: int, w: int, h: int) -> pygame.Surface:
    if level_number in _BG_CACHE:
        return _BG_CACHE[level_number]
    if level_number == 1:
        bg = _bg_modern(w, h)
    elif level_number == 2:
        bg = _bg_wildwest(w, h)
    elif level_number == 3:
        bg = _bg_colosseum(w, h)
    elif level_number == 4:
        bg = _bg_space(w, h)
    else:
        bg = pygame.Surface((w, h))
        bg.fill(pygame.Color("#474747"))
    _BG_CACHE[level_number] = bg
    return bg


# Color theme per level used for platforms and movable walls
_LEVEL_THEME = {
    1: {   # Modern (glass & steel)
        "top":    pygame.Color("#6fa8d6"),
        "body":   pygame.Color("#3c5a7a"),
        "edge":   pygame.Color("#1a2838"),
        "accent": pygame.Color("#9cdfff"),
    },
    2: {   # Wild West (weathered wood)
        "top":    pygame.Color("#b8864b"),
        "body":   pygame.Color("#7a5020"),
        "edge":   pygame.Color("#3a2410"),
        "accent": pygame.Color("#e0b070"),
    },
    3: {   # Colosseum (marble)
        "top":    pygame.Color("#e8ddc4"),
        "body":   pygame.Color("#b8a886"),
        "edge":   pygame.Color("#6a5b40"),
        "accent": pygame.Color("#f8f0d8"),
    },
    4: {   # Space station (dark steel + neon)
        "top":    pygame.Color("#00bbee"),
        "body":   pygame.Color("#141830"),
        "edge":   pygame.Color("#050810"),
        "accent": pygame.Color("#0077cc"),
    },
}


# Draw a static platform in the current level's theme
def draw_themed_platform(screen: pygame.Surface, rect: pygame.Rect, level_number: int) -> None:
    theme = _LEVEL_THEME.get(level_number, _LEVEL_THEME[1])

    pygame.draw.rect(screen, theme["body"], rect)

    # top highlight band
    top_band = pygame.Rect(rect.x, rect.y, rect.width, max(4, rect.height // 3))
    pygame.draw.rect(screen, theme["top"], top_band)

    # dark edge
    pygame.draw.rect(screen, theme["edge"], rect, 2)

    # level-specific accents
    if level_number == 1:
        # neon trim + panel splits
        pygame.draw.line(screen, theme["accent"],
                         (rect.x + 2, rect.y + 1), (rect.right - 3, rect.y + 1), 1)
        for x in range(rect.x + 60, rect.right - 10, 60):
            pygame.draw.line(screen, theme["edge"],
                             (x, rect.y + 3), (x, rect.bottom - 2), 1)
    elif level_number == 2:
        # wood grain + plank joints with nails
        grain_y = rect.y + rect.height // 2
        pygame.draw.line(screen, theme["edge"],
                         (rect.x + 2, grain_y), (rect.right - 3, grain_y), 1)
        for x in range(rect.x + 40, rect.right - 8, 40):
            pygame.draw.line(screen, theme["edge"],
                             (x, rect.y + 3), (x, rect.bottom - 2), 1)
            pygame.draw.circle(screen, theme["edge"], (x, rect.y + 5), 1)
    elif level_number == 3:
        # marble block seams
        for x in range(rect.x + 80, rect.right - 10, 80):
            pygame.draw.line(screen, theme["edge"],
                             (x, rect.y + 3), (x, rect.bottom - 2), 1)
        pygame.draw.line(screen, theme["accent"],
                         (rect.x + 2, rect.y + 1), (rect.right - 3, rect.y + 1), 1)
    elif level_number == 4:
        # tech panel seams + glowing neon top trim
        for x in range(rect.x + 50, rect.right - 5, 50):
            pygame.draw.line(screen, theme["edge"],
                             (x, rect.y + 2), (x, rect.bottom - 2), 1)
        pygame.draw.line(screen, theme["accent"],
                         (rect.x + 2, rect.y + 1), (rect.right - 3, rect.y + 1), 2)
        pygame.draw.line(screen, theme["top"],
                         (rect.x + 2, rect.y + 3), (rect.right - 3, rect.y + 3), 1)


# Draw a movable wall with hatching so it reads as a special wall
def draw_themed_wall(screen: pygame.Surface, rect: pygame.Rect, level_number: int) -> None:
    theme = _LEVEL_THEME.get(level_number, _LEVEL_THEME[1])
    pygame.draw.rect(screen, theme["accent"], rect)
    pygame.draw.rect(screen, theme["edge"], rect, 2)
    # hatching pattern
    for y in range(rect.y + 6, rect.bottom - 3, 10):
        pygame.draw.line(screen, theme["body"],
                         (rect.x + 3, y), (rect.right - 3, y), 1)


# Draw themed hazard art; returns True if handled, False to fall back to default spikes
def draw_themed_hazard(screen: pygame.Surface, hazard, level_number: int) -> bool:
    if level_number == 1:
        _draw_electric_hazard(screen, hazard)
        return True
    elif level_number == 2:
        _draw_cactus_hazard(screen, hazard)
        return True
    elif level_number == 3:
        _draw_lion_hazard(screen, hazard)
        return True
    elif level_number == 4:
        _draw_asteroid_hazard(screen, hazard)
        return True
    return False


# Modern-era hazard: electric zap pads
def _draw_electric_hazard(screen: pygame.Surface, hazard) -> None:
    base = pygame.Color("#202830")
    pad = pygame.Color("#d4a017")
    spark = pygame.Color("#fff5a0")
    for i in range(hazard.count):
        bx = hazard.rect.x + i * hazard.spike_w
        by = hazard.rect.y
        # metal pad base
        pygame.draw.rect(screen, base, (bx, by + hazard.spike_h - 8, hazard.spike_w, 8))
        # coil body
        coil_top = by + 4
        pygame.draw.rect(screen, pad,
                         (bx + 4, coil_top, hazard.spike_w - 8, hazard.spike_h - 8))
        # zigzag lightning
        mid_x = bx + hazard.spike_w // 2
        pts = [
            (mid_x, coil_top + 2),
            (mid_x - 4, coil_top + 8),
            (mid_x + 3, coil_top + 14),
            (mid_x - 2, coil_top + 20),
        ]
        pygame.draw.lines(screen, spark, False, pts, 2)
        pygame.draw.rect(screen, pygame.Color("#000000"),
                         (bx, by, hazard.spike_w, hazard.spike_h), 1)


# Wild-west hazard: cactus with spines
def _draw_cactus_hazard(screen: pygame.Surface, hazard) -> None:
    cactus_green = pygame.Color("#3a6638")
    cactus_dark  = pygame.Color("#244022")
    spine        = pygame.Color("#f0e0a0")
    for i in range(hazard.count):
        bx = hazard.rect.x + i * hazard.spike_w
        by = hazard.rect.y
        # cactus body
        body_rect = pygame.Rect(bx + 2, by + 4, hazard.spike_w - 4, hazard.spike_h - 4)
        pygame.draw.rect(screen, cactus_green, body_rect)
        # vertical ridge
        mid_x = bx + hazard.spike_w // 2
        pygame.draw.line(screen, cactus_dark,
                         (mid_x, by + 5), (mid_x, by + hazard.spike_h - 2), 1)
        # spines on top and sides
        for sx, sy, ex, ey in [
            (mid_x, by + 4, mid_x, by),
            (mid_x - 3, by + 6, mid_x - 6, by + 2),
            (mid_x + 3, by + 6, mid_x + 6, by + 2),
            (bx + 2, by + 10, bx - 2, by + 8),
            (bx + hazard.spike_w - 3, by + 10, bx + hazard.spike_w + 1, by + 8),
        ]:
            pygame.draw.line(screen, spine, (sx, sy), (ex, ey), 1)
        pygame.draw.rect(screen, pygame.Color("#000000"), body_rect, 1)


# Colosseum hazard: prowling lions
def _draw_lion_hazard(screen: pygame.Surface, hazard) -> None:
    mane   = pygame.Color("#8b5a20")
    mane_d = pygame.Color("#5a3a14")
    fur    = pygame.Color("#c49050")
    fur_d  = pygame.Color("#8a6838")
    eye    = pygame.Color("#ffdc60")
    nose   = pygame.Color("#2a1810")

    for i in range(hazard.count):
        bx = hazard.rect.x + i * hazard.spike_w
        by = hazard.rect.y
        cw = hazard.spike_w
        ch = hazard.spike_h

        # body
        body_rect = pygame.Rect(bx + 2, by + ch - 12, cw - 4, 10)
        pygame.draw.rect(screen, fur, body_rect)
        pygame.draw.rect(screen, fur_d, (body_rect.x, body_rect.bottom - 3, body_rect.width, 3))

        # paws
        pygame.draw.rect(screen, fur_d, (bx + 2, by + ch - 3, 5, 3))
        pygame.draw.rect(screen, fur_d, (bx + cw - 7, by + ch - 3, 5, 3))

        # mane
        mane_cx = bx + cw // 2
        mane_cy = by + ch - 16
        pygame.draw.circle(screen, mane, (mane_cx, mane_cy), 8)
        pygame.draw.circle(screen, mane_d, (mane_cx, mane_cy), 8, 1)
        # mane fringe
        for dx, dy in [(-7, -5), (-4, -8), (0, -9), (4, -8), (7, -5), (-8, 0), (8, 0)]:
            pygame.draw.circle(screen, mane, (mane_cx + dx, mane_cy + dy), 2)

        # face
        face_rect = pygame.Rect(mane_cx - 4, mane_cy - 3, 8, 7)
        pygame.draw.rect(screen, fur, face_rect)
        # eyes
        screen.set_at((mane_cx - 2, mane_cy - 1), eye)
        screen.set_at((mane_cx + 2, mane_cy - 1), eye)
        # nose
        pygame.draw.rect(screen, nose, (mane_cx - 1, mane_cy + 2, 2, 2))

        # tail
        pygame.draw.line(screen, fur_d,
                         (bx + cw - 3, by + ch - 8),
                         (bx + cw + 2, by + ch - 12), 2)


# Space hazard: tumbling asteroids with a danger glow
def _draw_asteroid_hazard(screen: pygame.Surface, hazard) -> None:
    rock_mid   = pygame.Color("#504540")
    rock_dark  = pygame.Color("#282018")
    rock_light = pygame.Color("#706560")
    glow       = pygame.Color("#ff5522")

    for i in range(hazard.count):
        bx = hazard.rect.x + i * hazard.spike_w
        by = hazard.rect.y
        cw = hazard.spike_w
        ch = hazard.spike_h
        cx = bx + cw // 2
        cy = by + ch // 2 + 3
        r  = min(cw, ch) // 2 - 3

        # Irregular rocky outline (offset polygon)
        pts = [
            (cx - r + 1, by + 3),
            (cx + r - 2, by + 2),
            (cx + r,     cy - 2),
            (cx + r - 1, cy + r - 1),
            (cx + 2,     by + ch - 2),
            (cx - r + 3, by + ch - 3),
            (cx - r,     cy + 2),
            (cx - r + 1, cy - r + 2),
        ]
        pygame.draw.polygon(screen, rock_mid, pts)
        pygame.draw.polygon(screen, rock_dark, pts, 2)

        # Surface craters
        pygame.draw.circle(screen, rock_dark,  (cx - r // 3, cy - r // 3), max(2, r // 3))
        pygame.draw.circle(screen, rock_light, (cx + r // 4, cy + r // 4), max(1, r // 4))

        # Danger glow ring
        pygame.draw.circle(screen, glow, (cx, cy), r + 2, 1)

        # Small trailing debris chips
        pygame.draw.circle(screen, rock_mid, (cx - r - 3, cy - 1), 2)
        pygame.draw.circle(screen, rock_mid, (cx + r + 2, cy + 2), 1)