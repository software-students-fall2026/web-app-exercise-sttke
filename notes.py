from datetime import datetime, timezone


from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from helpers import TYPES, check_anchor, find_or_404, db

bp = Blueprint("notes", __name__)


def read_form():

    form = {}

    for name in ["scope", "page", "unit", "vs_edition", "anchor_desc", "kind", "body"]:

        form[name] = request.form.get(name, "").strip()

    form["owner_name"] = current_user.username

    form["visibility"] = request.form.get("visibility", "shared").strip()

    return form



def form_errors(form, book_doc):
    page = None
    if form["scope"] == "page":
        try:
            page = int(form["page"])
        except ValueError:
            page = None

    unit = form["unit"] or None
    vs_edition = form["vs_edition"] or None

    errors = check_anchor(
        form["scope"],
        page,
        unit,
        vs_edition or "",
        book_doc
    )

    if not form["anchor_desc"]:
        errors.append("Describe the spot in the book")

    if len(form["anchor_desc"]) > 80:
        errors.append("The spot description is too long")

    if form["kind"] not in TYPES:
        errors.append("Choose a valid note type")

    if not form["body"]:
        errors.append("Please enter a note")

    if form["visibility"] not in ("shared", "private"):
        errors.append("Choose a valid visibility option")

    return errors, page, unit, vs_edition



@bp.route("/books/<book_id>/notes/new", methods=["GET", "POST"])
@login_required


def write(book_id):

    book_doc = find_or_404(db.books, book_id)

    form = {
        "scope": "page",
        "page": request.args.get("page", ""),
        "unit": "",
        "vs_edition": "",
        "anchor_desc": "",
        "kind": "question",
        "body": "",
        "owner_name": current_user.username,
        "visibility": "shared"

    }

    errors = []

    if request.method == "POST":

        form = read_form()
        errors, page, unit, vs_edition = form_errors(form, book_doc)

        if not errors:

            now = datetime.now(timezone.utc)

            note = {
                "book_id": book_doc["_id"],
                "scope": form["scope"],
                "page": page,
                "unit": form["unit"],
                "vs_edition": form["vs_edition"],
                "anchor_desc": form["anchor_desc"],
                "kind": form["kind"],
                "body": form["body"],
                "owner_name": current_user.username,
                "owner_id": current_user.get_id(),
                "visibility": form["visibility"],
                "reply_to": None,
                "created_at": now,
                "updated_at": now
            }

            result = db.notes.insert_one(note)

            return redirect(url_for("books.show", book_id=book_id) + "#n-" + str(result.inserted_id))
    return render_template(
        "note_form.html",
        book=book_doc,
        form=form,
        errors=errors

    )




@bp.route("/notes/<note_id>/reply", methods=["GET", "POST"])
@login_required

def answer(note_id):

    note = find_or_404(db.notes, note_id)

    if note["reply_to"] or note["visibility"] != "shared":

        abort(403)

    errors = []

    body = ""

    owner_name = current_user.username

    if request.method == "POST":

        body = request.form.get("body", "").strip()
        owner_name = current_user.username

        if not body:

            errors.append("Please enter a reply")

        if not errors:

            now = datetime.now(timezone.utc)

            reply_doc = {
                "book_id": note["book_id"],
                "reply_to": note["_id"],
                "body": body,
                "owner_id": current_user.get_id(),
                "owner_name": owner_name,
                "visibility": "shared",
                "created_at": now,
                "updated_at": now
            }

            db.notes.insert_one(reply_doc)

            return redirect(url_for("books.show", book_id=note["book_id"]) + "#n-" + str(note["_id"]))

    return render_template("reply.html", note=note, body=body, owner_name=owner_name, errors=errors)






@bp.route("/notes/<note_id>/edit", methods=["GET", "POST"])
@login_required


def change(note_id):

    note = find_or_404(db.notes, note_id)

    if note["owner_id"] != current_user.get_id():

        abort(403)

    form = {

        "body": note["body"],
        "visibility": note["visibility"]
    }

    errors = []

    if request.method == "POST":

        form["body"] = request.form.get("body", "").strip()

        form["visibility"] = request.form.get("visibility", "").strip()


        if not form["body"]:

            errors.append("Please enter a note")

        if form["visibility"] not in ("shared", "private"):

            errors.append("Choose a valid visibility option")

        if note.get("reply_to") and form["visibility"] != "shared":
            errors.append("Replies must stay public")

        if note.get("visibility") == "shared" and form["visibility"] == "private":
            errors.append("A public note cannot be made private again")
        if not errors:

            changes = {
                "body": form["body"],
                "visibility": form["visibility"],
                "updated_at": datetime.now(timezone.utc)
            }

            db.notes.update_one({"_id": note["_id"]}, {"$set": changes})

            return redirect(

                url_for("books.show", book_id=note["book_id"]) + "#n-" + str(note["_id"])
            )


    return render_template(

        "edit_note.html",
        note=note,
        form=form,
        errors=errors
    )





@bp.route("/notes/<note_id>/delete", methods=["GET", "POST"])
@login_required

def remove(note_id):

    note = find_or_404(db.notes, note_id)

    if note["owner_id"] != current_user.get_id():

        abort(403)

    if request.method == "POST":

        db.notes.delete_one({
            "_id": note["_id"],
            "owner_id": current_user.get_id()
        })

        if not note.get("reply_to"):
            db.notes.delete_many({"reply_to": note["_id"]})

        if note.get("reply_to"):
            return redirect(
                url_for(
                    "books.show",
                    book_id=note["book_id"],
                    _anchor="n-" + str(note["reply_to"])
                )
            )
        return redirect(

            url_for("books.show", book_id=note["book_id"])

        )

    return render_template(
        "delete_note.html",
        note=note
    )


@bp.route("/notebook")
@login_required

def my_notes():
    notes = list(db.notes.find({"owner_id": current_user.get_id(), "reply_to": None}).sort("created_at", -1))
    names = {book["_id"]: book["title"] for book in db.books.find(
        {"_id": {"$in": [note["book_id"] for note in notes]}})}
    for note in notes:
        note["book_name"] = names.get(note["book_id"], "Unknown book")
    return render_template("notebook.html", notes=notes)


@bp.route("/notes/<note_id>/share",methods=["POST"])
@login_required

def publish(note_id):
    note = find_or_404(db.notes, note_id)
    if note.get("owner_id") != current_user.get_id():
        abort(403)
    if note.get("reply_to"):
        abort(400)
    if note.get("visibility") == "private":
        db.notes.update_one(
            {"_id": note["_id"], "owner_id": current_user.get_id(), "visibility": "private"},
            {"$set": {"visibility": "shared", "updated_at": datetime.now(timezone.utc)}}
        )
    return redirect(url_for("notes.my_notes", _anchor="n-" + str(note["_id"])))
