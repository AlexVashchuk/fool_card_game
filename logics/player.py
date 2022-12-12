from logics.card import Card
from logics.helpers import after_take, differ, match_cards, deck2known, \
    defence_wins, attack_wins, enter2super
from logics.head import imagine_sequences, valuate, follower, valuate_addons, \
    super_sequence, super_follower, clear_super_sequence, Sequence, \
    make_sequence_objects


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

        # Когда карты равны. В короткой есть элемент 'а', а на столе 'take':
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
        if defence:
            check, response = attack_wins, 'take'
        if check:
            return response

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
