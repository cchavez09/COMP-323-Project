import pygame

from lost_in_time.level import Level
from lost_in_time.player import Player
from lost_in_time.menu import Menu
from lost_in_time.button import Button
from lost_in_time.collectible import Collectible
from lost_in_time.hazard import Hazard
from lost_in_time.hud import HUD

# Controls for p1 and p2 defined to be passed to player class
CONTROLS_PLAYER1 = {
    "left": pygame.K_a,
    "right": pygame.K_d,
    "jump": pygame.K_w
}
CONTROLS_PLAYER2 = {
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "jump": pygame.K_UP
}

FPS = 60
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
PADDING = 50
HUD_H = 100

class Game:

    def __init__(self) -> None:
        self.fps = FPS

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.current_level = 1
        self.level = Level(self.current_level, SCREEN_WIDTH, SCREEN_HEIGHT, PADDING, HUD_H)
        self.menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT, "title")
        self.state = "title_menu"

        # Keep track of menus for back button implementation
        self.menu_track = []

        # Spawn positions come from the level so each level can place players anywhere
        self.players = [
            Player(*self.level.spawn_p1, CONTROLS_PLAYER1),
            Player(*self.level.spawn_p2, CONTROLS_PLAYER2),
        ]
        self.players[0].color = pygame.Color("#FF0000")
        self.players[1].color = pygame.Color("#0000FF")

        self.level_select_button = Button(
            "Level Select",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80),
            400, 100, "#8DF78DFF"
        )

        self.hud = HUD(SCREEN_WIDTH, HUD_H)

    def _apply_bounds_player(self, player: Player) -> None:
        player.rect.clamp_ip(self.level.playfield)

        player.pos.x = max(self.level.playfield.left, min(self.level.playfield.right, player.pos.x))
        player.pos.y = max(self.level.playfield.top, min(self.level.playfield.bottom, player.pos.y))

        if player.rect.bottom >= self.level.playfield.bottom:
            player.on_ground = True
            player.velocity.y = 0

    def _apply_wall_collisions(self, player: Player) -> None:
        # Combine static walls and currently-active movable walls
        all_walls = list(self.level.walls) + [
            mw.rect for mw in self.level.movable_walls if mw.active
        ]
        for wall in all_walls:
            if not player.rect.colliderect(wall):
                continue

            # Minimum-overlap resolution: push the player out the shortest axis
            overlap_left   = player.rect.right  - wall.left
            overlap_right  = wall.right  - player.rect.left
            overlap_top    = player.rect.bottom  - wall.top
            overlap_bottom = wall.bottom - player.rect.top

            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

            if min_overlap == overlap_top:
                # Player landed on top of wall
                player.rect.bottom = wall.top
                player.pos.y = player.rect.centery
                player.velocity.y = 0
                player.on_ground = True
            elif min_overlap == overlap_bottom:
                # Player hit ceiling
                player.rect.top = wall.bottom
                player.pos.y = player.rect.centery
                if player.velocity.y < 0:
                    player.velocity.y = 0
            elif min_overlap == overlap_left:
                # Player hit right face of wall
                player.rect.right = wall.left
                player.pos.x = player.rect.centerx
                player.velocity.x = 0
            else:
                # Player hit left face of wall
                player.rect.left = wall.right
                player.pos.x = player.rect.centerx
                player.velocity.x = 0

        # Ground probe: pygame's colliderect returns False when rects only touch
        # (share an edge without overlapping), so after resolution the player sits
        # at exactly rect.bottom == wall.top and colliderect misses it next frame.
        # A 1 px downward probe catches this and keeps on_ground reliable.
        if not player.on_ground and player.velocity.y >= 0:
            probe = player.rect.move(0, 1)
            for wall in all_walls:
                if probe.colliderect(wall):
                    player.on_ground = True
                    break

    # Restart resets the level and both players without quitting
    def _restart(self) -> None:
        self.level = Level(self.current_level, SCREEN_WIDTH, SCREEN_HEIGHT, PADDING, HUD_H)
        self.players = [
            Player(*self.level.spawn_p1, CONTROLS_PLAYER1),
            Player(*self.level.spawn_p2, CONTROLS_PLAYER2),
        ]
        self.players[0].color = pygame.Color("#FF0000")
        self.players[1].color = pygame.Color("#0000FF")

        self.hud.reset()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            if event.key == pygame.K_r and self.state in ("play", "level_complete", "game_over"):
                self._restart()
                self.state = "play"

        if self.state == "title_menu":
            self.menu.handle_event(event)

        if self.state == "level_complete":
            self.level_select_button.handle_event(event)
            if self.level_select_button.clicked:
                self.level_select_button.clicked = False
                self.menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT, "level_select")
                self.menu_track = ["title"]
                self.state = "title_menu"

        if self.state == "play":
            for player in self.players:
                player.handle_event(event)
            # Forward interact keypresses to levers
            for lever in self.level.levers:
                lever.handle_event(event, self.players)

    def update(self, dt: float) -> None:
        if self.state == "title_menu":
            if self.menu.next_screen:
                _level_map = {"game": 1, "game2": 2, "game3": 3}
                if self.menu.next_screen in _level_map:
                    self.current_level = _level_map[self.menu.next_screen]
                    self._restart()
                    self.state = "play"
                elif self.menu.next_screen == "back":
                    if self.menu_track:
                        previous = self.menu_track.pop()
                        self.menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT, previous)
                else:
                    self.menu_track.append(self.menu.menu)
                    self.menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT, self.menu.next_screen)

        if self.state == "play":
            for player in self.players:
                player.update(dt)
                # Reset on_ground after update so the jump check inside update still sees
                # the previous frame's value; collision detection restores it if needed
                player.on_ground = False
                self._apply_wall_collisions(player)
                self._apply_bounds_player(player)

                for collectible in self.level.collectibles:
                    if collectible.active and player.rect.colliderect(collectible.rect):
                        collectible.active = False
                        self.hud.notify_collected()

                for hz in pygame.sprite.spritecollide(player, self.level.hazards, dokill=False):
                    self.state = "game_over"

            self.level.hazards.update(dt)

            for lever in self.level.levers:
                lever.update(dt)

            for btn in self.level.pressure_buttons:
                btn.update(self.players)

            if self.level.exit_door:
                self.level.exit_door.update(self.players)
                if self.level.exit_door.completed:
                    self.state = "level_complete"
            
            self.hud.update(dt)

            self.players = [p for p in self.players if p.health > 0] 

    def draw(self) -> None:
        if self.state == "title_menu":
            self.menu.draw(self.screen)

        elif self.state in ("play", "level_complete", "game_over"):
            self.screen.fill(pygame.Color("#474747"))
            self.level.draw(self.screen)
            self.hud.draw(self.screen)
            for player in self.players:
                player.draw(self.screen)

            if self.state == "level_complete":
                font = pygame.font.SysFont("Arial", 72, True)
                msg = font.render("Level Complete!", True, pygame.Color("#FFD700"))
                self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - 36))
                self.level_select_button.draw(self.screen)

            elif self.state == "game_over":
                font = pygame.font.SysFont("Arial", 72, True)
                msg = font.render("You died!  Press R to restart", True, pygame.Color("#FF4444"))
                self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - 36))