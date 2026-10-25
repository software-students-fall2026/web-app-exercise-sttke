from flask import render_template
from flask import Blueprint

from flask_login import current_user

from helpers import WHERE, db, find_or_404


bp=Blueprint("books",__name__)



def sort_key(note):

    unit=note["unit"] or ""
    number=0

    if unit.isdigit():
        number=int(unit)

    return (WHERE.index(note["scope"]), note["page"] or 0,number, unit)





@bp.route("/")
def home():

    query={"reply_to": None}

    if current_user.is_authenticated:
        query["$or"]=[{"visibility": "shared"}, {"owner_id": current_user.get_id()}]
    else:
        query["visibility"]="shared"


    counts={}
    for note in db.notes.find(query):
        counts[note["book_id"]]=counts.get(note["book_id"], 0)+1


    courses=[]
    for book in db.books.find().sort([("course",1), ("title",1)]):

        book["count"]=counts.get(book["_id"],0)

        if not courses or courses[-1]["course"]!=book["course"]:
            courses.append({"course": book["course"], "books": []})


        courses[-1]["books"].append(book)

    return render_template("index.html", courses=courses)







@bp.route("/books/<book_id>")
def show(book_id):

    book=find_or_404(db.books,book_id)

    query={"book_id":book["_id"]}

    if current_user.is_authenticated:
        query["$or"] = [{"visibility": "shared"},{"owner_id": current_user.get_id()}]
    else:
        query["visibility"] ="shared"


    all_notes=list(db.notes.find(query).sort("created_at", 1))

    shown=[]
    for note in all_notes:
        if note["reply_to"]:
            continue
        note["answers"] = []
        for reply in all_notes:
            if reply["reply_to"] == note["_id"]:
                note["answers"].append(reply)
        shown.append(note)
    shown.sort(key=sort_key)




    by_page=[]
    by_chapter=[]
    for note in shown:
        if note["scope"]=="page":

            if not by_page or by_page[-1]["page"]!=note["page"]:
                by_page.append({"page": note["page"],"notes": []})

            by_page[-1]["notes"].append(note)

        else:
            by_chapter.append(note)



    return render_template("book.html",book=book,by_page=by_page,by_chapter=by_chapter)
