from __future__ import annotations
from src.blackjack.deck import Deck, Card
from src.blackjack.player import Player, Dealer, Simple
from escprint import esc
from collections import namedtuple


### GAME ###
class Game:
    def __init__(self, players:list[Player], dealer:Dealer=Dealer(), deck:Deck=Deck(shuffle=True, num_decks=8)) -> None:
        self.players = players
        self.dealer = dealer
        self.deck = deck
        self.curr_player = 0

    def hit_player(self, player:Player) -> bool:
        card = self.deck.deal()
        return player.hit(card)

    def add_player(self,player:Player) -> None:
        self.players.append(player)

    def start(self):
        esc.enable_alt_buffer()
        esc.cursor_to_top()
        # initial deal
        for i in range(2):
            self.hit_player(self.dealer)
            for player in self.players:
                self.hit_player(player)
        # print cards
        print("===* Initial Deal *===")
        self.dealer.show_cards()
        for player in self.players:
            player.show_cards()
        # player hit rounds
        for player in self.players:
            player_choice = "y"
            while player_choice == "y" and not player.is_bust:
                player_choice = str.lower(input(f"{player.name}: Hit? [y/N]"))
                if player_choice == "y":
                    self.hit_player(player)
                player.show_cards()
        # dealer hit round
        while self.dealer.hand_value() < 17:
            print("Dealer Hit:")
            self.hit_player(self.dealer)
            
        self.dealer.show_cards(hidden=False)
        print("Dealer value: ", self.dealer.hand_value()) 
        # calculate winners
        results = self.get_results()

        print()
        # print winners
        esc.print("Winners", "Green", "underline", "bold")
        for player in results.won:
            player.show_cards()
        print()
        if len(results.tied) > 0:
            esc.print("Tied", "White", "underline", "bold")
            for player in results.tied:
                player.show_cards()
        print()
        esc.print("Losers", "Red", "underline", "bold")
        for player in results.lost:
            player.show_cards()
        print()
        if input("Play again? [y/N]") == "y":
            self.reset()
            esc.erase_screen()
            self.start()
        else:
            esc.disable_alt_buffer()

    def reset(self):
        [player.reset() for player in self.players]
        self.dealer.reset()

    def get_results(self) -> tuple:
        GameResults = namedtuple("GameResults", ("won", "tied", "lost")) 
        winners = []
        tied = []
        losers = []
        if self.dealer.is_bust:
            for player in self.players:
                if not player.is_bust:
                    winners.append(player)
                else:
                    losers.append(player)
        else:
            dealer_hand_value = self.dealer.hand_value()
            for player in self.players:
                if not player.is_bust:
                    if player.hand_value() > dealer_hand_value:
                        winners.append(player)
                    elif player.hand_value() < dealer_hand_value:
                        losers.append(player)
                    elif player.hand_value() == dealer_hand_value:
                        tied.append(player)
                else:
                    losers.append(player)

        return GameResults(won=winners, tied=tied, lost=losers)

    @staticmethod
    def create(players:list[str|tuple]) -> Game:
        players = [
            Player(name=player[0],strategy=player[1] if len(player) > 1 else Simple) if isinstance(player,tuple) else Player(name=player)
            for player in players
        ]
        return Game(players=players)

class AutoGame(Game):
    def __init__(self, players: list[Player], dealer: Dealer = Dealer(), deck: Deck = Deck(shuffle=True), strategy:str="Rule of Thumb") -> None:
        super().__init__(players, dealer, deck)
