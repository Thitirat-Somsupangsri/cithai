import json

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

from core.models import Library, Song, SongParameters, User
from core.services.music_generation import generate_song, get_music_generation_strategy


class MusicGenerationStrategyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='alice', email='alice@example.com')
        self.library = Library.objects.create(user=self.user)

    def _create_song(self):
        song = Song.objects.create(library=self.library)
        SongParameters.objects.create(
            song=song,
            title='Birthday Song',
            occasion='birthday',
            genre='pop',
            voice_type='girl',
            custom_text='make it cheerful',
        )
        return song

    @override_settings(MUSIC_GENERATION_PROVIDER='mock')
    def test_mock_strategy_is_selected(self):
        strategy = get_music_generation_strategy()
        self.assertEqual(strategy.provider_name, 'mock')

    @override_settings(MUSIC_GENERATION_PROVIDER='suno')
    def test_suno_strategy_is_selected(self):
        strategy = get_music_generation_strategy()
        self.assertEqual(strategy.provider_name, 'suno')

    @override_settings(MUSIC_GENERATION_PROVIDER='unknown')
    def test_invalid_provider_raises_error(self):
        with self.assertRaises(ImproperlyConfigured):
            get_music_generation_strategy()

    @override_settings(MUSIC_GENERATION_PROVIDER='mock')
    def test_generate_song_with_mock_marks_song_ready(self):
        song = generate_song(self._create_song())

        self.assertEqual(song.provider, 'mock')
        self.assertEqual(song.status, 'ready')
        self.assertEqual(song.duration, 180)
        self.assertTrue(song.provider_generation_id.startswith('mock-song-'))
        self.assertEqual(song.error_message, '')

    @override_settings(
        MUSIC_GENERATION_PROVIDER='suno',
        SUNO_API_KEY='',
        SUNO_API_URL='',
        SUNO_CALLBACK_URL='https://example.com/suno/callback',
    )
    def test_generate_song_with_suno_missing_config_marks_song_failed(self):
        song = generate_song(self._create_song())

        self.assertEqual(song.provider, 'suno')
        self.assertEqual(song.status, 'failed')
        self.assertIn('not configured', song.error_message)


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
        self.assertEqual(payload['duration'], 180)
        self.assertEqual(payload['error_message'], '')
