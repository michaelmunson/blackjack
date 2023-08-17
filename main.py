from src.blackjack.player import Strategy, Player, Dealer
from src.blackjack.game import AutoGame

class NeverHit(Strategy):
    # include these arguments even if you're not using them
    def run(self, player=None, players=None, dealer=None):
        return False
    
class Simple17(Strategy):
    def run(self, player=None, players=None, dealer=None):
        return player.hand_value() < 18
    
class DealerAce(Strategy):
    # include these arguments even if you're not using them
    def run(self, player=None, players=None, dealer=None):
        if dealer.showing() == 11 and player.hand_value() < 17:
            return True
        else:
            return player.hand_value() < 16

players = [
    Player("Mike", strategy=Simple17()),
    Player("Daniel", strategy=NeverHit())
]

auto_game = AutoGame(players=players)
# auto_game = AutoGame.create(["Mike", "Dan", "John"])
results = auto_game.simulate(n_times=1000000)
