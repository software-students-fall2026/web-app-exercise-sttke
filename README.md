# Annotation

Annotation is a mobile web application for textbooks on course reserve at Bobst Library. Readers can write their annotation in the webthey and it stays attached to that book, that edition and that page for the next reader.

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
| `MONGO_URI` | The connection string. Atlas: `mongodb+srv://<user>:<password>@<cluster>.mongodb.net/`. Local: `mongodb://localhost:27017` |
| `MONGO_DBNAME` | The database name. Use `annotation` (also the default when the line is missing) |
| `SECRET_KEY` | Any long random string. Flask uses it to sign the session cookie |
| `SEED_PASSWORD` | The password given to the sample accounts created by the seed script |

`.env` is listed in `.gitignore` and must never be committed. Share it through the team channel only.

To run MongoDB locally with Docker instead of Atlas:

```bash
docker run -d --name annotation-mongo -p 27017:27017 mongo:7
```

and set `MONGO_URI=mongodb://localhost:27017`. Without Docker, install MongoDB Community Server from mongodb.com instead; it runs as a service on port 27017 and the same `MONGO_URI` works.

### 4. Load the sample data

```bash
python seed.py
```

This empties the `books` and `notes` collections and inserts a set of course-reserve textbooks with notes and replies, so the app has something to show. Run it again at any time to reset the data.

It also creates six sample accounts, `amy`, `jun`, `kai`, `marco`, `priya` and `yuki`, whose password is the `SEED_PASSWORD` value from `.env`, so you can log in and edit the sample notes. Running the script again keeps these accounts.

### 5. Start the app

```bash
flask --app app run
```

Open http://127.0.0.1:5000 in browser

Log in with one of the sample accounts and the `SEED_PASSWORD` value.
Browsing and searching does not need login; writing, replying, editing, deleting and sharing notes need one.

### For teammates

After cloning, run the course setup script once from the repository root:

```bash
python3 .automations/setup.py
```

On Windows run `python .automations/setup.py`.

Work on a branch, open a pull request against this repository's `main`, and have another team member review and merge it.

## Task boards

- Sprint 1: https://github.com/orgs/software-students-fall2026/projects/48
- Sprint 2: https://github.com/orgs/software-students-fall2026/projects/64
