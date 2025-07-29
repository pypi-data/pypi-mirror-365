"""
This module defines the Suit class and constants for all standard card suits.
Each suit is represented as a dataclass with a unique bitmask, code, name, and symbol.

Examples:
    >>> from cardspy.suit import CLUB, HEART, Suit
    >>> CLUB.code
    'C'
    >>> HEART.symbol
    '♥'
    >>> str(CLUB)
    '♣'
"""
from dataclasses import dataclass


@dataclass
class Suit:
    """
    Represents the suit of a playing card (Clubs, Diamonds, Hearts, Spades).

    Attributes:
        key (int): Unique bitmask for the suit (power of 2).
        code (str): Single-character code (e.g., 'C', 'D').
        name (str): Full name of the suit (e.g., 'Club').
        symbol (str): Unicode symbol for the suit (e.g., '♣').

    Example:
        >>> suit = Suit(0x1, 'C', 'Club', '♣')
        >>> suit.code
        'C'
        >>> suit.symbol
        '♣'
        >>> str(suit)
        '♣'
    """
    key: int
    code: str
    name: str
    symbol: str

    def __str__(self) -> str:
        return self.symbol

    def __repr__(self) -> str:
        return self.symbol


CLUB = Suit(0x1, "C", "Club", "♣")
DIAMOND = Suit(0x2, "D", "Diamond", "♦")
HEART = Suit(0x4, "H", "Heart", "♥")
SPADE = Suit(0x8, "S", "Spade", "♠")

SUIT_SYMBOLS = ["♠", "♥", "♦", "♣"]
