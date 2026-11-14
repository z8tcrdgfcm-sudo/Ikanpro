import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame

from isekai import sfx
from isekai.game import Game


def main():
    pygame.init()
    sfx.init()
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
