import unittest
from components import Deck, Card

class TestCard(unittest.TestCase):

    def setUp(self):
        self.card1 = Card(5)
        self.card2 = Card(10)
        self.card3 = Card(5)

    def test_value(self):
        self.assertEqual(self.card1.value, 5)
        self.assertEqual(self.card2.value, 10)

    def test_lt(self):
        self.assertTrue(self.card1 < self.card2)
        self.assertFalse(self.card2 < self.card1)

    def test_gt(self):
        self.assertTrue(self.card2 > self.card1)
        self.assertFalse(self.card3 > self.card2)

    def test_repr(self):
        self.assertEqual(repr(self.card1), '5')
        self.assertEqual(repr(self.card3), '5')
        self.assertEqual(repr(self.card2), '10')


class TestDeck(unittest.TestCase):
    def setUp(self):
        # Create a deck with 10 cards (1 to 10)
        self.deck = Deck([Card(1),Card(2),Card(3),Card(4),Card(5),Card(6),Card(7),Card(8),Card(9),Card(10)])

    def test_deck_creation(self):
        # Check if the deck contains the expected number of cards
        self.assertEqual(len(self.deck), 10)

    def test_deal_cards(self):
        # Deal two cards and verify that they are different
        card1, card2 = self.deck.deal()
        self.assertIsInstance(card1, Card)
        self.assertIsInstance(card2, Card)
        self.assertNotEqual(card1, card2)

    def test_shuffle_deck(self):
        # Create a shuffled deck and verify that it's different from the original
        shuffled_deck = Deck.create(count=10, shuffle=True)
        self.assertNotEqual(self.deck, shuffled_deck)
        self.assertEqual(len(self.deck), len(shuffled_deck))

    def test_repr(self):
        # Verify that the representation of the deck is as expected
        expected_repr = " ".join(repr(Card(n)) for n in range(1, 11))
        self.assertEqual(repr(self.deck), expected_repr)

if __name__ == '__main__':
    unittest.main()


