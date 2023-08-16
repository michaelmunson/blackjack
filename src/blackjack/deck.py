import random

class Card:
    def __init__(self, rank:str, suit:str) -> None:
        self.rank = rank
        self.suit = suit
        if rank.isdigit():
            self.value = int(rank)
        elif rank == "Ace":
            self.value = 11
        else:
            self.value = 10
    
    def to_str(self):
        return f"{self.rank} of {self.suit}"

class Deck(list):
    def __init__(self, num_decks:int=1, shuffle:bool=False):
        self.num_decks = num_decks
        self.reset(shuffle=shuffle, num_decks=num_decks)
    # shuffle deck
    def shuffle(self):
        random.shuffle(self)
    # deal card
    def deal(self):
        if len(self) == 0:
            return None
        return self.pop()
    # reset deck
    def reset(self, shuffle:bool=False, num_decks:int=1):
        self.clear()
        for i in range(num_decks):
            self += [Card(rank, suit)
                    for rank in ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
                    for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']]
        if shuffle:
            self.shuffle()

    def card_str_list(self):
        return list(map(lambda card: card.to_str(), self))
    
    def peek(self,num_cards:int):
        return list(map(lambda card: card.to_str(), self[-num_cards:]))