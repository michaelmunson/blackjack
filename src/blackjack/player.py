from __future__ import annotations
from src.blackjack.deck import Card, Hand, SplitHand
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
    name:str
    strategy:Strategy
    hand:Hand|SplitHand
    chips:int
    bet:int
    is_out:bool
    has_insurance:bool
    is_split:bool
    insurance:int

    def __init__(self, name:str, chips:int=0, strategy:Strategy=Simple()) -> None:
        self.name = name
        self.strategy = strategy
        self.hand = Hand()
        self.chips = chips
        self.bet = 0
        self.insurance = 0
        self.is_out = False
        self.is_split = False
        self.has_insurance = False
    
    def hit(self, card:Card) -> bool:
        self.hand.add(card)
        return self.is_bust()
    
    def is_bust(self) -> bool:
        return self.hand.is_bust()

    def is_blackjack(self) -> bool:
        return self.hand.is_blackjack()
    
    def can_split(self) -> bool:
        return self.hand[0].rank == self.hand[1].rank and self.hand.len() == 2

    def hand_value(self) -> int:
        return self.hand.value()
    
    def lowest_hand_value(self) -> int:
        return self.hand.lowest_value()

    def card_str_list(self) -> list:
        return list(map(lambda card: card.to_str(), self.hand))

    def print(self, max_name_len:int=0, dealer:Dealer=None) -> None:
        dealer_hand_value = -1 if dealer == None else dealer.hand_value()

        card_str_arr = []
        for card in self.hand:
            card_str_arr.append(f"{card.to_str()}")

        pref_len = max_name_len - len(self.name)
        post_str = ""
        if pref_len > 0:
            post_str = " " * pref_len
        
        print_style = "red" if (self.is_bust() or (dealer_hand_value > self.hand_value() and dealer_hand_value < 22) or (dealer_hand_value == 21 and len(dealer.hand) == 2)) else "Green/bold"
        print_strike = "strike" if (self.is_bust() or (dealer_hand_value > self.hand_value() and dealer_hand_value < 22) or (dealer_hand_value == 21 and len(dealer.hand) == 2)) else ""
        esc.printf(
            (self.name, print_style, print_strike, "underline"), (post_str,print_style), 
            (f" ... ${self.chips} -> ${self.bet}", print_style),
            (f"\n{post_str + (' '*len(self.name))} ... {' | '.join(card_str_arr)}", print_style)

        )

    def reset(self) -> None:
        self.hand.clear()
        self.bet = 0
        self.out = True

    def place_bet(self, bet_amount:int, min_bet:int=15) -> int:
        if self.chips < bet_amount:
            return -2
        
        if min_bet > bet_amount:
            return -1
        
        self.bet += bet_amount
        self.chips -= bet_amount

        return self.bet

    def input_bet(self, min_bet:int=15) -> int:
        
        esc.printf(
            f"{self.name} (", [f"${self.chips}", "Green/underline"], ") What is your bet?"  
        )

        bet_amount = int(
            esc.input("$", input="Green", end="")
        )
        
        bet_placed = self.place_bet(bet_amount=bet_amount, min_bet=min_bet)

        if bet_placed < 0:
            esc.erase_prev(n=4)
            if bet_placed == -1:
                esc.print(f"Bet amount (${bet_amount}) lower than Min Bet (${min_bet})", "red")
            elif bet_placed == -2:
                esc.print(f"Insufficient Chips (${self.chips}) to Cover Bet (${bet_amount})","red")
            return self.input_bet(min_bet=min_bet)
        
        return bet_placed

    def run_strategy(self, dealer:Dealer=None, players:list[Player]=[]):
        other_players = list(filter(lambda player: player != self, players))
        return self.strategy.run(player=self, players=other_players, dealer=dealer)
        
class Dealer(Player):
    def __init__(self, strategy:Strategy=Simple17()) -> None:
        super().__init__("Dealer", strategy)

    def print(self, hidden=True, max_name_len:int=0) -> None:
        card_str_arr = []
        for i in range(len(self.hand)):
            if hidden and i > 0:
                card_str_arr.append("*******")
            else:
                card_str_arr.append(f"{self.hand[i].to_str()}")

        pref_len = max_name_len - len(self.name)
        post_str = ""
        if pref_len > 0:
            for _ in range(pref_len):
                post_str+= " "

        esc.printf(
            (self.name, "red/strikethrough" if self.is_bust() else "Blue/bold/underline"), post_str,
            (f" ... {' | '.join(card_str_arr)}", "red/strikethrough" if self.is_bust() else "Blue/bold")
        )

    def showing(self) -> int:
        if len(self.hand) > 0:
            return self.hand[0].value
        return 0