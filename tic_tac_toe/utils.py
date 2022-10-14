def lies_on_left_diagonal(x_coordinate, y_coordinate, board_size=3):
    return x_coordinate == y_coordinate


def lies_on_right_diagonal(x_coordinate, y_coordinate, board_size=3):
    top_right_x = 0
    top_right_y = board_size - 1
    if top_right_x == x_coordinate and top_right_y == y_coordinate:
        return True
    elif top_right_y == y_coordinate:
        return False
    elif top_right_x == x_coordinate:
        return False

    # Since the array is inverted, this is technically a -1 slope
    return ((top_right_y - y_coordinate) / (top_right_x - x_coordinate)) == -1


def lies_on_diagonal(x_coordinate, y_coordinate, board_size=3):
    return lies_on_left_diagonal(
        x_coordinate, y_coordinate, board_size
    ) or lies_on_right_diagonal(x_coordinate, y_coordinate, board_size)


def points_on_left_diagonal(board_size=3):
    return [(i, i) for i in range(board_size)]


def points_on_right_diagonal(board_size=3):
    return list(enumerate([i for i in reversed(range(board_size))]))
