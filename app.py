from flask import Flask, render_template, request, json, redirect
from logics.web_game import Game, handle_get, handle_post


app = Flask(__name__)

global game
game = None


@app.route("/", methods=['GET', 'POST'])
def main():
    global game

    if request.method == 'POST':
        
        data = json.loads(request.data.decode("utf-8"))['data']
        
        if data == 'New game':

            game = Game('Username')
            return redirect('/', 300)
            
        return json.dumps(handle_post(game, data), indent=4)
        
    if request.method == 'GET':    
        if not game:
            game = Game('Username')
        return render_template('main.html', **handle_get(game))


if __name__ == '__main__':
    app.run('', debug=True)