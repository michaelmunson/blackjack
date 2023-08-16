from src.blackjack.game import Game, Simple, Player
from src.blackjack.player import NeverHit

if __name__ == "__main__":
    game = Game.create([
        ("Mike",),
        ("Dan",)
    ])

    game.start()