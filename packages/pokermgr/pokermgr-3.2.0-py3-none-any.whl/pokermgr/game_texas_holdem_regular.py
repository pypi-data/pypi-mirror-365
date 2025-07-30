"""Regular Texas Hold'em Game

This module implements the standard Texas Hold'em game with small and big blinds.
"""

from typing import Dict, Any

from pokermgr.table import Table
from pokermgr.action import PlayerAction, PlayerActionType, GameActionType
from pokermgr.game_texas_holdem import GameTexasHoldem
from pokermgr.player import TablePlayer, PlayerStatus
from pokermgr.game_street import GameStreet


class GameTexasHoldemRegular(GameTexasHoldem):
    """Standard Texas Hold'em game with small and big blinds.

    This class implements a regular Texas Hold'em game where players post
    small and big blinds, and betting proceeds in standard fashion.

    Args:
        key: Unique identifier for the game
        table: Table object containing player information
        small_blind: Size of the small blind
        big_blind: Size of the big blind
        initial_board_count: Number of boards to use (default: 1)
        betting_structure: Betting structure (no_limit, fixed_limit, pot_limit)
        game_type: Game type (texas_holdem, omaha)

    Attributes:
        small_blind: Size of the small blind
        big_blind: Size of the big blind
        betting_structure: The betting structure
        game_type: The game type
        small_bet: Small bet amount for fixed-limit games
        big_bet: Big bet amount for fixed-limit games
        _raises_this_round: Number of raises in current betting round
        _last_raise_amount: Amount of the last raise
    """

    def __init__(
        self,
        key: int,
        table: Table,
        small_blind: int,
        big_blind: int,
        initial_board_count: int = 1,
        betting_structure: str = "no_limit",
        game_type: str = "texas_holdem",
    ) -> None:
        super().__init__(key, table, initial_board_count)
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.betting_structure = betting_structure
        self.game_type = game_type
        self.small_bet = big_blind  # For fixed-limit games
        self.big_bet = big_blind * 2  # For fixed-limit games
        self._raises_this_round = 0
        self._last_raise_amount: float = 0.0
        self.player_contributions: Dict[TablePlayer, float] = {}
        self.initiate_board()

    def _is_valid_action(self, action: PlayerAction) -> bool:
        """Validate if the given action is allowed in a regular Texas Hold'em game.

        This implementation enforces standard Texas Hold'em rules including
        proper bet sizing, minimum raise amounts, and blind structure.

        Args:
            action: The action to validate

        Returns:
            bool: True if the action is valid, False otherwise
        """
        # For fixed-limit, we handle validation completely here to avoid base class conflicts
        if self.betting_structure == "fixed_limit":
            # Check basic player status (from base class)
            if action.player.status in [PlayerStatus.FOLDED, PlayerStatus.SITOUT, PlayerStatus.ALLIN]:
                return False
            # Check sufficient stack
            if action.player.stack < action.stack:
                return False
            return self._validate_fixed_limit_action(action)

        # For non-fixed-limit, use base Texas Hold'em rules first
        if not super()._is_valid_action(action):
            return False

        # Additional validation for regular Texas Hold'em
        elif self.betting_structure == "pot_limit":
            return self._validate_pot_limit_action(action)
        else:
            # No-limit validation
            if action.action_type == PlayerActionType.BET:
                # For bets, check if it meets minimum or is all-in
                if action.stack == action.player.stack:
                    # All-in is always allowed
                    return True
                # Otherwise, must meet minimum bet
                return action.stack >= self.big_blind

            elif action.action_type == PlayerActionType.RAISE:
                # current_bet = self._get_current_bet()

                # If player is going all-in, it's valid regardless of amount
                if action.stack == action.player.stack:
                    return True

                # Calculate minimum raise based on last raise
                min_raise_amount = self.get_minimum_raise_amount()
                return action.stack >= min_raise_amount

            elif action.action_type == PlayerActionType.CALL:
                # Call amount should match the current bet
                # current_bet = self._get_current_bet()
                call_amount = self.calculate_call_amount(action.player)
                return action.stack == call_amount

            elif action.action_type == PlayerActionType.ALLIN:
                # All-in is always valid
                return True

            return True

    def get_minimum_raise_amount(self) -> float:
        """Get the minimum raise amount based on current betting state.

        Returns:
            float: Minimum raise amount
        """
        current_bet = self._get_current_bet()

        if current_bet == 0:
            # No bet yet, minimum raise is big blind
            return self.big_blind

        # Find the last complete raise amount
        last_raise_amount: float = float(self.big_blind)  # Default to big blind

        # Look for the most recent raise to determine raise size
        # Extract player actions from game_actions
        player_actions = [
            ga.details.get('player_action') 
            for ga in self.game_actions 
            if ga.action_type == GameActionType.ACCEPT_PLAYER_ACTION and ga.details and 'player_action' in ga.details
        ]
        
        betting_actions = [
            a
            for a in player_actions
            if a and a.action_type in [PlayerActionType.BET, PlayerActionType.RAISE]
        ]

        if len(betting_actions) >= 2:
            # Calculate the difference between last two betting actions
            last_raise_amount = betting_actions[-1].stack - betting_actions[-2].stack
        elif len(betting_actions) == 1:
            # First bet, raise amount should be at least big blind more
            last_raise_amount = float(self.big_blind)

        return current_bet + max(last_raise_amount, self.big_blind)

    def calculate_call_amount(self, player: TablePlayer) -> float:
        """Calculate the amount needed for player to call current bet.

        Args:
            player: Player to calculate call amount for

        Returns:
            float: Amount needed to call (limited by player's stack)
        """
        current_bet = self._get_current_bet()

        if current_bet == 0:
            return 0.0

        # Calculate how much player has already contributed this round
        player_contribution = self.player_contributions.get(player, 0.0)

        # Call amount is the difference between current bet and what player has contributed
        call_amount = current_bet - player_contribution

        # Limited by player's available stack
        call_amount = min(call_amount, player.stack)
        return max(0.0, call_amount)  # Ensure non-negative

    def can_call(self, player: TablePlayer) -> bool:
        """Check if player can call the current bet.

        Args:
            player: Player to check

        Returns:
            bool: True if player can call
        """
        if player.status in [
            PlayerStatus.FOLDED,
            PlayerStatus.ALLIN,
            PlayerStatus.SITOUT,
        ]:
            return False

        current_bet = self._get_current_bet()
        return current_bet > 0 and player.stack > 0

    def can_raise(self, player: TablePlayer) -> bool:
        """Check if player can raise the current bet.

        Args:
            player: Player to check

        Returns:
            bool: True if player can raise
        """
        if player.status in [
            PlayerStatus.FOLDED,
            PlayerStatus.ALLIN,
            PlayerStatus.SITOUT,
        ]:
            return False

        min_raise = self.get_minimum_raise_amount()
        return player.stack >= min_raise

    def get_minimum_bet_amount(self) -> float:
        """Get the minimum bet amount.

        Returns:
            float: Minimum bet amount (big blind)
        """
        return self.big_blind

    def post_blinds(self) -> None:
        """Post small and big blinds."""
        if len(self.table.players) < 2:
            return

        # In a real implementation, we'd have positions for small blind and big blind
        # For simplicity, assume first two players are SB and BB
        sb_player = self.table.players[0] if len(self.table.players) > 0 else None
        bb_player = self.table.players[1] if len(self.table.players) > 1 else None

        # Create pot if it doesn't exist
        if not self.pots:
            self.add_pot(0)

        blinds_posted = {}
        
        # Post small blind
        if sb_player:
            sb_player.stack -= self.small_blind
            self.player_contributions[sb_player] = self.small_blind
            self.pots[0].stack += self.small_blind
            blinds_posted['small_blind'] = {
                'player': getattr(sb_player, 'code', str(sb_player)),
                'amount': self.small_blind
            }

        # Post big blind (this creates the "bet" that others must call)
        if bb_player:
            bb_player.stack -= self.big_blind
            self.player_contributions[bb_player] = self.big_blind
            self.pots[0].stack += self.big_blind
            blinds_posted['big_blind'] = {
                'player': getattr(bb_player, 'code', str(bb_player)),
                'amount': self.big_blind
            }

        # Blind posting tracked only via external process_game_action

        # Note: We don't create a BET action for blinds because they are forced bets
        # that occur before voluntary action begins. This allows the first non-blind
        # player to BET if they want to.
        
        # Set player to act to the first player after big blind
        if len(self.table.players) > 2:
            self.player_to_act = self.table.players[2]
        elif len(self.table.players) == 2:
            # Heads up: small blind acts first pre-flop
            self.player_to_act = self.table.players[0]

    def _validate_fixed_limit_action(self, action: PlayerAction) -> bool:
        """Validate action for fixed-limit betting structure.

        Args:
            action: PlayerAction to validate

        Returns:
            bool: True if action is valid
        """
        # Check if we've reached the cap on raises
        if self._raises_this_round >= 3 and action.action_type == PlayerActionType.RAISE:
            return False

        # Determine bet size based on street
        if self.game_street in [GameStreet.PRE_FLOP, GameStreet.FLOP]:
            bet_size = self.small_bet
        else:
            bet_size = self.big_bet

        if action.action_type == PlayerActionType.BET:
            # Fixed-limit bets must be exactly the bet size
            return action.stack == bet_size or action.stack == action.player.stack

        elif action.action_type == PlayerActionType.RAISE:
            # Raises must be exactly one bet increment
            current_bet = self._get_current_bet()
            new_bet_level = current_bet + bet_size
            player_contribution = self.player_contributions.get(action.player, 0.0)
            expected_wager = new_bet_level - player_contribution
            return (
                action.stack == expected_wager or action.stack == action.player.stack
            )

        elif action.action_type == PlayerActionType.CALL:
            call_amount = self.calculate_call_amount(action.player)
            return action.stack == call_amount

        elif action.action_type == PlayerActionType.ALLIN:
            return True

        return True

    def _validate_pot_limit_action(self, action: PlayerAction) -> bool:
        """Validate action for pot-limit betting structure.

        Args:
            action: PlayerAction to validate

        Returns:
            bool: True if action is valid
        """
        if action.action_type == PlayerActionType.BET:
            # In pot-limit, opening bet can be any reasonable amount (up to player's stack)
            # Once there's a pot, subsequent bets/raises are limited by pot size
            pot_size = self.get_total_pot_size()
            if pot_size == 0:
                # Opening bet - allow any amount up to stack (no pot to limit against)
                return (
                    action.stack >= self.big_blind
                    or action.stack == action.player.stack
                )
            else:
                # Subsequent bet - limited by pot size
                return action.stack <= pot_size or action.stack == action.player.stack

        elif action.action_type == PlayerActionType.RAISE:
            # Calculate max pot-limit raise
            max_raise = self.calculate_max_pot_limit_raise(action.player)
            return action.stack <= max_raise or action.stack == action.player.stack

        elif action.action_type == PlayerActionType.CALL:
            call_amount = self.calculate_call_amount(action.player)
            return action.stack == call_amount

        elif action.action_type == PlayerActionType.ALLIN:
            return True

        return True

    def _get_current_bet(self) -> float:
        """Get the current bet amount in the betting round.

        Returns:
            float: Current bet amount
        """
        # The current bet is the highest total contribution any player has made
        if self.player_contributions:
            return max(self.player_contributions.values())
        return 0.0

    def calculate_max_pot_limit_raise(self, player: TablePlayer) -> float:
        """Calculate maximum allowed raise in pot-limit games.

        Args:
            player: Player making the raise

        Returns:
            float: Maximum raise amount
        """
        # Current bet to call
        # current_bet = self._get_current_bet()
        call_amount = self.calculate_call_amount(player)

        # Pot after the call
        pot_after_call = self.get_total_pot_size() + call_amount

        # Maximum raise is the pot after call
        max_raise_total = call_amount + pot_after_call

        # Limited by player's stack
        return min(max_raise_total, player.stack)

    def register_action(self, action: PlayerAction) -> bool:
        """Register an action and update game state.

        Args:
            action: PlayerAction to register

        Returns:
            bool: True if action was registered successfully
        """
        # Reset raise count on new street
        old_street = self.game_street
        result = super().register_action(action)

        # Track raises for fixed-limit games (only if action was successful)
        if result and action.action_type == PlayerActionType.RAISE:
            self._raises_this_round += 1
            # Track last raise amount
            current_bet = self._get_current_bet()
            if current_bet > 0:
                # Extract player actions from game_actions
                player_actions = [
                    ga.details.get('player_action') 
                    for ga in self.game_actions 
                    if ga.action_type == GameActionType.ACCEPT_PLAYER_ACTION and ga.details and 'player_action' in ga.details
                ]
                
                betting_actions = [
                    a
                    for a in player_actions
                    if a and a.action_type in [PlayerActionType.BET, PlayerActionType.RAISE]
                ]
                if betting_actions:
                    self._last_raise_amount = action.stack - current_bet

        # Reset raise count on new street
        if result and self.game_street != old_street:
            self._raises_this_round = 0
            self._last_raise_amount = 0.0

        return result

    def _get_additional_state(self) -> Dict[str, Any]:
        """Get additional state specific to Texas Hold'em Regular game.
        
        Returns:
            Dict[str, Any]: Additional state including raises count
        """
        return {
            '_raises_this_round': self._raises_this_round
        }
    
    def _restore_additional_state(self, additional_state: Dict[str, Any]) -> None:
        """Restore additional state specific to Texas Hold'em Regular game.
        
        Args:
            additional_state: The additional state data to restore
        """
        if '_raises_this_round' in additional_state:
            self._raises_this_round = additional_state['_raises_this_round']
    
    def _reset_additional_betting_state(self) -> None:
        """Reset additional betting state for Texas Hold'em Regular."""
        self._raises_this_round = 0
        self._last_raise_amount = 0.0
