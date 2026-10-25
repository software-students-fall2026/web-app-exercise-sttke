import os

from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask
from flask import render_template
from flask_login import LoginManager

import auth
import books
import notes
import search
from helpers import db


load_dotenv()

if not os.environ.get("SECRET_KEY"):
    raise RuntimeError("Set SECRET_KEY in .env before starting the app")

app=Flask(__name__)

app.secret_key=os.environ["SECRET_KEY"]


login_manager=LoginManager()
login_manager.login_view="auth.login"
login_manager.login_message=None
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):

    if not ObjectId.is_valid(user_id):
        return None
    
    record=db.users.find_one({"_id":ObjectId(user_id)})

    if record is None:
        return None
    
    return auth.User(record)


app.register_blueprint(auth.bp)

app.register_blueprint(books.bp)

app.register_blueprint(search.bp)

app.register_blueprint(notes.bp)


@app.errorhandler(403)
def err_403(err):
    return render_template("oops.html",code=403),403


@app.errorhandler(404)
def err_404(err):
    return render_template("oops.html",code=404),404
