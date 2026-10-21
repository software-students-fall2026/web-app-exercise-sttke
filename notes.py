import datetime

from flask import Blueprint, current_app, redirect, render_template, request, url_for

from helpers import KINDS, anchor_errors, current_owner_id, get_or_404

notes_bp = Blueprint("notes", __name__)


def read_form():

    form = {}

    for name in ["scope", "page", "unit", "vs_edition", "anchor_desc", "kind", "body"]:

        form[name] = request.form.get(name, "").strip()

    form["owner_name"] = request.form.get("owner_name", "").strip()

    form["visibility"] = request.form.get("visibility", "shared").strip()

    return form



def form_errors(form, book_doc):

    page = None

    if form["page"]:

        if form["page"].isdecimal():

            page = int(form["page"])


        else:
            page = 0

    unit = form["unit"] or None

    vs_edition = form["vs_edition"] or None

    errors = anchor_errors(
        form["scope"],
        page,
        unit,
        vs_edition,
        book_doc
    )

    if not form["anchor_desc"]:

        errors.append("Describe the spot in the book")

    if form["kind"] not in KINDS:

        errors.append("Choose a valid note type")

    if not form["body"]:

        errors.append("Please enter a note")

    if not form["owner_name"]:

        errors.append("Please enter your name")

    if len(form["owner_name"]) > 40:


        errors.append("Your name is too long")

    if form["visibility"] not in ("shared", "private"):

        errors.append("Choose a valid visibility option")

    return errors, page, unit, vs_edition




@notes_bp.route("/books/<book_id>/notes/new", methods=["GET", "POST"])


def new(book_id):

    book_doc = get_or_404(current_app.db.books, book_id)

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

        form = read_form()

        errors, page, unit, vs_edition = form_errors(form, book_doc)

        if not errors:

            note = {
                "book_id": book_doc["_id"],
                "scope": form["scope"],
                "page": page,
                "unit": unit,
                "vs_edition": vs_edition,
                "anchor_desc": form["anchor_desc"],
                "kind": form["kind"],
                "body": form["body"],
                "owner_name": form["owner_name"],
                "owner_id": current_owner_id(),
                "visibility": form["visibility"],
                "reply_to": None,
                "created_at": datetime.datetime.now(datetime.timezone.utc)
            }

            current_app.db.notes.insert_one(note)

            return redirect(url_for("books.book", book_id=book_id))
    return render_template(
        "note_form.html",
        book=book_doc,
        form=form,
        errors=errors,
        kinds=KINDS

    )



@notes_bp.route("/notes/<note_id>")
def detail(note_id):
    return "not yet",501



@notes_bp.route("/notes/<note_id>/reply",methods=["GET", "POST"])
def reply(note_id):
    return "not yet",501




@notes_bp.route("/notes/<note_id>/edit",methods=["GET", "POST"])
def edit(note_id):
    return "not yet",501



@notes_bp.route("/notes/<note_id>/delete",methods=["GET", "POST"])
def delete(note_id):
    return "not yet",501


@notes_bp.route("/notebook")

def notebook():
    return "not yet",501


@notes_bp.route("/notes/<note_id>/share",methods=["POST"])

def share(note_id):
    return "not yet",501
