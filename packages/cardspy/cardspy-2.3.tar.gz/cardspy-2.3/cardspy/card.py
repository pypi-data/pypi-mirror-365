"""Card"""
from typing import List
from functools import reduce
from dataclasses import dataclass
from .rank import (
    Rank,
    R2,
    R3,
    R4,
    R5,
    R6,
    R7,
    R8,
    R9,
    RT,
    RJ,
    RQ,
    RK,
    RA,
    RANK_CODES,
)
from .suit import Suit, CLUB, DIAMOND, HEART, SPADE, SUIT_SYMBOLS


@dataclass
class Card:
    """
    A playing card with rank and suit.

    Attributes:
        key (int): Unique bitmask identifier for the card (power of 2).
        rank (Rank): The rank of the card (e.g., Ace, King, 2, 3, etc.).
        suit (Suit): The suit of the card (Clubs, Diamonds, Hearts, Spades).
        code (str): Two-character code representing the card (e.g., 'AS' for Ace of Spades).
        name (str): Full name of the card (e.g., 'Ace of Spades').
        symbol (str): Unicode symbol representation of the card (e.g., 'A♠').

    Example:
        >>> card = Card(key=0x1, rank=R2, suit=CLUB, code='2C', name='Two of Clubs', symbol='2♣')
        >>> print(card)
        2♣
        >>> card.rank
        Rank.TWO
        >>> card.suit
        <Suit.CLUB: 1>
    """
    key: int
    rank: Rank
    suit: Suit
    code: str
    name: str
    symbol: str

    def __str__(self) -> str:
        return self.symbol

    def __repr__(self) -> str:
        return self.__str__()


C2C = Card(0x1, R2, CLUB, "2C", "Two of Clubs", "2♣")
C2D = Card(0x2, R2, DIAMOND, "2D", "Two of Diamonds", "2♦")
C2H = Card(0x4, R2, HEART, "2H", "Two of Hearts", "2♥")
C2S = Card(0x8, R2, SPADE, "2S", "Two of Spades", "2♠")

C3C = Card(0x10, R3, CLUB, "3C", "Three of Clubs", "3♣")
C3D = Card(0x20, R3, DIAMOND, "3D", "Three of Diamonds", "3♦")
C3H = Card(0x40, R3, HEART, "3H", "Three of Hearts", "3♥")
C3S = Card(0x80, R3, SPADE, "3S", "Three of Spades", "3♠")

C4C = Card(0x100, R4, CLUB, "4C", "Four of Clubs", "4♣")
C4D = Card(0x200, R4, DIAMOND, "4D", "Four of Diamonds", "4♦")
C4H = Card(0x400, R4, HEART, "4H", "Four of Hearts", "4♥")
C4S = Card(0x800, R4, SPADE, "4S", "Four of Spades", "4♠")

C5C = Card(0x1000, R5, CLUB, "5C", "Five of Clubs", "5♣")
C5D = Card(0x2000, R5, DIAMOND, "5D", "Five of Diamonds", "5♦")
C5H = Card(0x4000, R5, HEART, "5H", "Five of Hearts", "5♥")
C5S = Card(0x8000, R5, SPADE, "5S", "Five of Spades", "5♠")

C6C = Card(0x10000, R6, CLUB, "6C", "Six of Clubs", "6♣")
C6D = Card(0x20000, R6, DIAMOND, "6D", "Six of Diamonds", "6♦")
C6H = Card(0x40000, R6, HEART, "6H", "Six of Hearts", "6♥")
C6S = Card(0x80000, R6, SPADE, "6S", "Six of Spades", "6♠")

C7C = Card(0x100000, R7, CLUB, "7C", "Seven of Clubs", "7♣")
C7D = Card(0x200000, R7, DIAMOND, "7D", "Seven of Diamonds", "7♦")
C7H = Card(0x400000, R7, HEART, "7H", "Seven of Hearts", "7♥")
C7S = Card(0x800000, R7, SPADE, "7S", "Seven of Spades", "7♠")

C8C = Card(0x1000000, R8, CLUB, "8C", "Eight of Clubs", "8♣")
C8D = Card(0x2000000, R8, DIAMOND, "8D", "Eight of Diamonds", "8♦")
C8H = Card(0x4000000, R8, HEART, "8H", "Eight of Hearts", "8♥")
C8S = Card(0x8000000, R8, SPADE, "8S", "Eight of Spades", "8♠")

C9C = Card(0x10000000, R9, CLUB, "9C", "Nine of Clubs", "9♣")
C9D = Card(0x20000000, R9, DIAMOND, "9D", "Nine of Diamonds", "9♦")
C9H = Card(0x40000000, R9, HEART, "9H", "Nine of Hearts", "9♥")
C9S = Card(0x80000000, R9, SPADE, "9S", "Nine of Spades", "9♠")

CTC = Card(0x100000000, RT, CLUB, "TC", "Ten of Clubs", "10♣")
CTD = Card(0x200000000, RT, DIAMOND, "TD", "Ten of Diamonds", "10♦")
CTH = Card(0x400000000, RT, HEART, "TH", "Ten of Hearts", "10♥")
CTS = Card(0x800000000, RT, SPADE, "TS", "Ten of Spades", "10♠")

CJC = Card(0x1000000000, RJ, CLUB, "JC", "Jack of Clubs", "J♣")
CJD = Card(0x2000000000, RJ, DIAMOND, "JD", "Jack of Diamonds", "J♦")
CJH = Card(0x4000000000, RJ, HEART, "JH", "Jack of Hearts", "J♥")
CJS = Card(0x8000000000, RJ, SPADE, "JS", "Jack of Spades", "J♠")

CQC = Card(0x10000000000, RQ, CLUB, "QC", "Queen of Clubs", "Q♣")
CQD = Card(0x20000000000, RQ, DIAMOND, "QD", "Queen of Diamonds", "Q♦")
CQH = Card(0x40000000000, RQ, HEART, "QH", "Queen of Hearts", "Q♥")
CQS = Card(0x80000000000, RQ, SPADE, "QS", "Queen of Spades", "Q♠")

CKC = Card(0x100000000000, RK, CLUB, "KC", "King of Clubs", "K♣")
CKD = Card(0x200000000000, RK, DIAMOND, "KD", "King of Diamonds", "K♦")
CKH = Card(0x400000000000, RK, HEART, "KH", "King of Hearts", "K♥")
CKS = Card(0x800000000000, RK, SPADE, "KS", "King of Spades", "K♠")

CAC = Card(0x1000000000000, RA, CLUB, "AC", "Ace of Clubs", "A♣")
CAD = Card(0x2000000000000, RA, DIAMOND, "AD", "Ace of Diamonds", "A♦")
CAH = Card(0x4000000000000, RA, HEART, "AH", "Ace of Hearts", "A♥")
CAS = Card(0x8000000000000, RA, SPADE, "AS", "Ace of Spades", "A♠")

ALL_CARDS = [
    C2C, C2D, C2H, C2S,
    C3C, C3D, C3H, C3S,
    C4C, C4D, C4H, C4S,
    C5C, C5D, C5H, C5S,
    C6C, C6D, C6H, C6S,
    C7C, C7D, C7H, C7S,
    C8C, C8D, C8H, C8S,
    C9C, C9D, C9H, C9S,
    CTC, CTD, CTH, CTS,
    CJC, CJD, CJH, CJS,
    CQC, CQD, CQH, CQS,
    CKC, CKD, CKH, CKS,
    CAC, CAD, CAH, CAS,
]


def sort_cards(cards: List[Card]) -> List[Card]:
    """
    Sort a list of cards by their rank in ascending order.

    Args:
        cards: List of Card objects to be sorted.

    Returns:
        List[Card]: A new list containing the sorted cards.

    Example:
        >>> hand = [C5H, C2S, CKC, C9D]
        >>> sorted_hand = sort_cards(hand)
        >>> [card.code for card in sorted_hand]
        ['2S', '5H', '9D', 'KC']
    """
    return sorted(cards, key=lambda card: card.rank.key)


def cards_mask(cards: List[Card]) -> int:
    """
    Generate a bitmask representing a collection of cards.

    Each card's key is a unique power of 2. This function combines multiple
    card keys using bitwise OR to create a single integer mask.

    Args:
        cards: List of Card objects to combine into a bitmask.

    Returns:
        int: A bitmask where each bit represents the presence of a specific card.

    Example:
        >>> hand = [C2C, C3D, C4H, C5S]
        >>> bin(cards_mask(hand))  # 0b1 | 0b10 | 0x100 | 0x1000 = 0x1111
        '0b1000100010001'
    """
    return reduce(lambda mask, card: mask | card.key, cards, 0)


def rank_mask_from_cards(cards: int) -> int:
    """
    Create a rank mask from a card bitmask.

    This function takes a bitmask of cards and returns a new bitmask
    representing the ranks present in those cards (ignoring suits).

    Args:
        cards: Bitmask representing a set of cards.

    Returns:
        int: Bitmask where each bit represents a rank present in the input.

    Example:
        >>> # Cards: 2♣ (0x1) and 2♦ (0x2) and 3♣ (0x10)
        >>> mask = 0x1 | 0x2 | 0x10
        >>> bin(rank_mask_from_cards(mask))  # 2 and 3 ranks are present
        '0b11'  # 0b01 | 0b10 = 0b11 (binary 3)
    """
    rmask = 0
    for card in ALL_CARDS:
        if cards & card.key != 0:
            rmask |= card.rank.key
    return rmask


def extract_cards(cards: int) -> List[Card]:
    """
    Convert a card bitmask back to a list of Card objects.

    Args:
        cards: Bitmask representing a set of cards.

    Returns:
        List[Card]: List of Card objects corresponding to the input bitmask.

    Example:
        >>> # Get mask for 2♣ (0x1) and 3♦ (0x20)
        >>> mask = 0x1 | 0x20
        >>> cards = extract_cards(mask)
        >>> [card.code for card in cards]
        ['2C', '3D']
    """
    return [
        card for card in ALL_CARDS if cards & card.key != 0
    ]


def extract_cards_key(card_keys: int) -> List[int]:
    """
    Extract individual card keys from a combined card bitmask.

    Args:
        card_keys: Combined bitmask of multiple cards.

    Returns:
        List[int]: List of individual card keys (each a power of 2).

    Example:
        >>> # Combined mask for 2♣ (0x1) and 3♦ (0x20)
        >>> keys = extract_cards_key(0x1 | 0x20)
        >>> [hex(key) for key in keys]
        ['0x1', '0x20']
    """
    return [card.key for card in ALL_CARDS if card_keys & card.key != 0]


def get_card(card_code: str) -> Card:
    """
    Get a card by its code.

    Args:
        card_code: Two-character code representing the card (e.g., 'AS' for Ace of Spades).

    Returns:
        Card: The card object corresponding to the input code.

    Raises:
        ValueError: If the input code does not correspond to a valid card.
    """
    if len(card_code) != 2:
        raise ValueError("Invalid card code: must be two characters")
    rank_code = card_code[0]
    suit_symbol = card_code[1]
    if rank_code not in RANK_CODES:
        raise ValueError(f"Invalid rank code: {rank_code}")
    if suit_symbol not in SUIT_SYMBOLS:
        raise ValueError(f"Invalid suit symbol: {suit_symbol}")
    for card in ALL_CARDS:
        if card.rank.code == rank_code and card.suit.symbol == suit_symbol:
            return card
    raise ValueError(f"Invalid card code: {card_code}")


def get_card_key_from_code(card_code: str) -> int:
    """
    Get the key of a card from its code.

    Args:
        card_code: Two-character code representing the card (e.g., 'AS' for Ace of Spades).

    Returns:
        int: The key of the card corresponding to the input code.

    Raises:
        ValueError: If the input code does not correspond to a valid card.
    """
    return get_card(card_code).key


def get_cards(card_codes: List[str]) -> List[Card]:
    """
    Get a list of cards by their codes.

    Args:
        card_codes: List of two-character codes representing cards (e.g., ['AS', '2C']).

    Returns:
        List[Card]: List of Card objects corresponding to the input codes.

    Raises:
        ValueError: If any input code does not correspond to a valid card.
    """
    return [get_card(card_code) for card_code in card_codes]


def get_card_keys_from_codes(card_codes: List[str]) -> int:
    """
    Get a list of card keys from their codes.

    Args:
        card_codes: List of two-character codes representing cards (e.g., ['AS', '2C']).

    Returns:
        int: Bitmask of card keys corresponding to the input codes.

    Raises:
        ValueError: If any input code does not correspond to a valid card.
    """
    return cards_mask(get_cards(card_codes))
