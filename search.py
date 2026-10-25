import re

from flask import Blueprint
from flask import render_template
from flask import request

from flask_login import current_user

from helpers import db

bp=Blueprint("search",__name__)


@bp.route("/search")
def search():

    q=(request.args.get("q") or "").strip()

    books=[]
    notes=[]
    if q:
        pattern={"$regex": re.escape(q), "$options": "i"}

        books =list(db.books.find({"$or":[{"title": pattern},{"authors": pattern},{"course": pattern},{"call_number": pattern}]}).sort([("course", 1),("title",1)]))



        if current_user.is_authenticated:
            who={"$or": [{"visibility":"shared"},{"owner_id":current_user.get_id()}]}
        else:
            who ={"visibility":"shared"}



        what={"$or":[{"body":pattern},{"anchor_desc":pattern}]}
        notes=list(db.notes.find({"$and":[who, what]}).sort("created_at", -1))



        names={}
        for book in db.books.find({"_id":{"$in":[note["book_id"] for note in notes]}}):
            names[book["_id"]]=book["title"]


        for note in notes:
            note["book_name"]=names.get(note["book_id"],"Unknown book")

    return render_template("search.html",q=q,books=books, notes=notes)
