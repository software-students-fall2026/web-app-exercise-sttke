import os

import uuid

from dotenv import load_dotenv
from flask import Flask
from flask import render_template
from flask import session

import books

import notes
import search


load_dotenv()

app=Flask(__name__)

app.secret_key=os.environ["SECRET_KEY"]





app.register_blueprint(books.bp)

app.register_blueprint(search.bp)

app.register_blueprint(notes.bp)





@app.before_request
def set_readerid():
    if "rid" not in session:
        session["rid"]=str(uuid.uuid4())

        session.permanent=True




@app.errorhandler(403)
def err_403(err):
    return render_template("oops.html",code=403),403




@app.errorhandler(404)
def err_404(err):
    return render_template("oops.html",code=404),404
