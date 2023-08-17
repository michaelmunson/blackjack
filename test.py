from src.blackjack.game import Game, Simple, Player, Dealer, AutoGame
from src.blackjack.deck import Deck, Card
from src.blackjack.player import Simple

def test_game():
    game = Game.create([
        ("Mike",),
        ("Dan",)
    ])
    game.start()

def test_player_show_cards():
    player = Player("Mike")
    dealer = Dealer()
    for x in [dealer, player]:
        x.hit(Card("King","hearts"))
        x.hit(Card("Jack","spades"))
        x.print(max_name_len=len(dealer.name))

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
        Player("Mike", strategy=Simple()),
        Player("Daniel", strategy=Simple())
    ]

    auto_game = AutoGame(players=players)
    # auto_game = AutoGame.create(["Mike", "Dan", "John"])
    results = auto_game.simulate(n_times=n_times, print_sim=print_sim, wait=wait)

if __name__ == "__main__":
    test_game()
    # test_simulate(n_times=10000, print_sim=True, wait=.00001)
    