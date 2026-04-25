from .song_creation_error import SongCreationError


class LibraryFullError(SongCreationError):
    status_code = 400
