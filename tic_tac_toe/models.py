from typing import List, Optional
from sqlalchemy import String, Enum
from tic_tac_toe.database import db

import enum

from tic_tac_toe.errors import InvalidMoveException, UnableToJoinGameException
from tic_tac_toe.utils import (
    lies_on_left_diagonal,
    lies_on_right_diagonal,
    points_on_left_diagonal,
    points_on_right_diagonal,
)


class GameResultChoice(enum.Enum):
    WIN = "win"
    LOSS = "loss"
    TIE = "tie"


class GameStatus(enum.Enum):
    PENDING_PLAYERS = "pending_players"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)

    def to_dict(self) -> dict:
        return {"id": self.id}


class GameResult(db.Model):
    __tablename__ = "gameresults"
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"))
    result = db.Column("value", Enum(GameResultChoice))
    player_id = db.Column(db.Integer, db.ForeignKey("game_players.id"))

    # relationships
    player = db.relationship("GamePlayer")

    def to_dict(self) -> dict:
        return {
            "user_id": self.player.user_id,
            "result": self.result.value,
        }


class GameMove(db.Model):
    __tablename__ = "game_moves"

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"))
    row_placed = db.Column(db.Integer)
    column_placed = db.Column(db.Integer)
    player_moved_id = db.Column(db.Integer, db.ForeignKey("game_players.id"))
    # Set if there is a next move
    next_move_id = db.Column(db.Integer, db.ForeignKey("game_moves.id"), nullable=True)

    # relationships
    player_moved = db.relationship("GamePlayer")


class GamePlayer(db.Model):
    __tablename__ = "game_players"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"))
    marker = db.Column(String(8))
    turn = db.Column(db.Integer)

    # relationships
    user = db.relationship("User")

    def to_dict(self):
        return {"user_id": self.user_id, "marker": self.marker}


class Game(db.Model):
    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True)
    max_rows = db.Column(db.Integer, default=3)
    max_columns = db.Column(db.Integer, default=3)
    max_players = db.Column(db.Integer, default=2)
    status = db.Column("value", Enum(GameStatus), default=GameStatus.PENDING_PLAYERS)

    # relationships
    moves = db.relationship("GameMove", lazy="dynamic")  # One-To-Many
    players = db.relationship(
        "GamePlayer", lazy="dynamic", backref="game"
    )  # One-To-Many
    results = db.relationship("GameResult")  # One-To-Many

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "status": self.status.value,
            "board": self.board_serialization(),
            "board_size": self.max_rows,  # Only support a square board for now
            "players": [player.to_dict() for player in self.players],
            "results": [result.to_dict() for result in self.results],
            "player_turn": self.player_turn().id
            if self.status == "in_progress"
            else None,
        }

    def board_serialization(self) -> List[List[str]]:
        # Get all GameMoves, serialize
        board = [["" for c in range(self.max_columns)] for r in range(self.max_rows)]
        for move in self.moves:
            board[move.row_placed][move.column_placed] = move.player_moved.marker

        return board

    def valid_space(self, row: int, col: int) -> bool:
        return (0 <= row < self.max_rows) and (0 <= col < self.max_columns)

    def space_occupied(self, row: int, col: int) -> bool:
        return (
            self.moves.filter(
                GameMove.row_placed == row, GameMove.column_placed == col
            ).count()
            > 0
        )

    def most_recent_move(self) -> Optional[GameMove]:
        if not self.moves:
            return None
        return self.moves.filter(GameMove.next_move_id == None).first()

    def player_turn(self) -> User:
        num_moves_done = self.moves.count()
        turn = num_moves_done % self.max_players
        return self.players.filter(GamePlayer.turn == turn).first().user

    def process_player_win(self, player_moved: GamePlayer):
        self.results.append(
            GameResult(result=GameResultChoice.WIN, player=player_moved)
        )
        for player in self.players.filter(GamePlayer.id!=player_moved.id):
            self.results.append(
                    GameResult(result=GameResultChoice.LOSS, player=player)
                )
        self.status = GameStatus.COMPLETED
        db.session.commit()

    def process_game_tie(self):
        for player in self.players:
            self.results.append(GameResult(result=GameResultChoice.TIE, player=player))
        self.status = GameStatus.COMPLETED
        db.session.commit()

    def player_mark_at_position(self, row: int, col: int, player_moved: GamePlayer) -> bool:
        return self.moves.filter(GameMove.row_placed == row, GameMove.column_placed == col, GameMove.player_moved==player_moved).count() == 1

    def process_game_state(self, row: int, col: int, player_moved: GamePlayer) -> None:
        # Look for a vertical win by filtering for GameMoves along this row by this player
        if all([self.player_mark_at_position(row, i, player_moved) for i in range(self.max_rows)]):
            self.process_player_win(player_moved)
            return
        # Look for a horizontal win by filtering for GameMoves along this row by this player
        # horizontal_moves = self.moves.filter(
        #     GameMove.column_placed == col, GameMove.player_moved == player_moved
        # )
        # if horizontal_moves.count() == self.max_rows:
        #     self.process_player_win(player_moved)
        #     return

        if all([self.player_mark_at_position(i, col, player_moved) for i in range(self.max_rows)]):
            self.process_player_win(player_moved)
            return
        # Look for a left diagonal win
        if lies_on_left_diagonal(row, col, self.max_rows):
            if all([self.player_mark_at_position(x, y, player_moved) for x,y in points_on_left_diagonal(self.max_rows)]):
                self.process_player_win(player_moved)
                return
        # Look for a right diagonal win
        if lies_on_right_diagonal(row, col, self.max_rows):
            if all([self.player_mark_at_position(x, y, player_moved) for x,y in points_on_right_diagonal(self.max_rows)]):
                self.process_player_win(player_moved)
                return
        # Look for a tie
        if self.moves.count() == (self.max_rows * self.max_columns):
            self.process_game_tie()

    def join_game(self, user) -> None:
        # Validate joining a game
        if self.players.filter(GamePlayer.user == user).count() > 0:
            raise UnableToJoinGameException(
                f"User {user.id} already joined game {self.id}"
            )
        if self.players.count() == self.max_players:
            raise UnableToJoinGameException(f"Game {self.id} has no more player spots.")

        # Only support max size 2 for now. First player will have X, second player will have O
        marker = "X" if self.players.count() == 0 else "O"
        turn = self.players.count()
        # Join by adding a GamePlayer instance
        player = GamePlayer(user=user, game=self, marker=marker, turn=turn)
        db.session.add(player)
        # If we've reached the max players, the game can begin
        if self.players.count() == self.max_players:
            self.status = GameStatus.IN_PROGRESS
        db.session.add(self)
        db.session.commit()

    def make_move(self, user, row, col) -> None:
        # Move validation
        if self.status != GameStatus.IN_PROGRESS:
            raise InvalidMoveException(
                f"Cannot make a move on a game in {self.status.value} status"
            )
        if user != self.player_turn():
            raise InvalidMoveException(f"Not {user.id}'s turn!")
        if not self.valid_space(row, col):
            raise InvalidMoveException(f"Position ({row},{col}) is invalid.")
        if self.space_occupied(row, col):
            raise InvalidMoveException("Space ({row}, {col}) is already occupied!")

        # Persist the move
        game_player = self.players.filter(GamePlayer.user == user).first()
        move = GameMove(
            game_id=self.id, row_placed=row, column_placed=col, player_moved=game_player
        )
        db.session.add(move)
        if last_move := self.most_recent_move():
            last_move.next_move_id = move.id
            db.session.add(last_move)
        # Persist to the db
        db.session.commit()
        # Look for a win or tie
        self.process_game_state(row, col, game_player)
