import json

from django.test import TestCase

from core.models import Library, User


class ProfileApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='frank', email='frank@example.com')
        Library.objects.create(user=self.user)

    def test_post_profile_creates_profile(self):
        response = self.client.post(
            f'/users/{self.user.id}/profile/',
            data=json.dumps({'gender': 'male', 'birthday': '2000-01-01'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['gender'], 'male')

    def test_put_profile_rejects_blank_birthday(self):
        self.client.post(
            f'/users/{self.user.id}/profile/',
            data=json.dumps({'gender': 'male', 'birthday': '2000-01-01'}),
            content_type='application/json',
        )

        response = self.client.put(
            f'/users/{self.user.id}/profile/',
            data=json.dumps({'birthday': ' '}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'gender and birthday cannot be blank')
