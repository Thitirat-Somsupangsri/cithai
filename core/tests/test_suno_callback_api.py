import json

from django.test import TestCase

from core.models import Library, Song, SongParameters, SongStatus, User


class SunoCallbackApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='hank', email='hank@example.com')
        self.library = Library.objects.create(user=self.user)
        self.song = Song.objects.create(
            library=self.library,
            provider='suno',
            provider_generation_id='task-123',
            status=SongStatus.GENERATING,
        )
        SongParameters.objects.create(
            song=self.song,
            title='Callback Song',
            occasion='other',
            genre='pop',
            voice_type='boy',
        )

    def test_complete_callback_marks_song_ready(self):
        response = self.client.post(
            '/integrations/suno/callback/',
            data=json.dumps({
                'code': 200,
                'msg': 'success',
                'data': {
                    'task_id': 'task-123',
                    'callbackType': 'complete',
                    'data': [
                        {
                            'title': 'Generated Track 1',
                            'duration': 215,
                        }
                    ],
                },
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.song.refresh_from_db()
        self.assertEqual(self.song.status, SongStatus.READY)
        self.assertEqual(self.song.duration, 215)
        self.assertEqual(self.song.description, 'Generated Track 1')
        self.assertEqual(self.song.error_message, '')

    def test_error_callback_marks_song_failed(self):
        response = self.client.post(
            '/integrations/suno/callback/',
            data=json.dumps({
                'code': 400,
                'msg': 'content violation',
                'data': {
                    'task_id': 'task-123',
                    'callbackType': 'error',
                },
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.song.refresh_from_db()
        self.assertEqual(self.song.status, SongStatus.FAILED)
        self.assertEqual(self.song.error_message, 'content violation')

    def test_callback_requires_task_id(self):
        response = self.client.post(
            '/integrations/suno/callback/',
            data=json.dumps({
                'code': 200,
                'msg': 'success',
                'data': {'callbackType': 'complete'},
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'task_id is required')
