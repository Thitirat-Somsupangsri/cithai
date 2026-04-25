from .song_creation_error import SongCreationError


class LibraryNotFoundError(SongCreationError):
    status_code = 404
