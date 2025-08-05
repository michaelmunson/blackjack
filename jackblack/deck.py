from __future__ import annotations
import random
from typing import NamedTuple


class Card:
    SYM_MAP = {
        "hearts" : "❤️",
        "spades" : "♠︎",
        "diamonds" : "♦️",
        "clubs" : "♣︎"
    }

    def __init__(self, rank:str, suit:str="spades") -> None:
        if not Card.is_rank(rank):
            raise TypeError(f"'{rank}' not a valid card rank.")
        if not Card.is_suit(suit):
            raise TypeError(f"'{suit}' not a valid card suit.")

        self.rank = str.upper(rank[0]) + str.lower(rank[1:])
        self.suit = self.SYM_MAP[suit.lower()] if suit.lower() in self.SYM_MAP else suit
        if rank.isdigit():
            self.value = int(rank)
        elif rank == "Ace":
            self.value = 11
        else:
            self.value = 10
    
    def to_str(self) -> str:
        return f"{self.rank} {self.suit}"

    @staticmethod
    def is_card(card) -> bool:
        return isinstance(card,Card)

    @staticmethod
    def is_rank(rank:str) -> bool:
        return rank in ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']

    @staticmethod
    def is_suit(suit:str) -> bool:
        return str.lower(suit) in ['hearts','diamonds','clubs','spades', '❤️', '♦️', '♣︎', '♠︎'] 

class Hand(list[Card]):
    bet:int
    
    def __init__(self, *cards:Card|str, bet:int=0):
        self.bet = bet
        for card in cards:
            self.add(card)

    def add(self,card:Card|str) -> None:
        if Card.is_card(card):
            return self.append(card)
        elif isinstance(card,str):
            card = Card(card)
            return self.append(card)
        
    def value(self) -> int:
        value = 0
        for card in self:
            value += card.value

        if value > 21:
            i = 0
            while i < len(self) and value > 21:
                card = self[i]
                if card.rank == "Ace":
                    value -= 10
                i += 1

        return value
    
    def is_bust(self) -> int:
        return self.value() > 21
    
    def is_blackjack(self) -> int:
        return len(self) == 2 and self.value() == 21

    def lowest_value(self) -> int:
        value = 0
        for card in self:
            if card.rank == "Ace":
                value += 1
            else:
                value += card.value
        return value

    def to_str() -> str:
        return " | ".join(list(map(lambda card: card.to_str())))

    def len(self) -> int:
        return len(self)
    
    def split(self) -> tuple[Hand,Hand]:
        return (
            Hand(self[0]),
            Hand(self[1])
        )

class Deck(list):
    def __init__(self, num_decks:int=1, shuffle:bool=False):
        self.num_decks = num_decks
        self.is_shuffle = shuffle
        self.reset()
    # shuffle deck
    def shuffle(self):
        random.shuffle(self)
    # deal card
    def deal(self):
        if len(self) == 0:
            return None
        return self.pop()
    # reset deck
    def reset(self):
        self.clear()
        for i in range(self.num_decks):
            self += [Card(rank, suit)
                    for rank in ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
                    for suit in ['❤️', '♦️', '♣︎', '♠︎']]
                    # for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']]
        if self.shuffle:
            self.shuffle()
            self.shuffle()

    def card_str_list(self):
        return list(map(lambda card: card.to_str(), self))
    
    def peek(self,num_cards:int):
        return list(map(lambda card: card.to_str(), self[-num_cards:]))
    