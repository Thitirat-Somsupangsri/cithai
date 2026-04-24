import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from ...models import Song
from ...presenters import present_song_detail, present_song_generation
from ...services.generation_timeout_service import GenerationTimeoutService


@method_decorator(csrf_exempt, name='dispatch')
class SongDetailView(View):
    timeout_service = GenerationTimeoutService()
    def _get_song(self, user_id, song_id):
        try:
            song = Song.objects.select_related('parameters').get(
                pk=song_id,
                library__user_id=user_id,
            )
            return song, None
        except Song.DoesNotExist:
            return None, JsonResponse({'error': 'Song not found'}, status=404)

    def get(self, request, user_id, song_id):
        song, err = self._get_song(user_id, song_id)
        if err:
            return err
        self.timeout_service.expire_if_timed_out(song)
        return JsonResponse(present_song_detail(song))

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
        return JsonResponse(present_song_generation(song))

    def delete(self, request, user_id, song_id):
        song, err = self._get_song(user_id, song_id)
        if err:
            return err
        song.delete()
        return JsonResponse({'message': f'Song {song_id} deleted'})
