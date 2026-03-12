import pygame


class Hazard(pygame.sprite.Sprite):
    def __init__(
        self,
        topleft: tuple[int, int],
        *,
        color: pygame.Color,
        count: int = 1,
        spike_w: int = 20,
        spike_h: int = 30,
        # direction of hazard strip, either up/down for vertical or left/right for horizontal
        direction: str = "up",
    ) -> None:
        super().__init__()
        self.color = color
        # number of spikes in strip
        self.count = count
        # width of spikes
        self.spike_w = spike_w
        # height of spikes
        self.spike_h = spike_h
        self.direction = direction

        # rect covers entire hazard strip for collision detection and image is drawn separately in draw method
        if direction in ("up", "down"):
            self.rect = pygame.Rect(topleft[0], topleft[1], spike_w * count, spike_h)
        # if direction is horizontal, swap width and height for rect
        else:
            self.rect = pygame.Rect(topleft[0], topleft[1], spike_h, spike_w * count)
