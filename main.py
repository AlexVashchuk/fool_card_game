from logics.card import Card
from logics.player import Player
from logics.human import Human
from random import shuffle
from logics.helpers import VALUES, SUITS, make_trumps, \
    change_queue, trump_search, first_turn


# game mechanic
def give_cards_to_player(player):
    cards_in_hand = len(player.hand)
    if cards_in_hand < 6:
        for _ in range(6 - cards_in_hand):
            if not deck:
                break
            else:
                player.hand.append(deck.pop(0))


def make_turn(func):
    def wrapper(*args):
        i = 0
        result = None
        while i < 6:
            result = func(*args)
            if not isinstance(result[-1], Card):
                break
            i += 1
        return result
    return wrapper


@make_turn
def request_card():

    on_table.append(queue[0].make_turn(on_table))
    if not isinstance(on_table[-1], Card):
        return on_table

    on_table.append(queue[1].make_turn(on_table, defence=True))
    if not isinstance(on_table[-1], Card):
        return on_table

    return on_table


def turn_result(_queue):
    # начинаем серию ходов
    result = request_card()[-1]

    # смотрим не победил ли кто-нибудь
    if not deck:
        if not _queue[0].hand:
            return _queue[0], 'win'
        if not _queue[1].hand:
            return _queue[1], 'win'

    # смотрим чем закончилась серия и действуем соответственно
    if isinstance(result, Card) or result == "discards":
        # проверяем, все-ли прошло так, как планировалось
        _queue[1].behavior_check(on_table)
        # игроки берут карты из колоды
        for player in _queue:
            give_cards_to_player(player)
        # передаем длину руки оппонента каждому игроку
        _queue[0].opp_cards_qty = len(_queue[1].hand)
        _queue[1].opp_cards_qty = len(_queue[0].hand)
        # передаем длину колоды игрокам
        deck_len = len(deck)
        _queue[0].real_deck = queue[1].real_deck = deck_len
        # меняем очередность хода
        new_queue = change_queue(_queue)
        # очищаем стол
        on_table.clear()
        return new_queue
    if result == 'take':
        # проверяем, все-ли прошло так, как планировалось
        _queue[0].behavior_check(on_table)
        # проверяем если нападавший игрок хочет добавить карт
        additional = _queue[0].addons(on_table[:-1])
        if additional:
            _queue[1].hand += additional
            _queue[1].check_addons(additional)
            _queue[0].known += additional
            if not deck:
                if not _queue[0].hand:
                    return _queue[0], 'win'

        # атакующий игрок получает карты из колоды
        give_cards_to_player(_queue[0])
        # обороняющийся игрок забирает карты со стола
        # и запоминает количество карт оппонента
        _queue[1].hand += on_table[:-1]
        _queue[1].opp_cards_qty = len(_queue[0].hand)
        # атакующий игрок запоминает карты, которые забрал
        # оборонявшийся игрок и общее количество карта оппонента
        _queue[0].known += on_table[:-1]
        _queue[0].opp_cards_qty = len(_queue[1].hand)
        # передаем длину колоды игрокам
        deck_len = len(deck)
        queue[0].real_deck = deck_len
        queue[1].real_deck = deck_len
        # убираем карты со стола и очищаем стол
        on_table.clear()
        return _queue


# Game
#########################################


# создаем колоду
deck = [Card(value, suit) for suit in SUITS for value in VALUES]


# пока не убедимся что в первых 12 картах есть козырь, перемешиваем
while not trump_search(deck):
    shuffle(deck)
# назначаем козыря и делаем карты козырными
trump = deck[-1]
make_trumps(deck, trump)

# Создаем игроков и раздаем карты и сообщаем необходимую информацию игроку
deck_to_remember = sorted(deck)
deck_to_remember.append(deck_to_remember.pop(deck_to_remember.index(trump)))

player1 = Human('Human', deck[0:11:2], trump)
# player1 = Player('Player1', deck[0:11:2], trump, deck_to_remember)
player2 = Player('Player2', deck[1:12:2], trump, deck_to_remember)
print(id(player1.hand), player1.hand, id(player2.hand), player2.hand)
del deck[0:12]
_len = len(deck)
player1.real_deck = player2.real_deck = _len

# определяем очередность хода и создаем стол
queue = first_turn(player1, player2, trump)
# если игрок показал козырь для определения очередности хода, другой его может
# запомнить
for _ in range(2):
    if isinstance(queue[1], Player):
        t1 = queue[0].find_trump(trump)
        if isinstance(t1, Card):
            queue[1].known.append(t1)
    queue = change_queue(queue)

# инициализируем стол
on_table = []


# играем
print(trump)
while player1.hand and player2.hand:
    queue = turn_result(queue)
    if isinstance(queue[1], str):
        print(queue[0].name, queue[1])
        break

