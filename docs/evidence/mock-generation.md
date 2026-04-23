# Mock Generation Evidence

This evidence corresponds to the automated API flow in [core/tests/test_song_api_generation.py](/Users/thitiratss/srs/ex3_srs/core/tests/test_song_api_generation.py:1).

## Example API result

Example request used by the automated Django test client:

```http
POST /users/<user_id>/songs/
Content-Type: application/json

{
  "title": "Road Trip",
  "occasion": "other",
  "genre": "rock",
  "voice_type": "boy",
  "custom_text": "anthemic chorus"
}
```

Expected response shape in mock mode:

```json
{
  "id": 1,
  "title": "Road Trip",
  "provider": "mock",
  "provider_generation_id": "mock-song-1",
  "status": "ready",
  "duration": 180,
  "description": "Mock song for Road Trip (other, rock, boy)",
  "error_message": ""
}
```

This is the behavior asserted by the test:

- `status_code == 201`
- `provider == "mock"`
- `status == "ready"`
- `duration == 180`
- `error_message == ""`

## Test run log

Command:

```bash
python3 manage.py test core.tests.test_song_api_generation -v 2
```

Output:

```text
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Found 1 test(s).
Operations to perform:
  Synchronize unmigrated apps: messages, staticfiles
  Apply all migrations: admin, auth, contenttypes, core, sessions
Synchronizing apps without migrations:
  Creating tables...
    Running deferred SQL...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying core.0001_initial... OK
  Applying core.0002_remove_song_title... OK
  Applying core.0003_song_generation_fields... OK
  Applying core.0004_alter_library_id_alter_profile_id_alter_sharelink_id_and_more... OK
  Applying sessions.0001_initial...test_post_song_generates_song_via_strategy (core.tests.test_song_api_generation.SongApiGenerationTests.test_post_song_generates_song_via_strategy) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.005s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
 OK
System check identified no issues (0 silenced).
```
