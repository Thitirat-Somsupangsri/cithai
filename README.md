# EX3_SRS – Cithai AI Music Generator

Exercise project implemented with Django backend + React/Vite frontend.

## How to install

### 1. Clone the repository

```bash
git clone https://github.com/Thitirat-Somsupangsri/cithai.git
cd cithai
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 5. Create your environment file

```bash
cp .env.example .env
```

Available environment variables:

```env
MUSIC_GENERATION_PROVIDER=mock
SUNO_API_URL=https://api.suno.example/api/v1/generate
SUNO_API_KEY=your_suno_api_key_here
SUNO_CALLBACK_URL=
BACKEND_PUBLIC_URL=https://your-public-url.example
SUNO_MODEL=V4_5ALL
SUNO_CUSTOM_MODE=false
SUNO_INSTRUMENTAL=false
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret
GOOGLE_OAUTH_REDIRECT_URI=http://127.0.0.1:8000/auth/google/callback/
GOOGLE_OAUTH_AUTH_URI=https://accounts.google.com/o/oauth2/v2/auth
GOOGLE_OAUTH_TOKEN_URI=https://oauth2.googleapis.com/token
GOOGLE_OAUTH_USERINFO_URI=https://openidconnect.googleapis.com/v1/userinfo
GOOGLE_OAUTH_SCOPES=openid email profile
FRONTEND_APP_URL=http://127.0.0.1:5173
```

### 6. Set up Suno API secrets

If you want to run in `suno` mode:

1. Get a valid Suno API key from your Suno API provider account.
2. Put the key into `SUNO_API_KEY` in `.env`.
3. Set `SUNO_API_URL` to the Suno generate endpoint.
4. Set either `SUNO_CALLBACK_URL` directly, or set `BACKEND_PUBLIC_URL` and let the app build the callback automatically. The callback must point to:

```text
/integrations/suno/callback/
```

For local development, `localhost` is usually not reachable by Suno directly. You will usually need a public tunnel such as `ngrok` or another reverse-tunnel service.

Install `ngrok` first if you want to test Suno mode against your local Django server.

If `ngrok` is already installed:

```bash
ngrok http 8000
```

Then copy the public HTTPS URL and set:

```env
BACKEND_PUBLIC_URL=https://your-public-url.example
```

or explicitly:

```env
SUNO_CALLBACK_URL=https://your-public-url.example/integrations/suno/callback/
```

Important:

- `SUNO_CALLBACK_URL` must be public and must end with `/integrations/suno/callback/`
- `localhost`, `127.0.0.1`, and placeholder example URLs will fail
- restart Django after changing `.env`

### 7. Set up Google OAuth

Put your Google OAuth client values into `.env`:

```env
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret
GOOGLE_OAUTH_REDIRECT_URI=http://127.0.0.1:8000/auth/google/callback/
FRONTEND_APP_URL=http://127.0.0.1:5173
```

Google Cloud Console values:

- Authorized JavaScript origins:

```text
http://127.0.0.1:5173
```

- Authorized redirect URIs:

```text
http://127.0.0.1:8000/auth/google/callback/
```

If you use a public backend domain for OAuth testing, add that redirect URI too.

### 8. Apply migrations

```bash
python3 manage.py migrate
```

### 9. Optional: create a superuser

```bash
python3 manage.py createsuperuser
```

## How to run

### Run with separated frontend and backend

Backend:

```bash
./venv/bin/python manage.py runserver
```

Frontend:

```bash
cd frontend
npm run dev
```

Open:

```text
http://127.0.0.1:5173/
```

Notes:

- Django API stays on `http://127.0.0.1:8000`
- React frontend runs on `http://127.0.0.1:5173`
- Vite proxies `/users`, `/share-links`, `/integrations`, and `/auth` to Django during development

### Run in Mock mode

Set this in `.env`:

```env
MUSIC_GENERATION_PROVIDER=mock
```

Then run:

```bash
python3 manage.py runserver
```

Behavior in this mode:

- Song generation finishes immediately.
- No external API key is required.
- Useful for demo and testing.

### Run in Suno mode

Set this in `.env`:

```env
MUSIC_GENERATION_PROVIDER=suno
SUNO_API_URL=https://api.sunoapi.org/api/v1/generate
SUNO_API_KEY=your_real_suno_api_key
BACKEND_PUBLIC_URL=https://your-public-url.example
SUNO_MODEL=V4_5ALL
SUNO_CUSTOM_MODE=false
SUNO_INSTRUMENTAL=false
```

Then run:

```bash
python3 manage.py runserver
```

Behavior in this mode:

- Creating a song starts an async generation task on Suno.
- The app stores Suno `taskId` in `provider_generation_id`.
- Suno sends the final result back to:

```text
POST /integrations/suno/callback/
```

- The callback updates the local song status to `ready` or `failed`.

Recommended local flow for Suno:

1. Start Django:

```bash
./venv/bin/python manage.py runserver
```

2. Start ngrok:

```bash
ngrok http 8000
```

3. Put the ngrok HTTPS URL into `BACKEND_PUBLIC_URL`

4. Restart Django

5. Start frontend:

```bash
cd frontend
npm run dev
```

6. Create a song from `http://127.0.0.1:5173`

### Google Login

The project supports Google OAuth login through:

- `GET /auth/google/login/`
- `GET /auth/google/callback/`

Frontend starts the flow from the login page and the backend redirects back to the frontend after a successful Google sign-in.

## Verify the project

Run tests:

```bash
python3 manage.py test core
```

## Example Run Output / Logs

- Mock generation evidence: [docs/evidence/mock-generation.md](/Users/thitiratss/srs/ex3_srs/docs/evidence/mock-generation.md:1)
- Suno generation evidence: [docs/evidence/suno-generation.md](/Users/thitiratss/srs/ex3_srs/docs/evidence/suno-generation.md:1)

## Notes

- Mock mode is the easiest way to verify the project end-to-end.
- Suno mode requires valid credentials and a reachable callback URL.
- Google OAuth requires a valid client ID/client secret and correctly configured redirect URI.
- The current app stores one local `Song` per Suno task. When Suno returns multiple generated tracks in the callback, the app currently uses the first returned track as the representative result for that local song.

## CRUD Evidence

[demo video](https://youtu.be/2D5Z9Am61D8)

Users:
![django admin](pic/users.png)

Profiles:
![django admin](pic/profiles.png)

Songs:
![django admin](pic/songs.png)

Libraries:
![django admin](pic/libraries.png)

Share links:
![django admin](pic/sharelinks.png)
