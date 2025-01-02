import asyncio
from game.game import Game

def main():
    game = Game()
    asyncio.run(game.run())

if __name__ == "__main__":
    main()