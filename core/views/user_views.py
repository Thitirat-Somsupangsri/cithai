import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from ..models import User, Library


@method_decorator(csrf_exempt, name='dispatch')
class UserListView(View):
    """
    GET  /users/       → list all users
    POST /users/       → create a new user (and auto-create their Library)
    """

    def get(self, request):
        users = list(
            User.objects.values('id', 'username', 'email', 'created_at')
        )
        return JsonResponse({'users': users})

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        username = data.get('username', '').strip()
        email    = data.get('email', '').strip()

        if not username or not email:
            return JsonResponse({'error': 'username and email are required'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'username already taken'}, status=409)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'email already registered'}, status=409)

        user = User.objects.create(username=username, email=email)
        # Auto-create a Library for every new User
        Library.objects.create(user=user)

        return JsonResponse({
            'id':         user.id,
            'username':   user.username,
            'email':      user.email,
            'created_at': user.created_at.isoformat(),
        }, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class UserDetailView(View):
    """
    GET    /users/<id>/  → retrieve a user
    PUT    /users/<id>/  → update username / email
    DELETE /users/<id>/  → delete a user (cascades to Profile, Library, Songs)
    """

    def _get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id), None
        except User.DoesNotExist:
            return None, JsonResponse({'error': 'User not found'}, status=404)

    def get(self, request, user_id):
        user, err = self._get_user(user_id)
        if err:
            return err
        return JsonResponse({
            'id':         user.id,
            'username':   user.username,
            'email':      user.email,
            'created_at': user.created_at.isoformat(),
        })

    def put(self, request, user_id):
        user, err = self._get_user(user_id)
        if err:
            return err

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if 'username' in data:
            new_username = data['username'].strip()
            if User.objects.exclude(pk=user_id).filter(username=new_username).exists():
                return JsonResponse({'error': 'username already taken'}, status=409)
            user.username = new_username

        if 'email' in data:
            new_email = data['email'].strip()
            if User.objects.exclude(pk=user_id).filter(email=new_email).exists():
                return JsonResponse({'error': 'email already registered'}, status=409)
            user.email = new_email

        user.save()
        return JsonResponse({
            'id':       user.id,
            'username': user.username,
            'email':    user.email,
        })

    def delete(self, request, user_id):
        user, err = self._get_user(user_id)
        if err:
            return err
        user.delete()
        return JsonResponse({'message': f'User {user_id} deleted'}, status=200)
