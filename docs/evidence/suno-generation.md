# Suno Generation Evidence

This evidence corresponds to:

- strategy and task-id behavior in [core/tests/test_music_generation_strategy.py](/Users/thitiratss/srs/ex3_srs/core/tests/test_music_generation_strategy.py:1)
- callback/status update behavior in [core/tests/test_suno_callback_api.py](/Users/thitiratss/srs/ex3_srs/core/tests/test_suno_callback_api.py:1)

## 1. Suno generation creates a taskId

The strategy test uses a fake provider client and verifies that the Suno strategy returns a provider generation id:

```python
return GenerationResult(
    status='generating',
    provider_generation_id='task-123',
    description='started',
)
```

The test then asserts:

- `result.provider_generation_id == "task-123"`

Example create-song response shape in Suno mode:

```json
{
  "id": 1,
  "title": "Skyline",
  "provider": "suno",
  "provider_generation_id": "task-123",
  "status": "generating",
  "duration": 0,
  "description": "Suno generation started",
  "error_message": ""
}
```

## 2. The app can retrieve status/details after Suno updates the task

The project now exposes:

```http
POST /integrations/suno/callback/
```

Example callback payload used by the automated test:

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "task_id": "task-123",
    "callbackType": "complete",
    "data": [
      {
        "title": "Generated Track 1",
        "duration": 215
      }
    ]
  }
}
```

After that callback is processed, the local song detail endpoint can be retrieved again:

```http
GET /users/<user_id>/songs/<song_id>/
```

Expected detail state after callback:

```json
{
  "id": 1,
  "title": "Callback Song",
  "provider": "suno",
  "provider_generation_id": "task-123",
  "status": "ready",
  "duration": 215,
  "description": "Generated Track 1",
  "error_message": "",
  "occasion": "other",
  "genre": "pop",
  "voice_type": "boy",
  "custom_text": "",
  "created_at": "...",
  "updated_at": "..."
}
```

This is the behavior asserted by the callback test:

- callback returns `200`
- local `Song.status == "ready"`
- local `Song.duration == 215`
- local `Song.description == "Generated Track 1"`

## Test run log

Command:

```bash
python3 manage.py test core.tests.test_music_generation_strategy core.tests.test_suno_callback_api -v 2
```

Output:

```text
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Found 9 test(s).
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
  Applying sessions.0001_initial...test_generate_song_with_mock_marks_song_ready (core.tests.test_music_generation_strategy.MusicGenerationStrategyTests.test_generate_song_with_mock_marks_song_ready) ... ok
test_generate_song_with_suno_missing_config_marks_song_failed (core.tests.test_music_generation_strategy.MusicGenerationStrategyTests.test_generate_song_with_suno_missing_config_marks_song_failed) ... ok
test_invalid_provider_raises_error (core.tests.test_music_generation_strategy.MusicGenerationStrategyTests.test_invalid_provider_raises_error) ... ok
test_mock_strategy_is_selected (core.tests.test_music_generation_strategy.MusicGenerationStrategyTests.test_mock_strategy_is_selected) ... ok
test_suno_strategy_delegates_to_provider_adapter (core.tests.test_music_generation_strategy.MusicGenerationStrategyTests.test_suno_strategy_delegates_to_provider_adapter) ... ok
test_suno_strategy_is_selected (core.tests.test_music_generation_strategy.MusicGenerationStrategyTests.test_suno_strategy_is_selected) ... ok
test_callback_requires_task_id (core.tests.test_suno_callback_api.SunoCallbackApiTests.test_callback_requires_task_id) ... ok
test_complete_callback_marks_song_ready (core.tests.test_suno_callback_api.SunoCallbackApiTests.test_complete_callback_marks_song_ready) ... ok
test_error_callback_marks_song_failed (core.tests.test_suno_callback_api.SunoCallbackApiTests.test_error_callback_marks_song_failed) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.008s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
 OK
System check identified no issues (0 silenced).
```
