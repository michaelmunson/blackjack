from __future__ import annotations
from src.blackjack.deck import Card, Hand
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
    hand:Hand
    chips:int
    bet:int
    is_out:bool
    has_insurance:bool
    is_split:bool
    insurance:int
    psuedos:list[PseudoPlayer]

    def __init__(self, name:str, chips:int=0, strategy:Strategy=Simple()) -> None:
        self.name = name
        self.strategy = strategy
        self.hand = Hand()
        self.chips = chips
        self.bet = 0
        self.insurance = 0
        self.is_out = False
        self.psuedos = []
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
        print_hand_style = "red" if (self.is_bust() or (dealer_hand_value > self.hand_value() and dealer_hand_value < 22) or (dealer_hand_value == 21 and len(dealer.hand) == 2)) else "Cyan/bold"
        
        if not self.has_psuedos():
            esc.printf(
                (self.name, print_style, print_strike, "underline"), (post_str,print_style), 
                " ... ", (f"${self.bet}", print_style, "underline"),
                " -> ", # (f"{post_str + (' '*len(self.name))} ... ", print_style), 
                (f"{' | '.join(card_str_arr)}", print_hand_style)
            )
        else:
            esc.printf(
                (self.name, print_style, print_strike, "underline"), 
                (post_str,print_style)," ... ", (f"${self.bet}", print_style, "underline/dim"),
            )
            for pseudo in self.psuedos:
                pseudo.print(max_name_len=max_name_len, dealer=dealer)

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
            f"{self.name} (", [f"${self.chips}", "Green/underline"], 
            f") What is your bet? ", (f"defualt = ${min_bet}","dim")  
        )

        bet_amount = (
            esc.input("$", input="Green", end="")
        )

        if bet_amount == "":
            bet_amount = min_bet
        else:
            bet_amount = int(bet_amount)
        
        # bet_placed = self.place_bet(bet_amount=bet_amount, min_bet=min_bet)

        if bet_amount > self.chips or min_bet > bet_amount:
            esc.erase_prev(n=4)
            if min_bet > bet_amount == -1:
                esc.print(f"Bet amount (${bet_amount}) lower than Min Bet (${min_bet})", "red")
            elif bet_amount > self.chips == -2:
                esc.print(f"Insufficient Chips (${self.chips}) to cover bet (${bet_amount})","red")
            return self.input_bet(min_bet=min_bet)
        
        return bet_amount

    def get_init_round_inputs(self, min_bet:int=15) -> None:
        esc.printf(
            f"{self.name}, How many hands? ", ("default = 1", "dim")  
        )

        hand_amount = (
            esc.input("#", input="Green", end="")
        )

        if hand_amount == "":
            hand_amount = 1
        else:
            hand_amount = int(hand_amount)

        bet_amount = self.input_bet()

        if hand_amount > 1:
            for i in range(hand_amount):
                self.psuedos.append(
                    PseudoPlayer(name=f"{self.name}", parent=self, bet=bet_amount)
                )
        
        self.place_bet(bet_amount=bet_amount*hand_amount, min_bet=min_bet)

    def has_psuedos(self) -> bool:
        return len(self.psuedos) > 0

    def run_strategy(self, dealer:Dealer=None, players:list[Player]=[]):
        other_players = list(filter(lambda player: player != self, players))
        return self.strategy.run(player=self, players=other_players, dealer=dealer)

### Pseudo PLAYER ###
class PseudoPlayer(Player):
    def __init__(self, name:str, parent:Player, bet:int) -> None:
        super().__init__(name)
        self.bet = bet
        self.parent = parent
    
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
        print_hand_style = "red" if (self.is_bust() or (dealer_hand_value > self.hand_value() and dealer_hand_value < 22) or (dealer_hand_value == 21 and len(dealer.hand) == 2)) else "Cyan/bold"
        
        esc.printf(
            (f"{post_str + (' '*len(self.name))} ... ${self.bet}", print_style, print_strike), 
            " -> ", (f"{' | '.join(card_str_arr)}", print_hand_style, print_strike)
        )

    def place_bet(self, bet_amount: int, min_bet: int = 15) -> int:
        if self.chips < bet_amount:
            return -2
        
        if min_bet > bet_amount:
            return -1
        
        self.bet += bet_amount
        self.chips -= bet_amount

        return self.bet

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
            (f" ... {' | '.join(card_str_arr)}", "red/strikethrough" if self.is_bust() else "Cyan/bold")
        )

    def showing(self) -> int:
        if len(self.hand) > 0:
            return self.hand[0].value
        return 0