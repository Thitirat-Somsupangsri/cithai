import json

from django.test import TestCase

from core.models import Library, User
from core.views._session_auth import SESSION_USER_ID_KEY


class UserApiTests(TestCase):
    def login(self, user):
        session = self.client.session
        session[SESSION_USER_ID_KEY] = user.id
        session.save()

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
        self.login(user)

        response = self.client.put(
            f'/users/{user.id}/',
            data=json.dumps({'username': '  '}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'username and email cannot be blank')

    def test_get_users_requires_authentication(self):
        response = self.client.get('/users/')

        self.assertEqual(response.status_code, 401)

    def test_session_login_and_me_return_current_user(self):
        user = User.objects.create(username='maya', email='maya@example.com')
        Library.objects.create(user=user)

        login_response = self.client.post(
            '/auth/session/login/',
            data=json.dumps({'identifier': 'maya@example.com'}),
            content_type='application/json',
        )
        me_response = self.client.get('/auth/session/me/')

        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.json()['user']['id'], user.id)
