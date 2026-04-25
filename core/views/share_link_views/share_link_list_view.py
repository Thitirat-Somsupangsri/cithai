import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from ...presenters import present_share_link
from .._session_auth import require_owned_user
from ...services import (
    ShareLinkCreatePayload,
    ShareLinkPayloadValidationError,
    ShareLinkService,
    ShareSongNotFoundError,
    SongNotShareableError,
)


@method_decorator(csrf_exempt, name='dispatch')
class ShareLinkListView(View):
    share_link_service = ShareLinkService()

    def get(self, request, user_id, song_id):
        _, err = require_owned_user(request, user_id)
        if err:
            return err
        try:
            links = self.share_link_service.list_links(user_id, song_id)
        except ShareSongNotFoundError as exc:
            return JsonResponse({'error': str(exc)}, status=exc.status_code)
        links = [present_share_link(link, include_validity=True) for link in links]
        return JsonResponse({'share_links': links})

    def post(self, request, user_id, song_id):
        _, err = require_owned_user(request, user_id)
        if err:
            return err
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        try:
            link = self.share_link_service.create_link(
                user_id,
                song_id,
                ShareLinkCreatePayload.from_dict(data),
            )
        except (
            ShareLinkPayloadValidationError,
            ShareSongNotFoundError,
            SongNotShareableError,
        ) as exc:
            return JsonResponse({'error': str(exc)}, status=exc.status_code)
        return JsonResponse(present_share_link(link), status=201)
