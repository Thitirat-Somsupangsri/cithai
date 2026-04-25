from .selector import get_music_generation_strategy
from .strategies.base import SongGenerationError


def generate_song(song):
    strategy = get_music_generation_strategy()

    song.provider = strategy.provider_name
    song.status = 'generating'
    song.error_message = ''
    song.provider_generation_id = ''
    song.save(update_fields=['provider', 'status', 'error_message', 'provider_generation_id', 'updated_at'])

    try:
        result = strategy.generate(song)
        song.status = result.status
        song.duration = result.duration
        song.description = result.description
        song.provider_generation_id = result.provider_generation_id
        song.error_message = result.error_message
        song.callback_url = result.callback_url
    except SongGenerationError as exc:
        song.status = 'failed'
        song.error_message = str(exc)
        song.provider_generation_id = ''
    except Exception as exc:
        song.status = 'failed'
        song.error_message = f'Unexpected generation error: {exc}'
        song.provider_generation_id = ''

    song.save()
    return song
