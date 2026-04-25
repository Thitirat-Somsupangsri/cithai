from .share_link_service_error import ShareLinkServiceError


class ShareLinkNotFoundError(ShareLinkServiceError):
    status_code = 404
