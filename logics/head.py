from functools import reduce
from logics.helpers import Card, filter_sequences, find_bigger, \
    find_to_add, differ, cut_collection, finish_sequences, differ_two_hands, \
    last_sequence_takes, after_take, clear_super_sequence


class Sequence:
    """
    Объект класса при создании схраняет последнее положение в игре после
    выполнения последней цепочки ходов. Цепочки достраиваются до достижения
    нулевого результата (hand или known = пустой)
    """
    def __init__(self, hand, known, sequence, reverse, deck=None):
        self.hand = hand
        self.known = known
        self.deck = deck if deck else []
        self.sequence = sequence
        self.reverse_counter = reverse
        self.is_winning = None


def need_reverse(sequence):
    """
    Определяет нужно ли менять местами hand и known, что бы планировать
    как оппонент будет ходить ко мне.
    """
    if len(sequence) % 2 == 0:
        return False
    return True


def is_winning(s_seq, defence=False):
    """
    Функция определяет чья рука в конечном счете осталась с картами, на основе
    количества разворотов при построении цепочки до нулевого результата
    """
    if defence:
        s_seq.hand, s_seq.known = s_seq.known, s_seq.hand
        s_seq.reverse_counter += 1

    if s_seq.hand and not s_seq.known:
        if s_seq.reverse_counter % 2 != 0:
            return True

    elif s_seq.known and not s_seq.hand:
        if s_seq.reverse_counter % 2 == 0:
            return True

    if not s_seq.hand and not s_seq.known:
        cards_between, counter = 0, 0
        _reverse = s_seq.reverse_counter
        for item in s_seq.sequence[::-1]:
            if isinstance(item, str):
                counter += 1
            cards_between += 1
            if counter == 2:
                break
        if counter < 2:
            cards_between -= 1
        if cards_between % 2 == 0:
            _reverse += 1

        if not defence and _reverse % 2 == 0:
            return True
        elif defence and _reverse % 2 != 0:
            return True

    return False


def make_choice(s_sequences, defence=False):
    """
    Делает выбор среди воображаемых вариантов, который пойдет в конечном счете
    в реальную игру.
    Делаем группы по начальным картам.

    Ищем:
    1. Группы, которые выигрывают во всех случаях
    2. Группы, которые выигрывают в некоторых случаях:
        а. Проигранные случаи являются ошибкой игрока
        б. Проигранные случаи являются волевым решением оппонента
    3. Группы, которые проигрывают во всех случаях

    Выбираем лучшие варианты (1, 2а). Если их нет, тогда смотрим 2б.
    Если их нет смотрим 3 (там где больше разворотов).
    """
    stumps = []
    trees = {}
    black_trees = []
    gray_trees = []
    remain = []

    # группируем все имеющиеся последовательности по начальной карте
    for item in s_sequences:
        if item.sequence[0] not in stumps:
            stumps.append(item.sequence[0])
        trees[item] = stumps.index(item.sequence[0])

    # смотрим каждое дерево на вероятность победы
    for i in stumps:
        wins = 0
        tree = [k for k, v in trees.items() if v == stumps.index(i)]

        for branch in tree:
            if not is_winning(branch, defence):
                wins += 1

        if wins == len(tree):
            # выдаем любую последовательность из списка, например первую
            return tree[0]
        elif wins == 0:
            # оставим на потом, если ничего лучшего не будет
            black_trees.append(tree)
        else:
            # деревья с которыми можно как проиграть, так и выиграть
            gray_trees.append(tree)

    if gray_trees:

        # находим ту, которая выигрывает
        for branch in gray_trees:
            # вытаскиваем выигрышные и не выигрышные
            bad = [item for item in branch if not item.is_winning]
            wins = [[item, bad] for item in branch if item.is_winning]

            # для каждой выигрышной крутим цикл
            for w in wins:

                i = 1
                while i < len(w[0].sequence):
                    # если все плохие ветки отсеялись и осталась
                    # только хорошая ее и возвращаем
                    if len(w) == 1:
                        return w[0]

                    bean = []
                    for b in w[1]:
                        # Если наша плохая последовательность в позиции i все еще хороша,
                        # тогда мы добавим ее в корзину для следующих итераций,
                        # а если нет мы проверим кто инициатор ветки. Если это оппонент, выкидываем всю ветку.
                        if (isinstance(w[0].sequence[i], Card) and isinstance(b.sequence[i], Card)) \
                                or (isinstance(w[0].sequence[i], str) and isinstance(b.sequence[i], str)):
                            if len(b.sequence) > i:
                                if w[0].sequence[i] == b.sequence[i]:
                                    bean.append(b)
                                else:
                                    # убиваем ветку целиком, если проигрыш под контролем оппонента
                                    if not zone_control(b.sequence[:i], defence):
                                        remain.append(Sequence(w[0].hand, w[0].known,
                                                               w[0].sequence, w[0].reverse_counter))
                                        # remain[-1].reverse_counter = w[0].reverse_counter
                                        remain[-1].is_winning = w[0].is_winning
                                        w[0].sequence = []
                                        break
                        else:
                            # убиваем ветку целиком, если проигрыш под контролем оппонента
                            if not zone_control(b.sequence[:i], defence):
                                remain.append(Sequence(w[0].hand, w[0].known, w[0].sequence, w[0].reverse_counter))
                                # remain[-1].reverse_counter = w[0].reverse_counter
                                remain[-1].is_winning = w[0].is_winning
                                w[0].sequence = []
                                break
                    w[1] = bean if bean else w[1]
                    i += 1

    # если, что то осталось от того что может выиграть смотрим  в этих остатках
    if remain:
        result = remain[0]
        for item in remain:
            if item.reverse_counter > result.reverse_counter:
                result = item

        return result

    # если даже остатков не было смотрим в проигрышных вариантах и пробуем найти где побольше разворотов
    if black_trees:
        broom = []
        for item in black_trees:
            broom += item
        result = broom[0]
        for item in broom:
            if item.reverse_counter > result.reverse_counter:
                result = item
        return result


def super_sequence(
        hand, known, trump, defence=False, deck=None, table=None, addons=None):

    """
    Соединяем короткие цепочки в длинные и создаем из них законченные объекты,
    которые будут группироваться и оцениваться

    param: addons необходим, в случае, функция вызвана во время подкидывания
    дополнительны карт: Player.addons
    """
    result = []
    if not addons:

        # Создаем колоду и малую последовательность. После этого создаем объект
        # Sequence и если он не законченный, отправляем его в сито
        deck = deck if deck else []
        sub_result = imagine_sequences(hand, known, trump) if not \
            table else imagine_sequences(hand, known, trump, table[:])
        reverse = 0
        if defence:
            hand, known = known, hand
            reverse = -1
        renewable, _result = make_sequence_objects(sub_result, hand, known,
                                                   reverse, deck=deck,
                                                   defence=defence)

        result += _result
        sieve = renewable[:]
    else:
        sieve = addons[0]
        result = addons[1]

    while sieve:
        # Достраиваем наши Sequences объекты до достижения конечного результата
        renewable = []
        for sieve_item in sieve:
            sub_result = imagine_sequences(sieve_item.hand,
                                           sieve_item.known, trump)

            renewable, _result = make_sequence_objects(
                sub_result, sieve_item.hand, sieve_item.known,
                sieve_item.reverse_counter, sieve_item.sequence,
                sieve_item.deck, defence=defence)
            result += _result

        sieve = renewable

        if len(sieve) > 150:
            break

    return make_choice(result, defence)


def continue_sequence(hand, known, trump, collection=None):
    """
    Строим малые последовательности исходя из того, что мы знаем. Т.е. если
    мы знаем только свои карты и у нас стол еще чисты, тогда набор
    последовательностей будет состоять из каждой первой карты (в случае атаки)

    В случае, когда на столе что-то есть делаем прибавляем пару к карте:
    что можно добавить или чем можно побить.
    """
    new = []
    # start sequencing in attack mode
    # Если нет коллекции или стола начинаем новую коллекцию, каждая карта в руке станет началом коллекции
    if not collection:
        collection = [[card] for card in hand]

        # если мы не знаем карт оппонента завершаем коллекцию
        if not known:
            return finish_sequences(collection)
        # если мы знаем карты оппонента
        else:
            cards = [card for card in hand]
            bite = find_bigger(cards, known, trump)

            if bite:
                _cards = []
                for item in bite:
                    new.append(item)
                    _cards.append(item[0])
                _cards = differ(cards, _cards)

                if _cards:
                    for card in _cards:
                        new.append([card, '0'])
            else:
                for card in cards:
                    new.append([card, '0'])

        return cut_collection(collection + new)

    # sequences in attack mode
    if len(collection[0]) % 2 == 0 and type(collection[0][-1]) == Card:

        for sequence in collection:
            # if len(sequence) % 2 == 0 and type(sequence[-1]) == Card:
            if type(sequence[-1]) == Card:
                cards = find_to_add(hand, sequence)
                cards = differ(cards, sequence) if cards else []

                if not cards:
                    new.append(sequence.copy())
                    new[-1] += ['0']

                if cards and not known:
                    for card in cards:
                        new.append(sequence.copy())
                        new[-1] += [card, '0']

                if cards and known:
                    # known = differ(known, sequence)
                    bite = find_bigger(cards, known, trump)
                    _cards = [item[0] for item in bite if item[1] in sequence and item[0] not in sequence]
                    bite = [item for item in bite if item[1] not in sequence]
                    if not bite:
                        for card in cards:
                            new.append(sequence.copy())
                            new[-1] += [card, '0']

                    if bite:
                        _cards = []
                        _ = [item[0] for item in bite]
                        _cards += differ(cards, _) if cards and bite else []
                        for item in bite:
                            new.append(sequence.copy())
                            new[-1] += item
                            if item[0] in _cards:
                                _cards.remove(item[0])

                        if _cards:
                            for card in _cards:
                                new.append(sequence.copy())
                                new[-1] += [card, '0']

        return cut_collection(collection + new)

    # in defence mode
    if len(collection[0]) % 2 != 0 and type(collection[0][-1]) == Card:

        for sequence in collection:

            if type(sequence[-1]) == Card:
                bite = find_bigger(sequence[-1], hand, trump)
                bite = [item for item in bite if item[1] not in sequence]
                if bite:
                    for item in bite:
                        new.append(sequence.copy())
                        new[-1].append(item[1])
                        to_add = differ(known, new[-1]) if known else []
                        to_add = find_to_add(to_add, new[-1]) if to_add else []

                        if not to_add or len(sequence) == 11:
                            new[-1].append('0')

                        else:
                            _new = []
                            for card in to_add:
                                _new.append(new[-1].copy())
                                _new[-1].append(card)
                            new += _new
                else:
                    new.append(sequence.copy())
                    new[-1].append('0')

        return cut_collection(collection + new)


def seq_compose(func):
    """
    Здесь мы многократно прокручиваем логику continue_sequence, что бы
    наплодить все возможные варианты развития игры
    """
    def wrapper(*args):

        sub_result = []
        if len(args) == 4:
            # if not isinstance(args[3][0], list):
            if not isinstance(args[3], list):
                sub_result = [args[3]]
            else:
                sub_result = args[3]

        result = []
        closed_sequences = []

        i = 0
        while i < 12:

            sub_result = func(*args[:3], sub_result)
            _closed, sub_result = filter_sequences(sub_result)
            closed_sequences += _closed

            if not sub_result:
                result += closed_sequences
                return result
            else:
                i = len(sub_result[0])
                if i == 12:
                    closed_sequences += finish_sequences(sub_result)

        result = sub_result + closed_sequences
        return result

    return wrapper


@seq_compose
def imagine_sequences(hand, known, trump, collection=None):
    """
    Обертка для continue sequence
    """
    if not collection:
        return continue_sequence(hand, known, trump)

    else:
        if type(collection[0]) == Card:
            collection = [collection]

        return continue_sequence(hand, known, trump, collection)


def sum_cards(cards):
    """ Посчитываем сумму значений в наборе карт"""
    cards = [card.value for card in cards]
    return reduce(lambda x, y: x + y, cards)


# разложение вариантов карт по рукам
def decompose(hand, known, other_qty, deck):
    """
    Разворачиваем положение и наличие карт в игре для возможности выбора
    наилучшего варианта.
    """
    _unknown = []
    _deck = deck.copy()
    _hand = hand.copy()
    _known = known.copy()
    len_unknown = other_qty - len(known)
    if len_unknown > 0:
        _unknown = deck[-len_unknown:]
    if _unknown:
        _deck = differ(_deck, _unknown)
    return _hand, _known, _unknown, _deck


def give_cards(hand, deck, side=0):
    """
    Т.к. частью идеи выбора стратегии в игре является способ min-max, то эта
    реализация раздачи карт раздает карты в мнимые руки с разных сторон.
    Мы предполагаем что нам достанутся карты плохие, а противнику хорошие
    """
    cards_in_hand = len(hand)
    if side == 0:
        if cards_in_hand < 6:
            for i in range(6 - cards_in_hand):
                if deck:
                    hand.append(deck.pop(side))
                else:
                    break
    else:
        if cards_in_hand < 6:
            for i in range(6 - cards_in_hand):
                if len(deck) >= 2:
                    hand.append(deck.pop(-2))
                elif len(deck) == 1:
                    hand.append(deck.pop(0))
                else:
                    break
    return hand, deck


def amount(hand, other_cards, deck, sequence=None):
    # if not sequence:
    #     sequence = []
    # if sequence and not isinstance(sequence[-1], Card):
    #     sequence = sequence[:-1]
    #
    # # if not other_cards:
    # #     return -5
    """
    Считаем удельную стоимость руки
    """
    hand_amount = sum_cards(hand) if hand else 0
    other_amount = sum_cards(other_cards) if other_cards else 0
    deck_amount = sum_cards(deck) if deck else 0
    deck_with_others = deck_amount + other_amount
    hand_len = len(hand)
    hand_specific_amount = (hand_amount / deck_with_others / hand_len) / -1 \
        if deck_with_others != 0 and hand_len != 0 else 0

    return hand_specific_amount


def discards(hand, known, unknown, deck, sequence, defence=False):
    """
    Посчитываем результат при принятии решения на отбой. Т.е. нужно ли
    продолжать следовать цепочке по всей длине, или выгодно выйти раньше
    """
    hand = differ(hand, sequence)
    known_len = len(known)
    if known:
        known = differ(known, sequence)
    if len(known) == known_len and unknown:
        unknown.pop(0)
    other_cards = known + unknown

    if not defence:
        hand, deck = give_cards(hand, deck)
        other_cards, deck = give_cards(other_cards, deck, side=-1)
    else:
        other_cards, deck = give_cards(other_cards, deck, side=-1)
        hand, deck = give_cards(hand, deck)

    return amount(hand, other_cards, deck)


def take(hand, known, unknown, deck, sequence, alt=None):
    """
    Посчитываем результат при принятии решения на взятие. Т.е. нужно ли
    продолжать следовать цепочке по всей длине, или выгодно выйти раньше
    """
    if hand:
        hand = differ(hand, sequence)
    known_len = len(known)
    if known:
        known = differ(known, sequence)
    if len(known) == known_len and unknown:
        unknown.pop(0)
    other_cards = known + unknown

    if len(sequence) < 12:
        to_add = sorted(find_to_add(hand, sequence))
        while len(sequence) <= 12 and to_add:
            sequence.append(to_add.pop(0))

    sequence = [item for item in sequence if isinstance(item, Card)]
    hand += sequence
    side = 0 if alt else -1
    other_cards, deck = give_cards(other_cards, deck, side)
    if alt:
        hand, other_cards = other_cards, hand

    return amount(hand, other_cards, deck, sequence)


# added param len_table for second valuate try
def valuate(sequences, hand, known, deck, other_qty, len_table=0, attack=True):
    """
    Ищем лучший вариант хода. По признаку наименьшего значения
    """
    # если у нас всего 1 последовательность в коллекции, тогда считать не нужно.
    if len(sequences) == 1:
        return sequences[0]

    result = {'sequence': [], 'stop': 1000}

    for sequence in sequences:
        _hand, _known, _unknown, _deck = decompose(hand, known, other_qty, deck)

        # Смотрим для каждой пары в последовательности
        for i in range(len_table, len(sequence), 2):
            _seq, stop = [], 10000

            if attack:

                # если окончание пары = карта или (не карта, но есть
                # неизвестные, проверяем стоимость)
                if isinstance(sequence[:i + 2][-1], Card) or (not isinstance(
                        sequence[:i + 2][-1], Card) and _unknown):
                    _seq, stop = sequence[:i + 2], discards(
                        _hand, _known, _unknown, _deck, sequence[:i + 2])

                if not isinstance(sequence[:i + 2][-1], Card) and not _unknown:
                    # проверяем если оппонент прервет последовательность
                    # взяв карты со стола себе.

                    # _hand, _known -> _known, _hand as parameters
                    stop = take(
                        _known, _hand, _unknown, _deck, sequence[:i + 2], alt=1)
                    _seq = sequence[:i + 1]

            else:
                if isinstance(sequence[:i + 2][-1], Card):
                    continue_val = discards(
                        _hand, _known, _unknown, _deck,
                        sequence[:i + 2], defence=True)
                    alt_take_val = take(_hand, _known, _unknown,
                                        _deck, sequence[:i + 1])
                    if continue_val <= alt_take_val:
                        _seq, stop = sequence[:i + 2], continue_val

                    else:
                        _seq, stop = sequence[:i + 1], alt_take_val

                else:
                    if _hand and sequence[:i]:
                        _seq, stop = sequence[:i], take(
                            _hand, _known, _unknown, _deck, sequence[:i])

            if stop < result['stop']:
                result['sequence'], result['stop'] = _seq, stop

    if result['sequence'] and isinstance(result['sequence'][-1], Card):
        result['sequence'].append('0')

    return result['sequence']


def follower(sequence, table):
    """
    Проверяем соответствие карт на столе и нашего плана, если соответсвует
    возвращаем карту, если нет возвращаем bool
    """
    if not table:
        return sequence[0]
    next_idx = len(table)
    if next_idx <= len(sequence):
        if isinstance(sequence[next_idx - 1], Card) \
                and table[-1] == sequence[next_idx - 1]:
            return sequence[next_idx]

    return False


# self.hand, self.known, self.deck, self.opp_cards_qty, cards
def valuate_addons(hand, known, deck, opp_cards_qty, addons, table):
    _hand, _known, _unknown, _deck = decompose(hand, known, opp_cards_qty, deck)
    """
    Тоже что valuate, только на случай подбрасывания
    """
    while len(_hand) < 6 and _deck:
        _hand.append(_deck.pop(0))
    other_cards = _known + table + _unknown
    result = [], amount(_hand, other_cards, _deck)

    for item in addons[1:]:
        _hand, _known, _unknown, _deck = decompose(
            hand, known, opp_cards_qty, deck)
        _hand = differ(_hand, item)
        while len(_hand) < 6 and _deck:
            _hand.append(_deck.pop(0))
        other_cards = _known + table + _unknown + item
        _result = item, amount(_hand, other_cards, _deck)
        if _result[1] > result[1]:
            result = _result

    return result[0]


def super_follower(s_sequence, hand, known, defence=False):
    """
    Следуем за большой последовательностью, отрезаем начало по мере развития.
    Режем от 0-го элемента до первой 'f'
    """
    stop = 0
    for item in s_sequence.sequence:
        stop += 1
        if isinstance(item, str) and item == 'f':
            break

    if len(s_sequence.sequence) <= 1:
        return s_sequence.sequence, s_sequence

    # filtered = [card for card in s_sequence.sequence[:stop]
    #             if isinstance(card, Card)]
    lim_sequence = s_sequence.sequence[:stop]
    s_sequence.sequence = s_sequence.sequence[stop:]
    if not s_sequence.sequence:
        s_sequence.sequence = lim_sequence

    return lim_sequence, s_sequence


def zone_control(sequence, defence):
    """
    Показывает руку, из которой пришла та или иная карта в большой
    последовательности
    """
    zeros = 0
    zero_indexes = []
    player_control = 0
    # Находим все потенциальные точки разворота хода
    j = 0
    for item in sequence:
        if not isinstance(item, Card):
            zeros += 1
            zero_indexes.append(j)
        j += 1
    # Если точек разворота нет считаем по длине последовательности
    # False - это карта оппонента
    if zeros == 0:
        if len(sequence) % 2 == defence:
            return False
        return True
    # проверяем все последовательности внутри точек разворота
    if zeros >= 2:
        for i in range(len(zero_indexes[:-1])):
            if len(sequence[zero_indexes[i] + 1: zero_indexes[i + 1]]):
                player_control += 1
    # проверяем последовательность слева от первой точки разворота
    z_idx = zero_indexes[0]
    if zeros > 0 and len(sequence[:z_idx]) % 2 == 0:
        player_control += 1
    # меняем defence flag, если сумма разворота поменяла роли в
    # конце последовательностей
    if player_control % 2 != 0:
        defence = not defence
    # проверяем чья карта последняя в последовательности,
    # где False - это карта оппонента
    z_idx = zero_indexes[-1]
    if len(sequence[z_idx:-1]) % 2 == defence:
        return False

    return True


def make_sequence_objects(sub_result, hand, known, reverse, s_seq=None,
                          deck=None, defence=False):
    """
    Создает объект большой последовательности и показывает состояние игры
    в конце последовательности
    """
    result = []
    newborn = []
    s_seq = s_seq if s_seq else []
    deck = deck if deck else []
    for s in sub_result:

        # if len(s) // 2 > len(known):
        #     s = s[:-1]
        #     s[-1] = '0'

        _hand, _known = differ_two_hands(hand, known, s)
        last = last_sequence_takes(s)
        if last[0]:
            to_add = after_take(_hand, _known, s)
            s[-1] = 'a'
            for i in to_add:
                new = s[:]
                for j in i:
                    new.append(j), new.append('a')
                new[-1] = 'f'
                newborn.append(Sequence(_hand, _known, s_seq[:], reverse, deck))
                newborn[-1].sequence += new
                newborn[-1].hand, newborn[-1].known = differ_two_hands(
                    newborn[-1].hand, newborn[-1].known, s + new)

                if newborn[-1].deck:
                    newborn[-1].hand, newborn[-1].deck = give_cards(
                        newborn[-1].hand, newborn[-1].deck)
                newborn[-1].known += clear_super_sequence(new)

        else:
            new = s[:]
            new[-1] = 'f'
            newborn.append(Sequence(_hand, _known, s_seq[:], reverse, deck[:]))
            newborn[-1].sequence += new
            newborn[-1].reverse_counter += 1

            if newborn[-1].deck:
                newborn[-1].hand, newborn[-1].deck = give_cards(
                    newborn[-1].hand, newborn[-1].deck)

                if newborn[-1].deck:
                    newborn[-1].known, newborn[-1].deck = give_cards(
                        newborn[-1].known, newborn[-1].deck)

            newborn[-1].hand, newborn[-1].known \
                = newborn[-1].known, newborn[-1].hand

        if (not newborn[-1].hand or not newborn[-1].known) and not newborn[-1].deck:
            newborn[-1].is_winning = is_winning(newborn[-1], defence)
            result.append(newborn.pop(-1))

    return newborn, result


def addons_in_super(hand, known, table):
    """
    Не пригодилось ))
    """

    to_add = after_take(hand, known, table)
    table[-1] = 'a'
    result = []
    for item in to_add:
        points = ['a' for i in item]
        points[-1] = 'f'
        addons = [j for i in zip(item, points) for j in i]
        result.append(table + addons)

    return result

