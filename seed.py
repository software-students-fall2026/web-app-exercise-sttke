
import datetime
import os

from dotenv import load_dotenv
from pymongo import MongoClient



DESK_2H = "Bobst Course Reserves desk, 2-hour loan"
DESK_1D = "Bobst Course Reserves desk, 1-day loan"
DESK_3D = "Bobst Course Reserves desk, 3-day loan"

OWNERS = {
    "Amy": "seed-amy",
    "Jun": "seed-jun",
    "Kai": "seed-kai",
    "Marco": "seed-marco",
    "Priya": "seed-priya",
    "Yuki": "seed-yuki",
}



BOOKS = [
    {"title": "Introduction to Algorithms", "authors": "Cormen, Leiserson, Rivest, Stein", "edition": "4th ed.", "call_number": "QA76.6 .C662 2022", "course": "CSCI-UA 310 Basic Algorithms", "page_count": 1312, "chapter_count": 35, "appendices": "ABCD", "location": DESK_2H},
    {"title": "Computer Systems: A Programmer's Perspective", "authors": "Bryant, O'Hallaron", "edition": "3rd ed.", "call_number": "QA76.5 .B795 2016", "course": "CSCI-UA 201 Computer Systems Organization", "page_count": 1120, "chapter_count": 12, "appendices": "A", "location": DESK_2H},
    {"title": "Operating System Concepts", "authors": "Silberschatz, Galvin, Gagne", "edition": "10th ed.", "call_number": "QA76.76.O63 S5583 2018", "course": "CSCI-UA 202 Operating Systems", "page_count": 1280, "chapter_count": 21, "appendices": "", "location": DESK_2H},
    {"title": "Discrete Mathematics and Its Applications", "authors": "Rosen", "edition": "8th ed.", "call_number": "QA39.3 .R67 2019", "course": "MATH-UA 120 Discrete Mathematics", "page_count": 1120, "chapter_count": 13, "appendices": "", "location": DESK_2H},
    {"title": "Linear Algebra and Its Applications", "authors": "Lay, Lay, McDonald", "edition": "5th ed.", "call_number": "QA184.2 .L39 2016", "course": "MATH-UA 140 Linear Algebra", "page_count": 576, "chapter_count": 7, "appendices": "AB", "location": DESK_2H},
    {"title": "Introduction to Probability", "authors": "Bertsekas, Tsitsiklis", "edition": "2nd ed.", "call_number": "QA273 .B475 2008", "course": "MATH-UA 235 Probability and Statistics", "page_count": 544, "chapter_count": 9, "appendices": "", "location": DESK_2H},
    {"title": "Artificial Intelligence: A Modern Approach", "authors": "Russell, Norvig", "edition": "4th ed.", "call_number": "Q335 .R86 2021", "course": "CSCI-UA 472 Artificial Intelligence", "page_count": 1136, "chapter_count": 28, "appendices": "AB", "location": DESK_2H},
    {"title": "Pattern Recognition and Machine Learning", "authors": "Bishop", "edition": None, "call_number": "Q327 .B57 2006", "course": "CSCI-UA 473 Fundamentals of Machine Learning", "page_count": 738, "chapter_count": 14, "appendices": "ABCDE", "location": DESK_1D},
    {"title": "Software Engineering", "authors": "Sommerville", "edition": "10th ed.", "call_number": "QA76.758 .S657 2016", "course": "CSCI-UA 474 Software Engineering", "page_count": 816, "chapter_count": 25, "appendices": "", "location": DESK_1D},
    {"title": "Psychology", "authors": "Myers, DeWall", "edition": "13th ed.", "call_number": "BF121 .M96 2021", "course": "PSYCH-UA 1 Introduction to Psychology", "page_count": 1000, "chapter_count": 16, "appendices": "", "location": DESK_3D},
    {"title": "Physics for Scientists and Engineers", "authors": "Serway, Jewett", "edition": "10th ed.", "call_number": "QC21.3 .S48 2018", "course": "PHYS-UA 11 General Physics I", "page_count": 1200, "chapter_count": 44, "appendices": "ABC", "location": DESK_2H},
    {"title": "University Physics", "authors": "Young, Freedman", "edition": "15th ed.", "call_number": "QC23 .Y68 2020", "course": "PHYS-UA 12 General Physics II", "page_count": 1500, "chapter_count": 32, "appendices": "AB", "location": DESK_2H},
    {"title": "Calculus: Early Transcendentals", "authors": "Stewart", "edition": "8th ed.", "call_number": "QA303.2 .S74 2016", "course": "MATH-UA 121 Calculus I", "page_count": 1360, "chapter_count": 17, "appendices": "ABC", "location": DESK_2H},
    {"title": "Database System Concepts", "authors": "Silberschatz, Korth, Sudarshan", "edition": "7th ed.", "call_number": "QA76.9.D3 S54 2019", "course": "CSCI-UA 60 Database Systems", "page_count": 1376, "chapter_count": 21, "appendices": "AB", "location": DESK_1D},
    {"title": "Human Anatomy & Physiology", "authors": "Marieb, Hoehn", "edition": "11th ed.", "call_number": "QP34.5 .M37 2018", "course": "BIOL-UA 11 Anatomy and Physiology", "page_count": 1248, "chapter_count": 28, "appendices": "A", "location": DESK_3D},
]




NOTE_TEMPLATES = [
    ("page", 49, None, None, "question", "the definition near the top of the page", "Could we add a small example to make this definition easier to apply?"),
    ("page", 52, None, None, "translation", "the paragraph introducing the main idea", "In simpler words, this paragraph is explaining how the pieces fit together."),
    ("page", 86, None, None, "correction", "the worked example in the middle of the page", "The next step seems to skip an intermediate calculation. It may help to write it out."),
    ("chapter", None, "1", None, "summary", "Chapter 1 as a whole", "This chapter introduces the key terms and the basic method. Review the definitions before moving on."),
    ("front_matter", None, "notation", None, "translation", "the notation table", "Check the notation carefully: similar symbols are used for different concepts in different books."),
]





NOTES = []
for book_index, book in enumerate(BOOKS):
    for template_index, template in enumerate(NOTE_TEMPLATES[:3]):
        scope, page, unit, vs_edition, kind, anchor_desc, body = template
        
        if scope == "page":
            page =min(page + book_index * 3, book["page_count"])
        
        NOTES.append({
            "book": book_index,
            "scope": scope,
            "page": page,
            "unit": unit,
            "vs_edition": vs_edition,
            "kind": kind,
            "owner": list(OWNERS.keys())[(book_index + template_index) % len(OWNERS)],
            "anchor_desc": anchor_desc,
            "body": f"{body} (Sample note for {book['title']})",
        })


for book_index in range(5):
    template_index = 3 + (book_index % 2)
    scope, page, unit, vs_edition, kind, anchor_desc, body = NOTE_TEMPLATES[template_index]
    NOTES.append({
        "book": book_index,
        "scope": scope,
        "page": page,
        "unit": unit,
        "vs_edition": vs_edition,
        "kind": kind,
        "owner": list(OWNERS.keys())[(book_index + template_index + 2) % len(OWNERS)],
        "anchor_desc": anchor_desc,
        "body": f"{body} (Additional sample note for {BOOKS[book_index]['title']})",
    })

REPLIES = [
    {"note": 0, "owner": "Jun", "body": "An example would help. I will add one to my study notes."},
    {"note": 1, "owner": "Amy", "body": "Agreed. Rephrasing it this way made the idea clearer to me."},
    {"note": 5, "owner": "Kai", "body": "I had the same question and found the next section helpful."},
    {"note": 12, "owner": "Priya", "body": "Good point. It is worth comparing this with the definition earlier in the chapter."},
    {"note": 22, "owner": "Marco", "body": "I think this is a useful summary to review before the exam."},
]








def seed_books(db, start):
    book_ids = []
    for index, book in enumerate(BOOKS):
        doc = dict(book)
        doc["created_at"] = start
        doc["seed_key"] = f"annotation-demo-book-{index}"

        result = db.books.insert_one(doc)
        book_ids.append(result.inserted_id)

    return book_ids





def seed_notes(db, start, book_ids):
    note_ids = []
    for index, note in enumerate(NOTES):
        stamp = start + datetime.timedelta(minutes=index + 1)
        doc = {
            "seed_key": f"annotation-demo-note-{index}",
            "book_id": book_ids[note["book"]],
            "scope": note["scope"],
            "page": note["page"],
            "unit": note["unit"],
            "vs_edition": note["vs_edition"],
            "anchor_desc": note["anchor_desc"],
            "kind": note["kind"],
            "body": note["body"],
            "owner_id": OWNERS[note["owner"]],
            "owner_name": note["owner"],
            "visibility": "shared",
            "reply_to": None,
            "created_at": stamp,
            "updated_at": stamp,
        }

        result = db.notes.insert_one(doc)
        note_ids.append(result.inserted_id)
    return note_ids



def seed_replies(db, start, note_ids):

    for index, reply in enumerate(REPLIES):
        parent = db.notes.find_one({"_id": note_ids[reply["note"]]})
        stamp = start +datetime.timedelta(minutes=len(NOTES) + index + 1)
        db.notes.insert_one({
            "seed_key": f"annotation-demo-reply-{index}",
            "book_id": parent["book_id"],
            "scope": None,
            "page":None,
            "unit":None,
            "vs_edition": None,
            "anchor_desc": None,
            "kind": "reply",
            "body": reply["body"],
            "owner_id": OWNERS[reply["owner"]],
            "owner_name": reply["owner"],
            "visibility": "shared",
            "reply_to": parent["_id"],
            "created_at": stamp,
            "updated_at": stamp,
        }
    )














def main():
    load_dotenv()
    mongo_uri =os.getenv("MONGO_URI")
    db_name =os.getenv("MONGO_DBNAME")
    
    if not mongo_uri or not db_name:
        raise RuntimeError("Please set MONGO_URI and MONGO_DBNAME in your .env file.")

    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    
    try:
        client.admin.command("ping")
        db = client[db_name]
        db.books.delete_many({})
        db.notes.delete_many({})

        start = datetime.datetime(2026, 10, 12, 9, 0, tzinfo=datetime.timezone.utc)
        book_ids = seed_books(db, start)
        note_ids = seed_notes(db, start, book_ids)
        seed_replies(db, start, note_ids)

        print("Seed completed successfully.")
        print("Books:", db.books.count_documents({}))
        print("Notes and replies:", db.notes.count_documents({}))
        print("Top-level notes:", db.notes.count_documents({"reply_to": None}))
        print("Replies:", db.notes.count_documents({"kind": "reply"}))
    
    finally:
        client.close()



if __name__ == "__main__":
    main()







