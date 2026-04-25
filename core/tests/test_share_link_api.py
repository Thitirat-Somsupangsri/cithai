import json
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from core.models import Library, ShareLink, Song, SongStatus, User


class ShareLinkApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='gina', email='gina@example.com')
        self.library = Library.objects.create(user=self.user)
        self.song = Song.objects.create(
            library=self.library,
            status=SongStatus.READY,
            title='Ready Song',
            occasion='other',
            genre='pop',
            voice_type='girl',
        )

    def test_post_share_link_creates_link(self):
        response = self.client.post(
            f'/users/{self.user.id}/songs/{self.song.id}/share-links/',
            data=json.dumps({}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        link = ShareLink.objects.get(song=self.song)
        self.assertEqual(link.expiration_date, timezone.localdate() + timedelta(days=7))

    def test_post_share_link_accepts_one_month_option(self):
        response = self.client.post(
            f'/users/{self.user.id}/songs/{self.song.id}/share-links/',
            data=json.dumps({'expiration_option': '1_month'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        link = ShareLink.objects.get(song=self.song)
        self.assertEqual(link.expiration_date.isoformat(), response.json()['expiration_date'])

    def test_post_share_link_rejects_invalid_option(self):
        response = self.client.post(
            f'/users/{self.user.id}/songs/{self.song.id}/share-links/',
            data=json.dumps({'expiration_option': 'tomorrow'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'expiration_option must be 7_days or 1_month')

    def test_get_expired_share_link_returns_gone(self):
        link = ShareLink.objects.create(
            song=self.song,
            expiration_date=timezone.now().date() - timedelta(days=1),
        )

        response = self.client.get(f'/share-links/{link.token}/')

        self.assertEqual(response.status_code, 410)

    def test_put_share_link_rejects_raw_expiration_date(self):
        link = ShareLink.objects.create(
            song=self.song,
            expiration_date=timezone.localdate() + timedelta(days=7),
        )

        response = self.client.put(
            f'/share-links/{link.token}/',
            data=json.dumps({'expiration_date': timezone.localdate().isoformat()}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Use expiration_option instead of expiration_date')
