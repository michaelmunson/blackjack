# BlackJack
Python library for playing/simulating Black Jack games. 
Create strategies and simulate them. Inspired by and with help from Daniel Tarrant.

## Usage
### Playing a Game
```python
from src.blackjack.game import Game
from src.blackjack.player import Player, Dealer

players = [
    Player("Mike", chips=1000),
    Player("Dan", chips=1000)
]

dealer = Dealer()

deck = Deck(shuffle=True, num_decks=8)

game = Game(
    players=players, 
    dealer=dealer,
    deck=deck, 
    min_bet=15,
    hit_on_soft_17=True
)

game.start()
```

### Simulating Games
```python
from src.blackjack.game import Simulation
from src.blackjack.player import Player, Simple

sim = Simulation(
    players=[
        Player("Mike", chips=10000, strategy=Simple()),
        Player("Dan", chips=10000, strategy=Simple())
    ],
    min_bet=15
)

sim_results = sim.run(n_times=1000)

sim_results.print()
```
or, if you want to see the results in real time
```python
# set print_sim to True
# set a wait time (float value), this sets the time it takes between rounds. 
sim_results = sim.run(n_times=1000, print_sim=True, wait=.01)
```

#### Simulation Results
**Simulation.run** returns a dict, whose [key,value] pairs are [player.name, PlayerSimulationResults]. The class PlayerSimulationResults is a NamedTuple class of the following fields:
```python
player:Player
rounds:int
hands:int
won:int
pushed:int
busted:int
net:int
win_rate:float
```
These results are derived from a list of **PlayerResults** instances. These can be found @ player.results

### Creating a Strategy

To create the stragey, create a class that extends the **Strategy** class.

The class can have 3 methods:
1. **init_state**(self) -> None:
* Used to initialize the state field to keep a player "memory". (example below)
2. **decide_hands**(self, player:Player) -> int ... (optional)
* This method takes a **player** as an argument, and returns the number of hands (integer) the player will play during that round.
* If this method is excluded from your strategy class, the number of hands will default to 1.
* If this method returns None, the number of hands will default to 1. 
3. **decide_bet**(self,player:Player, min_bet:int) -> int ... (optional)
* This method takes a **player**, and the **min_bet** as an argument, and returns the amount the player will bet (integer) during that round.
* If this method is excluded, the player bet will default to the minimum bet provided. (15 is the default)
* If this method returns None, the player bet will default to the minimum bet provided.
4. **decide**(self, player:Player, choices:list[str], dealer:Dealer, players:list[Player]) -> str ... (required)
* This method takes as arguments a **player**, a list of available **choices** (ex. ["stay","hit","double down", "split", "insurance"]), a **dealer**, and a list of other **players**. 
* The method returns a str, indicating which of the available choices the player should make. 
* IF method returns None, the decision will be interpreted as STAY

#### Examples

Here is an example of the default strategy (Simple) that all simulated players have, unless another is specified. This strategy simply hits if the players hand value is lower than 16. 

```python
from src.blackjack.player import Player, Strategy, STAY, HIT

class Simple(Strategy):
    # include these arguments, even if they're not used
    def decide(self, player, choices, dealer, players):
        return HIT if player.hand_value() < 16 else STAY
```

Here is a more complex example.

```python
from random import randint 
from src.blackjack.player import Player, Strategy, STAY, HIT, INSURANCE, DOUBLE_DOWN, SPLIT

class MoreComplex(Strategy):
    # randomly decide between 1 and 2 hands
    def decide_hands(self, player):
        # include these arguments, even if they're not used
        return randint(1,2)
    # if the player is net positive on chips, bet twice the amount
    def decide_bet(self, player, min_bet):
        # include these arguments, even if they're not used
        if player.chips > player.init_chips:
            return int(2 * min_bet)
    #
    def decide(self, player, choices, dealer, players):
        # include these arguments, even if they're not used
        player_val = player.hand_value()

        if INSURANCE in choices:
            return INSURANCE
        
        elif dealer.showing() in [4,5,6]:
            return STAY
        
        elif SPLIT in choices:
            return SPLIT

        elif DOUBLE_DOWN in choices and player_val <= 13 and player_val >= 11:
            return DOUBLE_DOWN

        elif player_val < dealer.showing() + 10 and player_val < 16:
            return HIT

        return STAY
```

If you want to keep a "memory" of the previous games, use the Strategy.state field, in conjunction with the .init_state() method and the .after() method.
```python
from src.blackjack.player import Strategy

class CardCounting(Strategy):
    # initialize state field
    def init_state(self) -> None:
        self.state = {
            "Aces" : 0
        }
    # after round is over
    def after(self, player, dealer, players):
        if "Ace" in map(lambda card: card.rank, player.hand):
            self.state["Aces"] += 1 
        
        for p in players:
            if "Ace" in map(lambda card: card.rank, p.hand):
                self.state["Aces"] += 1

        if "Ace" in map(lambda card: card.rank, dealer.hand):
            self.state["Aces"] += 1 

```

### Using your Strategy
```python
from src.blackjack.game import Simulation
from src.blackjack.player import Player
from path/to/strategy import MoreComplex

sim = Simulation(
    players=[
        Player("Mike", chips=10000, strategy=MoreComplex()),
        Player("Cheater", chips=10000, strategy=CardCounting())
    ],
    min_bet=15
)

sim_results = sim.run(n_times=10000)

sim_results.print()

```

### *Useful* Player Fields & Methods
### Fields
```python 
# players hand
hand:Hand
# amount of chips the player started with
init_chips:int
# amount of chips player has now
chips:int
# current bet amount
bet:int
# current insurance amount
insurance:int
# list of PlayerResults 
results:list[PlayerResults]
```
#### Methods

* **.has_blackjack**() -> bool
    * returns whether or not the player has blackjack

* **.can_split**() -> bool
    * returns whether the player can split their hand

* **.hand_value**() -> int
    * returns the highest value of the players hand that is still playable. Meaning if the Player has [King, Ace], it will return 21, but if the player has [King, Ace, 3], it will return 14.

* **.lowest_hand_value**() -> int
    * returns the lowest possible hand value. Essentially turns all aces into 1.

### *Useful* Dealer Fields & Methods

* **.showing**() -> int
    * returns the value (integer) of the visible card the dealer is showing

* **.showing_ace**() -> bool
    * returns whether or not the dealer is showing an ace

### Hand & Card Classes
A Player instance has a field **hand**, which is an instance of the **Hand** class. 

#### Hand
The hand class is essentially a list of **Card** instances

#### Card
The Card class has two fields, **rank** and **suit**
```python
class Card(
    rank: str,
    suit: str,
)
```

#### Example
```python
from src.blackjack.player import Player
from src.blackjack.deck import Card, Hand

mike = Player("Mike")
hand = mike.hand

hand.add(Card("Ace","Spades"))
hand.add(Card("King", "Diamonds"))

print(hand[0].rank) # -> Ace
print(hand[0].suit) # -> Spades
print(hand[0].value) # -> 11
print(hand.value()) # -> 21

```