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
