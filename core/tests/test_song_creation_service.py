from django.test import TestCase, override_settings

from core.models import Library, Song, User
from core.services import (
    LibraryFullError,
    LibraryNotFoundError,
    SongCreationPayload,
    SongCreationService,
    SongPayloadValidationError,
)


class SongCreationServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='charlie', email='charlie@example.com')
        self.library = Library.objects.create(user=self.user)
        self.service = SongCreationService()

    def test_payload_factory_rejects_missing_required_fields(self):
        with self.assertRaises(SongPayloadValidationError):
            SongCreationPayload.from_dict({'title': 'Only title'})

    @override_settings(MUSIC_GENERATION_PROVIDER='mock')
    def test_service_creates_song_for_user(self):
        song = self.service.create_for_user(
            self.user.id,
            SongCreationPayload(
                title='Party Mix',
                occasion='birthday',
                genre='pop',
                voice_type='girl',
                custom_text='bright and fun',
            ),
        )

        self.assertEqual(song.library, self.library)
        self.assertEqual(song.title, 'Party Mix')
        self.assertEqual(song.status, 'generating')

    def test_service_raises_when_library_missing(self):
        with self.assertRaises(LibraryNotFoundError):
            self.service.create_for_user(
                user_id=99999,
                payload=SongCreationPayload(
                    title='Missing Library',
                    occasion='other',
                    genre='rock',
                    voice_type='boy',
                ),
            )

    def test_service_raises_when_library_is_full(self):
        for index in range(Library.MAX_SONGS):
            Song.objects.create(
                library=self.library,
                title=f'Song {index}',
                occasion='other',
                genre='rock',
                voice_type='boy',
                custom_text='',
                provider_generation_id=str(index),
            )

        with self.assertRaises(LibraryFullError):
            self.service.create_for_user(
                self.user.id,
                SongCreationPayload(
                    title='Overflow',
                    occasion='other',
                    genre='rock',
                    voice_type='boy',
                ),
            )
