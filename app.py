from flask import Flask, render_template, request, jsonify, json
from logics.player import Player


app = Flask(__name__)
game = Game('Username')
if isinstance(game.queue[0], Player):
    _ = ai(game)



@app.route("/")
def main():
    return 