from dataclasses import dataclass
from urllib.parse import urlsplit

from django.conf import settings

from ..strategies.base import SongGenerationError


@dataclass(frozen=True)
class SunoConfig:
    api_key: str
    api_url: str
    callback_url: str
    model: str
    custom_mode: bool
    instrumental: bool

    @classmethod
    def from_settings(cls):
        api_key     = getattr(settings, 'SUNO_API_KEY', '').strip()
        api_url     = getattr(settings, 'SUNO_API_URL', '').strip()
        callback_url = getattr(settings, 'SUNO_CALLBACK_URL', '').strip()
        model       = getattr(settings, 'SUNO_MODEL', 'V4_5ALL')
        custom_mode = getattr(settings, 'SUNO_CUSTOM_MODE', False)
        instrumental = getattr(settings, 'SUNO_INSTRUMENTAL', False)

        if not api_key:
            raise SongGenerationError('Suno API key is not configured.')
        if not api_url:
            raise SongGenerationError('Suno API URL is not configured.')

        cls._validate_callback_url(callback_url)

        return cls(
            api_key=api_key,
            api_url=api_url,
            callback_url=callback_url,
            model=model,
            custom_mode=custom_mode,
            instrumental=instrumental,
        )

    @staticmethod
    def _validate_callback_url(url):
        if not url:
            raise SongGenerationError(
                'Suno callback URL is not configured. '
                'Set SUNO_CALLBACK_URL or BACKEND_PUBLIC_URL.'
            )

        parsed = urlsplit(url)
        hostname = (parsed.hostname or '').lower()

        if hostname in {'localhost', '127.0.0.1'} or hostname.endswith('.local'):
            raise SongGenerationError(
                'Suno callback URL must be publicly reachable. '
                'Use a public BACKEND_PUBLIC_URL or SUNO_CALLBACK_URL.'
            )
        if hostname == 'example.com' or 'example.' in hostname or hostname.endswith('.example'):
            raise SongGenerationError(
                'Suno callback URL is still a placeholder. '
                'Replace it with your real public callback URL.'
            )
        if not parsed.path.rstrip('/').endswith('/integrations/suno/callback'):
            raise SongGenerationError(
                'Suno callback URL must point to /integrations/suno/callback/.'
            )
