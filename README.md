# Annotation

Annotation is a mobile web application for textbooks on course reserve at Bobst Library. Readers can write their annotation in the web and it stays attached to that book, that edition and that page for the next reader.

## Product vision statement

Write it here, not in the book: a shared margin for library textbooks, where readers can leave notes on a specific page.

## Screens

- Books (`/`): the textbooks grouped by course with their number of notes.
- Book page (`/books/<id>`): notes by page and by chapter or edition, replies under each note, and a box to start writing on a page.
- Search (`/search`): books by title, author, course or call number, and notes by their text.
- Write note, reply note, edit note, delete note (with confirmation page) (need login).
- My Notebook (`/notebook`): your own notes and replies, private drafts first, with a Share button to make a draft public.
- Register, login, logout.

## User stories

User stories:
https://github.com/software-students-fall2026/web-app-exercise-sttke/issues?q=label%3A%22user+story%22

All issues:
https://github.com/software-students-fall2026/web-app-exercise-sttke/issues

## Steps necessary to run the software

### What you need

- Python 3.11 or newer
- A MongoDB database with Atlas cluster.

### 1. Clone the repository

```bash
git clone https://github.com/software-students-fall2026/web-app-exercise-sttke.git
cd web-app-exercise-sttke
```

### 2. Create a virtual environment and install the dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, use `python` and activate `source .venv/Scripts/activate`

### 3. Configure the database connection

Copy the example file and fill in the values:

```bash
cp env.example .env
```

| Variable | What to put there |
|---|---|
| `MONGO_URI` | Connection string. Atlas: `mongodb+srv://<user>:<password>@<cluster>.mongodb.net/` |
| `MONGO_DBNAME` | Database name |
| `SECRET_KEY` | Any long random string |
| `SEED_PASSWORD` | Password for sample accounts |


### 4. Load the sample data

```bash
python seed.py
```

This empties the `books` and `notes` collections and inserts a set of textbooks with notes and replies so the app has something to show. Run it again at any time to reset the data.

It also creates six sample accounts: `amy`, `jun`, `kai`, `marco`, `priya`, `yuki` with password variable `SEED_PASSWORD`

### 5. Start the app

```bash
flask --app app run
```

Open http://127.0.0.1:5000 in browser

Log in with sample accounts and `SEED_PASSWORD` value.
Browsing and searching does not need login; writing, replying, editing, deleting and sharing notes need one.

## Task boards

- Sprint 1: https://github.com/orgs/software-students-fall2026/projects/48
- Sprint 2: https://github.com/orgs/software-students-fall2026/projects/64
