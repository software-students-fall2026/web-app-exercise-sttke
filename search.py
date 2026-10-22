from flask import Blueprint
bp=Blueprint("search",__name__)





@bp.route("/search")
def search():
    return "not yet",501
