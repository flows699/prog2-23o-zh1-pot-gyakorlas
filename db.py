from main import get_db, app
from flask import current_app


def init_db():
    with app.app_context():
        db = get_db()
        with current_app.open_resource("schema.sql") as f:
            db.executescript(f.read().decode("utf8"))


init_db()