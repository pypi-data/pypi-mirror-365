# cardspy

A Python library for modeling and manipulating playing cards, decks, suits, and ranks. Provides utilities for games, simulations, and card-based logic.

## Features
- Full 52-card deck modeling with efficient bitmask operations
- Rich Card, Suit, and Rank objects with comprehensive properties
- Deck operations: shuffle, deal, add/remove cards, reset, clear
- Bitmask utilities for efficient card set operations
- Card code utilities for easy card creation and manipulation
- Unicode symbol support for beautiful card representation
- 100% test coverage

## Installation
```bash
pip install cardspy
```

## Quick Start
```python
from cardspy.deck import Deck
from cardspy.card import Card, C2C, C3D, sort_cards, cards_mask, extract_cards, rank_mask_from_cards
from cardspy.suit import CLUB, DIAMOND, HEART, SPADE
from cardspy.rank import R2, R3, R4, R5, R6, R7, R8, R9, RT, RJ, RQ, RK, RA

# Create a new deck
deck = Deck()
print(f"Deck has {deck.count()} cards")  # 52

# Shuffle and deal 5 cards
deck.shuffle()
cards_mask_val = deck.deal_cards(5)  # Bitmask of 5 cards
dealt_cards = extract_cards(cards_mask_val)
print("Dealt:", [str(card) for card in dealt_cards])

# Remove a card
deck.remove_card(C2C.key)
print(deck.contains(C2C.key))  # False

# Add a card back
deck.add_card(C2C.key)
print(deck.contains(C2C.key))  # True

# Sort cards
sorted_cards = sort_cards(dealt_cards)
print("Sorted:", [str(card) for card in sorted_cards])

# Bitmask utilities
mask = cards_mask([C2C, C3D])
print(mask)
print(extract_cards(mask))
print(rank_mask_from_cards(mask))
```

## Detailed Examples

### Working with Cards

#### Creating and Accessing Cards
```python
from cardspy.card import Card, C2C, C3D, C4H, C5S
from cardspy.suit import CLUB, DIAMOND, HEART, SPADE
from cardspy.rank import R2, R3, R4, R5

# Using predefined card constants
print(C2C)  # 2♣
print(C3D)  # 3♦
print(C4H)  # 4♥
print(C5S)  # 5♠

# Accessing card properties
print(C2C.key)      # 0x1 (unique bitmask)
print(C2C.rank)     # Rank.TWO
print(C2C.suit)     # <Suit.CLUB: 1>
print(C2C.code)     # "2C"
print(C2C.name)     # "Two of Clubs"
print(C2C.symbol)   # "2♣"

# Creating a custom card
custom_card = Card(
    key=0x1,
    rank=R2,
    suit=CLUB,
    code="2C",
    name="Two of Clubs",
    symbol="2♣"
)
```

#### Card Code Utilities
```python
from cardspy.card import get_card, get_card_key_from_code, get_cards, get_card_keys_from_codes

# Get a single card by code
card = get_card('AS')
print(card)  # A♠

# Get card key from code
key = get_card_key_from_code('10H')
print(key)  # integer key for 10 of Hearts

# Get multiple cards from codes
cards = get_cards(['2C', 'KD', 'JH'])
print(cards)  # [2♣, K♦, J♥]

# Get bitmask from card codes
keys_mask = get_card_keys_from_codes(['2C', 'KD', 'JH'])
print(keys_mask)  # bitmask representing those cards
```

### Working with Suits and Ranks

#### Suit Operations
```python
from cardspy.suit import CLUB, DIAMOND, HEART, SPADE, Suit

# Using predefined suits
print(CLUB)      # ♣
print(DIAMOND)   # ♦
print(HEART)     # ♥
print(SPADE)     # ♠

# Accessing suit properties
print(CLUB.key)      # 0x1
print(CLUB.code)     # "C"
print(CLUB.name)     # "Club"
print(CLUB.symbol)   # "♣"

# Creating a custom suit
custom_suit = Suit(
    key=0x1,
    code="C",
    name="Club",
    symbol="♣"
)
```

#### Rank Operations
```python
from cardspy.rank import R2, R3, R4, R5, R6, R7, R8, R9, RT, RJ, RQ, RK, RA, Rank

# Using predefined ranks
print(R2)  # 2
print(RK)  # K
print(RA)  # A

# Accessing rank properties
print(R2.key)   # 0x1
print(R2.code)  # "2"
print(R2.name)  # "Two"

# Creating a custom rank
custom_rank = Rank(
    key=0x1,
    code="2",
    name="Two"
)
```

### Working with Decks

#### Basic Deck Operations
```python
from cardspy.deck import Deck
from cardspy.card import C2C, C3D, C4H, C5S

# Create and manage a deck
deck = Deck()
print(deck.count())  # 52

# Shuffle the deck
deck.shuffle()

# Deal cards
cards_mask = deck.deal_cards(5)  # Deal 5 cards
cards = extract_cards(cards_mask)
print([str(card) for card in cards])

# Add and remove cards
deck.remove_card(C2C.key)
print(deck.contains(C2C.key))  # False
deck.add_card(C2C.key)
print(deck.contains(C2C.key))  # True

# Reset and clear
deck.clear()
print(deck.count())  # 0
deck.reset()
print(deck.count())  # 52
```

#### Advanced Deck Operations
```python
from cardspy.deck import Deck
from cardspy.card import C2C, C3D, C4H, C5S, cards_mask

# Deal specific cards
deck = Deck()
specific_cards = cards_mask([C2C, C3D])
deck.deal_specific_cards(specific_cards)

# Get all cards in deck
all_cards = deck.get_cards()
print([str(card) for card in all_cards])

# Add multiple cards
deck.add_cards(specific_cards)
print(deck.contains(C2C.key))  # True
print(deck.contains(C3D.key))  # True

# Remove multiple cards
deck.remove_cards(specific_cards)
print(deck.contains(C2C.key))  # False
print(deck.contains(C3D.key))  # False
```

### Bitmask Operations

#### Card Set Operations
```python
from cardspy.card import C2C, C3D, C4H, C5S, cards_mask, extract_cards, rank_mask_from_cards

# Create card sets using bitmasks
hand = [C2C, C3D, C4H, C5S]
mask = cards_mask(hand)
print(bin(mask))  # Binary representation of the bitmask

# Extract cards from bitmask
cards = extract_cards(mask)
print([str(card) for card in cards])

# Get rank mask from cards
rank_mask = rank_mask_from_cards(mask)
print(bin(rank_mask))  # Binary representation of ranks
```

#### Card Sorting and Comparison
```python
from cardspy.card import C2C, C3D, C4H, C5S, sort_cards

# Sort cards by rank
hand = [C5S, C2C, C4H, C3D]
sorted_hand = sort_cards(hand)
print([str(card) for card in sorted_hand])  # [2♣, 3♦, 4♥, 5♠]
```

## API Reference

### Card
- `Card(key, rank, suit, code, name, symbol)`
  - `key`: Unique bitmask identifier (power of 2)
  - `rank`: Rank object (R2-RK, RA)
  - `suit`: Suit object (CLUB, DIAMOND, HEART, SPADE)
  - `code`: Two-character code (e.g., "2C")
  - `name`: Full name (e.g., "Two of Clubs")
  - `symbol`: Unicode symbol (e.g., "2♣")
- Predefined constants: `C2C`, `C2D`, ..., `CAS` (all 52 cards)
- Methods: `__str__()`, `__repr__()`

### Suit
- `Suit(key, code, name, symbol)`
  - `key`: Unique bitmask (power of 2)
  - `code`: Single character (C, D, H, S)
  - `name`: Full name (Club, Diamond, Heart, Spade)
  - `symbol`: Unicode symbol (♣, ♦, ♥, ♠)
- Predefined: `CLUB`, `DIAMOND`, `HEART`, `SPADE`

### Rank
- `Rank(key, code, name)`
  - `key`: Unique bitmask (power of 2)
  - `code`: Single character (2-9, T, J, Q, K, A)
  - `name`: Full name (Two, Three, ..., Ace)
- Predefined: `R2`, `R3`, ..., `RA`

### Deck
- `Deck()` — creates a new deck (full 52 cards)
- `deck.shuffle()` — shuffle deck
- `deck.clear()` — remove all cards
- `deck.reset()` — restore to full deck
- `deck.count()` — number of cards
- `deck.get_cards()` — list of `Card` objects in deck
- `deck.add_card(card_key)` — add a card by key
- `deck.add_cards(cards_key)` — add multiple cards by bitmask
- `deck.remove_card(card_key)` — remove a card by key
- `deck.remove_cards(cards_key)` — remove multiple cards by bitmask
- `deck.deal_cards(count, shuffle=True)` — deal N cards, returns bitmask
- `deck.deal_specific_card(card_key)` — deal a specific card
- `deck.deal_specific_cards(cards_key)` — deal specific cards by bitmask
- `deck.contains(card_key)` — check if card is present

### Utility Functions (in cardspy.card)
- `sort_cards(cards)` — sort by rank
- `cards_mask(cards)` — get bitmask from list of cards
- `extract_cards(mask)` — get list of cards from bitmask
- `extract_cards_key(mask)` — get list of card keys from bitmask
- `rank_mask_from_cards(mask)` — get rank bitmask from card bitmask
- `get_card(card_code)` — get a `Card` by its two-character code
- `get_card_key_from_code(card_code)` — get the key (int) of a card by its code
- `get_cards(card_codes)` — get a list of `Card` objects from a list of codes
- `get_card_keys_from_codes(card_codes)` — get bitmask (int) from a list of codes

## Testing
To run the tests and check coverage:
```bash
pytest --cov=cardspy --cov-report=term-missing
```

## License
MIT

---
For more details, see the source code and tests in the `cardspy` and `tests` directories.