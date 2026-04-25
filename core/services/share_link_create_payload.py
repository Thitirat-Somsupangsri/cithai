from dataclasses import dataclass

from .share_link_payload_validation_error import ShareLinkPayloadValidationError


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
