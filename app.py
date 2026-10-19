import os

import uuid

from dotenv import load_dotenv
from flask import Flask, render_template, session
from pymongo import MongoClient

from books import books_bp

from helpers import SCOPE_LABELS,UNIT_LABELS,current_owner_id

from notes import notes_bp
from search import search_bp


def create_app():

    load_dotenv()

    app=Flask(__name__)

    app.config["SECRET_KEY"]=os.environ["SECRET_KEY"]

    app.db = MongoClient(os.environ["MONGO_URI"])[os.environ["MONGO_DBNAME"]]





    app.register_blueprint(books_bp)

    app.register_blueprint(search_bp)

    app.register_blueprint(notes_bp)

    @app.before_request

    def give_reader_id():
        if "reader_id" not in session:
            session["reader_id"] = uuid.uuid4().hex

    @app.context_processor
    
    def template_globals():
        return {
            "current_owner_id":current_owner_id,
            "SCOPE_LABELS":SCOPE_LABELS,
            "UNIT_LABELS":UNIT_LABELS,
        }

    @app.errorhandler(403)

    @app.errorhandler(404)

    def error_page(e):
        return render_template("errors.html",code=e.code),e.code

    return app
