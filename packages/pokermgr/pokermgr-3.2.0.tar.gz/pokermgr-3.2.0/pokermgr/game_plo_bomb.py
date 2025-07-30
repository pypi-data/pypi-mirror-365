"""Pot Limit Omaha Bomb Game

This module implements the Pot Limit Omaha Bomb variant where all players
post a bomb amount preflop and then betting continues with pot-limit rules
on post-flop streets.
"""

from typing import Dict, List, Optional, Set
from itertools import combinations

from pokermgr.table import Table
from pokermgr.action import PlayerAction, PlayerActionType
from pokermgr.game_plo import GamePLO
from pokermgr.player import TablePlayer, PlayerStatus
from pokermgr.game_street import GameStreet
from pokermgr.pot import Pot


class GamePLOBomb(GamePLO):
    """Pot Limit Omaha Bomb game with forced preflop all-in.

    In this variant, all players must post a bomb amount preflop. Players
    with insufficient stacks go all-in. After the bomb posting, the game
    proceeds to the flop with normal pot-limit betting rules.

    Args:
        key: Unique identifier for the game
        table: Table object containing player information
        bomb_amount: Amount each player must post preflop
        initial_board_count: Number of boards to use (default: 1)
        hand_size: Number of hole cards (4, 5, 6, or 7)
        betting_structure: Betting structure (always "pot_limit" for PLO)
        game_type: Game type (always "omaha" for PLO)

    Attributes:
        bomb_amount: Mandatory bomb amount for all players
        hand_size: Number of hole cards per player
        betting_structure: The betting structure ("pot_limit")
        game_type: The game type ("omaha")
        player_contributions: Dict tracking player contributions this round
    """

    def __init__(
        self,
        key: int,
        table: Table,
        bomb_amount: int,
        initial_board_count: int = 1,
        hand_size: int = 4,
        betting_structure: str = "pot_limit",
        game_type: str = "omaha",
    ) -> None:
        """Initialize PLO Bomb game.
        
        Args:
            key: Unique identifier for the game
            table: Table object containing player information
            bomb_amount: Amount each player must post preflop
            initial_board_count: Number of boards to use (default: 1)
            hand_size: Number of hole cards (4, 5, 6, or 7)
            betting_structure: Betting structure (default: "pot_limit")
            game_type: Game type (default: "omaha")
        
        Raises:
            ValueError: If hand_size is not between 4 and 7 inclusive
            ValueError: If bomb_amount is not positive
            ValueError: If there are fewer than 2 players
        """
        if hand_size not in [4, 5, 6, 7]:
            raise ValueError(f"Invalid hand size {hand_size}. Must be 4, 5, 6, or 7.")
        
        if bomb_amount <= 0:
            raise ValueError(f"Bomb amount must be positive, got {bomb_amount}")
        
        if len(table.players) < 2:
            raise ValueError(f"PLO Bomb requires minimum 2 players, got {len(table.players)}")
        
        super().__init__(key, table, initial_board_count, hand_size, betting_structure, game_type)
        self.bomb_amount = bomb_amount
        
        # Initialize empty pot before posting bombs
        if not self.pots:
            self.add_pot(0)

    def _core_deal_hole_cards(self) -> None:
        """Deal hole cards to each player based on hand_size.
        
        This implements Omaha hole card dealing where each player
        receives hand_size (4, 5, 6, or 7) private cards.
        """
        for player in self.table.players:
            player.set_hole_cards(self.deck.deal_cards(self.hand_size))

    def deal_hole_cards(self, cards: Optional[List[int]] = None) -> None:
        """Deal hole cards to each player.
        
        Deals the specified number of hole cards (hand_size) to each player.
        
        Raises:
            ValueError: If there are not enough cards in the deck
        """
        total_cards_needed = len(self.table.players) * self.hand_size
        if total_cards_needed > 52:
            raise ValueError(f"Not enough cards in deck. Need {total_cards_needed}, deck has 52.")
        
        for player in self.table.players:
            hole_cards = self.deck.deal_cards(self.hand_size)
            
            # Add player to each board
            for board in self.boards:
                board.add_board_player(player, hole_cards)

    def post_bomb_amounts(self) -> None:
        """Post bomb amounts for all players.
        
        Each player posts the bomb amount. Players with insufficient stacks
        post their entire stack and are marked as all-in. Creates side pots
        as necessary.
        """
        # Clear any existing contributions
        self.player_contributions.clear()
        
        # Track players and their contributions for side pot creation
        contributions: List[tuple[TablePlayer, float]] = []
        bomb_contributions = {}
        
        for player in self.table.players:
            # Player posts bomb amount or their entire stack if insufficient
            contribution = min(self.bomb_amount, player.stack)
            
            # Update player stack
            player.stack -= contribution
            
            # Track contribution
            self.player_contributions[player] = contribution
            contributions.append((player, contribution))
            bomb_contributions[getattr(player, 'code', str(player))] = contribution
            
            # Update player status
            if player.stack == 0:
                player.status = PlayerStatus.ALLIN
            else:
                player.status = PlayerStatus.INGAME
        
        # Sort contributions to create side pots
        contributions.sort(key=lambda x: x[1])
        
        # Clear existing pots and create new ones based on contributions
        self.pots.clear()
        
        # Create main pot and side pots
        remaining_players = list(self.table.players)
        last_contribution = 0.0
        
        for i, (player, contribution) in enumerate(contributions):
            if contribution > last_contribution:
                # Calculate pot size for this level
                pot_contribution = contribution - last_contribution
                pot_size = pot_contribution * len(remaining_players)
                
                # Create pot with eligible players
                pot = self.add_pot(int(pot_size), remaining_players.copy())
                
                last_contribution = contribution
            
            # Remove all-in player from remaining players if they can't contribute more
            if player.status == PlayerStatus.ALLIN:
                remaining_players.remove(player)
        
        # Update PLO pot tracking for proper pot limit calculations
        total_bomb_amount = sum(self.player_contributions.values())
        self.pot_current_street = total_bomb_amount
        self.current_bet = max(self.player_contributions.values()) if self.player_contributions else 0.0
        
        # Bomb posting tracked only via external process_game_action

    def _is_valid_action(self, action: PlayerAction) -> bool:
        """Validate if the given action is allowed in PLO Bomb.

        During preflop, no betting actions are allowed as all players are
        forced to post the bomb amount. Post-flop follows pot-limit rules.

        Args:
            action: The action to validate

        Returns:
            bool: True if the action is valid, False otherwise
        """
        # No actions allowed preflop in bomb pot
        if self.game_street == GameStreet.PRE_FLOP:
            return False
        
        # Post-flop validation
        # Check basic player status
        if action.player.status in [PlayerStatus.FOLDED, PlayerStatus.SITOUT, PlayerStatus.ALLIN]:
            return False
        
        # Check sufficient stack
        if action.player.stack < action.stack:
            return False

        # Validate specific action types
        if action.action_type == PlayerActionType.FOLD:
            return True
            
        elif action.action_type == PlayerActionType.CHECK:
            # Can only check if no bet to call
            return self.current_bet == 0
            
        elif action.action_type == PlayerActionType.CALL:
            # Call amount should match what's needed to call
            call_amount = self.calculate_call_amount(action.player)
            return action.stack == call_amount
            
        elif action.action_type == PlayerActionType.BET:
            # Validate pot-limit bet
            return self._validate_pot_limit_bet(action)
            
        elif action.action_type == PlayerActionType.RAISE:
            # Validate pot-limit raise
            return self._validate_pot_limit_raise(action)
            
        elif action.action_type == PlayerActionType.ALLIN:
            return True

        return False




    def _validate_pot_limit_bet(self, action: PlayerAction) -> bool:
        """Validate pot-limit bet for bomb pot.
        
        Args:
            action: Bet action to validate
            
        Returns:
            bool: True if bet is valid
        """
        # Can only bet if no current bet exists
        if self.current_bet > 0:
            return False
            
        # Use parent class validation which implements correct PLO formula
        return super()._validate_pot_limit_bet(action)

    def _validate_pot_limit_raise(self, action: PlayerAction) -> bool:
        """Validate pot-limit raise for bomb pot.
        
        Args:
            action: Raise action to validate
            
        Returns:
            bool: True if raise is valid
        """
        # Must have a bet to raise
        if self.current_bet == 0:
            return False
            
        # Use parent class validation which implements correct PLO formula
        return super()._validate_pot_limit_raise(action)

    def advance_to_flop(self, burn_card: bool = False) -> None:
        """Advance the game to the flop.
        
        In bomb pot, this automatically happens after bomb posting.
        Deals 3 community cards and resets betting state.
        
        Args:
            burn_card: If True, burn a card before dealing flop
        """
        self.game_street = GameStreet.FLOP
        
        # Burn a card if requested
        if burn_card:
            self.deck.deal_cards(1)
        
        # Deal 3 community cards to each board
        for board in self.boards:
            if board.cards == 0:  # No cards on board yet
                flop_cards = self.deck.deal_cards(3)
                board.add_cards(flop_cards)
        
        # Reset betting round state using parent class method
        self._advance_street()
        
        # Board dealing tracked only via external process_game_action

    def advance_to_turn(self, burn_card: bool = False) -> None:
        """Advance the game to the turn and deal 1 community card.
        
        Args:
            burn_card: If True, burn a card before dealing turn
        """
        self.game_street = GameStreet.TURN
        
        # Burn a card if requested
        if burn_card:
            self.deck.deal_cards(1)
        
        # Deal 1 community card to each board
        for board in self.boards:
            turn_card = self.deck.deal_cards(1)
            board.add_cards(turn_card)
        
        # Reset betting round state using parent class method
        self._advance_street()
        
        # Board dealing tracked only via external process_game_action

    def advance_to_river(self, burn_card: bool = False) -> None:
        """Advance the game to the river and deal 1 community card.
        
        Args:
            burn_card: If True, burn a card before dealing river
        """
        self.game_street = GameStreet.RIVER
        
        # Burn a card if requested
        if burn_card:
            self.deck.deal_cards(1)
        
        # Deal 1 community card to each board
        for board in self.boards:
            river_card = self.deck.deal_cards(1)
            board.add_cards(river_card)
        
        # Reset betting round state using parent class method
        self._advance_street()
        
        # Board dealing tracked only via external process_game_action

    def advance_to_showdown(self) -> None:
        """Advance the game to showdown."""
        self.game_street = GameStreet.SHOWDOWN


    def get_active_players_for_betting(self) -> List[TablePlayer]:
        """Get list of players eligible for betting (not folded or all-in).
        
        Returns:
            List of players who can still bet
        """
        return [p for p in self.table.players if p.status == PlayerStatus.INGAME]

    def get_board_player(self, player: TablePlayer, board_index: int) -> Optional[object]:
        """Get the board player for a given table player and board.
        
        Args:
            player: The table player
            board_index: Index of the board
            
        Returns:
            Board player object or None if not found
        """
        if board_index >= len(self.boards):
            return None
            
        board = self.boards[board_index]
        for board_player in board.players:
            if board_player.code == player.code:
                return board_player
        
        return None

    def get_valid_hand_combinations(self, hole_cards: List[int], board_cards: List[int]) -> List[List[int]]:
        """Get all valid Omaha hand combinations using exactly 2 hole + 3 board cards.
        
        Args:
            hole_cards: List of hole card integers
            board_cards: List of board card integers
            
        Returns:
            List of valid 5-card combinations
        """
        valid_combinations = []
        
        # Generate all combinations of 2 hole cards
        for hole_combo in combinations(hole_cards, 2):
            # Generate all combinations of 3 board cards
            for board_combo in combinations(board_cards, 3):
                # Combine into 5-card hand
                hand = list(hole_combo) + list(board_combo)
                valid_combinations.append(hand)
        
        return valid_combinations

    def is_valid_omaha_hand(self, hand: List[int], hole_cards: List[int], board_cards: List[int]) -> bool:
        """Check if a hand is a valid Omaha hand (exactly 2 hole + 3 board cards).
        
        Args:
            hand: 5-card hand to validate
            hole_cards: Available hole cards
            board_cards: Available board cards
            
        Returns:
            bool: True if hand follows Omaha 2+3 rule
        """
        if len(hand) != 5:
            return False
            
        hole_used = sum(1 for card in hand if card in hole_cards)
        board_used = sum(1 for card in hand if card in board_cards)
        
        return hole_used == 2 and board_used == 3

    def get_best_omaha_hand(self, hole_cards: List[int], board_cards: List[int]) -> List[int]:
        """Get the best possible Omaha hand using 2 hole + 3 board cards.
        
        Args:
            hole_cards: Available hole cards
            board_cards: Available board cards
            
        Returns:
            Best 5-card Omaha hand
        """
        valid_combinations = self.get_valid_hand_combinations(hole_cards, board_cards)
        
        # For now, return the first valid combination
        # In a full implementation, this would evaluate hand strength
        if valid_combinations:
            return valid_combinations[0]
        
        return []