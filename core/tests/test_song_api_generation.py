import json
from datetime import timedelta

from django.test import TestCase, override_settings
from django.utils import timezone

from core.models import Library, Song, SongStatus, User
from core.views._session_auth import SESSION_USER_ID_KEY
from core.services.music_generation.strategies.mock_music_generation_strategy import (
    MOCK_AUDIO_DURATION_SECONDS,
    MOCK_AUDIO_URL,
)


class SongApiGenerationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='bob', email='bob@example.com')
        Library.objects.create(user=self.user)
        session = self.client.session
        session[SESSION_USER_ID_KEY] = self.user.id
        session.save()

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

    @override_settings(MUSIC_GENERATION_PROVIDER='mock')
    def test_put_song_can_cancel_generating_song(self):
        library = Library.objects.get(user=self.user)
        song = Song.objects.create(
            library=library,
            title='Road Trip',
            occasion='other',
            genre='rock',
            voice_type='boy',
            custom_text='anthemic chorus',
            provider='mock',
            status=SongStatus.GENERATING,
        )

        cancel_response = self.client.put(
            f'/users/{self.user.id}/songs/{song.id}/',
            data=json.dumps({'action': 'cancel'}),
            content_type='application/json',
        )

        self.assertEqual(cancel_response.status_code, 200)
        self.assertEqual(cancel_response.json()['status'], SongStatus.FAILED)

    @override_settings(MUSIC_GENERATION_PROVIDER='mock')
    def test_put_song_can_regenerate_failed_song_without_creating_duplicate(self):
        library = Library.objects.get(user=self.user)
        song = Song.objects.create(
            library=library,
            title='Retry Me',
            occasion='other',
            genre='pop',
            voice_type='girl',
            custom_text='',
            provider='mock',
            status=SongStatus.FAILED,
            error_message='Old failure',
            retry_count=4,
            duration=111,
            description='Old description',
            audio_url='https://example.com/old.mp3',
        )

        response = self.client.put(
            f'/users/{self.user.id}/songs/{song.id}/',
            data=json.dumps({'action': 'regenerate'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], song.id)
        self.assertEqual(Song.objects.count(), 1)
        song.refresh_from_db()
        self.assertEqual(song.status, SongStatus.READY)
        self.assertEqual(song.retry_count, 0)
        self.assertEqual(song.error_message, '')
        self.assertEqual(song.duration, MOCK_AUDIO_DURATION_SECONDS)
        self.assertIn('Mock generation complete', song.description)
        self.assertEqual(song.audio_url, MOCK_AUDIO_URL)

    @override_settings(MUSIC_GENERATION_PROVIDER='mock')
    def test_regenerated_song_can_become_ready_on_follow_up_fetch(self):
        library = Library.objects.get(user=self.user)
        song = Song.objects.create(
            library=library,
            title='Retry Me',
            occasion='other',
            genre='pop',
            voice_type='girl',
            custom_text='',
            provider='mock',
            status=SongStatus.FAILED,
            error_message='Old failure',
            retry_count=4,
        )

        regenerate_response = self.client.put(
            f'/users/{self.user.id}/songs/{song.id}/',
            data=json.dumps({'action': 'regenerate'}),
            content_type='application/json',
        )
        self.assertEqual(regenerate_response.status_code, 200)
        song.refresh_from_db()
        self.assertEqual(song.status, SongStatus.READY)
        self.assertEqual(song.audio_url, MOCK_AUDIO_URL)

    def test_song_endpoints_require_authentication(self):
        self.client.cookies.clear()
        response = self.client.get(f'/users/{self.user.id}/songs/')

        self.assertEqual(response.status_code, 401)
