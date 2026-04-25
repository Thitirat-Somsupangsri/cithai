from ..models import Library, Song, SongStatus
from .content_moderation_service import ContentModerationService, ContentViolationError
from .library_full_error import LibraryFullError
from .library_not_found_error import LibraryNotFoundError
from .music_generation import generate_song
from .song_creation_error import SongCreationError
from .song_creation_payload import SongCreationPayload
from .song_payload_validation_error import SongPayloadValidationError


class SongCreationService:
    moderation_service = ContentModerationService()

    def create_for_user(self, user_id, payload):
        library = self._get_library(user_id)
        if library.is_full:
            raise LibraryFullError(f'Library is full (max {Library.MAX_SONGS} songs)')

        flagged = self.moderation_service.validate(payload.title, payload.custom_text)
        if flagged:
            raise ContentViolationError(flagged)

        song = Song.objects.create(
            library=library,
            status=SongStatus.GENERATING,
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
