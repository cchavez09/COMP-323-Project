import pygame

from lost_in_time.level import Level
from lost_in_time.player import Player
from lost_in_time.menu import Menu
from lost_in_time.button import Button
from lost_in_time.collectible import Collectible
from lost_in_time.hazard import Hazard
from lost_in_time.hud import HUD
from lost_in_time.Multiplayer.server import Server
from lost_in_time.Multiplayer.client import Client

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

        # Player 1 starts left, player 2 starts right (inside the cage in level 1)
        self.players = [
            Player(self.level.playfield.left + 20, self.level.playfield.bottom - 20, CONTROLS_PLAYER1),
            Player(self.level.playfield.right - 20, self.level.playfield.bottom - 20, CONTROLS_PLAYER2)
        ]
        self.players[0].color = pygame.Color("#FF0000")
        self.players[1].color = pygame.Color("#0000FF")

        self.level_select_button = Button(
            "Level Select",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80),
            400, 100, "#8DF78DFF"
        )

        self.hud = HUD(SCREEN_WIDTH, HUD_H)

        # Multiplayer attributes
        self.server = None
        self.client = None
        self.join_ip = ""

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
            Player(self.level.playfield.left + 20, self.level.playfield.bottom - 20, CONTROLS_PLAYER1),
            Player(self.level.playfield.right - 20, self.level.playfield.bottom - 20, CONTROLS_PLAYER2)
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
                # Send restart message to server 
                if self.client:
                    self.client.send("restart", {})

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
            # Check to see if in multiplayer or local and handle events based on
            # if self.client is None or not
            if self.client is None:
                for player in self.players:
                    player.handle_event(event)
                # Forward interact keypresses to levers
                for lever in self.level.levers:
                    lever.handle_event(event, self.players)
            else:
                self.players[self.client.player_id].handle_event(event)
                if event.type == pygame.KEYDOWN:
                    # Need to send interact message for lever interactions
                    if event.key in (pygame.K_e, pygame.K_SLASH):
                        self.client.send("interact", {"key": event.key})


        # State for joining multiplayer game allowing user to input host IP address
        if self.state == "joining":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.join_ip = self.join_ip[:-1]
                elif event.key == pygame.K_RETURN and self.join_ip:
                    # Send connect message to server to then receive player id 
                    # and the game state
                    self.client = Client(self.join_ip)
                    self.client.send("connect", {})
                else:
                    char = event.unicode
                    if char.isdigit() or char == ".":
                        self.join_ip += char

    def update(self, dt: float) -> None:
        if self.state == "title_menu":
            if self.menu.next_screen:
                if self.menu.next_screen in ("game", "game2"):
                    self.current_level = 2 if self.menu.next_screen == "game2" else 1
                    self._restart()
                    self.state = "play"
                elif self.menu.next_screen == "back":
                    if self.menu_track:
                        previous = self.menu_track.pop()
                        self.menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT, previous)

                # Initialize server and client with server IP for host if player 
                # chooses to host
                elif self.menu.next_screen == "host":
                    self.server = Server()
                    self.client = Client(self.server.ip)
                    self.client.send("connect", {})
                    self.state = "hosting"
                elif self.menu.next_screen == "join":
                    self.join_ip = ""
                    self.state = "joining"
                else:
                    self.menu_track.append(self.menu.menu)
                    self.menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT, self.menu.next_screen)

        # If hosting server waiting for second player to join and client 
        # confirms connection 
        # Check to see if server has 2 players before starting
        if self.state == "hosting":
            self.server.handle_connect()
            self.client.receive()
            if len(self.server.players) == 2 and self.client.player_id is not None:
                self._restart()
                self.state = "play"

        # Check to see if client has received game state 
        # from the server to start game
        if self.state == "joining":
            if self.client:
                self.client.receive()
                if self.client.player_id is not None:
                    self._restart()
                    self.state = "play"

        if self.state == "play":
            # Local game update
            if self.client is None:
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
            # Multiplayer game update
            else:
                # Get inputs and send them to server
                keys = pygame.key.get_pressed()
                x = 0.0
                if keys[pygame.K_a]:
                    x -= 1.0
                if keys[pygame.K_d]:
                    x += 1.0
                jump = keys[pygame.K_w]
                self.client.send("move", {"x": x, "jump": jump})

                # If server exists then update the game state through server and broadcast it back
                if self.server:
                    self.server.handle_connect()
                    self.server.update(dt)
                    self.server.broadcast()

                # Receive game state from server with broadcase
                self.client.receive()
                
                # Check to see if client has game state and then proceed to update
                # player positions based on game state data
                if self.client.game_state:
                    position = self.client.game_state["players"]
                    self.players[0].rect.center = (position[0]["x"], position[0]["y"])
                    self.players[0].pos.x = position[0]["x"]
                    self.players[0].pos.y = position[0]["y"]
                    self.players[1].rect.center = (position[1]["x"], position[1]["y"])
                    self.players[1].pos.x = position[1]["x"]
                    self.players[1].pos.y = position[1]["y"]

                    if position[0]["health"] == 0 or position[1]["health"] == 0:
                        self.state = "game_over"

                    if self.level.exit_door:
                        self.level.exit_door.p1_touching = self.client.game_state.get("door_p1_touching", False)
                        self.level.exit_door.p2_touching = self.client.game_state.get("door_p2_touching", False)
                        if self.client.game_state.get("door_completed"):
                            self.state = "level_complete"

                    for collectible in self.level.collectibles:
                        for player in self.players:
                            if collectible.active and player.rect.colliderect(collectible.rect):
                                collectible.active = False
                                self.hud.notify_collected()
                    
                    wall_states = self.client.game_state.get("movable_walls", [])
                    i = 0
                    for wall in self.level.movable_walls:
                        if i < len(wall_states):
                            wall.active = wall_states[i]
                        i += 1

                    for lever in self.level.levers:
                        lever.update(dt)
                    
                self.hud.update(dt)

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

        # Added drawing for hosting and joining states with basic instructions and minimum design
        # Will fix
        elif self.state == "hosting":
            self.screen.fill(pygame.Color("#474747"))
            font = pygame.font.SysFont("Arial", 48, True)
            ip_msg = font.render(f"Your IP: {self.server.ip}", True, pygame.Color("#FFFFFF"))
            msg = font.render("Hosting... Waiting for player to join.", True, pygame.Color("#FFFFFF"))
            self.screen.blit(ip_msg, (SCREEN_WIDTH // 2 - ip_msg.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - 24))
        
        elif self.state == "joining":
            self.screen.fill(pygame.Color("#474747"))
            font = pygame.font.SysFont("Arial", 48, True)
            msg = font.render("Enter Host IP: " + self.join_ip, True, pygame.Color("#FFFFFF"))
            help = font.render("Press Enter to connect, Backspace to delete", True, pygame.Color("#FFFFFF"))
            self.screen.blit(help, (SCREEN_WIDTH // 2 - help.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - 24))