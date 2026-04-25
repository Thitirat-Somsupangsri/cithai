import json

from django.test import TestCase, override_settings

from core.models import Library, Song, SongParameters, SongStatus, User
from core.services.music_generation.strategies.mock import (
    MOCK_AUDIO_DURATION_SECONDS,
    MOCK_AUDIO_URL,
)


class SongApiGenerationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='bob', email='bob@example.com')
        Library.objects.create(user=self.user)

    @override_settings(MUSIC_GENERATION_PROVIDER='mock')
    def test_post_song_generates_song_via_strategy(self):
        response = self.client.post(
            f'/users/{self.user.id}/songs/',
            data=json.dumps({
                'title': 'Road Trip',
                'occasion': 'other',
                'genre': 'rock',
                'voice_type': 'boy',
                'custom_text': 'anthemic chorus',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertEqual(payload['provider'], 'mock')
        self.assertEqual(payload['status'], 'ready')
        self.assertEqual(payload['duration'], MOCK_AUDIO_DURATION_SECONDS)
        self.assertEqual(payload['error_message'], '')
        self.assertEqual(payload['audio_url'], MOCK_AUDIO_URL)

    def test_list_songs_backfills_audio_url_for_ready_mock_song(self):
        library = Library.objects.get(user=self.user)
        song = Song.objects.create(
            library=library,
            provider='mock',
            status=SongStatus.READY,
            duration=3,
            description='Legacy mock song',
            audio_url='',
        )
        SongParameters.objects.create(
            song=song,
            title='Legacy Track',
            occasion='other',
            genre='pop',
            voice_type='boy',
            custom_text='',
        )

        response = self.client.get(f'/users/{self.user.id}/songs/')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['songs'][0]['audio_url'], MOCK_AUDIO_URL)
