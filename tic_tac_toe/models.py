from typing import List, Optional
from sqlalchemy import CHAR, String, Enum
from tic_tac_toe.database import db
from sqlalchemy.dialects.postgresql import ARRAY

import enum

from tic_tac_toe.errors import InvalidMoveException, UnableToJoinGameException
from tic_tac_toe.utils import lies_on_left_diagonal, lies_on_right_diagonal, points_on_left_diagonal, points_on_right_diagonal

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

class GameResult(db.Model):
    __tablename__ = "gameresults"
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"))
    result = db.Column('value', Enum(GameResultChoice))
    player_id = db.Column(db.Integer, db.ForeignKey("game_players.id"))

    # relationships
    player = db.relationship("GamePlayer")
    game = db.relationship("Game")

class GameMove(db.Model):
    __tablename__ = "game_moves"

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"))
    row_placed = db.Column(db.Integer)
    column_placed = db.Column(db.Integer)
    player_moved_id = db.Column(db.Integer, db.ForeignKey("game_players.id"))
    # Set if there is a next move
    next_move = db.Column(db.Integer, db.ForeignKey("game_moves.id"), nullable=True)

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

class Game(db.Model):
    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True)
    max_rows = db.Column(db.Integer, default=3)
    max_columns = db.Column(db.Integer, default=3)
    max_players = db.Column(db.Integer, default=2)
    status = db.Column("value", Enum(GameStatus), default=GameStatus.PENDING_PLAYERS)
    
    # relationships
    moves = db.relationship("GameMove", lazy='dynamic')# One-To-Many
    players = db.relationship("GamePlayer", lazy='dynamic', backref="game") # One-To-Many
    results = db.relationship("GameResult") # One-To-Many

    def board_serialization(self) -> List[List[str]]:
        # Get all GameMoves, serialize
        board = [["" for c in range(self.max_columns)] for r in range(self.max_rows)]
        for move in self.moves:
            board[move.row_placed][move.column_placed] = move.player_moved.marker
        
        return board

    def valid_space(self, row, col) -> bool:
        return (0 <= row < self.max_rows) and (0 <= col < self.max_columns)

    def space_occupied(self, row, col) -> bool:
        return self.moves.filter(GameMove.row_placed == row, GameMove.column_placed==col).count() > 0

    def most_recent_move(self) -> Optional[GameMove]:
        if not self.moves:
            return None
        return self.moves.filter(GameMove.next_move==None).first()

    def player_turn(self) -> User:
        num_moves_done = self.moves.count()
        turn = (num_moves_done % self.max_players)
        return self.players.filter(GamePlayer.turn==turn).first().user

    def process_game_state(self, row, col, player_moved) -> None:
        # Look for a vertical win
        vertical_moves = self.moves.filter(row_placed=row)
        if len(vertical_moves) == self.max_rows:
            if all([move.player_moved == player_moved for move in vertical_moves]):
                # player_moved won
                db.session.add(GameResult(game=self.id, result=GameResultChoice.WIN, player=player_moved))
                for player in self.players:
                    if player != player_moved:
                        db.session.add(GameResult(game=self.id, result=GameResultChoice.LOSS, player=player))                
                db.session.commit()
                return
        # Look for a horizontal win
        horizontal_moves = self.moves.filter(col_placed=col)
        if len(horizontal_moves) == self.max_rows:
            if all([move.player_moved == player_moved for move in vertical_moves]):
                # player_moved won
                db.session.add(GameResult(game=self.id, result=GameResultChoice.WIN, player=player_moved))
                for player in self.players:
                    if player != player_moved:
                        db.session.add(GameResult(game=self.id, result=GameResultChoice.LOSS, player=player))
                db.session.commit()
                return
        # Look for a left diagonal win
        if lies_on_left_diagonal(row, col, self.max_rows):
            all_in_a_row = True
            for x, y in points_on_left_diagonal(self.max_rows):
                if not self.moves.filter(GameMove.row_placed==x, GameMove.col_placed==y).count() != 1:
                    all_in_a_row = False
                    break
                move = self.moves.filter(GameMove.row_placed==x, GameMove.col_placed==y).first()
                if move.player_moved != player_moved:
                    all_in_a_row = False
                    break
            if all_in_a_row:
                # player_moved won
                db.session.add(GameResult(game=self.id, result=GameResultChoice.WIN, player=player_moved))
                for player in self.players.filter(GameMove.player!=player_moved):
                    db.session.add(GameResult(game=self.id, result=GameResultChoice.LOSS, player=player))                
                db.session.commit()
        # Look for a right diagonal win
        if lies_on_right_diagonal(row, col, self.max_rows):
            for x, y in points_on_right_diagonal(self.max_rows):
                all_in_a_row = True
                if not self.moves.filter(GameMove.row_placed==row, GameMove.col_placed==col).count() != 1:
                    all_in_a_row = False
                    break
                move = self.moves.filter(GameMove.row_placed==row, GameMove.col_placed==col).first()
                if move.player_moved != player_moved:
                    all_in_a_row = False
                    break
                if all_in_a_row:
                    # player_moved won
                    db.session.add(GameResult(game=self.id, result=GameResultChoice.WIN, player=player_moved))
                    for player in self.players.filter(GameMove.player!=player_moved):
                        db.session.add(GameResult(game=self.id, result=GameResultChoice.LOSS, player=player))                
                    db.session.commit()
        # Look for a tie
        if self.moves.count() == (self.max_rows * self.max_columns):
            # All get ties
            for player in self.players:
                db.session.add(GameResult(game=self.id, result=GameResultChoice.TIE, player=player))
            self.status = GameStatus.COMPLETED
            db.session.add(self)
            
            db.session.commit()

    def join_game(self, user) -> None:
        if self.players.filter(GamePlayer.user==user).count() > 0:
            raise UnableToJoinGameException(f"User {user.id} already joined game {self.id}")
        if self.players.count() == self.max_players:
            raise UnableToJoinGameException(f"Game {self.id} has no more player spots.")
        
        # Only support max size 2 for now
        marker = "X" if self.players.count() == 0 else "O"
        turn = self.players.count()
        # Actually join
        player = GamePlayer(user=user, game=self, marker=marker, turn=turn)
        db.session.add(player)
        db.session.commit()
        # Change state if necessary
        if self.players.count() == self.max_players:
            self.status = GameStatus.IN_PROGRESS
        db.session.add(self)
        db.session.commit()

    
    def make_move(self, user, row, col) -> None:
        # Validate the move
        if self.status != GameStatus.IN_PROGRESS:
            raise InvalidMoveException(f"Cannot make a move on a game in {self.status.value} status")
        if user != self.player_turn():
            raise InvalidMoveException(f"Not {user.id}'s turn!")
        if not self.valid_space(row,col):
            raise InvalidMoveException(f"Position ({row},{col}) is invalid.")
        if self.space_occupied(row, col):
            # Do not allow
            raise InvalidMoveException("Space ({row}, {col}) is already occupied!")

        # Persist the move
        game_player = self.players.filter(GamePlayer.user==user).first()
        move = GameMove(game_id=self.id, row_placed=row, column_placed=col, player_moved=game_player.id)
        db.session.add(move)
        if last_move := self.most_recent_move():
            last_move.next_move = move
            db.session.add(last_move)
        # Persist to the db
        db.session.commit()
        # Look for a win or tie
        self.process_game_state(row, col, game_player)


    