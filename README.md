# jackblack

A comprehensive Python library for playing and simulating Black Jack games with customizable strategies. Perfect for learning the game, testing strategies, or running statistical analysis.

## Features

- 🎮 **Interactive Game Mode**: Play Black Jack with a beautiful terminal interface
- 📊 **Simulation Mode**: Run thousands of games to test strategies and analyze performance
- 🧠 **Customizable Strategies**: Implement your own betting and decision strategies
- 🃏 **Multiple Deck Support**: Configurable number of decks (1-8)
- 💰 **Betting System**: Support for insurance, double down, and split hands
- 📈 **Detailed Statistics**: Track wins, losses, win rates, and profit/loss
- 🎯 **Strategy Analysis**: Compare different strategies side-by-side

## Installation

### From PyPI (Coming Soon)
```bash
pip install jackblack
```

### From Source
```bash
git clone https://github.com/michaelmunson/blackjack.git
cd jackblack
pip install -e .
```

## Quick Start

### Command Line Interface

Run a quick simulation with default settings:
```bash
jackblack --rounds 1000 --strategy simple
```

Run an interactive game:
```bash
python -m jackblack.cli --interactive
```

### Python API

```python
from jackblack import Game, Player, Simple, Simulation

# Create players with strategies
player1 = Player("Alice", chips=1000, strategy=Simple())
player2 = Player("Bob", chips=1000, strategy=Simple())

# Play an interactive game
game = Game([player1, player2])
results = game.start()

# Run a simulation
sim = Simulation([player1, player2])
results = sim.run(n_times=1000)
results.print()
```

## Usage Examples

### Basic Game Setup

```python
from jackblack import Game, Player, Simple

# Create players
players = [
    Player("Player1", chips=1000, strategy=Simple()),
    Player("Player2", chips=1000, strategy=Simple())
]

# Create and start game
game = Game(players=players, min_bet=15)
results = game.start()
```

### Custom Strategy Implementation

```python
from jackblack import Strategy, Player, HIT, STAY

class MyStrategy(Strategy):
    def decide(self, player, choices, dealer=None, players=None):
        # Basic strategy: hit on 16 or less, stay on 17+
        if player.hand_value() <= 16:
            return HIT
        return STAY
    
    def decide_bet(self, player, min_bet=15):
        # Bet 5% of chips, minimum bet
        bet = max(min_bet, player.chips // 20)
        return min(bet, player.chips)

# Use custom strategy
player = Player("CustomPlayer", chips=1000, strategy=MyStrategy())
```

### Running Simulations

```python
from jackblack import Simulation, Player, Simple, Simple17

# Compare strategies
simple_players = [Player(f"Simple{i}", chips=1000, strategy=Simple()) for i in range(3)]
simple17_players = [Player(f"Simple17_{i}", chips=1000, strategy=Simple17()) for i in range(3)]

# Run simulations
sim1 = Simulation(simple_players)
sim2 = Simulation(simple17_players)

results1 = sim1.run(n_times=10000)
results2 = sim2.run(n_times=10000)

print("Simple Strategy Results:")
results1.print()
print("\nSimple17 Strategy Results:")
results2.print()
```

## API Reference

### Core Classes

#### `Game`
Main game controller for interactive play.

```python
Game(players, deck=None, min_bet=15, hit_on_soft_17=False)
```

**Parameters:**
- `players`: List of Player objects
- `deck`: Deck object (default: 8-deck shuffled)
- `min_bet`: Minimum bet amount (default: 15)
- `hit_on_soft_17`: Whether dealer hits on soft 17 (default: False)

**Methods:**
- `start()`: Start interactive game
- `add_player(player)`: Add player to game

#### `Simulation`
Game controller optimized for running multiple games quickly.

```python
Simulation(players, deck=None, min_bet=15, hit_on_soft_17=False)
```

**Methods:**
- `run(n_times=1, print_sim=False, wait=0.01)`: Run simulation
- `start()`: Run single game (non-interactive)

#### `Player`
Represents a player in the game.

```python
Player(name, chips=1000, strategy=Simple())
```

**Parameters:**
- `name`: Player name
- `chips`: Starting chip count
- `strategy`: Strategy object for decisions

**Properties:**
- `hand`: Current hand
- `chips`: Current chip count
- `bet`: Current bet amount
- `hand_value()`: Current hand value
- `is_bust()`: Check if busted
- `has_blackjack()`: Check for blackjack

#### `Dealer`
Specialized Player class for the dealer.

```python
Dealer(strategy=Simple17())
```

**Methods:**
- `showing()`: Value of visible card
- `showing_ace()`: Check if showing ace

### Strategy System

#### Base Strategy Class
```python
class Strategy:
    def decide(self, player, choices, dealer=None, players=None) -> str
    def decide_bet(self, player, min_bet=15) -> int
    def decide_hands(self, player) -> int
    def after(self, player, dealer=None, players=None) -> None
```

#### Built-in Strategies

- **`Simple`**: Basic hit/stand strategy
- **`Simple17`**: Dealer strategy (hit on soft 17)

### Deck and Cards

#### `Deck`
```python
Deck(shuffle=True, num_decks=8)
```

**Methods:**
- `deal()`: Deal one card
- `shuffle()`: Shuffle deck
- `reset()`: Reset and shuffle deck

#### `Card`
```python
Card(rank, suit="spades")
```

**Valid Ranks:** Ace, 2-10, Jack, Queen, King
**Valid Suits:** hearts, diamonds, clubs, spades

#### `Hand`
```python
Hand(*cards, bet=0)
```

**Methods:**
- `value()`: Calculate hand value
- `is_bust()`: Check if busted
- `is_blackjack()`: Check for blackjack
- `split()`: Split hand into two

## Game Rules

This implementation follows standard casino Black Jack rules:

- **Objective**: Beat the dealer by getting closer to 21 without going over
- **Card Values**: 
  - 2-10: Face value
  - Jack, Queen, King: 10
  - Ace: 1 or 11 (soft/hard)
- **Actions**:
  - **Hit**: Take another card
  - **Stay**: Keep current hand
  - **Double Down**: Double bet, take one card
  - **Split**: Split pair into two hands
  - **Insurance**: Bet against dealer blackjack
- **Dealer Rules**: Hit on 16 or less, stay on 17+ (configurable for soft 17)

## Command Line Options

```bash
jackblack [OPTIONS]

Options:
  --players TEXT...     Player names (default: Player1 Player2)
  --chips INTEGER       Starting chips per player (default: 1000)
  --rounds INTEGER      Number of rounds to simulate (default: 1000)
  --min-bet INTEGER     Minimum bet (default: 15)
  --strategy TEXT       Strategy to use: simple, simple17 (default: simple)
  --verbose             Show simulation progress
  --help                Show help message
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/michaelmunson/blackjack.git
cd jackblack
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
flake8 .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Python 3.8+
- Uses [escprint](https://pypi.org/project/escprint/) for terminal formatting
- Inspired by casino Black Jack games

