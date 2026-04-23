from dataclasses import dataclass

from ..models import Library, Song, SongParameters, SongStatus
from .music_generation import generate_song


class SongCreationError(Exception):
    status_code = 400


class LibraryNotFoundError(SongCreationError):
    status_code = 404


class LibraryFullError(SongCreationError):
    status_code = 400


class SongPayloadValidationError(SongCreationError):
    status_code = 400


@dataclass(frozen=True)
class SongCreationPayload:
    title: str
    occasion: str
    genre: str
    voice_type: str
    custom_text: str = ''

    @classmethod
    def from_dict(cls, data):
        required = ('title', 'occasion', 'genre', 'voice_type')
        missing = [field for field in required if not str(data.get(field, '')).strip()]
        if missing:
            raise SongPayloadValidationError(f'Missing fields: {missing}')

        return cls(
            title=str(data['title']).strip(),
            occasion=str(data['occasion']).strip(),
            genre=str(data['genre']).strip(),
            voice_type=str(data['voice_type']).strip(),
            custom_text=str(data.get('custom_text', '')).strip(),
        )


class SongCreationService:
    def create_for_user(self, user_id, payload):
        library = self._get_library(user_id)
        if library.is_full:
            raise LibraryFullError(f'Library is full (max {Library.MAX_SONGS} songs)')

        song = Song.objects.create(library=library, status=SongStatus.GENERATING)
        SongParameters.objects.create(
            song=song,
            title=payload.title,
            occasion=payload.occasion,
            genre=payload.genre,
            voice_type=payload.voice_type,
            custom_text=payload.custom_text,
        )
        return generate_song(song)

    def _get_library(self, user_id):
        try:
            return Library.objects.get(user_id=user_id)
        except Library.DoesNotExist as exc:
            raise LibraryNotFoundError('Library not found for this user') from exc
