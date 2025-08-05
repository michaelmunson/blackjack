import pytest
from .game import Game, Simulation
from blackjack.player import Player, Simple
from blackjack.deck import Deck

def test_game_creation():
    players = [Player("Test", strategy=Simple())]
    game = Game(players=players)
    assert len(game.players) == 1
    assert game.min_bet == 15

def test_simulation():
    players = [Player("Test", strategy=Simple())]
    sim = Simulation(players=players)
    results = sim.run(n_times=10)
    assert len(results) == 1
    assert "Test" in results 