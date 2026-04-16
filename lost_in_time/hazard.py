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

    def update(self, dt: float) -> None:
        pass


class MovingHazard(Hazard):
    """A hazard strip that bounces horizontally between min_x and max_x."""

    def __init__(
        self,
        topleft: tuple[int, int],
        *,
        color: pygame.Color,
        count: int = 1,
        spike_w: int = 20,
        spike_h: int = 30,
        direction: str = "up",
        min_x: int,
        max_x: int,
        speed: float = 150.0,
    ) -> None:
        super().__init__(topleft, color=color, count=count, spike_w=spike_w,
                         spike_h=spike_h, direction=direction)
        self.min_x = min_x   # left boundary (rect.left)
        self.max_x = max_x   # right boundary (rect.right)
        self._vx = float(speed)
        self._fx = float(topleft[0])  # sub-pixel x position

    def update(self, dt: float) -> None:
        self._fx += self._vx * dt
        if self._vx > 0 and self._fx + self.rect.width > self.max_x:
            self._fx = self.max_x - self.rect.width
            self._vx = -self._vx
        elif self._vx < 0 and self._fx < self.min_x:
            self._fx = self.min_x
            self._vx = -self._vx
        self.rect.x = int(self._fx)
