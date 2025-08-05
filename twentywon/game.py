from __future__ import annotations
from .deck import Deck, Hand, Card
from .player import Player, Dealer, Simple, PlayerResults, PlayerSimulationResults
from escprint import esc
from collections import namedtuple
from time import sleep, time
from typing import NamedTuple

### GAME ###
class Game:
    players: list[Player]
    dealer: Dealer
    deck: Deck
    min_bet:int
    log: Log
    out_players: list[Player]

    def __init__(self, players:list[Player], deck:Deck=Deck(shuffle=True, num_decks=8), min_bet:int=15, hit_on_soft_17:bool=False) -> None:
        self.players = players
        self.out_players = []
        self.dealer = Dealer()
        self.deck = deck
        self.min_bet = min_bet
        self.hit_on_soft_17 = hit_on_soft_17
        self.log = Log()

    def hit_player(self,player:Player) -> bool:
        # if out of cards
        if (len(self.deck) == 0):
            self.deck.reset()
        card = self.deck.deal()
        return player.hit(card)

    def add_player(self,player:Player) -> None:
        self.players.append(player)

    def start(self) -> GameResults:
        self._reset()
        # init screen
        esc.enable_alt_buffer(); esc.cursor_to_top()
        try:
            self._check_player_chips()
            #
            if len(self.players) < 1:
                self._print_exit()
                return
            # start bet round
            self._start_bet_round()
            # start initial hit round
            self._start_init_hit_round()
            # start decision round
            self._start_player_decision_round()
            # start dealer hit round
            self._start_dealer_hit_round()
            # handle game end
            game_results = self._get_results()
            # print results
            self._print_game_state(dealer=self.dealer,game_results=game_results, )
            # play again?
            if self._is_play_again():
                self._restart_game()

        # end round, disable screen
        finally:
            esc.disable_alt_buffer()
            self._print_exit()
        
        return game_results

    def _check_player_chips(self):
        for player in self.players:
            if player.chips < self.min_bet:
                self.out_players.append(player)
        
        for player in self.out_players:
            if player in self.players:      
                self.players.remove(player)
                
    def _start_bet_round(self) -> None:
        for player in self.players:
            player.get_init_round_inputs(min_bet=self.min_bet)
            esc.erase_screen(); esc.cursor_to_top()
    
    def _start_init_hit_round(self) -> None:
        for _ in range(2):
            for player in self.players:
                if player.has_pseudos():
                    for pseudo in player.pseudos:
                        # pseudo.hit(Card("9"))
                        self.hit_player(player=pseudo)
                else:
                    # player.hit(Card("9"))
                    self.hit_player(player=player)

            self.hit_player(player=self.dealer)
            # self.dealer.hit(Card("9"))

    def _start_player_decision_round(self) -> None:
        self._print_game_state()
        self.log.add(f"starting")
        i = 0
        while i < len(self.players):
            self.log.add(f"i = {i}")
            player = self.players[i]
            i += 1
        # for player in self.players:
            if player.has_pseudos():
                j = 0
                while j < len(player.pseudos) :
                    self.log.add(f"j = {j}")
                    pseudo = player.pseudos[j]
                    j+=1
                    self._print_game_state()
                    if pseudo.has_blackjack():
                        self._handle_player_blackjack(player=pseudo)
                        continue
                    decision = self._get_player_decision(player=pseudo)
                    if decision in ["spl","split", "i","insurance", "hit","h"]:
                        j -= 1
                    self._handle_player_decision(player=pseudo, decision=decision)
                    if pseudo.is_bust():
                        j += 1
                    self._print_game_state()
            else:
                self._print_game_state(current_player=player)
                if player.has_blackjack():
                    self._handle_player_blackjack(player=player)
                    self._print_game_state()
                    continue
                decision = self._get_player_decision(player=player)
                self.log.add(decision)
                if decision in ["spl","split", "i","insurance", "hit","h"]:
                    i -= 1
                self._handle_player_decision(player=player, decision=decision)
                if player.is_bust():
                    i += 1
            self._print_game_state()
            
    def _handle_player_blackjack(self, player:Player) -> None:
        if player.has_blackjack():
            self.log.add(f"{player.name} has Black Jack!", "Green/italic/bold")
            if self.dealer.showing_ace():
                player_choice = esc.input(f"Insurance? [y/N]\n> ", input="Magenta",end="")
                if str.lower(player_choice) == "y":
                    player.place_insurance_bet()
            player.is_stayed = True

    def _get_player_decision(self, player:Player) -> str:
        keyclr = "Magenta"
        valid_inps = ["","Stay","s", "Hit", "h"]
        
        if player.hand.len() <= 2:
            if (player.is_pseudo and player.parent.chips > player.bet) or player.chips > player.bet:
                valid_inps += ["Double Down", "dd"]
            if player.can_split():
                valid_inps += ["Split", "spl"]

        if self.dealer.hand[0].rank == "Ace":
            if not player.has_insurance():
                valid_inps += ["Insurance","i"]
        
        esc.printf((player.name,"Cyan/underline/bold")," -> ", (" | ".join(list(map(lambda card: card.to_str(), player.hand))), "Cyan/bold"), end="")
        for i in range(1,len(valid_inps),2):
            post_str = ", " if i+2 != len(valid_inps) else ""
            print(f"{valid_inps[i]} (", end=""); esc.print(valid_inps[i+1], keyclr, end=""); print(")"+post_str, end="")

        print() 
        player_inp = esc.input("> ", input=keyclr, end="")

        if str.lower(player_inp) not in list(map(lambda s:str.lower(s), valid_inps)):
            esc.erase_prev(3)
            esc.print(f'"{player_inp}" not a valid input', "red")
            return self._get_player_decision(player=player)

        return player_inp
    
    def _handle_player_decision(self, player:Player, decision:str) -> None:
        decision = str.lower(decision)
        # STAY
        if decision in ["s","stay", ""]:
            self.log.add(f"{player.name} has Stayed", "Blue/italic")
            player.is_stayed = True
        # DOUBLE DOWN
        elif decision in ["dd", "double down"]:
            self._handle_player_double_down(player=player)
        # SPLIT
        elif decision in ["spl","split"]:
            player.split_hand()
        # HIT
        elif decision in ["hit","h"]:
            self.hit_player(player=player)
        # INSURANCE
        elif decision in ["i", "insurance"]:
            # esc.print(f"{player.name} chose Insurance... insurance bet set @ {round(player.bet/2)}", "Green")
            player.place_insurance_bet()

    def _handle_player_double_down(self, player:Player) -> None:
        self.log.add(f"{player.name} has doubled down", "Blue/italic")
        player.place_bet(bet_amount=player.bet)
        self.hit_player(player=player)
        player.is_stayed = True
        if player.is_bust():
            self.log.add(f"{player.name} has busted", "red/italic")

    def _start_dealer_hit_round(self) -> None:
        if self.hit_on_soft_17:
            while self.dealer.lowest_hand_value() < 17:
                self.hit_player(player=self.dealer)
        else:
            while self.dealer.hand_value() < 17:
                self.hit_player(player=self.dealer)
    
    def _get_results(self) -> GameResults:
        game_results = GameResults()
        for player in self.players:
            p_res_dict = {
                "player":player,
                "hands" : 0,
                "won" : 0,
                "busted" : 0,
                "pushed" : 0,
                "net" : 0
            }
            # multiple / split hands
            if player.has_pseudos():
                for pseudo in player.pseudos:
                    p_res_dict["hands"] += 1
                    if pseudo.has_insurance():
                        if self.dealer.has_blackjack():
                            player.chips += (2*pseudo.insurance)
                            p_res_dict["net"] += (pseudo.insurance)
                        else:
                            p_res_dict["net"] -= pseudo.insurance

                    if pseudo.is_bust():
                        p_res_dict["busted"] += 1
                        p_res_dict["net"] -= pseudo.bet

                    
                    elif self.dealer.is_bust():
                        p_res_dict["won"] += 1
                        player.chips += (pseudo.bet * 2)
                        p_res_dict["net"] += pseudo.bet
                    
                    elif self.dealer.has_blackjack():
                        if pseudo.has_blackjack():
                            p_res_dict["pushed"] += 1
                        else:
                            p_res_dict["net"] -= pseudo.bet

                    elif pseudo.has_blackjack():
                        p_res_dict["won"] += 1
                        player.chips += (pseudo.bet * 1.5)
                        p_res_dict["net"] += (pseudo.bet * .5)
                    
                    elif pseudo.hand_value() == self.dealer.hand_value():
                        p_res_dict["pushed"] += 1
                        player.chips += pseudo.bet
                    
                    elif pseudo.hand_value() > self.dealer.hand_value():
                        p_res_dict["won"] += 1
                        player.chips += (pseudo.bet * 2)
                        p_res_dict["net"] += (pseudo.bet)
                    
                    elif player.hand_value() < self.dealer.hand_value():
                        p_res_dict["net"] -= pseudo.bet
            # 1 hand
            else:
                p_res_dict["hands"] = 1

                if player.has_insurance():
                    if self.dealer.has_blackjack():
                        player.chips += (2*player.insurance)
                        p_res_dict["net"] += (player.insurance)
                    else:
                        p_res_dict["net"] -= player.insurance

                if player.is_bust():
                    p_res_dict["busted"] += 1
                    p_res_dict["net"] -= player.bet

                elif self.dealer.is_bust():
                    p_res_dict["won"] += 1
                    player.chips += (player.bet * 2)
                    p_res_dict["net"] += player.bet
                
                elif self.dealer.has_blackjack():
                    if player.has_blackjack():
                        p_res_dict["pushed"] += 1
                    else:
                        p_res_dict["net"] -= player.bet

                elif player.has_blackjack():
                    p_res_dict["won"] += 1
                    player.chips += (player.bet * 1.5)
                    p_res_dict["net"] += (player.bet * .5)
                                
                elif player.hand_value() == self.dealer.hand_value():
                    p_res_dict["pushed"] += 1
                    player.chips += player.bet
                
                elif player.hand_value() > self.dealer.hand_value():
                    p_res_dict["won"] += 1
                    player.chips += (player.bet * 2)
                    p_res_dict["net"] += (player.bet)
                
                elif player.hand_value() < self.dealer.hand_value():
                    p_res_dict["net"] -= player.bet

            p_results = PlayerResults(**p_res_dict)
            player.results.append(p_results)
            game_results.add(p_results)
        return game_results

    def _is_play_again(self) -> bool:
        return str.lower(input("Play again? (Y/n) \n> ")) != "n"
    
    def _reset(self) -> None:
        [player.reset() for player in self.players]
        self.dealer.reset()

    def _restart_game(self) -> GameResults:
        esc.erase_screen()
        self._reset()
        return self.start()

    def _get_player_max_name_len(self) -> int:
        max_len = len(self.dealer.name)
        for player in self.players:
            if player.has_pseudos():
                for pseudo in player.pseudos:
                    if len(pseudo.name) > max_len:
                        max_len = len(pseudo.name)
            else: 
                if len(player.name) > max_len:
                    max_len = len(player.name)
        return max_len

    def _print_game_state(self, current_player:Player=None, reset:bool=True, dealer:Dealer=None, game_results:GameResults=None) -> None:
        hide_dealer = (dealer == None)
        if reset:
            esc.erase_screen()
            esc.cursor_to_top()
        mxnmlen = self._get_player_max_name_len()
        # if current_player:
        #     esc.set("dim")
        self.dealer.print(max_name_len=mxnmlen, hidden=hide_dealer)
        print()
        for player in self.players:
            # if current_player and player != current_player:
            #     esc.set("dim")
            player.print(max_name_len=mxnmlen, dealer=dealer)
            print()
        if game_results:
            game_results.print()
        # self.log.print()
        print()

    def _print_exit(self) -> None:
        for player in self.players:
            esc.printf(
                (player.name,"Magenta"), " ended with ",(f"${player.chips}","Magenta"),
            )
        for player in self.out_players:
            esc.printf(
                (player.name,"Magenta"), " ended with ",(f"${player.chips}","Magenta"),
            )
        print()

    def _is_all_players_bust(self) -> bool:
        for player in self.players:
            if not player.is_bust():
                return False
        return True

    @staticmethod
    def create(players:list[str|tuple]) -> Game:
        players = [
            Player(name=player[0],strategy=player[1] if len(player) > 1 else Simple()) if isinstance(player,tuple) else Player(name=player)
            for player in players
        ]
        return Game(players=players)

### SIMULATION
class Simulation(Game):
    def __init__(self, players: list[Player], deck:Deck = Deck(shuffle=True, num_decks=8), min_bet:int = 15, hit_on_soft_17:bool=False) -> None:
        super().__init__(players, deck, min_bet, hit_on_soft_17)
    
    def run(self, n_times:int=1, print_sim:bool=False, wait:float=.01) -> SimulationResults:
        start_time = time()

        if print_sim:
            esc.enable_alt_buffer(); 
            esc.cursor_to_top()

        for i in range(n_times):    
            if len(self.players) < 1:
                break
            self._start(print_sim=print_sim)
            if print_sim:
                sleep(wait)
                esc.erase_screen()
                esc.cursor_to_top()

        time_elapsed = time() - start_time

        if print_sim:
            esc.disable_alt_buffer()
        
        results = SimulationResults(players=self.players+self.out_players, n_times=n_times, time_elapsed=time_elapsed)
        
        return results

    def _start(self, print_sim:bool=False) -> GameResults:
        self._reset()
        #
        self._check_player_chips()
        # get hand & bet amount
        self._handle_init_round_inputs()
        # handle init hit rounds
        self._start_init_hit_round()
        # handle decision rounds
        self._handle_decision_round()
        # handle dealer hit round
        self._start_dealer_hit_round()
        # print game state
        if print_sim:
            self._print_game_state(dealer=self.dealer, reset=False)
        
        self._handle_post_game_strat()

        results = self._get_results()
        if print_sim:
            results.print()

        return results
    
    def _handle_init_round_inputs(self) -> None:
        for player in self.players:
            n_hands = player.strategy.__decide_hands__(player=player)
            p_bet = player.strategy.__decide_bet__(player=player, min_bet=self.min_bet)
            if p_bet < self.min_bet:
                p_bet = self.min_bet
            if n_hands > 1:
                player._handle_mult_hands(hand_amount=n_hands, bet_amount=p_bet)
            else:
                player.place_bet(p_bet, min_bet=self.min_bet)
    
    def _handle_decision_round(self) -> None:
        self.log.add(f"starting")
        i = 0
        while i < len(self.players):
            player = self.players[i]
            i += 1
        # for player in self.players:
            if player.has_pseudos():
                j = 0
                while j < len(player.pseudos) :
                    pseudo = player.pseudos[j]
                    j+=1
                    if pseudo.has_blackjack():
                        self._handle_player_blackjack(player=pseudo)
                        continue

                    decision = self._get_player_decision(player=pseudo)
                    if decision in ["spl","split", "i","insurance", "hit","h"]:
                        j -= 1
                    
                    self._handle_player_decision(player=pseudo, decision=decision)
                    if pseudo.is_bust():
                        j += 1
            else:
                if player.has_blackjack():
                    self._handle_player_blackjack(player=player)
                    continue
        
                decision = self._get_player_decision(player=player)
                if decision in ["spl","split", "i","insurance", "hit","h"]:
                    i -= 1
                self._handle_player_decision(player=player, decision=decision)
                if player.is_bust():
                    i += 1
     
    def _handle_player_blackjack(self, player:Player) -> None:
        if player.has_blackjack():
            if self.dealer.showing_ace():
                decision = self._get_player_decision(player=player, choices=["insurance","stay"])
                self._handle_player_decision(player=player, decision=decision)
            player.is_stayed = True

    def _get_player_decision(self, player: Player, choices:list[str]=None) -> str:
        if not choices:
            choices = self._get_valid_choices(player=player)
        players = list(filter(lambda p: p != player, self.players))
        decision = player.strategy.__decide__(player=player, choices=choices, dealer=self.dealer, players=players)
        return decision

    def _get_valid_choices(self, player:Player) -> list[str]:
        valid_inps = ["","stay","hit"]
        
        if player.hand.len() <= 2:
            if (player.is_pseudo and player.parent.chips > player.bet) or player.chips > player.bet:
                valid_inps.append("double down")
            if player.can_split():
                valid_inps.append("split")

        if self.dealer.hand[0].rank == "Ace":
            if not player.has_insurance():
                valid_inps.append("insurance")
        
        return valid_inps
        
    def _handle_post_game_strat(self) -> None:
        for player in self.players:
            players = list(filter(lambda p: p != player, self.players))
            player.strategy.__after__(player=player, players=players, dealer=self.dealer)
### GAME RESULTS
class GameResults(list[PlayerResults]):
    def __init__(self) -> None:
        super().__init__()
    def add(self, player_res:PlayerResults) -> None:
        return self.append(player_res)
    def print(self) -> None:
        for result in self:
            # print(result.net)
            net = (f"+(${result.net})","Green") if result.net >= 0 else (f"-(${abs(result.net)})","Red")
            _and = " with " if result.pushed > 0 else ""
            pushed = (f"{result.pushed}","Magenta") if result.pushed > 0 else ""
            plshands = " hands pushed." if result.pushed > 0 else ""
            esc.printf(
                (f"{result.player.name} ","Magenta"), net, ": ",(f"{result.won}","Magenta"), "/",(f"{result.hands}","Magenta"), " hands won", _and, pushed, plshands
            )

### SIMULATION RESULTS
class SimulationResults(dict[str,PlayerSimulationResults]):
    def __init__(self, players:list[Player], n_times:int, time_elapsed:float=0.0) -> None:
        self.players = players
        self.n_times = n_times
        self.update()

    def update(self):
        for player in self.players:
            self[player.name] = PlayerSimulationResults(
                player=player,
                rounds=self.n_times,
                hands=sum(res.hands for res in player.results),
                won=sum(res.won for res in player.results),
                pushed=sum(res.pushed for res in player.results),
                busted=sum(res.busted for res in player.results),
                net=(player.chips - player.init_chips),
                win_rate=(sum(res.won for res in player.results) / sum(res.hands for res in player.results))
            )
    
    def print(self):
        for name in self:
            res = self[name]
            rate_sty = "Red" if res.win_rate < .5 else "Green"
            net_sty = "Red" if res.net < 0 else "Green"
            esc.printf(
                (f"{name}", "Magenta"), " won ",(f"{round(res.win_rate * 100, 2)}%", rate_sty), " of the time with net chip earnings = ",(f"{res.net}",net_sty),
            )
            print()

### LOG
class Log(list[tuple[str,str]]):
    def __init__(self) -> None:
        pass

    def add(self, log_item:str, style:str=""):
        self.append((log_item, style))
        
    def delete(self, key:str):
        for i in range(len(self)):
            if self[i][0] == key:
                del self[i]
        
    def print(self):
        for item in self:
            esc.print('~ ' + item[0], item[1])
