from ...models import Song, SongStatus
from .music_generation_callback_error import MusicGenerationCallbackError
from .music_generation_callback_song_not_found_error import MusicGenerationCallbackSongNotFoundError
from .music_generation_callback_validation_error import MusicGenerationCallbackValidationError


class SunoCallbackService:
    def process(self, payload):
        task_id = self._extract_task_id(payload)
        try:
            song = Song.objects.get(provider='suno', provider_generation_id=task_id)
        except Song.DoesNotExist as exc:
            raise MusicGenerationCallbackSongNotFoundError('Song not found for this Suno task') from exc

        status = self._resolve_status(payload)
        data = payload.get('data') or {}
        tracks = data.get('data') or []
        first_track = tracks[0] if tracks else {}

        song.status = status
        if first_track.get('duration') is not None:
            try:
                song.duration = int(first_track['duration'])
            except (TypeError, ValueError):
                pass

        if status == SongStatus.READY:
            song.description = first_track.get('title') or payload.get('msg', '')
            song.error_message = ''
            audio_url = (
                first_track.get('audio_url')
                or first_track.get('stream_audio_url')
                or first_track.get('streamAudioUrl')
                or first_track.get('audioUrl')
                or ''
            )
            if audio_url:
                song.audio_url = audio_url
        elif status == SongStatus.FAILED:
            song.error_message = payload.get('msg', 'Suno generation failed.')

        song.save()
        return song

    def _extract_task_id(self, payload):
        data = payload.get('data') or {}
        task_id = (
            data.get('task_id')
            or data.get('taskId')
            or payload.get('task_id')
            or payload.get('taskId')
            or payload.get('provider_generation_id')
        )
        if not task_id:
            raise MusicGenerationCallbackValidationError('task_id is required')
        return str(task_id)

    def _resolve_status(self, payload):
        code = payload.get('code')
        data = payload.get('data') or {}
        callback_type = str(data.get('callbackType', '')).lower()

        if callback_type == 'error' or code in (400, 451, 500):
            return SongStatus.FAILED
        if callback_type == 'complete' and code == 200:
            return SongStatus.READY
        return SongStatus.GENERATING
