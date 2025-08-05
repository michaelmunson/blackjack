"""
BlackJack Simulator

A Python library for playing and simulating Black Jack games with customizable strategies.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main classes for easy access
from .game import Game, Simulation
from .player import Player, Dealer, Strategy, Simple, Simple17
from .deck import Deck, Hand, Card

# Import constants
from .player import HIT, STAY, INSURANCE, DOUBLE_DOWN, SPLIT

__all__ = [
    # Game classes
    "Game",
    "Simulation",
    
    # Player classes
    "Player",
    "Dealer",
    "Strategy",
    "Simple",
    "Simple17",
    
    # Deck classes
    "Deck",
    "Hand", 
    "Card",
    
    # Constants
    "HIT",
    "STAY",
    "INSURANCE",
    "DOUBLE_DOWN",
    "SPLIT",
]
