import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from ...presenters import present_share_link, present_share_link_resolution
from .._session_auth import require_authenticated_user
from ...services import (
    ShareLinkNotFoundError,
    ShareLinkPayloadValidationError,
    ShareLinkService,
    ShareLinkUpdatePayload,
)


@method_decorator(csrf_exempt, name='dispatch')
class ShareLinkDetailView(View):
    share_link_service = ShareLinkService()

    def get(self, request, token):
        try:
            link = self.share_link_service.get_link(token)
        except ShareLinkNotFoundError as exc:
            return JsonResponse({'error': str(exc)}, status=exc.status_code)
        if not link.is_valid:
            return JsonResponse({'error': 'Share link is expired or inactive'}, status=410)
        return JsonResponse(present_share_link_resolution(link))

    def put(self, request, token):
        user, err = require_authenticated_user(request)
        if err:
            return err
        try:
            existing = self.share_link_service.get_link(token)
        except ShareLinkNotFoundError as exc:
            return JsonResponse({'error': str(exc)}, status=exc.status_code)
        if existing.song.library.user_id != user.id:
            return JsonResponse({'error': 'Forbidden'}, status=403)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        try:
            link = self.share_link_service.update_link(token, ShareLinkUpdatePayload.from_dict(data))
        except (ShareLinkNotFoundError, ShareLinkPayloadValidationError) as exc:
            return JsonResponse({'error': str(exc)}, status=exc.status_code)
        return JsonResponse(present_share_link(link))

    def delete(self, request, token):
        user, err = require_authenticated_user(request)
        if err:
            return err
        try:
            existing = self.share_link_service.get_link(token)
        except ShareLinkNotFoundError as exc:
            return JsonResponse({'error': str(exc)}, status=exc.status_code)
        if existing.song.library.user_id != user.id:
            return JsonResponse({'error': 'Forbidden'}, status=403)

        try:
            self.share_link_service.delete_link(token)
        except ShareLinkNotFoundError as exc:
            return JsonResponse({'error': str(exc)}, status=exc.status_code)
        return JsonResponse({'message': 'Share link deleted'})
