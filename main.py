import pygame
import sys

from lost_in_time.game import Game


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Lost in Time")

    server_ip = sys.argv[1] if len(sys.argv) > 1 else None

    # Start game with server IP if provided
    game = Game(server_ip = server_ip)
    clock = pygame.time.Clock()

    running = True
    
    while running:
        dt = clock.tick(game.fps) / 1000.0
        dt = min(dt, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event)
                
        game.update(dt)
        game.draw()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()