from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import UserMixin, current_user, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import db


bp=Blueprint("auth",__name__)



class User(UserMixin):
    def __init__(self,record):
        self.id=str(record["_id"])
        self.username=record["username"]



def next_page():

    back=request.args.get("next", "")

    if back.startswith("/") and not back.startswith("//") and "\\" not in back and "\r" not in back and "\n" not in back:
        return back
    
    return url_for("books.home")




@bp.route("/register",methods=["GET","POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("books.home"))

    username=request.form.get("username","").strip()

    errors =[]
    if request.method=="POST":
        password=request.form.get("password","")

        if len(username)<3 or len(username)>30 or not username.replace("_","").isalnum():
            errors.append("Use 3-30 letters, numbers, or underscores for your username.")

        if len(password)<8:
            errors.append("Use a password with at least 8 characters.")

        if password!=request.form.get("confirm_password",""):
            errors.append("The passwords do not match.")

        if db.users.find_one({"username_key": username.lower()}) is not None:
            errors.append("That username is already taken.")


        if not errors:
            user={"username":username,"username_key":username.lower(),"password_hash":generate_password_hash(password)}

            db.users.insert_one(user)


            login_user(User(user))
            return redirect(next_page())

    return render_template("register.html",form={"username":username},errors=errors)






@bp.route("/login",methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("books.home"))

    username =request.form.get("username","").strip()
    errors =[]

    if request.method=="POST":
        user=db.users.find_one({"username_key":username.lower()})

        password=request.form.get("password","")

        if user is None or not check_password_hash(user["password_hash"],password):
            errors.append("Check your username and password, then try again.")
        else:
            login_user(User(user))
            return redirect(next_page())

    return render_template("login.html",form={"username":username},errors=errors)




@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("books.home"))
