# BlackJack
Python library for playing/simulating Black Jack games. 
Create strategies and simulate them. 

## Usage
### Playing a Game
There are two ways to play a game
```python
from src.blackjack.game import Game
from src.blackjack.player import Player, Dealer

players = [
    Player("Mike"),
    Player("Dan")
]

dealer = Dealer()

deck = Deck(shuffle=True, num_decks=8)

game = Game(players=players, dealer=dealer, deck=deck)

game.start()
```
or
```python
from src.blackjack.game import Game

game = Game.create([
    ("Mike",),
    ("Dan",)
])

game.start()
```

### Simulating Games
```python
from src.blackjack.game import Game, Player, Dealer
from src.blackjack.player import Player, Simple

players = [
    Player("Mike", strategy=Simple()),
    Player("Dan", strategy=Simple())
]

auto_game = AutoGame(players=players)

results = auto_game.simulate(n_times=10000)
```

### Creating a Strategy

To create the stragey, create a class that extends the **Strategy** class.

Your strategy class should include a **run** method, which takes the arguments **player**, **players**, and **dealer**. The **run** method should return a boolean value, indicating whether or not the player should hit. 

#### Examples

Here we create a strategy in which the player never hits.
```python
from src.blackjack.player import Strategy, Player, Dealer

class NeverHit(Strategy):
    # include these arguments even if you're not using them
    def run(self, player:Player, players:list[Player], dealer:Dealer) -> bool:
        return False
```
Here we create a strategy in which the player always hits if the value of their hand is below 17

```python
from src.blackjack.player import Strategy, Player, Dealer

class Simple17(Strategy):
    def run(self, player:Player, players:list[Player], dealer:Dealer) -> bool:
        return player.hand_value() < 17
```
Here we create a strategy in which the player hits if the dealer has an ace, and their hand value is below 17. If the dealer doesn't have an ace, the player will hit if the value of their hand is below 16.

```python
from src.blackjack.player import Strategy, Player, Dealer

class DealerAce(Strategy):
    def run(self, player:Player, players:list[Player], dealer:Dealer) -> bool:
        if dealer.showing() == 11 and player.hand_value() < 17:
            return True
        else:
            return player.hand_value() < 16
```
#### Running your Strategy
Now to run your strategy, simply attach it to a player when creating the simulation.

```python
from src.blackjack.game import Game, Player, Dealer
from src.blackjack.player import Player, Simple
from ... import NeverHit, DealerAce

players = [
    Player("Never Hitter", strategy=NeverHit()),
    Player("Dealer Acer", strategy=DealerAce())
]

auto_game = AutoGame(players=players)

results = auto_game.simulate(n_times=10000)
```