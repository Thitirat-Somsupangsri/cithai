import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from ..models import Library, Song, SongParameters, SongStatus


@method_decorator(csrf_exempt, name='dispatch')
class SongListView(View):
    """
    GET  /users/<user_id>/songs/  → list all songs in the user's library
    POST /users/<user_id>/songs/  → create a new song (with parameters)
    """

    def _get_library(self, user_id):
        try:
            return Library.objects.get(user_id=user_id), None
        except Library.DoesNotExist:
            return None, JsonResponse({'error': 'Library not found for this user'}, status=404)

    def get(self, request, user_id):
        library, err = self._get_library(user_id)
        if err:
            return err

        songs = []
        for song in library.songs.select_related('parameters').all():
            songs.append({
                'id':          song.id,
                'title':       song.title,
                'status':      song.status,
                'duration':    song.duration,
                'description': song.description,
                'created_at':  song.created_at.isoformat(),
            })
        return JsonResponse({'songs': songs, 'count': len(songs)})

    def post(self, request, user_id):
        library, err = self._get_library(user_id)
        if err:
            return err

        if library.is_full:
            return JsonResponse(
                {'error': f'Library is full (max {Library.MAX_SONGS} songs)'},
                status=400
            )

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        required = ('title', 'occasion', 'genre', 'voice_type')
        missing  = [f for f in required if not data.get(f)]
        if missing:
            return JsonResponse({'error': f'Missing fields: {missing}'}, status=400)

        song = Song.objects.create(library=library, status=SongStatus.GENERATING)
        SongParameters.objects.create(
            song        = song,
            title       = data['title'],
            occasion    = data['occasion'],
            genre       = data['genre'],
            voice_type  = data['voice_type'],
            custom_text = data.get('custom_text', ''),
        )

        return JsonResponse({
            'id':     song.id,
            'title':  song.title,
            'status': song.status,
        }, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class SongDetailView(View):
    """
    GET    /users/<user_id>/songs/<song_id>/  → retrieve song details
    PUT    /users/<user_id>/songs/<song_id>/  → update status / duration / description
    DELETE /users/<user_id>/songs/<song_id>/  → delete song
    """

    def _get_song(self, user_id, song_id):
        try:
            song = Song.objects.select_related('parameters').get(
                pk=song_id,
                library__user_id=user_id
            )
            return song, None
        except Song.DoesNotExist:
            return None, JsonResponse({'error': 'Song not found'}, status=404)

    def get(self, request, user_id, song_id):
        song, err = self._get_song(user_id, song_id)
        if err:
            return err
        return JsonResponse({
            'id':          song.id,
            'title':       song.title,
            'status':      song.status,
            'duration':    song.duration,
            'description': song.description,
            'occasion':    song.parameters.occasion   if hasattr(song, 'parameters') else None,
            'genre':       song.parameters.genre      if hasattr(song, 'parameters') else None,
            'voice_type':  song.parameters.voice_type if hasattr(song, 'parameters') else None,
            'custom_text': song.parameters.custom_text if hasattr(song, 'parameters') else '',
            'created_at':  song.created_at.isoformat(),
            'updated_at':  song.updated_at.isoformat(),
        })

    def put(self, request, user_id, song_id):
        song, err = self._get_song(user_id, song_id)
        if err:
            return err

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if 'status' in data:
            song.status = data['status']
        if 'duration' in data:
            song.duration = data['duration']
        if 'description' in data:
            song.description = data['description']

        song.save()
        return JsonResponse({
            'id':       song.id,
            'title':    song.title,
            'status':   song.status,
            'duration': song.duration,
        })

    def delete(self, request, user_id, song_id):
        song, err = self._get_song(user_id, song_id)
        if err:
            return err
        song.delete()
        return JsonResponse({'message': f'Song {song_id} deleted'})
