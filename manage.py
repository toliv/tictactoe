from venv import create
from flask.cli import FlaskGroup
from flask import current_app

from tic_tac_toe.models import User
from tic_tac_toe.database import db
from tic_tac_toe.factory import create_app


cli = FlaskGroup(create_app=create_app)


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command("seed_db")
def seed_db():
    db.session.add(User(email="michael@mherman.org"))
    db.session.commit()

if __name__ == "__main__":
    cli()
