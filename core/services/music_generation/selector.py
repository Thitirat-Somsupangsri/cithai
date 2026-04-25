from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .strategies.mock_music_generation_strategy import MockMusicGenerationStrategy
from .strategies.suno_music_generation_strategy import SunoMusicGenerationStrategy


def get_music_generation_strategy():
    provider = getattr(settings, 'MUSIC_GENERATION_PROVIDER', 'mock').lower()

    if provider == 'mock':
        return MockMusicGenerationStrategy()
    if provider == 'suno':
        return SunoMusicGenerationStrategy()

    raise ImproperlyConfigured(
        f"Unsupported MUSIC_GENERATION_PROVIDER '{provider}'. "
        "Expected 'mock' or 'suno'."
    )
