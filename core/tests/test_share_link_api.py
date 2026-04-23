import json
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from core.models import Library, ShareLink, Song, SongParameters, SongStatus, User


class ShareLinkApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='gina', email='gina@example.com')
        self.library = Library.objects.create(user=self.user)
        self.song = Song.objects.create(library=self.library, status=SongStatus.READY)
        SongParameters.objects.create(
            song=self.song,
            title='Ready Song',
            occasion='other',
            genre='pop',
            voice_type='girl',
        )

    def test_post_share_link_creates_link(self):
        tomorrow = (timezone.now().date() + timedelta(days=1)).isoformat()
        response = self.client.post(
            f'/users/{self.user.id}/songs/{self.song.id}/share-links/',
            data=json.dumps({'expiration_date': tomorrow}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(ShareLink.objects.filter(song=self.song).exists())

    def test_get_expired_share_link_returns_gone(self):
        link = ShareLink.objects.create(
            song=self.song,
            expiration_date=timezone.now().date() - timedelta(days=1),
        )

        response = self.client.get(f'/share-links/{link.token}/')

        self.assertEqual(response.status_code, 410)
