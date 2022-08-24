from unittest import TestCase, main
from logics.helpers import match_cards


class matchCardTest(TestCase):
    def test_last_in_known(self):
        self.assertTrue(match_cards([1], [2], [3, 1], 2, 0))

    def test_last_in_deck(self):
        self.assertTrue(match_cards([2], [1], [3, 1], 2, 0))

    def test_make_deck_known(self):
        self.assertTrue(match_cards([], [1, 4, 5], [3, 1], 3, 0))
        self.assertTrue(match_cards([7], [1, 4, 5, 6, 2], [1], 5, 1))

    def test_last_no_where(self):
        with self.assertRaises(ValueError) as e:
            match_cards([2], [0], [3, 1], 1, 0)
        self.assertEqual('Last card on the table must be in known nor in deck', e.exception.args[0])

    def test_all_cards_known(self):
        with self.assertRaises(ValueError) as e:
            match_cards([2], [0], [0], 3, 0)
            match_cards([2], [], [3, 1], 5, 0)
        self.assertEqual('Absence of real deck means all cards in play are turned up and known', e.exception.args[0])


if __name__ == '__main__':
    main()
