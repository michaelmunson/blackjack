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
