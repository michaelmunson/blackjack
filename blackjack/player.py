from __future__ import annotations
from .deck import Card, Hand
from escprint import esc
from typing import NamedTuple

HIT = "hit"
STAY = "stay"
INSURANCE = "insurance"
DOUBLE_DOWN = "double down"
SPLIT = "split"

### STRATEGY ###
class Strategy:
    log:list
    auto_log:bool
    state_log: list
    state: dict

    def __init__(self, auto_log:bool=True) -> None:
        self.auto_log = auto_log
        self.log = []
        self.state_log = []
        self.state = {}
        self.init_state()

    def init_state(self):
        self.state = {}

    def __decide_hands__(self, player:Player) -> int:
        n_hands = self.decide_hands(player=player)
        if not n_hands:
            n_hands = 1
        if self.auto_log:
            self.log.append(f"hands -> {n_hands}")
        if not isinstance(n_hands,int):
            raise TypeError("Strategy decision for number of hands must be integer.")
        if n_hands < 1:
            raise ValueError("Strategy decision for number of hands must exceed 0")
        
        return n_hands
        
    def __decide_bet__(self, player:Player, min_bet:int=15) -> int:
        bet = self.decide_bet(player=player, min_bet=min_bet)
        if bet == None:
            bet = min_bet
        if not isinstance(bet, int):
            raise TypeError(f"Strategy bet decision must be integer")
        if bet < min_bet:
            raise ValueError(f"Strategy bet decision must be integer greater than min_bet ({min_bet})")
        if self.auto_log:
            self.log.append(f"bet -> {bet}")
        return bet
        
    def __decide__(self, player:Player, choices:list[str], dealer:Dealer=None, players:list[Player]=[]) -> str:
        decision = self.decide(
            player=player,
            choices=choices,
            dealer=dealer,
            players=players
        )

        if not decision:
            decision = STAY

        decision = str.lower(decision)

        if not isinstance(decision, str):
            raise TypeError("Strategy decision must be of type str")
        if decision not in choices:
            raise ValueError(f"Straregy decision not in list of valid choices: {choices}")
        
        return decision
        
    def __after__(self, player:Player, dealer:Dealer=None, players:list[Player]=[]) -> None:
        return self.after(player=player, dealer=dealer, players=players)

    def _reset_log(self) -> None:
        self.log.clear()

    def decide_hands(self, player:Player) -> int:
        return 1
    
    def decide_bet(self, player:Player, min_bet:int=15) -> int:
        return min_bet

    def decide(self, player:Player, choices:list[str], dealer:Dealer=None, players:list[Player]=[]) -> str:
        # possible choices = ["insurance","split","hit","stay","double down"]
        return STAY

    def after(self, player:Player, dealer:Dealer=None, players:list[Player]=[]) -> None:
        pass

class Simple(Strategy):
    def init_state(self):
        self.state = {
            "Aces" : 0
        }

    def decide_hands(self, player: Player) -> int:
        return 1
    
    def decide_bet(self, player: Player, min_bet: int = 15) -> int:
        return min_bet

    def decide(self, player:Player, choices:list[str], dealer:Dealer=None, players:list[Player]=[]) -> str:
        return HIT if player.hand_value() < 16 else STAY

class Simple17(Strategy):
    def decide(self, player:Player, choices:list[str], dealer:Dealer=None, players:list[Player]=[]) -> str:
        return HIT if player.hand_value() < 17 else STAY

### PLAYER ###
class Player: 
    name:str
    strategy:Strategy
    hand:Hand
    init_chips:int
    chips:int
    bet:int
    is_split:bool
    insurance:int
    pseudos:list[PseudoPlayer]
    is_pseudo:bool
    is_stayed:bool
    results:list[PlayerResults]

    def __init__(self, name:str, chips:int=1000, strategy:Strategy=Simple()) -> None:
        self.name = name
        self.strategy = strategy
        self.hand = Hand()
        self.init_chips = chips
        self.chips = chips
        self.bet = 0
        self.insurance = 0
        self.pseudos = []
        self.is_pseudo = False
        self.is_stayed = False
        self.results = []
    
    def hit(self, card:Card) -> bool:
        self.hand.add(card)
        return self.is_bust()
    
    def is_bust(self) -> bool:
        return self.hand.is_bust()

    def has_blackjack(self) -> bool:
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
        
        bet_str = f"${self.bet}" if not self.has_insurance() else f"${self.bet} + (${self.insurance})"
        stayed_check = " ✔︎" if self.is_stayed else ""

        if not self.has_pseudos():
            esc.printf(
                (self.name, print_style, print_strike, "underline"), (post_str,print_style), 
                (" ... ",print_red), (bet_str, print_style, "underline"),
                (" -> ",print_red), # (f"{post_str + (' '*len(self.name))} ... ", print_style), 
                (f"{' | '.join(card_str_arr)}", print_hand_style, print_strike),
                stayed_check
            )
        else:
            print_style = "red" if (self.is_bust() or (dealer_hand_value == 21 and len(dealer.hand) == 2)) else "Green/bold"
            print_strike = "strike" if (self.is_bust() or (dealer_hand_value == 21 and len(dealer.hand) == 2)) else ""

            esc.printf(
                (self.name, print_style, print_strike, "underline"), 
                (post_str,print_style)," ... ", (bet_str, print_style, "underline/dim"),
            )
            for pseudo in self.pseudos:
                pseudo.print(max_name_len=max_name_len, dealer=dealer)

    def reset(self) -> None:
        self.hand.clear()
        self.bet = 0
        self.insurance = 0
        self.is_stayed = False
        self.pseudos = []

    def place_bet(self, bet_amount:int, min_bet:int=15) -> int:
        if self.chips < bet_amount:
            return -2
        
        if min_bet > bet_amount:
            return -1
        
        self.bet += bet_amount
        self.chips -= bet_amount

        return self.bet

    def place_insurance_bet(self) -> None:
        bet = (self.bet / 2)
        self.insurance = bet
        self.chips -= bet

    def get_init_round_inputs(self, min_bet:int=15) -> None:
        esc.printf(
            f"{self.name}, How many hands? ", ("default = 1", "dim")  
        )

        hand_amount = (
            esc.input("#", input="Green", end="")
        )
        
        if not hand_amount.isdigit() and hand_amount != "":
            esc.erase_screen(); esc.cursor_to_top()
            esc.print("Hand amount must be integer.","Red/italic")
            return self.get_init_round_inputs(min_bet=min_bet)

        if hand_amount == "":
            hand_amount = 1
        else:
            hand_amount = int(hand_amount)

        esc.printf(
            f"{self.name} (", [f"${self.chips}", "Green/underline"], 
            f") What is your bet? ", (f"defualt = ${min_bet}","dim")  
        )

        bet_amount = (
            esc.input("$", input="Green", end="")
        )
                
        if not bet_amount.isdigit() and bet_amount != "":
            esc.erase_screen(); esc.cursor_to_top()
            esc.print("Bet amount must be integer.","Red/italic")
            return self.get_init_round_inputs(min_bet=min_bet)

        if bet_amount == "":
            bet_amount = min_bet
        else:
            bet_amount = int(bet_amount)


        if (hand_amount * bet_amount > self.chips):
            esc.erase_screen(); esc.cursor_to_top()
            esc.print("Bet * Hand Amt. greater than chip count","Red/italic")
            return self.get_init_round_inputs(min_bet=min_bet)
        if (bet_amount < min_bet):
            esc.erase_screen(); esc.cursor_to_top()
            esc.print("Bet amount lower than Min Bet.","Red/italic")
            return self.get_init_round_inputs(min_bet=min_bet)

        if hand_amount > 1:
            for i in range(hand_amount):
                self.pseudos.append(
                    PseudoPlayer(name=f"{self.name}", parent=self, bet=bet_amount)
                )
        else:
            self.place_bet(bet_amount=bet_amount, min_bet=min_bet)

    def has_pseudos(self) -> bool:
        return len(self.pseudos) > 0

    def has_insurance(self) -> bool:
        return self.insurance > 0

    def split_hand(self) -> None:
        # weed out bad calls
        if not self.can_split():
            return
        # rest
        (hand1,hand2) = self.hand.split()

        bet = self.bet
        self.bet = 0

        self.pseudos = [
            PseudoPlayer(self.name, parent=self, bet=bet, hand=hand1),
            PseudoPlayer(self.name, parent=self, bet=bet, hand=hand2)
        ]
        #
        # self.bet *= 2

    def _handle_mult_hands(self, hand_amount:int, bet_amount:int) -> None:
        if hand_amount > 1:
            for i in range(hand_amount):
                self.pseudos.append(
                    PseudoPlayer(name=f"{self.name}", parent=self, bet=bet_amount)
                )

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
        stayed_check = " ✔︎" if self.is_stayed else ""

        esc.printf(
            (f"{post_str + (' '*len(self.name))} ... ${self.bet}", print_style, print_strike), 
            (" -> ",print_red), (f"{' | '.join(card_str_arr)}", print_hand_style, print_strike),
            stayed_check
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
        bet = self.bet
        self.bet = 0
        # weed out bad calls
        if not self.can_split():
            return
        # rest
        (hand1,hand2) = self.hand.split()
        index = self.parent.pseudos.index(self)
        self.parent.pseudos.pop(index)
        self.parent.pseudos.insert(index, PseudoPlayer(self.name, parent=self.parent, bet=bet, hand=hand1))
        self.parent.pseudos.insert(index+1,  PseudoPlayer(self.name, parent=self.parent, bet=bet, hand=hand2))
        # self.parent.bet += self.bet

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
    
    def showing_ace(self) -> bool:
        return self.hand[0].rank == "Ace"
    
### PLAYER RESULTS
class PlayerResults(NamedTuple):
    player:Player
    hands:int
    won:int
    pushed:int
    busted:int
    net:int

class PlayerSimulationResults(NamedTuple):
    player:Player
    rounds:int
    hands:int
    won:int
    pushed:int
    busted:int
    net:int
    win_rate:float
    