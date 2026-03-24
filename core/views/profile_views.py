import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from ..models import User, Profile


@method_decorator(csrf_exempt, name='dispatch')
class ProfileView(View):
    """
    One Profile per User — accessed via /users/<user_id>/profile/

    GET    → read profile
    POST   → create profile (if none exists)
    PUT    → update gender / birthday
    DELETE → delete profile only (User is preserved)
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
        try:
            p = user.profile
        except Profile.DoesNotExist:
            return JsonResponse({'error': 'Profile not found'}, status=404)

        return JsonResponse({
            'id':       p.id,
            'user_id':  user.id,
            'gender':   p.gender,
            'birthday': p.birthday.isoformat(),
        })

    def post(self, request, user_id):
        user, err = self._get_user(user_id)
        if err:
            return err

        if Profile.objects.filter(user=user).exists():
            return JsonResponse({'error': 'Profile already exists for this user'}, status=409)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        gender   = data.get('gender', '').strip()
        birthday = data.get('birthday', '').strip()

        if not gender or not birthday:
            return JsonResponse({'error': 'gender and birthday are required'}, status=400)

        p = Profile.objects.create(user=user, gender=gender, birthday=birthday)
        return JsonResponse({
            'id':       p.id,
            'user_id':  user.id,
            'gender':   p.gender,
            'birthday': p.birthday.isoformat(),
        }, status=201)

    def put(self, request, user_id):
        user, err = self._get_user(user_id)
        if err:
            return err
        try:
            p = user.profile
        except Profile.DoesNotExist:
            return JsonResponse({'error': 'Profile not found'}, status=404)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if 'gender' in data:
            p.gender = data['gender']
        if 'birthday' in data:
            p.birthday = data['birthday']

        p.save()
        return JsonResponse({
            'id':       p.id,
            'gender':   p.gender,
            'birthday': p.birthday.isoformat(),
        })

    def delete(self, request, user_id):
        user, err = self._get_user(user_id)
        if err:
            return err
        try:
            user.profile.delete()
        except Profile.DoesNotExist:
            return JsonResponse({'error': 'Profile not found'}, status=404)
        return JsonResponse({'message': f'Profile for user {user_id} deleted'})
