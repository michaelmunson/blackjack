#!/usr/bin/env python3
"""
Command-line interface for the BlackJack simulator.
"""

import argparse
import sys
from .game import Simulation, Game
from .player import Player, Simple, Simple17

def main():
    parser = argparse.ArgumentParser(
        description="BlackJack Simulator - Run simulations with different strategies"
    )
    parser.add_argument(
        "--players", 
        nargs="+", 
        default=["Player1", "Player2"],
        help="Player names (default: Player1 Player2)"
    )
    parser.add_argument(
        "--chips", 
        type=int, 
        default=1000,
        help="Starting chips per player (default: 1000)"
    )
    parser.add_argument(
        "--rounds", 
        type=int, 
        default=1000,
        help="Number of rounds to simulate (default: 1000)"
    )
    parser.add_argument(
        "--min-bet", 
        type=int, 
        default=15,
        help="Minimum bet (default: 15)"
    )
    parser.add_argument(
        "--strategy", 
        choices=["simple", "simple17"], 
        default="simple",
        help="Strategy to use (default: simple)"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Show simulation progress"
    )
    parser.add_argument(
        "--interactive", 
        action="store_true",
        help="Play a single interactive game instead of running simulations"
    )

    args = parser.parse_args()

    # Create strategy
    strategy_map = {
        "simple": Simple(),
        "simple17": Simple17(),
    }
    strategy = strategy_map[args.strategy]

    # Create players
    players = [
        Player(name, chips=args.chips, strategy=strategy)
        for name in args.players
    ]

    if args.interactive:
        # Play interactive game
        game = Game(players=players, min_bet=args.min_bet)
        game.start()
    else:
        # Run simulation
        sim = Simulation(players=players, min_bet=args.min_bet)
        results = sim.run(n_times=args.rounds, print_sim=args.verbose)
        
        # Print results
        results.print()

if __name__ == "__main__":
    main() 