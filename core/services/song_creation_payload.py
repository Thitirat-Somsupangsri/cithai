from dataclasses import dataclass

from .song_payload_validation_error import SongPayloadValidationError


@dataclass(frozen=True)
class SongCreationPayload:
    title: str
    occasion: str
    genre: str
    voice_type: str
    custom_text: str = ''

    @classmethod
    def from_dict(cls, data):
        required = ('title', 'occasion', 'genre', 'voice_type')
        missing = [field for field in required if not str(data.get(field, '')).strip()]
        if missing:
            raise SongPayloadValidationError(f'Missing fields: {missing}')

        return cls(
            title=str(data['title']).strip(),
            occasion=str(data['occasion']).strip(),
            genre=str(data['genre']).strip(),
            voice_type=str(data['voice_type']).strip(),
            custom_text=str(data.get('custom_text', '')).strip(),
        )
