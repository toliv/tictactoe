from tic_tac_toe.utils import lies_on_diagonal, points_on_left_diagonal, points_on_right_diagonal


def test_lies_on_diagonal():
    """
    Test all diagonals
    """
    board_size = 3
    diagonals = [
        [True, False, True],
        [False, True, False],
        [True, False, True],
    ]

    for i in range(len(diagonals)):
        for j in range(len(diagonals[i])):
            assert lies_on_diagonal(i, j, board_size) == diagonals[i][j]

def test_lies_on_diagonal_2():
    """
    Test all diagonals
    """
    board_size = 2
    diagonals = [
        [True, True],
        [True, True],
    ]

    for i in range(len(diagonals)):
        for j in range(len(diagonals[i])):
            assert lies_on_diagonal(i, j, board_size) == diagonals[i][j]

def test_lies_on_diagonal_4():
    """
    Test all diagonals
    """
    board_size = 4
    diagonals = [
        [True, False, False, True],
        [False, True, True, False],
        [False, True, True, False],
        [True, False, False, True],
    ]

    for i in range(len(diagonals)):
        for j in range(len(diagonals[i])):
            assert lies_on_diagonal(i, j, board_size) == diagonals[i][j]

def test_points_on_left_diagonal():
    assert points_on_left_diagonal(3) == [(0, 0), (1, 1), (2, 2)]

def test_points_on_right_diagonal():
    assert points_on_right_diagonal(3) == [(0, 2), (1, 1), (2, 0)]