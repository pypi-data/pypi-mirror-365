"""
Constants for poker.
"""

from typing import List

__version__ = "3.0.0"

# Poker hand constants (must be at the top to avoid circular import issues)
RANK_ORDER = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "T": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14,
}

STRAIGHTS: List[int] = [
    0x1F,
    0x100F,
    0x3E,
    0x7C,
    0xF8,
    0x1F0,
    0x3E0,
    0xF80,
    0x1F00,
]

STRAIGHT_FLUSH = 0x8000000000
FOUR_OF_A_KIND = 0x4000000000
FULL_HOUSE = 0x2000000000
FLUSH = 0x1000000000
STRAIGHT = 0x800000000
THREE_OF_A_KIND = 0x400000000
TWO_PAIRS = 0x200000000
PAIR = 0x100000000
HIGH_CARD = 0x80000000

HAND_WEIGHT: List[int] = [
    STRAIGHT_FLUSH,
    FOUR_OF_A_KIND,
    FULL_HOUSE,
    FLUSH,
    STRAIGHT,
    THREE_OF_A_KIND,
    TWO_PAIRS,
    PAIR,
    HIGH_CARD,
]

HAND_TYPES = [
    "Straight Flush",
    "Four of a Kind",
    "Full House",
    "Flush",
    "Straight",
    "Three of a Kind",
    "Two Pairs",
    "Pair",
    "High Card",
]

HAND_TYPE_MAPPING = {
    STRAIGHT_FLUSH: "Straight Flush",
    FOUR_OF_A_KIND: "Four of a Kind",
    FULL_HOUSE: "Full House",
    FLUSH: "Flush",
    STRAIGHT: "Straight",
    THREE_OF_A_KIND: "Three of a Kind",
    TWO_PAIRS: "Two Pairs",
    PAIR: "Pair",
    HIGH_CARD: "High Card",
}


TWOS = 0xF
THREES = 0xF0
FOURS = 0xF00
FIVES = 0xF000
SIXES = 0xF0000
SEVENES = 0xF00000
EIGHTS = 0xF000000
NINES = 0xF0000000
TENS = 0xF00000000
JACKS = 0xF000000000
QUEENS = 0xF0000000000
KINGS = 0xF00000000000
ACE = 0xF000000000000

# Import game simulators for easy access (at the end to avoid circular imports)
from pokermgr.game_simulator_texas_holdem_regular import GameSimulatorTexasHoldemRegular
from pokermgr.game_simulator_texas_holdem_bomb import GameSimulatorTexasHoldemBomb
from pokermgr.game_simulator_plo_regular import GameSimulatorPLORegular
from pokermgr.game_simulator_plo_bomb import GameSimulatorPLOBomb

__all__ = [
    "GameSimulatorTexasHoldemRegular",
    "GameSimulatorTexasHoldemBomb", 
    "GameSimulatorPLORegular",
    "GameSimulatorPLOBomb",
]
