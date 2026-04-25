import os

from django.conf import settings

from .base import GenerationResult, MusicGenerationStrategy

MOCK_AUDIO_PATH = os.path.join(settings.BASE_DIR, 'frontend', 'public', 'mock-song.mp3')
MOCK_AUDIO_URL = '/mock-song.mp3'
MOCK_AUDIO_DURATION_SECONDS = 9


class MockMusicGenerationStrategy(MusicGenerationStrategy):
    provider_name = 'mock'

    def generate(self, song):
        prompt = song.parameters
        description = (
            f"Mock song for {prompt.title} "
            f"({prompt.occasion}, {prompt.genre}, {prompt.voice_type})"
        )
        return GenerationResult(
            status='ready',
            duration=MOCK_AUDIO_DURATION_SECONDS,
            description=description,
            audio_url=MOCK_AUDIO_URL,
            provider_generation_id=f'mock-song-{song.id}',
        )
