from re import findall
from random import shuffle

from logics.card import Card
from logics.const import FRONT_SUITS
from logics.human import Human, input_processing
from logics.player import Player
from logics.helpers import VALUES, SUITS, make_trumps, change_queue, \
    trump_search, first_turn, clear_super_sequence, differ


def card2image(card):
    return f'{SUITS.index(card.suit) + 1}-{card.value}.png'


def image2card(string):
    card = input_processing(string)
    return Card(int(card[1]), FRONT_SUITS[card[0]])


def images2cards(cards):
    cards = findall('\d+[-]\d+', cards)
    cards = [input_processing(card_name) for card_name in cards]
    cards = [Card(int(elem[1]), FRONT_SUITS[elem[0]]) for elem in cards]
    print('images2cards', cards)
    print('cards2images', cards2images(cards))
    return cards


def cards2images(cards):
    return [card2image(card) for card in cards]
       

def give_cards_to_player(player, deck):
    cards_in_hand = len(player.hand)
    if cards_in_hand < 6:
        for i in range(6 - cards_in_hand):
            if not deck:
                break
            else:
                player.hand.append(deck.pop(0))
    return player.hand, deck


def ai(game):

    defence = False if len(game.on_table) % 2 == 0 else True
    card = game.player2.make_turn(game.on_table, defence)

    if isinstance(card, str):
        return card

    game.on_table.append(card)
    return 'continue'


def ui(game):
    if game.addons:
        return game.player1.web_addons(game.on_table)
    
    defence = False if len(game.on_table) % 2 == 0 else True # определяем образ действия
    card = game.player1.web_turn(game.on_table, defence) # получаем true / false
    if not card:
        return False
    
    game.on_table.append(game.player1.endpoint) 
    return True


def got_addons(game, data):
    print(data)
    if data == 'Take':
        toTaker = cards2images(game.on_table)
        return {
            'clearTable' : True,
            'lastCard' : toTaker,
            'lenDeck' : len(game.deck)
        }
    else:
        print('endpoint', game.player1.endpoint)       
        game.player1.endpoint = images2cards(data)
        if ui(game):
            game.give_addons(game.player1.endpoint)
            if game.winner:
                return {'message' : game.winner }
            toTaker = cards2images(game.on_table)
            return {
                'clearTable' : True,
                'lenDeck' : len(game.deck)
            }

    return {'message' : 'It wasn\'t the right choice. Try again', 'actionText' : 'Add cards'}


def got_card(game, data):
    game.player1.endpoint = image2card(data)
    if not ui(game):
        return {'message': 'Try again'}

    winner = game.somebodywins()
    if winner:
        return {'winner': game.winner, 'lastCard': data}

    draw_on = [data]
    result = ai(game)

    game.player1.endpoint = None
    return backend_handler(result, game, draw_on)


def got_discards(game):
    last_card = card2image(game.on_table[-2]) if len(game.on_table) > 1 else ''
    if not game.on_table:
        return {'message' : 'Try again'}
    if game.discards():
        return {
            'winner': game.winner, 
            'toTable' : card2image(game.on_table[-1])}

    deck = 'coloda.png' if game.deck else 'fon.png'
    return {
        'clearTable' : True,
        'actionText' : 'Take',
        'fromFront' : True,
        'lastCard' : last_card,
        'deck' : deck,
        'toTable' : card2image(game.on_table[-1]),
        'lenDeck' : len(game.deck)
    }


def got_take(game):
    last_card = card2image(game.on_table[-2]) if len(game.on_table) > 1 else ''
    if game.take():
        return {
            'winner': game.winner, 
            'playerCards' : [card2image(card) for card in game.player1.hand],
            'opponentCards' : len(game.player2.hand)}

    deck = 'coloda.png' if game.deck else 'fon.png'
    return {
        'clearTable' : True,
        'lenDeck' : len(game.deck),
        'actionText' : 'Take',
        'fromFront' : True,
        'lastCard' : last_card,
        'deck' : deck,
        'toTable' : card2image(game.on_table[-1])
    }


def backend_card(game, draw):
    draw.append(card2image(game.on_table[-1]))
    winner = game.somebodywins()
    if winner:
        return { 'message' : winner, 'toTable' : draw }
    action_text = 'Discards' if len(game.on_table) % 2 == 0 else 'Take'
    return {
        'actionText' : action_text,
        'toTable' : draw,
    }


def backend_discards(game):
    last_card = card2image(game.on_table[-1])
    if game.discards():
        return {'message' : game.winner}
    return {
        'clearTable' : True,
        'lastCard' : last_card,
        'lenDeck' : len(game.deck)
    }


def backend_takes(game, draw):
    game.addons = True
    winner = game.somebodywins()
    if winner:
        return {'winner' : winner}
    return {
        'message' : 'You can add cards',
        'clearTable': False,
        'actionText': 'Add cards',
        'lastCard' : draw        
    }


def backend_handler(data, game, draw):
    match data:
        case "take":
            return backend_takes(game, draw)
        case "discards":
            return backend_discards(game)
        case _:
            return backend_card(game, draw)


def switch_action(data, game):

    match data:
            case "Take":
                return got_take(game)
            case "Discards":
                return got_discards(game)
            case _:
                return got_card(game, data)


def handle_post(game, data):
    if game.addons:
        result = got_addons(game, data)
    else:
        result = switch_action(data, game)
    print('###############')
    print(game.player2.hand)
    print(game.on_table)
    print(game.player1.hand)
    print(game.player2.limited_sequence)
    print(game.player2.super)
    if len(result) == 1:
        if 'message' in result:
            return {'message' : result['message']}

    if 'winner' in result:
        return {**result}

    default_values = {
        'message' : 'Your turn',
        'playerCards' : [card2image(card) for card in game.player1.hand],
        'opponentCards' : len(game.player2.hand),
        'clearTable' : False,
        'toTable' : 'nothing',
        'fromFront': False,
        'lastCard' : data,
        'actionText' : 'Discards',
        'lenDeck' : len(game.deck)
    }

    return {**default_values, **result}


def handle_get(game):
    player_cards = [card2image(card) for card in game.player1.hand]
    deck = 'coloda.png' if game.deck else 'fon.png'
    trump = card2image(game.trump)
    table = [card2image(card) for card in game.on_table]
    if not game.addons:
        action_text = 'Discards' if len(game.on_table) % 2 == 0 else 'Take'
        first_second = 'secondComp' if len(game.on_table) % 2 == 0 else 'firstComp'
    else:
        action_text = 'Add cards'
    return  {
        # "cleanTable": False,
        # "addons": game.addons,
        "playerCards": player_cards,
        "opponentCards": len(game.player2.hand),
        "table": table,
        "deck": deck,
        "lenDeck": len(game.deck),
        "trump": trump,
        "message": 'Your turn',
        "actionText": action_text,
        "firstSecond": first_second,
        "trumpSuit" : game.trump.suit,
        "idTrump" : [k for k, v in FRONT_SUITS.items() if v == game.trump.suit][0]
    }
    

class Game:
    def __init__(self, name):
        """ Перемешивание колоды раздача карт, поиск козыря и очередности"""
        self.addons = False
        self.winner = None
        self.deck = [Card(value, suit) for suit in SUITS for value in VALUES]
        self.deck_to_remember = self.deck[:]

        while not trump_search(self.deck):
            shuffle(self.deck)
        self.trump = self.deck[-1]
        self.deck = make_trumps(self.deck, self.trump)
        self.deck_to_remember.append(
            self.deck_to_remember.pop(self.deck_to_remember.index(self.trump)))

        self.player1 = Human(name, self.deck[0:11:2], self.trump)
        self.player2 = Player('computer', self.deck[1:12:2], self.trump,
                              self.deck_to_remember)
        del self.deck[0:12]
        self.player1.real_deck = self.player2.real_deck = len(self.deck)

        self.queue = first_turn(self.player1, self.player2, self.trump)
        self.on_table = []
        if isinstance(self.queue[0], Player):
            _ = ai(self)

    def discards(self):
        """Игрок или компьютер объявил discards"""
        for player in self.queue:
            give_cards_to_player(player, self.deck)
            hasattr(player, "limited_sequence") and player.limited_sequence.clear()
        if self.somebodywins():
            return self.winner
        self.queue[0].opp_cards_qty = len(self.queue[1].hand)
        self.queue[1].opp_cards_qty = len(self.queue[0].hand)
        self.queue = change_queue(self.queue)
        self.on_table = []
        if isinstance(self.queue[0], Player):
            self.on_table.append(self.queue[0].make_turn(self.on_table))
        return None
    
    def take(self):
        """take объявил игрок, а не компьютер"""
        cards = self.player2.addons(self.on_table)
        total_cards = clear_super_sequence(self.on_table + cards)
        self.player1.hand += total_cards
        self.player2.known += total_cards
        self.player2.hand, self.deck = give_cards_to_player(self.player2, self.deck)
        if self.somebodywins():
            return self.winner
        self.on_table = []
        self.player2.opp_cards_qty = len(self.player1.hand)
        self.on_table.append(self.player2.make_turn(self.on_table))
        return None

    def give_addons(self, cards):
        """handle user addons"""
        total_cards = clear_super_sequence(self.on_table + cards)
        self.player2.hand += total_cards
        if cards:
            self.player1.hand = differ(self.player1.hand, cards)
        self.player1.hand, self.deck = give_cards_to_player(self.player1, self.deck)
        self.player2.opp_cards_qty = len(self.player1.hand)
        if self.somebodywins():
            return self.winner
        self.on_table = []
        self.addons = False
        return None

    def somebodywins(self):
        if not self.queue[0].hand and not self.deck:
            self.winner = self.queue[0].name
            return f'{self.queue[0].name} won!'
        if not self.queue[1].hand and not self.deck:
            self.winner = self.queue[1].name
            return f'{self.queue[1].name} won!'
        return None
