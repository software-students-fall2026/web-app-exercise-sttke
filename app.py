import os

from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, current_app, render_template
from flask_login import LoginManager
from pymongo import MongoClient

from auth import User, auth_bp
from books import books_bp
from helpers import SCOPE_LABELS, UNIT_LABELS, current_owner_id
from notes import notes_bp
from search import search_bp


login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    if not ObjectId.is_valid(user_id):
        return None
    record = current_app.db.users.find_one({"_id": ObjectId(user_id)})
    return User(record) if record else None


def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        MONGO_URI=os.environ.get("MONGO_URI"),
        MONGO_DBNAME=os.environ.get("MONGO_DBNAME", "annotation"),
    )
    if test_config:
        app.config.update(test_config)

    if not app.config["SECRET_KEY"] or not app.config["MONGO_URI"]:
        raise RuntimeError("Set SECRET_KEY and MONGO_URI in .env before starting the app")

    app.db = MongoClient(app.config["MONGO_URI"])[app.config["MONGO_DBNAME"]]
    login_manager.init_app(app)

    for blueprint in (auth_bp, books_bp, search_bp, notes_bp):
        app.register_blueprint(blueprint)

    @app.context_processor
    def template_globals():
        return {
            "current_owner_id": current_owner_id,
            "SCOPE_LABELS": SCOPE_LABELS,
            "UNIT_LABELS": UNIT_LABELS,
        }

    @app.errorhandler(403)
    @app.errorhandler(404)
    def error_page(error):
        return render_template("errors.html", code=error.code), error.code

    return app
