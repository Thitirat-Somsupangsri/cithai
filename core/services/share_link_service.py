import calendar
from datetime import timedelta

from django.utils import timezone

from ..models import ShareLink, Song
from .share_link_create_payload import ShareLinkCreatePayload
from .share_link_not_found_error import ShareLinkNotFoundError
from .share_link_payload_validation_error import ShareLinkPayloadValidationError
from .share_link_service_error import ShareLinkServiceError
from .share_link_update_payload import ShareLinkUpdatePayload
from .share_song_not_found_error import ShareSongNotFoundError
from .song_not_shareable_error import SongNotShareableError


def _add_months(value, months):
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


def _resolve_expiration_date(expiration_option):
    today = timezone.localdate()
    if expiration_option == '1_month':
        return _add_months(today, 1)
    return today + timedelta(days=7)


class ShareLinkService:
    def list_links(self, user_id, song_id):
        return self._get_song(user_id, song_id).share_links.all()

    def create_link(self, user_id, song_id, payload):
        song = self._get_song(user_id, song_id)
        if not song.is_accessible:
            raise SongNotShareableError('Cannot share a song that is not ready')
        link = ShareLink.objects.create(
            song=song,
            expiration_date=_resolve_expiration_date(payload.expiration_option),
        )
        link.refresh_from_db()
        return link

    def get_link(self, token):
        try:
            return ShareLink.objects.get(token=token)
        except ShareLink.DoesNotExist as exc:
            raise ShareLinkNotFoundError('Share link not found') from exc

    def update_link(self, token, payload):
        link = self.get_link(token)
        if payload.is_active is not None:
            link.is_active = payload.is_active
        if payload.expiration_option is not None:
            link.expiration_date = _resolve_expiration_date(payload.expiration_option)
        link.save()
        link.refresh_from_db()
        return link

    def delete_link(self, token):
        link = self.get_link(token)
        link.delete()

    def _get_song(self, user_id, song_id):
        try:
            return Song.objects.get(pk=song_id, library__user_id=user_id)
        except Song.DoesNotExist as exc:
            raise ShareSongNotFoundError('Song not found') from exc
