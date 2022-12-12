from re import findall
from random import shuffle

from card import Card
from const import FRONT_SUITS
from helpers import VALUES, SUITS, clear_super_sequence
from human import input_processing
from player import make_turn


def card2image(card):
    return f'{SUITS.index(card.suit) + 1}-{card.value}.png'


def image2card(string):
    card = input_processing(string)
    return Card(int(card[1]), FRONT_SUITS[card[0]])


def images2cards(cards):
    cards = findall('\d+[-]\d+', cards)
    cards = [input_processing(card_name) for card_name in cards]
    return cards

def ai(game, addons=False):
    if addons:
        to_add = game.queue[0].addons(game.on.table)
        game.on_table += to_add
        game.on_table = clear_super_sequence(game.on_table)
        return None

    defence = False if len(game.on_table) % 2 == 0 else True
    response = game.player2.make_turn(game.on_table, defence)

    if isinstance(response, str):
        return response
    
    game.on_table.append(response)
    return 'continue'

def ui(game, addons=False):
    if addons: # ???
        return game.queue[0].web_addons(game.on_table, addons)

    defence = False if len(game.on_table) % 2 == 0 else True
    response = game.player1.make_turn(game.on_table, defence)
    
    if isinstance(response, str):
        return response
        
    game.on_table.append(response)
    return 'continue'
