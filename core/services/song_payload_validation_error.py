from .song_creation_error import SongCreationError


class SongPayloadValidationError(SongCreationError):
    status_code = 400
