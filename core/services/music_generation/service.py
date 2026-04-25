from .selector import get_music_generation_strategy
from .strategies.base import SongGenerationError

MAX_RETRIES = 3


def generate_song(song):
    strategy = get_music_generation_strategy()

    song.provider = strategy.provider_name
    song.status = 'generating'
    song.duration = 0
    song.description = ''
    song.error_message = ''
    song.provider_generation_id = ''
    song.callback_url = ''
    song.audio_url = ''
    song.save(
        update_fields=[
            'provider', 'status', 'duration', 'description',
            'error_message', 'provider_generation_id',
            'callback_url', 'audio_url', 'updated_at',
        ]
    )

    last_error = ''
    while song.retry_count <= MAX_RETRIES:
        try:
            result = strategy.generate(song)
            song.status = result.status
            song.duration = result.duration
            song.description = result.description
            song.provider_generation_id = result.provider_generation_id
            song.error_message = result.error_message
            song.callback_url = result.callback_url
            song.audio_url = result.audio_url
            song.save()
            return song
        except SongGenerationError as exc:
            last_error = str(exc)
        except Exception as exc:
            last_error = f'Unexpected error: {exc}'

        song.retry_count += 1
        if song.retry_count <= MAX_RETRIES:
            song.error_message = f'Attempt {song.retry_count} failed, retrying… ({last_error})'
            song.save(update_fields=['retry_count', 'error_message', 'updated_at'])
        else:
            break

    song.status = 'failed'
    song.error_message = (
        f'Generation failed after {MAX_RETRIES} retries. Last error: {last_error}'
    )
    song.provider_generation_id = ''
    song.audio_url = ''
    song.save()
    return song
