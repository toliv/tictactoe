import pytest
from tic_tac_toe.errors import InvalidMoveException, UnableToJoinGameException

from tic_tac_toe.models import Game, GameMove, GamePlayer, GameStatus, User

@pytest.fixture()
def user(session):
    user = User()
    session.add(user)
    session.commit()
    return user

@pytest.fixture()
def game(session):
    game = Game()
    session.add(game)
    session.flush()
    return game

def test_post_model(session, user):
    user = User()
    session.add(user)
    session.commit()

    assert user.id >= 0

def test_empty_board_serialization(session, game):
    assert game.board_serialization() == [
        ["", "", "",],
        ["", "", "",],
        ["", "", "",]
    ]

def test_non_empty_board_serialization(session, user, game):
    player = GamePlayer(user=user, game_id = game.id, marker="X", turn=0)
    session.add(player)
    session.flush()
    game_move = GameMove(game_id=game.id, row_placed=0, column_placed=1, player_moved=player)
    session.add(game_move)
    session.flush()
    print(game_move.player_moved)
    assert game.board_serialization() == [
        ["", "X", "",],
        ["", "", "",],
        ["", "", "",]
    ]
def test_space_occupied(session, user, game):
    player = GamePlayer(user=user, game_id = game.id, marker="X", turn=0)
    assert game.space_occupied(0, 0) == False
    game_move = GameMove(game_id=game.id, row_placed=0, column_placed=1, player_moved=player.id)
    session.add(game_move)
    session.flush()
    assert game.space_occupied(0, 0) == False
    assert game.space_occupied(0, 1) == True

def test_most_recent_move(session, user, game):
    player = GamePlayer(user=user, game_id = game.id, marker="X", turn=0)
    assert game.most_recent_move() == None # no moves yet
    game_move = GameMove(game_id=game.id, row_placed=0, column_placed=1, player_moved=player.id)
    session.add(game_move)
    session.flush()
    assert game.most_recent_move() == game_move

def test_player_turn(session, user, game):
    player1 = GamePlayer(user=user, game_id = game.id, marker="X", turn=0)
    session.add(player1)
    other_user = User()
    session.add(other_user)
    player2 = GamePlayer(user=other_user, game_id = game.id, marker="O", turn=1)
    session.add(player2)
    session.commit()

    assert game.player_turn() == user # player1
    # A move is made
    game_move = GameMove(game_id=game.id, row_placed=0, column_placed=1, player_moved=player1)
    session.add(game_move)
    session.flush()
    # Other's turn
    assert game.player_turn() == other_user
    # Flip back again
    game_move = GameMove(game_id=game.id, row_placed=0, column_placed=1, player_moved=player2)
    session.add(game_move)
    session.flush()

    assert game.player_turn() == user

def test_join_game(session, user, game):
    assert game.status == GameStatus.PENDING_PLAYERS
    other_user = User()
    session.add(other_user)
    session.commit()

    game.join_game(user)
    session.refresh(game)
    assert game.status == GameStatus.PENDING_PLAYERS

    # Same user cannot join the same game twice
    with pytest.raises(UnableToJoinGameException):
        game.join_game(user)

    # Other user joins
    game.join_game(other_user)
    session.refresh(game)
    assert game.status == GameStatus.IN_PROGRESS

    third_user = User()
    session.add(third_user)
    session.commit()
    
    # Max players reached
    with pytest.raises(UnableToJoinGameException):
        game.join_game(third_user)

def test_make_move_exceptions(session, user, game):
    other_user = User()
    session.add(other_user)
    session.commit()

    game.join_game(user)
    session.refresh(game)
    
    # Can't move, game hasn't started
    with pytest.raises(InvalidMoveException):
        game.make_move(user, 0, 0)

    game.join_game(other_user)
    session.refresh(game)

    assert game.status == GameStatus.IN_PROGRESS

    # Can't move, not this user's turn
    with pytest.raises(InvalidMoveException):
        game.make_move(other_user, 0, 0)
    
    with pytest.raises(InvalidMoveException):
        game.make_move(user, 0, -1)

    with pytest.raises(InvalidMoveException):
        game.make_move(user, 3, 3)

    game.make_move(user, 0, 0)

    assert game.board_serialization() == [
        ["X", "", ""],
        ["", "", ""],
        ["", "", ""],
    ]


    