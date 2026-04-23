import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from ..services.music_generation.callback_service import (
    MusicGenerationCallbackSongNotFoundError,
    MusicGenerationCallbackValidationError,
    SunoCallbackService,
)


@method_decorator(csrf_exempt, name='dispatch')
class SunoCallbackView(View):
    callback_service = SunoCallbackService()

    def post(self, request):
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        try:
            song = self.callback_service.process(payload)
        except (
            MusicGenerationCallbackValidationError,
            MusicGenerationCallbackSongNotFoundError,
        ) as exc:
            return JsonResponse({'error': str(exc)}, status=exc.status_code)

        return JsonResponse({
            'message': 'Callback received',
            'song_id': song.id,
            'status': song.status,
        }, status=200)
