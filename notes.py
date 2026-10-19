from flask import Blueprint

notes_bp = Blueprint("notes",__name__)


@notes_bp.route("/books/<book_id>/notes/new",methods=["GET","POST"])


def new(book_id):
    return "not yet",501


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
