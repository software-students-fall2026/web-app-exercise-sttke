import os

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

from flask import abort




load_dotenv()
db = MongoClient(os.environ["MONGO_URI"])[os.environ["MONGO_DBNAME"]]



TYPES=["question","correction","translation","argument","summary"]
WHERE=["page","front_matter","chapter","appendix","edition"]

NUMS=[]
for i in range(1, 100):
    NUMS.append(str(i))

LETTERS=list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")







def check_anchor(scope, page, unit, other_ed, book):
    if scope not in WHERE:
        return ["Choose where this note is anchored"]


    errs=[]


    if scope=="page":

        if page is None:
            errs.append("Page must be a whole number from 1 to " + str(book["page_count"]))
        elif page<1 or page>book["page_count"]:
            errs.append("Page must be a whole number from 1 to " + str(book["page_count"]))

        if unit:
            errs.append("A page note does not take a chapter or position")


    elif scope=="chapter":
        if unit not in NUMS:
            errs.append("Chapter must be from 1 to " + str(book["chapter_count"]))
        elif int(unit) > book["chapter_count"]:
            errs.append("Chapter must be from 1 to " + str(book["chapter_count"]))


    elif scope=="appendix":
        if not book["appendices"]:
            errs.append("This book has no appendices")
        elif unit not in LETTERS:
            errs.append("This book only has appendices " + book["appendices"])
        elif unit not in book["appendices"]:
            errs.append("This book only has appendices " + book["appendices"])

    elif scope=="front_matter":
        if unit not in ["preface","contents","notation","inside_cover"]:
            errs.append("A front matter note need one of preface, contents, notation or inside_cover")

    elif scope=="edition":
        if unit not in ["exercise_numbering","page_numbering","notation","figures","appendix_content"]:
            errs.append("An edition note need one of exercise_numbering, page_numbering, notation, figures or appendix_content")

        if not book["edition"]:
            errs.append("This book has no edition, so it cannot take edition notes")
        elif not other_ed.endswith(" ed."):
            errs.append("An edition note needs the edition it is compared with, like 3rd ed.")
        elif other_ed==book["edition"]:
            errs.append("The compared edition cannot be this book's own edition")

    if scope!="edition" and other_ed:
        errs.append("Only edition notes take a compared edition")


    return errs









def find_or_404(col, raw):

    if not ObjectId.is_valid(raw):
        abort(404)

    found=col.find_one({"_id":ObjectId(raw)})


    
    if found is None:
        abort(404)
    return found