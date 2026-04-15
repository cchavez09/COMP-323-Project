import socket
import json
import pygame

from lost_in_time.player import Player
from lost_in_time.level import Level

host = socket.gethostname()
IPAddr = socket.gethostbyname(host)
port = 5555


# Server is authoritative so it handles game logic and send updates to clients
# based on inputs from clients
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
PADDING = 50
HUD_H = 100

class Server:
    def __init__(self):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((self.ip, self.port)) 
        self.server.setblocking(False)
        
        # Keep track of players and their inputs
        self.players = {}
        self.inputs = {
            0: {"x": 0, "jump": False},
            1: {"x": 0, "jump": False}
        }

        # Hardcode first level for testing
        self.level = Level(1, SCREEN_WIDTH, SCREEN_HEIGHT, PADDING, HUD_H)

        # Needed to add temp input for player initialization
        self.temp = {"left": 0, "right": 0, "jump": 0}
        self.bodies = [
            Player(self.level.playfield.left  + 20, self.level.playfield.bottom - 20, self.temp),
            Player(self.level.playfield.right - 20, self.level.playfield.bottom - 20, self.temp),
        ]
        self.bodies[0].color = pygame.Color("#FF0000")
        self.bodies[1].color = pygame.Color("#0000FF")

    # listen for messages from players
    def handle_connect(self):
        while True:
            try:
                data, addr = self.server.recvfrom(4096)
                message = json.loads(data.decode("ascii"))
                self.handle_request(message, addr)
            except socket.error:
                break

    # Handle the requests from the players
    def handle_request(self, message, addr):
        type = message.get("type")
        data = message.get("data")

        # Assign player id based on when they connected
        if type == "connect":
            if addr not in self.players and len(self.players) < 2:
                player_id = len(self.players)
                self.players[addr] = {"player_id": player_id}
                print(f"Player {player_id} has connected from {addr}")
                self.send("connect", {"player_id": player_id}, addr)

        elif type == "disconnect":
            if addr in self.players:
                del self.players[addr]
                print(f"Player disconnected from {addr}")

        # Get inputs from clients and update the game state with defaults if there no values for input
        elif type == "move" and addr in self.players:
            player_id = self.players[addr]["player_id"]
            self.inputs[player_id]["x"] = data.get("x", 0.0)
            self.inputs[player_id]["jump"] = self.inputs[player_id]["jump"] or data.get("jump", False)

        elif type == "restart" and addr in self.players:
            self._restart()

        # Handle interactions with levers
        elif type == "interact" and addr in self.players:
            key = data.get("key")
            if key in (pygame.K_e, pygame.K_SLASH):
                for lever in self.level.levers:
                    lever.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": key}), self.bodies)

     # Restart resets the level and both players without quitting
    def _restart(self) -> None:
        self.level = Level(1, SCREEN_WIDTH, SCREEN_HEIGHT, PADDING, HUD_H)
        self.bodies = [
            Player(self.level.playfield.left + 20, self.level.playfield.bottom - 20, self.temp),
            Player(self.level.playfield.right - 20, self.level.playfield.bottom - 20, self.temp)
        ]
        self.bodies[0].color = pygame.Color("#FF0000")
        self.bodies[1].color = pygame.Color("#0000FF")
                
    # Update game state through server rather than game.py since server is authoritative
    def update(self, dt):
        for player_id in self.inputs:
            # Update player position for each player based on inputs received and apply collisions 
            # Similar structure to local in game.py
            body = self.bodies[player_id]
            body.update(dt, input_override=self.inputs[player_id])
            body.on_ground = False
            self._apply_wall_collisions(body)
            self._apply_bounds_player(body)
            self.inputs[player_id]["jump"] = False

            for hz in pygame.sprite.spritecollide(body, self.level.hazards, dokill=False):
                body.health = 0

            for collectible in self.level.collectibles:
                if collectible.active and body.rect.colliderect(collectible.rect):
                    collectible.active = False

        for lever in self.level.levers:
            lever.update(dt)

        for btn in self.level.pressure_buttons:
            btn.update(self.bodies)

        if self.level.exit_door:
            self.level.exit_door.update(self.bodies)

    def broadcast(self) -> None:
        # Allow clients to see the game state by sending state to clients after each update
        state = {
            "players": [
                {"x": self.bodies[0].rect.centerx, "y": self.bodies[0].rect.centery, "health": self.bodies[0].health},
                {"x": self.bodies[1].rect.centerx, "y": self.bodies[1].rect.centery, "health": self.bodies[1].health},
            ],
            "collectibles": [collectible.active for collectible in self.level.collectibles],
            "movable_walls": [walls.active for walls in self.level.movable_walls],
            "door_completed": self.level.exit_door.completed,
            "door_p1_touching": self.level.exit_door.p1_touching,
            "door_p2_touching": self.level.exit_door.p2_touching,
        }
        for addr in self.players:
            self.send("state", state, addr)

    # Send the messages to designated address
    def send(self, type, data, addr):
        message = {"type": type, "data": data}
        message = json.dumps(message).encode("ascii")
        self.server.sendto(message, addr)

    # Physics and collision from game.py
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

    
