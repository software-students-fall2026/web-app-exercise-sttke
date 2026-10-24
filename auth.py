import re
from urllib.parse import urlsplit

from flask import Blueprint, current_app, redirect, render_template, request, url_for
from flask_login import UserMixin, current_user, login_required, login_user, logout_user
from pymongo.errors import DuplicateKeyError
from werkzeug.security import check_password_hash, generate_password_hash


auth_bp = Blueprint("auth", __name__)
USERNAME_PATTERN = re.compile(r"[A-Za-z0-9_]{3,30}\Z")


class User(UserMixin):
    def __init__(self, record):
        self.id = str(record["_id"])
        self.username = record["username"]


def next_page():
    destination = request.args.get("next", "")
    parsed = urlsplit(destination)
    if destination.startswith("/") and not destination.startswith("//") and not parsed.netloc and "\\" not in destination:
        return destination
    return url_for("books.index")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("books.index"))

    username = request.form.get("username", "").strip()
    errors = []
    if request.method == "POST":
        password = request.form.get("password", "")
        if not USERNAME_PATTERN.fullmatch(username):
            errors.append("Use 3–30 letters, numbers, or underscores for your username.")
        if len(password) < 8:
            errors.append("Use a password with at least 8 characters.")
        if password != request.form.get("confirm_password", ""):
            errors.append("The passwords do not match.")

        if not errors:
            users = current_app.db.users
            users.create_index("username_key", unique=True)
            try:
                result = users.insert_one({
                    "username": username,
                    "username_key": username.casefold(),
                    "password_hash": generate_password_hash(password),
                })
            except DuplicateKeyError:
                errors.append("That username is already taken.")
            else:
                login_user(User({"_id": result.inserted_id, "username": username}))
                return redirect(next_page())

    return render_template("register.html", username=username, errors=errors)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("books.index"))

    username = request.form.get("username", "").strip()
    errors = []
    if request.method == "POST":
        user = current_app.db.users.find_one({"username_key": username.casefold()})
        password = request.form.get("password", "")
        if user is None or not check_password_hash(user["password_hash"], password):
            errors.append("Check your username and password, then try again.")
        else:
            login_user(User(user))
            return redirect(next_page())

    return render_template("login.html", username=username, errors=errors)


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("books.index"))
