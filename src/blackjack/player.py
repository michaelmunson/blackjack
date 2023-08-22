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
    pseudos:list[PseudoPlayer]

    def __init__(self, name:str, chips:int=0, strategy:Strategy=Simple()) -> None:
        self.name = name
        self.strategy = strategy
        self.hand = Hand()
        self.chips = chips
        self.bet = 0
        self.insurance = 0
        self.is_out = False
        self.pseudos = []
        self.has_insurance = False
        self.is_pseudo = False
    
    def hit(self, card:Card) -> bool:
        self.hand.add(card)
        return self.is_bust()
    
    def is_bust(self) -> bool:
        return self.hand.is_bust()

    def is_blackjack(self) -> bool:
        return self.hand.is_blackjack()
    
    def can_split(self) -> bool:
        return self.hand.len() == 2 and self.hand[0].rank == self.hand[1].rank

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
        print_red = "red" if (self.is_bust() or (dealer_hand_value > self.hand_value() and dealer_hand_value < 22) or (dealer_hand_value == 21 and len(dealer.hand) == 2)) else ""
        
        if not self.has_pseudos():
            esc.printf(
                (self.name, print_style, print_strike, "underline"), (post_str,print_style), 
                (" ... ",print_red), (f"${self.bet}", print_style, "underline"),
                (" -> ",print_red), # (f"{post_str + (' '*len(self.name))} ... ", print_style), 
                (f"{' | '.join(card_str_arr)}", print_hand_style, print_strike)
            )
        else:
            esc.printf(
                (self.name, print_style, print_strike, "underline"), 
                (post_str,print_style)," ... ", (f"${self.bet}", print_style, "underline/dim"),
            )
            for pseudo in self.pseudos:
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
                self.pseudos.append(
                    PseudoPlayer(name=f"{self.name}", parent=self, bet=bet_amount)
                )
        else:
            self.place_bet(bet_amount=bet_amount, min_bet=min_bet)

    def has_pseudos(self) -> bool:
        return len(self.pseudos) > 0

    def run_strategy(self, dealer:Dealer=None, players:list[Player]=[]):
        other_players = list(filter(lambda player: player != self, players))
        return self.strategy.run(player=self, players=other_players, dealer=dealer)

    def split_hand(self) -> None:
        # weed out bad calls
        if not self.can_split():
            return
        # rest
        (hand1,hand2) = self.hand.split()

        self.pseudos = [
            PseudoPlayer(self.name, parent=self, bet=self.bet, hand=hand1),
            PseudoPlayer(self.name, parent=self, bet=self.bet, hand=hand2)
        ]
        #
        self.bet *= 2

### Pseudo PLAYER ###
class PseudoPlayer(Player):
    def __init__(self, name:str, parent:Player, bet:int, hand:Hand=None) -> None: # hand = Hand() causes weird bug
        super().__init__(name)
        self.parent = parent
        self.hand = hand if hand != None else Hand() # again have to do cause weird bug
        self.is_pseudo = True
        self.place_bet(bet_amount=bet)
    
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
        print_red = "red" if (self.is_bust() or (dealer_hand_value > self.hand_value() and dealer_hand_value < 22) or (dealer_hand_value == 21 and len(dealer.hand) == 2)) else ""
        print_hand_style = "red" if (self.is_bust() or (dealer_hand_value > self.hand_value() and dealer_hand_value < 22) or (dealer_hand_value == 21 and len(dealer.hand) == 2)) else "Cyan/bold"
        
        esc.printf(
            (f"{post_str + (' '*len(self.name))} ... ${self.bet}", print_style, print_strike), 
            (" -> ",print_red), (f"{' | '.join(card_str_arr)}", print_hand_style, print_strike)
        )

    def place_bet(self, bet_amount: int, min_bet: int = 15) -> int:
        if self.parent.chips < bet_amount:
            return -2
        
        if min_bet > bet_amount:
            return -1
        
        self.bet += bet_amount
        self.parent.bet += bet_amount
        self.parent.chips -= bet_amount

        return self.bet

    def split_hand(self):
        # weed out bad calls
        if not self.can_split():
            return
        # rest
        (hand1,hand2) = self.hand.split()
        index = self.parent.pseudos.index(self)
        self.parent.pseudos.pop(index)
        self.parent.pseudos.insert(index, PseudoPlayer(self.name, parent=self.parent, bet=self.bet, hand=hand1))
        self.parent.pseudos.insert(index+1,  PseudoPlayer(self.name, parent=self.parent, bet=self.bet, hand=hand2))
        self.parent.bet += self.bet

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