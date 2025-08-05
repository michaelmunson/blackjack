from blackjack.game import Game, Simple, Player, Dealer, Simulation
from blackjack.deck import Deck, Card, Hand
from blackjack.player import Simple, Simple17, PseudoPlayer, Strategy, INSURANCE, SPLIT, STAY, HIT, DOUBLE_DOWN
from random import randint
from escprint import esc
from typing import TypedDict, NamedTuple
import typing

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

print_tname = esc.create_fn("White")
def _print_succ():
    esc.print("✔︎ All Tests Passed", "Green")
def _print_err():
    esc.print("𐄂 Test Failed", "red")

## ACTUAL TESTS

def test_hand():
    esc.print("*** Test Hand Methods ***", "White")
    try: 
        hand = Hand(Card("Ace","hearts"), Card("9", "diamonds"), Card("8","spades"))
        assert hand.value() == 18, "hand.value() == 18"
        hand = Hand(Card("Ace","spades"), Card("Ace","diamonds"), Card("Ace", "hearts"), Card("2", "hearts"))
        assert hand.value() == 15, "hand.value() == 15"
        assert hand.lowest_value() == 5, "hand.low_value() == 5"
        _print_succ()
    except AssertionError as error:
        _print_err()

def test_is_blackjack():
    print_tname("*** TEST Hand.is_blackjack")
    try:
        hand = Hand(Card("Ace"), Card("King"))
        assert hand.is_blackjack(), "Hand (Ace,King) should return blackjack"
        hand = Hand("King","9")
        assert not hand.is_blackjack(), "Hand (King,9) should return NOT blackjack"
        _print_succ()
    except AssertionError as error:
        _print_err()
        print(error)

def test_input_bet():
    print_tname("*** Test Input Bet ***")
    init_chips = 1000
    player = Player("Mike", chips=init_chips)
    bet = player.input_bet(min_bet=15)
    assert player.chips == (init_chips - bet), "Discrepancy between difference between initial chips and bet amount, and actual result."
    _print_succ()

def test_split_hand():
    print_tname("*** TEST Player.split_hand ***")
    player = Player("Mike", 1000)
    player.bet = 100
    player.hand = Hand("5","5")
    player.split_hand()
    assert player.pseudos[0].hand.len() == 1 and player.pseudos[1].hand.len() == 1, "Hand length should be 1"
    assert player.pseudos[0].hand[0].value == 5 and player.pseudos[1].hand[0].value == 5, "Hand values should be 5"
    assert player.bet == 200, "Player bet should be 200"
    _print_succ()

def test_pseudo_place_bet():
    print_tname("*** TEST PseudoPlayer.place_bet ***")
    player = Player("Mike",chips=1000)
    pseudo = PseudoPlayer("Mike-pseudo",parent=player, bet=15)
    # print(player.chips)
    # print(f"bet: {pseudo.bet}")
    pseudo.place_bet(15)
    # print(f"bet: {pseudo.bet}")
    # print(f"player chips = {player.chips}")
    assert pseudo.bet == 30, "Pseudo bet should be 30"
    assert player.chips == 970, "Player chips should be 970"
    assert player.bet == 30, "Player bet should be 30"
    _print_succ()

# OTHER
def test_game():
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

def test_print():
    player = Player("Mike")
    player.hit(Card("Ace"))
    player.hit(Card("2"))
    player.print()

def test_start():
    players = [
        Player("Mike", chips=1000),
        # Player("Dan", chips=1000),
        # Player("John", chips=1000)
    ]

    game = Game(players=players, min_bet=15)

    game.start()

def test_sim_start():
    sim = Simulation(
        players=[
            Player("Mike",1000)
        ],
        min_bet=15
    )

    sim._start(is_print=True)

def test_sim_run(n_times:int=1, print_sim:bool=True, wait:float=.01):
    ccstrat = CardCounting()
    sim = Simulation(
        players=[
            Player("Mike",10000, strategy=MoreComplex()),
            Player("Cheater",10000, strategy=ccstrat)
        ],
        min_bet=15
    )

    sim_results = sim.run(n_times=n_times, print_sim=print_sim, wait=wait)
    
    sim_results.print()

    print(ccstrat.state)
    # for player in sim_results.players:
    #     print(player.chips - player.init_chips)

    # print(sum(res.won for res in mike.results))


if __name__ == "__main__":
    # test_is_blackjack()
    # test_split_hand()
    # test_game()
    # player = Player("Mike", 100)
    # pseudo = PseudoPlayer("Mike1",parent=player, bet=player.bet)
    # pseudo.hit(Card("5"))
    # print(pseudo.hand)
    # test_input_bet()
    # test_pseudo_place_bet()
    # test_split_hand()
    # test_sim_start()
    # test_sim_run(n_times=10000, print_sim=False, wait=.1)

    test_sim_run(n_times=1000, print_sim=False, wait=.01)
    # hand = Hand("King","King")
    # print(hand)
    # if "Ace" in map(lambda card: card.rank, hand):
    #     print(True)
