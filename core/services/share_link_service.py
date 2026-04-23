from dataclasses import dataclass

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


@dataclass(frozen=True)
class ShareLinkCreatePayload:
    expiration_date: str

    @classmethod
    def from_dict(cls, data):
        expiration_date = str(data.get('expiration_date', '')).strip()
        if not expiration_date:
            raise ShareLinkPayloadValidationError('expiration_date is required')
        return cls(expiration_date=expiration_date)


@dataclass(frozen=True)
class ShareLinkUpdatePayload:
    is_active: bool | None = None
    expiration_date: str | None = None

    @classmethod
    def from_dict(cls, data):
        expiration_date = str(data['expiration_date']).strip() if 'expiration_date' in data else None
        if expiration_date == '':
            raise ShareLinkPayloadValidationError('expiration_date cannot be blank')
        return cls(
            is_active=bool(data['is_active']) if 'is_active' in data else None,
            expiration_date=expiration_date,
        )


class ShareLinkService:
    def list_links(self, user_id, song_id):
        return self._get_song(user_id, song_id).share_links.all()

    def create_link(self, user_id, song_id, payload):
        song = self._get_song(user_id, song_id)
        if not song.is_accessible:
            raise SongNotShareableError('Cannot share a song that is not ready')
        link = ShareLink.objects.create(song=song, expiration_date=payload.expiration_date)
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
        if payload.expiration_date is not None:
            link.expiration_date = payload.expiration_date
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
