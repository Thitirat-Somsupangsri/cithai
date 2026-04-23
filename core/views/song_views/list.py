import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from ...models import Library
from ...presenters import present_song_generation, present_song_summary
from ...services import (
    LibraryFullError,
    LibraryNotFoundError,
    SongCreationPayload,
    SongCreationService,
    SongPayloadValidationError,
)


@method_decorator(csrf_exempt, name='dispatch')
class SongListView(View):
    creation_service = SongCreationService()

    def _get_library(self, user_id):
        try:
            return Library.objects.get(user_id=user_id), None
        except Library.DoesNotExist:
            return None, JsonResponse({'error': 'Library not found for this user'}, status=404)

    def get(self, request, user_id):
        library, err = self._get_library(user_id)
        if err:
            return err

        songs = [present_song_summary(song) for song in library.songs.select_related('parameters').all()]
        return JsonResponse({'songs': songs, 'count': len(songs)})

    def post(self, request, user_id):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        try:
            payload = SongCreationPayload.from_dict(data)
            song = self.creation_service.create_for_user(user_id, payload)
        except (LibraryNotFoundError, LibraryFullError, SongPayloadValidationError) as exc:
            return JsonResponse({'error': str(exc)}, status=exc.status_code)

        return JsonResponse(present_song_generation(song), status=201)
