from logics.head import imagine_sequences, valuate, follower, valuate_addons, \
    super_sequence, super_follower, clear_super_sequence, Sequence, \
    make_sequence_objects
from logics.helpers import after_take, differ, match_cards, deck2known, \
    defence_wins, attack_wins, enter2super
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
        self.deck2known = None

    def find_trump(self, trump):
        """
        Ищем самый маленький козырь - сортируем все карты и находим первый
        """
        self.trump = trump
        self.hand.sort()
        for card in self.hand:
            if card.has_suit(trump):
                return card
        return False

    # def attack(self, table=None):
    #
    #     # Если стола нет, это значит игроки получили карты из колоды и эти
    #     # карты необходимо пересчитать.
    #     # Если есть стол. Удаляем последнюю карту стола из карт оппонента,
    #     # если она есть в известных, либо удаляем ее из мнимой колоды
    #
    #     if not table:
    #         self.limited_sequence = []
    #         self.deck = differ(self.deck, self.hand) \
    #             if self.deck else self.deck
    #
    #     self.known, self.deck, self.opp_cards_qty = match_cards(
    #         self.known, self.deck, table, self.opp_cards_qty)
    #
    #     if self.real_deck < 2 and not self.deck2known:
    #         self.known, self.deck, self.deck2known = deck2known(
    #             self.real_deck, self.known, self.deck
    #         )
    #     print()
    #     print(self.name)
    #     print('attack', 'super = ', self.super)
    #     print('table', table, self.hand, self.known, self.opp_cards_qty,
    #           self.deck, self.real_deck)
    #     if self.super:
    #         print(self.super.sequence, self.limited_sequence)
    #     else:
    #         print(self.limited_sequence)
    #
    #     if self.opp_cards_qty == 0:
    #         if self.real_deck == 0 or 6 - len(self.hand) >= self.real_deck:
    #             return 'discards'
    #
    #     # Случай в котором мы точно знаем,
    #     # что неизвестная часть колоды отправляется только в свою руку
    #     if 6 - len(self.hand) >= len(self.deck[:-1]) and \
    #             len(self.known) == self.opp_cards_qty:
    #
    #         if not self.super:
    #
    #             if not table:
    #                 table = []
    #             self.super = super_sequence(self.hand, self.known,
    #                                         self.trump, defence=False,
    #                                         deck=self.deck[:])  # table
    #
    #             self.limited_sequence, self.super = super_follower(
    #                 self.super, self.hand, self.known)
    #             card = follower(self.limited_sequence, table)
    #
    #             if isinstance(card, Card):
    #                 return self.hand.pop(self.hand.index(card))
    #             elif isinstance(card, str):
    #                 self.limited_sequence = []
    #                 return 'discards'
    #         else:
    #             if not self.limited_sequence:
    #                 self.limited_sequence, self.super = super_follower(
    #                     self.super, self.hand, self.known)
    #             if self.limited_sequence:
    #                 card = follower(self.limited_sequence, table)
    #                 if isinstance(card, Card):
    #                     return self.hand.pop(self.hand.index(card))
    #                 elif isinstance(card, str):
    #                     self.limited_sequence = []
    #                     return 'discards'
    #                 elif isinstance(card, bool):
    #                     # hand, known, trump, defence=False, deck=None, table=None
    #                     self.super = super_sequence(self.hand, self.known,
    #                                                 self.trump, defence=False,
    #                                                 deck=self.deck[:],
    #                                                 table=table)
    #                     self.limited_sequence, self.super = super_follower(
    #                         self.super, self.hand, self.known)
    #                     card = follower(self.limited_sequence, table)
    #                     if isinstance(card, Card):
    #                         return self.hand.pop(self.hand.index(card))
    #                     elif isinstance(card, str):
    #                         self.limited_sequence = []
    #                         return 'discards'
    #
    #     # Когда мы не перешли в конечную фазу игры
    #     if table and self.limited_sequence:
    #         card = follower(self.limited_sequence, table)
    #         if isinstance(card, Card):
    #             return self.hand.pop(self.hand.index(card))
    #         elif isinstance(card, str):
    #             self.limited_sequence = []
    #             return 'discards'
    #         # else:
    #         #     self.limited_sequence = []
    #
    #     if not table:
    #         table = []
    #
    #     # self.limited_sequence = []
    #     sequences = imagine_sequences(self.hand, self.known, self.trump, table)
    #     self.limited_sequence = valuate(sequences, self.hand, self.known,
    #                                     self.deck, self.opp_cards_qty,
    #                                     len(table))
    #     card = follower(self.limited_sequence, table)
    #
    #     if isinstance(card, Card):
    #         return self.hand.pop(self.hand.index(card))
    #     # if isinstance(card, str):
    #     else:
    #         self.limited_sequence = []
    #         return 'discards'
    #
    # def addons(self, table):
    #     cards = []
    #     # если режим супер и если режим обычный
    #     if not self.hand:
    #         return cards
    #
    #     if not self.super:
    #         print('addons')
    #         cards = after_take(self.hand, self.opp_cards_qty, table)
    #         cards = valuate_addons(self.hand, self.known, self.deck,
    #                                self.opp_cards_qty, cards, table)
    #         if cards:
    #             self.hand = differ(self.hand, cards)
    #         return cards
    #     else:
    #
    #         print()
    #         print(self.name)
    #         print('super addons')
    #         if not isinstance(self.super, str):
    #             print(self.super.sequence, self.limited_sequence)
    #         else:
    #             print(self.super, self.limited_sequence)
    #
    #         if isinstance(self.super, str):
    #             reverse_counter = 0
    #             table[-1] = '0'
    #             renewable, result = make_sequence_objects(
    #                 [table], self.hand, self.known, reverse_counter, self.deck
    #             )
    #             if renewable:
    #                 self.super = super_sequence(
    #                     '', '', self.trump, addons=(renewable, result)
    #                 )
    #
    #         begin = 0
    #         for i in self.super.sequence:
    #             begin += 1
    #             if isinstance(i, str) and i == 'a':
    #                 break
    #
    #         stop = 0
    #         for i in self.super.sequence:
    #             stop += 1
    #             if isinstance(i, str) and i == 'f':
    #                 break
    #
    #         if begin and begin < stop:
    #             cards = clear_super_sequence(
    #                 self.super.sequence[begin:stop])
    #         if stop < len(self.super.sequence):
    #             self.super.sequence = self.super.sequence[stop:]
    #     print('cards', cards, 'super', self.super.sequence)
    #     return cards
    #
    # def check_addons(self, table, addons):
    #     print('check addons')
    #     if self.known and addons:
    #         self.known = differ(self.known, addons)
    #     if self.deck and addons:
    #         self.deck = differ(self.deck, addons)
    #
    #     if self.super:
    #         begin = len(table) - 1
    #         if begin < len(self.limited_sequence):
    #             if isinstance(table[begin], str) and isinstance(
    #                     self.limited_sequence[begin], str):
    #                 if self.limited_sequence[begin] == 'a':
    #                     cards = [card for card in self.limited_sequence[begin:]
    #                              if isinstance(card, Card)]
    #                     addons.sort(), cards.sort()
    #                     if addons == cards:
    #                         self.limited_sequence = []
    #                     else:
    #                         self.super, self.limited_sequence = None, []
    #                 else:
    #                     self.super, self.limited_sequence = None, []
    #             else:
    #                 self.super, self.limited_sequence = None, []
    #         else:
    #             self.super, self.limited_sequence = None, []
    #
    #         # if isinstance(self.limited_sequence[begin], str) \
    #         #         and self.limited_sequence[begin] == 'a':
    #         #
    #         #     begin = table.index(table[-1]) + 1
    #         #     cards = [card for card in self.limited_sequence[begin:]
    #         #              if isinstance(card, Card)]
    #         #     addons.sort(), cards.sort()
    #         #     if addons == cards:
    #         #         self.limited_sequence = []
    #         #     else:
    #         #         self.super = None
    #
    # def defence(self, table):
    #
    #     if len(table) == 1:
    #         self.limited_sequence = []
    #         if self.deck:
    #             self.deck = differ(self.deck, self.hand)
    #
    #     self.known, self.deck, self.opp_cards_qty = match_cards(
    #         self.known, self.deck, table, self.opp_cards_qty)
    #
    #     if self.real_deck < 2 and not self.deck2known:
    #         self.known, self.deck, self.deck2known = deck2known(
    #             self.real_deck, self.known, self.deck
    #         )
    #
    #     print()
    #     print(self.name)
    #     print('defence', 'super = ', self.super)
    #     print('table', table, self.hand, self.known, self.opp_cards_qty,
    #           self.deck, self.real_deck)
    #     if self.super:
    #         print(self.super.sequence, self.limited_sequence)
    #     else:
    #         print(self.limited_sequence)
    #
    #     if self.opp_cards_qty == 0 and self.real_deck == 0:
    #         return 'take'
    #
    #     # if len(table) == 1 and self.deck:
    #     #     self.deck = differ(self.deck, self.hand)
    #     #     self.known.remove(table[0]) if table[0] in self.known \
    #     #         else self.deck.remove(table[0])
    #     # # self.deck = differ(self.deck, self.hand)
    #     # else:
    #     #     if len(self.known) == self.opp_cards_qty:
    #     #         self.known.remove(table[-1])
    #     #         self.opp_cards_qty -= 1
    #     #     else:
    #     #         self.known, self.deck, self.opp_cards_qty = match_cards(
    #     #             self.known, self.deck, table,
    #     #             self.opp_cards_qty, self.real_deck)
    #
    #     # Момент когда неизвестные карты становятся известными
    #     # if self.real_deck <= 1 and len(self.deck) > self.real_deck:
    #     #     if self.real_deck == 1 and self.opp_cards_qty - len(self.known) \
    #     #             == len(self.deck[:-1]):
    #     #         self.known += self.deck[:-1]
    #     #         self.deck = [self.deck[-1]]
    #     #     if self.real_deck == 0 and self.opp_cards_qty - len(self.known) \
    #     #             == len(self.deck):
    #     #         self.known += self.deck
    #     #         self.deck.clear()
    #
    #     # Случай в котором мы знаем, что неизвестная часть
    #     # колоды отправляется в одну руку
    #     if 6 - len(self.known) >= len(self.deck[:-1]) and len(self.known) \
    #             == self.opp_cards_qty:
    #
    #         if not self.super:
    #             self.super = super_sequence(self.hand, self.known, self.trump,
    #                                         defence=True, deck=self.deck[:],
    #                                         table=table)
    #             self.limited_sequence, self.super = super_follower(self.super,
    #                                                                self.hand,
    #                                                                self.known)
    #             card = follower(self.limited_sequence, table)
    #             if isinstance(card, Card):
    #                 return self.hand.pop(self.hand.index(card))
    #             elif isinstance(card, str):
    #                 self.limited_sequence = []
    #                 return 'take'
    #         else:
    #             if not self.limited_sequence:
    #                 self.limited_sequence, self.super = super_follower(
    #                     self.super, self.hand, self.known)
    #             if self.limited_sequence:
    #                 card = follower(self.limited_sequence, table)
    #                 if isinstance(card, Card):
    #                     return self.hand.pop(self.hand.index(card))
    #                 elif isinstance(card, str):
    #                     self.limited_sequence = []
    #                     return 'take'
    #                 elif isinstance(card, bool):
    #                     self.super = super_sequence(self.hand, self.known,
    #                                                 self.trump, defence=True,
    #                                                 deck=self.deck[:],
    #                                                 table=table)
    #                     self.limited_sequence, self.super = super_follower(
    #                         self.super, self.hand, self.known)
    #                     card = follower(self.limited_sequence, table)
    #                     if isinstance(card, Card):
    #                         return self.hand.pop(self.hand.index(card))
    #                     elif isinstance(card, str):
    #                         self.limited_sequence = []
    #                         return 'take'
    #
    #     if self.limited_sequence:
    #         card = follower(self.limited_sequence, table)
    #         if isinstance(card, Card):
    #             return self.hand.pop(self.hand.index(card))
    #         elif isinstance(card, str):
    #             self.limited_sequence = []
    #             return 'take'
    #
    #     sequences = imagine_sequences(self.hand, self.known, self.trump, table)
    #     self.limited_sequence = valuate(sequences, self.hand, self.known,
    #                                     self.deck, self.opp_cards_qty,
    #                                     len(table) - 1, attack=False)
    #
    #     card = follower(self.limited_sequence, table)
    #     if isinstance(card, Card):
    #         return self.hand.pop(self.hand.index(card))
    #     else:
    #         self.limited_sequence = []
    #         return 'take'
    #
    # def behavior_check(self, table):
    #     # На случай когда мы не в режиме super
    #     if not self.super or isinstance(self.super, str):
    #         self.super = None
    #         return None
    #
    #     if self.limited_sequence and table:
    #         if len(table) <= len(self.limited_sequence):
    #             a = [card for card in table[:-1] if isinstance(card, Card)]
    #             b = [card for card in self.limited_sequence[:len(table) - 1]
    #                  if isinstance(card, Card)]
    #             if a == b:
    #                 if isinstance(table[-1], str) and isinstance(
    #                         self.limited_sequence[len(table) - 1], str):
    #                     return None
    #
    #     if table[-1] == 'take':
    #         self.super, self.limited_sequence = 'addons', []
    #     if table[-1] == 'discards':
    #         self.super, self.limited_sequence = None, []

    # #################
    # def attack(self, table):
    #     # Первый ход в кругу мы получили карты из колоды
    #     # Необходимо привести в порядок мнимую колоду
    #     print('ATTACK')
    #     match_known = self.known[:]
    #     match_deck = self.deck[:]
    #     if not table:
    #         self.deck = differ(self.deck,
    #                            self.hand) if self.deck else self.deck
    #
    #     # Приведение карт на столе, в руках и в мнимой колоде в порядок
    #     print('MATCH', id(table), table, self.known, self.deck)
    #     self.known, self.deck, self.opp_cards_qty = match_cards(
    #         self.known, self.deck, table, self.opp_cards_qty
    #     )
    #
    #     # Ловим момент, в котором мы можем вычислить, у кого в руках какие карты
    #     if self.real_deck < 2 and not self.deck2known:
    #         self.known, self.deck, self.deck2known = deck2known(
    #             self.real_deck, self.known, self.deck
    #         )
    #
    #     # Проверяем оппонента на предмет, если он выиграл:
    #     # Например, у него кончились карты и он точно не получит новых
    #     if self.opp_cards_qty == 0:
    #         if self.real_deck == 0 or 6 - len(self.hand) >= self.real_deck:
    #             return 'discards'
    #
    #     # Случай, в котором мы точно знаем, что неизвестная часть колоды
    #     # отправляется только в свою руку. В этом случае мы можем уходить
    #     # в режим супер-последовательности
    #     if 6 - len(self.hand) >= len(self.deck[:-1]) and \
    #             len(self.known) == self.opp_cards_qty and \
    #             len(self.hand + self.known + self.deck) <= 12:
    #
    #         # Начинаем новую последовательность или начинаем заново
    #         if self.super is None:
    #             self.limited_sequence = []
    #             self.super = super_sequence(
    #                 self.hand, self.known, self.trump,
    #                 defence=False, deck=self.deck[:], table=table
    #             )
    #             print(self.super, isinstance(self.super, Sequence))
    #
    #         # Финишная часть супер-последовательности.
    #         if self.super is str:
    #             if not self.limited_sequence:
    #                 self.super = super_sequence(
    #                     self.hand, self.known, self.trump,
    #                     defence=False, deck=self.deck[:], table=table
    #                 )
    #
    #         if isinstance(self.super, Sequence):
    #             if not self.limited_sequence:
    #                 self.limited_sequence, self.super = super_follower(
    #                     self.super, self.hand, self.known
    #                 )
    #     else:
    #         if not self.limited_sequence:
    #             sequences = imagine_sequences(
    #                 self.hand, self.known, self.trump, table
    #             )
    #             self.limited_sequence = valuate(
    #                 sequences, self.hand, self.known, self.deck,
    #                 self.opp_cards_qty, len(table)
    #             )
    #     print('******************************************************')
    #     if isinstance(self.super, Sequence):
    #         print('l-s', self.limited_sequence, 'super', self.super.sequence)
    #     else:
    #         print('!!!!! l-s', self.limited_sequence, 'super', self.super)
    #
    #     card = follower(self.limited_sequence, table)
    #     print(card)
    #     if not card and isinstance(self.super, Sequence):
    #         self.super, self.limited_sequence = None, []
    #         self.known, self.deck = match_known[:], match_deck[:]
    #         card = self.attack(table)
    #
    #     print()
    #     print('attack', self.name, self.hand)
    #     print('opponent', self.known, self.opp_cards_qty)
    #     print('deck', self.deck, self.real_deck)
    #     print('table', table)
    #     if isinstance(self.super, Sequence):
    #         print('l-s', self.limited_sequence, 'super', self.super.sequence)
    #     else:
    #         print('l-s', self.limited_sequence, 'super', self.super)
    #     if isinstance(card, Card):
    #         return self.hand.pop(self.hand.index(card))
    #     else:
    #         self.limited_sequence = []
    #         return 'discards'

    # def defence(self, table):
    #     print('DEFENCE')
    #     match_known = self.known[:]
    #     match_deck = self.deck[:]
    #     # Получив карты из колоды приводим в порядок мнимую колоду
    #     if len(table) == 1:
    #         self.deck = differ(self.deck,
    #                            self.hand) if self.deck else self.deck
    #
    #     # Приведение карт на столе, в руках и в мнимой колоде в порядок
    #     print('MATCH', table, self.known, self.deck)
    #     self.known, self.deck, self.opp_cards_qty = match_cards(
    #         self.known, self.deck, table, self.opp_cards_qty
    #     )
    #
    #     # Ловим момент, в котором мы можем вычислить, у кого в руках какие карты
    #     if self.real_deck < 2 and not self.deck2known:
    #         self.known, self.deck, self.deck2known = deck2known(
    #             self.real_deck, self.known, self.deck
    #         )
    #
    #     # Проверка оппонента на выигрыш
    #     if self.opp_cards_qty == 0 and self.real_deck == 0:
    #         return 'take'
    #
    #     # Случай, в котором мы точно знаем, что неизвестная часть колоды,
    #     # отправляется только в свою руку. В этом случае мы можем уходить
    #     # в режим супер-последовательности
    #     if 6 - len(self.known) >= len(self.deck[:-1]) and len(self.known) \
    #             == self.opp_cards_qty and len(
    #         self.hand + self.known + self.deck) <= 12:
    #
    #         if self.super is None:
    #             self.limited_sequence = []
    #             self.super = super_sequence(
    #                 self.hand, self.known, self.trump,
    #                 defence=True, deck=self.deck[:], table=table
    #             )
    #
    #         # Финишная часть супер-последовательности.
    #         if self.super is str:
    #             if not self.limited_sequence:
    #                 self.super = super_sequence(
    #                     self.hand, self.known, self.trump,
    #                     defence=True, deck=self.deck[:], table=table
    #                 )
    #
    #         if isinstance(self.super, Sequence):
    #             if not self.limited_sequence:
    #                 self.limited_sequence, self.super = super_follower(
    #                     self.super, self.hand, self.known
    #                 )
    #
    #     else:
    #         if not self.limited_sequence:
    #             sequences = imagine_sequences(
    #                 self.hand, self.known, self.trump, table
    #             )
    #             self.limited_sequence = valuate(
    #                 sequences, self.hand, self.known, self.deck,
    #                 self.opp_cards_qty, len(table)
    #             )
    #
    #     card = follower(self.limited_sequence, table)
    #     if not card and isinstance(self.super, Sequence):
    #         self.super, self.limited_sequence = None, []
    #         self.known, self.deck = match_known[:], match_deck[:]
    #         card = self.defence(table)
    #
    #     print()
    #     print('defence', self.name, self.hand)
    #     print('opponent', self.known, self.opp_cards_qty)
    #     print('deck', self.deck, self.real_deck)
    #     print('table', table)
    #     if isinstance(self.super, Sequence):
    #         print('l-s', self.limited_sequence, 'super', self.super.sequence)
    #     else:
    #         print('l-s', self.limited_sequence, 'super', self.super)
    #     if isinstance(card, Card):
    #         return self.hand.pop(self.hand.index(card))
    #     else:
    #         self.limited_sequence = []
    #         return 'take'

    def addons(self, table, first_try_done=False):
        """
        Добавление карт в случае, когда оппонент не смог отбить
        """
        cards = []
        if not self.hand:
            self.limited_sequence = []
            return cards

        elif isinstance(self.super, Sequence) \
                and not self.limited_sequence and not first_try_done:
            self.limited_sequence = []
            return cards

        # Мы не перешли в режим длинной последовательности
        if self.super is None:
            cards = after_take(self.hand, self.opp_cards_qty, table)
            cards = valuate_addons(
                self.hand, self.known, self.deck, self.opp_cards_qty, cards,
                table
            )

        # Игра уже находится в режиме длинной последовательности, но оппонент
        # перестал отбиваться раньше чем планировалось, поэтому здесь мы
        # начинаем генерировать объекты длинных последовательностей по новой
        if isinstance(self.super, str):

            if not self.limited_sequence:
                reverse_counter = 0
                if isinstance(table[-1], Card):
                    table.append('take')
                renewable, result = make_sequence_objects(
                    [table], self.hand, self.known, reverse_counter,
                    deck=self.deck[:]
                )

                self.super = super_sequence(
                    'blind', 'cap', self.trump, addons=(renewable, result)
                )

                self.limited_sequence, self.super = super_follower(
                    self.super, self.hand, self.known
                )

        # вычисляем то, что нужно добавить к картам, котороые оппонент забрал
        start, end, counter = 0, 0, 0
        for item in self.limited_sequence:
            if isinstance(item, str):
                if item == 'a' and start < 1:
                    start = counter
                if item == 'f' and end < 1:
                    end = counter
                    break
            counter += 1

        # если карты нашлись, проверяем что они есть в руке
        if end > start != 0:
            cards = clear_super_sequence(self.limited_sequence[start:end])
            not_in_hand = [card for card in cards if card not in self.hand]
            if cards and not_in_hand:
                if not first_try_done:
                    table = table[:-1]
                    self.super, self.limited_sequence = 'try again', []
                    cards = self.addons(table, first_try_done=True)
                else:
                    cards = []

        # Если есть карты, чтобы отдать - убираем их из руки.
        # Обнуляем короткую последоательность. Возвращаем карты.
        if cards:
            self.hand = differ(self.hand, cards)
        self.limited_sequence = []

        return cards

    def check_addons(self, addons):
        """
        Функция принимает дополнительные карты, если оппонент их дал.
        Сверяет, было ли такое запланировано
        """
        if self.known and addons:
            self.known = differ(self.known, addons)
        if self.deck and addons:
            self.deck = differ(self.deck, addons)

        if clear_super_sequence(self.limited_sequence) != addons:
            self.super, self.limited_sequence = None, []
        else:
            self.limited_sequence = []

    def behavior_check(self, table):
        """
        Функция сверяет действие оппонента с собственным планом в контексте
        вышел ли игрок из цепочки раньше времени.
        """
        # Когда нет длинной последовательности, ничего не проверяем.
        # Только обнуляем короткую последовательность
        if self.super is None:
            self.limited_sequence = []
            return None

        # Достаем карты из короткой последовательности для сравнения с картами
        # на столе
        check = clear_super_sequence(self.limited_sequence[:len(table) - 1])
        check_point = self.limited_sequence[len(table) - 1]

        # Когда карты равны. В короткой есть элемент 'a', а на столе 'take':
        # Игра направит делать addons, в этом случае ничего делать не нужно
        # Если стол и короткая последовательности заканчиваются чем-то еще:
        # Обнуляем короткую.
        if check == table[:-1]:
            if isinstance(check_point, str):
                if check_point == 'a' and table[-1] == 'take':
                    return None
                if isinstance(check_point, str) and isinstance(table[-1], str):
                    self.limited_sequence = []
                    return None
        # Случай, когда карты не совпали значит, что противник закончил играть
        # раньше запланированного маркируем длинную и короткую для
        # правильной обработки в addons (случай take). Либо для формирования
        # новой длинной последовательности
        if isinstance(table[-1], str):
            if table[-1] == 'take':
                self.super, self.limited_sequence = 'addons', []
            if table[-1] == 'discards':
                self.super, self.limited_sequence = None, []

    def make_turn(self, table, defence=False):
        """
        Функция кладет карту на стол в соответвии с планом либо его отсутствием.
        """
        # Инициализируем данные для проверки, если вдруг у оппонента нет карт
        check, response = defence_wins, 'discards'
        args = self.real_deck, self.hand, self.opp_cards_qty
        if defence:
            check, response = attack_wins, 'take'
            args = self.real_deck, self.opp_cards_qty

        # если начало розыгрыша, удаляем карты в руках из мнимой колоды
        if not table and not defence:
            self.deck = differ(self.deck,
                               self.hand) if self.deck else self.deck
        if len(table) == 1 and defence:
            self.deck = differ(self.deck,
                               self.hand) if self.deck else self.deck

        # Проверяем, что игра развивается по плану
        card = None
        if self.limited_sequence:
            card = follower(self.limited_sequence, table)
        if not card:
            self.super, self.limited_sequence = None, []

        # Удаляем то, что на столе из известных нам карт и из неизвестных
        self.known, self.deck, self.opp_cards_qty = match_cards(
            self.known, self.deck, table, self.opp_cards_qty)

        # Мы можем сделать неизвестными карты известными
        if not self.deck2known and self.real_deck < 2:
            self.known, self.deck, self.deck2known = deck2known(
                self.real_deck, self.known, self.deck
            )

        # Проверка оппонента на выигрыш
        if check(*args):
            return response

        # Точка входа в режим долгой последовательности
        if enter2super(
                self.hand, self.known, self.opp_cards_qty, self.deck, defence):

            if not self.super:
                self.limited_sequence = []
                self.super = super_sequence(
                    self.hand, self.known, self.trump,
                    defence=defence, deck=self.deck[:], table=table
                )

            if isinstance(self.super, Sequence):
                if not self.limited_sequence:
                    self.limited_sequence, self.super = super_follower(
                        self.super, self.hand, self.known
                    )
                card = follower(self.limited_sequence, table)

        # Точка входа в режим короткой последовательности
        else:
            if not self.limited_sequence:
                sequences = imagine_sequences(
                    self.hand, self.known, self.trump, table)

                self.limited_sequence = valuate(
                    sequences, self.hand, self.known, self.deck,
                    self.opp_cards_qty, len(table))

                card = follower(self.limited_sequence, table)

        # Возвращаем карту или действие (discards / take)
        if isinstance(card, Card):
            return self.hand.pop(self.hand.index(card))

        else:
            self.limited_sequence = []
            return response
