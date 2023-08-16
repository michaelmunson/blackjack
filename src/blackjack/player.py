from __future__ import annotations
from escprint import esc

### STRATEGY ###
class Strategy:
    def __init__(self, player:Player) -> None:
        self.player = player
class NeverHit(Strategy):
    def __init__(self, player: Player) -> None:
        super().__init__(player=player)
    
    def run(self) -> bool:
        return False  
class Book(Strategy):
    def __init__(self, player: Player) -> None:
        super().__init__(player=player)
    
    def run(self, dealer:Dealer) -> bool:
        return False
class Simple(Strategy):
    def __init__(self, player: Player) -> None:
        super().__init__(player=player)
    
    def run(self) -> bool:
        return self.player.hand_value() < 16 
class Simple17(Strategy):
    def __init__(self, player: Player) -> None:
        super().__init__(player=player)
    
    def run(self) -> bool:
        return self.player.hand_value() < 16 

### PLAYER ###
class Player(list):
    def __init__(self, name:str, strategy:Strategy=Simple) -> None:
        self.name = name
        self.strategy = strategy(player=self)
        self.is_bust = False
    
    def hit(self, card:Card) -> bool:
        self.append(card)
        if self.hand_value() > 21:
            self.is_bust = True
        return self.is_bust
    
    def hand_value(self) -> int:
        value = 0
        for card in self:
            value += card.value
        
        if value > 21:
            i = 0
            while i < len(self) and value > 21:
                card = self[i]
                if card.rank == "Ace":
                    value -= 10
                i += 1

        return value
    
    def card_str_list(self) -> list:
        return list(map(lambda card: card.to_str(), self))

    def show_cards(self) -> None:
        if (not self.is_bust):
            esc.print(f"{self.name}: {self.card_str_list()}", "green")
        else:
            esc.print(f"{self.name}: {self.card_str_list()}", "red")
    
    def reset(self) -> None:
        self.clear()
        self.is_bust = False

class Dealer(Player):
    def __init__(self, strategy:Strategy=Simple17) -> None:
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
