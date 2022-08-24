from logics.head import imagine_sequences, valuate, follower, valuate_addons, super_sequence, super_follower
from logics.helpers import after_take, differ, match_cards
from logics.card import Card


class Player:
    def __init__(self, name, hand, trump, deck):
        self.name = name
        self.hand = hand[:]
        self.known = []
        self.opp_cards_qty = 6
        self.deck = differ(deck, hand)
        self.real_deck = 0
        self.trump = trump
        self.limited_sequence = []
        self.super = None
        self.stop = 0

    def find_trump(self, trump):
        # теперь игрок знает, что есть козырь и что есть последняя карта в колоде
        self.trump = trump
        # сортируем и находим первый козырь, он же самый маленький
        self.hand.sort()
        for card in self.hand:
            if card.has_suit(trump):
                return card
        return False

    def attack(self, table=None):

        # если стола нет, это значит игроки получили карты из колоды и эти карты необходимо пересчитать.
        # если есть стол. Удаляем последнюю карту стола из карт оппонента если она есть в известных
        # либо удаляем ее из мнимой колоды

        if not table:
            self.deck = differ(self.deck, self.hand) if self.deck else self.deck
        else:
            if len(self.known) == self.opp_cards_qty:
                self.known.remove(table[-1])
                self.opp_cards_qty -= 1
            else:
                self.known, self.deck, self.opp_cards_qty = match_cards(self.known, self.deck, table,
                                                                        self.opp_cards_qty, self.real_deck)

        # print(table, id(self.hand), self.hand, self.known, id(self.deck), self.deck, 'real', self.real_deck,
        #       self.opp_cards_qty)
        # # TODO Момент когда неизвестные карты становятся известными
        # if self.real_deck <= 1 and len(self.deck) > self.real_deck:
        #     if self.real_deck == 1 and self.opp_cards_qty - len(self.known) == len(self.deck[:-1]):
        #         self.known += self.deck[:-1]
        #         self.deck = list(self.deck[-1])
        #     if self.real_deck == 0 and self.opp_cards_qty - len(self.known) == len(self.deck):
        #         self.known += self.deck
        #         self.deck.clear()

        # Случай в котором мы точно знаем, что неизвестная часть колоды отправляется только в свою руку
        # if 6 - len(self.hand) >= len(self.deck[:-1]) and len(self.known) == self.opp_cards_qty:
        #     print('we got here')
        #     if not self.super:
        #         if not table:
        #             table = []
        #         self.super = super_sequence(self.hand, self.known, self.trump, self.deck, table)
        #         self.limited_sequence, self.stop = super_follower(self.super, self.stop, self.hand, self.known)
        #         card = follower(self.limited_sequence, table)
        #         if isinstance(card, Card):
        #             return self.hand.pop(self.hand.index(card))
        #         elif isinstance(card, str):
        #             self.limited_sequence = []
        #             return 'discards'
        #     else:
        #         if not self.limited_sequence:
        #             self.limited_sequence, self.stop = super_follower(self.super, self.stop, self.hand, self.known)
        #         if self.limited_sequence:
        #             card = follower(self.limited_sequence, table)
        #             if isinstance(card, Card):
        #                 return self.hand.pop(self.hand.index(card))
        #             elif isinstance(card, str):
        #                 self.limited_sequence = []
        #                 return 'discards'
        #             elif isinstance(card, bool):
        #                 self.super = super_sequence(self.hand, self.known, self.trump, self.deck, table)
        #                 self.limited_sequence, self.stop = super_follower(self.super, self.stop, self.hand, self.known)
        #                 card = follower(self.limited_sequence, table)
        #                 if isinstance(card, Card):
        #                     return self.hand.pop(self.hand.index(card))
        #                 elif isinstance(card, str):
        #                     self.limited_sequence = []
        #                     return 'discards'

        # Когда мы не перешли в конечную фазу игры
        if table and self.limited_sequence:
            card = follower(self.limited_sequence, table)
            if isinstance(card, Card):
                return self.hand.pop(self.hand.index(card))
            elif isinstance(card, str):
                self.limited_sequence = []
                return 'discards'
            # else:
            #     self.limited_sequence = []

        if not table:
            table = []

        # self.limited_sequence = []
        sequences = imagine_sequences(self.hand, self.known, self.trump, table)
        self.limited_sequence = valuate(sequences, self.hand, self.known, self.deck, self.opp_cards_qty, len(table))
        card = follower(self.limited_sequence, table)

        if isinstance(card, Card):
            return self.hand.pop(self.hand.index(card))
        # if isinstance(card, str):
        else:
            self.limited_sequence = []
            return 'discards'

    def addons(self, table):
        # если режим супер и если режим обычный
        if not self.hand:
            return []

        if not self.super:
            cards = after_take(self.hand, self.opp_cards_qty, table)
            cards = valuate_addons(self.hand, self.known, self.deck, self.opp_cards_qty, cards, table)
            if cards:
                self.hand = differ(self.hand, cards)
            return cards
        else:
            if self.limited_sequence[-1] == 'a':
                cards = []

                for i in range(self.stop + 1, len(self.super) - 1, 2):
                    if isinstance(self.super[i + 1], str) and self.super[i + 1] == 'a':
                        cards.append(self.super[i])
                    elif isinstance(self.super[i + 1], str) and self.super[i + 1] == 'f':
                        cards.append(self.super[i])
                        self.stop = self.super.index(self.super[i])
                        break
                    else:
                        break
                return cards

    def check_addons(self, addons):
        if self.known and addons:
            self.known = differ(self.known, addons)
        if self.deck and addons:
            self.deck = differ(self.deck, addons)
        if self.super:
            i = 0
            for item in addons:
                if item in self.super[self.stop:len(addons) * 2]:
                    i += 1
            if i != len(addons):
                self.super = None

    def defence(self, table):
        if len(table) == 1 and self.deck:
            self.deck = differ(self.deck, self.hand)
            self.known.remove(table[0]) if table[0] in self.known else self.deck.remove(table[0])
        # self.deck = differ(self.deck, self.hand)
        else:
            if len(self.known) == self.opp_cards_qty:
                self.known.remove(table[-1])
                self.opp_cards_qty -= 1
            else:
                self.known, self.deck, self.opp_cards_qty = match_cards(self.known, self.deck, table,
                                                                        self.opp_cards_qty, self.real_deck)
        # print(table, id(self.hand), self.hand, self.known, id(self.deck), self.deck, 'real', self.real_deck,
        #       self.opp_cards_qty)

        # Момент когда неизвестные карты становятся известными
        # if self.real_deck <= 1 and len(self.deck) > self.real_deck:
        #     if self.real_deck == 1 and self.opp_cards_qty - len(self.known) == len(self.deck[:-1]):
        #         self.known += self.deck[:-1]
        #         self.deck = list(self.deck[-1])
        #     if self.real_deck == 0 and self.opp_cards_qty - len(self.known) == len(self.deck):
        #         self.known += self.deck
        #         self.deck.clear()
        # Случай в котором мы знаем, что неизвестная часть колоды отправляется в одну руку
        # if 6 - len(self.known) >= len(self.deck[:-1]) and len(self.known) == self.opp_cards_qty:
        #     print('we got here')
        #     if not self.super:
        #         self.super = super_sequence(self.hand, self.known, self.trump, self.deck, table)
        #         self.limited_sequence, self.stop = super_follower(self.super, self.stop, self.hand, self.known)
        #         print(table)
        #         card = follower(self.limited_sequence, table)
        #         if isinstance(card, Card):
        #             return self.hand.pop(self.hand.index(card))
        #         elif isinstance(card, str):
        #             self.limited_sequence = []
        #             return 'take'
        #     else:
        #         if not self.limited_sequence:
        #             self.limited_sequence, self.stop = super_follower(self.super, self.stop, self.hand, self.known)
        #         if self.limited_sequence:
        #             card = follower(self.limited_sequence, table)
        #             if isinstance(card, Card):
        #                 return self.hand.pop(self.hand.index(card))
        #             elif isinstance(card, str):
        #                 self.limited_sequence = []
        #                 return 'take'
        #             elif isinstance(card, bool):
        #                 self.super = super_sequence(self.hand, self.known, self.trump, self.deck, table)
        #                 self.limited_sequence, self.stop = super_follower(self.super, self.stop, self.hand, self.known)
        #                 card = follower(self.limited_sequence, table)
        #                 if isinstance(card, Card):
        #                     return self.hand.pop(self.hand.index(card))
        #                 elif isinstance(card, str):
        #                     self.limited_sequence = []
        #                     return 'take'

        if self.limited_sequence:
            card = follower(self.limited_sequence, table)
            if isinstance(card, Card):
                return self.hand.pop(self.hand.index(card))
            elif isinstance(card, str):
                self.limited_sequence = []
                return 'take'

        sequences = imagine_sequences(self.hand, self.known, self.trump, table)
        self.limited_sequence = valuate(sequences, self.hand, self.known, self.deck, self.opp_cards_qty, len(table)-1,
                                        attack=False)
        print(self.limited_sequence)
        card = follower(self.limited_sequence, table)
        if isinstance(card, Card):
            return self.hand.pop(self.hand.index(card))
        else:
            self.limited_sequence = []
            return 'take'
