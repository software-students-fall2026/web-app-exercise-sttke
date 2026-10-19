from flask import Blueprint

books_bp = Blueprint("books",__name__)


@books_bp.route("/")


def index():
    return "not yet",501


@books_bp.route("/books/<book_id>")


def book(book_id):
    return "not yet",501
