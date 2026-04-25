import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from ...models import Library
from ...presenters import present_song_generation, present_song_summary
from ...services.generation_timeout_service import GenerationTimeoutService
from ...services import (
    ContentViolationError,
    LibraryFullError,
    LibraryNotFoundError,
    SongCreationPayload,
    SongCreationService,
    SongPayloadValidationError,
)


@method_decorator(csrf_exempt, name='dispatch')
class SongListView(View):
    creation_service = SongCreationService()
    timeout_service = GenerationTimeoutService()

    def _get_library(self, user_id):
        try:
            return Library.objects.get(user_id=user_id), None
        except Library.DoesNotExist:
            return None, JsonResponse({'error': 'Library not found for this user'}, status=404)

    def get(self, request, user_id):
        library, err = self._get_library(user_id)
        if err:
            return err

        qs = library.songs.select_related('parameters').all()
        self.timeout_service.expire_timed_out_songs(qs)
        songs = [present_song_summary(song) for song in qs]
        return JsonResponse({'songs': songs, 'count': len(songs)})

    def post(self, request, user_id):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        try:
            payload = SongCreationPayload.from_dict(data)
            song = self.creation_service.create_for_user(user_id, payload)
        except ContentViolationError as exc:
            return JsonResponse(
                {'error': str(exc), 'flagged_words': exc.flagged_words},
                status=exc.status_code,
            )
        except (LibraryNotFoundError, LibraryFullError, SongPayloadValidationError) as exc:
            return JsonResponse({'error': str(exc)}, status=exc.status_code)

        return JsonResponse(present_song_generation(song), status=201)
