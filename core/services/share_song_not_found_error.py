from .share_link_service_error import ShareLinkServiceError


class ShareSongNotFoundError(ShareLinkServiceError):
    status_code = 404
