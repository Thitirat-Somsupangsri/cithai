# EX3_SRS – AI Music Generator (Domain Layer)

Exercise 3: Implementing the Domain Layer using Django  
**Kasetsart University**

## Project Structure

```
EX3_SRS/
├── config/  
├── core/                # Main app — all domain logic lives here
│   ├── migrations/      # Auto-generated database migrations
│   ├── admin.py         # Django Admin registration (CRUD evidence)
│   ├── apps.py
│   ├── models.py        # Domain entities: User, Profile, Library, Song, SongParameters, ShareLink
│   ├── services.py      # Business logic: generation, moderation, CRUD helpers
│   ├── views.py
│   └── tests.py
├── manage.py
├── .gitignore
└── README.md
└──requirements.txt
```

---

## Domain Model

| Entity | Description |
|---|---|
| `User` | Registered individual (extends Django AbstractUser) |
| `Profile` | Personal info (gender, birthday) — 1-to-1 with User |
| `Library` | Song collection owned by a User — max **20 songs** |
| `Song` | AI-generated composition — max **10 minutes** duration |
| `SongParameters` | Generation preferences (title, occasion, genre, voice type, custom text) — always preserved even on failure |
| `ShareLink` | Temporary UUID token for sharing a song |

---

## Business Rules

- Each user owns exactly **one library** and **one profile**
- Library holds a maximum of **20 songs**
- Users can generate up to **3 songs simultaneously**
- Song duration maximum is **10 minutes**
- Only songs with status `ready` can be played, downloaded, or shared
- Songs are **private by default** unless a ShareLink is created
- A ShareLink is valid only when `is_active=True` AND `expiration_date >= today`
- Song generation auto-retries **once** on failure, then marks status as `failed`
- `SongParameters` are **always preserved** — even when a song fails

---

## Setup & Run Locally

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd EX3_SRS
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install django
```

### 4. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a superuser (for Django Admin)

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

### 7. Access Django Admin

Open [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) and log in with the superuser credentials.

---

## CRUD Evidence

All domain entities are registered in Django Admin and support full Create, Read, Update, Delete operations:

- **User** — create and manage user accounts
- **Profile** — view and edit user profiles
- **Library** — view library and song count per user
- **Song** — create songs, view status, duration; SongParameters and ShareLinks shown inline
- **SongParameters** — visible inline inside each Song
- **ShareLink** — create/deactivate share links; validity status shown

---

## Song Generation Flow

```
User submits generation request
  ↓
Check: max 3 concurrent generations?  → TooManyConcurrentGenerationsError
  ↓
Check: library full (20 songs)?       → LibraryFullError
  ↓
Content moderation on custom_text     → ModerationError (highlight bad words)
  ↓
Song + SongParameters saved to DB     ← parameters committed here (always preserved)
  ↓
Call AI API (attempt 1)
  → fail → wait 5s → retry once (attempt 2)
  → fail → status = failed, error saved to description
  → success → status = ready, duration + description saved
  ↓
Hard timeout: 10 minutes total
User can cancel at any checkpoint
```

