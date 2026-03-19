# EX3_SRS – Cithai AI Music Generator (Domain Layer)

Exercise 3: Implementing the Domain Layer using Django
**Kasetsart University**

---

## Project Structure

```
EX3_SRS/
├── config/ 
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/        
│   ├── migrations/  
│   ├── admin.py 
│   ├── apps.py
│   ├── models.py 
│   ├── views.py
│   └── tests.py
├── manage.py
├── .gitignore
└── README.md
```

---
## Justification

[doc](https://docs.google.com/document/d/1j4psyMPPyhkBAgybqP1QvR26h9MuieuiFNBwUaGbQWg/edit?usp=sharing)

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

Open [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) and log in with the superuser credentials created in step 5.

---

## CRUD Evidence


---