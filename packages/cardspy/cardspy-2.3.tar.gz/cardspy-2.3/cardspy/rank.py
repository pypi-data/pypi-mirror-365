"""
This module defines the Rank class and constants for all standard card ranks.
Each rank is represented as a dataclass with a unique bitmask, code, and name.

Examples:
    >>> from cardspy.rank import R2, RA, Rank
    >>> R2.code
    '2'
    >>> RA.name
    'Ace'
    >>> str(R2)
    '2'
"""
from dataclasses import dataclass


@dataclass
class Rank:
    """
    Represents the rank of a playing card (e.g., 2, 3, ..., Ace).

    Attributes:
        key (int): Unique bitmask for the rank (power of 2).
        code (str): Single-character code (e.g., 'A', 'K', '2').
        name (str): Full name of the rank (e.g., 'Ace').

    Example:
        >>> rank = Rank(0x1, '2', 'Two')
        >>> rank.code
        '2'
        >>> rank.name
        'Two'
        >>> str(rank)
        '2'
    """
    key: int
    code: str
    name: str

    def __str__(self) -> str:
        return self.code

    def __repr__(self) -> str:
        return self.code


R2 = Rank(0x1, "2", "Two")
R3 = Rank(0x2, "3", "Three")
R4 = Rank(0x4, "4", "Four")
R5 = Rank(0x8, "5", "Five")
R6 = Rank(0x10, "6", "Six")
R7 = Rank(0x20, "7", "Seven")
R8 = Rank(0x40, "8", "Eight")
R9 = Rank(0x80, "9", "Nine")
RT = Rank(0x100, "T", "Ten")
RJ = Rank(0x200, "J", "Jack")
RQ = Rank(0x400, "Q", "Queen")
RK = Rank(0x800, "K", "King")
RA = Rank(0x1000, "A", "Ace")

NUM_RANKS = 13

RANK_CODES = [
    "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"
]
