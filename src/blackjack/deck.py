import random

class Card:
    SYM_MAP = {
        "hearts" : "❤️",
        "spades" : "♠︎",
        "diamonds" : "♦️",
        "clubs" : "♣︎"
    }

    def __init__(self, rank:str, suit:str) -> None:
        self.rank = rank
        self.suit = self.SYM_MAP[suit.lower()] if suit.lower() in self.SYM_MAP else suit
        if rank.isdigit():
            self.value = int(rank)
        elif rank == "Ace":
            self.value = 11
        else:
            self.value = 10
    
    def to_str(self):
        return f"{self.rank} {self.suit}"
    
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

    def card_str_list(self):
        return list(map(lambda card: card.to_str(), self))
    
    def peek(self,num_cards:int):
        return list(map(lambda card: card.to_str(), self[-num_cards:]))