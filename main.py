"""Save the Ocean — Turtle Game entry point."""

import pygame
import pygame.freetype

from game import config as cfg
from game.states import GameSession
from game.world.assets import ensure_assets, reload_assets
from game.world.display import Display


def main():
    pygame.init()
    pygame.freetype.init()
    pygame.display.set_caption(cfg.TITLE)

    display = Display()
    ensure_assets()
    reload_assets()

    clock = pygame.time.Clock()
    session = GameSession(display.virtual)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                display.handle_resize(event.w, event.h)
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_F11, pygame.K_f):
                    display.toggle_fullscreen()
                else:
                    session.handle_event(event)
            else:
                session.handle_event(event)

        session.update()
        session.draw()
        display.present()
        pygame.display.flip()
        clock.tick(cfg.FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
