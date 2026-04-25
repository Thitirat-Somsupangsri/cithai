from .music_generation_callback_error import MusicGenerationCallbackError


class MusicGenerationCallbackValidationError(MusicGenerationCallbackError):
    status_code = 400
