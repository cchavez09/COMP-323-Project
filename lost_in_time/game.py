import pygame

# Import files from the lost_in_time package for communcation between classes within
# Game File
from lost_in_time.level import Level
from lost_in_time.player import Player
#from lost_in_time.title import Title

class Game:
    fps = 60
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080
    PADDING = 50
    HUD_H = 100
    

    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.level = Level(1, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.PADDING, self.HUD_H)
        self.player = Player(self.level.spawn.x, self.level.spawn.y)
        #self.title = Title(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.state = "play"

    def _apply_bounds_player(self) -> None:
        # week2 example code to keep player within playfield
        self.player.rect.clamp_ip(self.level.playfield)

        # Claude debug for moving left even without touching left
        # Clamp_ip is clamping rect, essentially pulling the pos to the clamp
        # causing the "drift"
        self.player.pos.x = max(self.level.playfield.left, min(self.level.playfield.right, self.player.pos.x))
        self.player.pos.y = max(self.level.playfield.top, min(self.level.playfield.bottom, self.player.pos.y))

        # Checks player rect y value to see if player is on ground, when jump y value decreases causes if statement
        # to be invalid
        if self.player.rect.bottom >= self.level.playfield.bottom:
            self.player.on_ground = True
            self.player.velocity.y = 0
        
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
        
        # handle 'play' state events
        if self.state == "play":
            self.player.event(event)
            

    def update(self, dt: float) -> None:
        #if self.state == "title":
            #if self.title.play_button.clicked:
                #self.state = "play"
        if self.state == "play":
            self.player.update(dt)
            self._apply_bounds_player()

    def draw(self) -> None:
        if self.state == "title":
            self.title.draw(self.screen)
        elif self.state == "play":
            self.screen.fill(pygame.Color("#474747"))
            self.level.draw(self.screen)
            self.player.draw(self.screen)