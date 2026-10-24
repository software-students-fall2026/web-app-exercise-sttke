from collections import defaultdict

from flask import Blueprint, abort, current_app, render_template, request

from helpers import KINDS, get_or_404, position_key, visible_filter


books_bp = Blueprint("books", __name__)


@books_bp.get("/")
def index():
    books = list(current_app.db.books.find().sort([("course", 1), ("title", 1)]))
    counts = defaultdict(int)
    for note in current_app.db.notes.find({
        "reply_to": None,
        **visible_filter(),
    }, {"book_id": 1}):
        counts[note["book_id"]] += 1

    groups = []
    for book in books:
        book["note_count"] = counts[book["_id"]]
        course = book.get("course") or "Other"
        if not groups or groups[-1]["course"] != course:
            groups.append({"course": course, "books": []})
        groups[-1]["books"].append(book)
    return render_template("index.html", groups=groups)


@books_bp.get("/books/<book_id>")
def book(book_id):
    book_record = get_or_404(current_app.db.books, book_id)
    selected_kind = request.args.get("kind", "").strip()
    if selected_kind and selected_kind not in KINDS:
        abort(400)

    all_notes = list(current_app.db.notes.find({
        "book_id": book_record["_id"],
        **visible_filter(),
    }))
    roots = [note for note in all_notes if not note.get("reply_to")]
    replies = defaultdict(list)
    for note in all_notes:
        if note.get("reply_to"):
            replies[note["reply_to"]].append(note)
    for thread in replies.values():
        thread.sort(key=lambda note: (note["created_at"], str(note["_id"])))

    shown = [note for note in roots if not selected_kind or note.get("kind") == selected_kind]
    for note in shown:
        note["replies"] = replies[note["_id"]] if note.get("visibility") == "shared" else []
    shown.sort(key=position_key)

    return render_template(
        "book.html",
        book=book_record,
        total=len(roots),
        page_notes=[note for note in shown if note.get("scope") == "page"],
        chapter_notes=[note for note in shown if note.get("scope") != "page"],
        kinds=KINDS,
        selected_kind=selected_kind,
    )
