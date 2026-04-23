# EX3_SRS – Cithai AI Music Generator

Exercise project implemented with Django.

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

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create your environment file

```bash
cp .env.example .env
```

Available environment variables:

```env
MUSIC_GENERATION_PROVIDER=mock
SUNO_API_URL=https://api.suno.example/api/v1/generate
SUNO_API_KEY=your_suno_api_key_here
SUNO_CALLBACK_URL=https://your-domain.example/suno/callback
SUNO_MODEL=V4_5ALL
SUNO_CUSTOM_MODE=false
SUNO_INSTRUMENTAL=false
```

### 5. Set up Suno API secrets

If you want to run in `suno` mode:

1. Get a valid Suno API key from your Suno API provider account.
2. Put the key into `SUNO_API_KEY` in `.env`.
3. Set `SUNO_API_URL` to the Suno generate endpoint.
4. Set `SUNO_CALLBACK_URL` to a public URL that points to:

```text
/integrations/suno/callback/
```

For local development, `localhost` is usually not reachable by Suno directly. You will usually need a public tunnel such as `ngrok` or another reverse-tunnel service, then set:

```env
SUNO_CALLBACK_URL=https://your-public-url.example/integrations/suno/callback/
```

### 6. Apply migrations

```bash
python3 manage.py migrate
```

### 7. Optional: create a superuser

```bash
python3 manage.py createsuperuser
```

## How to run

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
SUNO_CALLBACK_URL=https://your-public-url.example/integrations/suno/callback/
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
