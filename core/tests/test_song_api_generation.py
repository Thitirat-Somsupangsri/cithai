import json
from datetime import timedelta

from django.test import TestCase, override_settings
from django.utils import timezone

from core.models import Library, Song, SongStatus, User
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
        self.assertEqual(payload['status'], 'generating')
        self.assertEqual(payload['duration'], 0)
        self.assertEqual(payload['error_message'], '')
        self.assertEqual(payload['audio_url'], '')

    @override_settings(MUSIC_GENERATION_PROVIDER='mock')
    def test_list_songs_completes_ready_mock_song_after_delay(self):
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
        song = Song.objects.get(pk=response.json()['id'])
        song.created_at = timezone.now() - timedelta(seconds=2)
        song.save(update_fields=['created_at'])

        list_response = self.client.get(f'/users/{self.user.id}/songs/')

        self.assertEqual(list_response.status_code, 200)
        song.refresh_from_db()
        self.assertEqual(song.status, SongStatus.READY)
        self.assertEqual(song.duration, MOCK_AUDIO_DURATION_SECONDS)
        self.assertEqual(song.audio_url, MOCK_AUDIO_URL)

    def test_list_songs_backfills_audio_url_for_ready_mock_song(self):
        library = Library.objects.get(user=self.user)
        song = Song.objects.create(
            library=library,
            title='Legacy Track',
            occasion='other',
            genre='pop',
            voice_type='boy',
            custom_text='',
            provider='mock',
            status=SongStatus.READY,
            duration=3,
            description='Legacy mock song',
            audio_url='',
        )

        response = self.client.get(f'/users/{self.user.id}/songs/')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['songs'][0]['audio_url'], MOCK_AUDIO_URL)
