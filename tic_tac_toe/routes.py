from flask import jsonify, request, current_app
from sqlalchemy import select
from tic_tac_toe.database import db

app = current_app

from tic_tac_toe.models import Game, GamePlayer, User

@current_app.route("/")
def hello_world():
    return jsonify(hello="world")

@current_app.route("/users", methods=["POST", "GET"])
def users():
    if request.method == "POST":
        user = User()
        db.session.add(user)
        db.session.commit()
        return jsonify(user_id=user.id)


@current_app.route("/games", methods=["POST", "GET"])
def games():
    if request.method == "POST":
        user = request.form['user']
        print(user)
        game = Game()
        player = GamePlayer(game_id=game.id, marker="X", player_id=1)
        db.session.add(game)
        db.session.add(player)
        db.session.commit()
        return jsonify(board=game.board_serialization())
    else:
        game_id = request.args.get('game_id')
        game = Game.query.get(game_id)
        return jsonify(board=game.board_serialization())

@current_app.route("/move", methods=["POST"])
def move():
    game_id = request.form['game']
    user_id = request.form['user']
    position = request.form['position']

    game = Game.query.get(game_id)
    return None

