class InvalidMoveException(Exception):
    msg: str

    def __init__(self, msg):
        self.msg = msg

class UnableToJoinGameException(Exception):
    msg: str

    def __init__(self, msg):
        self.msg = msg