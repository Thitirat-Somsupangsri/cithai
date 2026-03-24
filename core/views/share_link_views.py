import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from ..models import Song, ShareLink


@method_decorator(csrf_exempt, name='dispatch')
class ShareLinkListView(View):
    """
    GET  /users/<user_id>/songs/<song_id>/share-links/  → list all share links
    POST /users/<user_id>/songs/<song_id>/share-links/  → create a share link
    """

    def _get_song(self, user_id, song_id):
        try:
            return Song.objects.get(pk=song_id, library__user_id=user_id), None
        except Song.DoesNotExist:
            return None, JsonResponse({'error': 'Song not found'}, status=404)

    def get(self, request, user_id, song_id):
        song, err = self._get_song(user_id, song_id)
        if err:
            return err

        links = [
            {
                'id':              sl.id,
                'token':           str(sl.token),
                'expiration_date': sl.expiration_date.isoformat(),
                'is_active':       sl.is_active,
                'is_valid':        sl.is_valid,
                'created_at':      sl.created_at.isoformat(),
            }
            for sl in song.share_links.all()
        ]
        return JsonResponse({'share_links': links})

    def post(self, request, user_id, song_id):
        song, err = self._get_song(user_id, song_id)
        if err:
            return err

        if not song.is_accessible:
            return JsonResponse(
                {'error': 'Cannot share a song that is not ready'},
                status=400
            )

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        expiration_date = data.get('expiration_date')
        if not expiration_date:
            return JsonResponse({'error': 'expiration_date is required'}, status=400)

        sl = ShareLink.objects.create(song=song, expiration_date=expiration_date)
        return JsonResponse({
            'id':              sl.id,
            'token':           str(sl.token),
            'expiration_date': sl.expiration_date.isoformat(),
            'is_active':       sl.is_active,
        }, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class ShareLinkDetailView(View):
    """
    GET    /share-links/<token>/  → resolve a share link (public endpoint)
    PUT    /share-links/<token>/  → deactivate / update expiry (owner action)
    DELETE /share-links/<token>/  → delete share link
    """

    def _get_link(self, token):
        try:
            return ShareLink.objects.get(token=token), None
        except ShareLink.DoesNotExist:
            return None, JsonResponse({'error': 'Share link not found'}, status=404)

    def get(self, request, token):
        sl, err = self._get_link(token)
        if err:
            return err
        if not sl.is_valid:
            return JsonResponse({'error': 'Share link is expired or inactive'}, status=410)
        return JsonResponse({
            'song_id':         sl.song_id,
            'token':           str(sl.token),
            'expiration_date': sl.expiration_date.isoformat(),
        })

    def put(self, request, token):
        sl, err = self._get_link(token)
        if err:
            return err

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if 'is_active' in data:
            sl.is_active = bool(data['is_active'])
        if 'expiration_date' in data:
            sl.expiration_date = data['expiration_date']

        sl.save()
        return JsonResponse({
            'id':              sl.id,
            'token':           str(sl.token),
            'is_active':       sl.is_active,
            'expiration_date': sl.expiration_date.isoformat(),
        })

    def delete(self, request, token):
        sl, err = self._get_link(token)
        if err:
            return err
        sl.delete()
        return JsonResponse({'message': 'Share link deleted'})
