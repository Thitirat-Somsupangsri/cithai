import json

from django.test import TestCase

from core.models import Library, User


class UserApiTests(TestCase):
    def test_post_user_creates_library(self):
        response = self.client.post(
            '/users/',
            data=json.dumps({'username': 'dave', 'email': 'dave@example.com'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        user = User.objects.get(username='dave')
        self.assertTrue(Library.objects.filter(user=user).exists())

    def test_put_user_rejects_blank_username(self):
        user = User.objects.create(username='erin', email='erin@example.com')
        Library.objects.create(user=user)

        response = self.client.put(
            f'/users/{user.id}/',
            data=json.dumps({'username': '  '}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'username and email cannot be blank')
