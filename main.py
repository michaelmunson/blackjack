from escprint import esc
from src.blackjack.deck import Deck, Card
from src.blackjack.game import Game, Player

if __name__ == "__main__":
    esc.erase_screen()
    esc.cursor_to_top()
    deck = Deck(shuffle=True, num_decks=8)
    
    players = [
        Player("Mike"),
        Player("Daniel")
    ]

    game = Game(players=players, deck=deck)

    game.start()