# Масти для вывода в консоль
SUITS = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠'}
VALUES = {6: '6', 7: '7', 8: '8', 9: '9', 10: '10', 11: 'J', 12: 'Q', 13: 'K', 14: 'A',
          15: '6', 16: '7', 17: '8', 18: '9', 19: '10', 20: 'J', 21: 'Q', 22: 'K', 23: 'A'}
# Печать козырей с переопределенной ценностью см. тестер make_trumps


# Карты в колоде и их методы
class Card:
    def __init__(self, value, suit):
        self.value = value  # Значение карты(6, 7... 10, 11, 12, 13, 14)
        self.suit = suit    # Масть карты

    def __str__(self):
        return f"{VALUES[self.value]}{SUITS[self.suit]}"

    def __repr__(self):
        return f"{VALUES[self.value]}{SUITS[self.suit]}"

    def __eq__(self, other_card):
        if self.suit == other_card.suit and self.value == other_card.value:
            return True
        return False

    def has_suit(self, other_card):
        return self.suit == other_card.suit

    def same_value(self, other_card):
        return self.value == other_card.value or \
               self.value == other_card.value + 9 or \
               self.value == other_card.value - 9

    def __ne__(self, other_card):
        return self.suit != other_card.suit

    def __gt__(self, other_card):
        return self.value > other_card.value

    def __lt__(self, other_card):
        return self.value < other_card.value

    def __sub__(self, other_card):
        return self.value - other_card.value

    def greater(self, other_card):
        return self.value > other_card.value
