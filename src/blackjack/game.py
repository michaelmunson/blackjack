from __future__ import annotations
from src.blackjack.deck import Deck
from src.blackjack.player import Player, Dealer, Simple
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

    def __init__(self, players:list[Player], dealer:Dealer=Dealer(), deck:Deck=Deck(shuffle=True, num_decks=8), min_bet:int=15) -> None:
        self.players = players
        self.dealer = dealer
        self.deck = deck
        self.min_bet = min_bet
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
        self.reset()
        try: 
            esc.enable_alt_buffer()
            esc.cursor_to_top()
            # initial deal
            for _ in range(2):
                self.hit_player(self.dealer)
                for player in self.players:
                    self.hit_player(player)
            self._print_game_state()
            # hit rounds
            for player in self.players:
                player_choice = "y"
                while player_choice == "y" and not player.is_bust():
                    self._print_game_state(current_player=player, reset=True)
                    player_choice = str.lower(esc.input(f"{player.name}, hit? (y/N)\n> ", prompt="Magenta", input="Blue", end=""))
                    if player_choice == "y":
                        self.hit_player(player)
            
            # check if everyone busted
            everyone_busted = self._is_all_players_bust()
            
            if not everyone_busted:
                # dealer hit round
                while self.dealer.hand_value() < 17:
                    self.hit_player(self.dealer)

            self._print_game_state(dealer=self.dealer)

            results = self.get_results()

            # print results
            if len(results.won) > 0:
                esc.print("\nWinners", "Green/underline/bold")
                for player in results.won:
                    esc.print(player.name, "green/italic")
            if len(results.tied) > 0:
                esc.print("\nTied", "Yellow/underline/bold")
                for player in results.tied:
                    esc.print(player.name, "yellow/italic")
            if len(results.lost) > 0:
                esc.print("\nLosers", "red/underline/bold")
                for player in results.lost:
                    esc.print(player.name, "red/italic")
            print()

            # replay
            if str.lower(input("Play again? (Y/n)")) != "n":
                esc.erase_screen()
                return self.start()
            else:
                esc.disable_alt_buffer()
                return results
        
        except Exception as e:
            esc.disable_alt_buffer()

    def reset(self) -> None:
        [player.reset() for player in self.players]
        self.dealer.reset()

    def get_results(self) -> GameResults:
        winners : list[Player] = []
        tied : list[Player] = []
        losers : list[Player] = []
        if self.dealer.is_bust():
            for player in self.players:
                if not player.is_bust():
                    winners.append(player)
                else:
                    losers.append(player)
        else:
            dealer_hand_value = self.dealer.hand_value()
            for player in self.players:
                if not player.is_bust():
                    if player.hand_value() > dealer_hand_value:
                        winners.append(player)
                    elif player.hand_value() < dealer_hand_value:
                        losers.append(player)
                    elif player.hand_value() == dealer_hand_value:
                        tied.append(player)
                else:
                    losers.append(player)

        return GameResults(won=winners, tied=tied, lost=losers)

    def play(self) -> GameResults:
        # init screen
        esc.enable_alt_buffer(); esc.cursor_to_top()
        try:
            # start bet round
            self._start_bet_round()
            # start initial hit round
            self._start_init_hit_round()
            # start decision round
            self._start_player_decision_round()

            input()

        # end round, disable screen
        finally:
            esc.disable_alt_buffer()

    def _start_bet_round(self) -> None:
        for player in self.players:
            player.input_bet(min_bet=self.min_bet)
            esc.erase_screen(); esc.cursor_to_top()
    
    def _start_init_hit_round(self) -> None:
        for _ in range(2):
            for player in self.players:
                self.hit_player(player=player)
            self.hit_player(player=self.dealer)

    def _start_player_decision_round(self) -> None:
        for player in self.players:
            self._print_game_state(current_player=player)
            if player.is_blackjack():
                self._handle_player_blackjack(player=player)
                continue
            decision = self._get_player_decision(player=player)
            self._handle_player_decision(player=player, decision=decision)
        self._print_game_state()

    def _handle_player_blackjack(self, player:Player) -> None:
        if player.is_blackjack():
            # esc.print(f"{player.name} has Black Jack!", "Green/italic")
            self.log.add(f"{player.name} has Black Jack!", "Green/italic/bold")
            if self.dealer.hand[0] == "Ace":
                def get_choice():
                    player_choice = esc.input(f"Payout or Insurance? [P/i]\n> ", prompt="Green",input="Magenta")
                    if str.lower(player_choice) in ["p",""]:
                        self._payout_player(player=player, rate=1.5)
                    elif str.lower(player_choice) in ["i","insurance"]:
                        ins_bet = esc.input("Insurance Bet?\n$",end="")
                        while ins_bet < 0 and ins_bet >= round(player.bet/2):
                            esc.print(f"Insurance bet must be lower than half original bet (${player.bet/2})")
                            ins_bet = esc.input("Insurance Bet?\n$",end="")
                        player.has_insurance = True
                    else:
                        esc.print("Unrecognized input... Try again", "red")
                get_choice()
            else:
                self._payout_player(player=player, rate=1.5)

    def _get_player_decision(self, player:Player) -> str:
        keyclr = "Magenta"
        if len(player.hand) == 2:
            if self.dealer.hand[0] == "Ace":
                if player.can_split():
                    esc.printf((player.name,"Magenta"),f", What is your decision?\n","Stay (",("s",keyclr),"), ","Hit (",("h",keyclr),"), ","Double Down (",("dd",keyclr),"), ","Split (",("spl",keyclr),"), ","Insurance (",("i",keyclr),")")
            if player.can_split():
                esc.printf((player.name,"Magenta"),f", What is your decision?\n","Stay (",("s",keyclr),"), ","Hit (",("h",keyclr),"), ","Double Down (",("dd",keyclr),"), ","Split (",("spl",keyclr),")")
            else:
                esc.printf((player.name,"Magenta"),f", What is your decision?\n","Stay (",("s",keyclr),"), ","Hit (",("h",keyclr),"), ","Double Down (",("dd",keyclr),")")

        else:
            if self.dealer.hand[0] == "Ace":
                esc.printf((player.name,"Magenta"),f", What is your decision?\n","Stay (",("s",keyclr),"), ","Hit (",("h",keyclr),"), ","Insurance (",("i",keyclr),")")
            else:
                esc.printf((player.name,"Magenta"),f", What is your decision?\n","Stay (",("s",keyclr),"), ","Hit (",("h",keyclr),")")

        player_inp = esc.input("> ", input=keyclr, end="")
        return player_inp
    
    def _handle_player_decision(self, player:Player, decision:str):
        decision = str.lower(decision)
        # STAY
        if decision in ["s","stay", ""]:
            self.log.add(f"{player.name} has Stayed", "Blue/italic")
        # HIT
        elif decision in ["h","hit"]:
            self.hit_player(player=player)
            self._print_game_state(current_player=player)
            if player.hand_value() < 21:
                decision = self._get_player_decision(player=player)
                self._handle_player_decision(player=player, decision=decision)
            else:
                self.log.add(f"{player.name} has busted", "red/italic")
        # DOUBLE DOWN
        elif decision in ["dd", "double down"]:
            self._handle_player_double_down(player=player)
        # SPLIT
        elif decision in ["spl","split"]:
            esc.print(f"{player.name} has Split\n", "Green")
            pass
        # INSURANCE
        elif decision in ["i", "insurance"]:
            esc.print(f"{player.name} chose Insurance... insurance bet set @ {round(player.bet/2)}", "Green")
            player.has_insurance = True

    def _handle_player_double_down(self, player:Player) -> None:
        self.log.add(f"{player.name} has doubled down", "Blue/italic")
        player.place_bet(bet_amount=player.bet)
        self.hit_player(player=player)
        if player.is_bust():
            self.log.add(f"{player.name} has busted", "red/italic")
        
    def _handle_player_split(self, player:Player) -> None:
        self.log.add(f"{player.name} has split hand")
        player.hand = player.hand.split()
        

    def _check_and_handle_dealer_blackjack(self) -> None:
        if self.dealer.hand[0] == "Ace":
            if self.dealer.is_blackjack():
                for player in self.players:
                    if player.has_insurance:
                        player.chips += player.bet
                    else:
                        player.reset()
            else:
                for player in self.players:
                    pass
        # if self.dealer.hand[0] == "Ace":
        #     self._handle_insurance()
        
    # def _handle_insurance(self) -> None:
    #     if self.dealer.hand[0] != "Ace":
    #         return
    #     else:
    #         for player in self.players:
    #             if self.dealer.is_blackjack():


    def _payout_player(self,player:Player, rate:float=2) -> int:
        payout = round(player.bet * rate)
        player.is_out = True
        player.chips += payout
        player.bet = 0
        self.log.add(f"{player.name} paid out ${payout}", "Green/italic")
        return payout


    def _is_play_again(self) -> bool:
        return str.lower(input("Play again? (Y/n) \n> ")) != "n"
    
    def _restart_game(self) -> GameResults:
        esc.erase_screen()
        return self.start()

    def _get_player_max_name_len(self) -> int:
        max_len = len(self.dealer.name)
        for player in self.players:
            if len(player.name) > max_len:
                max_len = len(player.name)
        return max_len

    def _print_game_state(self, current_player:Player=None, reset:bool=True, dealer:Dealer=None) -> None:
        hide_dealer = (dealer == None)
        if reset:
            esc.erase_screen()
            esc.cursor_to_top()
        mxnmlen = self._get_player_max_name_len()
        if current_player:
            esc.set("dim")
        
        self.dealer.print(max_name_len=mxnmlen, hidden=hide_dealer)
        print()
        for player in self.players:
            if current_player and player != current_player:
                esc.set("dim")
            player.print(max_name_len=mxnmlen, dealer=dealer)
            print()

        self.log.print()
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

### AUTO GAME
class AutoGame(Game):
    def __init__(self, players: list[Player], dealer: Dealer = Dealer(), deck: Deck = Deck(shuffle=True, num_decks=8)) -> None:
        super().__init__(players, dealer, deck)

    def start(self, is_print:bool=False) -> tuple[list[Player], list[Player], list[Player]]:
        self.reset()
        # initial hit
        for _ in range(2):
            self.hit_player(self.dealer)
            for player in self.players:
                self.hit_player(player)
        # player hit
        for player in self.players:
            while player.run_strategy(dealer=self.dealer, players=self.players) and player.hand_value() < 22:
                self.hit_player(player=player)
        # check if everyone is busted
        everyone_busted = self._is_all_players_bust()
            
        if not everyone_busted:
            # dealer hit
            while self.dealer.run_strategy():
                self.hit_player(player=self.dealer)

        if is_print:
            self._print_game_state(dealer=self.dealer)

        return self.get_results()

    def simulate(self, n_times:int=1, print_sim:bool=False, wait:float|int=.01, print_results:bool=True) -> dict:
        start_time = time()
        # initialize player map
        player_res_map = {}
        for player in self.players:
            player_res_map[player.name] = {
                "won" : 0,
                "tied" : 0,
                "lost" : 0
            }
        # run game simulation
        for i in range(n_times):
            result = self.start(is_print=print_sim)
            for player in result.won:
                player_res_map[player.name]["won"] += 1
            for player in result.tied:
                player_res_map[player.name]["tied"] += 1
            for player in result.lost:
                player_res_map[player.name]["lost"] += 1
            if print_sim:
                # for name in player_res_map:
                #     win_rate = round((player_res_map[name]['won'] / (i+1)) * 100, 3) if player_res_map[name]['won'] > 0 else 0
                #     esc.printf(
                #         f"{name} win rate: ", (f"{win_rate}%\n", "red" if win_rate < 50 else "Green")
                #     ) 
                sleep(wait)


        if print_results:
            if print_sim:
                esc.erase_screen()
                esc.cursor_to_top()

            time_elapsed = time() - start_time

            esc.printf(f"\nSimulation ran ",
                (f"{n_times}", "Green/underline"), 
                " times in ", 
                (f"{round(time_elapsed, 3)}", "Green/underline"), 
                " seconds\n")

            for name in player_res_map:
                win_rate = round((player_res_map[name]['won'] / n_times) * 100, 3)
                esc.printf(
                    f"{name} win rate: ", (f"{win_rate}%\n", "red" if win_rate < 50 else "Green")
                ) 

        return player_res_map

    @staticmethod
    def create(players:list[str|tuple]) -> AutoGame:
        players = [
            Player(name=player[0],strategy=player[1] if len(player) > 1 else Simple()) if isinstance(player,tuple) else Player(name=player)
            for player in players
        ]
        return AutoGame(players=players)
    
### GAME RESULTS
class GameResults(NamedTuple):
    won:int
    tied:int
    lost:int

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