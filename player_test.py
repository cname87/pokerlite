import random
import unittest
from components import Card
from configuration import Game_Code, MIN_BET_OR_RAISE, MAX_BET_OR_RAISE

# Mock classes to support testing
class MockGamePlay(Game_Code):
    
    @property
    def player_name(self) -> str:
        return "player_1"
    
    def take_bet(self, required_bet: int, is_raise_allowed: bool = True):
        # Mock behavior based on the test case
        # Return a valid bet, raise, or 0 to fold
        if required_bet == 0: # opening bet
            bet: int = random.randint(MIN_BET_OR_RAISE, MAX_BET_OR_RAISE)
        else:
            random_play = random.randint(1, 3)
            bet = 0
            match(random_play):
                case 1:
                    bet = 0 # fold
                case 2:
                    bet = required_bet # see
                case 3:
                    if is_raise_allowed:
                        bet = required_bet + random.randint(MIN_BET_OR_RAISE, MAX_BET_OR_RAISE) # raise    
                    else:
                        bet = required_bet # see
                case _:
                    pass
        return bet

from player import Player

class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.game_play = MockGamePlay()
        self.player = Player("TestPlayer", self.game_play, 1000)

    def test_initialization(self):
        self.assertEqual(self.player.name, "TestPlayer")
        self.assertEqual(self.player.game_play, self.game_play)
        self.assertEqual(self.player.cash_balance, 1000)
        self.assertIsInstance(self.player.card, Card)

    def test_card_setter_getter(self):
        test_card = Card(5)
        self.player.card = test_card
        self.assertEqual(self.player.card, test_card)

    def test_bet_running_total_setter_getter(self):
        self.player.bet_running_total = 100
        self.assertEqual(self.player.bet_running_total, 100)

    def test_take_bet(self):
        # Add specific test cases for take_bet method
        pass

    def test_place_bet(self):
        initial_balance = self.player.cash_balance
        bet_amount = 100
        self.player.place_bet(bet_amount)
        self.assertEqual(self.player.cash_balance, initial_balance - bet_amount)

    def test_collect_winnings(self):
        initial_balance = self.player.cash_balance
        winnings = 200
        self.player.collect_winnings(winnings)
        self.assertEqual(self.player.cash_balance, initial_balance + winnings)

    def test_repr(self):
        self.assertEqual(repr(self.player), "Player('TestPlayer')")

if __name__ == '__main__':
    unittest.main()
