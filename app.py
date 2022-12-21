from secrets import token_hex
from datetime import datetime
from flask import Flask, render_template, request, json, make_response
from logics.web_game import Game, handle_get, handle_post


app = Flask(__name__)
games = {} 

def clear_games():
    now = int(datetime.timestamp(datetime.now()))
    to_delete = [id for id in games if now - games[id][1] > 30]
    for id in to_delete:
        del games[id]

@app.route("/", methods=['GET', 'POST'])
def main():
    game_id = request.cookies.get('game_id')
    if request.method == 'POST':
        if game_id:            
            data = 'New game' if not games.get(game_id) else json.loads(request.data.decode("utf-8"))['data']
            if data == 'New game':
                games[game_id] = [Game('User'), int(datetime.timestamp(datetime.now()))]
                clear_games()
                resp = make_response(render_template('main.html', **handle_get(games[game_id][0])))
                games[game_id][1] = int(datetime.timestamp(datetime.now()))               
                return resp           
            return json.dumps(handle_post(games[game_id][0], data), indent=4)
        
    if request.method == 'GET':
        clear_games()
        if not game_id or not games.get(game_id):
            game_id = token_hex(8)
            games[game_id] = [Game('User'), 0]

        resp = make_response(render_template('main.html', **handle_get(games[game_id][0])))
        games[game_id][1] = int(datetime.timestamp(datetime.now()))
        resp.set_cookie("game_id", value=game_id)
        return resp


if __name__ == '__main__':
    app.run()