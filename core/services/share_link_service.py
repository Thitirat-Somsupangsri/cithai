import calendar
from dataclasses import dataclass
from datetime import timedelta

from django.utils import timezone

from ..models import ShareLink, Song


class ShareLinkServiceError(Exception):
    status_code = 400


class ShareSongNotFoundError(ShareLinkServiceError):
    status_code = 404


class ShareLinkNotFoundError(ShareLinkServiceError):
    status_code = 404


class ShareLinkPayloadValidationError(ShareLinkServiceError):
    status_code = 400


class SongNotShareableError(ShareLinkServiceError):
    status_code = 400


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


@dataclass(frozen=True)
class ShareLinkCreatePayload:
    expiration_option: str = '7_days'

    @classmethod
    def from_dict(cls, data):
        if 'expiration_date' in data:
            raise ShareLinkPayloadValidationError('Use expiration_option instead of expiration_date')
        expiration_option = str(data.get('expiration_option', '7_days')).strip() or '7_days'
        if expiration_option not in {'7_days', '1_month'}:
            raise ShareLinkPayloadValidationError('expiration_option must be 7_days or 1_month')
        return cls(expiration_option=expiration_option)


@dataclass(frozen=True)
class ShareLinkUpdatePayload:
    is_active: bool | None = None
    expiration_option: str | None = None

    @classmethod
    def from_dict(cls, data):
        if 'expiration_date' in data:
            raise ShareLinkPayloadValidationError('Use expiration_option instead of expiration_date')
        expiration_option = str(data['expiration_option']).strip() if 'expiration_option' in data else None
        if expiration_option == '':
            raise ShareLinkPayloadValidationError('expiration_option cannot be blank')
        if expiration_option is not None and expiration_option not in {'7_days', '1_month'}:
            raise ShareLinkPayloadValidationError('expiration_option must be 7_days or 1_month')
        return cls(
            is_active=bool(data['is_active']) if 'is_active' in data else None,
            expiration_option=expiration_option,
        )


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
