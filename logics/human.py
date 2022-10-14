from re import sub
from logics.helpers import find_to_add, card_bigger, differ


def input_processing(cards):
    cards = sub(r'\D+', ' ', cards)
    cards = cards.strip()
    cards = cards.split()
    if cards:
        cards = [int(card) for card in cards]
    else:
        cards = []
    return cards


def choose_card(cards_qty, on_table):
    suggestion = f'enter card number from 1 to {cards_qty} ' \
                 f'or press enter to discards/take: ' if on_table > 0 \
        else f'enter card number from 1 to {cards_qty}: '

    number = -1
    while number == -1:
        number = input(suggestion)
        number = input_processing(number)
        if len(number) == 1:
            if 0 < number[0] <= cards_qty:
                number = number[0]
            else:
                print('You entered wrong value. Try again')
                number = -1
        elif not len(number):
            if on_table > 0:
                number = 0
            else:
                number = -1
        else:
            print('You need to enter only one value. Try again')
            number = -1

    return number


def show_table(opp_qty, table, deck, trump, hand):
    opponent = 'opponent:'
    for i in range(opp_qty):
        opponent += ' x'

    deck_vis = ''
    for i in range(deck):
        deck_vis += ' x'

    print(opponent, opp_qty, '\n')
    print(f'table: {table} deck {deck_vis} {deck} {trump} \n')
    print(f'hand: {hand}')


class Human:
    def __init__(self, name, hand, trump):
        self.name = name
        self.hand = hand
        self.trump = trump
        self.opp_cards_qty = 6
        self.real_deck = 24
        self.known = []

    def find_trump(self, trump):
        # теперь игрок знает, что есть козырь и что есть последняя карта в колоде
        self.trump = trump
        # сортируем и находим первый козырь, он же самый маленький
        self.hand.sort()
        for card in self.hand:
            if card.has_suit(trump):
                return card
        return False

    def attack(self, table):
        if table:
            self.opp_cards_qty -= 1
        show_table(self.opp_cards_qty, table, self.real_deck, self.trump, self.hand)

        chosen = choose_card(len(self.hand), len(table))

        if chosen == 0:
            return 'discards'
        if not table:
            return self.hand.pop(chosen - 1)

        can_be_added = find_to_add(self.hand, table)
        while self.hand[chosen - 1] not in can_be_added:
            print('This card cannot be added. Choose another one '
                  'or 0 as a discards action')
            chosen = choose_card(len(self.hand), len(table))
            if chosen == 0:
                return 'discards'

        return self.hand.pop(chosen - 1)

    def defence(self, table):
        self.opp_cards_qty -= 1
        show_table(
            self.opp_cards_qty, table, self.real_deck, self.trump, self.hand)

        chosen = choose_card(len(self.hand), len(table))
        if chosen == 0:
            return 'take'

        while not card_bigger(self.hand[chosen - 1], table[-1], self.trump):
            print('You cannot beat by this card. '
                  'Choose another one or 0 as a take action')
            chosen = choose_card(len(self.hand), len(table))
            if chosen == 0:
                return 'take'

        return self.hand.pop(chosen - 1)

    def addons(self, table):
        show_table(
            self.opp_cards_qty, table, self.real_deck, self.trump, self.hand)
        can_be_added = find_to_add(self.hand, table)

        if not can_be_added:
            print('There is no cards to add')
            return []

        qty_to_add = self.opp_cards_qty if \
            len(table) // 2 + self.opp_cards_qty < 6 else 6 - (len(table) // 2)
        hand = len(self.hand)
        result = False
        while not result:
            cards_to_add = input(f'Enter cards no. (from 1 to {hand}) to  '
                                 f'separated by spaces you want to add '
                                 f'(not more than {qty_to_add}) ')

            cards_to_add = input_processing(cards_to_add)
            if not cards_to_add:
                return []

            if len(cards_to_add) <= qty_to_add:
                cannot_add = [self.hand[i - 1] for i in cards_to_add if
                              self.hand[int(i) - 1] not in can_be_added]

                if cannot_add:
                    print(f'These cards cannot be added: '
                          f'{cannot_add}. Try again')
                else:
                    cards_to_add = [self.hand[i - 1] for i in cards_to_add]
                    self.hand = differ(self.hand, cards_to_add)
                    return cards_to_add
            else:
                print(f'Too many cards were chosen. '
                      f'Maximum qty is: {qty_to_add}')

    def check_addons(self, addons):
        """заглушка для механизма"""
        self.known.clear()

    def behavior_check(self, table):
        """Заглушка для механизма"""
        return None

    def make_turn(self, table, defence=False):
        if defence:
            return self.defence(table)
        return self.attack(table)
