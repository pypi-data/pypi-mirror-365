"""Omaha Hand Evaluator

This module provides hand evaluation for Omaha poker variants,
ensuring the mandatory 2+3 rule (exactly 2 hole cards + 3 board cards).
"""

from typing import List, Tuple, Set
from itertools import combinations


class OmahaHandEvaluator:
    """Evaluates Omaha hands with the mandatory 2+3 rule."""

    def __init__(self, hole_card_count: int = 4):
        """Initialize evaluator for specific Omaha variant.
        
        Args:
            hole_card_count: Number of hole cards (4, 5, 6, or 7)
        """
        if hole_card_count not in [4, 5, 6, 7]:
            raise ValueError("Omaha variants must have 4, 5, 6, or 7 hole cards")
        self.hole_card_count = hole_card_count

    def get_all_valid_hands(self, hole_cards: List[int], board_cards: List[int]) -> List[List[int]]:
        """Get all valid 5-card hands using exactly 2 hole + 3 board cards.
        
        Args:
            hole_cards: Player's hole cards
            board_cards: Community board cards
            
        Returns:
            List of valid 5-card hands
        """
        if len(hole_cards) != self.hole_card_count:
            raise ValueError(f"Expected {self.hole_card_count} hole cards, got {len(hole_cards)}")
        if len(board_cards) != 5:
            raise ValueError(f"Expected 5 board cards, got {len(board_cards)}")
            
        valid_hands = []
        
        # All combinations of 2 hole cards
        for hole_combo in combinations(hole_cards, 2):
            # All combinations of 3 board cards
            for board_combo in combinations(board_cards, 3):
                # Create 5-card hand
                hand = list(hole_combo) + list(board_combo)
                valid_hands.append(hand)
                
        return valid_hands

    def get_best_hand(self, hole_cards: List[int], board_cards: List[int]) -> Tuple[List[int], int]:
        """Get the best possible Omaha hand using 2+3 rule.
        
        Args:
            hole_cards: Player's hole cards
            board_cards: Community board cards
            
        Returns:
            Tuple of (best_hand, hand_value)
        """
        valid_hands = self.get_all_valid_hands(hole_cards, board_cards)
        
        # For now, just return the first valid hand with a placeholder value
        # In a real implementation, this would use proper hand evaluation
        if valid_hands:
            return valid_hands[0], 1000
        else:
            return [], 0

    def is_valid_omaha_hand(self, hand: List[int], hole_cards: List[int], board_cards: List[int]) -> bool:
        """Check if a 5-card hand follows Omaha 2+3 rule.
        
        Args:
            hand: 5-card hand to validate
            hole_cards: Player's hole cards
            board_cards: Community board cards
            
        Returns:
            True if hand uses exactly 2 hole + 3 board cards
        """
        if len(hand) != 5:
            return False
            
        # Count how many cards come from hole vs board
        hole_cards_used = sum(1 for card in hand if card in hole_cards)
        board_cards_used = sum(1 for card in hand if card in board_cards)
        
        # Must use exactly 2 hole and 3 board cards
        return hole_cards_used == 2 and board_cards_used == 3


class OmahaTwoPlusThreeValidator:
    """Validates Omaha hands follow the mandatory 2+3 rule."""

    def is_valid_omaha_hand(self, hand: List[int], hole_cards: List[int], board_cards: List[int]) -> bool:
        """Check if a 5-card hand follows Omaha 2+3 rule.
        
        Args:
            hand: 5-card hand to validate
            hole_cards: Player's hole cards  
            board_cards: Community board cards
            
        Returns:
            True if hand uses exactly 2 hole + 3 board cards
        """
        if len(hand) != 5:
            return False
            
        # Count how many cards come from hole vs board
        hole_cards_used = sum(1 for card in hand if card in hole_cards)
        board_cards_used = sum(1 for card in hand if card in board_cards)
        
        # Must use exactly 2 hole and 3 board cards
        return hole_cards_used == 2 and board_cards_used == 3

    def get_hole_cards_used(self, hand: List[int], hole_cards: List[int]) -> List[int]:
        """Get which hole cards are used in the hand.
        
        Args:
            hand: 5-card hand
            hole_cards: Player's hole cards
            
        Returns:
            List of hole cards used in the hand
        """
        return [card for card in hand if card in hole_cards]

    def get_board_cards_used(self, hand: List[int], board_cards: List[int]) -> List[int]:
        """Get which board cards are used in the hand.
        
        Args:
            hand: 5-card hand
            board_cards: Community board cards
            
        Returns:
            List of board cards used in the hand
        """
        return [card for card in hand if card in board_cards]

    def validate_hand_composition(self, hand: List[int], hole_cards: List[int], board_cards: List[int]) -> dict:
        """Validate hand composition and return detailed analysis.
        
        Args:
            hand: 5-card hand to analyze
            hole_cards: Player's hole cards
            board_cards: Community board cards
            
        Returns:
            Dict with validation results and details
        """
        hole_used = self.get_hole_cards_used(hand, hole_cards)
        board_used = self.get_board_cards_used(hand, board_cards)
        
        return {
            "is_valid": len(hole_used) == 2 and len(board_used) == 3,
            "hole_cards_used": hole_used,
            "board_cards_used": board_used,
            "hole_count": len(hole_used),
            "board_count": len(board_used),
            "total_cards": len(hand)
        }