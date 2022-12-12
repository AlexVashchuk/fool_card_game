from logics.card import Card
from itertools import combinations

VALUES = [6, 7, 8, 9, 10, 11, 12, 13, 14]
SUITS = ['Spades', 'Clubs', 'Diamonds', 'Hearts']


# ################## game initialization helpers ####################

def trump_search(deck):
    """Истина если козырная карта есть в первых 12 картах"""
    for card in deck[:12]:
        if card.has_suit(deck[-1]):
            return True
    return False


def first_turn(player1, player2, trump):
    """Возвращает очередность ходов игроков"""
    a, b = player1.find_trump(trump), player2.find_trump(trump)
    if a and b:
        if b < a:
            return player2, player1
        else:
            return player1, player2
    if b:
        return player2, player1
    return player1, player2


def make_trumps(cards, trump):
    """Делает карты, которые должны стать козырными, козырными"""
    for card in cards:
        if card.has_suit(trump):
            card.value += 9
    return cards


# ################# game logics helpers #############################

def find_bigger(cards, hand, trump):
    """
    Возвращает несколько карт которыми можно отбить карту
    """
    if isinstance(cards, Card):
        cards = [cards]

    result = []
    for card in cards:
        for _card in hand:
            if (_card.has_suit(card) or _card.has_suit(
                    trump)) and _card.value > card.value:
                result.append([card, _card])
    return result


def card_bigger(card, other_card, trump):
    """Возвращает истину если карта может бить другую карту"""
    return (card.has_suit(other_card) or card.has_suit(
        trump)) and card.value > other_card.value


def find_to_add(hand, cards):
    """Возвращает карты которые можно подкинуть"""
    if isinstance(cards, Card):
        return [card for card in hand if card.same_value(cards)]

    result = []

    if not isinstance(cards[-1], Card):
        cards = cards[:-1]

    for _card in cards:
        result += [card for card in hand if card.same_value(_card) if
                   card not in result]
    return result


def filter_sequences(sequences):
    """Возвращает последовательности без продолжения и с продолжением"""
    finished = [seq for seq in sequences if not isinstance(seq[-1], Card)]
    to_be_continued = [seq for seq in sequences if isinstance(seq[-1], Card)]
    return finished, to_be_continued


def cut_collection(collection):
    """
    Выкидывает менее развитые последовательности. Т.е. тогда когда они короче
    и не закончены
    """
    length = [len(seq) for seq in collection]
    length = max(length)
    collection = [seq for seq in collection if
                  len(seq) == length or not isinstance(seq[-1], Card)]

    return collection


def clear_super_sequence(s):
    """
    Возвращает долгую последовательность только из элементов типа Card.
    """
    idx = [i for i in range(len(s)) if isinstance(s[i], str) and s[i] == 'f']
    if len(idx) > 1:
        s = [item for item in s[idx[-2] + 1:idx[-1]] if isinstance(item, Card)]
    else:
        s = [item for item in s if isinstance(item, Card)]
    return s


def differ_two_hands(hand, known, sequence):
    """Вычитает из рук карты последовательности"""
    s = clear_super_sequence(sequence)
    hand = differ(hand, s) if hand else []
    known = differ(known, s) if known else []
    return hand, known


def differ(a, b):
    """list: a - list: b"""
    _a = a[:-1] if type(a[-1]) != Card else a
    _b = b[:-1] if type(b[-1]) != Card else b
    cards = [item for item in _a if item not in _b]

    return cards


def change_queue(q):
    a, b = q
    a, b = b, a
    return a, b


def finish_sequences(collection):
    """
    Делает нейтральные строчные оконцовки к коротким последовательностям
    """
    for seq in collection:
        if type(seq[-1]) == Card:
            seq.append('0')
    return collection


def after_take(hand, known, seq):
    """возвращает комбинации карт которые можно добавить"""
    opp_qty = len(known) if isinstance(known, list) else known
    to_add_qty = opp_qty if len(seq) // 2 + opp_qty < 6 else 6 - (
            len(seq) // 2)
    cards = find_to_add(hand, seq)
    result = [[]]
    for i in range(1, to_add_qty + 1):
        result += list(combinations(cards, i))

    return [list(item) for item in result]


def last_sequence_takes(seq):
    """
    Проверка на то, что результатом предыдущей функции будет 'take'
    """
    i = 0
    for card in seq[-2::-1]:
        if isinstance(card, str) and len(seq[-(i + 1):-1]) % 2 == 0:
            return False, seq[-(i + 1):-1]
        if isinstance(card, str) and len(seq[-(i + 1):-1]) % 2 != 0:
            return True, seq[-(i + 1):-1]
        i += 1
    if len(seq[:-1]) % 2 == 0:
        return False, seq[:-1]

    return True, seq[:-1]


def match_cards(known, deck, table, opp_cards_qty):
    """
    Приводит память игрока (known, deck) в соответствие с положением
    на игровом столе
    """
    if table:

        opp_cards_qty -= 1

        if known and table[-1] in known:
            known.remove(table[-1])

        elif deck and table[-1] in deck:
            deck.remove(table[-1])

        else:
            raise ValueError(
                f'Last card {table[-1]} on the table must be in known nor in deck')

    return known, deck, opp_cards_qty


def deck2known(real_deck, known, deck):
    """
    Deck содержит в себе функции хранения неизвестных карт.
    Функция вычисляет карты, которые превращаются из неизвестных в известные
    """
    known = known + deck if real_deck == 0 else known + deck[:-1]
    if deck and known:
        deck = differ(deck, known)

    done = None if deck else 'done'

    return known, deck, done


def defence_wins(real_deck, hand, opp_qty):
    """
    Возвращает истину если защищающийся оппонент уже выиграл
    """
    if opp_qty == 0:
        if real_deck == 0 or len(hand) >= real_deck:
            return True
    return False


def attack_wins(real_deck, opp_qty):
    """
    Возвращает истину если атакующий оппонент уже выиграл
    """
    if opp_qty == 0 and real_deck == 0:
        return True
    return False


def enter2super(hand, known, opp_qty, deck, defence):
    """
    Проверяем можем ли мы переключиться в режим долгой последовательности
    """
    if not defence:
        if 6 - len(hand) >= len(deck[:-1]) and len(known) == opp_qty \
               and len(hand + known + deck) <= 12:
            return True
    else:
        if 6 - len(known) >= len(deck[:-1]) and len(known) == opp_qty \
               and len(hand + known + deck) <= 12:
            return True

    return False

##################### for front end ###########################33

def to_JSON(o):
    if isinstance(o, Card):
        return f""