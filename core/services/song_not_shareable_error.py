from .share_link_service_error import ShareLinkServiceError


class SongNotShareableError(ShareLinkServiceError):
    status_code = 400
