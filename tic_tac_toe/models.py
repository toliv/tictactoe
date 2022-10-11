from typing import List
from sqlalchemy import CHAR, String
from tic_tac_toe.database import db
from sqlalchemy.dialects.postgresql import ARRAY

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)

class Game(db.Model):
    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True)
    max_rows = db.Column(db.Integer, default=3)
    max_columns = db.Column(db.Integer, default=3)
    max_players = db.Column(db.Integer, default=2)
    moves = db.relationship("GameMove")# One-To-Many
    players = db.relationship("GamePlayer") # One-To-Many

    def board_serialization(self) -> List[List[str]]:
        # Get all GameMoves, serialize
        board = [["" for c in range(self.max_columns)] for r in range(self.max_rows)]

        for move in self.moves:
            board[move.row_placed][move.column_placed] = move.player_moved.mark
        
        return board
    
    def make_move(self) -> None:
        return None


class GamePlayer(db.Model):
    __tablename__ = "game_players"

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"))
    marker = db.Column(String(8))

class GameMove(db.Model):
    __tablename__ = "game_moves"

    id = db.Column(db.Integer, primary_key=True)
    game = db.Column(db.Integer, db.ForeignKey("games.id"))
    row_placed = db.Column(db.Integer)
    column_placed = db.Column(db.Integer)
    player_moved = db.Column(db.Integer, db.ForeignKey("game_players.id"))
    # Set if there is a next move
    next_move = db.Column(db.Integer, db.ForeignKey("game_moves.id"), nullable=True)
    

    

class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    players = db.Column(ARRAY(CHAR, dimensions=2))

    