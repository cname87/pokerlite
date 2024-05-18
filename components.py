#!/usr/bin/env python

"""
This module contains game elements: Deck, Card.
Author: Seán Young
"""

from __future__ import annotations
import random
from typing import Sequence

class Card:

    def __init__(self, number: int) -> None:
        self.number = number

    @property
    def value(self) -> int:
        """The value of a card is its number"""
        return int(self.number)

    def __gt__(self, other: Card) -> bool:
        return self.number > other.number

    def __lt__(self, other: Card) -> bool:
        return self.number < other.number

    def __repr__(self) -> str:
        return f"{self.number}"

class Deck(Sequence[Card]):
# Deck is a subclass of List that will contain objects of type Card

    def __init__(self, cards: list[Card]) -> None:
        if not all(isinstance(card, Card) for card in cards): # type: ignore
            raise TypeError("The Deck object must consist of Card objects")
        self.cards = cards

    @classmethod
    def create(cls, count: int, shuffle: bool = False) -> Deck:
        """Create a new deck of cards"""
        if not count > 3:
            raise ValueError("The deck must have three cards minimum")
        cards = [Card(n) for n in list(range(1, count + 1))]
        if shuffle:
            random.shuffle(cards)
        return cls(cards)

    def deal(self, count: int = 2) -> list[Card]:
        """Deal a set of count random cards from the deck"""
        if not count < len(self):
            raise ValueError("The deal must be less than the deck size")
        deal = random.sample(self.cards, count)
        return deal

    def __len__(self) -> int:
        return len(self.cards)

    def __eq__(self, other: Deck) -> bool: # type: ignore
        return self.cards == other.cards
    
    # Define Deck[i] for use by the random function in the deal function
    def __getitem__(self, key: int) -> Card: # type: ignore
        if isinstance(key, int): # type: ignore
            return self.cards[key]
        else:
            raise TypeError("Indices must be an integer")

    def __repr__(self) -> str:
        return " ".join(repr(c) for c in self.cards)

