import pytest

from tic_tac_toe.models import User


def test_post_model(session):
    user = User()
    session.add(user)
    session.commit()

    assert user.id >= 0
