from datetime import datetime, timezone
import re

from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from helpers import KINDS, anchor_errors, current_owner_id, get_or_404


notes_bp = Blueprint("notes", __name__)
VISIBILITIES = ("shared", "private")
FORM_FIELDS = ("scope", "page", "unit", "vs_edition", "anchor_desc", "kind", "body", "visibility")


def form_values():
    return {field: request.form.get(field, "").strip() for field in FORM_FIELDS}


def valid_new_note(form, book):
    raw_page = form["page"]
    if not raw_page:
        page = None
    elif re.fullmatch(r"[0-9]{1,9}", raw_page):
        page = int(raw_page)
    else:
        page = 0
    unit = form["unit"] or None
    compared_edition = form["vs_edition"] or None
    errors = anchor_errors(form["scope"], page, unit, compared_edition, book)

    if not form["anchor_desc"]:
        errors.append("Describe the exact spot in the book.")
    elif len(form["anchor_desc"]) > 80:
        errors.append("Keep the location under 80 characters.")
    if form["kind"] not in KINDS:
        errors.append("Choose a note type.")
    errors.extend(body_errors(form["body"]))
    if form["visibility"] not in VISIBILITIES:
        errors.append("Choose public or private visibility.")
    return errors, page, unit, compared_edition


def body_errors(body):
    if not body:
        return ["Write something before saving."]
    if len(body) > 2000:
        return ["Keep your note under 2,000 characters."]
    return []


def owned_note(note_id):
    note = get_or_404(current_app.db.notes, note_id)
    if note.get("owner_id") != current_owner_id():
        abort(403)
    return note


def book_link(note, anchor=None):
    target = anchor or note["_id"]
    return url_for("books.book", book_id=note["book_id"], _anchor=f"note-{target}")


@notes_bp.route("/books/<book_id>/notes/new", methods=["GET", "POST"])
@login_required
def new(book_id):
    book = get_or_404(current_app.db.books, book_id)
    form = {
        "scope": "page", "page": request.args.get("page", ""), "unit": "",
        "vs_edition": "", "anchor_desc": "", "kind": KINDS[0],
        "body": "", "visibility": "shared",
    }
    errors = []
    if request.method == "POST":
        form = form_values()
        errors, page, unit, compared_edition = valid_new_note(form, book)
        if not errors:
            now = datetime.now(timezone.utc)
            note = {
                "book_id": book["_id"], "scope": form["scope"], "page": page,
                "unit": unit, "vs_edition": compared_edition,
                "anchor_desc": form["anchor_desc"], "kind": form["kind"],
                "body": form["body"], "visibility": form["visibility"],
                "owner_id": current_owner_id(), "owner_name": current_user.username,
                "reply_to": None, "created_at": now, "updated_at": now,
            }
            result = current_app.db.notes.insert_one(note)
            return redirect(book_link(note, result.inserted_id))

    return render_template("note_form.html", book=book, form=form, errors=errors, kinds=KINDS)


@notes_bp.get("/notes/<note_id>")
def detail(note_id):
    note = get_or_404(current_app.db.notes, note_id)
    if note.get("visibility") != "shared" and note.get("owner_id") != current_owner_id():
        abort(404)
    return redirect(book_link(note, note.get("reply_to") or note["_id"]))


@notes_bp.route("/notes/<note_id>/reply", methods=["GET", "POST"])
@login_required
def reply(note_id):
    parent = get_or_404(current_app.db.notes, note_id)
    if parent.get("reply_to") or parent.get("visibility") != "shared":
        abort(404)

    body = request.form.get("body", "").strip() if request.method == "POST" else ""
    errors = body_errors(body) if request.method == "POST" else []
    if request.method == "POST" and not errors:
        now = datetime.now(timezone.utc)
        reply_note = {
            "book_id": parent["book_id"], "scope": parent["scope"],
            "page": parent.get("page"), "unit": parent.get("unit"),
            "vs_edition": parent.get("vs_edition"),
            "anchor_desc": parent.get("anchor_desc"), "kind": parent.get("kind"),
            "body": body, "visibility": "shared", "reply_to": parent["_id"],
            "owner_id": current_owner_id(), "owner_name": current_user.username,
            "created_at": now, "updated_at": now,
        }
        current_app.db.notes.insert_one(reply_note)
        return redirect(book_link(parent))
    return render_template("reply.html", note=parent, body=body, errors=errors)


@notes_bp.route("/notes/<note_id>/edit", methods=["GET", "POST"])
@login_required
def edit(note_id):
    note = owned_note(note_id)
    body = note["body"]
    visibility = note.get("visibility", "shared")
    errors = []
    if request.method == "POST":
        body = request.form.get("body", "").strip()
        errors = body_errors(body)
        if not note.get("reply_to"):
            visibility = request.form.get("visibility", "").strip()
            if visibility not in VISIBILITIES:
                errors.append("Choose public or private visibility.")
            if note.get("visibility") == "shared" and visibility == "private":
                errors.append("A shared note cannot become private again.")

        if not errors:
            changes = {"body": body, "updated_at": datetime.now(timezone.utc)}
            if not note.get("reply_to"):
                changes["visibility"] = visibility
            current_app.db.notes.update_one(
                {"_id": note["_id"], "owner_id": current_owner_id()},
                {"$set": changes},
            )
            return redirect(book_link(note, note.get("reply_to") or note["_id"]))

    return render_template("edit_note.html", note=note, body=body,
                           visibility=visibility, errors=errors)


@notes_bp.route("/notes/<note_id>/delete", methods=["GET", "POST"])
@login_required
def delete(note_id):
    note = owned_note(note_id)
    if request.method == "POST":
        result = current_app.db.notes.delete_one({
            "_id": note["_id"], "owner_id": current_owner_id(),
        })
        if result.deleted_count and not note.get("reply_to"):
            current_app.db.notes.delete_many({"reply_to": note["_id"]})
        return redirect(url_for("books.book", book_id=note["book_id"]))
    return render_template("delete_note.html", note=note)


@notes_bp.get("/notebook")
@login_required
def notebook():
    notes = list(current_app.db.notes.find({
        "owner_id": current_owner_id(), "reply_to": None,
    }).sort("created_at", -1))
    book_ids = {note["book_id"] for note in notes}
    titles = {
        book["_id"]: book["title"]
        for book in current_app.db.books.find({"_id": {"$in": list(book_ids)}})
    }
    for note in notes:
        note["book_title"] = titles.get(note["book_id"], "Unknown book")
    return render_template("notebook.html", notes=notes)


@notes_bp.post("/notes/<note_id>/share")
@login_required
def share(note_id):
    note = owned_note(note_id)
    if note.get("reply_to"):
        abort(400)
    current_app.db.notes.update_one(
        {"_id": note["_id"], "owner_id": current_owner_id(), "visibility": "private"},
        {"$set": {"visibility": "shared", "updated_at": datetime.now(timezone.utc)}},
    )
    return redirect(url_for("notes.notebook", _anchor=f"note-{note['_id']}"))
