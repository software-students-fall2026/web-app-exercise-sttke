# Annotation

Annotation is a mobile web app for textbooks on course reserve at Bobst Library. Readers write the note they wish they could leave in the margin, and it stays attached to that book, that edition and that page for the next reader.

## Product vision statement

Write it here, not in the book: a shared margin for library textbooks, where readers can leave notes on a specific page or chapter of a particular edition.

## User stories

User stories are tracked as issues with the `user story` label:
https://github.com/software-students-fall2026/web-app-exercise-sttke/issues?q=label%3A%22user+story%22

All issues, including tasks and spikes:
https://github.com/software-students-fall2026/web-app-exercise-sttke/issues

## Steps necessary to run the software

### What you need

- Python 3.10 or newer
- A MongoDB database. Either use the team's Atlas cluster (ask in the team channel for the `.env` values) or run MongoDB locally (see step 3).

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

On Windows, activate with `.venv\Scripts\activate` instead of the `source` line.

### 3. Configure the database connection

Copy the example file and fill in the values:

```bash
cp env.example .env
```

| Variable | What to put there |
|---|---|
| `MONGO_URI` | The connection string. Atlas: `mongodb+srv://<user>:<password>@<cluster>.mongodb.net/`. Local: `mongodb://localhost:27017` |
| `MONGO_DBNAME` | The database name. Use `annotation` |
| `SECRET_KEY` | Any long random string. Flask uses it to sign the session cookie |
| `SEED_PASSWORD` | The password given to the sample accounts created by the seed script |

`.env` is listed in `.gitignore` and must never be committed. Share it through the team channel only.

To run MongoDB locally with Docker instead of Atlas:

```bash
docker run -d --name annotation-mongo -p 27017:27017 mongo:7
```

and set `MONGO_URI=mongodb://localhost:27017`.

### 4. Load the sample data

```bash
python seed.py
```

This empties the `books` and `notes` collections and inserts a set of course-reserve textbooks with notes and replies, so the app has something to show. Run it again at any time to reset the data.

### 5. Start the app

```bash
flask --app app run
```

Open http://127.0.0.1:5000 in a browser. The layout is designed for a phone, so use the browser's device toolbar (about 390px wide) or a narrow window. If port 5000 is already taken (on macOS it is often used by AirPlay Receiver), add `--port 5001` and open http://127.0.0.1:5001 instead.

### For teammates

After cloning, run the course setup script once from the repository root:

```bash
python3 .automations/setup.py
```

Work on a branch, open a pull request against this repository's `main`, and have another team member review and merge it.

## Task boards

- Sprint 1: https://github.com/orgs/software-students-fall2026/projects/48
- Sprint 2: https://github.com/orgs/software-students-fall2026/projects/64
