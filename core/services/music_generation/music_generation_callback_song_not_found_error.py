from .music_generation_callback_error import MusicGenerationCallbackError


class MusicGenerationCallbackSongNotFoundError(MusicGenerationCallbackError):
    status_code = 404
