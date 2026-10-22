from datetime import datetime, timezone


from flask import Blueprint, abort, redirect, render_template, request, session, url_for

from helpers import TYPES, check_anchor, find_or_404, db

bp = Blueprint("notes", __name__)


@bp.route("/books/<book_id>/notes/new", methods=["GET", "POST"])


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
        "owner_name": "",
        "visibility": "shared"

    }

    errors = []

    if request.method == "POST":

        for name in ["scope", "page", "unit", "vs_edition", "anchor_desc", "kind", "body", "owner_name", "visibility"]:

            form[name] = request.form.get(name, "").strip()

        page = None

        if form["scope"] == "page":

            try:

                page = int(form["page"])


            except ValueError:
                page = None

        errors = check_anchor(form["scope"], page, form["unit"], form["vs_edition"], book_doc)

        if not form["anchor_desc"]:

            errors.append("Describe the spot in the book")

        if len(form["anchor_desc"]) > 80:

            errors.append("The spot description is too long")

        if form["kind"] not in TYPES:

            errors.append("Choose a valid note type")

        if not form["body"]:

            errors.append("Please enter a note")

        if not form["owner_name"]:

            errors.append("Please enter your name")

        if len(form["owner_name"]) > 40:

            errors.append("Your name is too long")

        if form["visibility"] not in ("shared", "private"):

            errors.append("Choose a valid visibility option")

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
                "owner_name": form["owner_name"],
                "owner_id": session["rid"],
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

def answer(note_id):

    note = find_or_404(db.notes, note_id)

    if note["reply_to"] or note["visibility"] != "shared":

        abort(403)

    errors = []

    body = ""

    owner_name = ""

    if request.method == "POST":

        body = request.form.get("body", "").strip()
        owner_name = request.form.get("owner_name", "").strip()

        if not body:

            errors.append("Please enter a reply")

        if not owner_name:
            errors.append("Please enter your name")

        if len(owner_name) > 40:
            errors.append("Your name is too long")

        if not errors:

            now = datetime.now(timezone.utc)

            reply_doc = {
                "book_id": note["book_id"],
                "reply_to": note["_id"],
                "body": body,
                "owner_id": session["rid"],
                "owner_name": owner_name,
                "visibility": "shared",
                "created_at": now,
                "updated_at": now
            }

            db.notes.insert_one(reply_doc)

            return redirect(url_for("books.show", book_id=note["book_id"]) + "#n-" + str(note["_id"]))

    return render_template("reply.html", note=note, body=body, owner_name=owner_name, errors=errors)






@bp.route("/notes/<note_id>/edit", methods=["GET", "POST"])


def change(note_id):

    note = find_or_404(db.notes, note_id)

    if note["owner_id"] != session["rid"]:

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

        if note["visibility"] == "shared" and form["visibility"] == "private":

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

def remove(note_id):

    note = find_or_404(db.notes, note_id)

    if note["owner_id"] != session["rid"]:

        abort(403)

    if request.method == "POST":

        db.notes.delete_one({"_id": note["_id"]})

        db.notes.delete_many({"reply_to": note["_id"]})

        if note["reply_to"]:

            return redirect(url_for("books.show", book_id=note["book_id"]) + "#n-" + str(note["reply_to"]))

        return redirect(

            url_for("books.show", book_id=note["book_id"])

        )

    return render_template(
        "delete_note.html",
        note=note
    )


@bp.route("/notebook")

def my_notes():
    return "not yet",501


@bp.route("/notes/<note_id>/share",methods=["POST"])

def publish(note_id):
    return "not yet",501
