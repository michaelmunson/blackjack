from __future__ import annotations
from src.blackjack.deck import Card
from escprint import esc

### STRATEGY ###
class Strategy:
    def __init__(self) -> None:
        pass
    def run(self, player:Player, dealer:Dealer, ):
        pass

class Simple(Strategy):
    def __init__(self) -> None:
        super().__init__()
    
    def run(self, player:Player, players:list[Player]=[], dealer:Dealer=None) -> bool:
        return player.hand_value() < 16 

class Simple17(Strategy):
    def __init__(self) -> None:
        super().__init__()
    
    def run(self, player:Player, players:list[Player]=[], dealer:Dealer=None) -> bool:
        return player.hand_value() < 17 

### PLAYER ###
class Player: 
    def __init__(self, name:str, strategy:Strategy=Simple()) -> None:
        self.name = name
        self.strategy = strategy
        self.is_bust = False
        self.cards : list[Card] = []
    
    def hit(self, card:Card) -> bool:
        self.cards.append(card)
        if self.hand_value() > 21:
            self.is_bust = True
        return self.is_bust
    
    def hand_value(self) -> int:
        value = 0
        for card in self.cards:
            value += card.value

        if value > 21:
            i = 0
            while i < len(self.cards) and value > 21:
                card = self.cards[i]
                if card.rank == "Ace":
                    value -= 10
                i += 1

        return value
    
    def lowest_hand_value(self) -> int:
        value = 0
        for card in self.cards:
            if card.rank == "Ace":
                value += 1
            else:
                value += card.value
        return value

    def card_str_list(self) -> list:
        return list(map(lambda card: card.to_str(), self.cards))

    def show_cards(self) -> None:
        if (not self.is_bust):
            esc.print(f"{self.name}: {self.card_str_list()}", "green")
        else:
            esc.print(f"{self.name}: {self.card_str_list()}", "red")

    def print(self, max_name_len:int=0, dealer_hand_value:int=-1) -> None:
        card_str_arr = []
        for card in self.cards:
            card_str_arr.append(f"{card.to_str()}")

        pref_len = max_name_len - len(self.name)
        post_str = ""
        if pref_len > 0:
            for _ in range(pref_len):
                post_str+= " "
                
        esc.printf(
            (self.name, "red/strikethrough" if (self.is_bust or (dealer_hand_value > self.hand_value() and dealer_hand_value < 22)) else "Green/bold/underline"), post_str, 
            (f" ... {str(self.hand_value())} ... {' | '.join(card_str_arr)}", "red/strikethrough" if (self.is_bust or (dealer_hand_value > self.hand_value() and dealer_hand_value < 22)) else "Green/bold")
        )

    def reset(self) -> None:
        self.cards.clear()
        self.is_bust = False

    def run_strategy(self, dealer:Dealer=None, players:list[Player]=[]):
        strategy_name = type(self.strategy).__name__
        other_players = list(filter(lambda player: player != self, players))
        # strategy if chain
        return self.strategy.run(player=self, players=other_players, dealer=dealer)
        
class Dealer(Player):
    def __init__(self, strategy:Strategy=Simple17()) -> None:
        super().__init__("Dealer", strategy)

    def show_cards(self, hidden=True) -> None:
        card_str_list = self.card_str_list()
        if not hidden:
            if (not self.is_bust):
                esc.print(f"{self.name}: {card_str_list}", "green")
            else:
                esc.print(f"{self.name}: {card_str_list}", "red")
        else:
            for i in range(1, len(card_str_list)):
                card_str_list[i] = "*********"

            if (not self.is_bust):
                esc.print(f"{self.name}: {card_str_list}", "green")
            else:
                esc.print(f"{self.name}: {card_str_list}", "red")

    def print(self, hidden=True, max_name_len:int=0) -> None:
        card_str_arr = []
        for i in range(len(self.cards)):
            if hidden and i > 0:
                card_str_arr.append("*******")
            else:
                card_str_arr.append(f"{self.cards[i].to_str()}")

        pref_len = max_name_len - len(self.name)
        post_str = ""
        if pref_len > 0:
            for _ in range(pref_len):
                post_str+= " "

        esc.printf(
            (self.name, "red/strikethrough" if self.is_bust else "Blue/bold/underline"), post_str,
            (f" ... {'*' if hidden else str(self.hand_value())} ... {' | '.join(card_str_arr)}", "red/strikethrough" if self.is_bust else "Blue/bold")
        )

    def showing(self) -> int:
        if len(self.cards) > 0:
            return self.cards[0].value
        return 0