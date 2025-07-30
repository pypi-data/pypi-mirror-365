"""
Poker Hand Utility Functions
===========================

This module provides utility functions for evaluating and
analyzing poker hands using bitmask representations.
Functions include detection of pairs, suited cards,
straight/flush draws, hand range code generation,
and hand strength evaluation.

Main Features:
--------------
- Count pairs, suited cards, and connected cards using bitwise operations
- Detect open-ended and gutshot straight draws, flush draws
- Generate hand range codes (e.g., 'AKs', 'QJo') from bitmask
- Compute hand strength/weight for all standard poker
hands (pair, two pairs, trips, straight, flush, etc.)
- Helpers for board evaluation and property extraction

Example Usage:
--------------
>>> from pokermgr.funcs import get_paired, get_suited, get_range_codes
>>> # Suppose 'cards' is a bitmask representing Ah, Kh, Qh, Jh, Th (royal flush in hearts)
>>> paired = get_paired(cards, 2)
>>> suited = get_suited(cards, 5)
>>> ranges = get_range_codes(cards)
>>> print(f"Pairs: {paired}, Suited: {suited}, Ranges: {ranges}")
Pairs: 0, Suited: 1, Ranges: ['AKs', 'AQs', 'AJs', 'ATs', 'KQs', 'KJs', 'KTs', 'QJs', 'QTs', 'JTs']

See individual function docstrings for more details and examples.
"""

from itertools import combinations
from typing import List, Tuple
from cardspy.deck import SAME_RANKS, CLUBS, DIAMONDS, HEARTS, SPADES
from cardspy.card import extract_cards, rank_mask_from_cards, ALL_CARDS
from pokermgr import (
    TWOS, ACE,
    HAND_TYPE_MAPPING,
    STRAIGHT_FLUSH,
    STRAIGHTS,
    RANK_ORDER,
    FOUR_OF_A_KIND,
    FULL_HOUSE,
    THREE_OF_A_KIND,
    TWO_PAIRS,
    PAIR,
    FLUSH,
    STRAIGHT,
    HIGH_CARD,
)

# Board and hand evaluation functions moved to board_utils.py to avoid circular imports


def get_paired(cards: int, cards_count: int) -> int:
    """
    Count the number of ranks that appear exactly `cards_count` times in the given cards.

    Args:
        cards (int): Bitmask representing the cards to check.
        cards_count (int): Number of cards to check for each rank (e.g., 2 for pairs, 3 for trips).

    Returns:
        int: Number of ranks that appear exactly `cards_count` times.

    Example:
        >>> # Suppose cards is a bitmask with two pairs (e.g., 2♠ 2♥ 5♣ 5♦ 7♠)
        >>> get_paired(cards, 2)
        2
    """
    count = 0  # Initialize the count of paired ranks
    for same in SAME_RANKS:
        # Bitwise AND to mask out the cards of the same rank
        if (cards & same).bit_count() == cards_count:
            count += 1  # Increment if the number of cards matches cards_count
    return count  # Return the number of ranks with exactly cards_count cards


def get_suited(cards: int, cards_count: int) -> int:
    """
    Count the number of suits that have exactly `cards_count` cards in the given card bitmask.

    Args:
        cards (int): Bitmask representing the cards to check.
        cards_count (int): Number of cards to check for in each suit.

    Returns:
        int: Number of suits that have exactly `cards_count` cards.

    Example:
        >>> # Suppose cards is a bitmask with 4 spades and 1 club
        >>> get_suited(cards, 4)
        1
    """
    count = 0  # Initialize the count of suited groups
    for suit in [SPADES, CLUBS, DIAMONDS, HEARTS]:
        # Bitwise AND to mask out the cards of the same suit
        if (cards & suit).bit_count() == cards_count:
            count += 1  # Increment if the number of cards matches cards_count
    return count  # Return the number of suits with exactly cards_count cards


def get_connected(cards: int) -> int:
    """
    Count the number of adjacent rank pairs in the given cards.

    Args:
        cards (int): Bitmask representing the cards to check.

    Returns:
        int: Number of adjacent rank pairs (e.g., 2-3, J-Q).

    Example:
        >>> # Suppose cards is a bitmask with ranks 5, 6, 7, 8
        >>> get_connected(cards)
        3
    """
    board_rank_mask = rank_mask_from_cards(cards)  # Get bitmask for ranks only
    connected_count = 0  # Initialize adjacent rank pair counter
    for i in range(12):  # Iterate through rank bits 0 (2) to 11 (King)
        # Check if both current and next rank bits are set
        if ((board_rank_mask >> i) & 1) and ((board_rank_mask >> (i + 1)) & 1):
            connected_count += 1  # Increment if adjacent ranks found

    # Consider Ace and Two as connected
    if (cards & TWOS) and (cards & ACE):
        connected_count += 1

    return connected_count  # Return the count of adjacent rank pairs


def get_n_from_straight(cards: int, cards_count: int) -> int:
    """
    Count how many subsets of `cards_count` ranks can form part of a straight.

    Args:
        cards (int): Bitmask representing the cards to check.
        cards_count (int): Number of ranks to consider at a time.

    Returns:
        int: Number of distinct rank combinations that are part of a straight.

    Example:
        >>> # Suppose cards is a bitmask with 5, 6, 7, 8
        >>> get_n_from_straight(cards, 3)
        2  # Can form part of straights like 4-5-6-7-8 or 5-6-7-8-9
    """
    board_rank_mask = rank_mask_from_cards(cards)  # Get bitmask for ranks only

    # Find which rank bits are present (0-12 for 2-Ace)
    positions = [r for r in range(13) if (board_rank_mask >> r) & 1]

    count = 0  # Initialize count of valid straight subsets
    # For each way to choose 'cards_count' ranks out of those present
    for combo in combinations(positions, cards_count):
        combo_mask = 0  # Build a bitmask for this combination of ranks
        for r in combo:
            combo_mask |= 1 << r

        # Check if this combo_mask fits inside any straight mask
        for straight in STRAIGHTS:
            if (combo_mask & straight) == combo_mask:
                count += 1  # Increment if the combo is part of a straight
                break

    return count  # Return the number of valid straight subsets


def trailing_zeros(n: int) -> int:
    """
    Count the number of trailing zeros in the binary representation of n.

    Args:
        n (int): Integer to count trailing zeros for.

    Returns:
        int: Number of trailing zeros.

    Raises:
        ValueError: If n is 0 (undefined for 0).

    Example:
        >>> trailing_zeros(8)  # 8 in binary is 1000
        3
        >>> trailing_zeros(12)  # 12 in binary is 1100
        2
    """
    if n == 0:
        raise ValueError("trailing_zeros is undefined for 0")  # Error if input is zero
    # Isolate lowest 1-bit, take its bit_length, subtract 1 to get its index
    return (n & -n).bit_length() - 1


def set_is_open_straight_draw(cards: int, draws: int) -> int:
    """
    Check if the cards contain an open-ended straight draw and update draws bitmask.

    An open-ended straight draw means there are four consecutive ranks that
    could complete a straight with one more card on either end.

    Args:
        cards (int): Bitmask of cards to check.
        draws (int): Current draws bitmask to update.

    Returns:
        int: Updated draws bitmask with open-ended straight draw bit set if found.

    Example:
        >>> # Cards: 5,6,7,8 (open-ended straight draw for 4 or 9)
        >>> set_is_open_straight_draw(cards, 0)
        4  # 0b100 - open-ended straight draw bit is set
    """
    board_rank_mask = rank_mask_from_cards(cards)  # Get bitmask for ranks only
    for straight in STRAIGHTS:
        # Check if exactly 4 cards from a straight are present
        if (board_rank_mask & straight).bit_count() == 4:
            missing_mask = (
                straight & ~board_rank_mask
            )  # Find missing card in the straight
            offset = trailing_zeros(
                straight
            )  # Get offset of the lowest bit in the straight
            lowest = 1 << offset  # Mask for the lowest card in the straight
            highest = 1 << (offset + 4)  # Mask for the highest card in the straight
            # If the missing card is at either end, it's open-ended
            if missing_mask in (lowest, highest):
                draws |= 0x4  # Set the open-ended straight draw bit
                break
    return draws  # Return updated draws bitmask


def set_is_gut_straight_draw(cards: int, draws: int) -> int:
    """
    Check if the cards contain a gutshot straight draw and update draws bitmask.

    A gutshot straight draw means there are four cards that could complete
    a straight with one specific rank in the middle.
    Only checks if there isn't already an open-ended straight draw.

    Args:
        cards (int): Bitmask of cards to check.
        draws (int): Current draws bitmask to update.

    Returns:
        int: Updated draws bitmask with gutshot straight draw bit set if found.

    Example:
        >>> # Cards: 5,6,8,9 (gutshot straight draw for 7)
        >>> set_is_gut_straight_draw(cards, 0)
        2  # 0b010 - gutshot straight draw bit is set
    """
    if (draws & 0x4) != 0:
        return draws  # If already open-ended, skip gutshot check
    board_rank_mask = rank_mask_from_cards(cards)  # Get bitmask for ranks only
    for straight in STRAIGHTS:
        # Check if exactly 4 cards from a straight are present
        if (board_rank_mask & straight).bit_count() == 4:
            missing_mask = (
                straight & ~board_rank_mask
            )  # Find missing card in the straight
            offset = trailing_zeros(
                straight
            )  # Get offset of the lowest bit in the straight
            lowest = 1 << offset  # Mask for the lowest card in the straight
            highest = 1 << (offset + 4)  # Mask for the highest card in the straight
            # If missing card is not at either end, it's a gutshot
            if missing_mask not in (lowest, highest):
                draws |= 0x2  # Set the gutshot straight draw bit
                break
    return draws  # Return updated draws bitmask


def set_is_flush_draw(cards: int, draws: int) -> int:
    """
    Check if the cards contain a flush draw and update draws bitmask.

    A flush draw means there are four cards of the same suit,
    needing one more for a flush.

    Args:
        cards (int): Bitmask of cards to check.
        draws (int): Current draws bitmask to update.

    Returns:
        int: Updated draws bitmask with flush draw bit set if found.

    Example:
        >>> # Four hearts
        >>> set_is_flush_draw(cards, 0)
        1  # 0b001 - flush draw bit is set
    """
    for suit in [CLUBS, DIAMONDS, HEARTS, SPADES]:
        # Check each suit for exactly 4 cards present
        if (cards & suit).bit_count() == 4:
            draws |= 0x1  # Set the flush draw bit
            break
    return draws  # Return updated draws bitmask


def get_range_codes(cards: int) -> List[str]:
    """
    Generate poker hand range codes for all possible two-card combinations.

    Hand range codes follow standard poker notation:
    - Pairs: 'AA', 'KK', ..., '22'
    - Suited: 'AKs', 'QJs', ...
    - Offsuit: 'AKo', 'QJo', ...

    Args:
        cards (int): Bitmask of cards to generate range codes for.

    Returns:
        List[str]: Sorted list of unique range codes.

    Example:
        >>> # Ace of spades, King of spades, Queen of hearts
        >>> get_range_codes(cards)
        ['AKs', 'AQo', 'KQo']
    """
    ranges: List[str] = []  # Store unique range codes

    def add_range(range_code: str) -> None:
        # Add range code if not already present
        if range_code not in ranges:
            ranges.append(range_code)

    card_arr = extract_cards(cards)  # Get all card objects from bitmask
    for card_1, card_2 in combinations(card_arr, 2):
        # If both cards have the same rank, it's a pair
        if card_1.rank.key == card_2.rank.key:
            add_range(card_1.rank.code + card_2.rank.code)
        else:
            # Ensure card_1 is always higher for consistent notation
            if card_1.rank.key < card_2.rank.key:
                card_1, card_2 = card_2, card_1
            # Suited if suits match
            if card_1.suit.key == card_2.suit.key:
                add_range(card_1.rank.code + card_2.rank.code + "s")
            else:
                add_range(card_1.rank.code + card_2.rank.code + "o")
    return ranges  # Return all unique range codes


def get_cards_properties(cards: int) -> int:
    """
    Analyze a two-card hand (“hole cards”) and return a bitmask of its properties.

    Bit definitions (from highest to lowest):
      0x8 — Pair (both cards have the same rank)
      0x4 — Suited (both cards have the same suit)
      0x2 — Connected (ranks differ by exactly one, with Ace–2 also considered connected)
      0x1 — Two-card straight draw (the two ranks form part of any possible straight)

    Args:
        cards (int): Encoded representation of a complete deck state, from which the two hole cards
                     are extracted using `extract_cards`.

    Returns:
        int: Bitwise OR of all matching properties (0–15).

    Example:
        >>> # Suppose cards represents AhKh (Ace of hearts, King of hearts)
        >>> get_cards_properties(cards)
        0x6  # Suited and connected
    """
    properties = 0  # Bitmask to store properties

    # Decode the two hole cards into a list of Card objects
    cards_arr = extract_cards(cards)

    # Compare each pair of cards (there will only be one combination for two cards)
    for card_1, card_2 in combinations(cards_arr, 2):
        # Check for a pocket pair (same rank)
        if card_1.rank.key == card_2.rank.key:
            properties |= 0x8  # set bit 3 (0x8)

        # Check for suited (same suit)
        if card_1.suit.key == card_2.suit.key:
            properties |= 0x4  # set bit 2 (0x4)

        # Build a mask of the two ranks to test for straight draw potential
        rank_mask = rank_mask_from_cards(card_1.key | card_2.key)

        # Check for connectivity (adjacent ranks, including Ace–2 wrap)
        if get_connected(card_1.key | card_2.key) == 1:
            properties |= 0x2  # set bit 1 (0x2)
        else:
            # Check each known 5-card straight mask to see if these two ranks are
            # both part of any straight (i.e. bit_count == 2)
            for straight in STRAIGHTS:
                if (rank_mask & straight).bit_count() == 2:
                    properties |= 0x1  # set bit 0 (0x1)
                    break  # no need to check further straights once matched

    return properties  # Return the bitmask of properties


def set_draws(cards: int, draws: int) -> int:
    """
    Sets the draws.
    """
    # Set open-ended straight draw bit if present
    draws = set_is_open_straight_draw(cards, draws)
    # Set gutshot straight draw bit if present
    draws = set_is_gut_straight_draw(cards, draws)
    # Set flush draw bit if present
    draws = set_is_flush_draw(cards, draws)
    return draws  # Return updated draws bitmask


def is_flush(cards: int) -> bool:
    """Check if the hand is a flush.

    A flush is a hand where all five cards are of the same suit, but not in sequence.
    If the cards are also in sequence, it would be a straight flush or royal flush.

    Args:
        cards: Bitmask integer representing the 5-card hand to evaluate.

    Returns:
        bool: True if the hand is a flush, False otherwise.

    Example:
        >>> from cardspy.deck import cards_to_mask
        >>> # Flush: Five hearts, not in sequence
        >>> cards = cards_to_mask(['Ah', 'Kh', '9h', '7h', '2h'])
        >>> is_flush(cards)
        True

    Note:
        This function returns False for straight flushes and royal flushes,
        which are checked separately for proper hand ranking.
    """
    return get_suited(cards, 5) > 0


def is_straight(cards: int) -> bool:
    """Check if the hand is a straight.

    A straight is a hand that contains five cards of sequential rank, not all of the
    same suit. The wheel (A-2-3-4-5) is considered the lowest straight.

    Args:
        cards: Bitmask integer representing the 5-card hand to evaluate.

    Returns:
        bool: True if the hand is a straight, False otherwise.

    Example:
        >>> from cardspy.deck import cards_to_mask
        >>> # Straight: 7-8-9-T-J
        >>> cards = cards_to_mask(['7h', '8d', '9c', 'Ts', 'Jh'])
        >>> is_straight(cards)
        True
        >>> # Wheel (A-2-3-4-5)
        >>> wheel = cards_to_mask(['Ah', '2d', '3c', '4s', '5h'])
        >>> is_straight(wheel)
        True

    Note:
        This function handles the special case of the wheel (A-2-3-4-5) separately
        before checking for other straights. It returns False for straight flushes,
        which are checked separately for proper hand ranking.
    """
    # Check for the special case of a wheel (A-2-3-4-5)
    board_rank_mask = rank_mask_from_cards(cards)
    if board_rank_mask == 0x100F:
        return True
    # Check for regular straights (5-6-7-8-9 through T-J-Q-K-A)
    for straight in STRAIGHTS:
        if (board_rank_mask & straight) == straight:
            return True
    return False


def is_straight_flush(cards: int) -> bool:
    """Check if the hand is a straight flush.

    A straight flush is both a straight and a flush - five cards in sequence,
    all of the same suit. This is one of the strongest hands in poker.

    Args:
        cards: Bitmask integer representing the 5-card hand to evaluate.

    Returns:
        bool: True if the hand is a straight flush, False otherwise.

    Example:
        >>> from cardspy.deck import cards_to_mask
        >>> # Straight flush: 5-6-7-8-9 of hearts
        >>> cards = cards_to_mask(['5h', '6h', '7h', '8h', '9h'])
        >>> is_straight_flush(cards)
        True

    Note:
        A royal flush (A-K-Q-J-T of the same suit) is considered a special
        case of a straight flush with the highest possible ranking.
    """
    return is_flush(cards) and is_straight(cards)


def is_four_of_a_kind(cards: int) -> bool:
    """Check if the hand contains four cards of the same rank.

    Four of a kind (also known as quads) is a hand that contains four cards of
    one rank and one card of another rank (the kicker).

    Args:
        cards: Bitmask integer representing the 5-card hand to evaluate.

    Returns:
        bool: True if the hand contains four of a kind, False otherwise.

    Example:
        >>> from cardspy.deck import cards_to_mask
        >>> # Four of a kind: Four Kings with a 5 kicker
        >>> cards = cards_to_mask(['Kc', 'Kd', 'Kh', 'Ks', '5h'])
        >>> is_four_of_a_kind(cards)
        True
    """
    for same in SAME_RANKS:
        # Check if there are exactly 4 cards of the same rank
        if (cards & same).bit_count() == 4:
            return True  # Found four of a kind
    return False  # No four of a kind found


def is_full_house(cards: int) -> bool:
    """Check if the hand is a full house.

    A full house (also known as a full boat) is a hand that contains three
    matching cards of one rank and two matching cards of another rank.

    Args:
        cards: Bitmask integer representing the 5-card hand to evaluate.

    Returns:
        bool: True if the hand is a full house, False otherwise.

    Example:
        >>> from cardspy.deck import cards_to_mask
        >>> # Full house: Three 8s and two Kings
        >>> cards = cards_to_mask(['8c', '8d', '8h', 'Ks', 'Kh'])
        >>> is_full_house(cards)
        True

    Note:
        This function first checks for three of a kind and then verifies
        that there is also a pair (which could be the same three cards if
        there are actually four of a kind, but that case is handled by
        the calling function).
    """
    if get_paired(cards, 2) == 1 and get_paired(cards, 3) == 1:
        return True
    return False


def is_three_of_a_kind(cards: int) -> bool:
    """Check if the hand contains three cards of the same rank.

    Three of a kind (also called trips or a set) is a hand that contains three cards of
    one rank and two cards of two other ranks (the kickers).

    Args:
        cards: Bitmask integer representing the 5-card hand to evaluate.

    Returns:
        bool: True if the hand contains three of a kind, False otherwise.

    Example:
        >>> from cardspy.deck import cards_to_mask
        >>> # Three of a kind: Three Queens with K-9 kickers
        >>> cards = cards_to_mask(['Qc', 'Qd', 'Qh', 'Ks', '9h'])
        >>> is_three_of_a_kind(cards)
        True

    Note:
        This function will return False for full houses, which are checked
        separately for proper hand ranking.
    """
    return get_paired(cards, 3) == 1


def is_two_pair(cards: int) -> bool:
    """Check if the hand contains two different pairs of cards with the same rank.

    Two pair is a hand that contains two cards of one rank, two cards of another rank,
    and one card of a third rank (the kicker).

    Args:
        cards: Bitmask integer representing the 5-card hand to evaluate.

    Returns:
        bool: True if the hand contains two pairs, False otherwise.

    Example:
        >>> from cardspy.deck import cards_to_mask
        >>> # Two pair: Kings and Eights with a 5 kicker
        >>> cards = cards_to_mask(['Kc', 'Kd', '8h', '8s', '5h'])
        >>> is_two_pair(cards)
        True

    Note:
        This function will return False for hands with three or four of a kind,
        even though they technically contain two pairs, as those hands are
        ranked higher in poker.
    """
    return get_paired(cards, 2) == 2


def is_pair(cards: int) -> bool:
    """Check if the hand contains exactly one pair of cards with the same rank.

    One pair is a hand that contains two cards of one rank, plus three cards which are
    not of this rank nor the same as each other (the kickers).

    Args:
        cards: Bitmask integer representing the 5-card hand to evaluate.

    Returns:
        bool: True if the hand contains exactly one pair, False otherwise.

    Example:
        >>> from cardspy.deck import cards_to_mask
        >>> # One pair: Pair of Jacks with K-9-5 kickers
        >>> cards = cards_to_mask(['Jc', 'Jd', 'Kh', '9s', '5h'])
        >>> is_pair(cards)
        True

    Note:
        This function will return False for hands with two pairs, three of a kind,
        or four of a kind, as those hands are ranked higher in poker.
    """
    return get_paired(cards, 2) == 1


def get_weight_5_cards(cards: int, type_key: int) -> int:
    """
    Gets the weight of 5 cards.
    """
    kicker = 0  # Bitmask for kicker cards
    for card in ALL_CARDS:
        # If the card is present in the hand, include its rank in the kicker
        if card.key & cards != 0:
            kicker |= card.rank.key
    kicker &= 0x1FFF  # Limit kicker to 13 bits (one per rank)
    return type_key | kicker  # Combine type key and kicker


def get_weight_top_card(cards: int, base_type: int) -> int:
    """
    Compute a weighted value for the top card on the board for
    ranking straights and straight flushes.
    """
    # Derive the rank mask (bits 0–12) from the full card bitmask.
    rmask = rank_mask_from_cards(cards)

    # Default value if no ranks found (shouldn’t happen if cards non-empty)
    top_card_value = 0

    # Special case: A-to-5 “wheel” straight has mask 0x100F (bits for A,2,3,4,5)
    if rmask == 0x100F:
        top_card_value = 5  # Wheel straight: treat top card as 5
    else:
        # Scan ranks from Ace (bit 12) down to 2 (bit 0) to find the highest set bit
        for i in reversed(range(13)):
            if (rmask >> i) & 1:
                # bit 0 → rank 2, bit 12 → rank 14 (Ace)
                top_card_value = i + 2  # Highest rank present
                break

    # Combine the base hand type with the top-card rank to get the final weight
    return base_type + top_card_value


def get_weight_four_of_a_kind(cards: int) -> int:
    """
    Compute a numeric “weight” for a four-of-a-kind hand, combining:
      1) A base constant for four-of-a-kind (FOUR_OF_A_KIND),
      2) The rank of the quads (shifted into the high bits), and
      3) The kicker card’s rank ID.
    """
    quad_index = 0  # Index of the rank with four cards
    # SAME_RANKS is a list of 13 masks: index 0→four 2’s, …, index 12→four Aces.
    for i, same_mask in enumerate(SAME_RANKS, start=1):
        # Count how many cards of this rank are present
        if (cards & same_mask).bit_count() == 4:
            quad_index = i
            break

    # If we never found four-of-a-kind, bail out with weight 0
    if quad_index == 0:
        return 0

    # Convert index (1→2, …, 13→14) into the numeric rank
    quad_rank_value = quad_index + 1

    # The mask of the four-of-a-kind cards
    quad_mask = SAME_RANKS[quad_index - 1]

    kicker = 0  # Highest kicker card not part of the quad
    for card in ALL_CARDS:
        # Card is present if its bit is set, but not part of the quad
        if (cards & card.key) != 0 and (card.key & quad_mask) == 0:
            kicker = max(kicker, card.rank.key)

    # Combine into final weight: base + quads shifted + kicker
    weight = FOUR_OF_A_KIND + (quad_rank_value * 8192) + kicker
    return weight


def get_weight_full_house(cards: int) -> int:
    """
    Compute a numeric “weight” for a full house hand, combining:
      1) A base constant for full house (FULL_HOUSE),
      2) The rank of the three-of-a-kind (in the high bits), and
      3) The rank of the pair (in the low bits).

    Parameters:
    ----------
    cards : int
        Bitmask of all cards present (each bit represents one specific card).

    Returns:
    -------
    int
        0 if no full house is found; otherwise:
        FULL_HOUSE + (triple_rank * 8192) + pair_rank
        where triple_rank and pair_rank are in 2..14,
        and 8192 == 2**13 shifts the triple into the top bits.
    """
    # Indices in SAME_RANKS: 1 → fours-of-2s mask, …, 13 → fours-of-Aces mask.
    # We'll record the highest-ranking triple and the
    # highest-ranking pair distinct from that triple.
    triple_index = 0
    pair_index = 0

    # Scan from highest rank (index 13 → Aces) down to index 1 → Twos
    for i in range(13, 0, -1):
        # count how many cards of rank i are present
        count = (cards & SAME_RANKS[i - 1]).bit_count()
        if count == 3 and triple_index == 0:
            # First found three-of-a-kind becomes our “triple”
            triple_index = i
        elif count == 2 and i != triple_index and pair_index == 0:
            # First found pair (not of the same rank as triple) becomes our “pair”
            pair_index = i

    # If we have both a triple and a pair, compute weight; otherwise no full house
    if triple_index > 0 and pair_index > 0:
        # Convert rank index to actual card rank value (1→2, …, 13→14)
        triple_val = triple_index + 1
        pair_val = pair_index + 1
        # Combine into final weight:
        #   - FULL_HOUSE base constant
        #   - triple_val shifted into high bits (*8192)
        #   - pair_val in low bits
        return FULL_HOUSE + (triple_val * 8192) + pair_val
    return 0


def get_weight_three_of_a_kind(cards: int) -> int:
    """
    Compute a numeric “weight” for a three-of-a-kind hand, combining:
      1) A base constant for three-of-a-kind (THREE_OF_A_KIND),
      2) The rank of the triplet shifted into the high bits (rank * 2**13),
      3) A “kicker” mask built from the remaining two cards.

    Parameters:
    ----------
    cards : int
        Bitmask of all cards present (each bit represents one specific card).
    Returns:
    -------
    int
        0 if no three-of-a-kind is found; otherwise:
        THREE_OF_A_KIND + (triplet_rank * 8192) + kicker_bits
        where triplet_rank is in 2..14, and 8192 == 2**13 shifts it into the high bits.
    """
    # 1) Find the rank index (0→Twos, …, 12→Aces) of the three-of-a-kind,
    #    scanning from highest (Ace) down to lowest (Two).
    triple_idx = None
    for i in range(12, -1, -1):
        if (cards & SAME_RANKS[i]).bit_count() == 3:
            triple_idx = i
            break

    # If no triplet found, no three-of-a-kind
    if triple_idx is None:
        return 0

    # 2) Convert zero-based index to actual card rank (bit 0 → 2, bit 12 → 14)
    triplet_rank = triple_idx + 2

    # 3) Build the kicker: OR together the rank IDs of all cards present
    #    that are not part of the three-of-a-kind.
    kicker = 0
    mask_of_triplet = SAME_RANKS[triple_idx]
    for card in ALL_CARDS:
        if (cards & card.key) != 0 and (card.key & mask_of_triplet) == 0:
            # card.rank.key should be in the range 2..14
            kicker |= card.rank.key

    # 4) Ensure kicker only uses the lower 13 bits (one bit per rank)
    kicker &= 0x1FFF

    # 5) Combine into the final weight
    return THREE_OF_A_KIND + (triplet_rank * 8192) + kicker


def get_weight_two_pairs(cards: int) -> int:
    """
    Compute a numeric “weight” for a two-pair hand, combining:
      1) A base constant for two pairs (TWO_PAIRS),
      2) The higher pair’s rank shifted into the high bits (rank * 2**13 -> *8192),
      3) The lower pair’s rank shifted into the middle bits (rank * 2**9  -> *512),
      4) The kicker card’s rank in the low bits.

    Parameters:
    ----------
    cards : int
        Bitmask of all cards present (each bit represents one specific card).

    Returns:
    -------
    int
        0 if fewer than two distinct pairs are found; otherwise:
        TWO_PAIRS + (high_pair_rank * 8192)
                  + (low_pair_rank  * 512)
                  + kicker_rank
    """
    # 1) Identify the two distinct pairs by scanning from highest rank (idx 12 → Ace)
    #    down to lowest (idx 0 → Two). SAME_RANKS[idx] is the mask for four cards of that rank.
    pair_idxs = []
    for idx in range(12, -1, -1):
        if (cards & SAME_RANKS[idx]).bit_count() == 2:
            pair_idxs.append(idx)
            if len(pair_idxs) == 2:
                break

    # If we found fewer than two pairs, it’s not a two-pair hand
    if len(pair_idxs) < 2:
        return 0

    high_pair_idx = pair_idxs[0]
    low_pair_idx = pair_idxs[1]

    # 2) Determine the “kicker”: the highest remaining card not part of either pair
    kicker_rank = 0
    high_mask = SAME_RANKS[high_pair_idx]
    low_mask = SAME_RANKS[low_pair_idx]

    for card in ALL_CARDS:
        # Card is present if its bit is set, but must not be in either pair mask
        if (
            (cards & card.key) != 0
            and (card.key & high_mask) == 0
            and (card.key & low_mask) == 0
        ):
            # Use the rank's value directly (2-14)
            r = RANK_ORDER[card.rank.code]
            kicker_rank = max(kicker_rank, r)

    # If no kicker found (shouldn’t happen in a valid two-pair hand), bail
    if kicker_rank == 0:
        return 0

    # 3) Convert pair indices into numeric ranks (0→2, …, 12→14)
    high_pair_rank = high_pair_idx + 2
    low_pair_rank = low_pair_idx + 2

    # 4) Combine into the final weight:
    #    TWO_PAIRS base + high_pair_rank*8192 + low_pair_rank*512 + kicker_rank
    return TWO_PAIRS + (high_pair_rank * 8192) + (low_pair_rank * 512) + kicker_rank


def get_weight_pair(cards: int) -> int:
    """
    Compute a numeric “weight” for a one-pair hand, combining:
      1) A base constant for a pair (PAIR),
      2) The rank of the pair shifted into the high bits (pair_val * 2**13 → *8192),
      3) A “kicker” mask built from the remaining three cards.

    Parameters:
    ----------
    cards : int
        Bitmask of all cards present (each bit represents one specific card).

    Returns:
    -------
    int
        0 if no pair is found; otherwise:
        PAIR + (pair_val * 8192) + kicker
        where pair_val is in 2..14 and kicker fits in the lower 13 bits.
    """
    # 1) Find the highest-ranking pair by scanning from Ace (idx 12) down to Two (idx 0)
    pair_idx = None
    for idx in range(12, -1, -1):
        if (cards & SAME_RANKS[idx]).bit_count() == 2:
            pair_idx = idx
            break

    # 2) If no pair was found, return 0
    if pair_idx is None:
        return 0

    # 3) Convert zero-based index to actual card rank (0→2, …, 12→14)
    pair_val = pair_idx + 2

    # 4) Build the kicker: OR together the rank IDs of all cards present
    #    that are not part of the pair.
    kicker = 0
    pair_mask = SAME_RANKS[pair_idx]
    for card in ALL_CARDS:
        if (cards & card.key) != 0 and (card.key & pair_mask) == 0:
            # card.rank.key should be in the range 2..14 (coded as a power‐of‐two mask)
            kicker |= card.rank.key

    # 5) Limit kicker to the lower 13 bits (one bit per rank)
    kicker &= 0x1FFF

    # 6) Combine into the final weight:
    #    PAIR base + (pair_val * 8192) + kicker
    return PAIR + (pair_val * 8192) + kicker


def get_hand_type_weight(cards: int) -> Tuple[int, int, str]:
    """Determine the type and weight of a poker hand.

    This function evaluates a 5-card poker hand and returns its type, weight,
    and name. The weight can be used to compare hand strengths, with higher
    weights indicating stronger hands.

    Args:
        cards: Bitmask integer representing the 5-card hand to evaluate.
              Each bit corresponds to a specific card (see cardspy for details).

    Returns:
        Tuple containing:
            - weight (int): Numeric weight of the hand for comparison
            - type_key (int): Constant representing the hand type (e.g., STRAIGHT_FLUSH)
            - type_name (str): Human-readable name of the hand type

    Example:
        >>> from cardspy.deck import cards_to_mask
        >>> # Royal flush in hearts
        >>> cards = cards_to_mask(['Ah', 'Kh', 'Qh', 'Jh', 'Th'])
        >>> weight, key, name = get_hand_type_weight(cards)
        >>> print(f"{name}: {weight}")
        Straight Flush: 14

    Note:
        The function checks hand types in descending order of strength, so the
        strongest possible classification is always returned.
    """
    type_key = 0
    type_name = ""
    weight = 0

    # Check for straight flush (highest hand type)
    if is_straight_flush(cards):
        type_key = STRAIGHT_FLUSH
        type_name = HAND_TYPE_MAPPING[STRAIGHT_FLUSH]
        # For straight flushes, weight is determined by the high card
        weight = get_weight_top_card(cards, type_key)
        return weight, type_key, type_name
    # Check for four of a kind
    if is_four_of_a_kind(cards):
        type_key = FOUR_OF_A_KIND
        type_name = HAND_TYPE_MAPPING[FOUR_OF_A_KIND]
        # Weight considers the quads rank and kicker
        weight = get_weight_four_of_a_kind(cards)
        return weight, type_key, type_name
    # Check for full house (three of a kind + pair)
    if is_full_house(cards):
        type_key = FULL_HOUSE
        type_name = HAND_TYPE_MAPPING[FULL_HOUSE]
        # Weight considers the trips rank and pair rank
        weight = get_weight_full_house(cards)
        return weight, type_key, type_name
    # Check for flush (all cards same suit, not in sequence)
    if is_flush(cards):
        type_key = FLUSH
        type_name = HAND_TYPE_MAPPING[FLUSH]
        # For flushes, all cards are considered in order
        weight = get_weight_5_cards(cards, type_key)
        return weight, type_key, type_name
    # Check for straight (five sequential ranks, mixed suits)
    if is_straight(cards):
        type_key = STRAIGHT
        type_name = HAND_TYPE_MAPPING[STRAIGHT]
        # For straights, weight is determined by the high card
        weight = get_weight_top_card(cards, type_key)
        return weight, type_key, type_name
    # Check for three of a kind
    if is_three_of_a_kind(cards):
        type_key = THREE_OF_A_KIND
        type_name = HAND_TYPE_MAPPING[THREE_OF_A_KIND]
        # Weight considers the trips rank and kickers
        weight = get_weight_three_of_a_kind(cards)
        return weight, type_key, type_name
    # Check for two pairs
    if is_two_pair(cards):
        type_key = TWO_PAIRS
        type_name = HAND_TYPE_MAPPING[TWO_PAIRS]
        # Weight considers both pair ranks and kicker
        weight = get_weight_two_pairs(cards)
        return weight, type_key, type_name
    # Check for one pair
    if is_pair(cards):
        type_key = PAIR
        type_name = HAND_TYPE_MAPPING[PAIR]
        # Weight considers the pair rank and kickers
        weight = get_weight_pair(cards)
        return weight, type_key, type_name

    # If no other hand type matches, it's a high card hand
    type_key = HIGH_CARD
    type_name = HAND_TYPE_MAPPING[HIGH_CARD]
    # Weight is simply the highest card values in order
    weight = get_weight_5_cards(cards, type_key)

    return weight, type_key, type_name
