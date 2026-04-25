import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from ...models import Song
from ...presenters import present_song_detail, present_song_generation
from ...services.generation_timeout_service import GenerationTimeoutService
from ...services.mock_generation_completion_service import MockGenerationCompletionService
from ...services.music_generation import generate_song
from .._session_auth import require_owned_user


@method_decorator(csrf_exempt, name='dispatch')
class SongDetailView(View):
    timeout_service = GenerationTimeoutService()
    mock_completion_service = MockGenerationCompletionService()
    def _get_song(self, user_id, song_id):
        try:
            song = Song.objects.get(
                pk=song_id,
                library__user_id=user_id,
            )
            return song, None
        except Song.DoesNotExist:
            return None, JsonResponse({'error': 'Song not found'}, status=404)

    def get(self, request, user_id, song_id):
        _, err = require_owned_user(request, user_id)
        if err:
            return err
        song, err = self._get_song(user_id, song_id)
        if err:
            return err
        self.mock_completion_service.complete_if_ready(song)
        self.timeout_service.expire_if_timed_out(song)
        return JsonResponse(present_song_detail(song))

    def put(self, request, user_id, song_id):
        _, err = require_owned_user(request, user_id)
        if err:
            return err
        song, err = self._get_song(user_id, song_id)
        if err:
            return err

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if data.get('action') == 'cancel':
            if song.status != 'generating':
                return JsonResponse({'error': 'Only generating songs can be cancelled'}, status=409)
            song.status = 'failed'
            song.error_message = 'Generation cancelled by user.'
            song.save(update_fields=['status', 'error_message', 'updated_at'])
            return JsonResponse(present_song_generation(song))

        if data.get('action') == 'regenerate':
            if song.status == 'generating':
                return JsonResponse({'error': 'Song is already generating'}, status=409)
            song = generate_song(song)
            return JsonResponse(present_song_generation(song))

        if 'status' in data:
            song.status = data['status']
        if 'duration' in data:
            song.duration = data['duration']
        if 'description' in data:
            song.description = data['description']

        song.save()
        return JsonResponse(present_song_generation(song))

    def delete(self, request, user_id, song_id):
        _, err = require_owned_user(request, user_id)
        if err:
            return err
        song, err = self._get_song(user_id, song_id)
        if err:
            return err
        song.delete()
        return JsonResponse({'message': f'Song {song_id} deleted'})
