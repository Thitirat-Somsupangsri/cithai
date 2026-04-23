import json

from django.test import TestCase, override_settings

from core.models import Library, User


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
