import pygame

# Import files from the lost_in_time package for communcation between classes within
# Game File
from lost_in_time.level import Level
from lost_in_time.player import Player
from lost_in_time.title import Title
from lost_in_time.collectible import Collectible

# controls for p1 and p2 defined to be passed to player class
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

class Game:
    fps = 60
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080
    PADDING = 50
    HUD_H = 100
    

    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.level = Level(1, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.PADDING, self.HUD_H)
        self.title = Title(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        #self.title = Title(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.state = "title"

        # player starting positions defined to be passed to player class
        self.players = [
            Player(self.level.playfield.left + 20, self.level.playfield.bottom - 20, CONTROLS_PLAYER1),
            Player(self.level.playfield.right - 20, self.level.playfield.bottom - 20, CONTROLS_PLAYER2)
        ]
        # player colors defined to be different for p1 and p2
        self.players[0].color = pygame.Color("#FF0000")
        self.players[1].color = pygame.Color("#0000FF")

    def _apply_bounds_player(self, player: Player) -> None:
        # week2 example code to keep player within playfield
        player.rect.clamp_ip(self.level.playfield)

        # Claude debug for moving left even without touching left
        # Clamp_ip is clamping rect, essentially pulling the pos to the clamp
        # causing the "drift"
        player.pos.x = max(self.level.playfield.left, min(self.level.playfield.right, player.pos.x))
        player.pos.y = max(self.level.playfield.top, min(self.level.playfield.bottom, player.pos.y))

        # Checks player rect y value to see if player is on ground, when jump y value decreases causes if statement
        # to be invalid
        if player.rect.bottom >= self.level.playfield.bottom:
            player.on_ground = True
            player.velocity.y = 0
    
    # restart function to reset player position and collectibles without having to quit game, called in handle_event when 'r' key is pressed
    def _restart(self) -> None:
        self.level = Level(1, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.PADDING, self.HUD_H)
        self.players = [
            Player(self.level.playfield.left + 20, self.level.playfield.bottom - 20, CONTROLS_PLAYER1),
            Player(self.level.playfield.right - 20, self.level.playfield.bottom - 20, CONTROLS_PLAYER2)
        ]
        self.players[0].color = pygame.Color("#FF0000")
        self.players[1].color = pygame.Color("#0000FF")
        
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            # adding restart functionality to reset player position and collectibles without having to quit game
            if event.key == pygame.K_r and self.state == "play":
                self._restart()
        
        # handle 'title' state events like button clicks
        if self.state == "title":
            self.title.handle_event(event)
        
        # handle 'play' state events
        if self.state == "play":
            for player in self.players:
                player.handle_event(event)
            

    def update(self, dt: float) -> None:
        if self.state == "title":
            # check to see if play button click to transition from title to play
            if self.title.play_button.clicked:
                self.state = "play"
        if self.state == "play":
            # player movement + boundaries
            for player in self.players:
                player.update(dt)
                self._apply_bounds_player(player)
                # check for player collision with collectibles
                for collectible in self.level.collectibles:
                    if collectible.active and player.rect.colliderect(collectible.rect):
                        collectible.active = False
                        player.apply_jump_boost()

    def draw(self) -> None:
        if self.state == "title":
            # draw title screen
            self.title.draw(self.screen)
        elif self.state == "play":
            # play screen with level layouts and player starting positions
            self.screen.fill(pygame.Color("#474747"))
            self.level.draw(self.screen)
            for player in self.players:
                player.draw(self.screen)