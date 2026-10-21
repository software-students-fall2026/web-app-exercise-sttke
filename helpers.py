from bson import ObjectId

from flask import abort, session




TYPES=["question","correction","translation","argument","summary"]

WHERE=["page","front_matter","chapter","appendix","edition"]

NUMS=[str(i) for i in range(1, 100)]

RULES ={

    "front_matter":["preface","contents","notation","inside_cover"],


    "edition": 
    [
        "exercise_numbering",
        "page_numbering",
        "notation",
        "figures",
        "appendix_content",
    ],
    }


HELP={

    "chapter":"A chapter note needs one chapter number from 1 to 99",
    "appendix":"An appendix note needs one capital letter",



    "front_matter": 
    (
        "A front matter note need one of preface, contents, notation "
        "or inside_cover"
    ),

    "edition": 
    (
        "An edition note need one of exercise_numbering, page_numbering, "
        "notation, figures or appendix_content"
    ),

}


LABELS = {
    "preface":"Preface",
    "contents":"Contents",
    "notation":"Notation",
    "inside_cover":"Inside cover",
    "exercise_numbering": "Exercise numbering",
    "page_numbering": "Page numbering",
    "figures":"Figures",
    "appendix_content": "Appendix content",
}







def check_unit(scope, unit, book):
    if scope=="chapter":
        valid =unit in NUMS
    elif scope=="appendix":
        valid = bool(unit) and len(unit)==1 and "A" <= unit <= "Z"
    else:
        valid = unit in RULES[scope]


    if not valid:
        return [HELP[scope]]
    if scope=="chapter" and int(unit) > book["chapter_count"]:
        return ["Chapter must be from 1 to " + str(book["chapter_count"])]




    
    if scope =="appendix" and unit not in book["appendices"]:
        if book["appendices"]:
            return ["This book only has appendices " + book["appendices"]]
        return ["This book has no appendices"]
    return []








def check_edition(other_ed, book):

    if book.get("edition") is None:
        return ["This book has no edition, so it cannot take edition notes"]
    
    valid=False
    if other_ed and other_ed.endswith(" ed."):
        head=other_ed[:-4]
        if head[:-2] in NUMS and head[-2:] in ["st", "nd", "rd", "th"]:
            valid=True


    if not valid:
        return ["An edition note needs the edition it is compared with, like 3rd ed."]

    
    if other_ed==book["edition"]:
        return ["The compared edition cannot be this book's own edition"]
    return []








def check_anchor(scope, page, unit, other_ed, book):
    if scope not in WHERE:
        return ["Choose where this note is anchored"]

    
    errs=[]


    if scope=="page":

        if page is None or page<1 or page>book["page_count"]:
            errs.append("Page must be a whole number from 1 to " + str(book["page_count"]))

        if unit:
            errs.append("A page note does not take a chapter or position")

    else:
        if page is not None:
            errs.append("Only page notes take a page number")
        errs.extend(check_unit(scope, unit, book))

    if scope=="edition":
        errs.extend(check_edition(other_ed,book))
    elif other_ed:
        errs.append("Only edition notes take a compared edition")


    return errs


def reader_id():
    return session.get("rid")









def find_or_404(col, raw):

    if not ObjectId.is_valid(raw):
        abort(404)

    found=col.find_one({"_id":ObjectId(raw)})


    
    if found is None:
        abort(404)
    return found