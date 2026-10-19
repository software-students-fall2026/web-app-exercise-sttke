import re

from bson import ObjectId
from bson.errors import InvalidId

from flask import abort, session




KINDS=( "question", "correction", "translation", "argument", "summary" )

SCOPES=( "page", "front_matter", "chapter", "appendix", "edition")

UNIT_RULES ={

    "chapter":r"[1-9][0-9]?",

    "appendix":r"[A-Z]",

    "front_matter":("preface", "contents", "notation", "inside_cover"),


    "edition": (
        "exercise_numbering",
        "page_numbering",
        "notation",
        "figures",
        "appendix_content",
    ),}


UNIT_HELP={

    "chapter":"A chapter note needs one chapter number from 1 to 99",

    "appendix":"An appendix note needs one capital letter",

    "front_matter": (
        "A front matter note need one of preface, contents, notation "
        "or inside_cover"
    ),

    "edition": (
        "An edition note need one of exercise_numbering, page_numbering, "
        "notation, figures or appendix_content"
    ),

}


UNIT_LABELS = {
    "preface":"Preface",
    "contents":"Contents",
    "notation":"Notation",
    "inside_cover":"Inside cover",
    "exercise_numbering": "Exercise numbering",
    "page_numbering": "Page numbering",
    "figures":"Figures",
    "appendix_content": "Appendix content",
}



VS_EDITION_RE=r"[1-9][0-9]?(st|nd|rd|th) ed\."


SCOPE_LABELS = {
    "front_matter": "Front matter",
    "chapter":"Chapter",
    "appendix": "Appendix",
    "edition": "Edition",
}





def natural_key(unit):
    key=[]
    for part in re.findall(r"\d+|\D+", unit or ""):

        if part.isdecimal():
            key.append((0, int(part)))
        else:
            key.append((1, part.lower()))

    return tuple(key)


def unit_key(scope, unit):

    rule=UNIT_RULES.get(scope)
    if isinstance(rule, tuple):

        if unit in rule:
            return ((0, rule.index(unit)),)
        return ((1, ""),)
    
    return natural_key(unit)





def position_key(n):
    return (
        SCOPES.index(n["scope"]),
        n.get("page") or 0,
        unit_key(n["scope"], n.get("unit")),
        n.get("vs_edition") or "",
        n["created_at"],
    )




def unit_errors(scope, unit, book):
    rule=UNIT_RULES[scope]
    if isinstance(rule, tuple):
        ok =unit in rule
    else:
        ok = bool(unit) and re.fullmatch(rule, unit) is not None


    if not ok:
        return [UNIT_HELP[scope]]
    if scope=="chapter" and int(unit) > book["chapter_count"]:
        return [f"Chapter must be from 1 to {book['chapter_count']}"]




    
    if scope =="appendix" and unit not in book["appendices"]:
        if book["appendices"]:
            return [f"This book only has appendices {book['appendices']}"]
        return ["This book has no appendices"]
    return []








def edition_errors(vs_edition, book):

    if book.get("edition") is None:
        return ["This book has no edition, so it cannot take edition notes"]
    
    if not vs_edition or re.fullmatch(VS_EDITION_RE, vs_edition) is None:
        return ["An edition note needs the edition it is compared with, like 3rd ed."]
    
    if vs_edition==book["edition"]:
        return ["The compared edition cannot be this book's own edition"]
    return []








def anchor_errors(scope, page, unit, vs_edition, book):
    if scope not in SCOPES:
        return ["Choose where this note is anchored"]

    
    errors=[]


    if scope=="page":

        if page is None or page<1 or page>book["page_count"]:
            errors.append(f"Page must be a whole number from 1 to {book['page_count']}")

        if unit:
            errors.append("A page note does not take a chapter or position")

    else:
        if page is not None:
            errors.append("Only page notes take a page number")
        errors +=unit_errors(scope, unit, book)

    if scope=="edition":
        errors+=edition_errors(vs_edition,book)
    elif vs_edition:
        errors.append("Only edition notes take a compared edition")


    return errors


def current_owner_id():
    return session.get("reader_id")


def visible_filter():

    oid=current_owner_id()

    if oid is None:
        return {"visibility": "shared"}
    return {"$or": [{"visibility": "shared"},{"owner_id":oid}]}




def get_or_404(collection, id_str):

    try:
        oid=ObjectId(id_str)
    except (InvalidId, TypeError):
        abort(404)

    doc=collection.find_one({"_id":oid})
    
    if doc is None:
        abort(404)
    return doc