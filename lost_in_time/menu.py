import pygame

from lost_in_time.button import Button

class Menu:
    def __init__(self, screen_width: int, screen_height: int, menu: str) -> None:
        # Initialized screen tracking, buttons and fonts for title name and header
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.menu = menu
        self.next_screen = None
        self.buttons = []
        self.title_font = pygame.font.SysFont("Times New Roman", 200, True, True)
        self.header_font = pygame.font.SysFont("Times New Roman", 100, True)
        self.background_color = "#A7A7A7"

        # Creation of buttons for each menu screen
        if self.menu == "title":
            self.buttons.append(Button("Play", (self.screen_width // 2, 500), 180, 100, "#8DF78DFF"))
        elif self.menu == "game_mode":
            self.buttons.append(Button("Local", (self.screen_width // 2 - 300, 600), 220, 100, self.background_color))
            self.buttons.append(Button("Multiplayer", (self.screen_width // 2 + 400, 600), 450, 100, self.background_color))
            self.buttons.append(Button("Back", (self.screen_width // 2, 900), 450, 100, self.background_color))
        elif self.menu == "level_select":
            self.buttons.append(Button("1", (self.screen_width // 2 - 300, 600), 220, 100, self.background_color))
            self.buttons.append(Button("2", (self.screen_width // 2 - 150, 600), 220, 100, self.background_color))
            self.buttons.append(Button("3", (self.screen_width // 2, 600), 220, 100, self.background_color))
            self.buttons.append(Button("4", (self.screen_width // 2 + 150, 600), 220, 100, self.background_color))
            self.buttons.append(Button("5", (self.screen_width // 2 + 300, 600), 220, 100, self.background_color))
            self.buttons.append(Button("Back", (self.screen_width // 2, 900), 450, 100, self.background_color))

    # event in relation to button click
    def handle_event(self, event: pygame.event.Event) -> None:
        for button in self.buttons:
            button.handle_event(event)
            # Assign next_screen to allow tranistion between screen menus in relation to 
            # button clicks
            if button.clicked: 
                if button.text == "Play":
                    self.next_screen = "game_mode"
                if button.text == "Local":
                    self.next_screen = "level_select"
                if button.text == "Back":
                    self.next_screen = "back"
                if button.text == "1":
                    self.next_screen = "game"
                if button.text == "2":
                    self.next_screen = "game2"
                if button.text == "3":
                    self.next_screen = "game3"
                if button.text == "4":
                    self.next_screen = "game4"
                    
    # draw background 
    def draw(self, screen: pygame.Surface) -> None:
        # Draw menu design while also drawing buttons for their respective menu
        screen.fill(pygame.Color(self.background_color))
        game_name = self.title_font.render("Lost in Time", True, pygame.Color("#000000"))
        screen.blit(game_name, (game_name.get_rect(center=(self.screen_width // 2, 125))))

        if self.menu == "game_mode":
            game_mode_text = self.header_font.render("Choose Game Mode", True, pygame.Color("#000000"))
            screen.blit(game_name, (game_name.get_rect(center = (self.screen_width // 2, 125))))
            screen.blit(game_mode_text, (game_mode_text.get_rect(center = (self.screen_width // 2, 350))))
        elif self.menu == "level_select":
            level_select_text = self.header_font.render("Choose Level", True, pygame.Color("#000000"))
            screen.blit(level_select_text, (level_select_text.get_rect(center = (self.screen_width // 2, 350))))

        for button in self.buttons:
            button.draw(screen)


