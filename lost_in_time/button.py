import pygame

class Button:
    # Intialize button traits like position, text, and size of rect
    def __init__ (self, text: str, pos: tuple, width: int, height: int, rect_color: str = "#FFFFFF") -> None:
        self.text = text
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = pos
        self.rect_color = rect_color
        self.clicked = False
        self.font = pygame.font.SysFont("Times New Roman", 80, True)

    # Handle mouse button click
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
    
    # Draw rect + text within rect
    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, pygame.Color(self.rect_color), self.rect)
        button_label = self.font.render(self.text, True, pygame.Color("#000000"))
        screen.blit(button_label, (button_label.get_rect(center=self.rect.center)))