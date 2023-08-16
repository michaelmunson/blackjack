# BlackJack

```python
from src.blackjack.game import Game

if __name__ == "__main__":
    game = Game.create([
        ("Mike",),
        ("Dan",)
    ])

    game.start()

```