from flask import Flask


def create_app(name=None, settings_override=None):
    n = name or __name__
    app = Flask(n)
    app.config.from_object("tic_tac_toe.config.Config")
    if settings_override:
        app.config.update(settings_override)

    from tic_tac_toe.database import db
    db.init_app(app)
    return app