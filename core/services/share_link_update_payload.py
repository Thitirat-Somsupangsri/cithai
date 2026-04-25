from dataclasses import dataclass

from .share_link_payload_validation_error import ShareLinkPayloadValidationError


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
