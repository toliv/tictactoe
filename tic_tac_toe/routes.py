from flask import Blueprint, g, jsonify, request, current_app
from tic_tac_toe.database import db
from tic_tac_toe.errors import InvalidMoveException, UnableToJoinGameException

app = current_app

from tic_tac_toe.models import Game, User

routes_blueprint = Blueprint("", __name__)


@routes_blueprint.route("/")
def hello_world():
    """
    Sanity check endpoint
    """
    return jsonify(tic_tac="toe")


@routes_blueprint.route("/users", methods=["POST", "GET"])
def users():
    """
    Support POST to create a user and GET to fetch a User
    """
    if request.method == "POST":
        user = User()
        db.session.add(user)
        db.session.commit()
        return user.to_dict()
    elif request.method == "GET":
        user_id = request.args.get("id")
        if not user_id:
            return "Must provide a user_id", 400
        user = User.query.get(int(user_id))
        if not user:
            return f"User {user_id} not found.", 404
        return user.to_dict()


@routes_blueprint.route("/games", methods=["POST"])
def create_game():
    """
    POST request to create a Game
    """
    game = Game()
    db.session.add(game)
    db.session.commit()
    return game.to_dict()


@routes_blueprint.route("/games/<int:id>", methods=["GET"])
def games(id: int):
    """
    GET request to fetch a Game
    """
    game = Game.query.get(id)
    if not game:
        return f"Game {id} not found.", 404
    return game.to_dict()


@routes_blueprint.route("/games/<int:id>/join", methods=["POST"])
def join_game(id: int):
    """
    POST request to join a Game
    """
    game = Game.query.get(id)
    if not game:
        return f"Game {id} not found.", 404
    user_id = request.form.get("user_id")
    user = User.query.get(user_id)
    if not user:
        return f"User {user_id} not found.", 404
    try:
        game.join_game(user)
    except UnableToJoinGameException as e:
        return e.msg, 400
    return game.to_dict()


@routes_blueprint.route("/games/<int:id>/move", methods=["POST"])
def move(id: int):
    """
    POST request to make a move on this Game
    """
    game = Game.query.get(id)
    if not game:
        return f"Game {id} not found.", 404
    user_id = request.form.get("user_id")
    user = User.query.get(user_id)
    if not user:
        return f"User {user_id} not found.", 404
    try:
        row = request.form.get("row", type=int)
        column = request.form.get("column", type=int)
    except ValueError:
        return f"Provide valid integer types for row and column.", 400
    if row == None or column == None:
        return f"Row and column must be provided to make a move.", 400
    try:
        game.make_move(user, row, column)
    except InvalidMoveException as e:
        return e.msg, 400
    return game.to_dict()
