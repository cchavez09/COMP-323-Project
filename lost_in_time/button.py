import pygame

class Button:
    # Intialize button traits like position, text, and size of rect
    def __init__ (self, text: str, pos: tuple, width: int, height: int) -> None:
        self.text = text
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = pos
        self.clicked = False

    # Handle mouse button click
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
    
    # Draw rect + text within rect
    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, pygame.Color("#2E43FC"), self.rect)
        font = pygame.font.SysFont("Times New Roman", 80, True)
        button_label = font.render(self.text, True, pygame.Color("#000000"))
        screen.blit(button_label, (self.rect.centerx - button_label.get_width() // 2, 
                                   self.rect.centery - button_label.get_height() // 2))