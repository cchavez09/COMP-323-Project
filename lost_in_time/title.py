import pygame

from lost_in_time.button import Button

class Title:
    def __init__(self, screen_width: int, screen_height: int) -> None:
        # Creation of button
        self.play_button = Button("Play", (screen_width // 2, 350), 300, 100)

    # event in relation to button click
    def handle_event(self, event: pygame.event.Event) -> None:
        self.play_button.handle_event(event)

    # draw background 
    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(pygame.Color("#A7A7A7"))
        self.play_button.draw(screen)