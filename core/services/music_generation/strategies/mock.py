import os

from django.conf import settings

from .base import GenerationResult, MusicGenerationStrategy

MOCK_AUDIO_PATH = os.path.join(settings.BASE_DIR, 'frontend', 'public', 'mock-song.mp3')
MOCK_AUDIO_URL = '/mock-song.mp3'
MOCK_AUDIO_DURATION_SECONDS = 9
MOCK_GENERATION_DELAY_SECONDS = 1


class MockMusicGenerationStrategy(MusicGenerationStrategy):
    provider_name = 'mock'

    def generate(self, song):
        return GenerationResult(
            status='generating',
            duration=0,
            description=f'Mock generation started for "{song.title}"',
            audio_url='',
            provider_generation_id=f'mock-task-{song.id}',
        )
