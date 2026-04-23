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
from lost_in_time.pause_menu import PauseMenu


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

_SHAKE_TRAUMA = 0.5
_SHAKE_DECAY = 0.8
_SHAKE_MAX_OFFSET = 20

class Game:

    def __init__(self, server_ip: str = None) -> None:
        self.fps = FPS

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._render_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.current_level = 1
        self.level = Level(self.current_level, SCREEN_WIDTH, SCREEN_HEIGHT, PADDING, HUD_H)
        self.menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT, "title")
        self.state = "title_menu"

        # Keep track of menus for back button implementation
        self.menu_track = []

        # Spawn positions come from the level so each level can place players anywhere
        # P1 = cowboy, P2 = Roman soldier
        self.players = [
            Player(*self.level.spawn_p1, CONTROLS_PLAYER1, sprite_kind="cowboy"),
            Player(*self.level.spawn_p2, CONTROLS_PLAYER2, sprite_kind="roman"),
        ]
        
        if self.current_level == 4:
            for player in self.players:
                player.GRAVITY = 600.0
                player.JUMP_SPEED = 600.0

        self.level_select_button = Button(
            "Level Select",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80),
            400, 100, "#8DF78DFF"
        )

        self.hud = HUD(SCREEN_WIDTH, HUD_H)
        if self.level.collectibles:
            self.hud.set_gem_kind(self.level.collectibles[0].kind)

        # Multiplayer attributes
        self.server = None
        self.client = None
        self.join_ip = server_ip or ""
        self.pause_menu = PauseMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.paused = False

        self._shake_trauma = 0.0

        # main music
        pygame.mixer.init()
        pygame.mixer.music.load("assets/music/menu_music.mp3")
        pygame.mixer.music.play(-1)

        # sound effect for collecting collectibles
        self.collect_sound = pygame.mixer.Sound("assets/sounds/collect.mp3")
        # sound effect for player death
        self.death_sound = pygame.mixer.Sound("assets/sounds/death.mp3")

    def _add_trauma(self, amount: float) -> None:
        self._shake_trauma = min(1.0, self._shake_trauma + amount)

    def _shake_offset(self) -> tuple[int, int]:
        if self._shake_trauma <= 0:
            return (0, 0)
        shake = self._shake_trauma ** 2
        import random
        dx = int(random.uniform(-1, 1) * _SHAKE_MAX_OFFSET * shake)
        dy = int(random.uniform(-1, 1) * _SHAKE_MAX_OFFSET * shake)
        return (dx, dy)

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
            Player(*self.level.spawn_p1, CONTROLS_PLAYER1, sprite_kind="cowboy"),
            Player(*self.level.spawn_p2, CONTROLS_PLAYER2, sprite_kind="roman"),
        ]
        
        if self.current_level == 4:
            for player in self.players:
                player.GRAVITY = 600.0
                player.JUMP_SPEED = 600.0

        self.hud.reset()
        # tell HUD which gem this level uses 
        if self.level.collectibles:
            self.hud.set_gem_kind(self.level.collectibles[0].kind)
        self._shake_trauma = 0.0

        pygame.mixer.stop()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            # pause menu toggle on ESC; also quit from title menu or level complete screen
            if event.key == pygame.K_ESCAPE:
                if self.state == "play":
                    if self.client:
                        # Pause feature for multiplayer
                        self.client.send("pause", {"pause": not self.paused})
                    else:
                        self.paused = not self.paused
                else:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            if event.key == pygame.K_r and self.state in ("play", "level_complete", "game_over"):
                # Send restart message to server 
                if self.client:
                    self.client.send("restart", {})
                else:
                    self._restart()
                    self.state = "play"

        # while paused only pause menu should receive input events
        # Added self.client checks to allow server to correctly display each eaction
        # to all clients
        if self.paused:
            self.pause_menu.handle_event(event)
            action = self.pause_menu.action
            if action == "resume":
                if self.client:
                    self.client.send("pause", {"pause": False})
                else:
                    self.paused = False
            elif action == "level_select":
                if self.client:
                    self.client.send("menu", {})
                else:
                    self.paused = False
                    pygame.mixer.music.play(-1)  # restart menu music
                    self.menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT, "level_select")
                    self.menu_track = ["title"]
                    self.state = "title_menu"
            elif action == "restart":
                if self.client:
                    self.client.send("restart", {})
                else:
                    self._restart()
                self.state = "play"
            elif action == "quit":
                if self.client:
                    self.client.send("disconnect", {})
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            return  # block all game input while paused

        if self.state == "title_menu":
            self.menu.handle_event(event)

        if self.state == "level_complete":
            self.level_select_button.handle_event(event)
            if self.level_select_button.clicked:
                self.level_select_button.clicked = False
                # update all clients menu to be on the same menu
                if self.client:
                    self.client.send("menu", {})
                else:
                    pygame.mixer.music.play(-1)  # restart menu music
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
            # HUD has its own event handling for the pause button, so check it first
            self.hud.handle_event(event)
            if self.hud.pause_clicked:
                self.paused = not self.paused
                return
            for player in self.players:
                player.handle_event(event)
            # Forward interact keypresses to levers
            for lever in self.level.levers:
                lever.handle_event(event, self.players)

    def update(self, dt: float) -> None:
        # Handle client-server communication in different states for multiplayer
        # to be able to broadcast to both clients
        if self.client and self.state in ("play", "title_menu", "level_complete", "game_over"):
            if self.server:
                self.server.handle_connect()
            self.client.receive()
            if self.state == "play":
                self.paused = self.client.paused

        # Server broadcast level selection and clears old game state for fresh start
        if self.client and self.client.level is not None:
            self.current_level = self.client.level
            self.client.level = None
            self.client.game_state = None 
            self.client.paused = False
            self.paused = False
            pygame.mixer.music.stop()
            self._restart()
            self.state = "play"

        # Return to title menu from level complete screen
        if self.client and self.client.menu:
            self.client.menu = False
            self.paused = False
            pygame.mixer.music.play(-1)
            self.menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT, "level_select")
            self.menu_track = []
            self.state = "title_menu"

        # menu still needs to be navigable while paused but other game updates frozen
        if self.paused:
            return

        if self._shake_trauma > 0:
            self._shake_trauma = max(0.0, self._shake_trauma - _SHAKE_DECAY * dt)

        if self.state == "title_menu":
            if self.menu.next_screen:
                _level_map = {"game": 1, "game2": 2, "game3": 3, "game4": 4}
                if self.menu.next_screen in _level_map:
                    self.current_level = _level_map[self.menu.next_screen]
                    self.menu.next_screen = None
                    # check if self.client is active and send to server request to change level
                    if self.client:
                        self.client.send("level_select", {"level": self.current_level})
                    else:
                        pygame.mixer.music.stop()  # stop menu music when game starts
                        self._restart()
                        self.state = "play"
                elif self.menu.next_screen == "back":
                    if self.menu_track:
                        previous = self.menu_track.pop()
                        self.menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT, previous)

                # Initialize server and client with server IP for host if player 
                # chooses to host
                elif self.menu.next_screen == "host":
                    self.server = Server(self.current_level, ip = self.join_ip)
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
                self.menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT, "level_select")
                self.menu_track = []
                self.state = "title_menu"

        # Check to see if client has received game state
        # from the server to start game
        if self.state == "joining":
            if self.client:
                self.client.receive()
                if self.client.player_id is not None:
                    self.menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT, "level_select")
                    self.menu_track = []
                    self.state = "title_menu"

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
                            collectible.collect()
                            self.hud.notify_collected()
                            self.collect_sound.play()

                    if self.state == "play":
                        for hz in pygame.sprite.spritecollide(player, self.level.hazards, dokill=False):
                            self._add_trauma(_SHAKE_TRAUMA)
                            self.death_sound.play()
                            self.state = "game_over"
                            break

                for collectible in self.level.collectibles:
                    collectible.update(dt)

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
            # Multiplayer game update for game logic
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
                
                # Check to see if client has game state and then proceed to update
                # player positions based on game state data
                if self.client.game_state:
                    position = self.client.game_state["players"]

                    # Update player positions and their animations based on game state
                    for i in range(len(self.players)):
                        self.players[i].rect.center = (position[i]["x"], position[i]["y"])
                        self.players[i].pos.x = position[i]["x"]
                        self.players[i].pos.y = position[i]["y"]

                        # Update velocity, on_ground, and facing for animation state and movement
                        self.players[i].velocity.x = position[i]["vel_x"]
                        self.players[i].on_ground = position[i]["on_ground"]
                        self.players[i].facing_left = position[i]["facing_left"]

                        # animation state: in-air -> jump, moving -> walk, else idle
                        # pulled from player.py
                        if not self.players[i].on_ground:
                            self.players[i]._anim_state = "jump"
                            self.players[i]._walk_timer = 0.0
                        elif abs(self.players[i].velocity.x) > self.players[i].WALK_MIN_SPEED:
                            if self.players[i]._anim_state != "walk":
                                self.players[i]._anim_state = "walk"
                                self.players[i]._walk_frame = 0
                                self.players[i]._walk_timer = 0.0
                            self.players[i]._walk_timer += dt
                            if self.players[i]._walk_timer >= self.players[i].WALK_FRAME_DURATION:
                                self.players[i]._walk_timer -= self.players[i].WALK_FRAME_DURATION
                                self.players[i]._walk_frame = (self.players[i]._walk_frame + 1) % 2
                        else:
                            self._anim_state = "idle"
                            self._walk_timer = 0.0

                    # check server broadcast to see if either player lost health
                    # and play death effect upon dying
                    if position[0]["health"] == 0 or position[1]["health"] == 0:
                        self._add_trauma(_SHAKE_TRAUMA)
                        self.death_sound.play()
                        self.state = "game_over"

                    # check broadcast to see if message player touching door is true and update 
                    # and if message from server is door completed, update game state to level completed
                    if self.level.exit_door:
                        self.level.exit_door.p1_touching = self.client.game_state.get("door_p1_touching", False)
                        self.level.exit_door.p2_touching = self.client.game_state.get("door_p2_touching", False)
                        if self.client.game_state.get("door_completed"):
                            self.state = "level_complete"

                    # update collectables by checking if collisions
                    for collectible in self.level.collectibles:
                        for player in self.players:
                            if collectible.active and player.rect.colliderect(collectible.rect):
                                collectible.collect()
                                self.hud.notify_collected()
                                self.collect_sound.play()
                    
                    # Update movable walls, levers, and buttons visually based on game state
                    # received from server by iterating through each interactable
                    # and applying the state to each one and update if needed
                    wall_states = self.client.game_state.get("movable_walls", [])
                    i = 0
                    for wall in self.level.movable_walls:
                        if i < len(wall_states):
                            wall.active = wall_states[i]
                        i += 1

                    hazard_states = self.client.game_state.get("hazards", [])
                    i = 0
                    for hazard in self.level.hazards:
                        if i < len(hazard_states):
                            hazard.rect.x = hazard_states[i]["hz_x"]
                            hazard.rect.y = hazard_states[i]["hz_y"]
                        i += 1

                    lever_states = self.client.game_state.get("lever_activated", [])
                    i = 0
                    for lever in self.level.levers:
                        if i < len(lever_states):
                            lever.activated = lever_states[i]
                            lever.update(dt)
                        i += 1

                    button_states = self.client.game_state.get("pressure_buttons", [])
                    i = 0
                    for btn in self.level.pressure_buttons:
                        if i < len(button_states):
                            btn.pressed = button_states[i]
                            btn.update(self.players)
                        i += 1
                    
                    for collectible in self.level.collectibles:
                        collectible.update(dt)

                self.hud.update(dt)

    def draw(self) -> None:
        surf = self._render_surf

        if self.state == "title_menu":
            self.menu.draw(surf)
        elif self.state in ("play", "level_complete", "game_over"):
            surf.fill(pygame.Color("#474747"))
            self.level.draw(surf)
            self.hud.draw(surf, paused=self.paused)
            for player in self.players:
                player.draw(surf)
            if self.paused:
                self.pause_menu.draw(surf)
            if self.state == "level_complete":
                font = pygame.font.SysFont("Arial", 72, True)
                msg = font.render("Level Complete!", True, pygame.Color("#FFD700"))
                surf.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - 36))
                self.level_select_button.draw(surf)
            elif self.state == "game_over":
                font = pygame.font.SysFont("Arial", 72, True)
                msg = font.render("You died! Press R to restart", True, pygame.Color("#FF4444"))
                surf.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - 36))

        # hosting and joining screens 
        elif self.state == "hosting":
            surf.fill(pygame.Color("#A7A7A7"))
            font = pygame.font.SysFont("Times New Roman", 48, True)
            ip_msg = font.render(f"Your IP: {self.server.ip}", True, pygame.Color("#000000"))
            msg = font.render("Hosting... Waiting for player to join.", True, pygame.Color("#000000"))
            surf.blit(ip_msg, (SCREEN_WIDTH // 2 - ip_msg.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            surf.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - 24))
        
        elif self.state == "joining":
            surf.fill(pygame.Color("#A7A7A7"))
            font = pygame.font.SysFont("Times New Roman", 48, True)
            msg = font.render("Enter Host IP: " + self.join_ip, True, pygame.Color("#000000"))
            help = font.render("Press Enter to connect, Backspace to delete", True, pygame.Color("#000000"))
            surf.blit(help, (SCREEN_WIDTH // 2 - help.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            surf.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - 24))
        
        dx, dy = self._shake_offset()
        self.screen.fill(pygame.Color("#000000"))
        self.screen.blit(surf, (dx, dy))
