from src.blackjack.game import Game, Simple, Player, Dealer, AutoGame
from src.blackjack.deck import Deck, Card, Hand
from src.blackjack.player import Simple, Simple17
from escprint import esc
from typing import TypedDict, NamedTuple
import typing

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
    print_tname("*** TEST hand.split ***")
    hand = Hand("2","2")
    hand = hand.split(bet=20)
    assert hand[0].bet == 10, "Bet should be 10.0"
    hand[0].add("2")
    hand[0] = hand[0].split()
    assert hand[0][0].bet == 5, "Bet should be 5.0"
    assert hand[0][0].value() == 2 and hand[1][0].value == 2
    _print_succ()

# OTHER
def test_game():
    game = Game.create([
        ("Mike",),
        ("Dan",)
    ])
    game.start()

def test_print():
    player = Player("Mike")
    player.hit(Card("Ace"))
    player.hit(Card("2"))
    player.print()

def test_simple_strategy():
    print("Player: ")
    player = Player("self")
    player.hit(Card("King","hearts"))
    player.hit(Card("5", "spades"))
    print(f"{player.name} = {player.hand_value()}, Hit? -> {player.run_strategy()}")
    player.hit(Card("3", "clubs"))
    print(f"{player.name} = {player.hand_value()}, Hit? -> {player.run_strategy()}")
    ###
    print("Dealer: ")
    dealer = Dealer()
    dealer.hit(Card("King", "clubs"))
    dealer.hit(Card("6", "hearts"))
    print(f"{dealer.name} = {dealer.hand_value()}, Hit? -> {dealer.run_strategy()}")
    dealer.hit(Card("2", "spades"))
    print(f"{dealer.name} = {dealer.hand_value()}, Hit? -> {dealer.run_strategy()}")

def test_auto_game():
    auto_game = AutoGame.create(["Mike", "Dan", "John"])
    result = auto_game.start()
    print(result)

def test_simulate(n_times:int=10, print_sim:bool=False, wait:float|int=.1):
    players = [
        Player("Simple", strategy=Simple()),
        Player("Simple17", strategy=Simple17())
    ]

    auto_game = AutoGame(players=players)
    # auto_game = AutoGame.create(["Mike", "Dan", "John"])
    results = auto_game.simulate(n_times=n_times, print_sim=print_sim, wait=wait)

def _test_start():
    players = [
        Player("Mike", chips=1000),
        Player("Dan", chips=1000),
        # Player("John", chips=1000)
    ]

    game = Game(players=players, min_bet=15)

    max_n = game._get_player_max_name_len()

    game.play()

    for player in players:
        player.print(max_name_len=max_n)



if __name__ == "__main__":
    # test_is_blackjack()
    test_split_hand()
    # test_game()
    # test_simulate(n_times=1000, print_sim=True, wait=.01)

    # test_input_bet()
    # _test_start()

