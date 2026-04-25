from .share_link_service_error import ShareLinkServiceError


class ShareLinkPayloadValidationError(ShareLinkServiceError):
    status_code = 400
