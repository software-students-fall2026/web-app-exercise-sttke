from flask import Blueprint
bp=Blueprint("books",__name__)


@bp.route("/")
def home():
    return "not yet",501


@bp.route("/books/<book_id>")
def show(book_id):
    return "not yet",501
