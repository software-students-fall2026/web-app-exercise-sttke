import os

import uuid

from dotenv import load_dotenv
from flask import Flask, render_template, session
from pymongo import MongoClient

import books

from helpers import LABELS,reader_id

import notes
import search


def create_app():

    load_dotenv()

    app=Flask(__name__)

    app.config["SECRET_KEY"]=os.environ["SECRET_KEY"]

    app.db = MongoClient(os.environ["MONGO_URI"])[os.environ["MONGO_DBNAME"]]





    app.register_blueprint(books.bp)

    app.register_blueprint(search.bp)

    app.register_blueprint(notes.bp)





    @app.before_request
    def set_readerid():
        if "rid" not in session:
            session["rid"] = str(uuid.uuid4())

    app.jinja_env.globals.update(reader_id=reader_id,LABELS=LABELS)




    @app.errorhandler(403)
    def err_403(err):
        return render_template("oops.html",code=403),403




    @app.errorhandler(404)
    def err_404(err):
        return render_template("oops.html",code=404),404

    return app
