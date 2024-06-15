#!/usr/bin/env python

"""
To be decided if useful...
"""

import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('utility')

from configuration import CARD_HIGH_NUMBER

def remove_number(list: list[int], num_to_remove: int) -> list[int]:
    # Returns a new list with a number removed but leaves the original list unchanged
    return [num for num in list if num != num_to_remove]

def opening_bet(
    pot: int,
    required_bet: int,
    other_player_bets: list[int] = [],
) -> list[int]:

    """
        Returns a list of the card numbers that the player should bet on, when the player is to open, i.e. has the choice to open or to check.
        Note that the result is dependent on an estimate of the other player's betting strategy.

        Args:
            pot: int: The value of the pot before the bet is made.
            required_bet: int: The bet that the player must make.
            other_player_bets: list[int]: An estimated list of the card numbers that the other player will see and not fold.

        Returns:
            list[int]: A list of card numbers for which the player should make an open bet on.
    """

    # An estimated list of the cards for which the other player will bet and not fold
    if other_player_bets == []:
       other_player_bets = [8,9]
       # other_player_bets = bet_after_open(pot, required_bet)

    bet_cards: list[int] = []
    # Run though each possible player card and decide whether it should be be bet on
    for card in range(1, CARD_HIGH_NUMBER + 1):
        # The other player cannot bet on the same card as the player
        cleaned_other_player_bets = remove_number(other_player_bets, card)
        winnings: int = 0
        cost = 0
        # Run through all the cards the other player could hold
        for other_card in [i for i in range(1, CARD_HIGH_NUMBER + 1) if i != card]:
            if other_card not in cleaned_other_player_bets: # Other player folds
                winnings += pot
            else: # Other player sees
                if card > other_card: # Player wins
                    winnings += pot + required_bet
                else:
                    cost += required_bet # Other player wins
        if (winnings - cost) >= 0: # Bet if return is zero, or greater, otherwise check
            bet_cards.append(card)
    return bet_cards

def opening_bet_after_check(
    pot: int,
    required_bet: int,
    other_player_bets: list[int] = [],
) -> list[int]:

    """
        Returns a list of the card numbers that the player should bet on, when the player is to open after the other player has checked
        The player has the choice to open or to check.  If the player checks the round ends and th pot is carried into the next round.
        Note that the result is dependent on an estimate of the other player's betting strategy.

        Args:
            pot: int: The value of the pot before the bet is made.
            required_bet: int: The bet that the player must make.
            other_player_bets: list[int]: An estimated list of the card numbers that the other player will see and not fold.

        Returns:
            list[int]: A list of card numbers for which the player should make an open on.
    """

    # An estimated list of the cards for which the other player will bet and not fold
    if other_player_bets == []:
       other_player_bets = [5,6,7]
       # other_player_bets = bet_after_open(pot, required_bet)

    bet_cards: list[int] = []
    # Run though each possible player card and decide whether it should be be bet on
    for card in range(1, CARD_HIGH_NUMBER + 1):
        # The other player cannot bet on the same card as the player
        cleaned_other_player_bets = remove_number(other_player_bets, card)
        winnings: int = 0
        cost = 0
        # Run through all the cards the other player could hold
        for other_card in [i for i in range(1, CARD_HIGH_NUMBER + 1) if i != card]:
            if other_card not in cleaned_other_player_bets: # Other player folds
                winnings += pot
            else: # Other player sees
                if card > other_card: # Player wins
                    winnings += pot + required_bet
                else:
                    cost += required_bet # Other player wins
        if (winnings - cost) >= 0: # Bet if return is zero, or greater
            bet_cards.append(card)
    return bet_cards

def bet_after_open(
    pot: int,
    required_bet: int,
    other_player_bets: list[int] = [],
) -> list[int]:

    """
        Returns a list of the card numbers that the player should bet on, when the player has the choice to see a required bet or fold.
        The result is dependent on an estimate of the other player's betting strategy.

        Args:
            pot: int: The value of the pot before the bet is made.
            required_bet: int: The bet that the player must make.
            other_player_bets: list[int]: An estimated list of the card numbers that the other player has bet, and not checked.

        Returns:
            list[int]: A list of card numbers for which the player should bet on.
    """

    # An estimated list of the cards for which the other player has bet and not checked
    if other_player_bets == []:
        other_player_bets = [8,9]
        # other_player_bets = opening_bet(pot, required_bet)

    bet_cards: list[int] = []
    for card in range(1, CARD_HIGH_NUMBER + 1):
        cleaned_other_player_bets = remove_number(other_player_bets, card)
        winnings: int = 0
        cost = 0
        # Run through all the cards the other player could hold
        for other_card in [i for i in range(1, CARD_HIGH_NUMBER + 1) if i != card]:
            if other_card not in cleaned_other_player_bets: # Other player checks
                winnings += 0 # Player checks
            else: # Other player bets
                if card > other_card: # Player wins
                    winnings += pot + required_bet
                else:
                    cost += required_bet
        if (winnings - cost) >= 0: # Bet if return is zero, or greater
            bet_cards.append(card)
    return bet_cards


def bet_after_check(
    pot: int,
    required_bet: int,
    other_player_bets: list[int] = [],
) -> list[int]:

    """
        Returns a list of the card numbers that the player should bet on, when the player has the choice to see a required bet or fold.
        In this case the other player has bet after the player has previously checked.
        The result is dependent on an estimate of the other player's betting strategy.

        Args:
            pot: int: The value of the pot before the bet is made.
            required_bet: int: The bet that the player must make.
            other_player_bets: list[int]: An estimated list of the card numbers that the other player has bet, and not checked.

        Returns:
            list[int]: A list of card numbers for which the player should bet on.
    """

    # An estimated list of the cards for which the other player has bet and not checked
    if other_player_bets == []:
        other_player_bets = [5,6,7,8,9]
        # other_player_bets = opening_bet(pot, required_bet)

    bet_cards: list[int] = []
    for card in range(1, CARD_HIGH_NUMBER + 1):
        # other_player_bets = [8,9]
        cleaned_other_player_bets = remove_number(other_player_bets, card)
        winnings: int = 0
        cost = 0
        # Run through all the cards the other player could hold
        for other_card in [i for i in range(1, CARD_HIGH_NUMBER + 1) if i != card]:
            if other_card not in cleaned_other_player_bets: # Other player checks
                winnings += 0 # Player checks
            else: # Other player bets
                if card > other_card: # Player wins
                    winnings += pot + required_bet
                else:
                    cost += required_bet
        if (winnings - cost) >= 0: # Bet if return is zero, or greater
            bet_cards.append(card)
    return bet_cards

def bet_cards(
        pot: int,
        bet: int,
    ) -> dict[str, list[int]]:

    # Initial estimate for the cards for which the player will bet in response to the opening bet
    second_bet_estimate = [i for i in range((CARD_HIGH_NUMBER + 1)//2, CARD_HIGH_NUMBER + 1)]

    opening_bet_result = []
    second_bet_result = []
    max_loops = 5
    while max_loops > 0:
        # Start with an estimate of the second bet
        copied_second_bet_estimate = second_bet_estimate.copy()
        opening_bet_result = opening_bet(
            pot=pot,
            required_bet=bet,
            other_player_bets=copied_second_bet_estimate
        )
        second_bet_result = bet_after_open(
            pot=pot,
            required_bet=bet,
            other_player_bets=opening_bet_result
        )

        logger.debug(f"Second bet estimate for pot = {pot} and bet = {bet}  : {second_bet_estimate}")
        logger.debug(f"Second bet interim result for pot = {pot} and bet = {bet}  : {second_bet_result}")

        # Check if the card decks match
        if second_bet_result == second_bet_estimate:
            break

        # Update the estimate for the second bet
        second_bet_estimate = second_bet_result

        max_loops -= 1

    logger.debug(f"Final opening bet for pot = {pot} and bet = {bet}  : {opening_bet_result}")
    logger.debug(f"Final second bet for pot = {pot} and bet = {bet}  : {second_bet_result}")

    return {
        "Opening Bet": opening_bet_result,
        "Second Bet": second_bet_result
    }

# print(opening_bet(20,100))
# print(opening_bet_after_check(20,100))
# print(bet_after_check(20,1000))
# print(bet_cards(20, 100))
